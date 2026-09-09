from abc import ABC, abstractmethod
from typing import Any

from app.domain.ai_security import AISecurityAssessment


class BaseAISecurityProvider(ABC):
    """
    Abstract interface for AI Security Intelligence providers.
    """

    @abstractmethod
    async def analyze_security_context(
        self, correlation_id: str, context: dict[str, Any]
    ) -> AISecurityAssessment:
        """
        Submits normalized, redacted context to the AI model and returns a structured assessment.
        """
