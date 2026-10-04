import re


class LegalEntityExtractor:
    """Lightweight regex-based extractor (v1 baseline)."""

    DATE_PATTERNS = (
        r"\b\d{1,2}[./-]\d{1,2}[./-]\d{2,4}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},\s+\d{4}\b",
    )

    def extract(self, text: str) -> dict:
        parties = self._extract_parties(text)
        dates = self._extract_dates(text)
        amounts = self._extract_amounts(text)
        obligations = self._extract_obligations(text)

        return {
            "parties": sorted(set(parties)),
            "dates": sorted(set(dates)),
            "amounts": sorted(set(amounts)),
            "obligations": obligations,
        }

    def _extract_parties(self, text: str) -> list[str]:
        patterns = [
            r"\bParty\s+[A-Z]\b",
            r"\bplaintiff\b",
            r"\bdefendant\b",
            r"\bclient\b",
            r"\bvendor\b",
        ]
        out: list[str] = []
        for p in patterns:
            out += re.findall(p, text, flags=re.IGNORECASE)
        return out

    def _extract_dates(self, text: str) -> list[str]:
        out: list[str] = []
        for p in self.DATE_PATTERNS:
            out += re.findall(p, text, flags=re.IGNORECASE)
        return out

    def _extract_amounts(self, text: str) -> list[str]:
        patterns = [
            # currency before amount: USD 15,000 / $5000 / TRY 1200
            r"(?:USD|EUR|TRY|TL|\$|€|₺)\s?\d+(?:[.,]\d{3})*(?:[.,]\d{2})?",
            # amount before currency: 15,000 USD / 1200 TL
            r"\d+(?:[.,]\d{3})*(?:[.,]\d{2})?\s?(?:USD|EUR|TRY|TL)",
        ]
        out: list[str] = []
        for p in patterns:
            out += re.findall(p, text, flags=re.IGNORECASE)
        return out

    def _extract_obligations(self, text: str) -> list[str]:
        obligation_keywords = ["shall", "must", "obligation", "required", "confidentiality"]
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return [line for line in lines if any(k in line.lower() for k in obligation_keywords)]
