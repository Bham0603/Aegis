"""
Model Context Protocol (MCP) Integration for Aegis SDK.

This module provides the `AegisMCPGateway`, a wrapper around an underlying
MCP ClientSession. It intercepts tool discovery and tool calls, acting as a
strict security boundary.
"""
import re
from typing import Any

from mcp import ClientSession
from mcp.types import CallToolResult, Tool

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import (
    ActionBlockedError,
    AegisError,
    AegisUnavailableError,
    ApprovalRequiredError,
)
from aegis_sdk.models import Decision

# Regex to detect obvious secrets for basic redaction before sending to backend.
# The backend is authoritative, but we want to avoid sending raw secrets in the payload.
_SECRET_PATTERNS = [
    re.compile(r"(api[_-]?key|secret|password|token)", re.IGNORECASE)
]

def _redact_secrets(arguments: dict[str, Any]) -> dict[str, Any]:
    """Basic redaction of secrets in tool arguments."""
    sanitized: dict[str, Any] = {}
    for k, v in arguments.items():
        if any(p.search(k) for p in _SECRET_PATTERNS):
            sanitized[k] = "***redacted***"
        elif isinstance(v, dict):
            sanitized[k] = _redact_secrets(v)
        else:
            sanitized[k] = v
    return sanitized

def _validate_result_size(result: CallToolResult, max_length: int = 100000) -> CallToolResult:
    """Ensure the tool result size does not exceed reasonable limits to prevent memory exhaustion."""
    # This is a naive limit checking the string representation length.
    if len(str(result)) > max_length:
        raise ValueError("MCP tool result exceeded maximum allowed size limit.")
    return result

class AegisMCPGateway:
    """
    Acts as a security boundary around an MCP ClientSession.
    
    It delegates tool discovery to the underlying session, but treats all 
    returned metadata as untrusted. Tool invocations are intercepted and 
    evaluated by the Aegis backend before proceeding.
    """
    
    def __init__(
        self,
        aegis_client: AegisClient,
        mcp_session: ClientSession,
        server_id: str,
        agent_id: str,
        session_id: str | None = None,
        max_result_size: int = 100000
    ):
        self._aegis = aegis_client
        self._session = mcp_session
        self._server_id = server_id
        self._agent_id = agent_id
        self._session_id = session_id
        self._max_result_size = max_result_size
        
    async def list_tools(self) -> list[Tool]:
        """
        Discover tools from the MCP server.
        Note: Aegis does NOT automatically grant trust or permissions just 
        because a tool is discovered.
        """
        tools_result = await self._session.list_tools()
        # Return the raw tools. They are untrusted metadata.
        if hasattr(tools_result, "tools"):
            return tools_result.tools
        return tools_result # type: ignore

    async def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> CallToolResult:
        """
        Evaluate an MCP tool call against the Aegis backend.
        If allowed, invokes the tool on the MCP server.
        """
        if arguments is None:
            arguments = {}
            
        # 1. Sanitize arguments to avoid leaking secrets
        sanitized_args = _redact_secrets(arguments)
        
        # 2. Evaluate with Aegis
        # Tool identity combines the server_id and tool name to prevent collisions.
        tool_id = f"mcp://{self._server_id}/{name}"
        
        try:
            result = await self._aegis.evaluate_action(
                agent_id=self._agent_id,
                tool_id=tool_id,
                operation="mcp.tools.call",
                parameters=sanitized_args,
                session_id=self._session_id or "default"
            )
        except AegisError as e:
            # Wrap all backend failures to ensure fail-closed behavior
            raise AegisUnavailableError(f"Aegis evaluation failed: {e}") from e
        
        # 3. Handle Decision
        if result.decision == Decision.BLOCK:
            raise ActionBlockedError(reasons=result.reasons)
        elif result.decision == Decision.REVIEW:
            raise ApprovalRequiredError(approval_request_id=result.approval_request_id, reasons=result.reasons)
            
        # 4. If ALLOWED, invoke the actual MCP tool
        try:
            tool_result = await self._session.call_tool(name, arguments)
        except Exception as e:
            raise AegisUnavailableError(f"Failed to invoke MCP tool on server: {e}")
            
        # 5. Result Size Limits (Treating result as untrusted)
        return _validate_result_size(tool_result, self._max_result_size)
