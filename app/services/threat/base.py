import abc

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.threat import ThreatDetectionResult


class BaseThreatDetector(abc.ABC):
    """
    Abstract base class for deterministic threat detectors.
    """

    @property
    @abc.abstractmethod
    def id(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def version(self) -> str:
        pass

    @abc.abstractmethod
    def detect(
        self, action: Action, context: SecurityContext
    ) -> ThreatDetectionResult | None:
        """
        Evaluate the action and context for threats.
        Returns a ThreatDetectionResult if a threat is found, otherwise None.
        """
