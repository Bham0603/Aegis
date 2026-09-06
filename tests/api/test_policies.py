import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_create_policy(async_client: AsyncClient, db: AsyncSession):
    payload = {
        "name": "Test Policy",
        "description": "Block all access",
        "priority": 100,
        "rules": [{"effect": "BLOCK", "condition": {"tool_id": {"eq": "shell"}}}],
    }
    response = await async_client.post("/api/v1/policies/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Policy"
    assert data["status"] == "ACTIVE"
    assert len(data["rules"]) == 1
    assert data["rules"][0]["effect"] == "BLOCK"

    # Test duplicate name
    response_duplicate = await async_client.post("/api/v1/policies/", json=payload)
    assert response_duplicate.status_code == 400


@pytest.mark.asyncio
async def test_read_policies(async_client: AsyncClient, db: AsyncSession):
    # Setup some policies
    for i in range(3):
        payload = {"name": f"Policy {i}", "priority": i, "rules": []}
        await async_client.post("/api/v1/policies/", json=payload)

    response = await async_client.get("/api/v1/policies/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3


@pytest.mark.asyncio
async def test_update_policy(async_client: AsyncClient, db: AsyncSession):
    payload = {"name": "Policy to Update", "priority": 10, "rules": []}
    create_response = await async_client.post("/api/v1/policies/", json=payload)
    policy_id = create_response.json()["id"]

    update_payload = {"status": "DISABLED"}
    update_response = await async_client.patch(
        f"/api/v1/policies/{policy_id}", json=update_payload
    )
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "DISABLED"


@pytest.mark.asyncio
async def test_delete_policy(async_client: AsyncClient, db: AsyncSession):
    payload = {"name": "Policy to Delete", "priority": 10, "rules": []}
    create_response = await async_client.post("/api/v1/policies/", json=payload)
    policy_id = create_response.json()["id"]

    delete_response = await async_client.delete(f"/api/v1/policies/{policy_id}")
    assert delete_response.status_code == 204

    # Verify deleted
    get_response = await async_client.get(f"/api/v1/policies/{policy_id}")
    assert get_response.status_code == 404
