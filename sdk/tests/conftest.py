"""Shared test fixtures for Aegis SDK tests."""

from __future__ import annotations

import pytest
import respx

from aegis_sdk.client import AegisClient


@pytest.fixture
def mock_api():
    """Provide a respx router for mocking Aegis backend HTTP calls."""
    with respx.mock(assert_all_called=False, assert_all_mocked=True) as router:
        yield router


@pytest.fixture
def client():
    """Provide an AegisClient with a test API key."""
    return AegisClient(
        base_url="http://test-aegis:8000",
        api_key="test-api-key-12345",
        timeout=5.0,
        max_retries=0,
    )


@pytest.fixture
def client_with_retries():
    """Provide an AegisClient with retries enabled."""
    return AegisClient(
        base_url="http://test-aegis:8000",
        api_key="test-api-key-12345",
        timeout=5.0,
        max_retries=2,
    )


# -- Sample backend response payloads --

ALLOW_RESPONSE = {
    "action_id": "act_123",
    "correlation_id": "corr_456",
    "timestamp": "2026-01-01T00:00:00Z",
    "decision": "ALLOW",
    "risk_score": 15,
    "risk_level": "LOW",
    "risk_explanation": "Low-risk action",
    "risk_factors": [],
    "reasons": ["Policy allows read operations"],
    "violated_policies": [],
    "triggered_detectors": [],
    "highest_threat_severity": None,
    "threat_results": [],
    "approval_required": False,
    "approval_request_id": None,
}

BLOCK_RESPONSE = {
    "action_id": "act_789",
    "correlation_id": "corr_012",
    "timestamp": "2026-01-01T00:00:00Z",
    "decision": "BLOCK",
    "risk_score": 95,
    "risk_level": "CRITICAL",
    "risk_explanation": "Destructive operation",
    "risk_factors": [{"name": "operation_sensitivity", "contribution": 50, "category": "OPERATION_SENSITIVITY", "reason": "Destructive op"}],
    "reasons": ["Operation blocked by policy", "High risk score"],
    "violated_policies": ["no-delete-prod"],
    "triggered_detectors": ["dangerous_operation_pattern"],
    "highest_threat_severity": "CRITICAL",
    "threat_results": [{"detector_id": "dop_v1", "severity": "CRITICAL"}],
    "approval_required": False,
    "approval_request_id": None,
}

REVIEW_RESPONSE = {
    "action_id": "act_555",
    "correlation_id": "corr_666",
    "timestamp": "2026-01-01T00:00:00Z",
    "decision": "REVIEW",
    "risk_score": 60,
    "risk_level": "HIGH",
    "risk_explanation": "Elevated risk requires human review",
    "risk_factors": [],
    "reasons": ["Risk score exceeds review threshold"],
    "violated_policies": [],
    "triggered_detectors": [],
    "highest_threat_severity": None,
    "threat_results": [],
    "approval_required": True,
    "approval_request_id": "apr_999",
}

APPROVAL_RESPONSE = {
    "approval_request_id": "apr_999",
    "action_id": "act_555",
    "correlation_id": "corr_666",
    "agent_id": "test-agent",
    "user_id": None,
    "session_id": "sess_1",
    "tool_id": "database",
    "operation": "delete",
    "resource": "users",
    "environment": "production",
    "status": "PENDING",
    "required_approver_role": None,
    "approver_id": None,
    "created_at": "2026-01-01T00:00:00Z",
    "expires_at": "2026-01-01T01:00:00Z",
    "resolved_at": None,
    "risk_score": 60,
    "risk_level": "HIGH",
    "highest_threat_severity": None,
    "reasons": ["Risk score exceeds review threshold"],
    "resolution_comment": None,
}

AUDIT_EVENT_RESPONSE = {
    "event_id": "evt_123",
    "event_type": "ACTION_EVALUATED",
    "timestamp": "2026-01-01T00:00:00Z",
    "correlation_id": "corr_456",
    "action_id": "act_123",
    "agent_id": "test-agent",
    "tool_id": "database",
    "final_decision": "ALLOW",
    "decision_reasons": ["Policy allows"],
}
