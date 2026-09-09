from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit import AuditEvent, AuditEventType
from app.services.audit_service import AuditService


@pytest.mark.asyncio
async def test_audit_event_persistence(db: AsyncSession):
    audit_svc = AuditService(db)

    event = AuditEvent(
        event_id="evt_test_123",
        event_type=AuditEventType.ACTION_EVALUATED,
        timestamp=datetime.now(UTC),
        correlation_id="corr_test_123",
        action_id="act_test_123",
        final_decision="ALLOW",
        redacted_parameters={"safe": "data"},
    )

    await audit_svc.log_event(event)

    # Retrieve
    retrieved = await audit_svc.get_event("evt_test_123")
    assert retrieved is not None
    assert retrieved.event_id == "evt_test_123"
    assert retrieved.final_decision == "ALLOW"
    assert retrieved.redacted_parameters == {"safe": "data"}


@pytest.mark.asyncio
async def test_audit_action_history(db: AsyncSession):
    audit_svc = AuditService(db)

    for i in range(3):
        event = AuditEvent(
            event_id=f"evt_history_{i}",
            event_type=AuditEventType.ACTION_RECEIVED
            if i == 0
            else AuditEventType.ACTION_EVALUATED,
            timestamp=datetime.now(UTC),
            correlation_id="corr_hist",
            action_id="act_hist",
        )
        await audit_svc.log_event(event)

    history = await audit_svc.get_action_history("act_hist")
    assert len(history) == 3
    assert history[0].event_type == AuditEventType.ACTION_RECEIVED


@pytest.mark.asyncio
async def test_audit_persistence_failure_safe(db: AsyncSession):
    """
    Test that an exception during log_event is caught and logged, not raised.
    """
    audit_svc = AuditService(db)

    # Intentionally cause a failure by inserting a duplicate primary key
    event = AuditEvent(
        event_id="evt_dup",
        event_type=AuditEventType.ACTION_RECEIVED,
        timestamp=datetime.now(UTC),
        correlation_id="corr_dup",
    )
    await audit_svc.log_event(event)

    # Try inserting exactly the same event_id again
    # It should not raise an exception
    await audit_svc.log_event(event)
