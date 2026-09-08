from datetime import UTC

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.threat import ThreatSeverity, ThreatType
from app.services.threat.detectors.dangerous_pattern import DangerousPatternDetector
from app.services.threat.detectors.malformed_action import MalformedActionDetector
from app.services.threat.detectors.payload_anomaly import PayloadAnomalyDetector


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


def test_malformed_action_missing_operation():
    detector = MalformedActionDetector()
    context = SecurityContext(action=make_action())
    action = make_action(parameters={"some": "param"})

    result = detector.detect(action, context)
    assert result is not None
    assert result.threat_type == ThreatType.MALFORMED_ACTION
    assert result.severity == ThreatSeverity.MEDIUM


def test_malformed_action_missing_tool():
    detector = MalformedActionDetector()
    context = SecurityContext(action=make_action())
    action = make_action(operation="read")
    action.tool_id = ""  # Simulate missing

    result = detector.detect(action, context)
    assert result is not None
    assert result.threat_type == ThreatType.MALFORMED_ACTION
    assert result.severity == ThreatSeverity.HIGH


def test_payload_anomaly_normal():
    detector = PayloadAnomalyDetector()
    context = SecurityContext(action=make_action())
    action = make_action(parameters={"a": 1, "b": "test"})

    result = detector.detect(action, context)
    assert result is None


def test_payload_anomaly_excessive_params():
    detector = PayloadAnomalyDetector()
    context = SecurityContext(action=make_action())
    action = make_action(parameters={f"k{i}": i for i in range(51)})

    result = detector.detect(action, context)
    assert result is not None
    assert result.threat_type == ThreatType.SUSPICIOUS_PAYLOAD
    assert result.severity == ThreatSeverity.HIGH
    assert "excessive parameter count" in result.reason


def test_payload_anomaly_large_string():
    detector = PayloadAnomalyDetector()
    context = SecurityContext(action=make_action())
    action = make_action(parameters={"huge": "A" * 10001})

    result = detector.detect(action, context)
    assert result is not None
    assert result.threat_type == ThreatType.SUSPICIOUS_PAYLOAD
    assert result.severity == ThreatSeverity.HIGH
    assert "exceeding maximum allowed length" in result.reason


def test_payload_anomaly_deep_nesting():
    detector = PayloadAnomalyDetector()
    context = SecurityContext(action=make_action())

    deep_dict = {}
    current = deep_dict
    for _ in range(12):
        current["nested"] = {}
        current = current["nested"]

    action = make_action(parameters=deep_dict)

    result = detector.detect(action, context)
    assert result is not None
    assert result.threat_type == ThreatType.SUSPICIOUS_PAYLOAD
    assert result.severity == ThreatSeverity.HIGH
    assert "nesting depth" in result.reason


def test_dangerous_pattern_normal():
    detector = DangerousPatternDetector()
    context = SecurityContext(action=make_action())
    action = make_action(operation="read", resource="production_db")

    result = detector.detect(action, context)
    assert result is None


def test_dangerous_pattern_sensitive():
    detector = DangerousPatternDetector()
    context = SecurityContext(action=make_action())
    action = make_action(operation="delete", resource="production_db")

    result = detector.detect(action, context)
    assert result is not None
    assert result.threat_type == ThreatType.DANGEROUS_OPERATION_PATTERN
    assert result.severity == ThreatSeverity.HIGH
    assert "sensitive resource" in result.reason


def test_dangerous_pattern_external():
    detector = DangerousPatternDetector()
    context = SecurityContext(action=make_action())
    action = make_action(operation="drop", resource="https://evil.com/upload")

    result = detector.detect(action, context)
    assert result is not None
    assert result.threat_type == ThreatType.DANGEROUS_OPERATION_PATTERN
    assert result.severity == ThreatSeverity.CRITICAL
    assert "external resource" in result.reason


def test_dangerous_pattern_broad():
    detector = DangerousPatternDetector()
    context = SecurityContext(action=make_action())
    action = make_action(operation="delete", resource="*")

    result = detector.detect(action, context)
    assert result is not None
    assert result.threat_type == ThreatType.DANGEROUS_OPERATION_PATTERN
    assert result.severity == ThreatSeverity.CRITICAL
    assert "broad target scope" in result.reason
