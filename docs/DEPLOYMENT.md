> Historical planning/presentation note. Current behavior and verified evidence are in the root README. Local retrieval is lexical; provider/pgvector paths require separate validation. Citations identify context, not independently verified claims. Old deployment, experience and production wording must not be treated as current proof.

# Deployment Notes

## One-command local run

```bash
make install && make dev && make run-api
```

This starts Postgres (`pgvector`) and serves API at `http://localhost:8000/docs`.

## Minimal production checklist

- Move secrets to environment manager (not `.env` in repo)
- Keep `X-API-Key` enabled for non-public endpoints
- Configure reverse proxy + TLS
- Enable database backups
- Add structured logs and request-id tracing

## Docker options

```bash
docker build -t legal-doc-ai:latest .
docker run --env-file .env -p 8000:8000 legal-doc-ai:latest
```

## Full stack compose

```bash
docker compose up -d --build
```

- API: `http://localhost:8000/docs`
- UI: `http://localhost:8501`
