from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ThreatSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ThreatType(str, Enum):
    MALFORMED_ACTION = "MALFORMED_ACTION"
    SUSPICIOUS_PAYLOAD = "SUSPICIOUS_PAYLOAD"
    DANGEROUS_OPERATION_PATTERN = "DANGEROUS_OPERATION_PATTERN"
    # Other types can be added here in the future


class ThreatDetectionResult(BaseModel):
    detector_id: str
    detector_version: str
    threat_type: ThreatType
    severity: ThreatSeverity
    confidence: (
        str  # e.g., "HIGH", "MEDIUM", "LOW" based on deterministic rule strength
    )
    reason: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class ThreatAssessment(BaseModel):
    overall_severity: ThreatSeverity | None = None
    findings: list[ThreatDetectionResult] = Field(default_factory=list)
    explanation: str = "No threats detected."
