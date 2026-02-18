# Architecture

```mermaid
flowchart TD
    A[Upload File] --> B[OCR/Text Extraction]
    B --> C[Document Classification]
    C --> D[Chunking]
    D --> E[Embedding]
    E --> F[(Vector Store\npgvector or in-memory)]

    G[Retrieve Query] --> E2[Embedding]
    E2 --> F
    F --> H[Top-k Chunks]
    H --> I[Retrieve API Response]

    J[Analyze Text] --> K[Entity Extraction]
    J --> L[Summary + Risk Flags]

    M[QA Question] --> N[Retrieve Top-k Chunks]
    N --> O[LLM/Extractive Answer]
    O --> P[Answer + Citations]
```

## Key modules

- `services/ocr.py` → parse txt/pdf/image
- `services/classifier.py` → rule/LLM classification
- `services/chunker.py` → chunk split policy
- `services/embeddings.py` → OpenAI/local vector generation
- `services/vector_store.py` → storage + retrieval abstraction
- `services/analyzer.py` → summary + risk flags
- `services/qa.py` → grounded question answering
- `api/routes.py` → ingest/retrieve/extract/analyze/qa endpoints
