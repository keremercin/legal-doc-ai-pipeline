"""Transparent lexical retrieval / abstention diagnostic, without provider calls."""
import json
from pathlib import Path

from legal_doc_ai.config import get_settings
from legal_doc_ai.services.qa import QAGenerator
from legal_doc_ai.services.vector_store import InMemoryVectorStore


def main():
    settings = get_settings()
    if settings.openai_api_key:
        raise RuntimeError('This diagnostic requires OPENAI_API_KEY to be empty')
    documents = {
        'payment': 'Payment obligations: the invoice amount is USD 5000, payable within fifteen days.',
        'termination': 'Termination requires thirty days of written notice before cancellation.',
        'privacy': 'Confidentiality obligations protect customer information and prohibit disclosure.',
        'delivery': 'Delivery of the monthly report is due on the first business day.',
        'distractor': 'A history of maritime shipping describes cargo vessels and trade routes.',
    }
    cases = [
        ('payment invoice amount', 'payment', 'direct'),
        ('termination notice cancellation', 'termination', 'direct'),
        ('confidentiality customer information', 'privacy', 'direct'),
        ('monthly report delivery', 'delivery', 'direct'),
        ('When must I remit the fee?', 'payment', 'paraphrase'),
        ('How can we end the relationship?', 'termination', 'paraphrase'),
        ('Are client records secret?', 'privacy', 'paraphrase'),
        ('When is the recurring document submitted?', 'delivery', 'paraphrase'),
        ('astronomy spaceship galaxies', None, 'unanswerable'),
        ('banana bread recipe', None, 'unanswerable'),
        ('tax withholding percentage', None, 'unanswerable'),
        ('customer information encryption algorithm', None, 'hard_negative'),
    ]
    store = InMemoryVectorStore()
    ids = {}
    for label, text in documents.items():
        result = store.add_document(filename=label + '.txt', classification=label, full_text=text, chunks=[text])
        ids[label] = result['document_id']
    rows = []
    for query, expected, category in cases:
        hits = [h for h in store.search(query, 3) if h.score > 0]
        answer = QAGenerator(store).answer(query, 3)
        predicted = hits[0].metadata['classification'] if hits else None
        passed = predicted == expected if expected else not answer['citations']
        rows.append({'query': query, 'category': category, 'expected': expected, 'predicted': predicted,
                     'passed': passed, 'scores': [h.score for h in hits], 'answer': answer})
    payload = {'mode': 'offline lexical, synthetic diagnostic', 'documents': documents, 'cases': rows,
               'passed': sum(r['passed'] for r in rows), 'total': len(rows),
               'limitations': 'Manually authored tiny diagnostic, not held-out customer benchmark. Positive overlap can admit unsupported questions; paraphrases can be missed.'}
    path = Path('reports/grounding-diagnostic.json')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    print(f"{payload['passed']}/{payload['total']} diagnostic cases passed")
    for row in rows:
        if not row['passed']:
            print(f"FAIL [{row['category']}] {row['query']} -> {row['predicted']}")


if __name__ == '__main__':
    main()
