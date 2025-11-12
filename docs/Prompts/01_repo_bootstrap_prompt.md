You are an expert Python architect. Create a production-grade repo for an automated tender monitoring system.
Requirements:
- Python 3.11 project with src/ layout
- Poetry or pip-tools; include requirements with versions
- FastAPI minimal admin (optional) + health endpoint
- PostgreSQL (SQLAlchemy) with 3 tables: tenders_raw, tenders_filtered, alerts_sent
- Dockerfile + docker-compose (Postgres + app)
- Makefile with targets: setup, dev-up, test, lint, format, migrate
- .env handling (dotenv) and pydantic settings
- Logging (structlog), retry/backoff utilities
- Unit tests (pytest) and GitHub Actions CI
Deliver code as files with full contents. 