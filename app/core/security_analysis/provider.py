from abc import ABC, abstractmethod
from typing import Any


class SecurityAnalysisProvider(ABC):
    """
    Abstract base class for the AI Security Analysis Engine.
    This separates the core gateway architecture from the LLM provider.
    Future phases will implement this using Gemini for advanced threat detection.
    """

    @abstractmethod
    async def analyze_action_threat(
        self, action_payload: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Analyze an incoming action for sophisticated threats (e.g., Prompt Injection).

        Args:
            action_payload: The normalized action request.

        Returns:
            A dictionary containing threat signals, confidence, and severity.
        """

    @abstractmethod
    async def classify_risk(self, action_payload: dict[str, Any]) -> int:
        """
        Optionally augment deterministic risk scoring with AI-driven classification.
        """
