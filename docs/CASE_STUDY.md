# Case Study — Legal Document AI Pipeline

## Problem

Legal and operations teams waste significant time reading PDFs, invoices, and agreements to locate obligations, payment terms, and litigation context.

## Goal

Build a practical AI pipeline that can:

1. ingest heterogeneous legal files,
2. make them searchable with semantic retrieval,
3. expose fast API endpoints for downstream automation.

## Approach

- **Ingestion:** OCR + text extraction for `txt/pdf/image`
- **Understanding:** classification + entity extraction + risk-flag baseline
- **Search:** embeddings + vector indexing (`pgvector`) + hybrid lexical boost
- **Delivery:** FastAPI + Streamlit demo + benchmark reporting

## Outcome

- End-to-end ingest/retrieve/analyze workflow running locally
- API surface suitable for integration into automation pipelines
- Benchmark output report (`reports/benchmark.md`) for iterative quality tracking

## Next Improvements

- Replace baseline extraction with model-based legal NER
- Expand benchmark with real anonymized document set
- Add auth/audit logging for production deployment
