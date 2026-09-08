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
async def test_approver(db: AsyncSession) -> ApproverDB:
    approver = ApproverDB(
        approver_id="security_approver",
        display_name="Security Approver",
        email="sec@example.com",
        is_active=True,
    )
    db.add(approver)
    await db.commit()
    await db.refresh(approver)
    return approver


@pytest.mark.asyncio
async def test_approval_self_approval_prevented(db: AsyncSession, mock_action: Action):
    service = ApprovalService(db)
    from app.domain.context import SecurityContext
    from app.domain.decision import DecisionEnum, SecurityDecision

    temp_dec = SecurityDecision(
        action_id=mock_action.action_id,
        correlation_id=mock_action.correlation_id,
        timestamp=mock_action.timestamp,
        decision=DecisionEnum.REVIEW,
    )
    req = await service.create_request(mock_action, SecurityContext(action=mock_action), temp_dec)
    
    # Try to approve using the agent's ID
    resolved, error = await service.resolve(
        req.approval_request_id,
        mock_action.agent_id, # Self approval
        ApprovalStatus.APPROVED,
    )
    
    assert resolved is None
    assert error == "Self-approval is forbidden: agent cannot approve its own action"


@pytest.mark.asyncio
async def test_approval_fingerprint_mismatch(db: AsyncSession, mock_action: Action, test_approver: ApproverDB):
    service = ApprovalService(db)
    from app.domain.context import SecurityContext
    from app.domain.decision import DecisionEnum, SecurityDecision

    temp_dec = SecurityDecision(
        action_id=mock_action.action_id,
        correlation_id=mock_action.correlation_id,
        timestamp=mock_action.timestamp,
        decision=DecisionEnum.REVIEW,
    )
    req = await service.create_request(mock_action, SecurityContext(action=mock_action), temp_dec)
    
    # Approve it
    resolved, error = await service.resolve(
        req.approval_request_id,
        test_approver.approver_id,
        ApprovalStatus.APPROVED,
    )
    assert resolved is not None
    assert error is None
    
    # Mutate the action
    mutated_action = mock_action.model_copy()
    mutated_action.resource = "/db/secrets"
    
    # Verify should fail
    is_valid, reason = await service.verify_approval(mutated_action, req.approval_request_id)
    assert is_valid is False
    assert "fingerprint mismatch" in reason.lower()


@pytest.mark.asyncio
async def test_approval_expiration(db: AsyncSession, mock_action: Action, test_approver: ApproverDB):
    service = ApprovalService(db)
    from app.domain.context import SecurityContext
    from app.domain.decision import DecisionEnum, SecurityDecision

    temp_dec = SecurityDecision(
        action_id=mock_action.action_id,
        correlation_id=mock_action.correlation_id,
        timestamp=mock_action.timestamp,
        decision=DecisionEnum.REVIEW,
    )
    # Create with very short TTL
    req = await service.create_request(mock_action, SecurityContext(action=mock_action), temp_dec, ttl_seconds=-1)
    
    # Verify resolve should fail because it's expired
    resolved, error = await service.resolve(
        req.approval_request_id,
        test_approver.approver_id,
        ApprovalStatus.APPROVED,
    )
    assert resolved is None
    assert "expired" in error.lower()
