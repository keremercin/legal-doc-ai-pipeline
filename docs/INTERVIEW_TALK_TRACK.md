> Historical planning/presentation note. Current behavior and verified evidence are in the root README. Local retrieval is lexical; provider/pgvector paths require separate validation. Citations identify context, not independently verified claims. Old deployment, experience and production wording must not be treated as current proof.

# Interview Talk Track (2-3 min)

## 1) What did you build?
I built a legal document AI pipeline that ingests PDFs/images/text, indexes them in pgvector, and exposes APIs for retrieval, analysis, and grounded Q&A.

## 2) Why is this useful?
Legal/ops teams spend too much manual time searching contracts and invoices. This project shortens that loop using semantic retrieval and structured extraction.

## 3) Technical highlights
- FastAPI backend with clean endpoint design
- OCR + chunking + embedding + vector indexing
- Hybrid scoring (dense + lexical)
- Analyze endpoint (classification, summary, risk flags)
- Grounded QA endpoint with citations
- CI + tests + benchmark reporting

## 4) Engineering tradeoffs
- Rule/heuristic fallbacks keep system runnable without API keys
- Swappable backend: memory for quick dev, pgvector for persistence
- Explicit benchmark script to track retrieval quality over time

## 5) What would you improve next?
- Real anonymized legal benchmark dataset
- authentication + audit logs
- richer legal entity model and clause-level analytics
