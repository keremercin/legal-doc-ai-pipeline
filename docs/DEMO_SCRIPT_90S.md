# 90-Second Demo Script (Portfolio)

## Goal
Show hiring managers this is production-minded AI engineering, not prompt glue.

## Recording setup
- Start services: `docker compose up -d --build`
- Open API docs: `http://localhost:8000/docs`
- Open UI: `http://localhost:8501`

## Timeline (90s)

### 0s–10s — Intro
"This is a legal document AI pipeline. It ingests legal files, indexes them with pgvector, and supports retrieval, analysis, and grounded Q&A."

### 10s–30s — Ingest
- In Streamlit `Ingest` tab, upload `demo_contract.txt`
- Click **Ingest**
- Show response: classification, chunk_count, metadata

Say: "We parse and classify first, then index chunks for semantic retrieval."

### 30s–50s — Retrieve
- Go to `Retrieve` tab
- Query: `payment obligations and deadlines`
- Show top chunks + scores

Say: "Search is hybrid: vector relevance plus lexical boost for robustness."

### 50s–70s — Analyze
- Go to `Analyze Text`
- Paste legal paragraph
- Click **Analyze**
- Show `classification`, `entities`, `risk_flags`

Say: "This endpoint provides structured legal signals for downstream automation."

### 70s–90s — Grounded Q&A
- Go to `Grounded Q&A`
- Ask: `What must Party A pay and by when?`
- Show answer + citations

Say: "Answers are grounded in retrieved chunks with citations for traceability."

## End line
"This project is API-first, tested, benchmarked, and deployment-ready — built for real client delivery."
