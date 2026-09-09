"""
Aegis SDK data models.

These models represent the SDK's view of Aegis backend data.
They mirror the backend API contract but do NOT perform any
local security calculations — all values originate from the backend.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

# ---------------------------------------------------------------------------
# Enums — synchronized with backend values
# ---------------------------------------------------------------------------


class Decision(str, Enum):
    """Security decision returned by the Aegis backend."""

    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"

    @classmethod
    def _missing_(cls, value: object) -> Decision | None:
        """Gracefully handle unknown decision values from the backend."""
        if isinstance(value, str):
            # Return BLOCK for safety on unknown values
            return cls.BLOCK
        return None


class RiskLevel(str, Enum):
    """Risk level as assessed by the Aegis backend."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def _missing_(cls, value: object) -> RiskLevel | None:
        if isinstance(value, str):
            return cls.CRITICAL  # Fail-safe for unknown risk
        return None


class ThreatSeverity(str, Enum):
    """Threat severity as determined by the Aegis backend."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

    @classmethod
    def _missing_(cls, value: object) -> ThreatSeverity | None:
        if isinstance(value, str):
            return cls.CRITICAL
        return None


class ThreatType(str, Enum):
    """Threat types recognized by the Aegis backend."""

    MALFORMED_ACTION = "MALFORMED_ACTION"
    SUSPICIOUS_PAYLOAD = "SUSPICIOUS_PAYLOAD"
    DANGEROUS_OPERATION_PATTERN = "DANGEROUS_OPERATION_PATTERN"

    @classmethod
    def _missing_(cls, value: object) -> ThreatType | None:
        if isinstance(value, str):
            # Return a safe fallback rather than crashing
            return cls.SUSPICIOUS_PAYLOAD
        return None


class ApprovalStatus(str, Enum):
    """Approval lifecycle status."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"

    @classmethod
    def _missing_(cls, value: object) -> ApprovalStatus | None:
        if isinstance(value, str):
            return cls.PENDING
        return None


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------


class ActionRequest:
    """
    SDK representation of an action to be evaluated by the Aegis backend.
    Field names match the backend API contract exactly.
    """

    def __init__(
        self,
        *,
        agent_id: str,
        session_id: str,
        tool_id: str,
        user_id: str | None = None,
        operation: str | None = None,
        resource: str | None = None,
        parameters: dict[str, Any] | None = None,
        environment: str = "unknown",
        authorization_context: dict[str, Any] | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.session_id = session_id
        self.tool_id = tool_id
        self.user_id = user_id
        self.operation = operation
        self.resource = resource
        self.parameters = parameters or {}
        self.environment = environment
        self.authorization_context = authorization_context or {}

    def to_dict(self) -> dict[str, Any]:
        """Serialize to the backend API request format."""
        payload: dict[str, Any] = {
            "agent_id": self.agent_id,
            "session_id": self.session_id,
            "tool_id": self.tool_id,
            "environment": self.environment,
        }
        if self.user_id is not None:
            payload["user_id"] = self.user_id
        if self.operation is not None:
            payload["operation"] = self.operation
        if self.resource is not None:
            payload["resource"] = self.resource
        if self.parameters:
            payload["parameters"] = self.parameters
        if self.authorization_context:
            payload["authorization_context"] = self.authorization_context
        return payload

    def __repr__(self) -> str:
        return (
            f"ActionRequest(agent_id={self.agent_id!r}, tool_id={self.tool_id!r}, "
            f"operation={self.operation!r}, resource={self.resource!r})"
        )


# ---------------------------------------------------------------------------
# Response Models
# ---------------------------------------------------------------------------


class EvaluationResult:
    """
    SDK representation of a security evaluation result from the Aegis backend.

    The convenience properties (.allowed, .review_required, .blocked) are
    presentation helpers only — they simply map the backend decision
    to developer-friendly booleans. They do NOT perform any local
    security calculation.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.action_id: str = data.get("action_id", "")
        self.correlation_id: str = data.get("correlation_id", "")
        self.timestamp: str = data.get("timestamp", "")
        self.decision: Decision = Decision(data.get("decision", "BLOCK"))

        # Risk (backend-assessed)
        self.risk_score: int | None = data.get("risk_score")
        self.risk_level: str | None = data.get("risk_level")
        self.risk_explanation: str | None = data.get("risk_explanation")
        self.risk_factors: list[dict[str, Any]] = data.get("risk_factors") or []

        # Decision context
        self.reasons: list[str] = data.get("reasons") or []
        self.violated_policies: list[str] = data.get("violated_policies") or []
        self.triggered_detectors: list[str] = data.get("triggered_detectors") or []

        # Threat (backend-assessed)
        self.highest_threat_severity: str | None = data.get("highest_threat_severity")
        self.threat_results: list[dict[str, Any]] = data.get("threat_results") or []

        # Approval
        self.approval_required: bool = data.get("approval_required", False)
        self.approval_request_id: str | None = data.get("approval_request_id")

    # -- Convenience properties (presentation helpers, NOT local decisions) --

    @property
    def allowed(self) -> bool:
        """True if the backend decision is ALLOW."""
        return self.decision == Decision.ALLOW

    @property
    def review_required(self) -> bool:
        """True if the backend decision is REVIEW."""
        return self.decision == Decision.REVIEW

    @property
    def blocked(self) -> bool:
        """True if the backend decision is BLOCK."""
        return self.decision == Decision.BLOCK

    def __repr__(self) -> str:
        return (
            f"EvaluationResult(action_id={self.action_id!r}, "
            f"decision={self.decision.value!r}, "
            f"risk_level={self.risk_level!r})"
        )


class ApprovalInfo:
    """SDK representation of an approval request from the Aegis backend."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.approval_request_id: str = data.get("approval_request_id", "")
        self.action_id: str = data.get("action_id", "")
        self.correlation_id: str = data.get("correlation_id", "")
        self.agent_id: str = data.get("agent_id", "")
        self.user_id: str | None = data.get("user_id")
        self.session_id: str = data.get("session_id", "")
        self.tool_id: str = data.get("tool_id", "")
        self.operation: str | None = data.get("operation")
        self.resource: str | None = data.get("resource")
        self.environment: str = data.get("environment", "")
        self.status: ApprovalStatus = ApprovalStatus(data.get("status", "PENDING"))
        self.approver_id: str | None = data.get("approver_id")
        self.created_at: str = data.get("created_at", "")
        self.expires_at: str = data.get("expires_at", "")
        self.resolved_at: str | None = data.get("resolved_at")
        self.risk_score: int | None = data.get("risk_score")
        self.risk_level: str | None = data.get("risk_level")
        self.highest_threat_severity: str | None = data.get("highest_threat_severity")
        self.reasons: list[str] = data.get("reasons") or []
        self.resolution_comment: str | None = data.get("resolution_comment")

    @property
    def is_approved(self) -> bool:
        return self.status == ApprovalStatus.APPROVED

    @property
    def is_denied(self) -> bool:
        return self.status == ApprovalStatus.DENIED

    @property
    def is_pending(self) -> bool:
        return self.status == ApprovalStatus.PENDING

    def __repr__(self) -> str:
        return (
            f"ApprovalInfo(id={self.approval_request_id!r}, "
            f"status={self.status.value!r})"
        )


class AuditEvent:
    """SDK representation of an audit event from the Aegis backend."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.event_id: str = data.get("event_id", "")
        self.event_type: str = data.get("event_type", "")
        self.timestamp: str = data.get("timestamp", "")
        self.correlation_id: str = data.get("correlation_id", "")
        self.action_id: str | None = data.get("action_id")
        self.agent_id: str | None = data.get("agent_id")
        self.user_id: str | None = data.get("user_id")
        self.session_id: str | None = data.get("session_id")
        self.tool_id: str | None = data.get("tool_id")
        self.operation: str | None = data.get("operation")
        self.resource: str | None = data.get("resource")
        self.environment: str | None = data.get("environment")
        self.final_decision: str | None = data.get("final_decision")
        self.decision_reasons: list[str] = data.get("decision_reasons") or []
        self.risk_score: int | None = data.get("risk_score")
        self.risk_level: str | None = data.get("risk_level")
        self.threat_severity: str | None = data.get("threat_severity")

    def __repr__(self) -> str:
        return (
            f"AuditEvent(event_id={self.event_id!r}, "
            f"event_type={self.event_type!r})"
        )


class AttackScenario:
    """SDK representation of an Attack Lab scenario."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.scenario_id: str = data.get("scenario_id", "")
        self.name: str = data.get("name", "")
        self.description: str = data.get("description", "")
        self.category: str = data.get("category", "")
        self.severity: str = data.get("severity", "")
        self.expected_security_behavior: str = data.get("expected_security_behavior", "")

    def __repr__(self) -> str:
        return f"AttackScenario(id={self.scenario_id!r}, name={self.name!r})"


class AttackRunResult:
    """SDK representation of an Attack Lab run result."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self.run_id: str = data.get("run_id", "")
        self.scenario_id: str = data.get("scenario_id", "")
        self.status: str = data.get("status", "")
        self.expected_outcome: str = data.get("expected_outcome", "")
        self.actual_outcome: str = data.get("actual_outcome", "")
        self.explanation: str = data.get("explanation", "")
        self.correlation_id: str = data.get("correlation_id", "")
        self.risk_score: int | None = data.get("risk_score")
        self.risk_level: str | None = data.get("risk_level")
        self.threat_severity: str | None = data.get("threat_severity")
        self.final_decision: str | None = data.get("final_decision")
        self.triggered_detectors: list[str] = data.get("triggered_detectors") or []
        self.audit_event_ids: list[str] = data.get("audit_event_ids") or []

    @property
    def passed(self) -> bool:
        return self.status == "PASS"

    def __repr__(self) -> str:
        return (
            f"AttackRunResult(run_id={self.run_id!r}, "
            f"status={self.status!r})"
        )
