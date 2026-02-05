from typing import Optional

from pydantic import BaseModel


class StorageUploadResponse(BaseModel):
    id: int
    relative_path: str
    stored_name: str
    size_bytes: int
    content_type: Optional[str] = None