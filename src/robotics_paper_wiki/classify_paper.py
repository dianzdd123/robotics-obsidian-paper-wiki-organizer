"""
classify_paper.py
Rule-based classification of papers into research themes and applications.

Rules:
  - Every paper gets exactly ONE primary_theme (highest keyword score).
  - Papers may have secondary_themes (any theme scoring >= 45% of primary).
  - Papers may belong to MULTIPLE applications.
  - General_Robotics is the universal fallback application.
  - Scoring: each keyword hit in (title + abstract + filename + folder) = 1 pt;
    title hits count double.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from .metadata_extract import PaperMetadata
from .utils import safe_component

_SECONDARY_MIN_FRACTION = 0.45
_THEME_MIN_SCORE        = 1

_STOPWORDS = {
    "a", "an", "the", "for", "of", "in", "on", "to", "and", "with", "based",
    "via", "using", "from", "by", "at", "is", "are", "its", "as", "be", "or",
    "that", "this", "we", "our", "their", "has", "have", "been", "was", "were",
    "can", "into", "under", "over", "new", "novel", "toward", "towards",
    "within", "during", "between", "approach", "method", "system", "framework",
    "model", "network", "learning", "robot", "robotic", "paper", "study",
    "work", "real", "time", "high", "low", "large", "small", "multi",
    "multiple", "deep", "two", "three", "one", "first",
}


@dataclass
class Classification:
    primary_theme:     str
    secondary_themes:  list[str]      = field(default_factory=list)
    applications:      list[str]      = field(default_factory=list)
    year_bucket:       Optional[str]  = None
    title_keywords:    list[str]      = field(default_factory=list)
    theme_scores:      dict[str, int] = field(default_factory=dict)
    app_scores:        dict[str, int] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def classify_paper(meta: PaperMetadata, config: dict) -> Classification:
    """Classify *meta* using keyword lists from *config*."""
    search_text = _build_search_text(meta)
    title_text  = (meta.title or "").lower()

    # Theme scoring
    theme_cfg    = config.get("theme_keywords", {})
    raw_scores   = {
        theme: _score_keywords(tcfg.get("keywords", []), search_text, title_text)
        for theme, tcfg in theme_cfg.items()
    }
    sorted_themes = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    primary_theme, primary_score = sorted_themes[0] if sorted_themes else ("Unclassified", 0)

    if primary_score < _THEME_MIN_SCORE:
        primary_theme = "Unclassified"

    secondary = []
    if primary_score > 0:
        cutoff = primary_score * _SECONDARY_MIN_FRACTION
        for theme, score in sorted_themes[1:]:
            if score >= max(cutoff, _THEME_MIN_SCORE):
                secondary.append(theme)

    # Application scoring
    app_cfg    = config.get("application_keywords", {})
    app_scores = {
        app: _score_keywords(acfg.get("keywords", []), search_text, title_text)
        for app, acfg in app_cfg.items()
    }
    matched_apps = [
        app for app, sc in app_scores.items()
        if sc >= _THEME_MIN_SCORE and app != "General_Robotics"
    ]
    if not matched_apps:
        matched_apps = ["General_Robotics"]

    return Classification(
        primary_theme    = primary_theme,
        secondary_themes = secondary,
        applications     = matched_apps,
        year_bucket      = _year_bucket(meta.year),
        title_keywords   = _extract_title_keywords(meta.title, n=3),
        theme_scores     = raw_scores,
        app_scores       = app_scores,
    )


def proposed_filename(meta: PaperMetadata, clf: Classification) -> str:
    """Build the canonical filename: YEAR-VENUE-Kw1-Kw2-Kw3-FirstAuthor.pdf"""
    year       = str(meta.year)       if meta.year        else "XXXX"
    venue      = safe_component(meta.venue)    if meta.venue       else "Unknown-Venue"
    first_auth = safe_component(meta.first_author) if meta.first_author else "Unknown"
    keywords   = clf.title_keywords or ["Paper"]

    parts = [year, venue] + keywords[:3] + [first_auth]
    name  = "-".join(safe_component(p) for p in parts)
    return f"{name}.pdf"


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------
def _build_search_text(meta: PaperMetadata) -> str:
    parts = [
        meta.title or "",
        meta.abstract or "",
        re.sub(r"[-_]", " ", meta.filename),
        re.sub(r"[-_]", " ", meta.source_folder),
        meta.head_text[:1000] if meta.head_text else "",
    ]
    return " ".join(parts).lower()


def _score_keywords(keywords: list[str], search_text: str, title_text: str) -> int:
    score = 0
    for kw in keywords:
        kw_lower = kw.lower()
        if kw_lower in search_text:
            score += 1
        if kw_lower in title_text:
            score += 1  # extra point for title hit
    return score


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------
def _year_bucket(year: Optional[int]) -> str:
    if year is None:
        return "Unknown"
    if year < 2018:
        return "Pre-2018"
    start = (year // 2) * 2
    return f"{start}-{start + 1}"


def _extract_title_keywords(title: Optional[str], n: int = 3) -> list[str]:
    if not title:
        return []
    words     = re.findall(r"[A-Za-z']+", title)
    meaningful = [
        w.capitalize()
        for w in words
        if w.lower() not in _STOPWORDS and len(w) > 2
    ]
    seen: set[str] = set()
    unique: list[str] = []
    for w in meaningful:
        if w not in seen:
            seen.add(w)
            unique.append(w)
    return unique[:n]
