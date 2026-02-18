from fastapi.testclient import TestClient

from legal_doc_ai.main import app


def test_analyze_endpoint() -> None:
    client = TestClient(app)
    payload = {
        "text": (
            "This agreement is made between Party A and Party B on 12/03/2026. "
            "Party A shall pay USD 5,000 within 15 days and keep confidentiality."
        )
    }
    r = client.post("/v1/analyze", json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["classification"] in {"contract", "invoice", "litigation", "compliance", "other"}
    assert "summary" in body
    assert "entities" in body
    assert "risk_flags" in body
