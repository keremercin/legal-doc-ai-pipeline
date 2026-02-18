from fastapi.testclient import TestClient

from legal_doc_ai.main import app


def test_health() -> None:
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert "service" in body
    assert "metadata" in body
