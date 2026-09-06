import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models  # noqa: F401
from app.db.base import Base
from app.schemas.registry import (
    AgentCreate,
    SessionCreate,
    ToolCreate,
    ToolOperationCreate,
    UserCreate,
)
from app.services.registry_service import RegistryService

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
async def db_session(async_session_maker):
    async with async_session_maker() as session:
        yield session


@pytest.mark.asyncio
async def test_create_user(db_session):
    service = RegistryService(db_session)
    user_in = UserCreate(ext_id="ext-123", display_name="Test User")
    user = await service.create_user(user_in)

    assert user.id is not None
    assert user.ext_id == "ext-123"
    assert user.display_name == "Test User"


@pytest.mark.asyncio
async def test_create_agent(db_session):
    service = RegistryService(db_session)
    agent_in = AgentCreate(name="TestAgent", description="A test agent")
    agent = await service.create_agent(agent_in)

    assert agent.id is not None
    assert agent.name == "TestAgent"


@pytest.mark.asyncio
async def test_create_tool(db_session):
    service = RegistryService(db_session)
    tool_in = ToolCreate(
        canonical_name="test_tool",
        provider="test",
        operations=[ToolOperationCreate(name="op1", description="desc1")],
    )
    tool = await service.create_tool(tool_in)

    assert tool.id is not None
    assert tool.canonical_name == "test_tool"
    assert len(tool.operations) == 1
    assert tool.operations[0].name == "op1"


@pytest.mark.asyncio
async def test_create_session(db_session):
    service = RegistryService(db_session)
    agent_in = AgentCreate(name="TestAgent")
    agent = await service.create_agent(agent_in)

    session_in = SessionCreate(agent_id=agent.id)
    session = await service.create_session(session_in)

    assert session.id is not None
    assert session.agent_id == agent.id
