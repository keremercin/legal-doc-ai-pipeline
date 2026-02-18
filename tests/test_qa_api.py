from fastapi.testclient import TestClient

from legal_doc_ai.main import app


def test_qa_endpoint_returns_answer_and_citations() -> None:
    client = TestClient(app)

    content = b"This agreement requires payment within 15 days and confidentiality obligations."
    files = {"file": ("sample.txt", content, "text/plain")}
    ingest = client.post("/v1/ingest", files=files)
    assert ingest.status_code == 200

    r = client.post("/v1/qa", json={"question": "What is the payment deadline?", "top_k": 3})
    assert r.status_code == 200
    body = r.json()
    data = body["data"]
    assert "answer" in data
    assert "citations" in data
    assert isinstance(data["citations"], list)
