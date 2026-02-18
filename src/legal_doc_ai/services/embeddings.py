from hashlib import md5

from openai import OpenAI

from legal_doc_ai.config import get_settings

settings = get_settings()


def _fake_embedding(text: str, dim: int) -> list[float]:
    digest = md5(text.encode("utf-8")).digest()
    raw = list(digest) * ((dim // len(digest)) + 1)
    raw = raw[:dim]
    return [x / 255.0 for x in raw]


def embed_text(text: str) -> list[float]:
    """Generate embedding via OpenAI when API key exists; otherwise deterministic local vector."""
    if settings.openai_api_key:
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.embeddings.create(model=settings.openai_embedding_model, input=text)
        return resp.data[0].embedding

    # local fallback keeps project runnable without paid APIs
    return _fake_embedding(text, dim=settings.vector_dim)
