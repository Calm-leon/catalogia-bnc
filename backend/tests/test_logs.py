from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_log_creation(monkeypatch):
    async def _insert_log(*_args, **_kwargs):
        return 123

    monkeypatch.setattr("app.db.insert_log", _insert_log)

    payload = {
        "level": "info",
        "message": "test",
        "job_id": None,
        "user_id": None,
        "metadata": {"source": "pytest"},
    }

    response = client.post("/internal/logs", json=payload)
    assert response.status_code == 200
    assert response.json()["id"] == 123
    assert response.json()["status"] == "created"