"""
Approval domain models for human-in-the-loop authorization.

These models enforce the security principles that:
1. AI agents cannot approve their own actions
2. Approvals are action-bound via cryptographic fingerprinting
3. Approvals expire and cannot be silently extended
4. Approvals cannot be transferred between actions
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ApprovalStatus(str, Enum):
    """
    Approval request lifecycle states.

    Valid transitions:
    - PENDING -> APPROVED
    - PENDING -> DENIED
    - PENDING -> EXPIRED
    - PENDING -> CANCELLED

    Terminal states (APPROVED, DENIED, EXPIRED, CANCELLED) cannot transition.
    """

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

    def is_terminal(self) -> bool:
        """Check if this status is terminal (no further transitions allowed)."""
        return self in {
            ApprovalStatus.APPROVED,
            ApprovalStatus.DENIED,
            ApprovalStatus.EXPIRED,
            ApprovalStatus.CANCELLED,
        }


class ApprovalRequest(BaseModel):
    """
    Domain model for a human approval request.

    An approval request is created when the Decision Engine returns REVIEW.
    It is cryptographically bound to the exact action being approved via
    the action_fingerprint field.

    Security Invariants:
    - One approval request maps to exactly one action
    - The action_fingerprint must match at resolution time
    - Approvals expire and cannot authorize actions after expiration
    - The approver_id must be distinct from agent_id (no self-approval)
    - Status transitions are monotonic (terminal states cannot change)
    """

    # Unique identifier for this approval request
    approval_request_id: str

    # The action being approved
    action_id: str

    # Cryptographic fingerprint of the action's security-relevant fields
    # This prevents approval reuse for different actions
    action_fingerprint: str

    # Request correlation for observability
    correlation_id: str

    # Identity context (from the action)
    agent_id: str
    user_id: str | None = None
    session_id: str

    # Action context (from the action)
    tool_id: str
    operation: str | None = None
    resource: str | None = None
    environment: str

    # Approval lifecycle
    status: ApprovalStatus = ApprovalStatus.PENDING

    # Identity of the human who will approve/deny
    # This MUST be distinct from agent_id
    required_approver_role: str | None = None

    # Identity of the human who actually approved/denied
    # Set when status transitions to APPROVED or DENIED
    approver_id: str | None = None

    # Timestamps
    created_at: datetime
    expires_at: datetime
    resolved_at: datetime | None = None

    # Security context from decision engine
    risk_score: int | None = None
    risk_level: str | None = None
    highest_threat_severity: str | None = None

    # Explanation for human review
    reasons: list[str] = Field(default_factory=list)

    # Optional human comment on approval/denial
    resolution_comment: str | None = None

    def is_expired(self, current_time: datetime) -> bool:
        """
        Check if this approval request has expired.

        Args:
            current_time: The current UTC time to check against

        Returns:
            True if current_time >= expires_at, False otherwise
        """
        return current_time >= self.expires_at

    def can_resolve(self, current_time: datetime) -> tuple[bool, str | None]:
        """
        Check if this approval request can be resolved.

        Returns:
            (can_resolve, error_reason)
            - (True, None) if resolution is allowed
            - (False, reason) if resolution is blocked
        """
        # Already resolved
        if self.status.is_terminal():
            return False, f"Approval already in terminal state: {self.status.value}"

        # Expired
        if self.is_expired(current_time):
            return False, "Approval request has expired"

        return True, None

    def validate_approver(self, approver_id: str) -> tuple[bool, str | None]:
        """
        Validate that the approver is authorized to resolve this request.

        Critical security check: Prevents self-approval.

        Args:
            approver_id: The identity attempting to approve

        Returns:
            (is_valid, error_reason)
        """
        # SECURITY: Agent cannot approve itself
        if approver_id == self.agent_id:
            return (
                False,
                "Self-approval is forbidden: agent cannot approve its own action",
            )

        # Future: Additional authorization checks (roles, permissions, etc.)

        return True, None


class ApprovalDecision(BaseModel):
    """
    The decision rendered by a human approver.

    This is submitted to resolve a pending approval request.
    """

    approval_request_id: str
    approver_id: str
    decision: ApprovalStatus  # Must be APPROVED or DENIED
    comment: str | None = None
    timestamp: datetime
