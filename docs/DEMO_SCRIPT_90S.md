# Current local demonstration

Use the root README to install and start the API in memory/rule mode with provider credentials disabled. Start `streamlit_app.py`.

1. Ingest a synthetic TXT containing `Payment obligations: Party A shall pay USD 5,000 within 15 days`.
2. Ask a question sharing the words payment/obligations; show the extractive snippet and its chunk ID.
3. Ask `astronomy spaceship galaxies`; show no context/no citations.
4. Explain that paraphrases may be missed and overlapping words can retrieve insufficient evidence. The grounding diagnostic records these failures.
5. Show the audit view and extraction errors for unsupported/empty input.

Actual screenshot: `output/playwright/grounded-answer.png`. API example: `output/playwright/api-demo.json`. This screenshot verifies local Q&A, not all browser flows or live AI quality.
