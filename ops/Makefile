setup:
	python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt

dev-up:
	docker compose -f ops/docker-compose.yml up -d

test:
	pytest -q

lint:
	ruffleHog . || true
