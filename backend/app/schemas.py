from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class LogCreate(BaseModel):
    level: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    job_id: Optional[int] = None
    user_id: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LogResponse(BaseModel):
    id: int
    status: str = "created"


class StorageUploadResponse(BaseModel):
    id: int
    relative_path: str
    stored_name: str
    size_bytes: int
    content_type: Optional[str] = None