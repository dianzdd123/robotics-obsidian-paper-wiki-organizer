"""
duplicate_detection.py
Detect duplicate papers by DOI, PDF hash, normalised title, and canonical filename.

Detection priority (strongest to weakest):
  1. DOI match            — same DOI = same paper
  2. SHA-256 hash match   — identical binary content
  3. Normalised title     — same title after stripping punctuation/case
  4. Canonical stem       — same YEAR-VENUE-Kw-Kw-Kw-Author stem (ignoring _2/_3 suffix)
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class DuplicateInfo:
    is_duplicate:   bool
    match_type:     str             # "doi" | "hash" | "title" | "filename" | "none"
    matched_record: Optional[dict] = None


def compute_pdf_hash(pdf_path: Path) -> str:
    """Return the SHA-256 hex digest of the PDF's binary content."""
    h = hashlib.sha256()
    with open(pdf_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65_536), b""):
            h.update(chunk)
    return h.hexdigest()


def normalize_title(title: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace for comparison."""
    title = unicodedata.normalize("NFKC", title.lower())
    title = re.sub(r"[^\w\s]", "", title)
    return re.sub(r"\s+", " ", title).strip()


def _strip_suffix(canonical: str) -> str:
    """Remove _2, _3 ... suffix so 'file_2.pdf' and 'file.pdf' compare equal."""
    stem = canonical.replace(".pdf", "")
    return re.sub(r"_\d+$", "", stem)


def check_duplicate(
    doi:        Optional[str],
    title:      Optional[str],
    canonical:  str,
    pdf_hash:   Optional[str],
    existing_records: list[dict],
) -> DuplicateInfo:
    """Check if a candidate paper is a duplicate of any record in *existing_records*.

    Args:
        doi:              Candidate DOI (may be None).
        title:            Candidate title (may be None).
        canonical:        Proposed canonical filename (e.g. '2024-ICRA-...-Zhang.pdf').
        pdf_hash:         SHA-256 hash of the candidate PDF (may be None).
        existing_records: List of record dicts from papers_catalog.json.

    Returns:
        DuplicateInfo with is_duplicate=True and match details if found.
    """
    doi_norm   = doi.lower().strip()   if doi   else None
    title_norm = normalize_title(title) if title else None
    stem       = _strip_suffix(canonical)

    for rec in existing_records:
        # 1. DOI match
        rec_doi = (rec.get("doi") or "").lower().strip()
        if doi_norm and rec_doi and doi_norm == rec_doi:
            return DuplicateInfo(True, "doi", rec)

        # 2. Hash match
        rec_hash = rec.get("pdf_hash") or ""
        if pdf_hash and rec_hash and pdf_hash == rec_hash:
            return DuplicateInfo(True, "hash", rec)

        # 3. Title match
        rec_title = rec.get("title") or ""
        if title_norm and rec_title:
            if title_norm == normalize_title(rec_title):
                return DuplicateInfo(True, "title", rec)

        # 4. Canonical filename stem match
        rec_stem = _strip_suffix(rec.get("new_filename") or "")
        if stem and rec_stem and stem == rec_stem:
            return DuplicateInfo(True, "filename", rec)

    return DuplicateInfo(False, "none")


def disambiguate_canonicals(
    raw: list[tuple],
) -> tuple[list[tuple], set[str]]:
    """Resolve canonical name collisions by appending _2, _3, ...

    Keeps the first occurrence unchanged; suffixes all subsequent ones.

    Args:
        raw: List of (pdf_path, meta, clf, canonical) 4-tuples.

    Returns:
        (disambiguated list of 5-tuples with was_collision flag,
         set of original canonical names that had collisions)
    """
    from collections import defaultdict

    count_map: dict[str, int] = defaultdict(int)
    for _, _, _, c in raw:
        count_map[c] += 1
    collisions = {c for c, n in count_map.items() if n > 1}

    seen: dict[str, int] = defaultdict(int)
    result = []
    for pdf_path, meta, clf, canonical in raw:
        was_collision = canonical in collisions
        seen[canonical] += 1
        if seen[canonical] > 1:
            stem     = canonical.replace(".pdf", "")
            canonical = f"{stem}_{seen[canonical]}.pdf"
        result.append((pdf_path, meta, clf, canonical, was_collision))

    return result, collisions
