import uuid
from collections.abc import Sequence
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.registry import (
    AgentCreate,
    AgentResponse,
    AgentToolBindingCreate,
    AgentToolBindingResponse,
    AgentUpdate,
)
from app.services.registry_service import RegistryService

router = APIRouter()


@router.post("/", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    agent_in: AgentCreate,
) -> Any:
    """
    Create new agent.
    """
    registry_service = RegistryService(db)
    # Check for uniqueness if needed, but DB constraint handles it
    agent = await registry_service.create_agent(agent_in)
    return agent


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    agent_id: uuid.UUID,
) -> Any:
    """
    Get a specific agent by ID.
    """
    registry_service = RegistryService(db)
    agent = await registry_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    agent_id: uuid.UUID,
    agent_in: AgentUpdate,
) -> Any:
    """
    Update an agent.
    """
    registry_service = RegistryService(db)
    agent = await registry_service.update_agent(agent_id, agent_in)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post(
    "/{agent_id}/tools",
    response_model=AgentToolBindingResponse,
    status_code=status.HTTP_201_CREATED,
)
async def bind_tool_to_agent(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    agent_id: uuid.UUID,
    binding_in: AgentToolBindingCreate,
) -> Any:
    """
    Bind a tool to an agent.
    """
    registry_service = RegistryService(db)

    agent = await registry_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    tool = await registry_service.get_tool(binding_in.tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")

    binding = await registry_service.bind_tool_to_agent(agent_id, binding_in)
    return binding


@router.get("/{agent_id}/tools", response_model=Sequence[AgentToolBindingResponse])
async def get_agent_tools(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    agent_id: uuid.UUID,
) -> Any:
    """
    Get all tools bound to an agent.
    """
    registry_service = RegistryService(db)
    agent = await registry_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    bindings = await registry_service.get_agent_bindings(agent_id)
    return bindings
