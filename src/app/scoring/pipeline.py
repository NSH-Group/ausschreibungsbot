from __future__ import annotations

from typing import Tuple, List, Dict
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

from sqlalchemy.orm import Session

from app.models import TenderRaw, TenderFiltered
from app.scoring.nlp import tokenize
from app.scoring.keywords import load_keywords, RAIL_CONTEXT, TARGET_MARKETS


def fuzzy_contains(text_tokens: List[str], keyword: str, threshold: float = 0.85) -> bool:
    """Rough fuzzy match between token list and full keyword string."""
    if not keyword:
        return False
    kw_tokens = [w.lower() for w in keyword.split() if w]
    if not kw_tokens:
        return False

    text = " ".join(text_tokens)
    target = " ".join(kw_tokens)

    # whole-string similarity
    if SequenceMatcher(None, text, target).ratio() >= threshold:
        return True

    # token-wise similarity vs first keyword token
    for t in text_tokens:
        if SequenceMatcher(None, t, kw_tokens[0]).ratio() >= threshold:
            return True

    return False


def match_keywords(
    title: str,
    description: str,
    lang: str,
    keywords_per_lang: Dict[str, List[str]],
) -> List[str]:
    tokens = tokenize((title or "") + " " + (description or ""), lang_hint=lang)
    matched: List[str] = []

    for _, kws in keywords_per_lang.items():
        for kw in kws:
            if fuzzy_contains(tokens, kw):
                matched.append(kw)

    # dedupe, keep order
    return list(dict.fromkeys(matched))


def rail_context_signal(title: str, description: str, lang: str) -> float:
    tokens = tokenize((title or "") + " " + (description or ""), lang_hint=lang)
    ctx = RAIL_CONTEXT.get("de" if lang.startswith("de") else "en", [])
    hits = sum(1 for c in ctx if c in tokens)
    if hits >= 2:
        return 1.0
    if hits == 1:
        return 0.5
    return 0.0


def market_signal(country: str) -> float:
    if not country:
        return 0.0
    return 1.0 if country.upper() in TARGET_MARKETS else 0.0


def deadline_signal(deadline_date) -> float:
    if not deadline_date:
        return 0.0
    try:
        d = deadline_date
        if hasattr(d, "to_pydatetime"):
            d = d.to_pydatetime()
        if isinstance(d, datetime):
            d = d.date()
        today = datetime.now(timezone.utc).date()
        # require at least 7 days lead time
        if d and d >= today + timedelta(days=7):
            return 1.0
        return 0.0
    except Exception:
        return 0.0


def budget_signal(budget_amount) -> float:
    try:
        return 1.0 if budget_amount and float(budget_amount) > 0 else 0.0
    except Exception:
        return 0.0


def compute_score(
    keyword: float,
    rail: float,
    market: float,
    deadline: float,
    budget: float,
) -> int:
    """Score = 40*keyword + 30*rail_context + 15*market + 10*deadline + 5*budget."""
    s = 40 * keyword + 30 * rail + 15 * market + 10 * deadline + 5 * budget
    return int(round(s))


def score_record(
    rec: TenderRaw,
    keywords_per_lang: Dict[str, List[str]],
    threshold: int = 60,
) -> Tuple[int, List[str]]:
    lang = (rec.language or "en").lower()
    matched = match_keywords(rec.title or "", rec.description or "", lang, keywords_per_lang)
    keyword_sig = 1.0 if matched else 0.0
    rail_sig = rail_context_signal(rec.title or "", rec.description or "", lang)
    market_sig = market_signal(rec.country or "")
    deadline_sig = deadline_signal(rec.deadline_date)
    budget_sig = budget_signal(rec.budget_amount)

    score = compute_score(keyword_sig, rail_sig, market_sig, deadline_sig, budget_sig)
    return score, matched


def run_scoring(
    db: Session,
    keywords_csv_path: str = "config/keywords_multilingual.csv",
    threshold: int = 60,
) -> int:
    """Iterate over all TenderRaw, write matching tenders into TenderFiltered."""
    keywords_per_lang = load_keywords(keywords_csv_path)
    inserted = 0

    for rec in db.query(TenderRaw).all():
        score, matched = score_record(rec, keywords_per_lang, threshold=threshold)
        if score >= threshold:
            tf = TenderFiltered(
                raw_id=rec.id,
                relevance_score=score,
                matched_keywords=", ".join(matched),
                notes=None,
            )
            db.add(tf)
            inserted += 1

    db.commit()
    return inserted
