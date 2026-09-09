import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.attack_lab import AttackRunStatus
from app.services.attack_lab.runner import AttackRunner
from app.services.attack_lab.scenarios import SCENARIOS


@pytest.mark.asyncio
async def test_all_attack_scenarios(db: AsyncSession):
    """
    Executes all 10 attack scenarios and verifies they pass (actual matches expected).
    """
    runner = AttackRunner(db)

    for scenario in SCENARIOS:
        result = await runner.run(scenario.scenario_id)
        assert result.status == AttackRunStatus.PASS, (
            f"Scenario {scenario.scenario_id} failed: Expected {result.expected_outcome}, got {result.actual_outcome}. Reason: {result.explanation}"
        )
        assert result.actual_outcome == scenario.expected_security_behavior
