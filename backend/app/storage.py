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


async def save_upload_file(upload: UploadFile, storage_type: str) -> StoredFile:
    base = _storage_base()
    relative = _build_relative_path(storage_type, upload.filename or "file")
    absolute = base / relative
    _ensure_parent(absolute)

    data = await upload.read()
    absolute.write_bytes(data)

    return StoredFile(
        storage_type=_safe_segment(storage_type),
        original_name=upload.filename or "file",
        stored_name=absolute.name,
        relative_path=str(relative).replace("\\", "/"),
        content_type=upload.content_type,
        size_bytes=len(data),
    )