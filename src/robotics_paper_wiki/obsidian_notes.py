"""
obsidian_notes.py
Generate Obsidian Markdown notes: paper notes, link stubs, index notes.

All PDF links use vault-relative paths so notes are portable across machines.
Example:
    [[01_Renamed_PDFs_By_Research_Theme/Robot_Learning/2024/2024-ICRA-Paper-Zhang.pdf|Open PDF]]
"""

from __future__ import annotations

import textwrap
from datetime import date
from typing import Optional

from .metadata_extract import PaperMetadata
from .classify_paper import Classification
from .utils import year_folder

_TODAY = date.today().isoformat()


# ---------------------------------------------------------------------------
# Paper note
# ---------------------------------------------------------------------------
def generate_paper_note(
    meta:           PaperMetadata,
    clf:            Classification,
    canonical_name: str,
) -> str:
    """Return the full text of an Obsidian note (frontmatter + body)."""
    title        = _resolve_title(meta, canonical_name)
    authors_yaml = _authors_yaml(meta.authors)
    tags         = _build_tags(clf)
    abstract     = meta.abstract or "_Abstract not extracted — open the PDF._"
    abstract_fmt = textwrap.fill(abstract, width=100)

    secondary = (
        "\n".join(f"  - {t}" for t in clf.secondary_themes)
        if clf.secondary_themes else "  - _none_"
    )
    applications = (
        "\n".join(f"  - {a}" for a in clf.applications)
        if clf.applications else "  - General_Robotics"
    )

    yfolder  = year_folder(meta.year)
    pdf_link = (
        f"[[01_Renamed_PDFs_By_Research_Theme"
        f"/{clf.primary_theme}/{yfolder}/{canonical_name}|Open PDF]]"
    )

    return f"""\
---
title: "{_escape_yaml(title)}"
authors:
{authors_yaml}
year: {meta.year or "null"}
venue: {meta.venue or "null"}
doi: {meta.doi or "null"}
primary_theme: {clf.primary_theme}
secondary_themes:
{secondary}
applications:
{applications}
year_bucket: "{clf.year_bucket}"
confidence: {meta.confidence}
source_file: "{meta.filename}"
source_folder: "{meta.source_folder}"
date_added: {_TODAY}
tags:
{tags}
---

# {title}

## Abstract

> {abstract_fmt}

## Classification

| Field | Value |
|---|---|
| Primary Theme | `{clf.primary_theme}` |
| Secondary Themes | {", ".join(f"`{t}`" for t in clf.secondary_themes) or "—"} |
| Applications | {", ".join(f"`{a}`" for a in clf.applications)} |
| Year | {meta.year or "—"} |
| Venue | {meta.venue or "—"} |
| Year Bucket | {clf.year_bucket} |
| Confidence | {meta.confidence:.2f} |

## Source

- **Canonical PDF:** {pdf_link}
- **Original file:** `{meta.source_folder}/{meta.filename}`
{_doi_line(meta.doi)}

## Notes

> _Add your own annotations here._

## Related Papers

> _Link related notes here using `[[note-name]]`._
"""


# ---------------------------------------------------------------------------
# Link stub notes (no PDF copies in these folders)
# ---------------------------------------------------------------------------
def generate_application_link_note(
    meta:           PaperMetadata,
    clf:            Classification,
    canonical_name: str,
    application:    str,
) -> str:
    """Stub note under By_Application/<App>/.

    Uses a relative path 3 levels up to reach 01_Renamed_PDFs_By_Research_Theme.
    """
    title   = _resolve_title(meta, canonical_name)
    yfolder = year_folder(meta.year)
    pdf_rel = (
        f"../../../01_Renamed_PDFs_By_Research_Theme"
        f"/{clf.primary_theme}/{yfolder}/{canonical_name}"
    )

    return f"""\
---
title: "{_escape_yaml(title)}"
year: {meta.year or "null"}
venue: {meta.venue or "null"}
primary_theme: {clf.primary_theme}
application: {application}
canonical_pdf: "{pdf_rel}"
date_added: {_TODAY}
---

# {title}

**Application:** `{application}`
**Theme:** `{clf.primary_theme}`
**Year:** {meta.year or "—"} | **Venue:** {meta.venue or "—"}

> Renamed PDF: [{canonical_name}]({pdf_rel})

> Obsidian note: [[{canonical_name.replace('.pdf', '')}]]
"""


def generate_year_link_note(
    meta:           PaperMetadata,
    clf:            Classification,
    canonical_name: str,
) -> str:
    """Stub note under By_Year/<Year>/."""
    title   = _resolve_title(meta, canonical_name)
    yfolder = year_folder(meta.year)
    pdf_rel = (
        f"../../../01_Renamed_PDFs_By_Research_Theme"
        f"/{clf.primary_theme}/{yfolder}/{canonical_name}"
    )

    return f"""\
---
title: "{_escape_yaml(title)}"
year: {meta.year or "null"}
venue: {meta.venue or "null"}
primary_theme: {clf.primary_theme}
date_added: {_TODAY}
---

# {title}

**Theme:** `{clf.primary_theme}` | **Year:** {meta.year or "—"} | **Venue:** {meta.venue or "—"}

> [{canonical_name}]({pdf_rel})
"""


def generate_theme_link_note(
    meta:           PaperMetadata,
    clf:            Classification,
    canonical_name: str,
) -> str:
    """Stub note under By_Research_Theme/<Theme>/."""
    title   = _resolve_title(meta, canonical_name)
    yfolder = year_folder(meta.year)
    pdf_rel = (
        f"../../../01_Renamed_PDFs_By_Research_Theme"
        f"/{clf.primary_theme}/{yfolder}/{canonical_name}"
    )

    return f"""\
---
title: "{_escape_yaml(title)}"
year: {meta.year or "null"}
venue: {meta.venue or "null"}
primary_theme: {clf.primary_theme}
date_added: {_TODAY}
---

# {title}

**Theme:** `{clf.primary_theme}` | **Year:** {meta.year or "—"} | **Venue:** {meta.venue or "—"}

> [{canonical_name}]({pdf_rel})
"""


# ---------------------------------------------------------------------------
# Index notes (one per theme / application / year)
# ---------------------------------------------------------------------------
def generate_theme_index(theme: str, entries: list[dict]) -> str:
    rows = "\n".join(
        f"| [[{e['note']}|{e['title']}]] | {e['year'] or '—'} | {e['venue'] or '—'} "
        f"| {', '.join(e['applications'])} |"
        for e in sorted(entries, key=lambda x: x.get("year") or 0, reverse=True)
    )
    return f"""\
---
index_type: research_theme
theme: {theme}
date_updated: {_TODAY}
---

# {theme.replace('_', ' ')} — Paper Index

| Title | Year | Venue | Applications |
|---|---|---|---|
{rows}
"""


def generate_application_index(application: str, entries: list[dict]) -> str:
    rows = "\n".join(
        f"| [[{e['note']}|{e['title']}]] | {e['year'] or '—'} | {e['venue'] or '—'} "
        f"| {e['primary_theme']} |"
        for e in sorted(entries, key=lambda x: x.get("year") or 0, reverse=True)
    )
    return f"""\
---
index_type: application
application: {application}
date_updated: {_TODAY}
---

# {application.replace('_', ' ')} — Paper Index

| Title | Year | Venue | Primary Theme |
|---|---|---|---|
{rows}
"""


def generate_year_index(year: str, entries: list[dict]) -> str:
    rows = "\n".join(
        f"| [[{e['note']}|{e['title']}]] | {e['venue'] or '—'} | {e['primary_theme']} |"
        for e in entries
    )
    return f"""\
---
index_type: year
year: {year}
date_updated: {_TODAY}
---

# {year} — Papers

| Title | Venue | Primary Theme |
|---|---|---|
{rows}
"""


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------
def _resolve_title(meta: PaperMetadata, canonical_name: str) -> str:
    return meta.title or canonical_name.replace(".pdf", "").replace("-", " ")


def _authors_yaml(authors: list[str]) -> str:
    if not authors:
        return "  - Unknown"
    return "\n".join(f'  - "{_escape_yaml(a)}"' for a in authors[:10])


def _build_tags(clf: Classification) -> str:
    tags = set()
    tags.add(clf.primary_theme.lower().replace("_", "-"))
    for app in clf.applications:
        tags.add(app.lower().replace("_", "-"))
    if clf.year_bucket and clf.year_bucket not in ("Unknown", "Pre-2018"):
        tags.add(f"year-{clf.year_bucket}")
    return "\n".join(f'  - "{t}"' for t in sorted(tags))


def _doi_line(doi: Optional[str]) -> str:
    if not doi:
        return ""
    return f"- **DOI:** [{doi}](https://doi.org/{doi})"


def _escape_yaml(text: str) -> str:
    return text.replace('"', '\\"').replace("\n", " ")
