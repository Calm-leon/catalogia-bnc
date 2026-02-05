import json
import os
from typing import Any, Dict, Optional

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


async def insert_file(
    storage_type: str,
    original_name: str,
    stored_name: str,
    relative_path: str,
    content_type: Optional[str],
    size_bytes: int,
    job_id: Optional[int],
    user_id: Optional[int],
) -> int:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with _pool.acquire() as connection:
        return await connection.fetchval(
            """
            INSERT INTO files (
                storage_type,
                original_name,
                stored_name,
                relative_path,
                content_type,
                size_bytes,
                job_id,
                user_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            storage_type,
            original_name,
            stored_name,
            relative_path,
            content_type,
            size_bytes,
            job_id,
            user_id,
        )