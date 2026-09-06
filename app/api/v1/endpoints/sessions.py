import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.registry import SessionCreate, SessionResponse, SessionUpdate
from app.services.registry_service import RegistryService

router = APIRouter()


@router.post("/", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    session_in: SessionCreate,
) -> Any:
    """
    Create new session.
    """
    registry_service = RegistryService(db)
    try:
        session = await registry_service.create_session(session_in)
        return session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    session_id: uuid.UUID,
) -> Any:
    """
    Get a specific session by ID.
    """
    registry_service = RegistryService(db)
    session = await registry_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    *,
    db: AsyncSession = Depends(get_db),  # noqa: B008
    session_id: uuid.UUID,
    session_in: SessionUpdate,
) -> Any:
    """
    Update a session.
    """
    registry_service = RegistryService(db)
    session = await registry_service.update_session(session_id, session_in)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
