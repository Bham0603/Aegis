"""
Tests for approval domain models and lifecycle.
"""

import uuid
from datetime import UTC, datetime, timedelta

from app.domain.approval import ApprovalRequest, ApprovalStatus


def test_approval_status_terminal_states():
    """Test that terminal states are correctly identified."""
    assert ApprovalStatus.PENDING.is_terminal() is False
    assert ApprovalStatus.APPROVED.is_terminal() is True
    assert ApprovalStatus.DENIED.is_terminal() is True
    assert ApprovalStatus.EXPIRED.is_terminal() is True
    assert ApprovalStatus.CANCELLED.is_terminal() is True


def test_approval_request_is_expired():
    """Test expiration checking."""
    now = datetime.now(UTC)
    past = now - timedelta(seconds=10)
    future = now + timedelta(seconds=3600)

    approval = ApprovalRequest(
        approval_request_id="apr_test",
        action_id="act_123",
        action_fingerprint="abc123",
        correlation_id="cor_123",
        agent_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4()),
        environment="test",
        status=ApprovalStatus.PENDING,
        created_at=past,
        expires_at=future,
    )

    # Not expired yet
    assert approval.is_expired(now) is False

    # Expired
    approval_expired = ApprovalRequest(
        approval_request_id="apr_test2",
        action_id="act_124",
        action_fingerprint="abc124",
        correlation_id="cor_124",
        agent_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4()),
        environment="test",
        status=ApprovalStatus.PENDING,
        created_at=past,
        expires_at=past,
    )

    assert approval_expired.is_expired(now) is True


def test_approval_request_can_resolve_pending():
    """Test that PENDING approval can be resolved."""
    now = datetime.now(UTC)
    future = now + timedelta(seconds=3600)

    approval = ApprovalRequest(
        approval_request_id="apr_test",
        action_id="act_123",
        action_fingerprint="abc123",
        correlation_id="cor_123",
        agent_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4()),
        environment="test",
        status=ApprovalStatus.PENDING,
        created_at=now,
        expires_at=future,
    )

    can_resolve, error = approval.can_resolve(now)
    assert can_resolve is True
    assert error is None


def test_approval_request_cannot_resolve_terminal():
    """Test that terminal statuses cannot be resolved."""
    now = datetime.now(UTC)
    future = now + timedelta(seconds=3600)

    for terminal_status in [
        ApprovalStatus.APPROVED,
        ApprovalStatus.DENIED,
        ApprovalStatus.EXPIRED,
        ApprovalStatus.CANCELLED,
    ]:
        approval = ApprovalRequest(
            approval_request_id="apr_test",
            action_id="act_123",
            action_fingerprint="abc123",
            correlation_id="cor_123",
            agent_id=str(uuid.uuid4()),
            session_id=str(uuid.uuid4()),
            tool_id=str(uuid.uuid4()),
            environment="test",
            status=terminal_status,
            created_at=now,
            expires_at=future,
        )

        can_resolve, error = approval.can_resolve(now)
        assert can_resolve is False
        assert terminal_status.value in error


def test_approval_request_cannot_resolve_expired():
    """Test that expired approvals cannot be resolved."""
    now = datetime.now(UTC)
    past = now - timedelta(seconds=10)

    approval = ApprovalRequest(
        approval_request_id="apr_test",
        action_id="act_123",
        action_fingerprint="abc123",
        correlation_id="cor_123",
        agent_id=str(uuid.uuid4()),
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4()),
        environment="test",
        status=ApprovalStatus.PENDING,
        created_at=past,
        expires_at=past,
    )

    can_resolve, error = approval.can_resolve(now)
    assert can_resolve is False
    assert "expired" in error.lower()


def test_approval_request_validate_approver_prevents_self_approval():
    """
    SECURITY TEST: Agent cannot approve its own action.
    """
    agent_id = str(uuid.uuid4())

    approval = ApprovalRequest(
        approval_request_id="apr_test",
        action_id="act_123",
        action_fingerprint="abc123",
        correlation_id="cor_123",
        agent_id=agent_id,
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4()),
        environment="test",
        status=ApprovalStatus.PENDING,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(seconds=3600),
    )

    # Self-approval must be rejected
    is_valid, error = approval.validate_approver(agent_id)
    assert is_valid is False
    assert "self-approval" in error.lower()


def test_approval_request_validate_approver_allows_different_identity():
    """Test that different approver identity is allowed."""
    agent_id = str(uuid.uuid4())
    approver_id = str(uuid.uuid4())

    approval = ApprovalRequest(
        approval_request_id="apr_test",
        action_id="act_123",
        action_fingerprint="abc123",
        correlation_id="cor_123",
        agent_id=agent_id,
        session_id=str(uuid.uuid4()),
        tool_id=str(uuid.uuid4()),
        environment="test",
        status=ApprovalStatus.PENDING,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(seconds=3600),
    )

    # Different approver should be valid
    is_valid, error = approval.validate_approver(approver_id)
    assert is_valid is True
    assert error is None
