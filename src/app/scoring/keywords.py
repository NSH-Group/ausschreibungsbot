import csv
from typing import Dict, List

def load_keywords(csv_path: str) -> Dict[str, List[str]]:
    """Load multilingual keywords from CSV into dict: {lang: [keywords...]}"""
    per_lang: Dict[str, List[str]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            lang = (row.get("lang") or "en").strip().lower()
            kw = (row.get("keyword") or "").strip()
            if not kw:
                continue
            per_lang.setdefault(lang, []).append(kw)
    return per_lang


# Words that indicate rail / wheelset / workshop context
RAIL_CONTEXT = {
    "en": [
        "rail",
        "railway",
        "wheel",
        "wheelset",
        "underfloor",
        "lathe",
        "bogie",
        "workshop",
        "depot",
        "track",
    ],
    "de": [
        "bahn",
        "eisenbahn",
        "rad",
        "radsatz",
        "unterflur",
        "drehmaschine",
        "werkstatt",
        "depot",
        "gleis",
    ],
}

# Markets you care about (can be extended)
TARGET_MARKETS = {
    "DE",
    "AT",
    "CH",
    "PL",
    "CZ",
    "FR",
    "IT",
    "ES",
    "PT",
    "UK",
    "IE",
    "NL",
    "BE",
    "SE",
    "NO",
    "FI",
    "DK",
    "US",
    "CA",
    "AU",
    "NZ",
    "AE",
    "SA",
    "IN",
    "JP",
    "KR",
    "SG",
}
