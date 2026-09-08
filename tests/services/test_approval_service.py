"""
Tests for ApprovalService.
"""

import uuid
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.base import Base
from app.domain.action import Action
from app.domain.approval import ApprovalStatus
from app.domain.context import SecurityContext
from app.domain.decision import SecurityDecision
from app.models.approval import ApproverDB
from app.services.approval_service import ApprovalService


@pytest_asyncio.fixture
async def test_db():
    """Create a test database session."""
    from app.db.session import engine

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session_factory() as session:
        yield session

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def approver(test_db: AsyncSession):
    """Create a test approver."""
    approver = ApproverDB(
        approver_id="test_approver",
        display_name="Test Approver",
        email="test@example.com",
        is_active=True,
    )
    test_db.add(approver)
    await test_db.commit()
    await test_db.refresh(approver)
    return approver


@pytest_asyncio.fixture
def mock_action():
    """Create a mock action for testing."""
    return Action(
        action_id=f"act_{uuid.uuid4().hex[:8]}",
        correlation_id=f"cor_{uuid.uuid4().hex[:8]}",
        timestamp=datetime.now(UTC),
        agent_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4()),
        operation="read",
        resource="/db/users",
        environment="production",
        parameters={"limit": 10},
    )


@pytest_asyncio.fixture
def mock_security_decision(mock_action: Action):
    """Create a mock security decision."""
    return SecurityDecision(
        action_id=mock_action.action_id,
        correlation_id=mock_action.correlation_id,
        timestamp=mock_action.timestamp,
        decision="REVIEW",
        reasons=["High risk score"],
        approval_required=True,
    )


@pytest_asyncio.fixture
def mock_security_context(mock_action: Action):
    """Create a mock security context."""
    return SecurityContext(action=mock_action)


@pytest_asyncio.fixture
async def approval_service(test_db: AsyncSession):
    """Create an ApprovalService instance."""
    return ApprovalService(test_db)


@pytest.mark.asyncio
async def test_create_request(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
):
    """Test creating an approval request."""
    approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
        ttl_seconds=300,
    )

    assert approval is not None
    assert approval.approval_request_id.startswith("apr_")
    assert approval.action_id == mock_action.action_id
    assert approval.status == ApprovalStatus.PENDING
    assert approval.action_fingerprint is not None
    assert len(approval.action_fingerprint) == 64  # SHA-256 hex
    assert approval.expires_at > approval.created_at


@pytest.mark.asyncio
async def test_get_request(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
):
    """Test retrieving an approval request."""
    # Create a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    # Retrieve it
    retrieved_approval = await approval_service.get_request(
        created_approval.approval_request_id
    )

    assert retrieved_approval is not None
    assert retrieved_approval.approval_request_id == created_approval.approval_request_id
    assert retrieved_approval.action_id == created_approval.action_id
    assert retrieved_approval.action_fingerprint == created_approval.action_fingerprint


@pytest.mark.asyncio
async def test_get_request_not_found(
    approval_service: ApprovalService,
):
    """Test retrieving non-existent approval request."""
    approval = await approval_service.get_request("nonexistent")
    assert approval is None


@pytest.mark.asyncio
async def test_resolve_approve_success(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
    approver: ApproverDB,
):
    """Test successfully approving an approval request."""
    # Create a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    # Resolve as APPROVED
    resolved_approval, error = await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=approver.approver_id,
        decision=ApprovalStatus.APPROVED,
        comment="Looks good",
    )

    assert resolved_approval is not None
    assert error is None
    assert resolved_approval.status == ApprovalStatus.APPROVED
    assert resolved_approval.approver_id == approver.approver_id
    assert resolved_approval.resolved_at is not None
    assert resolved_approval.resolution_comment == "Looks good"


@pytest.mark.asyncio
async def test_resolve_deny_success(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
    approver: ApproverDB,
):
    """Test successfully denying an approval request."""
    # Create a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    # Resolve as DENIED
    resolved_approval, error = await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=approver.approver_id,
        decision=ApprovalStatus.DENIED,
        comment="Too risky",
    )

    assert resolved_approval is not None
    assert error is None
    assert resolved_approval.status == ApprovalStatus.DENIED
    assert resolved_approval.approver_id == approver.approver_id
    assert resolved_approval.resolved_at is not None
    assert resolved_approval.resolution_comment == "Too risky"


@pytest.mark.asyncio
async def test_resolve_prevents_self_approval(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
):
    """
    SECURITY TEST: Agent cannot approve its own action.
    """
    # Create a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    # Try to approve as the agent itself (self-approval)
    resolved_approval, error = await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=mock_action.agent_id,  # Same as agent_id - should be rejected
        decision=ApprovalStatus.APPROVED,
    )

    assert resolved_approval is None
    assert error is not None
    assert "self-approval" in error.lower() or "agent cannot approve" in error.lower()


@pytest.mark.asyncio
async def test_resolve_rejects_inactive_approver(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
    test_db: AsyncSession,
):
    """Test that inactive approvers cannot resolve approvals."""
    # Create an inactive approver
    inactive_approver = ApproverDB(
        approver_id="inactive_approver",
        display_name="Inactive Approver",
        email="inactive@example.com",
        is_active=False,
    )
    test_db.add(inactive_approver)
    await test_db.commit()

    # Create a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    # Try to resolve with inactive approver
    resolved_approval, error = await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=inactive_approver.approver_id,
        decision=ApprovalStatus.APPROVED,
    )

    assert resolved_approval is None
    assert error is not None
    assert "not active" in error.lower()


@pytest.mark.asyncio
async def test_resolve_rejects_nonexistent_approver(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
):
    """Test that nonexistent approvers cannot resolve approvals."""
    # Create a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    # Try to resolve with nonexistent approver
    resolved_approval, error = await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id="nonexistent_approver",
        decision=ApprovalStatus.APPROVED,
    )

    assert resolved_approval is None
    assert error is not None
    assert "not found" in error.lower()


@pytest.mark.asyncio
async def test_resolve_rejects_already_resolved(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
    approver: ApproverDB,
):
    """Test that resolved approvals cannot be resolved again."""
    # Create and approve a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    resolved_approval, error = await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=approver.approver_id,
        decision=ApprovalStatus.APPROVED,
    )

    assert resolved_approval is not None
    assert error is None

    # Try to resolve again
    resolved_approval2, error2 = await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=approver.approver_id,
        decision=ApprovalStatus.APPROVED,
    )

    assert resolved_approval2 is None
    assert error2 is not None
    assert "terminal state" in error2.lower() or "already" in error2.lower()


@pytest.mark.asyncio
async def test_verify_approval_valid(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
    approver: ApproverDB,
):
    """Test verifying a valid approval."""
    # Create and approve a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=approver.approver_id,
        decision=ApprovalStatus.APPROVED,
    )

    # Verify approval
    is_valid, reason = await approval_service.verify_approval(
        action=mock_action,
        approval_request_id=created_approval.approval_request_id,
    )

    assert is_valid is True
    assert reason == "Approval valid"


@pytest.mark.asyncio
async def test_verify_approval_fingerprint_mismatch(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
    approver: ApproverDB,
):
    """
    SECURITY TEST: Verification must fail if action fingerprint doesn't match.
    """
    # Create and approve a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=approver.approver_id,
        decision=ApprovalStatus.APPROVED,
    )

    # Modify the action after approval
    modified_action = Action(
        action_id=mock_action.action_id,
        correlation_id=mock_action.correlation_id,
        timestamp=mock_action.timestamp,
        agent_id=mock_action.agent_id,
        session_id=mock_action.session_id,
        tool_id=mock_action.tool_id,
        operation="write",  # Different operation!
        resource=mock_action.resource,
        environment=mock_action.environment,
        parameters=mock_action.parameters,
    )

    # Verification must fail due to fingerprint mismatch
    is_valid, reason = await approval_service.verify_approval(
        action=modified_action,
        approval_request_id=created_approval.approval_request_id,
    )

    assert is_valid is False
    assert "fingerprint" in reason.lower() or "modified" in reason.lower()


@pytest.mark.asyncio
async def test_verify_approval_denied(
    approval_service: ApprovalService,
    mock_action: Action,
    mock_security_context: SecurityContext,
    mock_security_decision: SecurityDecision,
    approver: ApproverDB,
):
    """Test that denied approvals are not valid."""
    # Create and deny a request
    created_approval = await approval_service.create_request(
        action=mock_action,
        security_context=mock_security_context,
        security_decision=mock_security_decision,
    )

    await approval_service.resolve(
        approval_request_id=created_approval.approval_request_id,
        approver_id=approver.approver_id,
        decision=ApprovalStatus.DENIED,
    )

    # Denied approvals should not verify as valid
    is_valid, reason = await approval_service.verify_approval(
        action=mock_action,
        approval_request_id=created_approval.approval_request_id,
    )

    assert is_valid is False
    assert "not in APPROVED state" in reason


@pytest.mark.asyncio
async def test_create_approver(
    approval_service: ApprovalService,
    test_db: AsyncSession,
):
    """Test creating an approver."""
    from sqlalchemy import text

    approver = await approval_service.create_approver(
        approver_id="new_approver",
        display_name="New Approver",
        email="new@example.com",
    )

    assert approver is not None
    assert approver.approver_id == "new_approver"
    assert approver.display_name == "New Approver"
    assert approver.email == "new@example.com"
    assert approver.is_active is True

    # Verify it was persisted
    stmt = text("SELECT * FROM approver WHERE approver_id = 'new_approver'")
    result = await test_db.execute(stmt)
    record = result.fetchone()
    assert record is not None
    assert record.approver_id == "new_approver"
