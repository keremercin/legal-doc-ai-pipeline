from pathlib import Path

import requests

API = "http://localhost:8000"


def check_health() -> None:
    r = requests.get(f"{API}/health", timeout=10)
    r.raise_for_status()
    print("health:", r.json())


def ingest_sample() -> None:
    sample = Path("data/smoke_contract.txt")
    sample.parent.mkdir(parents=True, exist_ok=True)
    sample.write_text(
        "This agreement is between Party A and Party B. Party A shall pay USD 3000 in 15 days.",
        encoding="utf-8",
    )

    with sample.open("rb") as f:
        r = requests.post(f"{API}/v1/ingest", files={"file": (sample.name, f, "text/plain")}, timeout=20)
    r.raise_for_status()
    print("ingest:", r.json())


def retrieve() -> None:
    r = requests.post(
        f"{API}/v1/retrieve",
        json={"query": "payment obligation in agreement", "top_k": 3},
        timeout=20,
    )
    r.raise_for_status()
    body = r.json()
    assert body["results"], "retrieve returned no hits"
    print("retrieve top1:", body["results"][0])




def qa() -> None:
    r = requests.post(
        f"{API}/v1/qa",
        json={"question": "What does Party A need to pay and by when?", "top_k": 3},
        timeout=25,
    )
    r.raise_for_status()
    body = r.json()
    assert body.get("answer")
    assert isinstance(body.get("citations"), list)
    print("qa:", body)

def analyze() -> None:
    text = "Party A shall pay USD 3000 by 12/03/2026 and maintain confidentiality."
    r = requests.post(f"{API}/v1/analyze", json={"text": text}, timeout=25)
    r.raise_for_status()
    body = r.json()
    assert "classification" in body
    assert "entities" in body
    print("analyze:", body)


if __name__ == "__main__":
    check_health()
    ingest_sample()
    retrieve()
    qa()
    analyze()
    print("E2E smoke test passed ✅")
