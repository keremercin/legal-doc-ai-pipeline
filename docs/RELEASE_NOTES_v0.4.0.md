> Historical planning/presentation note. Current behavior and verified evidence are in the root README. Local retrieval is lexical; provider/pgvector paths require separate validation. Citations identify context, not independently verified claims. Old deployment, experience and production wording must not be treated as current proof.

# Release Notes — v0.4.0

## Highlights

- End-to-end legal document pipeline (ingest/retrieve/analyze/qa)
- OCR support for txt/pdf/image inputs
- Hybrid retrieval (dense + lexical signal)
- Grounded Q&A with chunk citations
- Optional API key auth for `/v1/*` routes
- Request ID middleware for traceability
- In-memory audit trail endpoint (`GET /v1/audit`)
- Streamlit demo UI with dedicated tabs for each workflow

## Engineering Quality

- CI workflow (lint + tests)
- 11 passing tests
- benchmark + demo report scripts
- deployment and interview documentation

## Included endpoints

- `GET /health`
- `POST /v1/ingest`
- `POST /v1/retrieve`
- `POST /v1/extract`
- `POST /v1/analyze`
- `POST /v1/qa`
- `GET /v1/audit`

## Next in roadmap

- anonymized legal benchmark expansion
- auth/audit persistence (DB-backed)
- public demo deployment
