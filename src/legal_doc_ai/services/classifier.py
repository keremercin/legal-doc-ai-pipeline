from openai import OpenAI, OpenAIError

from legal_doc_ai.config import get_settings

settings = get_settings()


class ClassifierService:
    """Legal doc classifier with rule + optional LLM mode."""

    allowed_labels = frozenset({"contract", "invoice", "litigation", "compliance", "other"})

    def classify(self, text: str) -> str:
        mode = settings.classifier_mode.lower().strip()
        if mode == "rule":
            return self._rule_classify(text)
        if mode == "llm":
            return self._llm_classify(text) if settings.openai_api_key else self._rule_classify(text)

        # auto mode
        if settings.openai_api_key:
            return self._llm_classify(text)
        return self._rule_classify(text)

    def _rule_classify(self, text: str) -> str:
        lowered = text.lower()
        if any(k in lowered for k in ["contract", "agreement", "party", "termination"]):
            return "contract"
        if any(k in lowered for k in ["invoice", "payment", "amount due", "net 30", "net 15"]):
            return "invoice"
        if any(k in lowered for k in ["court", "lawsuit", "plaintiff", "defendant", "claim"]):
            return "litigation"
        if any(k in lowered for k in ["policy", "gdpr", "kvkk", "regulation", "compliance"]):
            return "compliance"
        return "other"

    def _llm_classify(self, text: str) -> str:
        try:
            client = OpenAI(api_key=settings.openai_api_key)
            prompt = (
                "You are classifying legal/business documents. "
                "Return exactly one label from: contract, invoice, litigation, compliance, other.\n\n"
                f"Document:\n{text[:4000]}"
            )
            resp = client.chat.completions.create(
                model=settings.openai_chat_model,
                temperature=0,
                messages=[
                    {"role": "system", "content": "Return only one label."},
                    {"role": "user", "content": prompt},
                ],
            )
            label = (resp.choices[0].message.content or "other").strip().lower()
            if label not in self.allowed_labels:
                return self._rule_classify(text)
            return label
        except (OpenAIError, IndexError, ValueError):
            return self._rule_classify(text)
