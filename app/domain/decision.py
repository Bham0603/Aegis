from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DecisionEnum(str, Enum):
    ALLOW = "ALLOW"
    REVIEW = "REVIEW"
    BLOCK = "BLOCK"


class TrustClassEnum(str, Enum):
    TRUSTED = "TRUSTED"
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    UNTRUSTED = "UNTRUSTED"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class TrustResult(BaseModel):
    is_trusted: bool
    trust_class: TrustClassEnum
    reasons: list[str] = Field(default_factory=list)


class PermissionStatusEnum(str, Enum):
    GRANTED = "GRANTED"
    DENIED = "DENIED"
    UNKNOWN = "UNKNOWN"


class PermissionResult(BaseModel):
    status: PermissionStatusEnum
    reasons: list[str] = Field(default_factory=list)


class SecurityDecision(BaseModel):
    """
    The final output of the Security Gateway evaluation pipeline.
    """

    action_id: str
    correlation_id: str
    timestamp: datetime

    decision: DecisionEnum

    risk_score: int | None = None
    risk_level: str | None = None

    reasons: list[str] = Field(default_factory=list)
    violated_policies: list[str] = Field(default_factory=list)
    triggered_detectors: list[str] = Field(default_factory=list)

    approval_required: bool = False
