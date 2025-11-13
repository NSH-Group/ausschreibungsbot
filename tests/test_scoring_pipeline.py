from app.models import Base, TenderRaw, TenderFiltered
from app.db import engine, SessionLocal
from app.scoring.pipeline import run_scoring


def setup_module():
    # create tables once (idempotent)
    Base.metadata.create_all(bind=engine)


def test_scoring_inserts_filtered_rows():
    db = SessionLocal()

    # relevant tender (should exceed threshold)
    db.add(
        TenderRaw(
            source="TED",
            external_id="X1",
            title="Underfloor wheel lathe for railway depot",
            description="Delivery and installation of a wheelset lathe (UWL)",
            country="DE",
            language="EN",
            cpv_codes="42620000",
            budget_amount=1_000_000,
            deadline_date=None,
            url="https://example/ted/1",
            published_at=None,
        )
    )

    # non-relevant tender (should stay below threshold)
    db.add(
        TenderRaw(
            source="TED",
            external_id="X2",
            title="Office chairs and desks",
            description="General office furniture",
            country="DE",
            language="EN",
            cpv_codes="39100000",
            budget_amount=20_000,
            deadline_date=None,
            url="https://example/ted/2",
            published_at=None,
        )
    )

    db.commit()

    inserted = run_scoring(db, keywords_csv_path="config/keywords_multilingual.csv", threshold=60)
    assert inserted >= 1

    rows = db.query(TenderFiltered).all()
    assert len(rows) >= 1
    assert rows[0].relevance_score >= 60

    db.close()
