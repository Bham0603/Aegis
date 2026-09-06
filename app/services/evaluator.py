import uuid

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.decision import (
    DecisionEnum,
    PermissionStatusEnum,
    SecurityDecision,
    TrustClassEnum,
)
from app.schemas.registry import (
    AgentResponse,
    AgentToolBindingResponse,
    SessionResponse,
    ToolResponse,
    UserAgentDelegationResponse,
    UserResponse,
)
from app.services.permission_engine import PermissionEngine
from app.services.policy_engine import PolicyEngine
from app.services.policy_service import PolicyService
from app.services.registry_service import RegistryService
from app.services.trust_engine import TrustEngine

logger = structlog.get_logger(__name__)


async def evaluate_action(action: Action, db: AsyncSession) -> SecurityDecision:
    """
    Evaluates the action through the Permission Engine, Trust Engine, and Policy Engine (Phase 5).
    Implements strict precedence and fail-closed behavior.
    """
    try:
        registry_svc = RegistryService(db)

        # 1. Fetch Context Entities
        agent_resp = None
        user_resp = None
        session_resp = None
        tool_resp = None
        binding_resp = None
        delegation_resp = None

        if action.agent_id:
            try:
                agent = await registry_svc.get_agent(uuid.UUID(action.agent_id))
                if agent:
                    agent_resp = AgentResponse.model_validate(agent)
            except ValueError:
                pass

        if action.user_id:
            try:
                user = await registry_svc.get_user(uuid.UUID(action.user_id))
                if user:
                    user_resp = UserResponse.model_validate(user)
            except ValueError:
                pass

        if action.session_id:
            try:
                session = await registry_svc.get_session(uuid.UUID(action.session_id))
                if session:
                    session_resp = SessionResponse.model_validate(session)
            except ValueError:
                pass

        if action.tool_id:
            try:
                tool = await registry_svc.get_tool(uuid.UUID(action.tool_id))
                if tool:
                    tool_resp = ToolResponse.model_validate(tool)
            except ValueError:
                pass

        if agent_resp and tool_resp:
            bindings = await registry_svc.get_agent_bindings(agent_resp.id)
            for b in bindings:
                if str(b.tool_id) == str(tool_resp.id):
                    binding_resp = AgentToolBindingResponse.model_validate(b)
                    break

        if agent_resp and user_resp:
            delegation = await registry_svc.get_user_agent_delegation(
                user_resp.id, agent_resp.id
            )
            if delegation:
                delegation_resp = UserAgentDelegationResponse.model_validate(delegation)

        # Build Context
        _context = SecurityContext(
            action=action,
            agent=agent_resp,
            user=user_resp,
            session=session_resp,
            tool=tool_resp,
            agent_tool_binding=binding_resp,
            user_agent_delegation=delegation_resp,
        )

        # 2. Evaluate Permissions
        permission_engine = PermissionEngine()
        permission_result = permission_engine.evaluate(_context)

        if permission_result.status == PermissionStatusEnum.DENIED:
            return SecurityDecision(
                action_id=action.action_id,
                correlation_id=action.correlation_id,
                timestamp=action.timestamp,
                decision=DecisionEnum.BLOCK,
                reasons=["Permission DENIED: " + " | ".join(permission_result.reasons)],
            )

        # 3. Evaluate Trust
        trust_engine = TrustEngine()
        trust_result = trust_engine.evaluate(_context)

        if trust_result.trust_class == TrustClassEnum.BLOCKED:
            return SecurityDecision(
                action_id=action.action_id,
                correlation_id=action.correlation_id,
                timestamp=action.timestamp,
                decision=DecisionEnum.BLOCK,
                reasons=["Trust Engine BLOCKED: " + " | ".join(trust_result.reasons)],
            )

        # 4. Fetch active policies
        policy_svc = PolicyService(db)
        policies = await policy_svc.get_active_policies()

        # 5. Evaluate using PolicyEngine
        # Inject trust_class into the context for Policy Engine
        eval_context = {
            "environment": action.environment,
            "trust_class": trust_result.trust_class.value,
        }

        eval_result = PolicyEngine.evaluate(
            action=action,
            policies=policies,  # type: ignore
            context=eval_context,
        )

        final_effect = eval_result["final_effect"]
        matched_rules = eval_result["matched_rules"]
        reasons = []

        if eval_result["default_deny"]:
            reasons.append("Default Deny: No matching policy found.")
        else:
            for match in matched_rules:
                reasons.append(
                    f"Matched Policy '{match['policy_name']}' (Priority {match['priority']}) -> {match['effect']}"
                )

        # Include trust reason info
        reasons.extend(trust_result.reasons)

        # Map PolicyEffect to DecisionEnum
        decision_val = DecisionEnum.BLOCK
        if final_effect == "ALLOW":
            decision_val = DecisionEnum.ALLOW
        elif final_effect == "REVIEW":
            decision_val = DecisionEnum.REVIEW
        elif final_effect == "BLOCK":
            decision_val = DecisionEnum.BLOCK

        # 6. Return decision
        return SecurityDecision(
            action_id=action.action_id,
            correlation_id=action.correlation_id,
            timestamp=action.timestamp,
            decision=decision_val,
            reasons=reasons,
        )

    except Exception as e:  # noqa: BLE001
        logger.error(
            "Security evaluation failure", error=str(e), action_id=action.action_id
        )
        # Fail-closed
        return SecurityDecision(
            action_id=action.action_id,
            correlation_id=action.correlation_id,
            timestamp=action.timestamp,
            decision=DecisionEnum.BLOCK,
            reasons=["Security evaluation failure (Fail-Closed)"],
        )
