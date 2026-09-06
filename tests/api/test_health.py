import pytest


@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

    # Verify correlation ID is injected
    assert "X-Correlation-ID" in response.headers


@pytest.mark.asyncio
async def test_version_info(async_client):
    response = await async_client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "env" in data


@pytest.mark.asyncio
async def test_correlation_id_forwarding(async_client):
    custom_id = "test-correlation-123"
    response = await async_client.get(
        "/health", headers={"X-Correlation-ID": custom_id}
    )
    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == custom_id
