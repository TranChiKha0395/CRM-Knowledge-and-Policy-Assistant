.PHONY: help up down dev-db lint check-csv test migrate

help:
	@echo "Targets: up | down | dev-db | lint | check-csv | test | migrate"

up:
	docker compose --profile app up -d

down:
	docker compose down

dev-db:
	docker compose up -d db redis

lint:
	cd backend && ruff check . && mypy src
	python -m compileall -q worker/src
	cd frontend && npm run lint

check-csv:
	python -c "import csv, pathlib, sys; errs = [f'{p}: expected {n} cols, got {len(c)}' for p, n in [('data/templates/passages_template.csv', 21), ('data/templates/critical_fields_template.csv', 23)] for r in [list(csv.reader(pathlib.Path(p).read_text(encoding='utf-8-sig').splitlines()))] for c in [r[0] if r else []] if len(c) != n]; print('; '.join(errs) if errs else 'Template CSV contracts valid'); sys.exit(1 if errs else 0)"

test:
	cd backend && pytest -q
	cd frontend && npm run build

migrate:
	cd backend && alembic upgrade head
