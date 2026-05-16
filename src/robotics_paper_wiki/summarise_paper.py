"""
summarise_paper.py
Generate extended paper analysis in slide-style Markdown.

Sections produced:
  One-Sentence Takeaway, Research Problem, Motivation, Key Contributions,
  Method, Experiments, Key Results, Strengths, Limitations, Future Work,
  Why It Matters, Suggested Slide Summary.

All sections are extracted from the abstract using keyword heuristics.
Sections that cannot be reliably extracted show a prompt placeholder.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Optional

from .metadata_extract import PaperMetadata
from .classify_paper import Classification
from .utils import year_folder

_TODAY       = date.today().isoformat()
_PLACEHOLDER = "_Not extracted — open the PDF._"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------
def generate_presentation_summary(
    meta:           PaperMetadata,
    clf:            Classification,
    canonical_name: str,
) -> str:
    """Return an extended slide-style Markdown summary."""
    title   = meta.title or canonical_name.replace(".pdf", "").replace("-", " ")
    authors = _authors_short(meta)

    takeaway      = _extract_takeaway(meta.abstract)
    problem       = _extract_problem(meta.abstract)
    motivation    = _extract_motivation(meta.abstract)
    contributions = _extract_contributions(meta.abstract)
    method        = _extract_method(meta.abstract)
    experiments   = _extract_experiments(meta.abstract)
    results       = _extract_results(meta.abstract)
    strengths     = _extract_strengths(meta.abstract)
    limitations   = _extract_limitations(meta.abstract)
    future_work   = _extract_future_work(meta.abstract)
    relevance     = _why_it_matters(clf)
    slide_summary = _suggest_slide_summary(meta, clf)

    theme_display = clf.primary_theme.replace("_", " ")
    secondary_display = (
        " -> " + ", ".join(t.replace("_", " ") for t in clf.secondary_themes)
        if clf.secondary_themes else ""
    )
    apps_display = " - ".join(a.replace("_", " ") for a in clf.applications)

    return f"""\
# {title}

**Theme:** {theme_display}{secondary_display}
**Applications:** {apps_display}
**Year:** {meta.year or "—"} | **Venue:** {meta.venue or "—"}
**Authors:** {authors}

---

## One-Sentence Takeaway

{takeaway}

---

## Research Problem

{problem}

## Motivation

{motivation}

## Key Contributions

{contributions}

## Method

{method}

## Experiments

{experiments}

## Key Results

{results}

## Strengths

{strengths}

## Limitations

{limitations}

## Future Work

{future_work}

---

## Why It Matters

{relevance}

---

## Suggested Slide Summary

{slide_summary}

---

*Source:* `{meta.source_folder}/{meta.filename}`
*Confidence:* {meta.confidence:.2f} | *Extracted:* {_TODAY}
"""


# ---------------------------------------------------------------------------
# Abstract section extractors
# ---------------------------------------------------------------------------
def _sentences(abstract: Optional[str]) -> list[str]:
    if not abstract:
        return []
    return re.split(r"(?<=[.!?])\s+", abstract.strip())


def _match_sentences(
    abstract: Optional[str],
    keywords: list[str],
    max_sents: int = 2,
) -> Optional[str]:
    sents   = _sentences(abstract)
    matched = [s for s in sents if any(kw in s.lower() for kw in keywords)]
    return " ".join(matched[:max_sents]) if matched else None


def _extract_takeaway(abstract: Optional[str]) -> str:
    sents = _sentences(abstract)
    return sents[0] if sents else _PLACEHOLDER


def _extract_problem(abstract: Optional[str]) -> str:
    sents = _sentences(abstract)
    if not sents:
        return _PLACEHOLDER
    result = _match_sentences(abstract, [
        "challenge", "difficult", "however", "limitation", "lack", "problem",
        "issue", "gap", "traditional", "conventional", "existing", "current",
        "despite", "yet", "still", "unresolved",
    ])
    return result or " ".join(sents[:max(1, len(sents) // 3)])


def _extract_motivation(abstract: Optional[str]) -> str:
    sents = _sentences(abstract)
    if not sents:
        return _PLACEHOLDER
    result = _match_sentences(abstract, [
        "important", "critical", "crucial", "essential", "need", "require",
        "benefit", "enable", "allow", "support", "improve", "clinical",
        "real-world", "practical", "application",
    ])
    return result or " ".join(sents[:max(1, len(sents) // 3)])


def _extract_contributions(abstract: Optional[str]) -> str:
    sents = _sentences(abstract)
    if not sents:
        return f"- {_PLACEHOLDER}"
    markers = [
        "we propose", "we present", "we introduce", "we develop", "we design",
        "novel", "new approach", "new method", "new framework", "contribution",
        "in this paper", "in this work", "this paper", "this work",
        "we demonstrate", "we show", "we achieve",
    ]
    matched = [s for s in sents if any(m in s.lower() for m in markers)]
    return "\n".join(f"- {s}" for s in matched[:3]) if matched else f"- {sents[0]}"


def _extract_method(abstract: Optional[str]) -> str:
    sents = _sentences(abstract)
    if not sents:
        return _PLACEHOLDER
    result = _match_sentences(abstract, [
        "method", "approach", "framework", "network", "algorithm", "architecture",
        "model", "pipeline", "system", "strategy", "technique", "using",
        "based on", "leverage", "employ",
    ])
    if result:
        return result
    n = len(sents)
    third = max(1, n // 3)
    return " ".join(sents[third: 2 * third]) or sents[0]


def _extract_experiments(abstract: Optional[str]) -> str:
    result = _match_sentences(abstract, [
        "experiment", "evaluat", "assess", "test", "validate", "verif",
        "dataset", "benchmark", "comparison", "baseline", "real-world",
        "simulation", "phantom", "in vivo", "in vitro", "hardware",
    ])
    return result or "_Experimental details not explicitly stated in abstract — see Experiments section._"


def _extract_results(abstract: Optional[str]) -> str:
    sents = _sentences(abstract)
    if not sents:
        return _PLACEHOLDER
    result = _match_sentences(abstract, [
        "result", "achiev", "show", "demonstrate", "outperform", "improve",
        "accuracy", "precision", "error", "rate", "%", "fold", "times",
        "significant", "superior", "state-of-the-art",
    ], max_sents=3)
    if result:
        return result
    n = len(sents)
    third = max(1, n // 3)
    return " ".join(sents[2 * third:]) or sents[-1]


def _extract_strengths(abstract: Optional[str]) -> str:
    result = _match_sentences(abstract, [
        "outperform", "improve", "surpass", "state-of-the-art", "superior",
        "robust", "efficient", "accurate", "effective", "significant",
        "better", "higher", "faster", "lower error",
    ])
    return result or "_Strengths not explicitly stated in abstract — see Discussion in full paper._"


def _extract_limitations(abstract: Optional[str]) -> str:
    result = _match_sentences(abstract, [
        "limitation", "drawback", "constraint", "assumption", "however",
        "but", "although", "nevertheless", "restrict", "only", "currently",
    ])
    return result or "_Not explicitly stated in abstract — check Limitations / Discussion section._"


def _extract_future_work(abstract: Optional[str]) -> str:
    result = _match_sentences(abstract, [
        "future", "plan", "will be", "could be", "potential", "extend",
        "pave the way", "enable", "open", "next step", "prospect",
    ])
    return result or "_Not explicitly stated in abstract — check Conclusion section._"


def _suggest_slide_summary(meta: PaperMetadata, clf: Classification) -> str:
    takeaway     = _extract_takeaway(meta.abstract)
    contrib_raw  = _extract_contributions(meta.abstract)
    contrib_line = contrib_raw.splitlines()[0].lstrip("- ").strip()
    result_sents = _sentences(_extract_results(meta.abstract))
    result_line  = result_sents[0] if result_sents else "_See paper._"
    apps         = " and ".join(a.replace("_", " ") for a in clf.applications[:2])

    return (
        f"**Slide 1 — What (Problem & Contribution):**\n"
        f"> {takeaway}\n\n"
        f"**Slide 2 — How (Method):**\n"
        f"> {contrib_line}\n\n"
        f"**Slide 3 — So What (Result & Relevance):**\n"
        f"> {result_line}\n"
        f"> Relevant to: **{apps}**"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _why_it_matters(clf: Classification) -> str:
    rationale = {
        "Design_and_Fabrication":  "Advances in physical sensor and hardware design enable new capabilities for downstream systems.",
        "Multimodal_Perception":   "Robust perception is the foundation for reliable autonomous and semi-autonomous robotic behaviour.",
        "Robot_Learning":          "Learning-based methods reduce manual engineering effort and improve generalisation to real-world variation.",
        "Human_Robot_Interaction": "Effective HRI bridges the gap between powerful robot hardware and practical, safe human-operated deployment.",
    }
    base = rationale.get(clf.primary_theme, "This work contributes to advancing robotic capabilities.")
    if clf.applications:
        apps = " and ".join(a.replace("_", " ") for a in clf.applications[:2])
        return f"{base} Directly relevant to: **{apps}**."
    return base


def _authors_short(meta: PaperMetadata) -> str:
    if not meta.authors:
        return meta.first_author or "Unknown"
    first = meta.authors[0]
    return first if len(meta.authors) == 1 else f"{first} et al."
