import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.action import Action
from app.domain.context import SecurityContext
from app.domain.decision import DecisionEnum, SecurityDecision
from app.services.policy_engine import PolicyEngine
from app.services.policy_service import PolicyService

logger = structlog.get_logger(__name__)


async def evaluate_action(action: Action, db: AsyncSession) -> SecurityDecision:
    """
    Evaluates the action through the Deterministic Policy Engine (Phase 4).
    Implements strict precedence and fail-closed behavior.
    """
    try:
        # Build Context (Stub for now)
        _context = SecurityContext(action=action)

        # 1. Fetch active policies
        policy_svc = PolicyService(db)
        policies = await policy_svc.get_active_policies()

        # 2. Evaluate using PolicyEngine
        eval_result = PolicyEngine.evaluate(
            action=action,
            policies=policies,  # type: ignore
            context={"environment": action.environment},
        )

        final_effect = eval_result["final_effect"]
        matched_rules = eval_result["matched_rules"]
        reasons = []

        if eval_result["default_deny"]:
            reasons.append("Default Deny: No matching policy found.")
        else:
            for match in matched_rules:
                reasons.append(f"Matched Policy '{match['policy_name']}' (Priority {match['priority']}) -> {match['effect']}")

        # Map PolicyEffect to DecisionEnum
        decision_val = DecisionEnum.BLOCK
        if final_effect == "ALLOW":
            decision_val = DecisionEnum.ALLOW
        elif final_effect == "REVIEW":
            decision_val = DecisionEnum.REVIEW
        elif final_effect == "BLOCK":
            decision_val = DecisionEnum.BLOCK

        # 3. Return decision
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
