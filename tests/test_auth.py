from fastapi.testclient import TestClient

from legal_doc_ai.api.auth import settings as auth_settings
from legal_doc_ai.main import app


def test_api_key_auth_when_enabled() -> None:
    old = auth_settings.api_key
    auth_settings.api_key = "secret123"
    try:
        client = TestClient(app)

        # no key -> unauthorized
        r1 = client.post("/v1/retrieve", json={"query": "x", "top_k": 1})
        assert r1.status_code == 401

        # wrong key -> unauthorized
        r2 = client.post(
            "/v1/retrieve",
            json={"query": "x", "top_k": 1},
            headers={"X-API-Key": "wrong"},
        )
        assert r2.status_code == 401

        # correct key -> success
        r3 = client.post(
            "/v1/retrieve",
            json={"query": "x", "top_k": 1},
            headers={"X-API-Key": "secret123"},
        )
        assert r3.status_code == 200
    finally:
        auth_settings.api_key = old
