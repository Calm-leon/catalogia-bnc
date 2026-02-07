from dataclasses import dataclass
from typing import Optional

from fastapi import UploadFile

from app import storage
from app.storage import StoredFile


@dataclass(frozen=True)
class PipelineImageResult:
    image_file: StoredFile
    xml_file: StoredFile
    xml_content: str


def _mock_dublin_core_xml(
    title: str,
    creator: str,
    date_value: str,
    format_value: str,
) -> str:
    return (
        "<dc:title>{}</dc:title>\n"
        "<dc:creator>{}</dc:creator>\n"
        "<dc:date>{}</dc:date>\n"
        "<dc:format>{}</dc:format>\n"
    ).format(title, creator, date_value, format_value)


async def run_image_pipeline(
    upload: UploadFile,
    storage_type: str,
    creator: Optional[str] = None,
) -> PipelineImageResult:
    image_file = await storage.save_upload_file(upload, storage_type)
    xml_content = _mock_dublin_core_xml(
        title=image_file.original_name,
        creator=creator or "Desconocido",
        date_value="2026-02-05",
        format_value=image_file.content_type or "application/octet-stream",
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