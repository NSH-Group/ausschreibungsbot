from sqlalchemy import Column, Integer, String, Text, Date, DateTime, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from .db import Base
class TenderRaw(Base):
    __tablename__='tenders_raw'
    id=Column(Integer, primary_key=True)
    source=Column(String(64), nullable=False)
    external_id=Column(String(128))
    title=Column(Text, nullable=False)
    description=Column(Text)
    country=Column(String(64))
    language=Column(String(8))
    cpv_codes=Column(Text)
    budget_amount=Column(Numeric)
    deadline_date=Column(Date)
    url=Column(Text, nullable=False)
    published_at=Column(DateTime(timezone=True))
    fetched_at=Column(DateTime(timezone=True), server_default=func.now())
    __table_args__=(UniqueConstraint('source','external_id', name='uq_raw_source_external'),)
class TenderFiltered(Base):
    __tablename__='tenders_filtered'
    id=Column(Integer, primary_key=True)
    raw_id=Column(Integer, nullable=False)
    relevance_score=Column(Integer, nullable=False)
    matched_keywords=Column(Text)
    notes=Column(Text)
    created_at=Column(DateTime(timezone=True), server_default=func.now())
class AlertSent(Base):
    __tablename__='alerts_sent'
    id=Column(Integer, primary_key=True)
    filtered_id=Column(Integer, nullable=False)
    channel=Column(String(32), nullable=False)
    sent_at=Column(DateTime(timezone=True), server_default=func.now())
