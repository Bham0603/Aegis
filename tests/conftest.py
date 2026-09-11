import os

# Guarantee test environment isolation BEFORE any application modules load
os.environ["ENVIRONMENT"] = "test"
os.environ["POSTGRES_SERVER"] = "sqlite"
os.environ["POSTGRES_DB"] = "aegis_test.db"

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa: F401
from app.api.deps import get_db
from app.api.security import get_current_principal
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.domain.auth import Principal, PrincipalType, Role
from app.main import app as fastapi_app

# Disable rate limiting in tests
settings.RATE_LIMIT_ENABLED = False

@pytest_asyncio.fixture
async def db():
    # Safely verify we are operating on the test database
    assert "test" in str(engine.url.database), "FATAL: Test suite attempted to connect to non-test database!"
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


from app.core.redis import get_redis_client


@pytest_asyncio.fixture
async def async_client(db: AsyncSession):
    # Override the get_db dependency to use the test db
    async def override_get_db():
        yield db

    # Override get_current_principal to bypass auth
    async def override_get_current_principal():
        return Principal(
            principal_id="test_admin",
            principal_type=PrincipalType.ADMIN,
            roles=[Role.ADMIN, Role.AGENT, Role.APPROVER, Role.AUDITOR, Role.OPERATOR],
        )

    async def override_get_redis_client():
        yield None

    fastapi_app.dependency_overrides[get_db] = override_get_db
    fastapi_app.dependency_overrides[get_current_principal] = (
        override_get_current_principal
    )
    fastapi_app.dependency_overrides[get_redis_client] = override_get_redis_client

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as client:
        yield client

    fastapi_app.dependency_overrides.clear()
