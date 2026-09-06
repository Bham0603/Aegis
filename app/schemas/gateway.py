from typing import Any

from pydantic import BaseModel, Field

from app.domain.decision import DecisionEnum, SecurityDecision


class ActionRequest(BaseModel):
    agent_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    user_id: str | None = None

    tool_id: str = Field(..., min_length=1)
    operation: str | None = None
    resource: str | None = None

    parameters: dict[str, Any] = Field(default_factory=dict)

    environment: str = Field(default="unknown")
    authorization_context: dict[str, Any] = Field(default_factory=dict)


# Re-export DecisionEnum and SecurityDecision for API ease of use
__all__ = ["ActionRequest", "DecisionEnum", "SecurityDecision"]
