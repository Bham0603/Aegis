from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Action(BaseModel):
    """
    The normalized domain representation of an AI agent's action.
    This object is strictly decoupled from the API payload layer.
    """

    action_id: str
    correlation_id: str
    timestamp: datetime

    # Identity
    agent_id: str
    session_id: str
    user_id: str | None = None

    # Target Operation
    tool_id: str
    operation: str | None = None
    resource: str | None = None

    # Payload
    parameters: dict[str, Any] = Field(default_factory=dict)

    # Context
    environment: str = "unknown"
    authorization_context: dict[str, Any] = Field(default_factory=dict)
