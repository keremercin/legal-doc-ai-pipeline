> Historical planning/presentation note. Current behavior and verified evidence are in the root README. Local retrieval is lexical; provider/pgvector paths require separate validation. Citations identify context, not independently verified claims. Old deployment, experience and production wording must not be treated as current proof.

# Deploy on Render (Docker)

## 1) Create Web Service

- Connect GitHub repo
- Environment: **Docker**
- Region: closest to users
- Branch: `main`

## 2) Add Environment Variables

Required:
- `RETRIEVER_BACKEND=memory` (quick start)

Optional:
- `OPENAI_API_KEY=...`
- `API_KEY=...` (protect `/v1/*`)

If you run with external Postgres + pgvector:
- `RETRIEVER_BACKEND=pgvector`
- `POSTGRES_HOST=...`
- `POSTGRES_PORT=5432`
- `POSTGRES_USER=...`
- `POSTGRES_PASSWORD=...`
- `POSTGRES_DB=...`

## 3) Start Command

Use Dockerfile default (no extra command needed).

## 4) Verify

- `GET /health`
- open `/docs`
- run ingest/retrieve from Streamlit (local) against deployed API URL

## Notes

For portfolio demo, `memory` backend is usually enough.
For production, prefer managed Postgres with pgvector + backups.
