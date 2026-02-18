import logging
import os
from pathlib import Path
from typing import Optional
from xml.sax.saxutils import escape

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import db, metrics, storage
from app.auth import require_role
from app.observability import configure_logging
from app.pipeline.image import run_image_pipeline
from app.schemas import (
    JobStatus,
    LogCreate,
    LogResponse,
    PipelineImageResponse,
    StorageUploadResponse,
    XmlRevisionRequest,
    XmlRevisionResponse,
)
from app.security import Role

configure_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="CatalogIA")

allowed_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup() -> None:
    await db.init_pool()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await db.close_pool()


@app.get("/health")
async def health() -> JSONResponse:
    db_ok = await db.check_db()
    status = "ok" if db_ok else "degraded"
    payload = {"status": status, "db": "ok" if db_ok else "down"}
    code = 200 if db_ok else 503
    return JSONResponse(status_code=code, content=payload)


@app.post("/internal/logs", response_model=LogResponse, dependencies=[require_role(Role.ADMIN, Role.CATALOGER)])
async def create_log(payload: LogCreate) -> LogResponse:
    try:
        log_id = await db.insert_log(
            level=payload.level,
            message=payload.message,
            job_id=payload.job_id,
            user_id=payload.user_id,
            metadata=payload.metadata,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return LogResponse(id=log_id)


@app.post("/internal/storage/upload", response_model=StorageUploadResponse, dependencies=[require_role(Role.ADMIN, Role.CATALOGER)])
async def upload_storage_file(
    file: UploadFile = File(...),
    storage_type: str = Form(...),
    job_id: Optional[int] = Form(None),
    user_id: Optional[int] = Form(None),
) -> StorageUploadResponse:
    stored = await storage.save_upload_file(file, storage_type)
    file_id = await db.insert_file(
        storage_type=stored.storage_type,
        original_name=stored.original_name,
        stored_name=stored.stored_name,
        relative_path=stored.relative_path,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
        job_id=job_id,
        user_id=user_id,
    )
    return StorageUploadResponse(
        id=file_id,
        relative_path=stored.relative_path,
        stored_name=stored.stored_name,
        size_bytes=stored.size_bytes,
        content_type=stored.content_type,
    )


@app.post("/internal/pipeline/image", response_model=PipelineImageResponse, dependencies=[require_role(Role.ADMIN, Role.CATALOGER)])
async def pipeline_image(
    file: UploadFile = File(...),
    storage_type: str = Form("images"),
    creator: Optional[str] = Form(None),
    job_id: Optional[int] = Form(None),
    user_id: Optional[int] = Form(None),
) -> PipelineImageResponse:
    effective_job_id = job_id
    if effective_job_id is None:
        try:
            effective_job_id = await db.insert_job(
                status=JobStatus.QUEUED.value,
                source_filename=file.filename,
                user_id=user_id,
            )
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    try:
        job_exists = await db.update_job_status(effective_job_id, JobStatus.RUNNING.value)
        if not job_exists:
            raise HTTPException(status_code=404, detail=f"Job {effective_job_id} not found")

        await db.insert_log(
            level="info",
            message="pipeline_image_started",
            job_id=effective_job_id,
            user_id=user_id,
            metadata={
                "stage": "pipeline_image",
                "storage_type": storage_type,
                "filename": file.filename,
            },
        )

        result = await run_image_pipeline(file, storage_type, creator=creator)
        metrics.record_pipeline_run(result.xml_content)
        image_file_id = await db.insert_file(
            storage_type=result.image_file.storage_type,
            original_name=result.image_file.original_name,
            stored_name=result.image_file.stored_name,
            relative_path=result.image_file.relative_path,
            content_type=result.image_file.content_type,
            size_bytes=result.image_file.size_bytes,
            job_id=effective_job_id,
            user_id=user_id,
        )
        xml_file_id = await db.insert_file(
            storage_type=result.xml_file.storage_type,
            original_name=result.xml_file.original_name,
            stored_name=result.xml_file.stored_name,
            relative_path=result.xml_file.relative_path,
            content_type=result.xml_file.content_type,
            size_bytes=result.xml_file.size_bytes,
            job_id=effective_job_id,
            user_id=user_id,
        )

        await db.update_job_status(effective_job_id, JobStatus.COMPLETED.value)
        await db.insert_log(
            level="info",
            message="pipeline_image_completed",
            job_id=effective_job_id,
            user_id=user_id,
            metadata={
                "stage": "pipeline_image",
                "image_file_id": image_file_id,
                "xml_file_id": xml_file_id,
                "xml_relative_path": result.xml_file.relative_path,
            },
        )

        return PipelineImageResponse(
            job_id=effective_job_id,
            job_status=JobStatus.COMPLETED,
            image_file_id=image_file_id,
            xml_file_id=xml_file_id,
            xml_relative_path=result.xml_file.relative_path,
            xml_content=result.xml_content,
        )
    except HTTPException:
        raise
    except RuntimeError as exc:
        try:
            await db.update_job_status(effective_job_id, JobStatus.FAILED.value)
            await db.insert_log(
                level="error",
                message="pipeline_image_failed",
                job_id=effective_job_id,
                user_id=user_id,
                metadata={
                    "stage": "pipeline_image",
                    "error": str(exc),
                },
            )
        except RuntimeError:
            logger.exception("Failed to write pipeline failure trace", extra={"job_id": effective_job_id})
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        try:
            await db.update_job_status(effective_job_id, JobStatus.FAILED.value)
            await db.insert_log(
                level="error",
                message="pipeline_image_failed",
                job_id=effective_job_id,
                user_id=user_id,
                metadata={
                    "stage": "pipeline_image",
                    "error": str(exc),
                },
            )
        except RuntimeError:
            logger.exception("Failed to write pipeline failure trace", extra={"job_id": effective_job_id})
        raise HTTPException(status_code=500, detail="Pipeline execution failed") from exc


@app.get("/internal/metrics", dependencies=[require_role(Role.ADMIN, Role.CATALOGER)])
async def get_metrics() -> JSONResponse:
    return JSONResponse(content=metrics.export_metrics())


def _reviewed_relative_path(xml_relative_path: str) -> str:
    source = Path(xml_relative_path)
    base = source.stem
    while base.endswith("_reviewed"):
        base = base[: -len("_reviewed")]
    suffix = source.suffix or ".xml"
    return str(source.with_name(f"{base}_reviewed{suffix}")).replace("\\", "/")


def _build_reviewed_xml(payload: XmlRevisionRequest) -> str:
    return (
        "<dc:title>{}</dc:title>\n"
        "<dc:creator>{}</dc:creator>\n"
        "<dc:date>{}</dc:date>\n"
        "<dc:format>{}</dc:format>\n"
        "<dc:description>{}</dc:description>\n"
    ).format(
        escape(payload.title),
        escape(payload.creator),
        escape(payload.date),
        escape(payload.format),
        escape(payload.description),
    )


@app.post(
    "/internal/pipeline/image/review",
    response_model=XmlRevisionResponse,
    dependencies=[require_role(Role.ADMIN, Role.CATALOGER)],
)
async def review_pipeline_image(payload: XmlRevisionRequest) -> XmlRevisionResponse:
    try:
        if not await db.job_exists(payload.job_id):
            raise HTTPException(status_code=404, detail=f"Job {payload.job_id} not found")

        reviewed_xml = _build_reviewed_xml(payload)
        reviewed_relative_path = _reviewed_relative_path(payload.xml_relative_path)
        reviewed_stored = storage.save_bytes_at_relative_path(
            relative_path=reviewed_relative_path,
            original_name=Path(reviewed_relative_path).name,
            data=reviewed_xml.encode("utf-8"),
            content_type="application/xml",
        )
        file_id = await db.upsert_file_for_job(
            storage_type="xml",
            original_name=reviewed_stored.original_name,
            stored_name=reviewed_stored.stored_name,
            relative_path=reviewed_stored.relative_path,
            content_type=reviewed_stored.content_type,
            size_bytes=reviewed_stored.size_bytes,
            job_id=payload.job_id,
            user_id=payload.user_id,
        )
        await db.insert_log(
            level="info",
            message="pipeline_image_review_saved",
            job_id=payload.job_id,
            user_id=payload.user_id,
            metadata={
                "stage": "xml_review",
                "xml_relative_path": reviewed_stored.relative_path,
            },
        )
        return XmlRevisionResponse(
            file_id=file_id,
            job_id=payload.job_id,
            xml_relative_path=reviewed_stored.relative_path,
            xml_content=reviewed_xml,
        )
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
