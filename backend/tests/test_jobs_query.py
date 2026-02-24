from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def _job_row(job_id: int, status: str = "completed"):
    now = datetime.now(timezone.utc)
    return {
        "id": job_id,
        "status": status,
        "source_filename": f"file-{job_id}.jpg",
        "user_id": None,
        "created_at": now,
        "updated_at": now,
    }


def test_jobs_list_descending_and_pagination(monkeypatch):
    async def _count_jobs(status=None):
        assert status is None
        return 2

    async def _list_jobs(limit, offset, status=None):
        assert limit == 2
        assert offset == 0
        assert status is None
        return [_job_row(2), _job_row(1)]

    async def _latest_xml(job_id):
        return {"relative_path": f"xml/2026/02/19/job-{job_id}.xml"}

    monkeypatch.setattr("app.db.count_jobs", _count_jobs)
    monkeypatch.setattr("app.db.list_jobs", _list_jobs)
    monkeypatch.setattr("app.db.get_latest_xml_file_for_job", _latest_xml)
    monkeypatch.setattr(
        "app.main.evaluate_xml_quality_from_relative_path",
        lambda _path: {"passed": True, "score": 100, "checks": []},
    )
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")

    response = client.get(
        "/internal/jobs?limit=2&offset=0",
        headers={"Authorization": "Bearer test-cataloger-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["limit"] == 2
    assert payload["offset"] == 0
    assert payload["total"] == 2
    assert [item["id"] for item in payload["jobs"]] == [2, 1]
    assert payload["jobs"][0]["quality"]["score"] == 100


def test_job_detail_includes_logs_files_and_quality(monkeypatch):
    async def _get_job(job_id):
        assert job_id == 10
        return _job_row(job_id=10, status="completed")

    async def _latest_xml(job_id):
        assert job_id == 10
        return {"relative_path": "xml/2026/02/19/job-10.xml"}

    async def _logs(job_id):
        now = datetime.now(timezone.utc)
        return [
            {
                "id": 1,
                "level": "info",
                "message": "pipeline_image_completed",
                "metadata": '{"stage":"pipeline"}',
                "user_id": None,
                "created_at": now,
            }
        ]

    async def _files(job_id):
        now = datetime.now(timezone.utc)
        return [
            {
                "id": 101,
                "storage_type": "images",
                "original_name": "img.jpg",
                "stored_name": "img.jpg",
                "relative_path": "images/2026/02/19/img.jpg",
                "content_type": "image/jpeg",
                "size_bytes": 100,
                "user_id": None,
                "created_at": now,
            }
        ]

    monkeypatch.setattr("app.db.get_job", _get_job)
    monkeypatch.setattr("app.db.get_latest_xml_file_for_job", _latest_xml)
    monkeypatch.setattr("app.db.list_job_logs", _logs)
    monkeypatch.setattr("app.db.list_job_files", _files)
    monkeypatch.setattr(
        "app.main.evaluate_xml_quality_from_relative_path",
        lambda _path: {
            "passed": False,
            "score": 75,
            "checks": [{"key": "required_description", "passed": False, "detail": "x"}],
        },
    )
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")

    response = client.get(
        "/internal/jobs/10",
        headers={"Authorization": "Bearer test-cataloger-token"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["job"]["id"] == 10
    assert payload["job"]["quality"]["score"] == 75
    assert len(payload["logs"]) == 1
    assert payload["logs"][0]["message"] == "pipeline_image_completed"
    assert payload["logs"][0]["metadata"]["stage"] == "pipeline"
    assert len(payload["files"]) == 1
    assert payload["files"][0]["storage_type"] == "images"
