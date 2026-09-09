"""Tests for the protected tool wrapper and @protect decorator."""

import httpx
import pytest
import respx
from conftest import ALLOW_RESPONSE, BLOCK_RESPONSE, REVIEW_RESPONSE

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import (
    ActionBlockedError,
    AegisUnavailableError,
    ApprovalRequiredError,
)
from aegis_sdk.protect import ProtectedTool, protect

# -- Test tool functions --

async def async_tool(x: int, y: int) -> int:
    """A simple async tool for testing."""
    return x + y


def sync_tool(x: int, y: int) -> int:
    """A simple sync tool for testing."""
    return x + y


class TestProtectedTool:
    @respx.mock
    @pytest.mark.asyncio
    async def test_allow_invokes_tool(self):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=ALLOW_RESPONSE)
        )
        client = AegisClient(base_url="http://test-aegis:8000", api_key="key", max_retries=0)
        tool = ProtectedTool(client, async_tool, agent_id="agent", tool_id="calc")
        result = await tool.invoke(3, 4)
        assert result == 7

    @respx.mock
    @pytest.mark.asyncio
    async def test_allow_invokes_sync_tool(self):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=ALLOW_RESPONSE)
        )
        client = AegisClient(base_url="http://test-aegis:8000", api_key="key", max_retries=0)
        tool = ProtectedTool(client, sync_tool, agent_id="agent", tool_id="calc")
        result = await tool.invoke(5, 6)
        assert result == 11

    @respx.mock
    @pytest.mark.asyncio
    async def test_block_raises_error_and_does_not_invoke(self):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=BLOCK_RESPONSE)
        )
        call_count = 0

        async def tracked_tool():
            nonlocal call_count
            call_count += 1

        client = AegisClient(base_url="http://test-aegis:8000", api_key="key", max_retries=0)
        tool = ProtectedTool(client, tracked_tool, agent_id="agent", tool_id="dangerous")
        with pytest.raises(ActionBlockedError) as exc_info:
            await tool.invoke()
        assert call_count == 0  # Tool was never invoked
        assert len(exc_info.value.reasons) > 0

    @respx.mock
    @pytest.mark.asyncio
    async def test_review_raises_approval_required(self):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=REVIEW_RESPONSE)
        )
        call_count = 0

        async def tracked_tool():
            nonlocal call_count
            call_count += 1

        client = AegisClient(base_url="http://test-aegis:8000", api_key="key", max_retries=0)
        tool = ProtectedTool(client, tracked_tool, agent_id="agent", tool_id="sensitive")
        with pytest.raises(ApprovalRequiredError) as exc_info:
            await tool.invoke()
        assert call_count == 0  # Tool was never invoked
        assert exc_info.value.approval_request_id == "apr_999"

    @respx.mock
    @pytest.mark.asyncio
    async def test_backend_unavailable_raises_error(self):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        call_count = 0

        async def tracked_tool():
            nonlocal call_count
            call_count += 1

        client = AegisClient(base_url="http://test-aegis:8000", api_key="key", max_retries=0)
        tool = ProtectedTool(client, tracked_tool, agent_id="agent", tool_id="calc")
        with pytest.raises(AegisUnavailableError):
            await tool.invoke()
        assert call_count == 0  # Fail-closed: tool was never invoked

    def test_repr(self):
        client = AegisClient(base_url="http://test-aegis:8000", api_key="key", max_retries=0)
        tool = ProtectedTool(client, async_tool, agent_id="agent", tool_id="calc")
        assert "ProtectedTool" in repr(tool)
        assert "async_tool" in repr(tool)


class TestProtectDecorator:
    @respx.mock
    @pytest.mark.asyncio
    async def test_decorated_function_runs_on_allow(self):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=ALLOW_RESPONSE)
        )
        client = AegisClient(base_url="http://test-aegis:8000", api_key="key", max_retries=0)

        @protect(client, agent_id="agent", tool_id="calc")
        async def add(x: int, y: int) -> int:
            return x + y

        result = await add(10, 20)
        assert result == 30

    @respx.mock
    @pytest.mark.asyncio
    async def test_decorated_function_blocked(self):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=BLOCK_RESPONSE)
        )
        client = AegisClient(base_url="http://test-aegis:8000", api_key="key", max_retries=0)

        @protect(client, agent_id="agent", tool_id="dangerous")
        async def delete_everything() -> None:
            pass

        with pytest.raises(ActionBlockedError):
            await delete_everything()
