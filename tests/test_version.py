from fastapi.testclient import TestClient

from legal_doc_ai.main import app


def test_version() -> None:
    client = TestClient(app)
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok"
    assert body["data"]["version"] == "0.5.0"
    assert body["meta"]["app_version"] == "0.5.0"
    assert body["meta"]["latency_ms"] is None
    assert "model_version" not in body["meta"]


def test_retrieval_report_records_application_version_not_model_version(tmp_path, monkeypatch) -> None:
    import json

    from scripts.eval_retrieval import write_report

    monkeypatch.chdir(tmp_path)
    write_report({"recall_at_1": 0.5, "recall_at_3": 0.8, "mrr": 0.6}, [], total_queries=2)
    metrics = json.loads((tmp_path / "reports" / "metrics.json").read_text(encoding="utf-8"))

    assert metrics["app_version"] == "0.5.0"
    assert "model_version" not in metrics
