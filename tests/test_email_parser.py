from pathlib import Path

from app.models import Base, TenderRaw
from app.db import engine, SessionLocal
from app.email_parser.parser import (
    parse_eml_bytes,
    extract_records_from_body,
    normalize_email_records,
    process_eml_file,
)


def setup_module():
    Base.metadata.create_all(bind=engine)


def test_parse_eml_and_extract_records():
    eml_path = Path("tests/fixtures/email_alert_1.eml")
    raw = eml_path.read_bytes()
    headers, body = parse_eml_bytes(raw)
    assert "Underfloor wheel lathe" in body

    records = extract_records_from_body(body)
    assert len(records) >= 1
    r = records[0]
    assert "Underfloor wheel lathe" in (r.get("title") or "")
    assert "tenders.example.com/t/123" in (r.get("url") or "")


def test_normalize_and_insert_with_dedup():
    db = SessionLocal()

    # process first email
    p1 = Path("tests/fixtures/email_alert_1.eml")
    inserted1 = process_eml_file(db, p1, source="EMAIL_ALERT")
    assert inserted1 >= 1

    count_after_first = db.query(TenderRaw).count()

    # process duplicate email with same URL -> should not increase count
    p2 = Path("tests/fixtures/email_alert_2_duplicate.eml")
    inserted2 = process_eml_file(db, p2, source="EMAIL_ALERT")
    count_after_second = db.query(TenderRaw).count()

    # second insert should be 0 because of dedup
    assert inserted2 == 0
    assert count_after_second == count_after_first

    db.close()
