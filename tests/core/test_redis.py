import pytest

from app.core.redis import close_redis_pool, get_redis_client, init_redis_pool


@pytest.mark.asyncio
async def test_redis_initialization():
    # Attempt to initialize the pool (using the configuration from settings)
    await init_redis_pool()

    # Verify the pool yields a client successfully
    client_gen = get_redis_client()
    client = await client_gen.__anext__()

    assert client is not None

    # Close generator
    try:
        await client_gen.__anext__()
    except StopAsyncIteration:
        pass

    await close_redis_pool()
