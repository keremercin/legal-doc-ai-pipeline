from pathlib import Path

import requests

API = "http://localhost:8000"

samples = {
    "demo_contract.txt": (
        "This agreement is made between Party A and Party B. "
        "The obligations include confidentiality and delivery schedule."
    ),
    "demo_invoice.txt": "Invoice total amount due is 4000 USD. Payment terms are Net 15.",
    "demo_litigation.txt": "The plaintiff filed a lawsuit in district court for breach of contract.",
}


def upload_file(path: Path) -> None:
    with path.open("rb") as f:
        r = requests.post(f"{API}/v1/ingest", files={"file": (path.name, f, "text/plain")}, timeout=30)
    print(path.name, r.status_code, r.text)


def demo_query(q: str) -> None:
    r = requests.post(f"{API}/v1/retrieve", json={"query": q, "top_k": 3}, timeout=30)
    print("\nQuery:", q)
    print(r.status_code, r.text)


if __name__ == "__main__":
    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    for fname, text in samples.items():
        p = data_dir / fname
        p.write_text(text, encoding="utf-8")
        upload_file(p)

    demo_query("contract parties confidentiality")
    demo_query("invoice payment terms")
    demo_query("lawsuit court plaintiff")
