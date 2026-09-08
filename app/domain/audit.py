from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AuditEventType(str, Enum):
    ACTION_RECEIVED = "ACTION_RECEIVED"
    ACTION_EVALUATED = "ACTION_EVALUATED"
    APPROVAL_REQUESTED = "APPROVAL_REQUESTED"
    APPROVAL_APPROVED = "APPROVAL_APPROVED"
    APPROVAL_DENIED = "APPROVAL_DENIED"
    APPROVAL_EXPIRED = "APPROVAL_EXPIRED"
    SECURITY_EVALUATION_FAILED = "SECURITY_EVALUATION_FAILED"


class AuditEvent(BaseModel):
    """
    The normalized domain representation of a security audit event.
    This preserves the provenance of a security decision.
    """

    event_id: str
    event_version: str = "1.0"
    event_type: AuditEventType
    timestamp: datetime
    correlation_id: str
    action_id: str | None = None

    # Actor Context
    user_id: str | None = None
    agent_id: str | None = None
    session_id: str | None = None

    # Target Context
    tool_id: str | None = None
    operation: str | None = None
    resource: str | None = None
    environment: str | None = None

    # Security Decision Provenance
    permission_result: str | None = None
    trust_result: str | None = None
    policy_result: str | None = None
    risk_score: int | None = None
    risk_level: str | None = None
    threat_severity: str | None = None
    approval_result: str | None = None

    final_decision: str | None = None
    decision_reasons: list[str] = Field(default_factory=list)

    # Action Payload (Redacted/Sanitized)
    redacted_parameters: dict[str, Any] | None = None

    # Extra
    metadata: dict[str, Any] = Field(default_factory=dict)
