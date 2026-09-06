from pydantic import BaseModel

from app.domain.action import Action


class SecurityContext(BaseModel):
    """
    Wrapper holding the Action and potentially other context items
    that evaluators (Policy, Risk, Threat) might need to produce a decision.
    """

    action: Action
    trust_score: int | None = None
