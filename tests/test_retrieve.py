from legal_doc_ai.services.vector_store import InMemoryVectorStore


def test_retriever_returns_hits() -> None:
    r = InMemoryVectorStore()
    r.add_document(
        filename="doc1.txt",
        classification="contract",
        full_text="This contract includes confidentiality clause.",
        chunks=["This contract includes confidentiality clause."],
    )
    r.add_document(
        filename="doc2.txt",
        classification="invoice",
        full_text="Invoice amount due in 30 days.",
        chunks=["Invoice amount due in 30 days."],
    )

    out = r.search("contract confidentiality", top_k=1)
    assert len(out) == 1
    assert out[0].metadata["classification"] in {"contract", "invoice"}
