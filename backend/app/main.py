from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from app import db, storage
from app.schemas import StorageUploadResponse

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
