import os
import time
import random
from pathlib import Path
from typing import List, Dict, Optional

from sqlalchemy.orm import Session

from app.normalize import normalize_record
from app.repository import TenderRepository

# -------------------------------------------------------------------------
# Configuration (adapt to your portal)
# -------------------------------------------------------------------------

# These must be set in the environment:
#   PORTAL_BASE_URL  - e.g. "https://tenders.example.com"
#   PORTAL_USER      - login username
#   PORTAL_PASS      - login password
# Optional:
#   PORTAL_STORAGE_STATE - path to storage_state json for cookies (default .playwright/portal_state.json)

SOURCE_NAME = "LOGIN_PORTAL"

STORAGE_STATE_PATH = os.getenv("PORTAL_STORAGE_STATE", ".playwright/portal_state.json")


# -------------------------------------------------------------------------
# HTML parsing helpers (pure functions, easy to test)
# -------------------------------------------------------------------------

def parse_results_html(html: str) -> List[Dict[str, Optional[str]]]:
    """Parse a search results HTML page into a list of raw records.

    Assumes a structure like:

        <div class="result">
          <a class="result-title" href="/t/123">Underfloor wheel lathe</a>
          <span class="result-budget">Budget: 1000000</span>
          <span class="result-deadline">Deadline: 2025-12-31</span>
          <div class="result-description">...</div>
          <span class="result-country">Country: DE</span>
        </div>

    Adjust CSS classes to your real portal and keep this function pure.
    """
    import re
    results: List[Dict[str, Optional[str]]] = []

    # Split by result blocks
    blocks = re.findall(r'<div class="result">(.*?)</div>', html, flags=re.S | re.I)

    def _extract(pattern: str, text: str) -> Optional[str]:
        m = re.search(pattern, text, flags=re.S | re.I)
        if not m:
            return None
        return m.group(1).strip()

    for block in blocks:
        title = _extract(r'<a[^>]*class="result-title"[^>]*>(.*?)</a>', block)
        url = _extract(r'<a[^>]*class="result-title"[^>]*href="([^"]+)"', block)
        budget = _extract(r'<span[^>]*class="result-budget"[^>]*>\s*Budget:\s*(.*?)</span>', block)
        deadline = _extract(r'<span[^>]*class="result-deadline"[^>]*>\s*Deadline:\s*(.*?)</span>', block)
        desc = _extract(r'<div[^>]*class="result-description"[^>]*>(.*?)</div>', block)
        country = _extract(r'<span[^>]*class="result-country"[^>]*>\s*Country:\s*(.*?)</span>', block)

        results.append(
            {
                "title": title,
                "url": url,
                "budget": budget,
                "deadline": deadline,
                "description": desc,
                "country": country,
            }
        )

    return results


def normalize_records(raw_records: List[Dict[str, Optional[str]]]) -> List[Dict]:
    """Map parsed HTML records to DB-ready normalized dicts using normalize_record()."""
    normalized: List[Dict] = []
    for i, r in enumerate(raw_records, start=1):
        url = r.get("url") or ""
        if url and url.startswith("/"):
            base = os.getenv("PORTAL_BASE_URL", "").rstrip("/")
            url = f"{base}{url}"
        norm = normalize_record(
            source=SOURCE_NAME,
            external_id=str(i),
            title=r.get("title") or "",
            description=r.get("description") or "",
            url=url,
            country=r.get("country"),
            language=None,
            cpv=None,
            budget=r.get("budget"),
            deadline=r.get("deadline"),
            published_at=None,
        )
        normalized.append(norm)
    return normalized


def ingest_results_html(db: Session, html: str) -> int:
    """Convenience for tests: parse HTML and insert into tenders_raw via ORM."""
    raw_records = parse_results_html(html)
    normalized = normalize_records(raw_records)
    repo = TenderRepository(db)
    return repo.add_many_raw(normalized)


# -------------------------------------------------------------------------
# Playwright-based scraper template (NOT used in unit tests)
# -------------------------------------------------------------------------

def _get_credentials() -> Dict[str, str]:
    base_url = os.getenv("PORTAL_BASE_URL")
    user = os.getenv("PORTAL_USER")
    password = os.getenv("PORTAL_PASS")
    if not base_url or not user or not password:
        raise RuntimeError("PORTAL_BASE_URL, PORTAL_USER, and PORTAL_PASS must be set in environment.")
    return {"base_url": base_url.rstrip("/"), "user": user, "password": password}


def _polite_delay():
    """Sleep a small random time between requests to be polite."""
    time.sleep(random.uniform(1.5, 3.5))


def run_playwright_search(keywords: str, max_pages: int = 3) -> List[Dict]:
    """Run a keyword search on the login portal using Playwright.

    - Headless browser
    - Uses env PORTAL_USER/PASS/BASE_URL
    - Stores cookies in STORAGE_STATE_PATH
    - You MUST adjust selectors and URLs to your actual portal.
    - Respect robots.txt / Terms of Service. Do NOT use this if not allowed.
    - No captcha bypass.
    """
    creds = _get_credentials()

    try:
        from playwright.sync_api import sync_playwright  # type: ignore
    except Exception as exc:
        raise RuntimeError("playwright is not installed. Install with 'pip install playwright' and run 'playwright install'.") from exc

    storage_path = Path(STORAGE_STATE_PATH)
    storage_path.parent.mkdir(parents=True, exist_ok=True)

    all_records: List[Dict] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context_args = {}
        if storage_path.exists():
            context_args["storage_state"] = str(storage_path)
        context = browser.new_context(**context_args)
        page = context.new_page()

        # --- Login step (adapt selectors!) ---
        if not storage_path.exists():
            page.goto(f"{creds['base_url']}/login", wait_until="networkidle")
            _polite_delay()
            page.fill('input[name="username"]', creds["user"])
            page.fill('input[name="password"]', creds["password"])
            _polite_delay()
            page.click('button[type="submit"]')
            page.wait_for_load_state("networkidle")
            _polite_delay()
            # Save cookies/session
            context.storage_state(path=str(storage_path))

        # --- Search step (adapt URL and selectors!) ---
        search_url = f"{creds['base_url']}/search"
        page.goto(search_url, wait_until="networkidle")
        _polite_delay()
        # Example: simple search form
        try:
            page.fill('input[name="q"]', keywords)
        except Exception:
            # Adjust selector for your portal
            pass
        _polite_delay()
        try:
            page.click('button[type="submit"]')
        except Exception:
            pass
        page.wait_for_load_state("networkidle")
        _polite_delay()

        current_page = 1
        while current_page <= max_pages:
            html = page.content()
            raw_records = parse_results_html(html)
            all_records.extend(normalize_records(raw_records))

            # Try to click "next" (adapt selector for your portal)
            try:
                next_button = page.query_selector("a.next, button.next")
                if not next_button:
                    break
                next_button.click()
                page.wait_for_load_state("networkidle")
                _polite_delay()
                current_page += 1
            except Exception:
                break

        browser.close()

    return all_records


def scrape_and_ingest(db: Session, keywords: str, max_pages: int = 3) -> int:
    """High-level helper: run Playwright search and store results in DB."""
    records = run_playwright_search(keywords=keywords, max_pages=max_pages)
    repo = TenderRepository(db)
    return repo.add_many_raw(records)
