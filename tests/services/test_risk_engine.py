import uuid
from datetime import UTC, datetime

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.decision import TrustClassEnum, TrustResult
from app.domain.risk import RiskLevelEnum
from app.services.risk_engine import RiskEngine


def make_action(
    operation: str = "read",
    environment: str = "production",
    resource: str = "public",
    tool_id: str = "trusted_tool",
) -> Action:
    return Action(
        action_id=str(uuid.uuid4()),
        correlation_id=str(uuid.uuid4()),
        timestamp=datetime.now(UTC),
        agent_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        tool_id=tool_id,
        operation=operation,
        resource=resource,
        environment=environment,
    )


def test_risk_engine_safe_action():
    engine = RiskEngine()
    action = make_action(
        operation="read",
        environment="development",
        resource="public",
        tool_id="safe_tool",
    )
    context = SecurityContext(action=action)
    trust_result = TrustResult(is_trusted=True, trust_class=TrustClassEnum.TRUSTED)

    assessment = engine.assess(action, context, trust_result)

    # Base (read=10) * env (dev=0.5) + trust (0) + dest (0) = 5
    assert assessment.risk_score == 5
    assert assessment.risk_level == RiskLevelEnum.LOW
    assert len(assessment.factors) == 4  # op, env, trust, dest


def test_risk_engine_critical_action():
    engine = RiskEngine()
    action = make_action(
        operation="delete",
        environment="production",
        resource="critical",
        tool_id="db_tool",
    )
    context = SecurityContext(action=action)
    trust_result = TrustResult(is_trusted=False, trust_class=TrustClassEnum.UNTRUSTED)

    assessment = engine.assess(action, context, trust_result)

    # Base (delete=80) * env (prod=1.5) + trust (25) + dest (0) = 120 + 25 = 145 -> clamped to 100
    assert assessment.risk_score == 100
    assert assessment.risk_level == RiskLevelEnum.CRITICAL


def test_risk_engine_external_destination():
    engine = RiskEngine()
    # Resource contains https://
    action = make_action(
        operation="write",
        environment="staging",
        resource="https://external.com",
        tool_id="http_client",
    )
    context = SecurityContext(action=action)
    trust_result = TrustResult(is_trusted=True, trust_class=TrustClassEnum.TRUSTED)

    assessment = engine.assess(action, context, trust_result)

    # Base (write=40) * env (staging=1.0) + trust (0) + dest (15) = 55
    assert assessment.risk_score == 55
    assert assessment.risk_level == RiskLevelEnum.HIGH

    # Check explanation
    assert "Action involves an external destination" in assessment.explanation
    assert "+ 15" in assessment.explanation or "+15" in assessment.explanation


def test_risk_engine_missing_context():
    engine = RiskEngine()
    # Unknown operation and environment
    action = make_action(operation="", environment="")
    context = SecurityContext(action=action)

    assessment = engine.assess(action, context, None)

    # Base (unknown=20) * env (unknown=1.5) + trust (None=0) + dest (0) = 30
    assert assessment.risk_score == 30
    assert assessment.risk_level == RiskLevelEnum.MEDIUM


def test_risk_engine_invariants():
    engine = RiskEngine()
    # Should never be < 0 or > 100
    action = make_action(
        operation="delete",
        environment="production",
        resource="critical",
        tool_id="email",
    )
    context = SecurityContext(action=action)
    trust_result = TrustResult(is_trusted=False, trust_class=TrustClassEnum.UNTRUSTED)

    assessment = engine.assess(action, context, trust_result)
    assert 0 <= assessment.risk_score <= 100
    assert assessment.risk_level == RiskLevelEnum.CRITICAL

    # Verify deterministic repeated execution
    assessment2 = engine.assess(action, context, trust_result)
    assert assessment.risk_score == assessment2.risk_score
    assert assessment.explanation == assessment2.explanation


def test_risk_level_boundaries():
    engine = RiskEngine()
    # 25 should be LOW
    assert engine._determine_risk_level(25) == RiskLevelEnum.LOW
    # 26 should be MEDIUM
    assert engine._determine_risk_level(26) == RiskLevelEnum.MEDIUM
    # 50 should be MEDIUM
    assert engine._determine_risk_level(50) == RiskLevelEnum.MEDIUM
    # 51 should be HIGH
    assert engine._determine_risk_level(51) == RiskLevelEnum.HIGH
    # 85 should be HIGH
    assert engine._determine_risk_level(85) == RiskLevelEnum.HIGH
    # 86 should be CRITICAL
    assert engine._determine_risk_level(86) == RiskLevelEnum.CRITICAL
    # 100 should be CRITICAL
    assert engine._determine_risk_level(100) == RiskLevelEnum.CRITICAL
