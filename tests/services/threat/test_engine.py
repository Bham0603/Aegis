from datetime import UTC

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.threat import ThreatDetectionResult, ThreatSeverity, ThreatType
from app.services.threat.base import BaseThreatDetector
from app.services.threat.engine import ThreatEngine


def make_action(operation=None, resource=None, parameters=None) -> Action:
    from datetime import datetime

    return Action(
        action_id="act_test",
        correlation_id="trace_test",
        timestamp=datetime.now(UTC),
        agent_id="00000000-0000-0000-0000-000000000000",
        session_id="11111111-1111-1111-1111-111111111111",
        tool_id="tool_test",
        operation=operation,
        resource=resource,
        parameters=parameters or {},
        environment="test",
        authorization_context={},
    )


class MockDetector(BaseThreatDetector):
    def __init__(self, result: ThreatDetectionResult | None, will_crash: bool = False):
        self._result = result
        self._will_crash = will_crash

    @property
    def id(self) -> str:
        return "mock_detector"

    @property
    def version(self) -> str:
        return "1.0"

    def detect(
        self, action: Action, context: SecurityContext
    ) -> ThreatDetectionResult | None:
        if self._will_crash:
            raise RuntimeError("Intentional crash")
        return self._result


def test_engine_no_threats():
    engine = ThreatEngine()
    engine.detectors = [MockDetector(None)]

    action = make_action()
    context = SecurityContext(action=action)
    assessment = engine.evaluate(action, context)

    assert assessment.overall_severity is None
    assert len(assessment.findings) == 0


def test_engine_aggregation():
    engine = ThreatEngine()
    engine.detectors = [
        MockDetector(
            ThreatDetectionResult(
                detector_id="mock_1",
                detector_version="1.0",
                threat_type=ThreatType.MALFORMED_ACTION,
                severity=ThreatSeverity.LOW,
                confidence="LOW",
                reason="low threat",
            )
        ),
        MockDetector(
            ThreatDetectionResult(
                detector_id="mock_2",
                detector_version="1.0",
                threat_type=ThreatType.SUSPICIOUS_PAYLOAD,
                severity=ThreatSeverity.HIGH,
                confidence="HIGH",
                reason="high threat",
            )
        ),
        MockDetector(None),
    ]

    action = make_action()
    context = SecurityContext(action=action)
    assessment = engine.evaluate(action, context)

    assert assessment.overall_severity == ThreatSeverity.HIGH
    assert len(assessment.findings) == 2


def test_engine_detector_crash_fail_closed():
    engine = ThreatEngine()
    engine.detectors = [MockDetector(None, will_crash=True)]

    action = make_action()
    context = SecurityContext(action=action)
    assessment = engine.evaluate(action, context)

    assert assessment.overall_severity == ThreatSeverity.HIGH
    assert len(assessment.findings) == 1
    assert assessment.findings[0].threat_type == ThreatType.MALFORMED_ACTION
    assert "Detector crashed" in assessment.findings[0].reason
