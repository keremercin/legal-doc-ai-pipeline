"""Automated local demo runner.

Assumes API is running at localhost:8000.
Creates demo files, ingests them, runs retrieve/analyze/qa, and writes a markdown report.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import os

import requests

API = os.getenv("API_BASE", "http://localhost:8000")
API_KEY = os.getenv("API_KEY", "")


def _headers() -> dict:
    return {"X-API-Key": API_KEY} if API_KEY else {}


def _post(path: str, **kwargs):
    r = requests.post(f"{API}{path}", timeout=45, headers=_headers(), **kwargs)
    r.raise_for_status()
    return r.json()


def _get(path: str, **kwargs):
    r = requests.get(f"{API}{path}", timeout=30, headers=_headers(), **kwargs)
    r.raise_for_status()
    return r.json()


def main() -> None:
    out_lines: list[str] = []
    ts = datetime.now(timezone.utc).isoformat()

    out_lines += [
        "# Demo Run Report",
        "",
        f"Generated at: `{ts}`",
        "",
    ]

    health = _get("/health")
    out_lines += ["## Health", "", f"```json\n{health}\n```", ""]

    samples = {
        "demo_contract.txt": (
            "This agreement is made between Party A and Party B. "
            "Party A shall pay USD 9000 within 15 days and maintain confidentiality."
        ),
        "demo_invoice.txt": "Invoice amount due is 18000 USD. Payment terms are Net 30.",
        "demo_litigation.txt": "The plaintiff filed a lawsuit in district court alleging breach.",
    }

    data_dir = Path("data")
    data_dir.mkdir(parents=True, exist_ok=True)

    out_lines += ["## Ingestion", ""]
    for fname, text in samples.items():
        p = data_dir / fname
        p.write_text(text, encoding="utf-8")
        with p.open("rb") as f:
            resp = _post("/v1/ingest", files={"file": (p.name, f, "text/plain")})
        out_lines += [f"### {fname}", "", f"```json\n{resp}\n```", ""]

    retrieve = _post("/v1/retrieve", json={"query": "payment obligations and deadline", "top_k": 3})
    out_lines += ["## Retrieval", "", f"```json\n{retrieve}\n```", ""]

    analyze = _post(
        "/v1/analyze",
        json={
            "text": (
                "Party A shall pay USD 9000 by 12/04/2026 and keep confidentiality. "
                "Either party may terminate with 30-day notice."
            )
        },
    )
    out_lines += ["## Analyze", "", f"```json\n{analyze}\n```", ""]

    qa = _post("/v1/qa", json={"question": "What must Party A pay and by when?", "top_k": 3})
    out_lines += ["## Grounded QA", "", f"```json\n{qa}\n```", ""]

    audit = _get("/v1/audit", params={"limit": 10})
    out_lines += ["## Audit", "", f"```json\n{audit}\n```", ""]

    reports = Path("reports")
    reports.mkdir(parents=True, exist_ok=True)
    report_path = reports / "demo_run.md"
    report_path.write_text("\n".join(out_lines), encoding="utf-8")

    print(f"Demo report written: {report_path}")


if __name__ == "__main__":
    main()
