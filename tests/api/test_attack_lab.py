import pytest
from httpx import AsyncClient

from app.domain.attack_lab import AttackRunStatus


@pytest.mark.asyncio
async def test_list_scenarios(async_client: AsyncClient):
    response = await async_client.get("/api/v1/attack-lab/scenarios")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 15
    assert data[0]["scenario_id"] == "direct_prompt_injection_01"


@pytest.mark.asyncio
async def test_get_scenario(async_client: AsyncClient):
    response = await async_client.get(
        "/api/v1/attack-lab/scenarios/direct_prompt_injection_01"
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == "direct_prompt_injection_01"


@pytest.mark.asyncio
async def test_get_scenario_not_found(async_client: AsyncClient):
    response = await async_client.get("/api/v1/attack-lab/scenarios/invalid_id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_run_scenario_and_get_results(async_client: AsyncClient):
    # Test one scenario end-to-end to ensure the runner works
    scenario_id = "tool_misuse_unauthorized_01"
    response = await async_client.post(
        "/api/v1/attack-lab/runs", json={"scenario_id": scenario_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["scenario_id"] == scenario_id
    assert data["status"] == AttackRunStatus.PASS.value
    run_id = data["run_id"]

    # Get run
    response_get = await async_client.get(f"/api/v1/attack-lab/runs/{run_id}")
    assert response_get.status_code == 200
    data_get = response_get.json()
    assert data_get["run_id"] == run_id

    # Get events
    response_events = await async_client.get(f"/api/v1/attack-lab/runs/{run_id}/events")
    assert response_events.status_code == 200
    events = response_events.json()
    assert len(events) >= 1  # Evaluated
