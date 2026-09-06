from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.action import Action
from app.domain.decision import DecisionEnum
from app.schemas.policy import PolicyCreate
from app.services.evaluator import evaluate_action
from app.services.policy_service import PolicyService


def make_action(tool_id: str, operation: str | None = None) -> Action:
    return Action(
        action_id="act_test",
        correlation_id="trace_test",
        timestamp=datetime.now(timezone.utc),
        agent_id="agt_1",
        session_id="ses_1",
        tool_id=tool_id,
        operation=operation,
    )


@pytest.mark.asyncio
async def test_evaluate_action_default_deny(db: AsyncSession):
    action = make_action("web.search", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.BLOCK
    assert "Default Deny" in decision.reasons[0]


@pytest.mark.asyncio
async def test_evaluate_action_allows_matched_policy(db: AsyncSession):
    # Create an allow policy
    svc = PolicyService(db)
    await svc.create_policy(PolicyCreate(
        name="Allow Web Search",
        priority=10,
        rules=[
            {
                "effect": "ALLOW",
                "condition": {
                    "tool_id": {"eq": "web.search"}
                }
            }
        ]
    ))

    action = make_action("web.search", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.ALLOW
    assert "Matched Policy" in decision.reasons[0]


@pytest.mark.asyncio
async def test_evaluate_action_fails_closed(monkeypatch, db: AsyncSession):
    def mock_evaluate(*args, **kwargs):
        raise ValueError("Simulated failure")

    import app.services.evaluator
    monkeypatch.setattr(app.services.evaluator.PolicyEngine, "evaluate", mock_evaluate)

    action = make_action("web.search", "read")
    decision = await evaluate_action(action, db)

    assert decision.decision == DecisionEnum.BLOCK
    assert "Fail-Closed" in decision.reasons[0]
