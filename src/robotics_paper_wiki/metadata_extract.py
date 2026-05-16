"""
metadata_extract.py
Extract bibliographic metadata from a PDF file using PyMuPDF.

Extraction pipeline (priority order):
  1. PDF document metadata fields (title, author)
  2. Page-1 layout analysis — largest-font spans -> title
  3. Plain-text scan of first 3 pages — abstract, DOI, year, venue, authors
  4. Filename stem parsing — year, venue shortcode, first-author surname
  5. Parent-folder name — fallback year hint

A confidence score (0.0-1.0) is computed from which fields were found.
Papers scoring below the config threshold are flagged for manual review.
"""

from __future__ import annotations

import re
import unicodedata
import logging
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import fitz  # PyMuPDF

from .utils import clean_text

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Regex patterns
# ---------------------------------------------------------------------------
_DOI_RE      = re.compile(r"\b(10\.\d{4,}/[^\s,;>\]]+)", re.I)
_YEAR_RE     = re.compile(r"\b(20[0-2]\d|199\d)\b")
_ABSTRACT_RE = re.compile(
    r"(?:Abstract|ABSTRACT)[^\w]?\s*[--:—–]?\s*(.{80,}?)"
    r"(?=\n{2,}|\n[A-Z][A-Z\s]{3,}\n|\nI[\.\s]|\nINTRODUCTION|\nIndex Terms|\nKeywords)",
    re.S | re.I,
)

# Words that look like surnames (CamelCase, 3+ chars) but are topic terms.
_TOPIC_WORDS = {
    "Clamp", "Pouring", "Control", "Robot", "Learning", "Vision", "Motion",
    "Sensor", "System", "Based", "Deep", "Model", "Field", "Force", "Grid",
    "Twist", "Patch", "Depth", "Vivo", "Micro", "Nano", "Real", "Time",
    "Dual", "Joint", "Soft", "Rigid", "Adaptive", "Multi", "Single",
    "Novel", "Fast", "Laser", "Guided", "Smart", "Human", "Aided",
}

# Default venue aliases — overridden by config at runtime
DEFAULT_VENUE_ALIASES: dict[str, list[str]] = {
    "ICRA":   ["International Conference on Robotics and Automation", "ICRA"],
    "IROS":   ["Intelligent Robots and Systems", "IROS"],
    "MARSS":  ["MARSS"],
    "TASE":   ["IEEE Transactions on Automation Science", "T-ASE", "TASE"],
    "RAL":    ["Robotics and Automation Letters", "RA-L", "RAL"],
    "TRO":    ["IEEE Transactions on Robotics", "T-RO", "TRO"],
    "IJRR":   ["International Journal of Robotics Research", "IJRR"],
    "RSS":    ["Robotics: Science and Systems", "RSS"],
    "ACS":    ["ACS Photonics", "ACS Nano", "ACS Applied", "acsphotonics"],
    "Advanced-Science": ["Advanced Science"],
    "AIS":    ["Advanced Intelligent Systems"],
    "Nature": ["Nature Communications", "Nature Robotics"],
    "Science-Robotics": ["Science Robotics", "scirobotics"],
    "Micromachines": ["Micromachines", "micromachines"],
    "Book":   ["Book Chapter", "book chapter"],
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class PaperMetadata:
    source_path:   str
    filename:      str
    source_folder: str

    title:         Optional[str]  = None
    authors:       list[str]      = field(default_factory=list)
    first_author:  Optional[str]  = None
    year:          Optional[int]  = None
    venue:         Optional[str]  = None
    doi:           Optional[str]  = None
    abstract:      Optional[str]  = None

    # Raw text from first 3 pages — available to classify and summarise
    head_text:         str        = ""
    confidence:        float      = 0.0
    extraction_notes:  list[str]  = field(default_factory=list)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def extract_metadata(
    pdf_path: Path,
    venue_aliases: dict | None = None,
) -> PaperMetadata:
    """Return a PaperMetadata for *pdf_path*. Never raises; errors go to notes."""
    aliases = venue_aliases or DEFAULT_VENUE_ALIASES
    path    = Path(pdf_path)

    meta = PaperMetadata(
        source_path   = str(path),
        filename      = path.name,
        source_folder = path.parent.name,
    )

    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        meta.extraction_notes.append(f"fitz open error: {exc}")
        return meta

    try:
        _from_pdf_metadata(doc, meta)
        head_text      = _extract_head_text(doc, pages=3)
        meta.head_text = head_text
        _from_text(head_text, meta, aliases)
        _from_page1_layout(doc, meta)
        _from_filename(path, meta, aliases)
        _from_folder(path, meta)
        _finalise(meta)
    except Exception as exc:
        meta.extraction_notes.append(f"extraction error: {exc}")
        logger.debug("Extraction error for %s: %s", path.name, exc, exc_info=True)
    finally:
        doc.close()

    _compute_confidence(meta)
    return meta


# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------
def _from_pdf_metadata(doc: fitz.Document, meta: PaperMetadata) -> None:
    pdf_meta   = doc.metadata or {}
    raw_title  = (pdf_meta.get("title")  or "").strip()
    raw_author = (pdf_meta.get("author") or "").strip()

    if raw_title and len(raw_title) > 6 and not _looks_like_junk(raw_title):
        meta.title = clean_text(raw_title)
        meta.extraction_notes.append("title: pdf-metadata")

    if raw_author and len(raw_author) > 2:
        meta.authors = _parse_author_string(raw_author)
        if meta.authors:
            meta.first_author = _surname(meta.authors[0])
            meta.extraction_notes.append("authors: pdf-metadata")


def _from_page1_layout(doc: fitz.Document, meta: PaperMetadata) -> None:
    if meta.title:
        return
    try:
        page   = doc[0]
        blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_LIGATURES)["blocks"]
        spans  = []
        h      = page.rect.height

        for blk in blocks:
            if blk.get("type") != 0:
                continue
            for line in blk.get("lines", []):
                for sp in line.get("spans", []):
                    txt = sp["text"].strip()
                    y   = sp["bbox"][1]
                    if len(txt) >= 4 and y < h * 0.65:
                        spans.append({"text": txt, "size": sp["size"], "y": y})

        if not spans:
            return

        max_size    = max(s["size"] for s in spans)
        title_spans = [s for s in spans if s["size"] >= max_size * 0.80]
        title_spans.sort(key=lambda s: s["y"])

        candidate = clean_text(" ".join(s["text"] for s in title_spans[:8]))
        if len(candidate) > 10 and not _looks_like_junk(candidate):
            meta.title = candidate
            meta.extraction_notes.append("title: layout-analysis")
    except Exception as exc:
        logger.debug("Layout title failed: %s", exc)


def _from_text(text: str, meta: PaperMetadata, aliases: dict) -> None:
    if not meta.abstract:
        m = _ABSTRACT_RE.search(text)
        if m:
            abstract = clean_text(m.group(1))
            if len(abstract) > 80:
                meta.abstract = abstract[:2000]
                meta.extraction_notes.append("abstract: regex")

    if not meta.doi:
        m = _DOI_RE.search(text)
        if m:
            meta.doi = m.group(1).rstrip(".")
            meta.extraction_notes.append("doi: regex")

    if not meta.year:
        years = _YEAR_RE.findall(text)
        if years:
            meta.year = int(Counter(years).most_common(1)[0][0])
            meta.extraction_notes.append("year: text-frequency")

    if not meta.venue:
        meta.venue = _detect_venue(text, aliases)
        if meta.venue:
            meta.extraction_notes.append("venue: text-scan")

    if not meta.authors:
        _detect_authors_from_text(text, meta)


def _from_filename(path: Path, meta: PaperMetadata, aliases: dict) -> None:
    stem = path.stem

    if not meta.year:
        m = _YEAR_RE.search(stem)
        if m:
            meta.year = int(m.group(1))
            meta.extraction_notes.append("year: filename")

    # Structured filename: YEAR-VENUE-... or YEAR_VENUE_...
    _structured = bool(re.match(r"^(20\d{2}|199\d)[_\-][A-Z]", stem))

    if _structured:
        fn_venue = _detect_venue(stem, aliases)
        if fn_venue:
            meta.venue = fn_venue
            meta.extraction_notes.append("venue: filename")
    elif not meta.venue:
        fn_venue = _detect_venue(stem, aliases)
        if fn_venue:
            meta.venue = fn_venue
            meta.extraction_notes.append("venue: filename")

    if not meta.first_author and _structured:
        parts = [
            p for p in re.split(r"[-_\s]+", stem)
            if p and not _YEAR_RE.fullmatch(p) and not p.isupper() and len(p) > 2
        ]
        for token in reversed(parts):
            if re.match(r"^[A-Z][a-z]{2,}$", token) and token not in _TOPIC_WORDS:
                meta.first_author = token
                meta.extraction_notes.append("first_author: filename")
                break

    if not meta.title:
        candidate = clean_text(re.sub(r"[-_]+", " ", _YEAR_RE.sub("", stem)))
        if len(candidate) > 8:
            meta.title = candidate
            meta.extraction_notes.append("title: filename")


def _from_folder(path: Path, meta: PaperMetadata) -> None:
    folder = path.parent.name
    if not meta.year:
        m = _YEAR_RE.search(folder)
        if m:
            meta.year = int(m.group(1))
            meta.extraction_notes.append("year: folder-name")


def _finalise(meta: PaperMetadata) -> None:
    if meta.authors and not meta.first_author:
        meta.first_author = _surname(meta.authors[0])


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def _extract_head_text(doc: fitz.Document, pages: int = 3) -> str:
    return "\n".join(doc[i].get_text("text") for i in range(min(pages, len(doc))))


def _detect_venue(text: str, aliases: dict) -> Optional[str]:
    text_lower = text.lower()
    for short_name, patterns in aliases.items():
        for pat in patterns:
            if pat.lower() in text_lower:
                return short_name
    return None


def _detect_authors_from_text(text: str, meta: PaperMetadata) -> None:
    abstract_pos = re.search(r"\bAbstract\b", text, re.I)
    head = text[: abstract_pos.start()] if abstract_pos else text[:800]
    pattern = re.compile(
        r"^([A-Z][a-z]+(?:\s+[A-Z][a-z]*)+"
        r"(?:[,;]\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]*)+){1,15})$",
        re.MULTILINE,
    )
    for m in pattern.finditer(head):
        authors = [a.strip() for a in re.split(r"[,;]", m.group(1)) if a.strip()]
        if 2 <= len(authors) <= 20:
            meta.authors      = authors
            meta.first_author = _surname(authors[0])
            meta.extraction_notes.append("authors: text-heuristic")
            return


def _parse_author_string(raw: str) -> list[str]:
    for sep in (";", " and ", ","):
        if sep in raw:
            parts = [p.strip() for p in raw.split(sep) if p.strip()]
            if parts:
                return parts
    return [raw.strip()]


def _surname(author: str) -> str:
    parts = author.strip().split()
    return parts[-1] if parts else author


def _looks_like_junk(text: str) -> bool:
    if len(text) < 6:
        return True
    if re.match(r"^[A-F0-9\-]{32,}$", text):
        return True
    if re.search(r"[/\\]", text):
        return True
    return False


def _compute_confidence(meta: PaperMetadata) -> None:
    score = 0.0
    if meta.title and not meta.title.startswith("title: filename"):
        score += 0.30
    elif meta.title:
        score += 0.10
    if meta.year:     score += 0.20
    if meta.venue:    score += 0.20
    if meta.authors:  score += 0.15
    if meta.doi:      score += 0.10
    if meta.abstract: score += 0.05
    meta.confidence = round(min(score, 1.0), 3)
