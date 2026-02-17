from fastapi.testclient import TestClient

from app.main import app
from app.pipeline.image import PipelineImageResult
from app.storage import StoredFile


client = TestClient(app)


def _fake_pipeline_result() -> PipelineImageResult:
    return PipelineImageResult(
        image_file=StoredFile(
            storage_type="images",
            original_name="input.jpg",
            stored_name="input-stored.jpg",
            relative_path="images/2026/02/13/input-stored.jpg",
            content_type="image/jpeg",
            size_bytes=12,
        ),
        xml_file=StoredFile(
            storage_type="xml",
            original_name="input-stored.jpg.xml",
            stored_name="output.xml",
            relative_path="xml/2026/02/13/output.xml",
            content_type="application/xml",
            size_bytes=50,
        ),
        xml_content="<dc:title>input.jpg</dc:title>",
    )


def test_pipeline_image_success_creates_and_completes_job(monkeypatch):
    states: list[str] = []
    inserted_files: list[dict] = []
    inserted_logs: list[dict] = []

    async def _insert_job(*_args, **_kwargs):
        return 77

    async def _update_job_status(job_id: int, status: str):
        assert job_id == 77
        states.append(status)
        return True

    async def _insert_log(*_args, **kwargs):
        inserted_logs.append(kwargs)
        return len(inserted_logs)

    async def _insert_file(*_args, **kwargs):
        inserted_files.append(kwargs)
        return len(inserted_files)

    async def _run_image_pipeline(*_args, **_kwargs):
        return _fake_pipeline_result()

    monkeypatch.setattr("app.db.insert_job", _insert_job)
    monkeypatch.setattr("app.db.update_job_status", _update_job_status)
    monkeypatch.setattr("app.db.insert_log", _insert_log)
    monkeypatch.setattr("app.db.insert_file", _insert_file)
    monkeypatch.setattr("app.main.run_image_pipeline", _run_image_pipeline)
    monkeypatch.setattr("app.metrics.record_pipeline_run", lambda *_args, **_kwargs: None)
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")

    response = client.post(
        "/internal/pipeline/image",
        files={"file": ("input.jpg", b"test-bytes", "image/jpeg")},
        data={"storage_type": "images", "creator": "Tester"},
        headers={"Authorization": "Bearer test-cataloger-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["job_id"] == 77
    assert body["job_status"] == "completed"
    assert body["image_file_id"] == 1
    assert body["xml_file_id"] == 2
    assert states == ["running", "completed"]
    assert {item["job_id"] for item in inserted_files} == {77}
    assert {item["job_id"] for item in inserted_logs} == {77}


def test_pipeline_image_failure_marks_job_failed_and_logs(monkeypatch):
    states: list[str] = []
    inserted_logs: list[dict] = []

    async def _insert_job(*_args, **_kwargs):
        return 88

    async def _update_job_status(job_id: int, status: str):
        assert job_id == 88
        states.append(status)
        return True

    async def _insert_log(*_args, **kwargs):
        inserted_logs.append(kwargs)
        return len(inserted_logs)

    async def _run_image_pipeline(*_args, **_kwargs):
        raise RuntimeError("pipeline explosion")

    monkeypatch.setattr("app.db.insert_job", _insert_job)
    monkeypatch.setattr("app.db.update_job_status", _update_job_status)
    monkeypatch.setattr("app.db.insert_log", _insert_log)
    monkeypatch.setattr("app.main.run_image_pipeline", _run_image_pipeline)
    monkeypatch.setattr("app.metrics.record_pipeline_run", lambda *_args, **_kwargs: None)
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")

    response = client.post(
        "/internal/pipeline/image",
        files={"file": ("input.jpg", b"test-bytes", "image/jpeg")},
        data={"storage_type": "images"},
        headers={"Authorization": "Bearer test-cataloger-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "pipeline explosion"
    assert states == ["running", "failed"]
    assert inserted_logs[-1]["message"] == "pipeline_image_failed"
    assert inserted_logs[-1]["job_id"] == 88
