import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.registry import ToolCreate, ToolResponse, ToolUpdate
from app.services.registry_service import RegistryService

router = APIRouter()


@router.post("/", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    tool_in: ToolCreate,
) -> Any:
    """
    Create new tool.
    """
    registry_service = RegistryService(db)
    tool = await registry_service.create_tool(tool_in)
    return tool


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    tool_id: uuid.UUID,
) -> Any:
    """
    Get a specific tool by ID.
    """
    registry_service = RegistryService(db)
    tool = await registry_service.get_tool(tool_id)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    tool_id: uuid.UUID,
    tool_in: ToolUpdate,
) -> Any:
    """
    Update a tool.
    """
    registry_service = RegistryService(db)
    tool = await registry_service.update_tool(tool_id, tool_in)
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool
