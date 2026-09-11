import asyncio
import uuid
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.action import Action
from app.domain.approval import ApprovalStatus
from app.models.approval import ApproverDB
from app.services.approval_service import ApprovalService


@pytest.fixture
def mock_action():
    return Action(
        action_id=f"act_{uuid.uuid4().hex[:8]}",
        correlation_id=f"cor_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(UTC),
        agent_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4()),
        operation="read",
        resource="/db/users",
        parameters={"limit": 10},
        environment="production",
        authorization_context={},
    )


@pytest_asyncio.fixture
async def test_approver_1(db: AsyncSession) -> ApproverDB:
    approver = ApproverDB(
        approver_id="approver_1",
        display_name="Test Approver 1",
        email="app1@example.com",
        is_active=True,
    )
    db.add(approver)
    await db.commit()
    await db.refresh(approver)
    return approver


@pytest_asyncio.fixture
async def test_approver_2(db: AsyncSession) -> ApproverDB:
    approver = ApproverDB(
        approver_id="approver_2",
        display_name="Test Approver 2",
        email="app2@example.com",
        is_active=True,
    )
    db.add(approver)
    await db.commit()
    await db.refresh(approver)
    return approver


@pytest_asyncio.fixture
async def pending_approval_request(db: AsyncSession, mock_action: Action):
    service = ApprovalService(db)
    from app.domain.decision import DecisionEnum, SecurityDecision

    temp_dec = SecurityDecision(
        action_id=mock_action.action_id,
        correlation_id=mock_action.correlation_id,
        timestamp=mock_action.timestamp,
        decision=DecisionEnum.REVIEW,
        risk_score=50,
        risk_level="MEDIUM",
    )
    # create request
    from app.domain.context import SecurityContext

    ctx = SecurityContext(action=mock_action)
    req = await service.create_request(mock_action, ctx, temp_dec)
    return req


@pytest.mark.asyncio
async def test_approval_resolution_concurrency(
    db: AsyncSession,
    pending_approval_request,
    test_approver_1: ApproverDB,
    test_approver_2: ApproverDB,
):
    """
    Test that resolving an approval request concurrently results in exactly one success.
    """
    from app.db.session import SessionLocal

    async with SessionLocal() as session1, SessionLocal() as session2:
        svc1 = ApprovalService(session1)
        svc2 = ApprovalService(session2)

        result1, result2 = await asyncio.gather(
            svc1.resolve(
                pending_approval_request.approval_request_id,
                test_approver_1.approver_id,
                ApprovalStatus.APPROVED,
                "Looks good 1",
            ),
            svc2.resolve(
                pending_approval_request.approval_request_id,
                test_approver_2.approver_id,
                ApprovalStatus.APPROVED,
                "Looks good 2",
            ),
            return_exceptions=True,
        )

        success_count = 0
        failure_count = 0

        for res in (result1, result2):
            if isinstance(res, Exception):
                failure_count += 1
            else:
                req, error = res
                if req and not error:
                    success_count += 1
                else:
                    failure_count += 1

        assert success_count == 1, "Exactly one approval should succeed"
        assert failure_count == 1, "Exactly one approval should fail or raise exception"
