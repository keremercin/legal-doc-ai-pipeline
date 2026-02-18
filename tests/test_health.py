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
