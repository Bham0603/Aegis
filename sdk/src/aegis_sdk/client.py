"""
Aegis SDK Client.

The primary developer interface for interacting with the Aegis Security Gateway.
This is a CLIENT/INTEGRATION LAYER — all security decisions come from the backend.

Usage:
    async with AegisClient(base_url="http://localhost:8000", api_key="...") as client:
        result = await client.evaluate_action(
            agent_id="research-agent",
            tool_id="database",
            operation="query",
            resource="customers",
            environment="production",
        )
        if result.blocked:
            raise SecurityError(result.reason)
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from aegis_sdk._http import HttpTransport
from aegis_sdk.models import (
    ActionRequest,
    ApprovalInfo,
    AttackRunResult,
    AttackScenario,
    AuditEvent,
    EvaluationResult,
)


class AegisClient:
    """
    Async-first client for the Aegis Security Gateway API.

    Supports both async context manager and explicit close().
    Configuration is read from explicit arguments first, then
    from environment variables as fallback.

    Environment Variables:
        AEGIS_BASE_URL: Base URL of the Aegis backend
        AEGIS_API_KEY: API key for authentication
        AEGIS_TIMEOUT: Request timeout in seconds (default: 30)
        AEGIS_RETRY_COUNT: Max retries for transient failures (default: 3)
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        *,
        timeout: float | None = None,
        max_retries: int | None = None,
    ) -> None:
        resolved_url = base_url or os.environ.get("AEGIS_BASE_URL", "")
        resolved_key = api_key or os.environ.get("AEGIS_API_KEY", "")
        resolved_timeout = timeout or float(os.environ.get("AEGIS_TIMEOUT", "30"))
        resolved_retries = max_retries if max_retries is not None else int(os.environ.get("AEGIS_RETRY_COUNT", "3"))

        # Validate required configuration
        if not resolved_url:
            raise ValueError(
                "base_url is required. Provide it as an argument or set AEGIS_BASE_URL."
            )
        if not resolved_key:
            raise ValueError(
                "api_key is required. Provide it as an argument or set AEGIS_API_KEY."
            )
        if resolved_timeout <= 0:
            raise ValueError("timeout must be positive")
        if resolved_retries < 0:
            raise ValueError("max_retries must be non-negative")

        self._transport = HttpTransport(
            base_url=resolved_url,
            api_key=resolved_key,
            timeout=resolved_timeout,
            max_retries=resolved_retries,
        )
        self._base_url = resolved_url

    async def close(self) -> None:
        """Close the underlying HTTP client and release resources."""
        await self._transport.close()

    async def __aenter__(self) -> AegisClient:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()

    def __repr__(self) -> str:
        """Safe representation — NEVER exposes the API key."""
        return f"AegisClient(base_url={self._base_url!r}, api_key='***redacted***')"

    def __str__(self) -> str:
        return self.__repr__()

    # ------------------------------------------------------------------
    # Sync convenience wrappers
    # ------------------------------------------------------------------

    def evaluate_action_sync(self, **kwargs: Any) -> EvaluationResult:
        """Synchronous wrapper for evaluate_action."""
        return asyncio.run(self.evaluate_action(**kwargs))

    def ping_sync(self) -> dict[str, Any]:
        """Synchronous wrapper for ping."""
        return asyncio.run(self.ping())

    # ------------------------------------------------------------------
    # Core API — Action Evaluation
    # ------------------------------------------------------------------

    async def evaluate_action(
        self,
        *,
        agent_id: str,
        session_id: str = "default",
        tool_id: str,
        user_id: str | None = None,
        operation: str | None = None,
        resource: str | None = None,
        parameters: dict[str, Any] | None = None,
        environment: str = "unknown",
        authorization_context: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> EvaluationResult:
        """
        Submit an action to the Aegis backend for security evaluation.

        Args:
            agent_id: Identity of the AI agent
            session_id: Session identifier
            tool_id: Tool being invoked
            user_id: Optional human user identity
            operation: Operation being performed
            resource: Target resource
            parameters: Action parameters
            environment: Deployment environment
            authorization_context: Additional auth context
            correlation_id: Optional caller-supplied correlation ID

        Returns:
            EvaluationResult with the backend's authoritative security decision

        Raises:
            AegisError subclasses on failure
        """
        action = ActionRequest(
            agent_id=agent_id,
            session_id=session_id,
            tool_id=tool_id,
            user_id=user_id,
            operation=operation,
            resource=resource,
            parameters=parameters,
            environment=environment,
            authorization_context=authorization_context,
        )
        data = await self._transport.request(
            "POST",
            "/actions/evaluate",
            json=action.to_dict(),
            correlation_id=correlation_id,
            is_mutation=False,  # Evaluate is safe to retry
        )
        return EvaluationResult(data)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Approval Workflow
    # ------------------------------------------------------------------

    async def get_approval(self, approval_request_id: str) -> ApprovalInfo:
        """Retrieve an approval request by ID."""
        data = await self._transport.request(
            "GET",
            f"/approvals/{approval_request_id}",
        )
        return ApprovalInfo(data)  # type: ignore[arg-type]

    async def approve(
        self,
        approval_request_id: str,
        *,
        approver_id: str,
        comment: str | None = None,
    ) -> ApprovalInfo:
        """
        Approve a pending approval request.

        This is a state-changing mutation — it will NOT be automatically retried.
        """
        data = await self._transport.request(
            "POST",
            f"/approvals/{approval_request_id}/approve",
            json={
                "approver_id": approver_id,
                "decision": "APPROVED",
                "comment": comment,
            },
            is_mutation=True,  # Never retry approval mutations
        )
        return ApprovalInfo(data)  # type: ignore[arg-type]

    async def deny(
        self,
        approval_request_id: str,
        *,
        approver_id: str,
        comment: str | None = None,
    ) -> ApprovalInfo:
        """
        Deny a pending approval request.

        This is a state-changing mutation — it will NOT be automatically retried.
        """
        data = await self._transport.request(
            "POST",
            f"/approvals/{approval_request_id}/deny",
            json={
                "approver_id": approver_id,
                "decision": "DENIED",
                "comment": comment,
            },
            is_mutation=True,  # Never retry denial mutations
        )
        return ApprovalInfo(data)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Audit
    # ------------------------------------------------------------------

    async def list_audit_events(
        self,
        *,
        limit: int = 50,
        offset: int = 0,
        event_type: str | None = None,
        agent_id: str | None = None,
        user_id: str | None = None,
        decision: str | None = None,
    ) -> list[AuditEvent]:
        """
        List audit events with pagination and optional filtering.

        Args:
            limit: Max events to return (1-100, default 50)
            offset: Pagination offset
            event_type: Filter by event type
            agent_id: Filter by agent
            user_id: Filter by user
            decision: Filter by decision

        Returns:
            List of AuditEvent objects
        """
        data = await self._transport.request(
            "GET",
            "/audit/events",
            params={
                "limit": limit,
                "offset": offset,
                "event_type": event_type,
                "agent_id": agent_id,
                "user_id": user_id,
                "decision": decision,
            },
        )
        if not isinstance(data, list):
            return []
        return [AuditEvent(item) for item in data]

    async def get_audit_event(self, event_id: str) -> AuditEvent:
        """Retrieve a specific audit event by ID."""
        data = await self._transport.request("GET", f"/audit/events/{event_id}")
        return AuditEvent(data)  # type: ignore[arg-type]

    async def get_action_history(self, action_id: str) -> list[AuditEvent]:
        """Retrieve all audit events for a specific action."""
        data = await self._transport.request("GET", f"/audit/actions/{action_id}")
        if not isinstance(data, list):
            return []
        return [AuditEvent(item) for item in data]

    async def get_correlation_history(self, correlation_id: str) -> list[AuditEvent]:
        """Retrieve all audit events for a specific correlation ID."""
        data = await self._transport.request("GET", f"/audit/correlations/{correlation_id}")
        if not isinstance(data, list):
            return []
        return [AuditEvent(item) for item in data]

    # ------------------------------------------------------------------
    # Attack Lab
    # ------------------------------------------------------------------

    async def list_attack_scenarios(self) -> list[AttackScenario]:
        """List all available Attack Lab scenarios."""
        data = await self._transport.request("GET", "/attack-lab/scenarios")
        if not isinstance(data, list):
            return []
        return [AttackScenario(item) for item in data]

    async def run_attack_scenario(self, scenario_id: str) -> AttackRunResult:
        """
        Execute an Attack Lab scenario.

        Only supports the existing safe scenario API — does NOT expose
        arbitrary execution.

        This is a state-changing mutation — it will NOT be automatically retried.
        """
        data = await self._transport.request(
            "POST",
            "/attack-lab/runs",
            json={"scenario_id": scenario_id},
            is_mutation=True,
        )
        return AttackRunResult(data)  # type: ignore[arg-type]

    async def get_attack_run(self, run_id: str) -> AttackRunResult:
        """Retrieve a specific Attack Lab run result."""
        data = await self._transport.request("GET", f"/attack-lab/runs/{run_id}")
        return AttackRunResult(data)  # type: ignore[arg-type]

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    async def ping(self) -> dict[str, Any]:
        """
        Check Aegis backend health.

        Returns the health check response from the backend.
        """
        # Health endpoint is outside the versioned API
        data = await self._transport.request("GET", "/../health")
        return data  # type: ignore[return-value]
