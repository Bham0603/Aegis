import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.gateway import DecisionEnum
from app.schemas.policy import PolicyCreate
from app.services.policy_service import PolicyService


@pytest.mark.asyncio
async def test_evaluate_endpoint_success(async_client: AsyncClient, db: AsyncSession):
    # Setup allow policy for the tool
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

    payload = {
        "agent_id": "agt_1",
        "session_id": "ses_1",
        "tool_id": "web.search",
        "operation": "read",
        "parameters": {"query": "security best practices"},
    }
    response = await async_client.post("/api/v1/actions/evaluate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "action_id" in data
    assert "correlation_id" in data
    assert data["decision"] == DecisionEnum.ALLOW.value


@pytest.mark.asyncio
async def test_evaluate_endpoint_missing_identity(async_client: AsyncClient):
    payload = {
        "tool_id": "web.search",
        "operation": "read",
    }
    response = await async_client.post("/api/v1/actions/evaluate", json=payload)
    # Pydantic should catch missing agent_id and session_id
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_evaluate_endpoint_unknown_tool_is_blocked(async_client: AsyncClient, db: AsyncSession):
    payload = {
        "agent_id": "agt_1",
        "session_id": "ses_1",
        "tool_id": "malicious.tool",
    }
    response = await async_client.post("/api/v1/actions/evaluate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["decision"] == DecisionEnum.BLOCK.value
    assert "Default Deny" in data["reasons"][0]

