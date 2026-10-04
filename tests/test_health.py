from fastapi.testclient import TestClient

from legal_doc_ai.main import app


def test_health() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "data" in body
    assert "service" in body["data"]
    assert "meta" in body
    assert body["error"] is None


def test_memory_health_never_contacts_postgres(monkeypatch):
    from legal_doc_ai.api import routes
    monkeypatch.setattr(routes.settings, 'retriever_backend', 'memory')
    def unexpected_connection():
        raise AssertionError('Memory health must not require PostgreSQL')
    monkeypatch.setattr(routes, 'test_db_connection', unexpected_connection)
    response = TestClient(app).get('/health')
    assert response.status_code == 200
    assert response.json()['data']['db_connected'] is False
