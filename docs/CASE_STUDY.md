> Current scope note: this is a local portfolio demo. It is not a client case study or a validated legal-review system.

# Local Legal Document Pipeline Demo

## Problem

The repository demonstrates document ingestion, extraction, classification, local retrieval, and an API/Streamlit interface.

## Goal

The current implementation can:

1. ingest heterogeneous legal files,
2. make them searchable with lexical retrieval in the default local configuration,
3. expose fast API endpoints for downstream automation.

## Approach

- **Ingestion:** OCR + text extraction for `txt/pdf/image`
- **Understanding:** classification + entity extraction + risk-flag baseline
- **Search:** lexical retrieval is the local default; provider and pgvector paths need separate validation
- **Delivery:** FastAPI + Streamlit demo + benchmark reporting

The built-in retrieval benchmark uses a small synthetic fixture set. It does not establish OCR quality, answer correctness, semantic retrieval quality, live provider reliability, or business outcomes. Returned source chunks identify context but do not independently validate claims.

## Next Improvements

- Replace baseline extraction with model-based legal NER
- Expand benchmark with real anonymized document set
- Add auth/audit logging for production deployment
