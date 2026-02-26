from fastapi.testclient import TestClient

from app.main import app
from app.rate_limit import reset_rate_limit_state


client = TestClient(app)


def test_security_headers_enabled(monkeypatch):
    monkeypatch.setenv("SECURITY_HEADERS_ENABLED", "true")

    async def _check_db():
        return True

    monkeypatch.setattr("app.db.check_db", _check_db)

    response = client.get("/health")
    assert response.status_code in {200, 503}
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("referrer-policy") == "no-referrer"
    assert response.headers.get("content-security-policy")


def test_rate_limit_logs_endpoint(monkeypatch):
    reset_rate_limit_state()

    async def _insert_log(*_args, **_kwargs):
        return 1

    monkeypatch.setattr("app.db.insert_log", _insert_log)
    monkeypatch.setenv("CATALOGER_TOKEN", "test-cataloger-token")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("RATE_LIMIT_WINDOW_SECONDS", "60")
    monkeypatch.setenv("RATE_LIMIT_LOGS_PER_MINUTE", "1")

    payload = {
        "level": "info",
        "message": "test",
        "job_id": None,
        "user_id": None,
        "metadata": {"source": "pytest"},
    }
    headers = {"Authorization": "Bearer test-cataloger-token"}

    first = client.post("/internal/logs", json=payload, headers=headers)
    second = client.post("/internal/logs", json=payload, headers=headers)

    assert first.status_code == 200
    assert second.status_code == 429
