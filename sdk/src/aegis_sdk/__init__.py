"""
Aegis SDK — Python client for Aegis Runtime Security & Governance for AI Agents.

Usage:
    from aegis_sdk import AegisClient

    async with AegisClient(base_url="http://localhost:8000", api_key="...") as client:
        result = await client.evaluate_action(
            agent_id="research-agent",
            tool_id="database",
            operation="query",
            resource="customers",
        )
        if result.blocked:
            print(f"Blocked: {result.reasons}")
"""

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import (
    ActionBlockedError,
    AegisAuthenticationError,
    AegisAuthorizationError,
    AegisConflictError,
    AegisError,
    AegisNetworkError,
    AegisNotFoundError,
    AegisRateLimitError,
    AegisServerError,
    AegisTimeoutError,
    AegisUnavailableError,
    AegisValidationError,
    ApprovalRequiredError,
)
from aegis_sdk.models import (
    ActionRequest,
    ApprovalInfo,
    ApprovalStatus,
    AttackRunResult,
    AttackScenario,
    AuditEvent,
    Decision,
    EvaluationResult,
    RiskLevel,
    ThreatSeverity,
    ThreatType,
)
from aegis_sdk.protect import ProtectedTool, protect

__version__ = "0.1.0"

__all__ = [
    # Client
    "AegisClient",
    # Models
    "ActionRequest",
    "ApprovalInfo",
    "ApprovalStatus",
    "AttackRunResult",
    "AttackScenario",
    "AuditEvent",
    "Decision",
    "EvaluationResult",
    "RiskLevel",
    "ThreatSeverity",
    "ThreatType",
    # Errors
    "ActionBlockedError",
    "AegisAuthenticationError",
    "AegisAuthorizationError",
    "AegisConflictError",
    "AegisError",
    "AegisNetworkError",
    "AegisNotFoundError",
    "AegisRateLimitError",
    "AegisServerError",
    "AegisTimeoutError",
    "AegisUnavailableError",
    "AegisValidationError",
    "ApprovalRequiredError",
    # Protection
    "ProtectedTool",
    "protect",
]
