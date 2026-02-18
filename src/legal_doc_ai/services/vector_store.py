from dataclasses import dataclass, field
from typing import Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from legal_doc_ai.config import get_settings
from legal_doc_ai.models import Chunk, Document
from legal_doc_ai.services.embeddings import embed_text

settings = get_settings()
STOPWORDS = {
    "the", "is", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "between",
    "this", "that", "it", "by", "are", "be", "as", "at", "from", "within"
}


@dataclass
class RetrievedItem:
    chunk_id: str
    score: float
    text: str
    metadata: dict = field(default_factory=dict)


class VectorStore(Protocol):
    def add_document(
        self, *, filename: str, classification: str, full_text: str, chunks: list[str]
    ) -> dict: ...

    def search(self, query: str, top_k: int) -> list[RetrievedItem]: ...


def _tokens(text: str) -> set[str]:
    import re

    toks = set(re.findall(r"[a-zA-Z0-9_]+", text.lower()))
    return {t for t in toks if t not in STOPWORDS and len(t) > 2}


def keyword_bonus(query: str, text: str) -> float:
    q = _tokens(query)
    t = _tokens(text)
    if not q or not t:
        return 0.0

    inter = len(q & t)
    union = len(q | t)
    if union == 0:
        return 0.0

    return inter / union


def combine_score(dense_score: float, keyword_score: float) -> float:
    if settings.openai_api_key:
        return dense_score + settings.hybrid_keyword_boost * keyword_score

    # In local/no-API mode fake embeddings are weak; use lexical signal only.
    return keyword_score


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._store: list[tuple[RetrievedItem, list[float]]] = []

    def add_document(
        self, *, filename: str, classification: str, full_text: str, chunks: list[str]
    ) -> dict:
        from uuid import uuid4

        document_id = str(uuid4())
        for idx, c in enumerate(chunks):
            chunk_id = f"{document_id}:{idx}"
            item = RetrievedItem(
                chunk_id=chunk_id,
                score=0.0,
                text=c,
                metadata={"filename": filename, "classification": classification},
            )
            self._store.append((item, embed_text(c)))

        return {
            "document_id": document_id,
            "filename": filename,
            "classification": classification,
            "chunk_count": len(chunks),
            "metadata": {"chars": len(full_text), "backend": "memory"},
        }

    def search(self, query: str, top_k: int) -> list[RetrievedItem]:
        q = embed_text(query)
        scored: list[RetrievedItem] = []
        for item, vec in self._store:
            dense_score = float(sum(a * b for a, b in zip(q, vec)))
            bonus = keyword_bonus(query, item.text)
            score = combine_score(dense_score, bonus)
            scored.append(
                RetrievedItem(
                    chunk_id=item.chunk_id,
                    score=score,
                    text=item.text,
                    metadata=item.metadata,
                )
            )
        scored.sort(key=lambda x: x.score, reverse=True)
        return scored[:top_k]


class PGVectorStore:
    def __init__(self, db: Session) -> None:
        self.db = db

    def add_document(
        self, *, filename: str, classification: str, full_text: str, chunks: list[str]
    ) -> dict:
        doc = Document(
            filename=filename,
            classification=classification,
            char_count=len(full_text),
        )
        self.db.add(doc)
        self.db.flush()

        chunk_rows: list[Chunk] = []
        for idx, text in enumerate(chunks):
            chunk_id = f"{doc.id}:{idx}"
            emb = embed_text(text)
            chunk_rows.append(
                Chunk(
                    id=chunk_id,
                    document_id=doc.id,
                    idx=idx,
                    text=text,
                    embedding=emb,
                )
            )

        self.db.add_all(chunk_rows)
        self.db.commit()

        return {
            "document_id": doc.id,
            "filename": doc.filename,
            "classification": doc.classification,
            "chunk_count": len(chunk_rows),
            "metadata": {"chars": doc.char_count, "backend": "pgvector"},
        }

    def search(self, query: str, top_k: int) -> list[RetrievedItem]:
        q = embed_text(query)

        distance = Chunk.embedding.cosine_distance(q)
        stmt = (
            select(Chunk, Document, distance.label("distance"))
            .join(Document, Chunk.document_id == Document.id)
            .order_by(distance.asc())
            .limit(top_k * 3)
        )

        rows = self.db.execute(stmt).all()
        out: list[RetrievedItem] = []
        for chunk, doc, dist in rows:
            d = float(dist)
            dense_score = max(0.0, 1.0 - d)
            bonus = keyword_bonus(query, chunk.text)
            score = combine_score(dense_score, bonus)
            out.append(
                RetrievedItem(
                    chunk_id=chunk.id,
                    score=score,
                    text=chunk.text,
                    metadata={
                        "filename": doc.filename,
                        "classification": doc.classification,
                        "document_id": doc.id,
                    },
                )
            )

        out.sort(key=lambda x: x.score, reverse=True)
        return out[:top_k]
