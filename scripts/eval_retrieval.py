import json
from datetime import datetime, timezone
from pathlib import Path

from legal_doc_ai.api.response import APP_VERSION
from legal_doc_ai.services.vector_store import InMemoryVectorStore


def reciprocal_rank(expected: str, ranked_labels: list[str]) -> float:
    for i, label in enumerate(ranked_labels, start=1):
        if label == expected:
            return 1.0 / i
    return 0.0


def write_report(metrics: dict[str, float], details: list[dict], total_queries: int) -> None:
    out_dir = Path("reports")
    out_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.now(timezone.utc).isoformat()

    benchmark_lines = [
        "# Retrieval Benchmark Report",
        "",
        f"Generated at: `{ts}`",
        "",
        "## Metrics",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Recall@1 | {metrics['recall_at_1']:.2f} |",
        f"| Recall@3 | {metrics['recall_at_3']:.2f} |",
        f"| MRR | {metrics['mrr']:.2f} |",
        "",
        "## Query-level details",
        "",
        "| Query | Expected | Top Labels | Hit@1 |",
        "|---|---|---|---:|",
    ]
    for row in details:
        labels = ", ".join(row["labels"]) if row["labels"] else "-"
        benchmark_lines.append(
            f"| {row['query']} | {row['expected']} | {labels} | {int(row['hit1'])} |"
        )

    (out_dir / "benchmark.md").write_text("\n".join(benchmark_lines), encoding="utf-8")

    metrics_payload = {
        "schema_version": "1.0",
        "project": "legal-doc-ai-pipeline",
        "app_version": APP_VERSION,
        "generated_at": ts,
        "dataset": {
            "path": "data/eval/retrieval_eval.json",
            "total_queries": total_queries,
        },
        "metrics": {
            "recall_at_1": round(metrics["recall_at_1"], 4),
            "recall_at_3": round(metrics["recall_at_3"], 4),
            "mrr": round(metrics["mrr"], 4),
        },
        "details": details,
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")


def main() -> None:
    data_path = Path("data/eval/retrieval_eval.json")
    rows = json.loads(data_path.read_text(encoding="utf-8"))

    store = InMemoryVectorStore()
    queries: list[tuple[str, str]] = []

    for i, row in enumerate(rows):
        store.add_document(
            filename=f"sample_{i}.txt",
            classification=row["label"],
            full_text=row["text"],
            chunks=[row["text"]],
        )
        for q in row.get("queries", []):
            queries.append((q, row["label"]))

    hit_at_1 = 0
    hit_at_3 = 0
    rr_total = 0.0
    details: list[dict] = []

    for q, expected in queries:
        hits = store.search(q, top_k=3)
        labels = [h.metadata.get("classification", "") for h in hits]

        h1 = bool(labels and labels[0] == expected)
        if h1:
            hit_at_1 += 1
        if expected in labels[:3]:
            hit_at_3 += 1

        rr_total += reciprocal_rank(expected, labels)
        details.append({"query": q, "expected": expected, "labels": labels, "hit1": h1})

    n = len(queries) or 1
    metrics = {
        "recall_at_1": hit_at_1 / n,
        "recall_at_3": hit_at_3 / n,
        "mrr": rr_total / n,
    }

    print(f"Recall@1: {metrics['recall_at_1']:.2f}")
    print(f"Recall@3: {metrics['recall_at_3']:.2f}")
    print(f"MRR: {metrics['mrr']:.2f}")

    write_report(metrics, details, total_queries=len(queries))
    print("Reports: reports/benchmark.md + reports/metrics.json")


if __name__ == "__main__":
    main()
