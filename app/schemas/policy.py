import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.policy import PolicyEffect, PolicyStatus


class PolicyRuleSchema(BaseModel):
    effect: PolicyEffect
    condition: dict[str, dict[str, Any]] = Field(
        ...,
        description="Condition dict mapping fields to operator maps e.g. {'parameters.path': {'eq': '/etc/passwd'}}",
    )


class PolicyBase(BaseModel):
    name: str
    description: str | None = None
    version: str = "1.0"
    status: PolicyStatus = PolicyStatus.ACTIVE
    priority: int = 0
    rules: list[PolicyRuleSchema] = Field(default_factory=list)


class PolicyCreate(PolicyBase):
    pass


class PolicyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    version: str | None = None
    status: PolicyStatus | None = None
    priority: int | None = None
    rules: list[PolicyRuleSchema] | None = None


class PolicyResponse(PolicyBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
