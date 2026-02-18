# Demo Run Report

Generated at: `2026-02-18T08:01:56.909465+00:00`

## Health

```json
{'status': 'ok', 'service': 'Legal Doc AI Pipeline', 'metadata': {'retriever_backend': 'memory', 'db_connected': False, 'classifier_mode': 'auto', 'auth_enabled': False}}
```

## Ingestion

### demo_contract.txt

```json
{'document_id': '653dd320-814f-4c78-81fc-2c38140470f0', 'filename': 'tmptgmly_8k.txt', 'classification': 'contract', 'chunk_count': 1, 'metadata': {'chars': 123, 'backend': 'memory', 'entities': {'parties': 2, 'dates': 0, 'amounts': 1, 'obligations': 1}}}
```

### demo_invoice.txt

```json
{'document_id': '061255f5-5dfd-45b4-aade-d6340ad3ded3', 'filename': 'tmpxewbk0gb.txt', 'classification': 'invoice', 'chunk_count': 1, 'metadata': {'chars': 58, 'backend': 'memory', 'entities': {'parties': 0, 'dates': 0, 'amounts': 1, 'obligations': 0}}}
```

### demo_litigation.txt

```json
{'document_id': '06b6c031-dea6-477d-93fd-2ea3f2c2bcff', 'filename': 'tmpvk2m8ov1.txt', 'classification': 'litigation', 'chunk_count': 1, 'metadata': {'chars': 64, 'backend': 'memory', 'entities': {'parties': 1, 'dates': 0, 'amounts': 0, 'obligations': 0}}}
```

## Retrieval

```json
{'query': 'payment obligations and deadline', 'results': [{'chunk_id': '061255f5-5dfd-45b4-aade-d6340ad3ded3:0', 'score': 0.1, 'text': 'Invoice amount due is 18000 USD. Payment terms are Net 30.', 'metadata': {'filename': 'tmpxewbk0gb.txt', 'classification': 'invoice'}}, {'chunk_id': '653dd320-814f-4c78-81fc-2c38140470f0:0', 'score': 0.0, 'text': 'This agreement is made between Party A and Party B. Party A shall pay USD 9000 within 15 days and maintain confidentiality.', 'metadata': {'filename': 'tmptgmly_8k.txt', 'classification': 'contract'}}, {'chunk_id': '06b6c031-dea6-477d-93fd-2ea3f2c2bcff:0', 'score': 0.0, 'text': 'The plaintiff filed a lawsuit in district court alleging breach.', 'metadata': {'filename': 'tmpvk2m8ov1.txt', 'classification': 'litigation'}}]}
```

## Analyze

```json
{'classification': 'contract', 'summary': 'Party A shall pay USD 9000 by 12/04/2026 and keep confidentiality. Either party may terminate with 30-day notice.', 'entities': {'parties': ['Party A'], 'dates': ['12/04/2026'], 'amounts': ['USD 9000'], 'obligations': ['Party A shall pay USD 9000 by 12/04/2026 and keep confidentiality. Either party may terminate with 30-day notice.']}, 'risk_flags': ['no_governing_law']}
```

## Grounded QA

```json
{'question': 'What must Party A pay and by when?', 'answer': 'Question: What must Party A pay and by when?\n\nGrounded snippets:\n- This agreement is made between Party A and Party B. Party A shall pay USD 9000 within 15 days and maintain confidentiality.\n- Invoice amount due is 18000 USD. Payment terms are Net 30.\n- The plaintiff filed a lawsuit in district court alleging breach.\n\n(LLM disabled, returned extractive answer from top retrieved chunks.)', 'citations': ['653dd320-814f-4c78-81fc-2c38140470f0:0', '061255f5-5dfd-45b4-aade-d6340ad3ded3:0', '06b6c031-dea6-477d-93fd-2ea3f2c2bcff:0']}
```

## Audit

```json
{'events': [{'timestamp': '2026-02-18T08:01:56.925512+00:00', 'action': 'qa', 'status': 'ok', 'metadata': {'question': 'What must Party A pay and by when?', 'citations': 3}}, {'timestamp': '2026-02-18T08:01:56.923997+00:00', 'action': 'analyze', 'status': 'ok', 'metadata': {'classification': 'contract', 'risk_flags': 1}}, {'timestamp': '2026-02-18T08:01:56.922513+00:00', 'action': 'retrieve', 'status': 'ok', 'metadata': {'query': 'payment obligations and deadline', 'top_k': 3, 'result_count': 3}}, {'timestamp': '2026-02-18T08:01:56.920612+00:00', 'action': 'ingest', 'status': 'ok', 'metadata': {'filename': 'demo_litigation.txt', 'classification': 'litigation', 'chunk_count': 1}}, {'timestamp': '2026-02-18T08:01:56.919225+00:00', 'action': 'ingest', 'status': 'ok', 'metadata': {'filename': 'demo_invoice.txt', 'classification': 'invoice', 'chunk_count': 1}}, {'timestamp': '2026-02-18T08:01:56.917522+00:00', 'action': 'ingest', 'status': 'ok', 'metadata': {'filename': 'demo_contract.txt', 'classification': 'contract', 'chunk_count': 1}}]}
```
