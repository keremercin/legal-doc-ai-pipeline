from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from openai import OpenAIError

from legal_doc_ai.services import analyzer, classifier


@pytest.mark.parametrize("label", ["contract", "invalid-label"])
def test_classifier_validates_provider_labels(monkeypatch, label):
    client = Mock()
    client.chat.completions.create.return_value = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=label))]
    )
    monkeypatch.setattr(classifier, "OpenAI", lambda **kwargs: client)
    assert classifier.ClassifierService()._llm_classify("agreement") == "contract"


def test_provider_failure_preserves_offline_fallback(monkeypatch):
    def unavailable(**kwargs):
        raise OpenAIError("provider unavailable")

    monkeypatch.setattr(classifier, "OpenAI", unavailable)
    monkeypatch.setattr(analyzer, "OpenAI", unavailable)
    monkeypatch.setattr(analyzer.settings, "openai_api_key", "mock-only")
    assert classifier.ClassifierService()._llm_classify("invoice payment") == "invoice"
    assert analyzer.DocumentAnalyzer()._summarize("A short document") == "A short document"
