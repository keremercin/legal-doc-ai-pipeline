from fastapi.testclient import TestClient

from legal_doc_ai.main import app


def test_request_id_header_is_returned() -> None:
    client = TestClient(app)
    r = client.get("/health", headers={"X-Request-Id": "req-123"})
    assert r.status_code == 200
    assert r.headers.get("x-request-id") == "req-123"
