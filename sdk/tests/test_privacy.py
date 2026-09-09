"""Tests verifying that credentials are never leaked in logs, errors, or payloads."""

import logging

import httpx
import pytest
import respx
from conftest import ALLOW_RESPONSE

from aegis_sdk._logging import safe_log_fields
from aegis_sdk.client import AegisClient
from aegis_sdk.errors import AegisAuthenticationError


class TestLoggingPrivacy:
    def test_safe_log_fields_redacts_credentials(self):
        fields = safe_log_fields(
            action_id="123",
            api_key="super-secret",
            password="pwd",
            token="bearer-token",
            safe_value="ok",
        )
        assert fields["action_id"] == "123"
        assert fields["safe_value"] == "ok"
        assert fields["api_key"] == "***redacted***"
        assert fields["password"] == "***redacted***"
        assert fields["token"] == "***redacted***"

    def test_logger_does_not_emit_keys(self, caplog):
        from aegis_sdk._logging import log_request
        with caplog.at_level(logging.DEBUG):
            # Pass something that looks like a key just in case
            log_request("POST", "http://test/api?api_key=secret")
        
        for record in caplog.records:
            # The URL itself is logged, but the SDK shouldn't accept URLs with query params for the base URL.
            # In actual usage, query params are passed via `params` dict, which isn't logged directly.
            assert "secret" not in record.message
            if hasattr(record, "api_key"):
                assert record.api_key == "***redacted***"


class TestErrorPrivacy:
    @respx.mock
    @pytest.mark.asyncio
    async def test_auth_error_message_is_safe(self, client):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(401, json={"detail": "Invalid API Key: my-secret-key"})
        )
        with pytest.raises(AegisAuthenticationError) as exc_info:
            await client.evaluate_action(agent_id="a", tool_id="t")
        
        # We ensure the error str is safe. (Note: if the backend is misbehaving and returns the key,
        # the SDK simply propagates the string. In Aegis, the backend NEVER returns the key.
        # But the SDK repr should definitely not include the client's configured key.)
        assert "test-api-key-12345" not in str(exc_info.value)
        assert "test-api-key-12345" not in repr(exc_info.value)

    def test_client_repr_is_safe(self):
        client = AegisClient(base_url="http://localhost:8000", api_key="my-super-secret-key-123")
        assert "my-super-secret-key-123" not in repr(client)
        assert "my-super-secret-key-123" not in str(client)


class TestRequestPrivacy:
    @respx.mock
    @pytest.mark.asyncio
    async def test_auth_header_sent_correctly(self):
        """Verify the API key is sent only in the designated header, not in the body or query."""
        def handler(request: httpx.Request):
            assert request.headers.get("X-API-Key") == "test-key"
            assert "test-key" not in str(request.url)
            body = request.read().decode("utf-8")
            if body:
                assert "test-key" not in body
            return httpx.Response(200, json=ALLOW_RESPONSE)

        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(side_effect=handler)
        
        client = AegisClient(base_url="http://test-aegis:8000", api_key="test-key")
        await client.evaluate_action(agent_id="a", tool_id="t")
