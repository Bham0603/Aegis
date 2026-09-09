"""
LangChain integration for Aegis SDK.

Provides AegisToolWrapper — a LangChain-compatible tool that wraps
another tool with Aegis security evaluation.

Optional dependency: requires `langchain-core>=0.1.0`.
Install with: pip install aegis-sdk[langchain]

Usage:
    from langchain_core.tools import Tool
    from aegis_sdk.integrations.langchain import AegisToolWrapper

    inner_tool = Tool(name="database", func=query_db, description="Query DB")
    protected = AegisToolWrapper(
        client=aegis_client,
        tool=inner_tool,
        agent_id="research-agent",
    )

    # protected.invoke(...) will evaluate with Aegis before executing
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import (
    ActionBlockedError,
    AegisUnavailableError,
    ApprovalRequiredError,
)
from aegis_sdk.models import Decision

if TYPE_CHECKING:
    from langchain_core.tools import BaseTool


class AegisToolWrapper:
    """
    Wraps a LangChain BaseTool with Aegis security evaluation.

    On each invocation, sends an action request to the Aegis backend.
    The underlying tool only executes if the backend returns ALLOW.

    This adapter does NOT monkey-patch LangChain internals — it wraps
    the tool invocation cleanly through the public API.
    """

    def __init__(
        self,
        client: AegisClient,
        tool: BaseTool,
        *,
        agent_id: str,
        session_id: str = "default",
        environment: str = "unknown",
    ) -> None:
        self._client = client
        self._tool = tool
        self._agent_id = agent_id
        self._session_id = session_id
        self._environment = environment

    @property
    def name(self) -> str:
        return self._tool.name

    @property
    def description(self) -> str:
        return self._tool.description

    async def ainvoke(self, input: Any, **kwargs: Any) -> Any:
        """
        Async invocation with Aegis security check.

        Raises:
            ActionBlockedError: Backend returned BLOCK
            ApprovalRequiredError: Backend returned REVIEW
            AegisUnavailableError: Backend unreachable
        """
        try:
            result = await self._client.evaluate_action(
                agent_id=self._agent_id,
                session_id=self._session_id,
                tool_id=self._tool.name,
                operation="invoke",
                environment=self._environment,
            )
        except AegisUnavailableError:
            raise
        except Exception as exc:
            raise AegisUnavailableError(
                f"Cannot verify security: {type(exc).__name__}"
            ) from exc

        if result.decision == Decision.BLOCK:
            raise ActionBlockedError(
                f"Action blocked: {', '.join(result.reasons) or 'Blocked by policy'}",
                reasons=result.reasons,
            )

        if result.decision == Decision.REVIEW:
            raise ApprovalRequiredError(
                f"Approval required for {self._tool.name}",
                approval_request_id=result.approval_request_id,
                reasons=result.reasons,
            )

        # ALLOW — invoke the underlying LangChain tool
        if hasattr(self._tool, "ainvoke"):
            return await self._tool.ainvoke(input, **kwargs)
        return self._tool.invoke(input, **kwargs)

    def invoke(self, input: Any, **kwargs: Any) -> Any:
        """
        Sync invocation — delegates to ainvoke via asyncio.run().
        """
        import asyncio
        return asyncio.run(self.ainvoke(input, **kwargs))

    def __repr__(self) -> str:
        return (
            f"AegisToolWrapper(tool={self._tool.name!r}, "
            f"agent_id={self._agent_id!r})"
        )
