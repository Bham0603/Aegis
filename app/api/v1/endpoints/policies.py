import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.policy import PolicyCreate, PolicyResponse, PolicyUpdate
from app.services.policy_service import PolicyService

router = APIRouter()


@router.post("/", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_in: PolicyCreate, db: AsyncSession = Depends(get_db)
) -> Any:
    """Create a new security policy."""
    svc = PolicyService(db)

    # Check if policy with same name exists
    existing = await svc.get_policy_by_name(policy_in.name)
    if existing:
        raise HTTPException(
            status_code=400, detail="Policy with this name already exists."
        )

    policy = await svc.create_policy(policy_in)
    return policy


@router.get("/", response_model=list[PolicyResponse])
async def read_policies(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> Any:
    """Retrieve policies."""
    svc = PolicyService(db)
    policies = await svc.get_multi(skip=skip, limit=limit)
    return policies


@router.get("/{policy_id}", response_model=PolicyResponse)
async def read_policy(policy_id: uuid.UUID, db: AsyncSession = Depends(get_db)) -> Any:
    """Get policy by ID."""
    svc = PolicyService(db)
    policy = await svc.get_policy(policy_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.patch("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: uuid.UUID, policy_in: PolicyUpdate, db: AsyncSession = Depends(get_db)
) -> Any:
    """Update a policy."""
    svc = PolicyService(db)
    policy = await svc.update_policy(policy_id, policy_in)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: uuid.UUID, db: AsyncSession = Depends(get_db)
) -> None:
    """Delete a policy."""
    svc = PolicyService(db)
    success = await svc.delete_policy(policy_id)
    if not success:
        raise HTTPException(status_code=404, detail="Policy not found")
