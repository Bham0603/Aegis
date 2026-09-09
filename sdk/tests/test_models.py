"""Tests for SDK data models and enums."""


from aegis_sdk.models import (
    ActionRequest,
    ApprovalInfo,
    ApprovalStatus,
    AttackRunResult,
    AttackScenario,
    AuditEvent,
    Decision,
    EvaluationResult,
    RiskLevel,
    ThreatSeverity,
    ThreatType,
)


class TestDecisionEnum:
    def test_allow(self):
        assert Decision("ALLOW") == Decision.ALLOW

    def test_review(self):
        assert Decision("REVIEW") == Decision.REVIEW

    def test_block(self):
        assert Decision("BLOCK") == Decision.BLOCK

    def test_unknown_value_defaults_to_block(self):
        """Unknown decision values must not crash — fail safe to BLOCK."""
        result = Decision("UNKNOWN_FUTURE_DECISION")
        assert result == Decision.BLOCK


class TestRiskLevelEnum:
    def test_known_values(self):
        assert RiskLevel("LOW") == RiskLevel.LOW
        assert RiskLevel("CRITICAL") == RiskLevel.CRITICAL

    def test_unknown_defaults_to_critical(self):
        assert RiskLevel("EXTREME") == RiskLevel.CRITICAL


class TestThreatSeverityEnum:
    def test_known_values(self):
        assert ThreatSeverity("HIGH") == ThreatSeverity.HIGH

    def test_unknown_defaults_to_critical(self):
        assert ThreatSeverity("UNKNOWN_SEVERITY") == ThreatSeverity.CRITICAL


class TestThreatTypeEnum:
    def test_known_values(self):
        assert ThreatType("MALFORMED_ACTION") == ThreatType.MALFORMED_ACTION

    def test_unknown_defaults_safely(self):
        assert ThreatType("FUTURE_THREAT") == ThreatType.SUSPICIOUS_PAYLOAD


class TestApprovalStatusEnum:
    def test_known_values(self):
        assert ApprovalStatus("PENDING") == ApprovalStatus.PENDING
        assert ApprovalStatus("APPROVED") == ApprovalStatus.APPROVED

    def test_unknown_defaults_to_pending(self):
        assert ApprovalStatus("WEIRD") == ApprovalStatus.PENDING


class TestActionRequest:
    def test_minimal_request(self):
        req = ActionRequest(agent_id="agent-1", session_id="sess-1", tool_id="db")
        d = req.to_dict()
        assert d["agent_id"] == "agent-1"
        assert d["session_id"] == "sess-1"
        assert d["tool_id"] == "db"
        assert d["environment"] == "unknown"

    def test_full_request(self):
        req = ActionRequest(
            agent_id="agent-1",
            session_id="sess-1",
            tool_id="db",
            user_id="user-1",
            operation="delete",
            resource="users",
            parameters={"table": "users"},
            environment="production",
            authorization_context={"scope": "admin"},
        )
        d = req.to_dict()
        assert d["user_id"] == "user-1"
        assert d["operation"] == "delete"
        assert d["resource"] == "users"
        assert d["parameters"] == {"table": "users"}
        assert d["environment"] == "production"
        assert d["authorization_context"] == {"scope": "admin"}

    def test_none_fields_omitted(self):
        req = ActionRequest(agent_id="a", session_id="s", tool_id="t")
        d = req.to_dict()
        assert "user_id" not in d
        assert "operation" not in d
        assert "resource" not in d

    def test_repr(self):
        req = ActionRequest(agent_id="a", session_id="s", tool_id="t")
        assert "ActionRequest" in repr(req)
        assert "agent_id=" in repr(req)


class TestEvaluationResult:
    def test_allow_result(self):
        data = {
            "action_id": "act_1",
            "correlation_id": "corr_1",
            "timestamp": "2026-01-01T00:00:00Z",
            "decision": "ALLOW",
            "risk_score": 10,
            "risk_level": "LOW",
            "reasons": ["Allowed by policy"],
        }
        result = EvaluationResult(data)
        assert result.allowed is True
        assert result.blocked is False
        assert result.review_required is False
        assert result.decision == Decision.ALLOW

    def test_block_result(self):
        data = {
            "decision": "BLOCK",
            "reasons": ["Blocked by policy"],
            "risk_score": 95,
        }
        result = EvaluationResult(data)
        assert result.blocked is True
        assert result.allowed is False

    def test_review_result(self):
        data = {
            "decision": "REVIEW",
            "approval_required": True,
            "approval_request_id": "apr_1",
        }
        result = EvaluationResult(data)
        assert result.review_required is True
        assert result.approval_required is True
        assert result.approval_request_id == "apr_1"

    def test_unknown_decision_treated_as_block(self):
        data = {"decision": "FUTURE_DECISION"}
        result = EvaluationResult(data)
        assert result.blocked is True

    def test_missing_fields_have_defaults(self):
        result = EvaluationResult({})
        assert result.action_id == ""
        assert result.risk_score is None
        assert result.reasons == []
        assert result.threat_results == []
        assert result.blocked is True  # Default decision is BLOCK

    def test_risk_and_threat_fields(self):
        data = {
            "decision": "BLOCK",
            "risk_score": 85,
            "risk_level": "CRITICAL",
            "risk_explanation": "Very dangerous",
            "highest_threat_severity": "CRITICAL",
            "threat_results": [{"detector_id": "dop", "severity": "CRITICAL"}],
            "triggered_detectors": ["dop_v1"],
        }
        result = EvaluationResult(data)
        assert result.risk_score == 85
        assert result.risk_level == "CRITICAL"
        assert len(result.threat_results) == 1
        assert result.triggered_detectors == ["dop_v1"]

    def test_repr(self):
        result = EvaluationResult({"action_id": "act_1", "decision": "ALLOW"})
        assert "EvaluationResult" in repr(result)


class TestApprovalInfo:
    def test_pending_approval(self):
        data = {"status": "PENDING", "approval_request_id": "apr_1"}
        info = ApprovalInfo(data)
        assert info.is_pending is True
        assert info.is_approved is False
        assert info.is_denied is False

    def test_approved(self):
        data = {"status": "APPROVED", "approver_id": "human-1"}
        info = ApprovalInfo(data)
        assert info.is_approved is True

    def test_denied(self):
        data = {"status": "DENIED"}
        info = ApprovalInfo(data)
        assert info.is_denied is True


class TestAuditEvent:
    def test_basic_fields(self):
        data = {
            "event_id": "evt_1",
            "event_type": "ACTION_EVALUATED",
            "correlation_id": "corr_1",
            "final_decision": "ALLOW",
        }
        event = AuditEvent(data)
        assert event.event_id == "evt_1"
        assert event.event_type == "ACTION_EVALUATED"
        assert event.final_decision == "ALLOW"


class TestAttackScenario:
    def test_basic_fields(self):
        data = {
            "scenario_id": "sc_1",
            "name": "Prompt Injection",
            "category": "PROMPT_INJECTION",
        }
        sc = AttackScenario(data)
        assert sc.scenario_id == "sc_1"
        assert sc.name == "Prompt Injection"


class TestAttackRunResult:
    def test_passed_result(self):
        data = {"status": "PASS", "run_id": "run_1"}
        result = AttackRunResult(data)
        assert result.passed is True

    def test_failed_result(self):
        data = {"status": "FAIL", "run_id": "run_2"}
        result = AttackRunResult(data)
        assert result.passed is False
