import pytest
from sqlalchemy.ext.asyncio import AsyncSession

import app.models  # noqa: F401
from app.schemas.registry import (
    AgentCreate,
    SessionCreate,
    ToolCreate,
    ToolOperationCreate,
    UserCreate,
)
from app.services.registry_service import RegistryService


@pytest.mark.asyncio
async def test_create_user(db: AsyncSession):
    service = RegistryService(db)
    user_in = UserCreate(ext_id="ext-123", display_name="Test User")
    user = await service.create_user(user_in)

    assert user.id is not None
    assert user.ext_id == "ext-123"
    assert user.display_name == "Test User"


@pytest.mark.asyncio
async def test_create_agent(db: AsyncSession):
    service = RegistryService(db)
    agent_in = AgentCreate(name="TestAgent", description="A test agent")
    agent = await service.create_agent(agent_in)

    assert agent.id is not None
    assert agent.name == "TestAgent"


@pytest.mark.asyncio
async def test_create_tool(db):
    service = RegistryService(db)
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
async def test_create_session(db: AsyncSession):
    service = RegistryService(db)
    agent_in = AgentCreate(name="TestAgent")
    agent = await service.create_agent(agent_in)

    session_in = SessionCreate(agent_id=agent.id)
    session = await service.create_session(session_in)

    assert session.id is not None
    assert session.agent_id == agent.id
