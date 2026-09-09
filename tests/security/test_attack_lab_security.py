import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.attack_lab import AttackRunStatus
from app.services.attack_lab.runner import AttackRunner


@pytest.mark.asyncio
async def test_attack_lab_api_no_scenario_injection(async_client: AsyncClient):
    """
    SECURITY BOUNDARY TESTING & RESULT INTEGRITY
    Verify that an attacker cannot inject malicious scenario definitions
    or falsify expected results via the API.
    """
    malicious_payload = {
        "scenario_id": "direct_prompt_injection_01",
        "expected_result": "BLOCK",
        "actual_result": "BLOCK",
        "status": "PASS",
        "synthetic_inputs": {"tool_id": "__import__('os').system('echo VULNERABLE')"},
    }
    response = await async_client.post(
        "/api/v1/attack-lab/runs", json=malicious_payload
    )
    assert response.status_code == 200
    data = response.json()

    # The API should completely ignore the injected fields and run the registered scenario
    # The actual outcome for direct_prompt_injection_01 is currently ALLOW due to limitations
    assert data["expected_outcome"] == "ALLOW"
    assert data["status"] == AttackRunStatus.PASS.value

    # Verify the injected fields were not returned / did not overwrite the real run result
    assert data["actual_outcome"] == "ALLOW"


@pytest.mark.asyncio
async def test_attack_lab_api_invalid_scenario(async_client: AsyncClient):
    """
    API SECURITY
    Verify nonexistent scenario handling and malformed requests.
    """
    response = await async_client.post(
        "/api/v1/attack-lab/runs", json={"scenario_id": "nonexistent_scenario"}
    )
    assert response.status_code == 404

    # Missing scenario_id
    response = await async_client.post(
        "/api/v1/attack-lab/runs", json={"other": "field"}
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_attack_lab_resource_limits(async_client: AsyncClient):
    """
    RESOURCE LIMITS
    Ensure no easy local DoS through massive payloads.
    """
    huge_scenario_id = "A" * 1000000
    response = await async_client.post(
        "/api/v1/attack-lab/runs", json={"scenario_id": huge_scenario_id}
    )
    # Should safely fail validation or return 404/422 without crashing
    assert response.status_code in [404, 422, 413]


@pytest.mark.asyncio
async def test_attack_lab_reproducibility(db: AsyncSession):
    """
    REPRODUCIBILITY
    Run the same scenario multiple times with identical configuration.
    Verify the meaningful security outcome is identical.
    """
    runner = AttackRunner(db)
    scenario_id = "tool_misuse_unauthorized_01"

    outcomes = []
    for _ in range(5):
        res = await runner.run(scenario_id)
        outcomes.append((res.actual_outcome, res.status))

    assert len(set(outcomes)) == 1, "Scenario execution is non-deterministic"
    assert outcomes[0][0] == "BLOCK"
    assert outcomes[0][1] == AttackRunStatus.PASS


@pytest.mark.asyncio
async def test_attack_lab_isolation(db: AsyncSession):
    """
    ISOLATION TESTING
    Verify scenario A state does not leak into scenario B.
    """
    runner = AttackRunner(db)

    # Run scenario A
    res_a1 = await runner.run("tool_misuse_unauthorized_01")
    assert res_a1.actual_outcome == "BLOCK"

    # Run scenario B
    res_b = await runner.run("direct_prompt_injection_01")
    assert res_b.actual_outcome == "ALLOW"  # expected behavior due to limitations

    # Run scenario A again to ensure B didn't pollute A's state or the policy engine
    res_a2 = await runner.run("tool_misuse_unauthorized_01")
    assert res_a2.actual_outcome == "BLOCK"


@pytest.mark.asyncio
async def test_attack_lab_audit_traceability(async_client: AsyncClient):
    """
    AUDIT TRACEABILITY
    Verify the full chain: Attack Run -> Action -> Permission -> Trust -> Policy -> Risk -> Threat -> Final Decision -> Audit Event(s).
    """
    scenario_id = "tool_misuse_unauthorized_01"
    run_response = await async_client.post(
        "/api/v1/attack-lab/runs", json={"scenario_id": scenario_id}
    )
    assert run_response.status_code == 200
    run_data = run_response.json()
    run_id = run_data["run_id"]

    events_response = await async_client.get(f"/api/v1/attack-lab/runs/{run_id}/events")
    assert events_response.status_code == 200
    events = events_response.json()

    # Ensure at least the evaluation event exists
    assert len(events) >= 1
    eval_event = next(
        (e for e in events if e["event_type"] == "ACTION_EVALUATED"), None
    )
    assert eval_event is not None

    # Verify provenance details in the event payload
    assert "permission_result" in eval_event
    assert "trust_result" in eval_event
    assert "policy_result" in eval_event
    assert "risk_score" in eval_event
    assert "threat_severity" in eval_event
    assert "final_decision" in eval_event

    assert eval_event["final_decision"] == "BLOCK"
