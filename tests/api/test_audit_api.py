from datetime import UTC, datetime

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.audit import AuditEvent, AuditEventType
from app.services.audit_service import AuditService


@pytest_asyncio.fixture
async def seed_audit_events(db: AsyncSession):
    audit_svc = AuditService(db)
    for i in range(5):
        event = AuditEvent(
            event_id=f"evt_api_{i}",
            event_type=AuditEventType.ACTION_EVALUATED,
            timestamp=datetime.now(UTC),
            correlation_id=f"corr_api_{i % 2}",
            action_id=f"act_api_{i}",
            final_decision="ALLOW" if i % 2 == 0 else "BLOCK",
        )
        await audit_svc.log_event(event)
    return True


@pytest.mark.asyncio
async def test_get_event(async_client: AsyncClient, seed_audit_events):
    response = await async_client.get("/api/v1/audit/events/evt_api_0")
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == "evt_api_0"
    assert data["final_decision"] == "ALLOW"


@pytest.mark.asyncio
async def test_get_event_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/v1/audit/events/evt_not_exist")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_action_history(async_client: AsyncClient, seed_audit_events):
    response = await async_client.get("/api/v1/audit/actions/act_api_1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["action_id"] == "act_api_1"


@pytest.mark.asyncio
async def test_list_events_with_pagination(
    async_client: AsyncClient, seed_audit_events
):
    response = await async_client.get("/api/v1/audit/events?limit=2&offset=0")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_events_with_filters(async_client: AsyncClient, seed_audit_events):
    response = await async_client.get("/api/v1/audit/events?decision=BLOCK")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2  # indices 1 and 3 are BLOCK
    for ev in data:
        assert ev["final_decision"] == "BLOCK"
