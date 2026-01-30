import os
from typing import Optional

import asyncpg

_pool: Optional[asyncpg.Pool] = None


def _database_url() -> str:
    return os.getenv("DATABASE_URL", "")


async def init_pool() -> None:
    global _pool
    database_url = _database_url()
    if not database_url:
        return
    _pool = await asyncpg.create_pool(dsn=database_url, min_size=1, max_size=5)


async def close_pool() -> None:
    global _pool
    if _pool is None:
        return
    await _pool.close()
    _pool = None


async def check_db() -> bool:
    if _pool is None:
        return False
    async with _pool.acquire() as connection:
        value = await connection.fetchval("SELECT 1")
        return value == 1