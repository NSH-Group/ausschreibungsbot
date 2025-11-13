import re
from typing import List, Optional, Callable, Union

def _try_import_spacy():
    """Try to import spaCy; return module or None."""
    try:
        import spacy  # type: ignore
        return spacy
    except Exception:
        return None


def get_tokenizer(lang: str) -> Union[Callable[[str], List[str]], "spacy.language.Language"]:
    """Return spaCy model for en/de if available, else simple fallback tokenizer."""
    spacy = _try_import_spacy()
    if spacy:
        try:
            if lang.startswith("en"):
                return spacy.load("en_core_web_sm")
            if lang.startswith("de"):
                return spacy.load("de_core_news_sm")
        except Exception:
            # model not installed -> fallback
            pass

    def _fallback(text: str) -> List[str]:
        return [t for t in re.findall(r"[A-Za-zÄÖÜäöüß\-]+", text.lower()) if t]

    return _fallback


def tokenize(text: str, lang_hint: Optional[str] = None) -> List[str]:
    """Tokenize + lemmatize (if spaCy available), else simple regex split."""
    if not text:
        return []

    lang = (lang_hint or "en").lower()
    tok = get_tokenizer(lang)

    try:
        # Fallback-function: just call
        if callable(tok) and not hasattr(tok, "pipe"):
            return tok(text)

        # spaCy Doc
        doc = tok(text)  # type: ignore
        tokens: List[str] = []
        for t in doc:
            lemma = (t.lemma_ or "").strip().lower()
            if not lemma:
                lemma = t.text.lower()
            if lemma:
                tokens.append(lemma)
        return tokens
    except Exception:
        return re.findall(r"[A-Za-zÄÖÜäöüß\-]+", text.lower())
