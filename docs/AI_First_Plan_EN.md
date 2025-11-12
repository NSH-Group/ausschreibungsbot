# Action Plan – AI-Assisted Delivery (EN)
**Goal:** Build an automated tender monitoring system for wheelset machining using maximum AI assistance (ChatGPT).

## Phase 0 – Setup (0.5–1 day)
- Create private Git repo, enable Issues & Actions.
- Provision mailbox `tenders@<company>.com` (IMAP).
- Collect API credentials, install Python 3.11 + Docker.
- Add this kit to the repo.

## Phase 1 – AI Bootstrap (1–2 days)
- Use `docs/Prompts/01_repo_bootstrap_prompt.md` with ChatGPT.
- Generate: project structure, Dockerfile, docker-compose, base FastAPI.
- Create DB schema: `tenders_raw`, `tenders_filtered`, `alerts_sent`.
- Makefile targets for dev/test/lint.

## Phase 2 – Data Acquisition (3–5 days)
- API/RSS connectors (TED, UNGM, World Bank, ADB, AfDB).
- Email parser (IMAP).
- (Optional) Aggregator API (TendersInfo/GlobalTenders).

## Phase 3 – Processing & Scoring (3–4 days)
- Keyword/NLP engine (spaCy + regex).  
- Scoring: 40% keywords, 30% rail-context, 15% market, 10% deadline, 5% budget.
- Normalization, deduplication, CPV tagging.

## Phase 4 – Alerts & Delivery (1–2 days)
- Email + Teams/Slack webhooks. Daily & instant alerts for score >= 60.
- CSV/Excel export.

## Phase 5 – Scheduling & Ops (1–2 days)
- Cron daily 05:00 (Europe/Berlin). Logging & retries.
- Secret manager for .env vars.

## Phase 6 – Pilot & Tuning (2 weeks)
- KPIs: precision, recall, time-to-alert, volume by region.
- Keyword/threshold tuning with ChatGPT.
- Add login scrapers if ToS allow.
