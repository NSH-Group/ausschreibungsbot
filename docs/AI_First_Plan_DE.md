# Maßnahmenplan – KI-unterstützte Umsetzung (DE)
**Ziel:** Bau eines Systems zur automatisierten Erkennung von Ausschreibungen für Radsatzbearbeitung/Radsatzfertigung mit maximaler Nutzung von KI (ChatGPT).

## Phase 0 – Vorbereitung (0.5–1 Tag)
- Erstelle privates Git-Repo (GitHub/GitLab).
- Lege Cloud-Postfach an: `tenders@<firma>.com` (IMAP aktiv).
- Sammle Zugangsdaten für APIs/Portale (wenn vorhanden).
- Installiere: Python 3.11, Docker, docker-compose.
- Kopiere dieses Kit ins Repo.

## Phase 1 – AI-Bootstrap (1–2 Tage)
1. **Repo-Bootstrap mit ChatGPT**  
   - Nutze `docs/Prompts/01_repo_bootstrap_prompt.md`.
   - Ergebnis: Projektstruktur, Pip/Poetry, Dockerfile, docker-compose, basic FastAPI (optional).
2. **DB & Schema**  
   - `tenders_raw`, `tenders_filtered`, `alerts_sent` – generieren lassen.
3. **Ops**  
   - Makefile-Targets (`make dev up`, `make test`, `make lint`).

## Phase 2 – Datengewinnung (3–5 Tage)
1. **API/RSS-Connectoren** (TED, UNGM, World Bank, ADB, AfDB).  
   - Prompt `02_connectors_prompt.md` nutzen.
2. **E-Mail-Parser (IMAP)**  
   - Prompt `05_email_parser_prompt.md`.
3. **(Optional) Aggregator-API** (TendersInfo/GlobalTenders).

## Phase 3 – Verarbeitung & Bewertung (3–4 Tage)
- **Keyword/NLP-Engine** (spaCy + Regex) – Prompt `03_scoring_prompt.md`.
- **Scoring**: 40% Keywords, 30% Rail-Kontext, 15% Markt, 10% Deadline, 5% Budget.
- **Deduplizierung**, **Normalisierung** (CPV, Sprache, Datum).

## Phase 4 – Alerts & Delivery (1–2 Tage)
- Email (SMTP) + Teams/Slack-Webhook.
- Tägliche und Sofort-Alerts (Score >= 60).
- CSV/Excel-Export.

## Phase 5 – Scheduler & Betrieb (1–2 Tage)
- Cron/Workflow: täglich 05:00 (Europe/Berlin).
- Logging, Retry/Backoff, Fehler-Alerts.
- .env in Secret-Manager übertragen.

## Phase 6 – Pilot & Tuning (2 Wochen)
- KPI: Precision, Recall, Time-to-Alert, Volumen pro Region.
- Keyword/Treshold-Tuning mit ChatGPT.
- Erweiterung um Login-Scraper, wenn AGB ok (Prompt `04_scraper_prompt.md`).

## Rollen
- Product Owner (Fachbereich), Developer (KI-unterstützt), DevOps, Data Engineer.

## Compliance
- Nur öffentliche Daten. Keine Captcha-Umgehung. Portal-AGB beachten.
