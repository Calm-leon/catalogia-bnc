from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.image import PipelineImageResult
from app.storage import StoredFile


client = TestClient(app)


@dataclass
class _MemState:
    job_id: int = 500
    file_id: int = 1000
    log_id: int = 2000

    def __post_init__(self):
        self.jobs = {}
        self.files = []
        self.logs = []


def _now():
    return datetime.now(timezone.utc)


def test_mvp_cataloger_flow_e2e(monkeypatch):
    state = _MemState()

    async def _insert_job(status, source_filename, user_id):
        state.job_id += 1
        now = _now()
        state.jobs[state.job_id] = {
            "id": state.job_id,
            "status": status,
            "source_filename": source_filename,
            "user_id": user_id,
            "created_at": now,
            "updated_at": now,
        }
        return state.job_id

    async def _update_job_status(job_id, status):
        if job_id not in state.jobs:
            return False
        state.jobs[job_id]["status"] = status
        state.jobs[job_id]["updated_at"] = _now()
        return True

    async def _insert_log(level, message, job_id, user_id, metadata):
        state.log_id += 1
        state.logs.append(
            {
                "id": state.log_id,
                "level": level,
                "message": message,
                "job_id": job_id,
                "user_id": user_id,
                "metadata": metadata,
                "created_at": _now(),
            }
        )
        return state.log_id

    async def _insert_file(
        storage_type,
        original_name,
        stored_name,
        relative_path,
        content_type,
        size_bytes,
        job_id,
        user_id,
    ):
        state.file_id += 1
        state.files.append(
            {
                "id": state.file_id,
                "storage_type": storage_type,
                "original_name": original_name,
                "stored_name": stored_name,
                "relative_path": relative_path,
                "content_type": content_type,
                "size_bytes": size_bytes,
                "job_id": job_id,
                "user_id": user_id,
                "created_at": _now(),
            }
        )
        return state.file_id

    async def _job_exists(job_id):
        return job_id in state.jobs

    async def _upsert_file_for_job(
        storage_type,
        original_name,
        stored_name,
        relative_path,
        content_type,
        size_bytes,
        job_id,
        user_id,
    ):
        for existing in state.files:
            if (
                existing["job_id"] == job_id
                and existing["storage_type"] == storage_type
                and existing["stored_name"] == stored_name
            ):
                existing["relative_path"] = relative_path
                existing["size_bytes"] = size_bytes
                return existing["id"]
        return await _insert_file(
            storage_type=storage_type,
            original_name=original_name,
            stored_name=stored_name,
            relative_path=relative_path,
            content_type=content_type,
            size_bytes=size_bytes,
            job_id=job_id,
            user_id=user_id,
        )

    async def _count_jobs(status=None):
        jobs = list(state.jobs.values())
        if status:
            jobs = [item for item in jobs if item["status"] == status]
        return len(jobs)

    async def _list_jobs(limit, offset, status=None):
        jobs = list(state.jobs.values())
        if status:
            jobs = [item for item in jobs if item["status"] == status]
        jobs.sort(key=lambda item: (item["created_at"], item["id"]), reverse=True)
        return jobs[offset : offset + limit]

    async def _get_job(job_id):
        return state.jobs.get(job_id)

    async def _list_job_logs(job_id):
        logs = [item for item in state.logs if item["job_id"] == job_id]
        logs.sort(key=lambda item: (item["created_at"], item["id"]))
        return logs

    async def _list_job_files(job_id):
        files = [item for item in state.files if item["job_id"] == job_id]
        files.sort(key=lambda item: (item["created_at"], item["id"]))
        return files

    async def _get_latest_xml_file_for_job(job_id):
        xmls = [
            item
            for item in state.files
            if item["job_id"] == job_id and item["storage_type"] == "xml"
        ]
        xmls.sort(key=lambda item: (item["created_at"], item["id"]), reverse=True)
        return xmls[0] if xmls else None

    async def _run_image_pipeline(*_args, **_kwargs):
        return PipelineImageResult(
            image_file=StoredFile(
                storage_type="images",
                original_name="input.jpg",
                stored_name="input-stored.jpg",
                relative_path="images/2026/02/26/input-stored.jpg",
                content_type="image/jpeg",
                size_bytes=10,
            ),
            xml_file=StoredFile(
                storage_type="xml",
                original_name="input-stored.jpg.xml",
                stored_name="output.xml",
                relative_path="xml/2026/02/26/output.xml",
                content_type="application/xml",
                size_bytes=100,
            ),
            xml_content=(
                '<?xml version="1.0" encoding="utf-8"?>\n'
                '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" '
                'xmlns:dc="http://purl.org/dc/elements/1.1/">'
                "<rdf:Description>"
                "<dc:title>Titulo</dc:title><dc:type>Image</dc:type>"
                "<dc:format>image/jpeg</dc:format>"
                "<dc:description>Descripcion</dc:description>"
                "</rdf:Description></rdf:RDF>"
            ),
        )

    def _save_bytes_at_relative_path(*_args, **kwargs):
        relative_path = kwargs["relative_path"]
        return StoredFile(
            storage_type="xml",
            original_name=Path(relative_path).name,
            stored_name=Path(relative_path).name,
            relative_path=relative_path,
            content_type="application/xml",
            size_bytes=120,
        )

    monkeypatch.setattr("app.db.insert_job", _insert_job)
    monkeypatch.setattr("app.db.update_job_status", _update_job_status)
    monkeypatch.setattr("app.db.insert_log", _insert_log)
    monkeypatch.setattr("app.db.insert_file", _insert_file)
    monkeypatch.setattr("app.db.job_exists", _job_exists)
    monkeypatch.setattr("app.db.upsert_file_for_job", _upsert_file_for_job)
    monkeypatch.setattr("app.db.count_jobs", _count_jobs)
    monkeypatch.setattr("app.db.list_jobs", _list_jobs)
    monkeypatch.setattr("app.db.get_job", _get_job)
    monkeypatch.setattr("app.db.list_job_logs", _list_job_logs)
    monkeypatch.setattr("app.db.list_job_files", _list_job_files)
    monkeypatch.setattr("app.db.get_latest_xml_file_for_job", _get_latest_xml_file_for_job)
    monkeypatch.setattr("app.main.run_image_pipeline", _run_image_pipeline)
    monkeypatch.setattr("app.metrics.record_pipeline_run", lambda *_args, **_kwargs: None)
    monkeypatch.setattr("app.storage.save_bytes_at_relative_path", _save_bytes_at_relative_path)
    monkeypatch.setattr(
        "app.main.evaluate_xml_quality_from_relative_path",
        lambda _path: {
            "passed": True,
            "score": 100,
            "checks": [{"key": "required_type", "passed": True, "detail": "ok"}],
        },
    )
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")
    monkeypatch.setenv("VIEWER_TOKEN", "test-viewer-token")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")

    # auth checks
    no_token = client.post(
        "/internal/pipeline/image",
        files={"file": ("input.jpg", b"img", "image/jpeg")},
        data={"storage_type": "images"},
    )
    assert no_token.status_code == 401

    viewer_forbidden = client.post(
        "/internal/pipeline/image",
        files={"file": ("input.jpg", b"img", "image/jpeg")},
        data={"storage_type": "images"},
        headers={"Authorization": "Bearer test-viewer-token"},
    )
    assert viewer_forbidden.status_code == 403

    # 1) authenticate -> upload -> generate
    upload_response = client.post(
        "/internal/pipeline/image",
        files={"file": ("input.jpg", b"img", "image/jpeg")},
        data={"storage_type": "images", "creator": "Catalogador"},
        headers={"Authorization": "Bearer test-cataloger-token"},
    )
    assert upload_response.status_code == 200
    upload_body = upload_response.json()
    job_id = upload_body["job_id"]
    assert upload_body["job_status"] == "completed"

    # 2) edit -> save (review endpoint)
    review_response = client.post(
        "/internal/pipeline/image/review",
        json={
            "job_id": job_id,
            "xml_relative_path": upload_body["xml_relative_path"],
            "title": "Titulo revisado",
            "creator": "Catalogador",
            "date": "2026-02-26",
            "format": "image/jpeg",
            "description": "Descripcion revisada",
        },
        headers={"Authorization": "Bearer test-cataloger-token"},
    )
    assert review_response.status_code == 200

    # 3) consult history
    jobs_response = client.get(
        "/internal/jobs?limit=20&offset=0&include_quality=true",
        headers={"Authorization": "Bearer test-cataloger-token"},
    )
    assert jobs_response.status_code == 200
    jobs_body = jobs_response.json()
    assert jobs_body["total"] >= 1
    assert jobs_body["jobs"][0]["id"] == job_id

    # 4) consult detail
    detail_response = client.get(
        f"/internal/jobs/{job_id}?include_quality=true",
        headers={"Authorization": "Bearer test-cataloger-token"},
    )
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert detail["job"]["id"] == job_id
    assert len(detail["files"]) >= 2
    assert any(log["message"] == "pipeline_image_completed" for log in detail["logs"])
    assert detail["job"]["quality"]["score"] == 100

