import logging
from typing import Any

from app.domain.action import Action
from app.models.policy import Policy, PolicyEffect

logger = logging.getLogger(__name__)


class PolicyEngine:
    """
    Evaluates an Action and its context against a set of Policy models.
    Deterministic, explainable, and testable.
    """

    @staticmethod
    def evaluate(
        action: Action, policies: list[Policy], context: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Evaluate policies using explicit precedence: BLOCK > REVIEW > ALLOW.
        Default is BLOCK (deny by default).
        """
        results: list[dict[str, Any]] = []

        # Sort policies by priority descending
        sorted_policies = sorted(policies, key=lambda p: p.priority, reverse=True)

        for policy in sorted_policies:
            if policy.status.value != "ACTIVE":
                continue

            for rule_dict in policy.rules:
                effect = rule_dict.get("effect")
                condition = rule_dict.get("condition", {})

                # If the rule matches the action, record it
                if PolicyEngine._matches_condition(action, context, condition):
                    results.append(
                        {
                            "policy_id": str(policy.id),
                            "policy_name": policy.name,
                            "effect": effect,
                            "priority": policy.priority,
                        }
                    )

        # Precedence reduction: BLOCK > REVIEW > ALLOW
        final_effect = PolicyEffect.BLOCK
        if not results:
            final_effect = PolicyEffect.BLOCK  # Default deny
        elif any(r["effect"] == PolicyEffect.BLOCK.value for r in results):
            final_effect = PolicyEffect.BLOCK
        elif any(r["effect"] == PolicyEffect.REVIEW.value for r in results):
            final_effect = PolicyEffect.REVIEW
        elif any(r["effect"] == PolicyEffect.ALLOW.value for r in results):
            final_effect = PolicyEffect.ALLOW

        return {
            "final_effect": final_effect.value,
            "matched_rules": results,
            "default_deny": not results,
        }

    @staticmethod
    def _matches_condition(
        action: Action, context: dict[str, Any], condition: dict[str, dict[str, Any]]
    ) -> bool:
        """
        Evaluate if a given condition matches the action + context.
        Condition format:
        {
            "tool_name": {"eq": "shell"},
            "parameters.path": {"startswith": "/etc/"}
        }
        """
        if not condition:
            return True  # Empty condition matches everything (catch-all for an effect)

        # Merge action data and context for evaluation
        eval_data = {
            "agent_id": action.agent_id,
            "tool_id": action.tool_id,
            "parameters": action.parameters,
            "context": context,
        }

        for field_path, operators in condition.items():
            field_value = PolicyEngine._get_nested_value(eval_data, field_path)

            for op, expected_val in operators.items():
                if not PolicyEngine._evaluate_operator(field_value, op, expected_val):
                    return False
        return True

    @staticmethod
    def _get_nested_value(data: Any, path: str) -> Any:
        """Resolve dot-notation path against a dict."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    @staticmethod
    def _evaluate_operator(actual: Any, op: str, expected: Any) -> bool:
        if op == "eq":
            return actual == expected
        elif op == "neq":
            return actual != expected
        elif op == "in":
            return isinstance(expected, list) and actual in expected
        elif op == "contains":
            if isinstance(actual, (str, list, dict)):
                return expected in actual
            return False
        elif op == "startswith":
            return (
                isinstance(actual, str)
                and isinstance(expected, str)
                and actual.startswith(expected)
            )
        elif op == "endswith":
            return (
                isinstance(actual, str)
                and isinstance(expected, str)
                and actual.endswith(expected)
            )
        elif op == "gt":
            return actual is not None and actual > expected
        elif op == "lt":
            return actual is not None and actual < expected
        elif op == "gte":
            return actual is not None and actual >= expected
        elif op == "lte":
            return actual is not None and actual <= expected
        else:
            logger.warning(f"Unknown operator: {op}")
            return False
