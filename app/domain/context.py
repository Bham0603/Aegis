from pydantic import BaseModel

from app.domain.action import Action
from app.schemas.registry import (
    AgentResponse,
    AgentToolBindingResponse,
    SessionResponse,
    ToolResponse,
    UserAgentDelegationResponse,
    UserResponse,
)


class SecurityContext(BaseModel):
    """
    Wrapper holding the Action and potentially other context items
    that evaluators (Policy, Risk, Threat) might need to produce a decision.
    """

    action: Action
    trust_score: int | None = None

    # Registry context
    agent: AgentResponse | None = None
    user: UserResponse | None = None
    session: SessionResponse | None = None
    tool: ToolResponse | None = None
    agent_tool_binding: AgentToolBindingResponse | None = None
    user_agent_delegation: UserAgentDelegationResponse | None = None
