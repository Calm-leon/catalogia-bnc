from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app import db

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