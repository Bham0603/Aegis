from datetime import UTC, datetime

from app.domain.context import SecurityContext
from app.domain.decision import PermissionResult, PermissionStatusEnum
from app.models.agent import AgentStatus
from app.models.session import SessionStatus
from app.models.tool import ToolStatus
from app.models.user import UserStatus


class PermissionEngine:
    def evaluate(self, context: SecurityContext) -> PermissionResult:
        """
        Evaluates permissions based on identity and explicitly requested operation.
        """
        reasons = []

        # 1. Identity & Lifecycle Validation
        if context.agent and context.agent.status != AgentStatus.ACTIVE:
            reasons.append(f"Agent {context.agent.id} is not ACTIVE.")

        if context.user and context.user.status != UserStatus.ACTIVE:
            reasons.append(f"User {context.user.id} is not ACTIVE.")

        if context.session:
            if context.session.status != SessionStatus.ACTIVE:
                reasons.append(f"Session {context.session.id} is not ACTIVE.")

            if context.session.expires_at and context.session.expires_at < datetime.now(
                UTC
            ):
                reasons.append(f"Session {context.session.id} has expired.")

            # Ensure session matches provided agent and user
            if context.agent and context.session.agent_id != context.agent.id:
                reasons.append("Agent ID does not match Session's Agent ID.")
            if (
                context.user
                and context.session.user_id
                and context.session.user_id != context.user.id
            ):
                reasons.append("User ID does not match Session's User ID.")

        if context.user and context.agent:
            if not context.user_agent_delegation:
                reasons.append(
                    f"No delegation found from User {context.user.id} to Agent {context.agent.id}."
                )
            else:
                if not context.user_agent_delegation.enabled:
                    reasons.append(
                        f"Delegation from User {context.user.id} to Agent {context.agent.id} is disabled."
                    )
                if (
                    context.user_agent_delegation.expires_at
                    and context.user_agent_delegation.expires_at < datetime.now(UTC)
                ):
                    reasons.append(
                        f"Delegation from User {context.user.id} to Agent {context.agent.id} has expired."
                    )

        if context.tool and context.tool.status != ToolStatus.ACTIVE:
            reasons.append(f"Tool {context.tool.id} is not ACTIVE.")

        if context.agent_tool_binding:
            if not context.agent_tool_binding.enabled:
                reasons.append("AgentToolBinding is disabled.")

            # 2. Operation-Level Permissions from Binding Config Metadata
            metadata = context.agent_tool_binding.config_metadata or {}
            allowed_operations = metadata.get("allowed_operations")

            if (
                allowed_operations is not None
                and context.action.operation not in allowed_operations
            ):
                reasons.append(
                    f"Operation '{context.action.operation}' is not allowed for this agent on this tool."
                )

        if reasons:
            return PermissionResult(status=PermissionStatusEnum.DENIED, reasons=reasons)

        # Default to granted if no explicit permission checks fail,
        # relying on policy engine and trust engine to enforce further limits.
        # Alternatively, we could fail-closed here if an entity was required but missing,
        # but the evaluator coordinates that flow.
        return PermissionResult(
            status=PermissionStatusEnum.GRANTED,
            reasons=["All permission checks passed."],
        )
