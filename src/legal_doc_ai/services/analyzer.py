from openai import OpenAI, OpenAIError

from legal_doc_ai.config import get_settings
from legal_doc_ai.services.classifier import ClassifierService
from legal_doc_ai.services.entities import LegalEntityExtractor

settings = get_settings()


class DocumentAnalyzer:
    def __init__(self) -> None:
        self.classifier = ClassifierService()
        self.extractor = LegalEntityExtractor()

    def analyze(self, text: str) -> dict:
        classification = self.classifier.classify(text)
        entities = self.extractor.extract(text)
        summary = self._summarize(text)
        risk_flags = self._risk_flags(text)

        return {
            "classification": classification,
            "summary": summary,
            "entities": entities,
            "risk_flags": risk_flags,
        }

    def _summarize(self, text: str) -> str:
        if settings.openai_api_key:
            try:
                client = OpenAI(api_key=settings.openai_api_key)
                resp = client.chat.completions.create(
                    model=settings.openai_chat_model,
                    temperature=0.1,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "Summarize legal/business text in max 3 concise bullet points. "
                                "Highlight obligations and deadlines."
                            ),
                        },
                        {"role": "user", "content": text[:6000]},
                    ],
                )
                return (resp.choices[0].message.content or "").strip()
            except (OpenAIError, IndexError, ValueError):
                return " ".join(text.split())[:320]

        # fallback extractive mini-summary
        cleaned = " ".join(text.split())
        return cleaned[:320] + ("..." if len(cleaned) > 320 else "")

    def _risk_flags(self, text: str) -> list[str]:
        checks = {
            "no_explicit_termination_clause": ["terminate", "termination"],
            "no_confidentiality_term": ["confidentiality", "non-disclosure", "nda"],
            "no_governing_law": ["governing law", "jurisdiction"],
            "no_payment_term": ["payment", "pay", "net 15", "net 30", "due"],
        }
        low = text.lower()
        flags: list[str] = []
        for flag, keywords in checks.items():
            if not any(k in low for k in keywords):
                flags.append(flag)
        return flags
