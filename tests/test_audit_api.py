from fastapi.testclient import TestClient

from legal_doc_ai.main import app


def test_audit_endpoint_after_actions() -> None:
    client = TestClient(app)

    content = b"Agreement between Party A and Party B with payment terms."
    files = {"file": ("sample.txt", content, "text/plain")}
    r_ing = client.post("/v1/ingest", files=files)
    assert r_ing.status_code == 200

    r_ret = client.post("/v1/retrieve", json={"query": "payment terms", "top_k": 3})
    assert r_ret.status_code == 200

    r_audit = client.get("/v1/audit", params={"limit": 10})
    assert r_audit.status_code == 200
    body = r_audit.json()
    assert "events" in body
    assert len(body["events"]) >= 2
    assert body["events"][0]["action"] in {"retrieve", "ingest", "analyze", "extract", "qa"}
