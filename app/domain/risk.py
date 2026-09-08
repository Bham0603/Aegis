from enum import Enum

from pydantic import BaseModel, Field


class RiskLevelEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskFactorCategoryEnum(str, Enum):
    OPERATION_SENSITIVITY = "OPERATION_SENSITIVITY"
    ENVIRONMENT = "ENVIRONMENT"
    TRUST = "TRUST"
    RESOURCE = "RESOURCE"
    DESTINATION = "DESTINATION"
    REVERSIBILITY = "REVERSIBILITY"
    BLAST_RADIUS = "BLAST_RADIUS"
    OTHER = "OTHER"


class RiskFactor(BaseModel):
    name: str
    contribution: int
    category: RiskFactorCategoryEnum
    reason: str


class RiskAssessment(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevelEnum
    factors: list[RiskFactor] = Field(default_factory=list)
    explanation: str
    model_version: str
