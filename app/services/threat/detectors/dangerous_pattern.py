from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.threat import ThreatDetectionResult, ThreatSeverity, ThreatType
from app.services.threat.base import BaseThreatDetector


class DangerousPatternDetector(BaseThreatDetector):
    @property
    def id(self) -> str:
        return "dangerous_pattern_detector"

    @property
    def version(self) -> str:
        return "1.0"

    def detect(
        self, action: Action, context: SecurityContext
    ) -> ThreatDetectionResult | None:
        op = (action.operation or "").lower()
        res = (action.resource or "").lower()

        # Identify destructive operations
        destructive_ops = {"delete", "drop", "destroy", "remove", "truncate"}
        is_destructive = any(d_op in op for d_op in destructive_ops)

        if not is_destructive:
            return None

        # Check if targeting sensitive or external resources
        sensitive_keywords = {"production", "prod", "auth", "secret", "password"}
        external_indicators = {"http://", "https://", "ftp://"}

        is_sensitive_resource = any(kw in res for kw in sensitive_keywords)
        is_external_resource = any(ind in res for ind in external_indicators)

        if is_sensitive_resource:
            return ThreatDetectionResult(
                detector_id=self.id,
                detector_version=self.version,
                threat_type=ThreatType.DANGEROUS_OPERATION_PATTERN,
                severity=ThreatSeverity.HIGH,
                confidence="MEDIUM",
                reason=f"Destructive operation '{action.operation}' targeting sensitive resource '{action.resource}'.",
            )

        if is_external_resource:
            return ThreatDetectionResult(
                detector_id=self.id,
                detector_version=self.version,
                threat_type=ThreatType.DANGEROUS_OPERATION_PATTERN,
                severity=ThreatSeverity.CRITICAL,
                confidence="HIGH",
                reason=f"Destructive operation '{action.operation}' targeting external resource '{action.resource}'.",
            )

        # Check broad scopes like "all" or "*"
        if res in {"*", "all"}:
            return ThreatDetectionResult(
                detector_id=self.id,
                detector_version=self.version,
                threat_type=ThreatType.DANGEROUS_OPERATION_PATTERN,
                severity=ThreatSeverity.CRITICAL,
                confidence="HIGH",
                reason=f"Destructive operation '{action.operation}' with unusually broad target scope '{action.resource}'.",
            )

        return None
