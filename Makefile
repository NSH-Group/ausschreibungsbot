.PHONY: setup dev-up test lint format migrate
setup:
	pip install poetry
	poetry install

dev-up:
	docker compose up --build -d

test:
	poetry run pytest -q

lint:
	poetry run ruff check .

format:
	poetry run ruff check . --fix
	poetry run black .

migrate:
	poetry run python -m app.migrations.migrate
