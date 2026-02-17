from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from fastapi import UploadFile

from app.ai.base import DublinCoreInput
from app.ai.factory import get_ai_engine
from app import storage
from app.storage import StoredFile


@dataclass(frozen=True)
class PipelineImageResult:
    image_file: StoredFile
    xml_file: StoredFile
    xml_content: str


async def run_image_pipeline(
    upload: UploadFile,
    storage_type: str,
    creator: Optional[str] = None,
) -> PipelineImageResult:
    image_file = await storage.save_upload_file(upload, storage_type)
    current_date = datetime.now(timezone.utc).date().isoformat()
    engine = get_ai_engine()
    xml_content = engine.generate_dublin_core_xml(
        DublinCoreInput(
            title=image_file.original_name,
            creator=creator or "Desconocido",
            date_value=current_date,
            format_value=image_file.content_type or "application/octet-stream",
        )
    )
    xml_bytes = xml_content.encode("utf-8")
    xml_file = storage.save_bytes(
        storage_type="xml",
        original_name=f"{image_file.stored_name}.xml",
        data=xml_bytes,
        content_type="application/xml",
    )
    return PipelineImageResult(
        image_file=image_file,
        xml_file=xml_file,
        xml_content=xml_content,
    )
