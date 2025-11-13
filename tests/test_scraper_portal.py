from pathlib import Path

from app.models import Base, TenderRaw
from app.db import engine, SessionLocal
from app.scraper.portal import parse_results_html, ingest_results_html


def setup_module():
    Base.metadata.create_all(bind=engine)


def test_parse_results_html_fixture():
    html_path = Path("tests/fixtures/portal_search_results.html")
    html = html_path.read_text(encoding="utf-8")
    records = parse_results_html(html)
    assert len(records) == 2
    first = records[0]
    assert "Underfloor wheel lathe" in (first.get("title") or "")
    assert first.get("budget") == "1000000"
    assert first.get("deadline") == "2025-12-31"


def test_ingest_results_html_inserts_into_db():
    html_path = Path("tests/fixtures/portal_search_results.html")
    html = html_path.read_text(encoding="utf-8")

    db = SessionLocal()
    before = db.query(TenderRaw).count()
    inserted = ingest_results_html(db, html)
    after = db.query(TenderRaw).count()
    db.close()

    assert inserted == 2
    assert after == before + 2
