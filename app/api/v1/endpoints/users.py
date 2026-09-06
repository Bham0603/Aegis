import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.registry import UserCreate, UserResponse, UserUpdate
from app.services.registry_service import RegistryService

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    registry_service = RegistryService(db)
    user = await registry_service.create_user(user_in)
    return user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID,
) -> Any:
    """
    Get a specific user by ID.
    """
    registry_service = RegistryService(db)
    user = await registry_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    registry_service = RegistryService(db)
    user = await registry_service.update_user(user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
