"""
Approval Service - manages human-in-the-loop approval workflow.

Security Requirements:
1. Agent cannot approve its own actions (self-approval prevention)
2. Approvals are bound to exact actions via fingerprints
3. Approvals expire and cannot be extended
4. Action mutation invalidates approval
5. Stronger security blocks override approvals
"""

import uuid
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.action import Action
from app.domain.approval import (
    ApprovalRequest,
    ApprovalStatus,
)
from app.domain.context import SecurityContext
from app.domain.decision import SecurityDecision
from app.models.approval import ApprovalRequestDB, ApprovalStatusDB, ApproverDB
from app.services.fingerprint import (
    generate_action_fingerprint,
    verify_action_fingerprint,
)

logger = structlog.get_logger(__name__)

# Default approval expiration (30 minutes)
DEFAULT_APPROVAL_TTL_SECONDS = 1800


class ApprovalService:
    """
    Service for managing approval requests and resolutions.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_request(
        self,
        action: Action,
        security_context: SecurityContext,
        security_decision: SecurityDecision,
        ttl_seconds: int = DEFAULT_APPROVAL_TTL_SECONDS,
    ) -> ApprovalRequest:
        """
        Create a new approval request for an action requiring REVIEW.

        Args:
            action: The action requiring approval
            security_context: Full security context
            security_decision: The decision that triggered REVIEW
            ttl_seconds: Time-to-live in seconds (default 30 minutes)

        Returns:
            ApprovalRequest domain object
        """
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=ttl_seconds)

        # Generate cryptographic fingerprint
        action_fingerprint = generate_action_fingerprint(action)

        # Generate unique approval request ID
        approval_request_id = f"apr_{uuid.uuid4().hex[:12]}"

        # Create domain model
        approval_request = ApprovalRequest(
            approval_request_id=approval_request_id,
            action_id=action.action_id,
            action_fingerprint=action_fingerprint,
            correlation_id=action.correlation_id,
            agent_id=action.agent_id,
            user_id=action.user_id,
            session_id=action.session_id,
            tool_id=action.tool_id,
            operation=action.operation,
            resource=action.resource,
            environment=action.environment,
            status=ApprovalStatus.PENDING,
            created_at=now,
            expires_at=expires_at,
            risk_score=security_decision.risk_score,
            risk_level=security_decision.risk_level,
            highest_threat_severity=security_decision.highest_threat_severity,
            reasons=security_decision.reasons,
        )

        # Persist to database
        db_model = ApprovalRequestDB(
            approval_request_id=approval_request.approval_request_id,
            action_id=approval_request.action_id,
            action_fingerprint=approval_request.action_fingerprint,
            correlation_id=approval_request.correlation_id,
            agent_id=uuid.UUID(approval_request.agent_id),
            user_id=uuid.UUID(approval_request.user_id)
            if approval_request.user_id
            else None,
            session_id=uuid.UUID(approval_request.session_id),
            tool_id=uuid.UUID(approval_request.tool_id),
            operation=approval_request.operation,
            resource=approval_request.resource,
            environment=approval_request.environment,
            status=ApprovalStatusDB.PENDING,
            created_at=approval_request.created_at,
            expires_at=approval_request.expires_at,
            risk_score=approval_request.risk_score,
            risk_level=approval_request.risk_level,
            highest_threat_severity=approval_request.highest_threat_severity,
            reasons={"reasons": approval_request.reasons}
            if approval_request.reasons
            else None,
        )

        self.db.add(db_model)
        await self.db.commit()
        await self.db.refresh(db_model)

        logger.info(
            "approval_request_created",
            approval_request_id=approval_request_id,
            action_id=action.action_id,
            correlation_id=action.correlation_id,
            expires_at=expires_at.isoformat(),
        )

        return approval_request

    async def get_request(self, approval_request_id: str) -> ApprovalRequest | None:
        """
        Retrieve an approval request by ID.

        Args:
            approval_request_id: The approval request ID

        Returns:
            ApprovalRequest if found, None otherwise
        """
        stmt = select(ApprovalRequestDB).where(
            ApprovalRequestDB.approval_request_id == approval_request_id
        )
        result = await self.db.execute(stmt)
        db_model = result.scalar_one_or_none()

        if not db_model:
            return None

        return self._to_domain(db_model)

    async def get_request_by_fingerprint(
        self, action_fingerprint: str
    ) -> ApprovalRequest | None:
        """
        Retrieve an approval request by its exact action fingerprint.
        This ensures duplicate pending requests aren't created for identical actions,
        and allows verifying if an action has already been approved.

        Args:
            action_fingerprint: The cryptographic fingerprint of the action

        Returns:
            The most recent ApprovalRequest matching this fingerprint if found, None otherwise
        """
        stmt = (
            select(ApprovalRequestDB)
            .where(ApprovalRequestDB.action_fingerprint == action_fingerprint)
            .order_by(ApprovalRequestDB.created_at.desc())
        )
        result = await self.db.execute(stmt)
        db_model = result.scalars().first()

        if not db_model:
            return None

        return self._to_domain(db_model)

    async def resolve(
        self,
        approval_request_id: str,
        approver_id: str,
        decision: ApprovalStatus,
        comment: str | None = None,
    ) -> tuple[ApprovalRequest | None, str | None]:
        """
        Resolve an approval request (approve or deny).

        Security validations:
        1. Approval request exists
        2. Status is PENDING
        3. Not expired
        4. Approver is not the agent (no self-approval)
        5. Approver is active

        Args:
            approval_request_id: The approval request to resolve
            approver_id: Identity of the human approver
            decision: APPROVED or DENIED
            comment: Optional human comment

        Returns:
            (resolved_approval_request, error_message)
            - (ApprovalRequest, None) on success
            - (None, error_message) on failure
        """
        # Validate decision type
        if decision not in {ApprovalStatus.APPROVED, ApprovalStatus.DENIED}:
            return None, f"Invalid decision: {decision}. Must be APPROVED or DENIED"

        # Fetch the approval request with row-level locking
        stmt = (
            select(ApprovalRequestDB)
            .where(ApprovalRequestDB.approval_request_id == approval_request_id)
            .with_for_update()
        )
        result = await self.db.execute(stmt)
        db_model = result.scalar_one_or_none()

        if not db_model:
            logger.warning(
                "approval_resolution_failed",
                approval_request_id=approval_request_id,
                reason="not_found",
            )
            return None, "Approval request not found"

        # Convert to domain model for validation
        approval_request = self._to_domain(db_model)
        now = datetime.now(UTC)

        # Check if can resolve
        can_resolve, error = approval_request.can_resolve(now)
        if not can_resolve:
            logger.warning(
                "approval_resolution_rejected",
                approval_request_id=approval_request_id,
                reason=error,
            )
            return None, error

        # Validate approver
        is_valid_approver, error = approval_request.validate_approver(approver_id)
        if not is_valid_approver:
            logger.warning(
                "approval_resolution_rejected",
                approval_request_id=approval_request_id,
                approver_id=approver_id,
                reason="invalid_approver",
                error=error,
            )
            return None, error

        # Check approver exists and is active
        approver = await self._get_approver(approver_id)
        if not approver:
            logger.warning(
                "approval_resolution_rejected",
                approval_request_id=approval_request_id,
                approver_id=approver_id,
                reason="approver_not_found",
            )
            return None, "Approver not found"

        if not approver.is_active:
            logger.warning(
                "approval_resolution_rejected",
                approval_request_id=approval_request_id,
                approver_id=approver_id,
                reason="approver_inactive",
            )
            return None, "Approver is not active"

        # Update the approval request atomically
        new_status = (
            ApprovalStatusDB.APPROVED
            if decision == ApprovalStatus.APPROVED
            else ApprovalStatusDB.DENIED
        )

        update_stmt = (
            update(ApprovalRequestDB)
            .where(
                ApprovalRequestDB.approval_request_id == approval_request_id,
                ApprovalRequestDB.status == ApprovalStatusDB.PENDING,
            )
            .values(
                status=new_status,
                approver_id=approver_id,
                resolved_at=now,
                resolution_comment=comment,
            )
        )
        update_result = await self.db.execute(update_stmt)

        if update_result.rowcount == 0:  # type: ignore[attr-defined]
            logger.warning(
                "approval_resolution_rejected",
                approval_request_id=approval_request_id,
                reason="concurrent_modification_or_already_resolved",
            )
            return (
                None,
                "Approval request was modified concurrently or is no longer pending",
            )

        await self.db.commit()
        await self.db.refresh(db_model)

        # Convert back to domain
        resolved_request = self._to_domain(db_model)

        logger.info(
            "approval_resolved",
            approval_request_id=approval_request_id,
            decision=decision.value,
            approver_id=approver_id,
            action_id=resolved_request.action_id,
        )

        return resolved_request, None

    async def verify_approval(
        self, action: Action, approval_request_id: str
    ) -> tuple[bool, str]:
        """
        Verify that an approval is valid for executing an action.

        Critical security checks:
        1. Approval exists
        2. Status is APPROVED
        3. Not expired
        4. Action fingerprint matches (prevents action substitution)

        Args:
            action: The action to be executed
            approval_request_id: The approval to verify

        Returns:
            (is_valid, reason)
        """
        approval = await self.get_request(approval_request_id)

        if not approval:
            return False, "Approval not found"

        if approval.status != ApprovalStatus.APPROVED:
            return False, f"Approval not in APPROVED state: {approval.status.value}"

        now = datetime.now(UTC)
        if approval.is_expired(now):
            return False, "Approval has expired"

        # CRITICAL: Verify action fingerprint matches
        if not verify_action_fingerprint(action, approval.action_fingerprint):
            logger.warning(
                "approval_fingerprint_mismatch",
                approval_request_id=approval_request_id,
                action_id=action.action_id,
                expected_fingerprint=approval.action_fingerprint,
                actual_fingerprint=generate_action_fingerprint(action),
            )
            return False, "Action fingerprint mismatch: action has been modified"

        return True, "Approval valid"

    async def _get_approver(self, approver_id: str) -> ApproverDB | None:
        """Fetch approver from database."""
        stmt = select(ApproverDB).where(ApproverDB.approver_id == approver_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_approver(
        self, approver_id: str, display_name: str, email: str | None = None
    ) -> ApproverDB:
        """
        Create a new approver identity.

        For MVP, this is a simple creation. Future phases will integrate
        with enterprise SSO and RBAC.

        Args:
            approver_id: Unique approver identifier
            display_name: Human-readable name
            email: Optional email address

        Returns:
            Created ApproverDB model
        """
        approver = ApproverDB(
            approver_id=approver_id,
            display_name=display_name,
            email=email,
            is_active=True,
        )
        self.db.add(approver)
        await self.db.commit()
        await self.db.refresh(approver)

        logger.info(
            "approver_created", approver_id=approver_id, display_name=display_name
        )

        return approver

    def _to_domain(self, db_model: ApprovalRequestDB) -> ApprovalRequest:
        """Convert database model to domain model."""
        reasons = []
        if db_model.reasons and isinstance(db_model.reasons, dict):
            reasons = db_model.reasons.get("reasons", [])

        # Ensure timestamps are timezone-aware (UTC)
        created_at = db_model.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=UTC)

        expires_at = db_model.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)

        resolved_at = db_model.resolved_at
        if resolved_at and resolved_at.tzinfo is None:
            resolved_at = resolved_at.replace(tzinfo=UTC)

        return ApprovalRequest(
            approval_request_id=db_model.approval_request_id,
            action_id=db_model.action_id,
            action_fingerprint=db_model.action_fingerprint,
            correlation_id=db_model.correlation_id,
            agent_id=str(db_model.agent_id),
            user_id=str(db_model.user_id) if db_model.user_id else None,
            session_id=str(db_model.session_id),
            tool_id=str(db_model.tool_id),
            operation=db_model.operation,
            resource=db_model.resource,
            environment=db_model.environment,
            status=ApprovalStatus(db_model.status.value),
            approver_id=db_model.approver_id,
            created_at=created_at,
            expires_at=expires_at,
            resolved_at=resolved_at,
            risk_score=db_model.risk_score,
            risk_level=db_model.risk_level,
            highest_threat_severity=db_model.highest_threat_severity,
            reasons=reasons,
            resolution_comment=db_model.resolution_comment,
        )
