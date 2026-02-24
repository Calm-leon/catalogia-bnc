from enum import StrEnum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobStatus(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


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


class PipelineImageResponse(BaseModel):
    job_id: int
    job_status: JobStatus
    image_file_id: int
    xml_file_id: int
    xml_relative_path: str
    xml_content: str


class XmlRevisionRequest(BaseModel):
    job_id: int
    user_id: Optional[int] = None
    xml_relative_path: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    creator: str = Field(..., min_length=1)
    date: str = Field(..., min_length=1)
    format: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)


class XmlRevisionResponse(BaseModel):
    file_id: int
    job_id: int
    xml_relative_path: str
    xml_content: str
    status: str = "saved"


class XmlQualityCheck(BaseModel):
    key: str
    passed: bool
    detail: str


class XmlQualitySummary(BaseModel):
    passed: bool
    score: float
    checks: List[XmlQualityCheck]


class JobListItem(BaseModel):
    id: int
    status: str
    source_filename: Optional[str] = None
    user_id: Optional[int] = None
    created_at: str
    updated_at: str
    quality: Optional[XmlQualitySummary] = None


class JobListResponse(BaseModel):
    limit: int
    offset: int
    total: int
    jobs: List[JobListItem]


class JobLogItem(BaseModel):
    id: int
    level: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    user_id: Optional[int] = None
    created_at: str


class JobFileItem(BaseModel):
    id: int
    storage_type: str
    original_name: str
    stored_name: str
    relative_path: str
    content_type: Optional[str] = None
    size_bytes: int
    user_id: Optional[int] = None
    created_at: str


class JobDetailResponse(BaseModel):
    job: JobListItem
    logs: List[JobLogItem]
    files: List[JobFileItem]
