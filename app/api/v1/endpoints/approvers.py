"""
API endpoints for approver management.
"""

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.v1.endpoints.approvals import ApproverResponse, CreateApproverRequest
from app.services.approval_service import ApprovalService

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post(
    "",
    response_model=ApproverResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new approver",
)
async def create_approver(
    request: CreateApproverRequest,
    db: AsyncSession = Depends(get_db),
) -> ApproverResponse:
    """
    Create a new approver identity.

    For MVP, this is a simple creation endpoint. Future phases will integrate
    with enterprise SSO and RBAC.

    Args:
        request: Approver creation details
        db: Database session

    Returns:
        Created approver

    Raises:
        400: Approver already exists
    """
    service = ApprovalService(db)

    try:
        approver = await service.create_approver(
            approver_id=request.approver_id,
            display_name=request.display_name,
            email=request.email,
        )

        return ApproverResponse(
            id=str(approver.id),
            approver_id=approver.approver_id,
            display_name=approver.display_name,
            email=approver.email,
            is_active=approver.is_active,
            created_at=approver.created_at,
        )
    except Exception as e:
        logger.error("approver_creation_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create approver: {e!s}",
        ) from e
