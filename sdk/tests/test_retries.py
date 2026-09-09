"""Tests for the SDK's retry logic and transient error handling."""

import httpx
import pytest
import respx
from conftest import ALLOW_RESPONSE

from aegis_sdk.errors import (
    AegisAuthenticationError,
    AegisServerError,
    AegisUnavailableError,
)


class TestRetries:
    @respx.mock
    @pytest.mark.asyncio
    async def test_retries_transient_502_then_succeeds(self, client_with_retries):
        route = respx.post("http://test-aegis:8000/api/v1/actions/evaluate")
        route.side_effect = [
            httpx.Response(502, json={"detail": "Bad Gateway"}),
            httpx.Response(200, json=ALLOW_RESPONSE),
        ]
        
        result = await client_with_retries.evaluate_action(agent_id="a", tool_id="t")
        assert result.allowed is True
        assert route.call_count == 2

    @respx.mock
    @pytest.mark.asyncio
    async def test_exhausts_retries_and_raises_unavailable(self, client_with_retries):
        route = respx.post("http://test-aegis:8000/api/v1/actions/evaluate")
        route.mock(return_value=httpx.Response(503, json={"detail": "Service Unavailable"}))
        
        with pytest.raises(AegisUnavailableError) as exc_info:
            await client_with_retries.evaluate_action(agent_id="a", tool_id="t")
            
        assert "after 3 attempts" in str(exc_info.value)
        assert route.call_count == 3  # 1 initial + 2 retries

    @respx.mock
    @pytest.mark.asyncio
    async def test_does_not_retry_auth_errors(self, client_with_retries):
        route = respx.post("http://test-aegis:8000/api/v1/actions/evaluate")
        route.mock(return_value=httpx.Response(401, json={"detail": "Unauthorized"}))
        
        with pytest.raises(AegisAuthenticationError):
            await client_with_retries.evaluate_action(agent_id="a", tool_id="t")
            
        assert route.call_count == 1  # No retries for 401

    @respx.mock
    @pytest.mark.asyncio
    async def test_does_not_retry_500_internal_error(self, client_with_retries):
        route = respx.post("http://test-aegis:8000/api/v1/actions/evaluate")
        route.mock(return_value=httpx.Response(500, json={"detail": "Internal Server Error"}))
        
        with pytest.raises(AegisServerError):
            await client_with_retries.evaluate_action(agent_id="a", tool_id="t")
            
        assert route.call_count == 1  # 500 is not in _RETRYABLE_STATUS_CODES (only 502, 503, 504)

    @respx.mock
    @pytest.mark.asyncio
    async def test_does_not_retry_mutations(self, client_with_retries):
        route = respx.post("http://test-aegis:8000/api/v1/approvals/apr_1/approve")
        route.mock(return_value=httpx.Response(502, json={"detail": "Bad Gateway"}))
        
        with pytest.raises(AegisUnavailableError):
            await client_with_retries.approve("apr_1", approver_id="h1")
            
        assert route.call_count == 1  # Mutations are not retried even on 502

    @respx.mock
    @pytest.mark.asyncio
    async def test_retries_network_errors(self, client_with_retries):
        route = respx.post("http://test-aegis:8000/api/v1/actions/evaluate")
        route.side_effect = [
            httpx.ConnectError("Connection refused"),
            httpx.Response(200, json=ALLOW_RESPONSE),
        ]
        
        result = await client_with_retries.evaluate_action(agent_id="a", tool_id="t")
        assert result.allowed is True
        assert route.call_count == 2
