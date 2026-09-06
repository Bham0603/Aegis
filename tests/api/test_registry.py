import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401
from app.api.deps import get_db
from app.db.base import Base
from app.main import app as fastapi_app

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session_maker():
    engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    yield session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def override_get_db(async_session_maker):
    async def _override_get_db():
        async with async_session_maker() as session:
            yield session

    fastapi_app.dependency_overrides[get_db] = _override_get_db
    yield
    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def client_with_db(override_get_db):
    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app), base_url="http://test"
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_create_user(client_with_db: AsyncClient):
    response = await client_with_db.post(
        "/api/v1/users/", json={"ext_id": "test-ext", "display_name": "Test User"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["display_name"] == "Test User"
    assert data["ext_id"] == "test-ext"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_agent(client_with_db: AsyncClient):
    response = await client_with_db.post("/api/v1/agents/", json={"name": "Test Agent"})

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Agent"
    assert "id" in data


@pytest.mark.asyncio
async def test_create_tool(client_with_db: AsyncClient):
    response = await client_with_db.post(
        "/api/v1/tools/",
        json={
            "canonical_name": "test_tool",
            "provider": "test_provider",
            "operations": [{"name": "op1", "description": "desc1"}],
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["canonical_name"] == "test_tool"
    assert len(data["operations"]) == 1
    assert data["operations"][0]["name"] == "op1"


@pytest.mark.asyncio
async def test_create_session(client_with_db: AsyncClient):
    # First create an agent
    agent_resp = await client_with_db.post(
        "/api/v1/agents/", json={"name": "Test Agent"}
    )
    agent_id = agent_resp.json()["id"]

    # Now create a session
    response = await client_with_db.post(
        "/api/v1/sessions/", json={"agent_id": agent_id}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["agent_id"] == agent_id
    assert "id" in data
