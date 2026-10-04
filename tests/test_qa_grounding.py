import pytest

from legal_doc_ai.services import qa
from legal_doc_ai.services.qa import QAGenerator
from legal_doc_ai.services.vector_store import RetrievedItem


class Store:
    def __init__(self, hits):
        self.hits = hits

    def search(self, question, top_k):
        return self.hits[:top_k]


def test_no_relevant_context_does_not_call_provider(monkeypatch):
    hits = [RetrievedItem('zero', 0, 'Unrelated text'), RetrievedItem('bad', float('nan'), 'Text'), RetrievedItem('empty', 1, ' ')]
    monkeypatch.setattr(qa.settings, 'openai_api_key', 'test-only')
    monkeypatch.setattr(QAGenerator, '_answer_with_llm', lambda *args: pytest.fail('Provider must not be called'))
    result = QAGenerator(Store(hits)).answer('payment deadline')
    assert result['citations'] == []
    assert result['answer'] == 'No relevant context found in indexed documents.'


def test_extractive_citations_match_only_displayed_chunks(monkeypatch):
    monkeypatch.setattr(qa.settings, 'openai_api_key', '')
    hits = [RetrievedItem(f'chunk-{i}', 0.5, f'Payment evidence {i}') for i in range(5)]
    result = QAGenerator(Store(hits)).answer('payment', top_k=5)
    assert result['citations'] == ['chunk-0', 'chunk-1', 'chunk-2']
    for citation in result['citations']:
        assert f'[{citation}]' in result['answer']
    assert 'chunk-3' not in result['answer']


@pytest.mark.parametrize('question,k', [(' ', 3), ('payment', 0), ('payment', 51)])
def test_invalid_qa_input(question, k):
    with pytest.raises(ValueError):
        QAGenerator(Store([])).answer(question, k)
