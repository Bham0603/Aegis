import uuid
from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.action import Action
from app.domain.decision import DecisionEnum
from app.schemas.policy import PolicyCreate
from app.services.evaluator import evaluate_action
from app.services.policy_service import PolicyService


def make_action(
    tool_id: str, operation: str | None = None, environment: str = "development"
) -> Action:
    return Action(
        action_id="act_test",
        correlation_id="trace_test",
        timestamp=datetime.now(UTC),
        agent_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4())
        if tool_id == "some_tool"
        else tool_id,  # Or generate if needed, wait tool_id needs to be a UUID!
        operation=operation,
        environment=environment,
    )


@pytest.mark.asyncio
async def test_evaluate_action_default_deny(db: AsyncSession):
    action = make_action("web.search", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.BLOCK
    assert "Default Deny" in decision.reasons[0]


@pytest.mark.asyncio
async def test_evaluate_action_allows_matched_policy(db: AsyncSession):
    # Create an allow policy
    svc = PolicyService(db)
    await svc.create_policy(
        PolicyCreate(
            name="Allow Web Search",
            priority=10,
            rules=[{"effect": "ALLOW", "condition": {"tool_id": {"eq": "web.search"}}}],
        )
    )

    action = make_action("web.search", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.ALLOW
    assert "Matched Policy" in decision.reasons[0]
    assert decision.risk_score is not None
    assert decision.risk_level == "LOW"


@pytest.mark.asyncio
async def test_evaluate_action_fails_closed(monkeypatch, db: AsyncSession):
    def mock_evaluate(*args, **kwargs):
        raise ValueError("Simulated failure")

    import app.services.evaluator

    monkeypatch.setattr(app.services.evaluator.PolicyEngine, "evaluate", mock_evaluate)

    action = make_action("web.search", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.BLOCK
    assert "Fail-Closed" in decision.reasons[0]


@pytest.mark.asyncio
async def test_evaluate_action_risk_block(db: AsyncSession):
    # Create an allow policy
    svc = PolicyService(db)
    await svc.create_policy(
        PolicyCreate(
            name="Allow DB Delete",
            priority=10,
            rules=[{"effect": "ALLOW", "condition": {"tool_id": {"eq": "db_tool"}}}],
        )
    )

    # Delete in production triggers a CRITICAL risk score
    action = make_action("db_tool", "delete", "production")

    # We must ensure there's no trust result or block trust, actually missing trust results in UNTRUSTED (+25) or UNKNOWN (+20)
    # Delete (80) * Prod (1.5) = 120 (Clamped to 100) -> CRITICAL
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.BLOCK
    assert decision.risk_score == 100
    assert decision.risk_level == "CRITICAL"
    # The reason should mention risk threshold
    assert any(
        "Risk Threshold: BLOCKED due to CRITICAL risk score of 100" in reason
        for reason in decision.reasons
    )


@pytest.mark.asyncio
async def test_golden_scenario_a_permission_denied(monkeypatch, db: AsyncSession):
    import app.services.evaluator
    from app.domain.decision import PermissionResult, PermissionStatusEnum

    def mock_perm_eval(*args, **kwargs):
        return PermissionResult(
            status=PermissionStatusEnum.DENIED, reasons=["mock denied"]
        )

    monkeypatch.setattr(
        app.services.evaluator.PermissionEngine, "evaluate", mock_perm_eval
    )

    action = make_action("some_tool", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.BLOCK
    assert "Permission DENIED" in decision.reasons[0]


@pytest.mark.asyncio
async def test_golden_scenario_d_policy_block(monkeypatch, db: AsyncSession):
    import app.services.evaluator

    def mock_policy_eval(*args, **kwargs):
        return {
            "final_effect": "BLOCK",
            "matched_rules": [
                {"policy_name": "mock", "priority": 1, "effect": "BLOCK"}
            ],
            "default_deny": False,
        }

    monkeypatch.setattr(
        app.services.evaluator.PolicyEngine, "evaluate", mock_policy_eval
    )

    action = make_action("some_tool", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.BLOCK


@pytest.mark.asyncio
async def test_golden_scenario_e_trust_blocked(monkeypatch, db: AsyncSession):
    import app.services.evaluator
    from app.domain.decision import TrustClassEnum, TrustResult

    def mock_trust_eval(*args, **kwargs):
        return TrustResult(
            is_trusted=False,
            trust_class=TrustClassEnum.BLOCKED,
            reasons=["mock blocked"],
        )

    monkeypatch.setattr(app.services.evaluator.TrustEngine, "evaluate", mock_trust_eval)

    action = make_action("some_tool", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.BLOCK
    assert "Trust Engine BLOCKED" in decision.reasons[0]


@pytest.mark.asyncio
async def test_golden_scenario_b_allow(monkeypatch, db: AsyncSession):
    # Already basically tested by test_evaluate_action_allows_matched_policy, but let's mock explicitly
    import app.services.evaluator
    from app.domain.risk import RiskAssessment, RiskLevelEnum

    def mock_policy_eval(*args, **kwargs):
        return {"final_effect": "ALLOW", "matched_rules": [], "default_deny": False}

    def mock_risk_eval(*args, **kwargs):
        return RiskAssessment(
            risk_score=10,
            risk_level=RiskLevelEnum.LOW,
            explanation="low",
            factors=[],
            model_version="1.0",
        )

    import app.services.risk_engine

    monkeypatch.setattr(
        app.services.evaluator.PolicyEngine, "evaluate", mock_policy_eval
    )
    monkeypatch.setattr(app.services.risk_engine.RiskEngine, "assess", mock_risk_eval)

    action = make_action("some_tool", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.ALLOW


@pytest.mark.asyncio
async def test_golden_scenario_c_risk_review(monkeypatch, db: AsyncSession):
    import app.services.evaluator
    from app.domain.risk import RiskAssessment, RiskLevelEnum

    def mock_policy_eval(*args, **kwargs):
        return {"final_effect": "ALLOW", "matched_rules": [], "default_deny": False}

    def mock_risk_eval(*args, **kwargs):
        return RiskAssessment(
            risk_score=80,
            risk_level=RiskLevelEnum.HIGH,
            explanation="high",
            factors=[],
            model_version="1.0",
        )

    import app.services.risk_engine

    monkeypatch.setattr(
        app.services.evaluator.PolicyEngine, "evaluate", mock_policy_eval
    )
    monkeypatch.setattr(app.services.risk_engine.RiskEngine, "assess", mock_risk_eval)

    action = make_action("some_tool", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.REVIEW
    assert any(
        "REVIEW required due to HIGH risk score (80)" in r for r in decision.reasons
    )


@pytest.mark.asyncio
async def test_golden_scenario_f_threat_failure(monkeypatch, db: AsyncSession):
    import app.services.evaluator
    from app.domain.risk import RiskAssessment, RiskLevelEnum

    def mock_policy_eval(*args, **kwargs):
        return {"final_effect": "ALLOW", "matched_rules": [], "default_deny": False}

    def mock_risk_eval(*args, **kwargs):
        return RiskAssessment(
            risk_score=10,
            risk_level=RiskLevelEnum.LOW,
            explanation="low",
            factors=[],
            model_version="1.0",
        )

    import app.services.risk_engine
    import app.services.threat.engine
    from app.domain.threat import (
        ThreatAssessment,
        ThreatDetectionResult,
        ThreatSeverity,
        ThreatType,
    )

    def mock_threat_eval(*args, **kwargs):
        # Simulate a crash handled by ThreatEngine returning HIGH severity MALFORMED_ACTION
        return ThreatAssessment(
            overall_severity=ThreatSeverity.HIGH,
            findings=[
                ThreatDetectionResult(
                    detector_id="crashed_detector",
                    detector_version="1.0",
                    threat_type=ThreatType.MALFORMED_ACTION,
                    severity=ThreatSeverity.HIGH,
                    confidence="HIGH",
                    reason="Detector crashed",
                )
            ],
        )

    monkeypatch.setattr(
        app.services.evaluator.PolicyEngine, "evaluate", mock_policy_eval
    )
    monkeypatch.setattr(app.services.risk_engine.RiskEngine, "assess", mock_risk_eval)
    monkeypatch.setattr(
        app.services.threat.engine.ThreatEngine, "evaluate", mock_threat_eval
    )

    action = make_action("some_tool", "read")
    decision = await evaluate_action(action, db)

    # Threat HIGH escalates ALLOW to REVIEW
    assert decision.decision == DecisionEnum.REVIEW
    assert (
        "Threat Threshold: REVIEW required due to HIGH threat detection."
        in decision.reasons
    )


@pytest.mark.asyncio
async def test_golden_scenario_g_threat_escalation(monkeypatch, db: AsyncSession):
    import app.services.evaluator
    from app.domain.risk import RiskAssessment, RiskLevelEnum

    def mock_policy_eval(*args, **kwargs):
        return {"final_effect": "ALLOW", "matched_rules": [], "default_deny": False}

    def mock_risk_eval(*args, **kwargs):
        return RiskAssessment(
            risk_score=10,
            risk_level=RiskLevelEnum.LOW,
            explanation="low",
            factors=[],
            model_version="1.0",
        )

    import app.services.risk_engine
    import app.services.threat.engine
    from app.domain.threat import (
        ThreatAssessment,
        ThreatDetectionResult,
        ThreatSeverity,
        ThreatType,
    )

    def mock_threat_eval(*args, **kwargs):
        return ThreatAssessment(
            overall_severity=ThreatSeverity.CRITICAL,
            findings=[
                ThreatDetectionResult(
                    detector_id="critical_detector",
                    detector_version="1.0",
                    threat_type=ThreatType.DANGEROUS_OPERATION_PATTERN,
                    severity=ThreatSeverity.CRITICAL,
                    confidence="HIGH",
                    reason="Critical threat",
                )
            ],
        )

    monkeypatch.setattr(
        app.services.evaluator.PolicyEngine, "evaluate", mock_policy_eval
    )
    monkeypatch.setattr(app.services.risk_engine.RiskEngine, "assess", mock_risk_eval)
    monkeypatch.setattr(
        app.services.threat.engine.ThreatEngine, "evaluate", mock_threat_eval
    )

    action = make_action("some_tool", "read")
    decision = await evaluate_action(action, db)

    # Threat CRITICAL escalates ALLOW to BLOCK
    assert decision.decision == DecisionEnum.BLOCK
    assert (
        "Threat Threshold: BLOCKED due to CRITICAL threat detection."
        in decision.reasons
    )
