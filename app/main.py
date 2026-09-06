from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.core.middleware import CorrelationIdMiddleware
from app.core.redis import close_redis_pool, init_redis_pool

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


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.APP_VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

from app.api.v1.api import api_router

app.add_middleware(CorrelationIdMiddleware)


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
