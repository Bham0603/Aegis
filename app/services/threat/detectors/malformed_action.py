from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.threat import ThreatDetectionResult, ThreatSeverity, ThreatType
from app.services.threat.base import BaseThreatDetector


class MalformedActionDetector(BaseThreatDetector):
    @property
    def id(self) -> str:
        return "malformed_action_detector"

    @property
    def version(self) -> str:
        return "1.0"

    def detect(
        self, action: Action, context: SecurityContext
    ) -> ThreatDetectionResult | None:
        # Check for missing tool or missing operation while parameters are present
        if not action.operation and action.parameters:
            return ThreatDetectionResult(
                detector_id=self.id,
                detector_version=self.version,
                threat_type=ThreatType.MALFORMED_ACTION,
                severity=ThreatSeverity.MEDIUM,
                confidence="HIGH",
                reason="Action contains parameters but no defined operation.",
            )

        if not action.tool_id:
            return ThreatDetectionResult(
                detector_id=self.id,
                detector_version=self.version,
                threat_type=ThreatType.MALFORMED_ACTION,
                severity=ThreatSeverity.HIGH,
                confidence="HIGH",
                reason="Action is missing a tool_id.",
            )

        return None
