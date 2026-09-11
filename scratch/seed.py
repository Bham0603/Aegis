import asyncio
import hashlib

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def seed():
    engine = create_async_engine("sqlite+aiosqlite:///test.db")
    session_maker = async_sessionmaker(engine)
    api_key = "demo-key"
    api_key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    async with session_maker() as session:
        await session.execute(
            text(
                """
                INSERT INTO api_principals (id, name, principal_type, api_key_hash, roles, is_active)
                VALUES ('seed-1', 'Test Client', 'SERVICE', :api_key_hash, '["admin"]', 1)
                """
            ),
            {"api_key_hash": api_key_hash}
        )
        await session.commit()
    print("Database seeded.")

if __name__ == "__main__":
    import os
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(seed())
