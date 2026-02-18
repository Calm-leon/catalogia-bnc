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


async def insert_log(
    level: str,
    message: str,
    job_id: Optional[int],
    user_id: Optional[int],
    metadata: Dict[str, Any],
) -> int:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    metadata_json = json.dumps(metadata)
    async with _pool.acquire() as connection:
        return await connection.fetchval(
            """
            INSERT INTO logs (level, message, job_id, user_id, metadata)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            level,
            message,
            job_id,
            user_id,
            metadata_json,
        )


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


async def insert_job(
    status: str,
    source_filename: Optional[str],
    user_id: Optional[int],
) -> int:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with _pool.acquire() as connection:
        return await connection.fetchval(
            """
            INSERT INTO jobs (status, source_filename, user_id)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            status,
            source_filename,
            user_id,
        )


async def update_job_status(job_id: int, status: str) -> bool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with _pool.acquire() as connection:
        updated_id = await connection.fetchval(
            """
            UPDATE jobs
            SET status = $2, updated_at = NOW()
            WHERE id = $1
            RETURNING id
            """,
            job_id,
            status,
        )
        return updated_id is not None


async def job_exists(job_id: int) -> bool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with _pool.acquire() as connection:
        found = await connection.fetchval("SELECT id FROM jobs WHERE id = $1", job_id)
        return found is not None


async def upsert_file_for_job(
    storage_type: str,
    original_name: str,
    stored_name: str,
    relative_path: str,
    content_type: Optional[str],
    size_bytes: int,
    job_id: int,
    user_id: Optional[int],
) -> int:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    async with _pool.acquire() as connection:
        existing_id = await connection.fetchval(
            """
            SELECT id
            FROM files
            WHERE job_id = $1
              AND storage_type = $2
              AND stored_name = $3
            LIMIT 1
            """,
            job_id,
            storage_type,
            stored_name,
        )
        if existing_id is None:
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
        return await connection.fetchval(
            """
            UPDATE files
            SET
                original_name = $2,
                relative_path = $3,
                content_type = $4,
                size_bytes = $5,
                user_id = $6,
                created_at = NOW()
            WHERE id = $1
            RETURNING id
            """,
            existing_id,
            original_name,
            relative_path,
            content_type,
            size_bytes,
            user_id,
        )
