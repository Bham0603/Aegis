from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import CorrelationIdMiddleware
from app.core.redis import close_redis_pool, init_redis_pool
from app.core.security_middleware import (
    ErrorSanitizationMiddleware,
    MaxBodySizeMiddleware,
    SecurityHeadersMiddleware,
)

# Set up logging early
setup_logging()
logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(
        "Starting Aegis Security Gateway",
        version=settings.APP_VERSION,
        env=settings.APP_ENV,
    )
    try:
        await init_redis_pool()
        logger.info("Redis connection pool initialized")
    except Exception as e:  # noqa: BLE001
        logger.error("Failed to initialize Redis pool", error=str(e))
        # Note: Depending on strictness, we could raise here to prevent startup if Redis is mandatory.

    yield

    # Shutdown
    logger.info("Shutting down Aegis Security Gateway")
    await close_redis_pool()
    logger.info("Redis connection pool closed")


openapi_url = (
    f"{settings.API_V1_STR}/openapi.json" if settings.APP_ENV != "production" else None
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    openapi_url=openapi_url,
    docs_url="/docs" if settings.APP_ENV != "production" else None,
    redoc_url="/redoc" if settings.APP_ENV != "production" else None,
    lifespan=lifespan,
)

from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router

# The order of middleware execution is bottom-to-top of how they are added.
# Exception handlers should be close to the app (bottom of stack),
# CORS near the top, MaxBodySize at the top.
# CorrelationId at the very top so everything has an ID.

app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(MaxBodySizeMiddleware, max_upload_size=settings.MAX_BODY_SIZE)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(ErrorSanitizationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code in (401, 403):
        logger.warning(
            "security_authorization_failed",
            path=request.url.path,
            status_code=exc.status_code,
            detail=exc.detail,
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.warning(
        "request_validation_failed",
        path=request.url.path,
        errors=exc.errors(),
    )
    return JSONResponse(
        status_code=422,
        content={"detail": "Invalid request parameters", "errors": exc.errors()},
    )


@app.get("/health", tags=["System"])
async def health_check():
    """
    Check the health of the application.
    Currently only checks if the API itself is running.
    Future phases can expand this to check DB/Redis connectivity.
    """
    logger.info("Health check requested")
    return {"status": "healthy"}


@app.get("/version", tags=["System"])
async def version_info():
    """
    Return the version info of the application.
    """
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.APP_VERSION,
        "env": settings.APP_ENV,
    }


app.include_router(api_router, prefix=settings.API_V1_STR)
