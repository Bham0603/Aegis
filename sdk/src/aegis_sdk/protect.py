"""
Protected Tool Wrapper and @aegis.protect decorator.

Provides application-level tool invocation control based on
authoritative Aegis backend decisions.

Behavior:
    ALLOW  → tool executes normally
    REVIEW → ApprovalRequiredError raised (tool does NOT execute)
    BLOCK  → ActionBlockedError raised (tool does NOT execute)
    Backend unavailable → AegisUnavailableError (fail-closed by default)

The SDK does NOT perform any local security decisions.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any, TypeVar

from aegis_sdk.client import AegisClient
from aegis_sdk.errors import (
    ActionBlockedError,
    AegisUnavailableError,
    ApprovalRequiredError,
)
from aegis_sdk.models import Decision

F = TypeVar("F", bound=Callable[..., Any])


class ProtectedTool:
    """
    Wraps any callable with Aegis security evaluation.

    Before the tool is invoked, the wrapper sends an action request to
    the Aegis backend. The tool only executes if the backend returns ALLOW.

    Args:
        client: An AegisClient instance
        tool_fn: The callable to protect
        agent_id: Agent identity for evaluation
        tool_id: Tool identity for evaluation
        operation: Operation being performed
        resource: Target resource
        environment: Deployment environment
        on_unavailable: Behavior when backend is unreachable.
            "fail_closed" (default) — raises AegisUnavailableError
            "raise" — same as fail_closed (explicit alias)
    """

    def __init__(
        self,
        client: AegisClient,
        tool_fn: Callable[..., Any],
        *,
        agent_id: str,
        tool_id: str,
        operation: str | None = None,
        resource: str | None = None,
        environment: str = "unknown",
        session_id: str = "default",
        on_unavailable: str = "fail_closed",
    ) -> None:
        self._client = client
        self._tool_fn = tool_fn
        self._agent_id = agent_id
        self._tool_id = tool_id
        self._operation = operation
        self._resource = resource
        self._environment = environment
        self._session_id = session_id
        self._on_unavailable = on_unavailable

    async def invoke(self, *args: Any, **kwargs: Any) -> Any:
        """
        Evaluate the action with the Aegis backend, then invoke the tool
        only if the backend returns ALLOW.

        Raises:
            ActionBlockedError: Backend returned BLOCK
            ApprovalRequiredError: Backend returned REVIEW
            AegisUnavailableError: Backend unreachable (fail-closed)
        """
        try:
            result = await self._client.evaluate_action(
                agent_id=self._agent_id,
                session_id=self._session_id,
                tool_id=self._tool_id,
                operation=self._operation,
                resource=self._resource,
                environment=self._environment,
            )
        except AegisUnavailableError:
            # Fail-closed: backend unavailable → do NOT execute tool
            raise
        except Exception as exc:
            # Any other Aegis error also means we don't execute
            raise AegisUnavailableError(
                f"Cannot verify security: {type(exc).__name__}"
            ) from exc

        if result.decision == Decision.BLOCK:
            raise ActionBlockedError(
                f"Action blocked: {', '.join(result.reasons) or 'No reason provided'}",
                reasons=result.reasons,
            )

        if result.decision == Decision.REVIEW:
            raise ApprovalRequiredError(
                f"Approval required: {', '.join(result.reasons) or 'Review needed'}",
                approval_request_id=result.approval_request_id,
                reasons=result.reasons,
            )

        # ALLOW — invoke the tool
        return await self._invoke_tool(*args, **kwargs)

    async def _invoke_tool(self, *args: Any, **kwargs: Any) -> Any:
        """Invoke the wrapped tool, handling both sync and async callables."""
        result = self._tool_fn(*args, **kwargs)
        if hasattr(result, "__await__"):
            return await result
        return result

    def __repr__(self) -> str:
        return (
            f"ProtectedTool(tool={self._tool_fn.__name__!r}, "
            f"agent_id={self._agent_id!r}, tool_id={self._tool_id!r})"
        )


def protect(
    client: AegisClient,
    *,
    agent_id: str,
    tool_id: str,
    operation: str | None = None,
    resource: str | None = None,
    environment: str = "unknown",
    session_id: str = "default",
    on_unavailable: str = "fail_closed",
) -> Callable[[F], F]:
    """
    Decorator that wraps a function with Aegis security evaluation.

    The decorated function will ONLY execute if the Aegis backend
    returns ALLOW. On BLOCK, REVIEW, or backend unavailability,
    an appropriate exception is raised.

    Usage:
        @protect(client, agent_id="my-agent", tool_id="database")
        async def query_database(sql: str) -> dict:
            ...

    The decorator MUST call the backend for every invocation.
    It does NOT perform local security decisions or cache results.

    Args:
        client: AegisClient instance
        agent_id: Agent identity
        tool_id: Tool identity
        operation: Operation being performed
        resource: Target resource
        environment: Deployment environment
        session_id: Session identifier
        on_unavailable: Failure mode ("fail_closed" or "raise")
    """

    def decorator(fn: F) -> F:
        tool = ProtectedTool(
            client,
            fn,
            agent_id=agent_id,
            tool_id=tool_id,
            operation=operation,
            resource=resource,
            environment=environment,
            session_id=session_id,
            on_unavailable=on_unavailable,
        )

        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            return await tool.invoke(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
