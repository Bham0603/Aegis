"""
API endpoints for approval management.
"""

from datetime import datetime

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.security import get_current_principal
from app.domain.approval import ApprovalStatus
from app.domain.auth import Principal, Role
from app.services.approval_service import ApprovalService

logger = structlog.get_logger(__name__)

router = APIRouter()


# Request/Response Schemas


class ApprovalRequestResponse(BaseModel):
    """Response schema for approval request."""

    approval_request_id: str
    action_id: str
    correlation_id: str
    agent_id: str
    user_id: str | None
    session_id: str
    tool_id: str
    operation: str | None
    resource: str | None
    environment: str
    status: str
    required_approver_role: str | None
    approver_id: str | None
    created_at: datetime
    expires_at: datetime
    resolved_at: datetime | None
    risk_score: int | None
    risk_level: str | None
    highest_threat_severity: str | None
    reasons: list[str]
    resolution_comment: str | None


class ApprovalDecisionRequest(BaseModel):
    """Request schema for approval decision (approve/deny)."""

    approver_id: str = Field(..., description="Identity of the human approver")
    decision: str = Field(
        ..., description="Decision: APPROVED or DENIED", pattern="^(APPROVED|DENIED)$"
    )
    comment: str | None = Field(
        None, description="Optional comment explaining the decision"
    )


class CreateApproverRequest(BaseModel):
    """Request schema for creating an approver."""

    approver_id: str = Field(..., description="Unique approver identifier")
    display_name: str = Field(..., description="Human-readable name")
    email: str | None = Field(None, description="Email address")


class ApproverResponse(BaseModel):
    """Response schema for approver."""

    id: str
    approver_id: str
    display_name: str
    email: str | None
    is_active: bool
    created_at: datetime


# Endpoints


@router.get(
    "/",
    response_model=list[ApprovalRequestResponse],
    summary="List approval requests",
)
async def list_approval_requests(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    status: str | None = None,
) -> list[ApprovalRequestResponse]:
    """
    List approval requests, optionally filtered by status.

    Args:
        skip: Pagination offset
        limit: Maximum number of results
        status: Optional filter (PENDING, APPROVED, DENIED, EXPIRED)
    """
    service = ApprovalService(db)
    approvals = await service.list_requests(skip=skip, limit=limit, status_filter=status)

    return [
        ApprovalRequestResponse(
            approval_request_id=a.approval_request_id,
            action_id=a.action_id,
            correlation_id=a.correlation_id,
            agent_id=a.agent_id,
            user_id=a.user_id,
            session_id=a.session_id,
            tool_id=a.tool_id,
            operation=a.operation,
            resource=a.resource,
            environment=a.environment,
            status=a.status.value,
            required_approver_role=a.required_approver_role,
            approver_id=a.approver_id,
            created_at=a.created_at,
            expires_at=a.expires_at,
            resolved_at=a.resolved_at,
            risk_score=a.risk_score,
            risk_level=a.risk_level,
            highest_threat_severity=a.highest_threat_severity,
            reasons=a.reasons,
            resolution_comment=a.resolution_comment,
        )
        for a in approvals
    ]


@router.get(
    "/{approval_request_id}",
    response_model=ApprovalRequestResponse,
    summary="Get approval request by ID",
)
async def get_approval_request(
    approval_request_id: str,
    db: AsyncSession = Depends(get_db),
) -> ApprovalRequestResponse:
    """
    Retrieve an approval request by its ID.

    Args:
        approval_request_id: The approval request identifier
        db: Database session

    Returns:
        ApprovalRequestResponse

    Raises:
        404: Approval request not found
    """
    service = ApprovalService(db)
    approval = await service.get_request(approval_request_id)

    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request {approval_request_id} not found",
        )

    return ApprovalRequestResponse(
        approval_request_id=approval.approval_request_id,
        action_id=approval.action_id,
        correlation_id=approval.correlation_id,
        agent_id=approval.agent_id,
        user_id=approval.user_id,
        session_id=approval.session_id,
        tool_id=approval.tool_id,
        operation=approval.operation,
        resource=approval.resource,
        environment=approval.environment,
        status=approval.status.value,
        required_approver_role=approval.required_approver_role,
        approver_id=approval.approver_id,
        created_at=approval.created_at,
        expires_at=approval.expires_at,
        resolved_at=approval.resolved_at,
        risk_score=approval.risk_score,
        risk_level=approval.risk_level,
        highest_threat_severity=approval.highest_threat_severity,
        reasons=approval.reasons,
        resolution_comment=approval.resolution_comment,
    )


@router.post(
    "/{approval_request_id}/approve",
    response_model=ApprovalRequestResponse,
    summary="Approve an approval request",
)
async def approve_approval_request(
    approval_request_id: str,
    request: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> ApprovalRequestResponse:
    """
    Approve a pending approval request.

    Security validations:
    - Approval request exists and is PENDING
    - Not expired
    - Approver is not the agent (no self-approval)
    - Approver is active

    Args:
        approval_request_id: The approval request to approve
        request: Approval decision details
        db: Database session

    Returns:
        Updated approval request

    Raises:
        400: Invalid decision or validation failed
        404: Approval request not found
    """
    # Enforce decision must be APPROVED for this endpoint
    if request.decision != "APPROVED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only accepts APPROVED decisions. Use /deny for denials.",
        )

    if Role.ADMIN not in principal.roles:
        if request.approver_id and request.approver_id != principal.principal_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot approve on behalf of another user.",
            )
        # Force the approver ID to the authenticated principal
        approver_id = principal.principal_id
    else:
        # Admin can approve on behalf if they provide an ID, otherwise default to themselves
        approver_id = request.approver_id or principal.principal_id

    service = ApprovalService(db)
    resolved_approval, error = await service.resolve(
        approval_request_id=approval_request_id,
        approver_id=approver_id,
        decision=ApprovalStatus.APPROVED,
        comment=request.comment,
    )

    if error:
        logger.warning(
            "approval_resolution_failed",
            approval_request_id=approval_request_id,
            error=error,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    if not resolved_approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request {approval_request_id} not found",
        )

    return ApprovalRequestResponse(
        approval_request_id=resolved_approval.approval_request_id,
        action_id=resolved_approval.action_id,
        correlation_id=resolved_approval.correlation_id,
        agent_id=resolved_approval.agent_id,
        user_id=resolved_approval.user_id,
        session_id=resolved_approval.session_id,
        tool_id=resolved_approval.tool_id,
        operation=resolved_approval.operation,
        resource=resolved_approval.resource,
        environment=resolved_approval.environment,
        status=resolved_approval.status.value,
        required_approver_role=resolved_approval.required_approver_role,
        approver_id=resolved_approval.approver_id,
        created_at=resolved_approval.created_at,
        expires_at=resolved_approval.expires_at,
        resolved_at=resolved_approval.resolved_at,
        risk_score=resolved_approval.risk_score,
        risk_level=resolved_approval.risk_level,
        highest_threat_severity=resolved_approval.highest_threat_severity,
        reasons=resolved_approval.reasons,
        resolution_comment=resolved_approval.resolution_comment,
    )


@router.post(
    "/{approval_request_id}/deny",
    response_model=ApprovalRequestResponse,
    summary="Deny an approval request",
)
async def deny_approval_request(
    approval_request_id: str,
    request: ApprovalDecisionRequest,
    db: AsyncSession = Depends(get_db),
    principal: Principal = Depends(get_current_principal),
) -> ApprovalRequestResponse:
    """
    Deny a pending approval request.

    Security validations:
    - Approval request exists and is PENDING
    - Not expired
    - Approver is authorized

    Args:
        approval_request_id: The approval request to deny
        request: Approval decision details
        db: Database session

    Returns:
        Updated approval request

    Raises:
        400: Invalid decision or validation failed
        404: Approval request not found
    """
    # Enforce decision must be DENIED for this endpoint
    if request.decision != "DENIED":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This endpoint only accepts DENIED decisions. Use /approve for approvals.",
        )

    if Role.ADMIN not in principal.roles:
        if request.approver_id and request.approver_id != principal.principal_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot deny on behalf of another user.",
            )
        approver_id = principal.principal_id
    else:
        approver_id = request.approver_id or principal.principal_id

    service = ApprovalService(db)
    resolved_approval, error = await service.resolve(
        approval_request_id=approval_request_id,
        approver_id=approver_id,
        decision=ApprovalStatus.DENIED,
        comment=request.comment,
    )

    if error:
        logger.warning(
            "approval_denial_failed",
            approval_request_id=approval_request_id,
            error=error,
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    if not resolved_approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Approval request {approval_request_id} not found",
        )

    return ApprovalRequestResponse(
        approval_request_id=resolved_approval.approval_request_id,
        action_id=resolved_approval.action_id,
        correlation_id=resolved_approval.correlation_id,
        agent_id=resolved_approval.agent_id,
        user_id=resolved_approval.user_id,
        session_id=resolved_approval.session_id,
        tool_id=resolved_approval.tool_id,
        operation=resolved_approval.operation,
        resource=resolved_approval.resource,
        environment=resolved_approval.environment,
        status=resolved_approval.status.value,
        required_approver_role=resolved_approval.required_approver_role,
        approver_id=resolved_approval.approver_id,
        created_at=resolved_approval.created_at,
        expires_at=resolved_approval.expires_at,
        resolved_at=resolved_approval.resolved_at,
        risk_score=resolved_approval.risk_score,
        risk_level=resolved_approval.risk_level,
        highest_threat_severity=resolved_approval.highest_threat_severity,
        reasons=resolved_approval.reasons,
        resolution_comment=resolved_approval.resolution_comment,
    )
