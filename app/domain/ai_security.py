from enum import Enum

from pydantic import BaseModel, Field

from app.domain.threat import ThreatSeverity


class AIThreatType(str, Enum):
    DIRECT_PROMPT_INJECTION = "DIRECT_PROMPT_INJECTION"
    INDIRECT_PROMPT_INJECTION = "INDIRECT_PROMPT_INJECTION"
    GOAL_HIJACKING = "GOAL_HIJACKING"
    SEMANTIC_TOOL_POISONING = "SEMANTIC_TOOL_POISONING"
    MEMORY_POISONING = "MEMORY_POISONING"
    SEMANTIC_DATA_EXFILTRATION = "SEMANTIC_DATA_EXFILTRATION"
    MALICIOUS_INSTRUCTION = "MALICIOUS_INSTRUCTION"
    SUSPICIOUS_INTENT = "SUSPICIOUS_INTENT"
    NONE = "NONE"


class AISecurityStatus(str, Enum):
    SUCCESS = "SUCCESS"
    UNAVAILABLE = "UNAVAILABLE"
    FAILED = "FAILED"
    TIMEOUT = "TIMEOUT"


class AISecurityAssessment(BaseModel):
    assessment_id: str
    provider: str
    model: str
    analyzer_version: str = "1.0"
    prompt_version: str = "1.0"

    status: AISecurityStatus = AISecurityStatus.SUCCESS
    threat_detected: bool = False
    threat_type: AIThreatType = AIThreatType.NONE
    severity: ThreatSeverity | None = None
    confidence: float | None = None  # Expected 0.0 to 1.0

    reason: str = "No threat detected"
    indicators: list[str] = Field(default_factory=list)
    latency_ms: float | None = None
    recommended_action: str | None = None
