import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import UploadFile


@dataclass(frozen=True)
class StoredFile:
    storage_type: str
    original_name: str
    stored_name: str
    relative_path: str
    content_type: Optional[str]
    size_bytes: int


def _storage_base() -> Path:
    return Path(os.getenv("STORAGE_PATH", "/data"))


def _safe_segment(value: str) -> str:
    cleaned = value.strip().lower().replace(" ", "_")
    return cleaned or "unknown"


def _build_relative_path(storage_type: str, original_name: str) -> Path:
    today = datetime.utcnow()
    date_path = Path(str(today.year), f"{today.month:02d}", f"{today.day:02d}")
    safe_type = _safe_segment(storage_type)
    ext = Path(original_name).suffix
    filename = f"{uuid4().hex}{ext}"
    return Path(safe_type) / date_path / filename


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _to_relative(path: Path) -> str:
    return str(path).replace("\\", "/")


async def save_upload_file(upload: UploadFile, storage_type: str) -> StoredFile:
    data = await upload.read()
    return save_bytes(
        storage_type=storage_type,
        original_name=upload.filename or "file",
        data=data,
        content_type=upload.content_type,
    )


def save_bytes(
    storage_type: str,
    original_name: str,
    data: bytes,
    content_type: Optional[str],
) -> StoredFile:
    base = _storage_base()
    relative = _build_relative_path(storage_type, original_name)
    absolute = base / relative
    _ensure_parent(absolute)
    absolute.write_bytes(data)

    return StoredFile(
        storage_type=_safe_segment(storage_type),
        original_name=original_name,
        stored_name=absolute.name,
        relative_path=_to_relative(relative),
        content_type=content_type,
        size_bytes=len(data),
    )