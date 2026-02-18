from legal_doc_ai.services.chunker import simple_chunk


def test_simple_chunk_splits_text() -> None:
    text = "a" * 1200
    chunks = simple_chunk(text, chunk_size=500, overlap=50)
    assert len(chunks) >= 2
    assert all(c for c in chunks)
