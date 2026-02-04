from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app import db
from app.schemas import LogCreate, LogResponse

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