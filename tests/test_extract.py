from legal_doc_ai.services.entities import LegalEntityExtractor


def test_extract_entities() -> None:
    text = """
    This agreement is made between Party A and Party B on 12/01/2026.
    Party A shall pay USD 15,000 within 30 days.
    """
    out = LegalEntityExtractor().extract(text)
    assert "Party A" in out["parties"] or "party a" in [p.lower() for p in out["parties"]]
    assert any("12/01/2026" in d for d in out["dates"])
    assert len(out["amounts"]) >= 1
