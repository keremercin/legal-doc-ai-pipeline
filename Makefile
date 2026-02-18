.PHONY: install dev test lint format run-api run-ui seed eval smoke demo-report init-db

install:
	python -m venv .venv && . .venv/bin/activate && pip install -e .[dev]

dev:
	docker compose up -d db

init-db:
	python scripts/init_db.py

run-api:
	uvicorn legal_doc_ai.main:app --reload --host 0.0.0.0 --port 8000

run-ui:
	streamlit run streamlit_app.py

seed:
	python scripts/seed_demo.py

eval:
	python scripts/eval_retrieval.py

smoke:
	python scripts/smoke_e2e.py

demo-report:
	python scripts/demo_walkthrough.py

test:
	pytest

lint:
	ruff check src tests scripts

format:
	ruff check --fix src tests scripts
