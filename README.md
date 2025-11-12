# AI-First Tender Monitoring – Execution Kit
Version: 1.0 | Date: 2025-11-12

This repo scaffolds everything you need to build the automated tender monitoring system **with maximum AI assistance (ChatGPT or similar)**.

## Structure
- `docs/AI_First_Plan_DE.md` – Vollständiger, konkreter Maßnahmenplan (DE)
- `docs/AI_First_Plan_EN.md` – Full, concrete action plan (EN)
- `docs/Prompts/` – High-quality prompts to ask ChatGPT for code generation
- `config/portal_master.csv` – Masterliste der Portale + Zugriffstyp + Priorität
- `config/keywords_multilingual.csv` – Start-Keywordliste (DE/EN/FR/ES/IT)
- `config/.env.example` – Platzhalter für Secrets
- `backlog/Product_Backlog.csv` – Umsetzungs-Backlog (Sprints, Stories, DoD)
- `src/` – Zielverzeichnis für den generierten Code
- `ops/` – DevOps: docker-compose, Makefile, CI stub
- `templates/` – E-Mail/Teams-Alert-Templates

## How to use with ChatGPT
1. Open `docs/Prompts/01_repo_bootstrap_prompt.md` and paste it into ChatGPT (GPT-5 Thinking).
2. Follow the steps; copy code back into your local repo.
3. Proceed with the next prompt file (02_connectors, 03_scrapers, 04_scoring, etc.).
4. Keep your secrets in `.env` (copy from `config/.env.example`).

## Success criteria (DoD)
- API Connectors (TED/UNGM/WB/ADB/AfDB) functional
- Email/Teams alerts for score >= 60
- Postgres schema created and running
- Daily cron fetch works
- 2-week pilot: >= 80% precision on alerts, >= 90% recall for EU/banks
