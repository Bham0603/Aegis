from datetime import UTC, datetime

import pytest

from app.domain.action import Action
from app.models.policy import Policy, PolicyStatus
from app.services.policy_engine import PolicyEngine


@pytest.fixture
def sample_action():
    return Action(
        action_id="act-123",
        correlation_id="corr-456",
        timestamp=datetime.now(UTC),
        agent_id="agent-007",
        session_id="session-001",
        tool_id="filesystem.read",
        operation="read",
        parameters={"path": "/etc/passwd"},
        environment="production",
    )


def test_engine_empty_policies_defaults_to_block(sample_action):
    result = PolicyEngine.evaluate(sample_action, [], {})
    assert result["final_effect"] == "BLOCK"
    assert result["default_deny"] is True
    assert len(result["matched_rules"]) == 0


def test_engine_matches_allow_policy(sample_action):
    p1 = Policy(
        id="policy-1",
        name="Allow Safe Read",
        status=PolicyStatus.ACTIVE,
        priority=10,
        rules=[
            {
                "effect": "ALLOW",
                "condition": {
                    "tool_id": {"eq": "filesystem.read"},
                    "parameters.path": {"startswith": "/var/log"},
                },
            }
        ],
    )
    # This shouldn't match because path is /etc/passwd
    res1 = PolicyEngine.evaluate(sample_action, [p1], {})
    assert res1["final_effect"] == "BLOCK"

    p2 = Policy(
        id="policy-2",
        name="Allow Any Read",
        status=PolicyStatus.ACTIVE,
        priority=10,
        rules=[
            {"effect": "ALLOW", "condition": {"tool_id": {"eq": "filesystem.read"}}}
        ],
    )
    res2 = PolicyEngine.evaluate(sample_action, [p2], {})
    assert res2["final_effect"] == "ALLOW"
    assert len(res2["matched_rules"]) == 1


def test_engine_block_overrides_allow(sample_action):
    p1 = Policy(
        id="policy-allow",
        name="Allow Any Read",
        status=PolicyStatus.ACTIVE,
        priority=10,
        rules=[
            {"effect": "ALLOW", "condition": {"tool_id": {"eq": "filesystem.read"}}}
        ],
    )
    p2 = Policy(
        id="policy-block",
        name="Block ETC",
        status=PolicyStatus.ACTIVE,
        priority=20,
        rules=[
            {
                "effect": "BLOCK",
                "condition": {"parameters.path": {"startswith": "/etc/"}},
            }
        ],
    )
    result = PolicyEngine.evaluate(sample_action, [p1, p2], {})
    assert result["final_effect"] == "BLOCK"
    assert len(result["matched_rules"]) == 2


def test_engine_review_overrides_allow(sample_action):
    p1 = Policy(
        id="policy-allow",
        name="Allow Any Read",
        status=PolicyStatus.ACTIVE,
        priority=10,
        rules=[
            {"effect": "ALLOW", "condition": {"tool_id": {"eq": "filesystem.read"}}}
        ],
    )
    p2 = Policy(
        id="policy-review",
        name="Review ETC",
        status=PolicyStatus.ACTIVE,
        priority=20,
        rules=[
            {
                "effect": "REVIEW",
                "condition": {"parameters.path": {"startswith": "/etc/"}},
            }
        ],
    )
    result = PolicyEngine.evaluate(sample_action, [p1, p2], {})
    assert result["final_effect"] == "REVIEW"
    assert len(result["matched_rules"]) == 2


def test_engine_ignores_disabled_policies(sample_action):
    p1 = Policy(
        id="policy-allow",
        name="Allow Any Read",
        status=PolicyStatus.DISABLED,
        priority=10,
        rules=[
            {"effect": "ALLOW", "condition": {"tool_id": {"eq": "filesystem.read"}}}
        ],
    )
    result = PolicyEngine.evaluate(sample_action, [p1], {})
    assert result["final_effect"] == "BLOCK"
    assert len(result["matched_rules"]) == 0
