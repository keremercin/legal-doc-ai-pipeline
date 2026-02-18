# ⚖️ legal-doc-ai-pipeline

Portfolio-grade **Legal Document AI** project designed to impress technical clients and hiring teams.

It provides a complete path from raw legal files to searchable, analyzable intelligence:

- OCR/text extraction (`txt`, `pdf`, image)
- LLM/rule-based legal document classification
- Chunking + embeddings
- Hybrid retrieval (vector + keyword boost)
- `pgvector` persistence (with in-memory fallback)
- Legal entity extraction + risk flags + summarization
- Grounded Q&A endpoint with citations
- Optional API-key auth + audit trail endpoint
- FastAPI backend + Streamlit demo UI
- Benchmark script with markdown report output

---

## 🚀 Why this repo matters

This is not a toy chatbot. It demonstrates production-thinking:

1. **Data pipeline discipline** (ingest → process → retrieve)
2. **LLM + infra integration** (OpenAI + vector DB)
3. **Measurable quality** (Recall@k, MRR, report generation)
4. **Deliverable UX** (API + demo UI + docs + CI)

---

## 🧱 Architecture

```text
Upload (PDF/Image/TXT)
   ↓
OCR / Text extraction
   ↓
Classification (Rule or LLM)
   ↓
Chunking
   ↓
Embeddings
   ↓
Vector Store (pgvector or memory)
   ↓
Hybrid Search (dense + keyword boost)
   ↓
Retrieve API + Streamlit

+ Analyze API: summary + entities + risk flags
```

See: `docs/ARCHITECTURE.md`

---

## 🛠 Tech stack

- **Backend:** FastAPI
- **Data/Vector:** PostgreSQL + pgvector
- **LLM:** OpenAI (embedding + classification/summarization optional)
- **OCR:** pypdf + pytesseract
- **UI:** Streamlit
- **Quality:** pytest + ruff + GitHub Actions CI

---

## ⚡ Quickstart

### 1) Setup

```bash
cp .env.example .env
# Optional: set API_KEY in .env to protect v1 endpoints
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

### 2) Start DB

```bash
docker compose up -d db
```

### 3) Run API

```bash
uvicorn legal_doc_ai.main:app --reload --host 0.0.0.0 --port 8000
```

### 4) Run UI

```bash
streamlit run streamlit_app.py
```

Open Swagger: <http://localhost:8000/docs>


### Full-stack with Docker (DB + API + UI)

```bash
docker compose up -d --build
```

- API: <http://localhost:8000/docs>
- UI: <http://localhost:8501>


---

## 🔌 API endpoints

- `GET /health` → service + backend metadata
- `POST /v1/ingest` → upload and index file
- `POST /v1/retrieve` → semantic + keyword-boosted retrieval
- `POST /v1/extract` → legal entity extraction
- `POST /v1/analyze` → classification + summary + entities + risk flags
- `POST /v1/qa` → grounded Q&A over indexed chunks + citations
- `GET /v1/audit` → recent API audit events

---

## 🧪 Benchmark

Run retrieval benchmark:

```bash
python scripts/eval_retrieval.py
```

Outputs:
- console metrics (`Recall@1`, `Recall@3`, `MRR`)
- markdown report at `reports/benchmark.md`

---


---

## 💥 Proof of Impact (Employer View)

If I’m hiring for AI/Data Automation work, this repo proves the candidate can:

- **Design end-to-end AI systems**, not only notebooks
- **Ship usable product surfaces** (API + demo UI)
- **Handle retrieval architecture choices** (memory vs pgvector, hybrid scoring)
- **Build practical legal-tech features** (entities, risk flags, grounded Q&A)
- **Measure quality** with repeatable benchmark/report workflow
- **Maintain engineering hygiene** (tests, lint, CI, deployment docs)

In short: this is a deployable, explainable AI feature stack — not a toy demo.

## 🧰 Useful commands

```bash
make dev        # start postgres
make run-api    # run fastapi
make run-ui     # run streamlit
make seed       # seed demo docs via API
make eval       # run retrieval benchmark
make smoke      # API e2e smoke (requires running API)
make demo-report # generates reports/demo_run.md (requires running API)
make test       # run tests
make lint       # lint checks
```

---

## 📁 Structure

```text
legal-doc-ai-pipeline/
├─ src/legal_doc_ai/
│  ├─ api/
│  ├─ core/
│  ├─ services/
│  ├─ config.py
│  ├─ db.py
│  ├─ models.py
│  └─ main.py
├─ scripts/
├─ tests/
├─ docs/
├─ reports/
├─ streamlit_app.py
└─ README.md
```

---

## ✅ Current status

- [x] End-to-end ingestion + retrieval
- [x] pgvector integration
- [x] Hybrid retrieval scoring
- [x] Entity extraction baseline
- [x] Analyze endpoint (summary + risk flags)
- [x] CI (lint + tests)
- [x] Benchmark report generator
- [x] Grounded Q&A endpoint with source citations
- [ ] GIF/video demo capture
- [ ] Real-world legal eval dataset expansion
- [x] Optional API key security + audit logs

---

## 📦 Deployment

Deployment notes: `docs/DEPLOYMENT.md`


Case study: `docs/CASE_STUDY.md`


Release notes: `docs/RELEASE_NOTES_v0.4.0.md`
Render deploy guide: `docs/DEPLOY_RENDER.md`
