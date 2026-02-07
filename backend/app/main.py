from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app import db, storage
from app.pipeline.image import run_image_pipeline
from app.schemas import LogCreate, LogResponse, PipelineImageResponse, StorageUploadResponse

app = FastAPI(title="CatalogIA")


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


@app.post("/internal/logs", response_model=LogResponse)
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


@app.post("/internal/storage/upload", response_model=StorageUploadResponse)
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


@app.post("/internal/pipeline/image", response_model=PipelineImageResponse)
async def pipeline_image(
    file: UploadFile = File(...),
    storage_type: str = Form("images"),
    creator: Optional[str] = Form(None),
    job_id: Optional[int] = Form(None),
    user_id: Optional[int] = Form(None),
) -> PipelineImageResponse:
    result = await run_image_pipeline(file, storage_type, creator=creator)
    image_file_id = await db.insert_file(
        storage_type=result.image_file.storage_type,
        original_name=result.image_file.original_name,
        stored_name=result.image_file.stored_name,
        relative_path=result.image_file.relative_path,
        content_type=result.image_file.content_type,
        size_bytes=result.image_file.size_bytes,
        job_id=job_id,
        user_id=user_id,
    )
    xml_file_id = await db.insert_file(
        storage_type=result.xml_file.storage_type,
        original_name=result.xml_file.original_name,
        stored_name=result.xml_file.stored_name,
        relative_path=result.xml_file.relative_path,
        content_type=result.xml_file.content_type,
        size_bytes=result.xml_file.size_bytes,
        job_id=job_id,
        user_id=user_id,
    )
    return PipelineImageResponse(
        image_file_id=image_file_id,
        xml_file_id=xml_file_id,
        xml_relative_path=result.xml_file.relative_path,
        xml_content=result.xml_content,
    )