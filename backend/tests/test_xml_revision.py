from fastapi.testclient import TestClient

from app.main import app
from app.storage import StoredFile


client = TestClient(app)


def test_xml_revision_saved_and_registered(monkeypatch):
    async def _job_exists(job_id: int):
        return job_id == 42

    def _save_bytes_at_relative_path(*_args, **kwargs):
        relative_path = kwargs["relative_path"]
        return StoredFile(
            storage_type="xml",
            original_name="source_reviewed.xml",
            stored_name="source_reviewed.xml",
            relative_path=relative_path,
            content_type="application/xml",
            size_bytes=128,
        )

    async def _upsert_file_for_job(*_args, **kwargs):
        assert kwargs["job_id"] == 42
        assert kwargs["storage_type"] == "xml"
        return 999

    async def _insert_log(*_args, **kwargs):
        assert kwargs["job_id"] == 42
        assert kwargs["message"] == "pipeline_image_review_saved"
        return 1

    monkeypatch.setattr("app.db.job_exists", _job_exists)
    monkeypatch.setattr("app.storage.save_bytes_at_relative_path", _save_bytes_at_relative_path)
    monkeypatch.setattr("app.db.upsert_file_for_job", _upsert_file_for_job)
    monkeypatch.setattr("app.db.insert_log", _insert_log)
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")

    response = client.post(
        "/internal/pipeline/image/review",
        json={
            "job_id": 42,
            "xml_relative_path": "xml/2026/02/18/source.xml",
            "title": "Nuevo titulo",
            "creator": "Catalogador",
            "date": "2026-02-18",
            "format": "image/jpeg",
            "description": "Descripcion validada",
        },
        headers={"Authorization": "Bearer test-cataloger-token"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "saved"
    assert body["file_id"] == 999
    assert body["job_id"] == 42
    assert body["xml_relative_path"].endswith("_reviewed.xml")
    assert not body["xml_relative_path"].endswith("_reviewed_reviewed.xml")


def test_xml_revision_normalizes_already_reviewed_path(monkeypatch):
    captured_path = {"value": None}

    async def _job_exists(job_id: int):
        return job_id == 42

    def _save_bytes_at_relative_path(*_args, **kwargs):
        relative_path = kwargs["relative_path"]
        captured_path["value"] = relative_path
        return StoredFile(
            storage_type="xml",
            original_name="source_reviewed.xml",
            stored_name="source_reviewed.xml",
            relative_path=relative_path,
            content_type="application/xml",
            size_bytes=128,
        )

    async def _upsert_file_for_job(*_args, **_kwargs):
        return 999

    async def _insert_log(*_args, **_kwargs):
        return 1

    monkeypatch.setattr("app.db.job_exists", _job_exists)
    monkeypatch.setattr("app.storage.save_bytes_at_relative_path", _save_bytes_at_relative_path)
    monkeypatch.setattr("app.db.upsert_file_for_job", _upsert_file_for_job)
    monkeypatch.setattr("app.db.insert_log", _insert_log)
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")

    response = client.post(
        "/internal/pipeline/image/review",
        json={
            "job_id": 42,
            "xml_relative_path": "xml/2026/02/18/source_reviewed_reviewed.xml",
            "title": "Nuevo titulo",
            "creator": "Catalogador",
            "date": "2026-02-18",
            "format": "image/jpeg",
            "description": "Descripcion validada",
        },
        headers={"Authorization": "Bearer test-cataloger-token"},
    )

    assert response.status_code == 200
    assert captured_path["value"] == "xml/2026/02/18/source_reviewed.xml"


def test_xml_revision_requires_description(monkeypatch):
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")

    response = client.post(
        "/internal/pipeline/image/review",
        json={
            "job_id": 42,
            "xml_relative_path": "xml/2026/02/18/source.xml",
            "title": "Nuevo titulo",
            "creator": "Catalogador",
            "date": "2026-02-18",
            "format": "image/jpeg",
            "description": "",
        },
        headers={"Authorization": "Bearer test-cataloger-token"},
    )

    assert response.status_code == 422
