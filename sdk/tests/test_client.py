"""Tests for the Aegis SDK client."""

import httpx
import pytest
import respx
from conftest import (
    ALLOW_RESPONSE,
    APPROVAL_RESPONSE,
    AUDIT_EVENT_RESPONSE,
    BLOCK_RESPONSE,
    REVIEW_RESPONSE,
)

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import (
    AegisAuthenticationError,
    AegisAuthorizationError,
    AegisNetworkError,
    AegisNotFoundError,
    AegisRateLimitError,
    AegisServerError,
    AegisTimeoutError,
    AegisValidationError,
)
from aegis_sdk.models import Decision


class TestClientConfiguration:
    def test_requires_base_url(self):
        with pytest.raises(ValueError, match="base_url is required"):
            AegisClient(api_key="key")

    def test_requires_api_key(self):
        with pytest.raises(ValueError, match="api_key is required"):
            AegisClient(base_url="http://localhost:8000")

    def test_rejects_negative_timeout(self):
        with pytest.raises(ValueError, match="timeout must be positive"):
            AegisClient(base_url="http://localhost:8000", api_key="key", timeout=-1)

    def test_rejects_negative_retries(self):
        with pytest.raises(ValueError, match="max_retries must be non-negative"):
            AegisClient(base_url="http://localhost:8000", api_key="key", max_retries=-1)

    def test_env_var_fallback(self, monkeypatch):
        monkeypatch.setenv("AEGIS_BASE_URL", "http://env-host:8000")
        monkeypatch.setenv("AEGIS_API_KEY", "env-key")
        monkeypatch.setenv("AEGIS_TIMEOUT", "10")
        monkeypatch.setenv("AEGIS_RETRY_COUNT", "5")
        client = AegisClient()
        assert "env-host" in repr(client)

    def test_safe_repr(self):
        client = AegisClient(base_url="http://localhost:8000", api_key="super-secret")
        r = repr(client)
        assert "super-secret" not in r
        assert "***redacted***" in r

    def test_safe_str(self):
        client = AegisClient(base_url="http://localhost:8000", api_key="super-secret")
        s = str(client)
        assert "super-secret" not in s
        assert "***redacted***" in s

    def test_rejects_javascript_url(self):
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            AegisClient(base_url="javascript:alert(1)", api_key="key")

    def test_rejects_file_url(self):
        with pytest.raises(ValueError, match="Unsupported URL scheme"):
            AegisClient(base_url="file:///etc/passwd", api_key="key")


class TestEvaluateAction:
    @respx.mock
    @pytest.mark.asyncio
    async def test_allow_response(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=ALLOW_RESPONSE)
        )
        result = await client.evaluate_action(
            agent_id="test-agent", tool_id="database", operation="query",
        )
        assert result.decision == Decision.ALLOW
        assert result.allowed is True
        assert result.action_id == "act_123"

    @respx.mock
    @pytest.mark.asyncio
    async def test_block_response(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=BLOCK_RESPONSE)
        )
        result = await client.evaluate_action(
            agent_id="test-agent", tool_id="database", operation="delete",
        )
        assert result.decision == Decision.BLOCK
        assert result.blocked is True
        assert "Operation blocked by policy" in result.reasons

    @respx.mock
    @pytest.mark.asyncio
    async def test_review_response(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=REVIEW_RESPONSE)
        )
        result = await client.evaluate_action(
            agent_id="test-agent", tool_id="database",
        )
        assert result.decision == Decision.REVIEW
        assert result.review_required is True
        assert result.approval_request_id == "apr_999"


class TestErrorHandling:
    @respx.mock
    @pytest.mark.asyncio
    async def test_401_raises_auth_error(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid API Key"})
        )
        with pytest.raises(AegisAuthenticationError):
            await client.evaluate_action(agent_id="a", tool_id="t")

    @respx.mock
    @pytest.mark.asyncio
    async def test_403_raises_authz_error(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(403, json={"detail": "Forbidden"})
        )
        with pytest.raises(AegisAuthorizationError):
            await client.evaluate_action(agent_id="a", tool_id="t")

    @respx.mock
    @pytest.mark.asyncio
    async def test_404_raises_not_found(self, client):
        respx.get("http://test-aegis:8000/api/v1/approvals/nonexistent").mock(
            return_value=httpx.Response(404, json={"detail": "Not found"})
        )
        with pytest.raises(AegisNotFoundError):
            await client.get_approval("nonexistent")

    @respx.mock
    @pytest.mark.asyncio
    async def test_422_raises_validation_error(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(422, json={"detail": "Validation error"})
        )
        with pytest.raises(AegisValidationError):
            await client.evaluate_action(agent_id="a", tool_id="t")

    @respx.mock
    @pytest.mark.asyncio
    async def test_429_raises_rate_limit(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(429, json={"detail": "Rate limit"})
        )
        with pytest.raises(AegisRateLimitError):
            await client.evaluate_action(agent_id="a", tool_id="t")

    @respx.mock
    @pytest.mark.asyncio
    async def test_500_raises_server_error(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(500, json={"detail": "Internal error"})
        )
        with pytest.raises(AegisServerError):
            await client.evaluate_action(agent_id="a", tool_id="t")

    @respx.mock
    @pytest.mark.asyncio
    async def test_malformed_json_raises_server_error(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, content=b"not json")
        )
        with pytest.raises(AegisServerError, match="Invalid JSON"):
            await client.evaluate_action(agent_id="a", tool_id="t")

    @respx.mock
    @pytest.mark.asyncio
    async def test_network_error(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        with pytest.raises(AegisNetworkError):
            await client.evaluate_action(agent_id="a", tool_id="t")

    @respx.mock
    @pytest.mark.asyncio
    async def test_timeout_error(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            side_effect=httpx.ReadTimeout("timeout")
        )
        with pytest.raises(AegisTimeoutError):
            await client.evaluate_action(agent_id="a", tool_id="t")


class TestApprovalClient:
    @respx.mock
    @pytest.mark.asyncio
    async def test_get_approval(self, client):
        respx.get("http://test-aegis:8000/api/v1/approvals/apr_999").mock(
            return_value=httpx.Response(200, json=APPROVAL_RESPONSE)
        )
        info = await client.get_approval("apr_999")
        assert info.approval_request_id == "apr_999"
        assert info.is_pending is True

    @respx.mock
    @pytest.mark.asyncio
    async def test_approve(self, client):
        approved = {**APPROVAL_RESPONSE, "status": "APPROVED", "approver_id": "human-1"}
        respx.post("http://test-aegis:8000/api/v1/approvals/apr_999/approve").mock(
            return_value=httpx.Response(200, json=approved)
        )
        info = await client.approve("apr_999", approver_id="human-1", comment="LGTM")
        assert info.is_approved is True

    @respx.mock
    @pytest.mark.asyncio
    async def test_deny(self, client):
        denied = {**APPROVAL_RESPONSE, "status": "DENIED", "approver_id": "human-1"}
        respx.post("http://test-aegis:8000/api/v1/approvals/apr_999/deny").mock(
            return_value=httpx.Response(200, json=denied)
        )
        info = await client.deny("apr_999", approver_id="human-1", comment="Too risky")
        assert info.is_denied is True


class TestAuditClient:
    @respx.mock
    @pytest.mark.asyncio
    async def test_list_events(self, client):
        respx.get("http://test-aegis:8000/api/v1/audit/events").mock(
            return_value=httpx.Response(200, json=[AUDIT_EVENT_RESPONSE])
        )
        events = await client.list_audit_events(limit=10)
        assert len(events) == 1
        assert events[0].event_id == "evt_123"

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_event(self, client):
        respx.get("http://test-aegis:8000/api/v1/audit/events/evt_123").mock(
            return_value=httpx.Response(200, json=AUDIT_EVENT_RESPONSE)
        )
        event = await client.get_audit_event("evt_123")
        assert event.event_type == "ACTION_EVALUATED"

    @respx.mock
    @pytest.mark.asyncio
    async def test_action_history(self, client):
        respx.get("http://test-aegis:8000/api/v1/audit/actions/act_123").mock(
            return_value=httpx.Response(200, json=[AUDIT_EVENT_RESPONSE])
        )
        events = await client.get_action_history("act_123")
        assert len(events) == 1

    @respx.mock
    @pytest.mark.asyncio
    async def test_correlation_history(self, client):
        respx.get("http://test-aegis:8000/api/v1/audit/correlations/corr_456").mock(
            return_value=httpx.Response(200, json=[AUDIT_EVENT_RESPONSE])
        )
        events = await client.get_correlation_history("corr_456")
        assert len(events) == 1


class TestAttackLabClient:
    @respx.mock
    @pytest.mark.asyncio
    async def test_list_scenarios(self, client):
        respx.get("http://test-aegis:8000/api/v1/attack-lab/scenarios").mock(
            return_value=httpx.Response(200, json=[{"scenario_id": "sc_1", "name": "Test"}])
        )
        scenarios = await client.list_attack_scenarios()
        assert len(scenarios) == 1
        assert scenarios[0].scenario_id == "sc_1"

    @respx.mock
    @pytest.mark.asyncio
    async def test_run_scenario(self, client):
        respx.post("http://test-aegis:8000/api/v1/attack-lab/runs").mock(
            return_value=httpx.Response(200, json={"run_id": "run_1", "status": "PASS", "scenario_id": "sc_1"})
        )
        result = await client.run_attack_scenario("sc_1")
        assert result.passed is True

    @respx.mock
    @pytest.mark.asyncio
    async def test_get_run(self, client):
        respx.get("http://test-aegis:8000/api/v1/attack-lab/runs/run_1").mock(
            return_value=httpx.Response(200, json={"run_id": "run_1", "status": "FAIL"})
        )
        result = await client.get_attack_run("run_1")
        assert result.passed is False


class TestContextManager:
    @respx.mock
    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=ALLOW_RESPONSE)
        )
        async with AegisClient(base_url="http://test-aegis:8000", api_key="key") as client:
            result = await client.evaluate_action(agent_id="a", tool_id="t")
            assert result.allowed
