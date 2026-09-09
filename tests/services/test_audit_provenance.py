"""
Phase 9 Audit Provenance Tests.

Verifies that ACTION_EVALUATED audit events preserve full decision provenance
using synthetic values — without recalculating anything inside AuditService.
"""

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit import AuditEvent, AuditEventType
from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_audit_provenance_full_pipeline(db: AsyncSession):
    """
    Verify that a realistic ACTION_EVALUATED event preserves all 7 provenance
    dimensions: Permission, Trust, Policy, Risk, Threat, Approval, Final Decision.
    """
    audit_svc = AuditService(db)

    event = AuditEvent(
        event_id="evt_prov_001",
        event_type=AuditEventType.ACTION_EVALUATED,
        timestamp=datetime.now(UTC),
        correlation_id="corr_prov_001",
        action_id="act_prov_001",
        agent_id="agt_001",
        user_id="usr_001",
        session_id="ses_001",
        tool_id="tool_001",
        operation="delete",
        resource="/db/production",
        environment="production",
        # All 7 provenance dimensions
        permission_result="GRANTED",
        trust_result="TRUSTED",
        policy_result="ALLOW",
        risk_score=85,
        risk_level="HIGH",
        threat_severity="MEDIUM",
        approval_result="REQUESTED",
        final_decision="REVIEW",
        decision_reasons=[
            "Matched Policy 'prod_delete' (Priority 100) -> ALLOW",
            "Risk Threshold: REVIEW required due to HIGH risk score (85).",
            "Threat Assessment: MEDIUM",
        ],
        redacted_parameters={"table": "users", "password": "[REDACTED]"},
    )

    await audit_svc.log_event(event)
    retrieved = await audit_svc.get_event("evt_prov_001")

    assert retrieved is not None
    assert retrieved.permission_result == "GRANTED"
    assert retrieved.trust_result == "TRUSTED"
    assert retrieved.policy_result == "ALLOW"
    assert retrieved.risk_score == 85
    assert retrieved.risk_level == "HIGH"
    assert retrieved.threat_severity == "MEDIUM"
    assert retrieved.approval_result == "REQUESTED"
    assert retrieved.final_decision == "REVIEW"
    assert len(retrieved.decision_reasons) == 3
    assert retrieved.redacted_parameters["password"] == "[REDACTED]"


@pytest.mark.asyncio
async def test_audit_provenance_block_scenario(db: AsyncSession):
    """Verify BLOCK provenance with permission denial."""
    audit_svc = AuditService(db)

    event = AuditEvent(
        event_id="evt_prov_block",
        event_type=AuditEventType.ACTION_EVALUATED,
        timestamp=datetime.now(UTC),
        correlation_id="corr_prov_block",
        action_id="act_prov_block",
        permission_result="DENIED",
        trust_result="UNKNOWN",
        policy_result="BLOCK",
        risk_score=95,
        risk_level="CRITICAL",
        threat_severity="CRITICAL",
        approval_result="NONE",
        final_decision="BLOCK",
        decision_reasons=["Permission DENIED: Agent lacks tool binding"],
    )
    await audit_svc.log_event(event)
    retrieved = await audit_svc.get_event("evt_prov_block")
    assert retrieved is not None
    assert retrieved.final_decision == "BLOCK"
    assert retrieved.permission_result == "DENIED"


@pytest.mark.asyncio
async def test_audit_provenance_allow_no_approval(db: AsyncSession):
    """Verify ALLOW provenance with no approval needed."""
    audit_svc = AuditService(db)

    event = AuditEvent(
        event_id="evt_prov_allow",
        event_type=AuditEventType.ACTION_EVALUATED,
        timestamp=datetime.now(UTC),
        correlation_id="corr_prov_allow",
        action_id="act_prov_allow",
        permission_result="GRANTED",
        trust_result="TRUSTED",
        policy_result="ALLOW",
        risk_score=15,
        risk_level="LOW",
        threat_severity=None,
        approval_result="NONE",
        final_decision="ALLOW",
    )
    await audit_svc.log_event(event)
    retrieved = await audit_svc.get_event("evt_prov_allow")
    assert retrieved is not None
    assert retrieved.final_decision == "ALLOW"
    assert retrieved.threat_severity is None
    assert retrieved.approval_result == "NONE"


@pytest.mark.asyncio
async def test_audit_historical_survives_entity_state(db: AsyncSession):
    """
    Verify audit records remain readable regardless of entity state.
    The audit record stores string IDs, not foreign key references,
    so disabled agents/users/tools do not affect historical records.
    """
    audit_svc = AuditService(db)

    event = AuditEvent(
        event_id="evt_hist_001",
        event_type=AuditEventType.ACTION_EVALUATED,
        timestamp=datetime.now(UTC),
        correlation_id="corr_hist_001",
        action_id="act_hist_001",
        agent_id="disabled_agent_id",
        user_id="disabled_user_id",
        tool_id="deleted_tool_id",
        session_id="expired_session_id",
        final_decision="ALLOW",
    )
    await audit_svc.log_event(event)

    # Retrieve should work regardless of entity existence
    retrieved = await audit_svc.get_event("evt_hist_001")
    assert retrieved is not None
    assert retrieved.agent_id == "disabled_agent_id"
    assert retrieved.user_id == "disabled_user_id"
    assert retrieved.tool_id == "deleted_tool_id"
    assert retrieved.session_id == "expired_session_id"


@pytest.mark.asyncio
async def test_audit_correlation_history_ordering(db: AsyncSession):
    """Verify correlation history returns events in deterministic timestamp order."""
    audit_svc = AuditService(db)

    # Create events with slightly different timestamps
    for i in range(4):
        event = AuditEvent(
            event_id=f"evt_corr_order_{i}",
            event_type=AuditEventType.ACTION_RECEIVED
            if i == 0
            else AuditEventType.ACTION_EVALUATED,
            timestamp=datetime(2026, 9, 8, 10, 0, i, tzinfo=UTC),
            correlation_id="corr_order_test",
            action_id=f"act_order_{i}",
        )
        await audit_svc.log_event(event)

    history = await audit_svc.get_correlation_history("corr_order_test")
    assert len(history) == 4
    # Verify ascending timestamp order
    for j in range(len(history) - 1):
        assert history[j].timestamp <= history[j + 1].timestamp
