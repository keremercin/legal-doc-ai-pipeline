from fastapi.testclient import TestClient

from legal_doc_ai.main import app


def test_version() -> None:
    client = TestClient(app)
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["data"]["version"] == "0.5.0"
