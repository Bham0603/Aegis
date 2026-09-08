"""
Tests for action fingerprinting service.
"""

from app.domain.action import Action
from app.services.fingerprint import (
    generate_action_fingerprint,
    verify_action_fingerprint,
)


def test_generate_action_fingerprint_deterministic():
    """Test that the same action produces the same fingerprint."""
    action = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
        parameters={"limit": 10, "offset": 0},
    )

    fingerprint1 = generate_action_fingerprint(action)
    fingerprint2 = generate_action_fingerprint(action)

    assert fingerprint1 == fingerprint2
    assert len(fingerprint1) == 64  # SHA-256 hex


def test_generate_action_fingerprint_different_for_different_actions():
    """Test that different actions produce different fingerprints."""
    action1 = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
        parameters={"limit": 10},
    )

    action2 = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="write",  # Different operation
        resource="/db/users",
        environment="production",
        parameters={"limit": 10},
    )

    fingerprint1 = generate_action_fingerprint(action1)
    fingerprint2 = generate_action_fingerprint(action2)

    assert fingerprint1 != fingerprint2


def test_generate_action_fingerprint_ignores_timestamp():
    """Test that timestamp does not affect fingerprint (observability only)."""
    action1 = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
    )

    action2 = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T10:00:00Z",  # Different timestamp
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
    )

    fingerprint1 = generate_action_fingerprint(action1)
    fingerprint2 = generate_action_fingerprint(action2)

    # Timestamps should not affect fingerprint
    assert fingerprint1 == fingerprint2


def test_generate_action_fingerprint_ignores_correlation_id():
    """Test that correlation_id does not affect fingerprint (observability only)."""
    action1 = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
    )

    action2 = Action(
        action_id="act_123",
        correlation_id="cor_999",  # Different correlation_id
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
    )

    fingerprint1 = generate_action_fingerprint(action1)
    fingerprint2 = generate_action_fingerprint(action2)

    # Correlation IDs should not affect fingerprint
    assert fingerprint1 == fingerprint2


def test_generate_action_fingerprint_includes_parameters():
    """Test that parameters affect fingerprint."""
    action1 = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
        parameters={"limit": 10},
    )

    action2 = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
        parameters={"limit": 100},  # Different parameter
    )

    fingerprint1 = generate_action_fingerprint(action1)
    fingerprint2 = generate_action_fingerprint(action2)

    assert fingerprint1 != fingerprint2


def test_generate_action_fingerprint_redacts_sensitive_parameters():
    """Test that sensitive parameters are redacted before fingerprinting."""
    action_with_password = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="authenticate",
        resource="/auth",
        environment="production",
        parameters={"username": "admin", "password": "secret123"},
    )

    fingerprint = generate_action_fingerprint(action_with_password)

    # Should produce a valid fingerprint
    assert len(fingerprint) == 64

    # Changing the password should change the fingerprint (hashed value differs)
    action_different_password = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="authenticate",
        resource="/auth",
        environment="production",
        parameters={"username": "admin", "password": "different_secret"},
    )

    fingerprint2 = generate_action_fingerprint(action_different_password)

    # Fingerprints should differ (different password hashes)
    assert fingerprint != fingerprint2


def test_verify_action_fingerprint_success():
    """Test successful fingerprint verification."""
    action = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
    )

    fingerprint = generate_action_fingerprint(action)
    is_valid = verify_action_fingerprint(action, fingerprint)

    assert is_valid is True


def test_verify_action_fingerprint_fails_on_modification():
    """
    SECURITY TEST: Fingerprint verification must fail if action is modified.
    """
    action = Action(
        action_id="act_123",
        correlation_id="cor_123",
        timestamp="2026-09-08T00:00:00Z",
        agent_id="agent_1",
        session_id="sess_1",
        tool_id="tool_1",
        operation="read",
        resource="/db/users",
        environment="production",
    )

    fingerprint = generate_action_fingerprint(action)

    # Modify the action after fingerprinting
    action.operation = "write"

    is_valid = verify_action_fingerprint(action, fingerprint)

    # Verification must fail
    assert is_valid is False
