# Obsidian Note Design

This document explains the format of auto-generated Obsidian notes and how to customise them.

---

## Note types

| Note type | Location | Generated | Editable |
|---|---|---|---|
| Paper note | `Papers/<canonical>.md` | Yes | Yes — Notes + Related Papers |
| Presentation summary | `Presentation_Summaries/<canonical>_summary.md` | Yes | Yes — all sections |
| Application link stub | `By_Application/<App>/<canonical>_link.md` | Yes | No |
| Year link stub | `By_Year/<Year>/<canonical>_link.md` | Yes | No |
| Theme index | `Indexes/Theme_Index_<Theme>.md` | Yes | No |
| Application index | `Indexes/App_Index_<App>.md` | Yes | No |
| Year index | `Indexes/Year_Index_<Year>.md` | Yes | No |
| Synthesis note | `Synthesis/*.md` | No — write yourself | Yes |

---

## Paper note format

```markdown
---
title: "Tactile Sensor Design for Surgical Teleoperation"
authors:
  - "Dandan Zhang"
  - "Felix Naef"
year: 2024
venue: ICRA
doi: 10.1109/ICRA12345.2024.9876543
primary_theme: Design_and_Fabrication
secondary_themes:
  - Human_Robot_Interaction
applications:
  - Surgical_Robot
  - Tactile_Sensing
year_bucket: "2024-2025"
confidence: 0.95
source_file: "original-filename.pdf"
source_folder: "Raw-Papers-Subfolder"
date_added: 2026-05-16
tags:
  - "design-and-fabrication"
  - "human-robot-interaction"
  - "surgical-robot"
  - "tactile-sensing"
  - "year-2024-2025"
---

# Tactile Sensor Design for Surgical Teleoperation

## Abstract

> Full abstract text here...

## Classification

| Field | Value |
|---|---|
| Primary Theme | `Design_and_Fabrication` |
| Secondary Themes | `Human_Robot_Interaction` |
| Applications | `Surgical_Robot`, `Tactile_Sensing` |
| Year | 2024 |
| Venue | ICRA |
| Year Bucket | 2024-2025 |
| Confidence | 0.95 |

## Source

- **Canonical PDF:** [[01_Renamed_PDFs_By_Research_Theme/Design_and_Fabrication/2024/2024-ICRA-Tactile-Sensor-Design-Zhang.pdf|Open PDF]]
- **Original file:** `Raw-Papers-Subfolder/original-filename.pdf`
- **DOI:** [10.1109/ICRA12345.2024.9876543](https://doi.org/10.1109/ICRA12345.2024.9876543)

## Notes

> _Add your own annotations here._

## Related Papers

> _Link related notes here using `[[note-name]]`._
```

### YAML frontmatter fields

| Field | Source | Notes |
|---|---|---|
| `title` | PDF metadata, layout analysis, filename | Escaped for YAML |
| `authors` | PDF metadata, text heuristic | Up to 10 authors |
| `year` | PDF metadata, text regex, filename | 4-digit year |
| `venue` | Text scan, filename | Short code (ICRA, RAL, ...) |
| `doi` | Text regex | Cleaned trailing punctuation |
| `primary_theme` | Keyword classifier | Highest keyword score |
| `secondary_themes` | Keyword classifier | Score >= 45% of primary |
| `applications` | Keyword classifier | Multiple allowed |
| `year_bucket` | Derived from year | 2-year range (2024-2025) |
| `confidence` | Scoring formula | 0.0–1.0 |
| `tags` | Derived | Lowercase, hyphenated theme/app/year |

### Confidence scoring

| Component | Weight |
|---|---|
| Title extracted (not from filename) | +0.30 |
| Title from filename | +0.10 |
| Year extracted | +0.20 |
| Venue extracted | +0.20 |
| Authors extracted | +0.15 |
| DOI extracted | +0.10 |
| Abstract extracted | +0.05 |

Papers with confidence < `threshold` (default 0.50) go to `00_Inbox_Review/` instead of `01_Renamed_PDFs_By_Research_Theme/`.

---

## Presentation summary format

The extended analysis note has 12 sections:

```markdown
# Paper Title

**Theme:** Design and Fabrication -> Human Robot Interaction
**Applications:** Surgical Robot · Tactile Sensing
**Year:** 2024 | **Venue:** ICRA
**Authors:** Dandan Zhang et al.

---

## One-Sentence Takeaway
First complete sentence of the abstract.

## Research Problem
Sentences containing challenge/problem indicators.

## Motivation
Sentences explaining why this matters.

## Key Contributions
- Bulleted sentences with proposal/contribution markers.

## Method
Sentences describing the approach.

## Experiments
Sentences mentioning evaluation/validation.

## Key Results
Sentences with results/performance metrics.

## Strengths
Sentences with positive outcome markers.

## Limitations
Placeholder if not in abstract.

## Future Work
Placeholder if not in abstract.

---

## Why It Matters
Theme-based rationale + application relevance.

---

## Suggested Slide Summary
**Slide 1 — What:** ...
**Slide 2 — How:** ...
**Slide 3 — So What:** ...

---
*Confidence:* 0.95 | *Extracted:* 2026-05-16
```

Most sections are extracted by keyword heuristics from the abstract. Sections that cannot be reliably extracted show a placeholder: `_Not extracted — open the PDF._`

### Regenerating summaries

To update all summaries with fresh extraction (e.g. after improving keyword rules):

```yaml
# config.yaml
regenerate_existing_summaries: true
```

Then re-run the organiser.

---

## Link format

All PDF links in notes are vault-relative:

```
[[01_Renamed_PDFs_By_Research_Theme/Theme/Year/filename.pdf|Open PDF]]
```

This means:
- The vault root is the `output_root` directory in `config.yaml`
- Opening this link in Obsidian opens the PDF directly
- The link is path-independent (works on any machine that has the vault)
- **Never** use absolute paths (`C:\...` or `/home/...`) inside notes

---

## Customising note templates

To change what goes into generated notes, edit:

- `src/robotics_paper_wiki/obsidian_notes.py` — `generate_paper_note()` controls the main note format
- `src/robotics_paper_wiki/summarise_paper.py` — `generate_presentation_summary()` controls the extended analysis

Both functions take `(meta: PaperMetadata, clf: Classification, canonical_name: str)` and return a Markdown string.

---

## Notes section (user-editable)

The `## Notes` section at the bottom of each paper note is intentionally blank. Use it for:
- Your own annotations and thoughts
- Literature context
- Links to related notes with `[[note-name]]`
- Figures or quotes from the paper

The `overwrite_existing_notes: false` config flag ensures your annotations survive re-runs.
