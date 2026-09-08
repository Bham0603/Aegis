import json
from typing import Any

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.threat import ThreatDetectionResult, ThreatSeverity, ThreatType
from app.services.threat.base import BaseThreatDetector


class PayloadAnomalyDetector(BaseThreatDetector):
    MAX_PARAMS = 50
    MAX_STRING_LEN = 10000
    MAX_DEPTH = 10
    MAX_PAYLOAD_SIZE = 100 * 1024  # 100 KB

    @property
    def id(self) -> str:
        return "payload_anomaly_detector"

    @property
    def version(self) -> str:
        return "1.0"

    def _check_depth_and_strings(self, data: Any, current_depth: int = 0) -> str | None:
        if current_depth > self.MAX_DEPTH:
            return f"Payload nesting depth exceeds maximum allowed ({self.MAX_DEPTH})."

        if isinstance(data, dict):
            for v in data.values():
                err = self._check_depth_and_strings(v, current_depth + 1)
                if err:
                    return err
        elif isinstance(data, list):
            for item in data:
                err = self._check_depth_and_strings(item, current_depth + 1)
                if err:
                    return err
        elif isinstance(data, str) and len(data) > self.MAX_STRING_LEN:
            return f"Payload contains a string exceeding maximum allowed length ({self.MAX_STRING_LEN})."

        return None

    def detect(
        self, action: Action, context: SecurityContext
    ) -> ThreatDetectionResult | None:
        if not action.parameters:
            return None

        # 1. Parameter Count
        if len(action.parameters) > self.MAX_PARAMS:
            return ThreatDetectionResult(
                detector_id=self.id,
                detector_version=self.version,
                threat_type=ThreatType.SUSPICIOUS_PAYLOAD,
                severity=ThreatSeverity.HIGH,
                confidence="HIGH",
                reason=f"Action contains excessive parameter count ({len(action.parameters)} > {self.MAX_PARAMS}).",
            )

        # 2. String Length & Nesting Depth
        structural_err = self._check_depth_and_strings(action.parameters)
        if structural_err:
            return ThreatDetectionResult(
                detector_id=self.id,
                detector_version=self.version,
                threat_type=ThreatType.SUSPICIOUS_PAYLOAD,
                severity=ThreatSeverity.HIGH,
                confidence="HIGH",
                reason=structural_err,
            )

        # 3. Overall Serialized Size
        try:
            serialized_size = len(json.dumps(action.parameters))
            if serialized_size > self.MAX_PAYLOAD_SIZE:
                return ThreatDetectionResult(
                    detector_id=self.id,
                    detector_version=self.version,
                    threat_type=ThreatType.SUSPICIOUS_PAYLOAD,
                    severity=ThreatSeverity.HIGH,
                    confidence="HIGH",
                    reason=f"Payload serialized size exceeds maximum allowed ({serialized_size} bytes).",
                )
        except (TypeError, ValueError):
            return ThreatDetectionResult(
                detector_id=self.id,
                detector_version=self.version,
                threat_type=ThreatType.SUSPICIOUS_PAYLOAD,
                severity=ThreatSeverity.MEDIUM,
                confidence="MEDIUM",
                reason="Payload could not be serialized for size estimation.",
            )

        return None
