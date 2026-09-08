"""
API tests for approval endpoints.
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest
import pytest_asyncio

from app.domain.action import Action
from app.models.approval import ApprovalRequestDB, ApprovalStatusDB, ApproverDB
from app.services.fingerprint import generate_action_fingerprint


@pytest_asyncio.fixture
async def test_approver(db):
    """Create a test approver for API tests."""
    approver = ApproverDB(
        approver_id="test_approver_api",
        display_name="API Test Approver",
        email="api_test@example.com",
        is_active=True,
    )
    db.add(approver)
    await db.commit()
    await db.refresh(approver)
    return approver


@pytest_asyncio.fixture
def mock_action():
    """Create a mock action for API tests."""
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
async def test_approval_request(db, mock_action):
    """Create a test approval request for API tests."""
    approval_request = ApprovalRequestDB(
        approval_request_id="apr_test123",
        action_id=mock_action.action_id,
        action_fingerprint=generate_action_fingerprint(mock_action),
        correlation_id=mock_action.correlation_id,
        agent_id=uuid.UUID(mock_action.agent_id),
        session_id=uuid.UUID(mock_action.session_id),
        tool_id=uuid.UUID(mock_action.tool_id),
        operation=mock_action.operation,
        resource=mock_action.resource,
        environment=mock_action.environment,
        status=ApprovalStatusDB.PENDING,
        created_at=datetime.now(UTC),
        expires_at=datetime.now(UTC) + timedelta(hours=1),  # Far future
        risk_score=85,
        risk_level="HIGH",
        highest_threat_severity="MEDIUM",
        reasons={"reasons": ["High risk score"]},
    )
    db.add(approval_request)
    await db.commit()
    await db.refresh(approval_request)

    return approval_request


@pytest.mark.asyncio
async def test_get_approval_request_success(
    async_client,
    test_approval_request,
):
    """Test GET /approvals/{id} with valid approval request."""
    response = await async_client.get(
        f"/api/v1/approvals/{test_approval_request.approval_request_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["approval_request_id"] == test_approval_request.approval_request_id
    assert data["action_id"] == test_approval_request.action_id
    assert data["status"] == "PENDING"


@pytest.mark.asyncio
async def test_get_approval_request_not_found(
    async_client,
):
    """Test GET /approvals/{id} with nonexistent approval request."""
    response = await async_client.get("/api/v1/approvals/nonexistent")

    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_approve_approval_request_success(
    async_client,
    test_approval_request,
    test_approver,
):
    """Test POST /approvals/{id}/approve with valid data."""
    payload = {
        "approver_id": test_approver.approver_id,
        "decision": "APPROVED",
        "comment": "Looks safe to me",
    }

    response = await async_client.post(
        f"/api/v1/approvals/{test_approval_request.approval_request_id}/approve",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["approval_request_id"] == test_approval_request.approval_request_id
    assert data["status"] == "APPROVED"
    assert data["approver_id"] == test_approver.approver_id
    assert data["resolution_comment"] == "Looks safe to me"


@pytest.mark.asyncio
async def test_approve_approval_request_wrong_decision_endpoint(
    async_client,
    test_approval_request,
    test_approver,
):
    """
    Test POST /approvals/{id}/approve with DENIED decision.
    Should be rejected because /approve endpoint only accepts APPROVED.
    """
    payload = {
        "approver_id": test_approver.approver_id,
        "decision": "DENIED",  # Wrong endpoint for DENIED
        "comment": "Should be rejected",
    }

    response = await async_client.post(
        f"/api/v1/approvals/{test_approval_request.approval_request_id}/approve",
        json=payload,
    )

    assert response.status_code == 400
    data = response.json()
    assert "only accepts APPROVED" in data["detail"]


@pytest.mark.asyncio
async def test_deny_approval_request_success(
    async_client,
    test_approval_request,
    test_approver,
):
    """Test POST /approvals/{id}/deny with valid data."""
    payload = {
        "approver_id": test_approver.approver_id,
        "decision": "DENIED",
        "comment": "Too risky",
    }

    response = await async_client.post(
        f"/api/v1/approvals/{test_approval_request.approval_request_id}/deny",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["approval_request_id"] == test_approval_request.approval_request_id
    assert data["status"] == "DENIED"
    assert data["approver_id"] == test_approver.approver_id
    assert data["resolution_comment"] == "Too risky"


@pytest.mark.asyncio
async def test_deny_approval_request_wrong_decision_endpoint(
    async_client,
    test_approval_request,
    test_approver,
):
    """
    Test POST /approvals/{id}/deny with APPROVED decision.
    Should be rejected because /deny endpoint only accepts DENIED.
    """
    payload = {
        "approver_id": test_approver.approver_id,
        "decision": "APPROVED",  # Wrong endpoint for APPROVED
        "comment": "Should be rejected",
    }

    response = await async_client.post(
        f"/api/v1/approvals/{test_approval_request.approval_request_id}/deny",
        json=payload,
    )

    assert response.status_code == 400
    data = response.json()
    assert "only accepts DENIED" in data["detail"]


@pytest.mark.asyncio
async def test_approve_approval_request_self_approval_prevented(
    async_client,
    test_approval_request,
    mock_action,
):
    """
    SECURITY TEST: Agent cannot approve its own action.
    """
    payload = {
        "approver_id": mock_action.agent_id,  # Same as agent ID - self-approval
        "decision": "APPROVED",
        "comment": "Should be rejected",
    }

    response = await async_client.post(
        f"/api/v1/approvals/{test_approval_request.approval_request_id}/approve",
        json=payload,
    )

    # Should fail due to self-approval prevention
    assert response.status_code == 400
    data = response.json()
    detail = data["detail"].lower()
    assert any(
        keyword in detail
        for keyword in ["self-approval", "agent cannot approve", "forbidden"]
    )


@pytest.mark.asyncio
async def test_approve_approval_request_nonexistent_approver(
    async_client,
    test_approval_request,
):
    """Test approval with nonexistent approver."""
    payload = {
        "approver_id": "nonexistent_approver",
        "decision": "APPROVED",
        "comment": "Should be rejected",
    }

    response = await async_client.post(
        f"/api/v1/approvals/{test_approval_request.approval_request_id}/approve",
        json=payload,
    )

    assert response.status_code == 400
    data = response.json()
    assert "not found" in data["detail"].lower()


@pytest.mark.asyncio
async def test_create_approver_success(
    async_client,
):
    """Test POST /approvers to create a new approver."""
    payload = {
        "approver_id": "api_created_approver",
        "display_name": "API Created Approver",
        "email": "api@example.com",
    }

    response = await async_client.post("/api/v1/approvers", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["approver_id"] == "api_created_approver"
    assert data["display_name"] == "API Created Approver"
    assert data["email"] == "api@example.com"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_approver_duplicate(
    async_client,
    test_approver,
):
    """Test creating duplicate approver should fail."""
    payload = {
        "approver_id": test_approver.approver_id,  # Already exists
        "display_name": "Duplicate Approver",
        "email": "duplicate@example.com",
    }

    response = await async_client.post("/api/v1/approvers", json=payload)

    # Should fail due to unique constraint violation
    assert response.status_code == 400
    data = response.json()
    assert "failed" in data["detail"].lower() or "error" in data["detail"].lower()


@pytest.mark.asyncio
async def test_approve_expired_request(
    async_client,
    db,
    mock_action,
    test_approver,
):
    """Test that expired approval requests cannot be approved."""
    # Create an already-expired approval request
    past_time = datetime.now(UTC) - timedelta(hours=1)

    expired_request = ApprovalRequestDB(
        approval_request_id="apr_expired",
        action_id=mock_action.action_id,
        action_fingerprint=generate_action_fingerprint(mock_action),
        correlation_id=mock_action.correlation_id,
        agent_id=uuid.UUID(mock_action.agent_id),
        session_id=uuid.UUID(mock_action.session_id),
        tool_id=uuid.UUID(mock_action.tool_id),
        operation=mock_action.operation,
        resource=mock_action.resource,
        environment=mock_action.environment,
        status=ApprovalStatusDB.PENDING,
        created_at=past_time,
        expires_at=past_time,  # Already expired
        risk_score=85,
        risk_level="HIGH",
    )
    db.add(expired_request)
    await db.commit()

    payload = {
        "approver_id": test_approver.approver_id,
        "decision": "APPROVED",
        "comment": "Should be rejected",
    }

    response = await async_client.post(
        f"/api/v1/approvals/{expired_request.approval_request_id}/approve",
        json=payload,
    )

    assert response.status_code == 400
    data = response.json()
    assert "expired" in data["detail"].lower()
