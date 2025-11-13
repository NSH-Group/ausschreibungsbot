import hashlib
import re
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import List, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from app.normalize import normalize_record
from app.repository import TenderRepository
from app.models import TenderRaw


# -------------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------------


def _hash_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def load_eml(path: Path) -> bytes:
    return path.read_bytes()


def parse_eml_bytes(raw: bytes) -> Tuple[Dict[str, str], str]:
    """Parse an .eml byte stream into (headers, body_text).

    - Tries text/plain part first
    - Falls back to text/html and strips tags
    """
    msg = BytesParser(policy=policy.default).parsebytes(raw)
    headers = {
        "subject": msg.get("Subject", ""),
        "from": msg.get("From", ""),
        "to": msg.get("To", ""),
        "date": msg.get("Date", ""),
    }

    body_text = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                body_text = part.get_content()
                break
        if not body_text:
            for part in msg.walk():
                ctype = part.get_content_type()
                if ctype == "text/html":
                    html = part.get_content()
                    body_text = _html_to_text(html)
                    break
    else:
        ctype = msg.get_content_type()
        if ctype == "text/plain":
            body_text = msg.get_content()
        elif ctype == "text/html":
            body_text = _html_to_text(msg.get_content())

    return headers, body_text


def _html_to_text(html: str) -> str:
    # very naive HTML tag stripper
    text = re.sub(r"<br\s*/?>", "\n", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# -------------------------------------------------------------------------
# Body parsing rules
# -------------------------------------------------------------------------


LINK_RE = re.compile(r"https?://\S+", re.I)
BUDGET_RE = re.compile(r"Budget[:\s]+([0-9\.,]+)", re.I)
DEADLINE_RE = re.compile(r"Deadline[:\s]+(\d{4}-\d{2}-\d{2})", re.I)
TITLE_RE = re.compile(r"Title[:\s]+(.+)", re.I)


def extract_records_from_body(body: str) -> List[Dict[str, Optional[str]]]:
    """Extract candidate records from a tender alert email body.

    This is heuristic and depends on your alert format. For now:
    - First URL in a paragraph == url
    - Budget: 'Budget: <number>'
    - Deadline: 'Deadline: YYYY-MM-DD'
    - Title: 'Title: <text>' or first line
    """
    records: List[Dict[str, Optional[str]]] = []
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    if not lines:
        return records

    # For simplicity: treat whole body as one record per URL
    urls = LINK_RE.findall(body)
    if not urls:
        return records

    budget = None
    m = BUDGET_RE.search(body)
    if m:
        budget = m.group(1).strip()

    deadline = None
    m = DEADLINE_RE.search(body)
    if m:
        deadline = m.group(1).strip()

    title = None
    m = TITLE_RE.search(body)
    if m:
        title = m.group(1).strip()
    else:
        # fallback: first non-empty line
        title = lines[0]

    description = body[:4000]  # truncate long bodies for DB

    for url in urls:
        rec = {
            "title": title,
            "description": description,
            "url": url,
            "budget": budget,
            "deadline": deadline,
        }
        records.append(rec)

    return records


def normalize_email_records(
    source: str,
    raw_records: List[Dict[str, Optional[str]]],
) -> List[Dict]:
    normalized: List[Dict] = []
    for r in raw_records:
        url = r.get("url") or ""
        external_id = _hash_url(url) if url else None
        norm = normalize_record(
            source=source,
            external_id=external_id or "",
            title=r.get("title") or "",
            description=r.get("description") or "",
            url=url,
            country=None,
            language=None,
            cpv=None,
            budget=r.get("budget"),
            deadline=r.get("deadline"),
            published_at=None,
        )
        normalized.append(norm)
    return normalized


def insert_normalized_with_dedup(
    db: Session,
    source: str,
    normalized_records: List[Dict],
) -> int:
    """Insert normalized records into tenders_raw, dedup by external_id or url hash.

    Dedup strategy:
    - compute url hash again
    - skip if any existing TenderRaw has same source + external_id OR same url
    """
    repo = TenderRepository(db)
    inserted = 0
    for rec in normalized_records:
        url = rec.get("url") or ""
        external_id = rec.get("external_id") or _hash_url(url)
        # check for duplicates
        existing = (
            db.query(TenderRaw)
            .filter(
                (TenderRaw.source == source)
                & (
                    (TenderRaw.external_id == external_id)
                    | (TenderRaw.url == url)
                )
            )
            .first()
        )
        if existing:
            continue
        rec["external_id"] = external_id
        repo.add_raw(rec)
        inserted += 1

    db.commit()
    return inserted


def process_eml_file(db: Session, path: Path, source: str = "EMAIL_ALERT") -> int:
    """High-level helper used in tests: parse .eml and insert deduped tenders_raw rows."""
    raw_bytes = load_eml(path)
    headers, body = parse_eml_bytes(raw_bytes)
    raw_records = extract_records_from_body(body)
    normalized = normalize_email_records(source, raw_records)
    return insert_normalized_with_dedup(db, source, normalized)
