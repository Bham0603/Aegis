"""Tests for the AegisMCPGateway."""

from typing import Any

import httpx
import pytest
import respx

mcp = pytest.importorskip("mcp")
from conftest import ALLOW_RESPONSE, BLOCK_RESPONSE, REVIEW_RESPONSE
from mcp.types import CallToolResult, Tool

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import (
    ActionBlockedError,
    AegisUnavailableError,
    ApprovalRequiredError,
)
from aegis_sdk.integrations.mcp import AegisMCPGateway, _redact_secrets


class MockMCPSession:
    async def list_tools(self) -> Any:
        class ListToolsResult:
            tools = [
                Tool(name="safe_tool", description="A safe tool", inputSchema={}),
                Tool(name="dangerous_tool", description="A dangerous tool", inputSchema={}),
            ]
        return ListToolsResult()
        
    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> CallToolResult:
        if name == "fail_server":
            raise RuntimeError("Server crash")
        return CallToolResult(content=[], is_error=False)


@pytest.fixture
def mcp_gateway(client: AegisClient) -> AegisMCPGateway:
    session = MockMCPSession()
    return AegisMCPGateway(
        aegis_client=client,
        mcp_session=session, # type: ignore
        server_id="test-mcp-server",
        agent_id="test-agent"
    )

def test_redact_secrets():
    args = {
        "query": "SELECT * FROM users",
        "api_key": "secret_123",
        "nested": {
            "token": "bearer xyz",
            "safe": "value"
        }
    }
    redacted = _redact_secrets(args)
    assert redacted["query"] == "SELECT * FROM users"
    assert redacted["api_key"] == "***redacted***"
    assert redacted["nested"]["token"] == "***redacted***"
    assert redacted["nested"]["safe"] == "value"


@pytest.mark.asyncio
async def test_list_tools(mcp_gateway: AegisMCPGateway):
    tools = await mcp_gateway.list_tools()
    assert len(tools) == 2
    assert tools[0].name == "safe_tool"


class TestMCPGatewayCallTool:
    @respx.mock
    @pytest.mark.asyncio
    async def test_allow_invokes_mcp(self, mcp_gateway: AegisMCPGateway):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=ALLOW_RESPONSE)
        )
        result = await mcp_gateway.call_tool("safe_tool", {"param": "value"})
        assert not result.is_error

    @respx.mock
    @pytest.mark.asyncio
    async def test_block_raises_error(self, mcp_gateway: AegisMCPGateway):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=BLOCK_RESPONSE)
        )
        with pytest.raises(ActionBlockedError) as exc_info:
            await mcp_gateway.call_tool("dangerous_tool")
        assert "Operation blocked by policy" in exc_info.value.reasons

    @respx.mock
    @pytest.mark.asyncio
    async def test_review_raises_approval(self, mcp_gateway: AegisMCPGateway):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=REVIEW_RESPONSE)
        )
        with pytest.raises(ApprovalRequiredError) as exc_info:
            await mcp_gateway.call_tool("sensitive_tool")
        assert exc_info.value.approval_request_id == "apr_999"

    @respx.mock
    @pytest.mark.asyncio
    async def test_aegis_unavailable_fails_closed(self, mcp_gateway: AegisMCPGateway):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            side_effect=httpx.ConnectError("Connection refused")
        )
        with pytest.raises(AegisUnavailableError):
            await mcp_gateway.call_tool("safe_tool")

    @respx.mock
    @pytest.mark.asyncio
    async def test_mcp_server_failure_raises_unavailable(self, mcp_gateway: AegisMCPGateway):
        respx.post("http://test-aegis:8000/api/v1/actions/evaluate").mock(
            return_value=httpx.Response(200, json=ALLOW_RESPONSE)
        )
        with pytest.raises(AegisUnavailableError) as exc_info:
            await mcp_gateway.call_tool("fail_server")
        assert "Failed to invoke MCP tool on server" in str(exc_info.value)
