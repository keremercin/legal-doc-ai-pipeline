from openai import OpenAI

from legal_doc_ai.config import get_settings
from legal_doc_ai.services.vector_store import RetrievedItem, VectorStore

settings = get_settings()


class QAGenerator:
    """Grounded QA over retrieved chunks."""

    def __init__(self, store: VectorStore) -> None:
        self.store = store

    def answer(self, question: str, top_k: int = 5) -> dict:
        hits = self.store.search(question, top_k=top_k)

        if not hits:
            return {
                "question": question,
                "answer": "No relevant context found in indexed documents.",
                "citations": [],
            }

        if settings.openai_api_key:
            llm_answer = self._answer_with_llm(question, hits)
            return {
                "question": question,
                "answer": llm_answer,
                "citations": [h.chunk_id for h in hits],
            }

        fallback = self._answer_fallback(question, hits)
        return {
            "question": question,
            "answer": fallback,
            "citations": [h.chunk_id for h in hits],
        }

    def _answer_with_llm(self, question: str, hits: list[RetrievedItem]) -> str:
        context = "\n\n".join(
            [f"[Chunk {h.chunk_id}]\n{h.text}" for h in hits]
        )
        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=settings.openai_chat_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Answer strictly from provided chunks. If missing, say insufficient context. "
                        "Use concise professional tone."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Question: {question}\n\nContext:\n{context}",
                },
            ],
        )
        return (resp.choices[0].message.content or "").strip()

    def _answer_fallback(self, question: str, hits: list[RetrievedItem]) -> str:
        top = hits[:3]
        bullets = "\n".join([f"- {h.text[:220]}" for h in top])
        return (
            f"Question: {question}\n\n"
            "Grounded snippets:\n"
            f"{bullets}\n\n"
            "(LLM disabled, returned extractive answer from top retrieved chunks.)"
        )
