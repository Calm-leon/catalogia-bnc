from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_ok(monkeypatch):
    async def _check_db():
        return True

    monkeypatch.setattr("app.db.check_db", _check_db)

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "db": "ok"}