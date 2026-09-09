from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AttackCategory(str, Enum):
    PROMPT_INJECTION = "PROMPT_INJECTION"
    INDIRECT_PROMPT_INJECTION = "INDIRECT_PROMPT_INJECTION"
    TOOL_MISUSE = "TOOL_MISUSE"
    PRIVILEGE_ESCALATION = "PRIVILEGE_ESCALATION"
    DATA_EXFILTRATION = "DATA_EXFILTRATION"
    DESTRUCTIVE_ACTION = "DESTRUCTIVE_ACTION"
    MEMORY_POISONING = "MEMORY_POISONING"
    APPROVAL_BYPASS = "APPROVAL_BYPASS"
    TOOL_POISONING = "TOOL_POISONING"
    EXCESSIVE_AUTONOMY = "EXCESSIVE_AUTONOMY"
    MCP_EXPLOIT = "MCP_EXPLOIT"


class AttackRunStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"


class AttackScenario(BaseModel):
    """
    Declarative model for an attack scenario.
    Does not contain arbitrary executable code.
    """

    scenario_id: str
    version: str
    category: AttackCategory
    name: str
    description: str
    severity: str
    prerequisites: list[str] = Field(default_factory=list)

    # The exact payload that will be converted to an Action
    synthetic_inputs: dict[str, Any]

    # Expected outcomes
    expected_security_behavior: str  # e.g., "BLOCK", "REVIEW", "ALLOW"
    limitations: str | None = None


class AttackRunResult(BaseModel):
    """
    Machine-readable result of executing an AttackScenario.
    """

    run_id: str
    scenario_id: str
    started_at: datetime
    completed_at: datetime
    correlation_id: str

    expected_outcome: str
    actual_outcome: str
    status: AttackRunStatus

    # Detailed security provenance
    permission_result: str | None = None
    trust_result: str | None = None
    policy_result: str | None = None
    risk_score: int | None = None
    risk_level: str | None = None
    threat_severity: str | None = None
    approval_result: str | None = None
    final_decision: str | None = None

    triggered_detectors: list[str] = Field(default_factory=list)
    audit_event_ids: list[str] = Field(default_factory=list)

    explanation: str
    limitations: str | None = None
