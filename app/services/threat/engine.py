import logging

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.threat import (
    ThreatAssessment,
    ThreatDetectionResult,
    ThreatSeverity,
    ThreatType,
)
from app.services.threat.base import BaseThreatDetector
from app.services.threat.detectors.dangerous_pattern import DangerousPatternDetector
from app.services.threat.detectors.malformed_action import MalformedActionDetector
from app.services.threat.detectors.payload_anomaly import PayloadAnomalyDetector

logger = logging.getLogger(__name__)

# Severity mapping for deterministic aggregation (highest wins)
SEVERITY_SCORE = {
    ThreatSeverity.LOW: 1,
    ThreatSeverity.MEDIUM: 2,
    ThreatSeverity.HIGH: 3,
    ThreatSeverity.CRITICAL: 4,
}


class ThreatEngine:
    """
    Executes a registry of deterministic threat detectors against an action.
    """

    def __init__(self):
        # Register enabled detectors in sequence
        self.detectors: list[BaseThreatDetector] = [
            MalformedActionDetector(),
            PayloadAnomalyDetector(),
            DangerousPatternDetector(),
        ]

    def _aggregate(self, findings: list[ThreatDetectionResult]) -> ThreatAssessment:
        if not findings:
            return ThreatAssessment(
                overall_severity=None, findings=[], explanation="No threats detected."
            )

        # Find highest severity
        highest_severity = max(
            findings, key=lambda f: SEVERITY_SCORE[f.severity]
        ).severity

        # Build explanation
        explanation_lines = [f"Threats detected (Highest: {highest_severity.value}):"]
        for f in findings:
            explanation_lines.append(
                f"- [{f.severity.value}] {f.detector_id} ({f.threat_type.value}): {f.reason}"
            )

        return ThreatAssessment(
            overall_severity=highest_severity,
            findings=findings,
            explanation="\n".join(explanation_lines),
        )

    def evaluate(self, action: Action, context: SecurityContext) -> ThreatAssessment:
        findings: list[ThreatDetectionResult] = []

        for detector in self.detectors:
            try:
                result = detector.detect(action, context)
                if result:
                    findings.append(result)
            except Exception as e:  # noqa: BLE001
                # Detector failure handling (fail-closed configurable)
                logger.error(f"Detector {detector.id} failed: {e}")
                # We inject a specific failure finding to ensure the failure is explicitly handled.
                # Depending on strictness, a detector crash is highly suspicious or indicates a malformed payload edge-case.
                findings.append(
                    ThreatDetectionResult(
                        detector_id=detector.id,
                        detector_version=detector.version,
                        threat_type=ThreatType.MALFORMED_ACTION,  # Reuse or we can add DETECTOR_FAILURE
                        severity=ThreatSeverity.HIGH,  # Treat crashes safely as HIGH severity
                        confidence="HIGH",
                        reason="Detector crashed during evaluation, defaulting to safe HIGH severity block.",
                    )
                )

        return self._aggregate(findings)
