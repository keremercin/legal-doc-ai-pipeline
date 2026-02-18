# Deployment Notes

## Local

```bash
cp .env.example .env
# set OPENAI_API_KEY + RETRIEVER_BACKEND=pgvector

docker compose up -d db
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn legal_doc_ai.main:app --host 0.0.0.0 --port 8000
```

## Production checklist

- [ ] move secrets to environment manager (not `.env` in repo)
- [ ] restrict CORS
- [ ] add API auth
- [ ] configure reverse proxy (Nginx/Caddy)
- [ ] setup backups for Postgres
- [ ] add structured logging + request IDs

## Docker run (API)

```bash
docker build -t legal-doc-ai:latest .
docker run --env-file .env -p 8000:8000 legal-doc-ai:latest
```


## Full stack compose

```bash
docker compose up -d --build
```

- API: http://localhost:8000/docs
- UI: http://localhost:8501
