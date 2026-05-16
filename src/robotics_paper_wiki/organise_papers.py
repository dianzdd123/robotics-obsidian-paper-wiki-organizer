"""
organise_papers.py — Main orchestrator and CLI entry point.

Usage:
    # First-time dry run (preview — no PDFs copied):
    python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run

    # First-time import (copies PDFs):
    python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run

    # Incremental dry run:
    python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental --dry-run

    # Incremental import:
    python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental

Safety:
    - raw_data_root is NEVER modified. PDFs are COPIED, not moved.
    - Source filenames are always preserved.
    - dry_run: true is the default in config.yaml.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import shutil
import sys
import textwrap
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import yaml
from tqdm import tqdm

from .metadata_extract import extract_metadata, PaperMetadata
from .classify_paper import classify_paper, proposed_filename, Classification
from .duplicate_detection import (
    compute_pdf_hash,
    check_duplicate,
    disambiguate_canonicals,
)
from .obsidian_notes import (
    generate_paper_note,
    generate_application_link_note,
    generate_year_link_note,
    generate_theme_link_note,
    generate_theme_index,
    generate_application_index,
    generate_year_index,
)
from .summarise_paper import generate_presentation_summary
from .utils import write_text_file, copy_pdf, vault_relative, year_folder as _yfolder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
def load_config(path: str = "config.yaml") -> dict:
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


# ---------------------------------------------------------------------------
# PDF scanning
# ---------------------------------------------------------------------------
def scan_pdfs(source_dir: str) -> list[Path]:
    root = Path(source_dir)
    pdfs = sorted(root.rglob("*.pdf"))
    logger.info("Found %d PDFs in %s", len(pdfs), root)
    return pdfs


# ---------------------------------------------------------------------------
# Record builder
# ---------------------------------------------------------------------------
def build_record(
    pdf_path:     Path,
    meta:         PaperMetadata,
    clf:          Classification,
    canonical:    str,
    dest_pdf:     Path,
    is_dup:       bool,
    is_low_conf:  bool,
    vault_root:   Path,
    notes_dir:    Path,
    app_root:     Path,
    year_root:    Path,
    pdf_hash:     str = "",
    dup_info:     str = "none",
) -> dict:
    stem    = canonical.replace(".pdf", "")
    yfolder = _yfolder(meta.year)

    def _vr(p: Path) -> str:
        return vault_relative(p, vault_root)

    return {
        "source_folder":           meta.source_folder,
        "original_filename":       meta.filename,
        "original_raw_path":       str(pdf_path),
        "new_filename":            canonical,
        "dest_path":               str(dest_pdf),
        "vault_relative_pdf_path": _vr(dest_pdf),
        "main_note_path":          _vr(notes_dir / f"{stem}.md"),
        "application_note_paths":  "; ".join(
            _vr(app_root / app / f"{stem}_link.md") for app in clf.applications
        ),
        "year_note_path":          _vr(year_root / yfolder / f"{stem}_link.md"),
        "title":                   meta.title or "",
        "authors":                 "; ".join(meta.authors),
        "first_author":            meta.first_author or "",
        "year":                    meta.year or "",
        "venue":                   meta.venue or "",
        "doi":                     meta.doi or "",
        "keywords":                "; ".join(clf.title_keywords),
        "abstract_snippet":        (meta.abstract or "")[:200],
        "primary_theme":           clf.primary_theme,
        "secondary_themes":        "; ".join(clf.secondary_themes),
        "applications":            "; ".join(clf.applications),
        "year_bucket":             clf.year_bucket or "",
        "confidence":              meta.confidence,
        "is_low_confidence":       is_low_conf,
        "is_duplicate":            is_dup,
        "dup_match_type":          dup_info,
        "pdf_hash":                pdf_hash,
        "extraction_notes":        "; ".join(meta.extraction_notes),
        "copy_status":             "",
        "note_status":             "",
        "summary_status":          "",
    }


# ---------------------------------------------------------------------------
# CSV column orders
# ---------------------------------------------------------------------------
_RENAME_COLS = [
    "source_folder",          "original_filename",       "original_raw_path",
    "new_filename",           "vault_relative_pdf_path", "main_note_path",
    "application_note_paths", "year_note_path",
    "title",                  "first_author",            "year",
    "venue",                  "keywords",
    "primary_theme",          "secondary_themes",        "applications",
    "confidence",             "is_low_confidence",       "is_duplicate",
    "dup_match_type",
    "copy_status",            "note_status",             "summary_status",
]

_CATALOG_COLS = [
    "source_folder",          "original_filename",       "original_raw_path",
    "new_filename",           "dest_path",               "vault_relative_pdf_path",
    "main_note_path",         "application_note_paths",  "year_note_path",
    "title",                  "authors",                 "first_author",
    "year",                   "venue",                   "doi",
    "keywords",               "abstract_snippet",
    "primary_theme",          "secondary_themes",        "applications",
    "year_bucket",            "confidence",
    "is_low_confidence",      "is_duplicate",            "dup_match_type",
    "pdf_hash",               "extraction_notes",
    "copy_status",            "note_status",             "summary_status",
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description="Robotics Paper Wiki Organiser",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Modes:
              first_run    Scan raw_data_root (full collection). Default.
              incremental  Scan new_papers_inbox; archive originals after import.
        """),
    )
    parser.add_argument("--config",  default="config.yaml")
    parser.add_argument("--mode",    default="first_run", choices=["first_run", "incremental"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--run",     action="store_true")
    args = parser.parse_args()

    config  = load_config(args.config)
    dry_run = config.get("dry_run", True)
    if args.dry_run: dry_run = True
    if args.run:     dry_run = False

    run_mode = args.mode

    conf_threshold  = config["confidence"]["threshold"]
    overwrite_pdfs  = config.get("overwrite_existing_pdfs",       False)
    overwrite_notes = config.get("overwrite_existing_notes",      False)
    overwrite_summ  = config.get("regenerate_existing_summaries", False)

    # Directory layout
    vault_root        = Path(config["output_root"])
    renamed_pdfs_root = Path(config["pdf_output_root"])
    notes_root        = Path(config["notes_output_root"])
    metadata_dir      = Path(config["metadata_folder"])
    inbox_dir         = Path(config["new_papers_needs_review"])
    unclear_dir       = vault_root / "99_Duplicates_or_Unclear"

    notes_dir    = notes_root / "Papers"
    summary_dir  = notes_root / "Presentation_Summaries"
    theme_dir    = notes_root / "By_Research_Theme"
    app_root     = notes_root / "By_Application"
    year_root    = notes_root / "By_Year"
    indexes_dir  = notes_root / "Indexes"

    for d in [notes_dir, summary_dir, theme_dir, app_root, year_root, indexes_dir,
              metadata_dir, inbox_dir, unclear_dir,
              notes_root / "Synthesis"]:
        d.mkdir(parents=True, exist_ok=True)

    if run_mode == "incremental":
        source_dir  = config["new_papers_inbox"]
        archive_dir = Path(config["new_papers_processed_archive"])
        archive_dir.mkdir(parents=True, exist_ok=True)
    else:
        source_dir  = config["raw_data_root"]
        archive_dir = None

    logger.info("mode=%s  dry_run=%s  source=%s", run_mode, dry_run, source_dir)

    # Load existing catalog for incremental duplicate detection
    existing_records: list[dict] = []
    catalog_path = metadata_dir / "papers_catalog.json"
    if run_mode == "incremental" and catalog_path.exists():
        with open(catalog_path, encoding="utf-8") as fh:
            existing_records = json.load(fh)
        logger.info("Loaded %d existing records for duplicate detection", len(existing_records))

    # -----------------------------------------------------------------------
    # Phase 1: Metadata extraction
    # -----------------------------------------------------------------------
    pdfs = scan_pdfs(source_dir)
    if not pdfs:
        logger.error("No PDFs found. Check source_dir in config.yaml.")
        sys.exit(1)

    logger.info("=== Phase 1: Metadata extraction ===")
    venue_aliases = {k: v for k, v in config.get("venues", {}).items()}
    raw_records: list[tuple[Path, PaperMetadata, Classification, str]] = []

    for pdf_path in tqdm(pdfs, desc="Extracting", unit="pdf"):
        meta      = extract_metadata(pdf_path, venue_aliases=venue_aliases)
        clf       = classify_paper(meta, config)
        canonical = proposed_filename(meta, clf)
        raw_records.append((pdf_path, meta, clf, canonical))

    # -----------------------------------------------------------------------
    # Phase 2: Canonical name disambiguation
    # -----------------------------------------------------------------------
    logger.info("=== Phase 2: Name disambiguation ===")
    raw_records, dup_names_before = disambiguate_canonicals(raw_records)
    if dup_names_before:
        logger.warning("%d canonical name collision(s) resolved with suffix", len(dup_names_before))

    # -----------------------------------------------------------------------
    # Phase 3: Duplicate detection (incremental mode)
    # -----------------------------------------------------------------------
    logger.info("=== Phase 3: Duplicate detection ===")
    dup_info_map: dict[str, tuple[bool, str]] = {}  # canonical -> (is_dup, match_type)

    for pdf_path, meta, clf, canonical, _ in raw_records:
        if existing_records:
            pdf_hash = compute_pdf_hash(pdf_path)
            info = check_duplicate(
                doi=meta.doi, title=meta.title,
                canonical=canonical, pdf_hash=pdf_hash,
                existing_records=existing_records,
            )
            dup_info_map[canonical] = (info.is_duplicate, info.match_type)
        else:
            dup_info_map[canonical] = (False, "none")

    # -----------------------------------------------------------------------
    # Phase 4: Write artefacts
    # -----------------------------------------------------------------------
    logger.info("=== Phase 4: Generating artefacts ===")

    records:          list[dict]            = []
    low_conf_records: list[dict]            = []
    dup_records:      list[dict]            = []
    theme_entries:    dict[str, list[dict]] = defaultdict(list)
    app_entries:      dict[str, list[dict]] = defaultdict(list)
    year_entries:     dict[str, list[dict]] = defaultdict(list)

    for pdf_path, meta, clf, canonical, was_collision in tqdm(raw_records, desc="Writing", unit="pdf"):
        is_low_conf            = meta.confidence < conf_threshold
        is_catalog_dup, dup_mt = dup_info_map.get(canonical, (False, "none"))
        is_dup                 = was_collision or is_catalog_dup

        yfolder = _yfolder(meta.year)

        if is_catalog_dup:
            dest_pdf = unclear_dir / canonical
        elif is_low_conf:
            dest_pdf = inbox_dir / canonical
        else:
            dest_pdf = renamed_pdfs_root / clf.primary_theme / yfolder / canonical

        pdf_hash = compute_pdf_hash(pdf_path) if not dry_run else ""

        record = build_record(
            pdf_path, meta, clf, canonical, dest_pdf,
            is_dup, is_low_conf,
            vault_root, notes_dir, app_root, year_root,
            pdf_hash=pdf_hash,
            dup_info=dup_mt,
        )

        # Obsidian note
        stem      = canonical.replace(".pdf", "")
        note_path = notes_dir / f"{stem}.md"
        note_stat = write_text_file(note_path, generate_paper_note(meta, clf, canonical), overwrite=overwrite_notes)
        record["note_status"] = note_stat

        # Presentation summary
        summ_path = summary_dir / f"{stem}_summary.md"
        summ_stat = write_text_file(summ_path, generate_presentation_summary(meta, clf, canonical), overwrite=overwrite_summ)
        record["summary_status"] = summ_stat

        # Application link stubs
        for app in clf.applications:
            write_text_file(
                app_root / app / f"{stem}_link.md",
                generate_application_link_note(meta, clf, canonical, app),
                overwrite=overwrite_notes,
            )

        # Year link stub
        write_text_file(
            year_root / yfolder / f"{stem}_link.md",
            generate_year_link_note(meta, clf, canonical),
            overwrite=overwrite_notes,
        )

        # Theme link stub
        write_text_file(
            theme_dir / clf.primary_theme / f"{stem}_link.md",
            generate_theme_link_note(meta, clf, canonical),
            overwrite=overwrite_notes,
        )

        # Accumulators for indexes
        entry = {
            "note":          stem,
            "title":         meta.title or canonical,
            "year":          meta.year,
            "venue":         meta.venue,
            "primary_theme": clf.primary_theme,
            "applications":  clf.applications,
        }
        theme_entries[clf.primary_theme].append(entry)
        for app in clf.applications:
            app_entries[app].append(entry)
        year_entries[yfolder].append(entry)

        # Copy PDF
        copy_stat = copy_pdf(pdf_path, dest_pdf, dry_run, overwrite=overwrite_pdfs)
        record["copy_status"] = copy_stat

        # Incremental: archive original after successful copy
        if run_mode == "incremental" and copy_stat == "COPIED" and archive_dir:
            archive_dest = archive_dir / pdf_path.name
            if not archive_dest.exists():
                shutil.copy2(str(pdf_path), str(archive_dest))

        records.append(record)
        if is_low_conf:    low_conf_records.append(record)
        if is_dup:         dup_records.append(record)

    # -----------------------------------------------------------------------
    # Phase 5: Write index notes
    # -----------------------------------------------------------------------
    logger.info("=== Phase 5: Writing index notes ===")

    for theme, entries in theme_entries.items():
        write_text_file(indexes_dir / f"Theme_Index_{theme}.md", generate_theme_index(theme, entries))

    for app, entries in app_entries.items():
        write_text_file(indexes_dir / f"App_Index_{app}.md", generate_application_index(app, entries))

    for year, entries in year_entries.items():
        write_text_file(indexes_dir / f"Year_Index_{year}.md", generate_year_index(year, entries))

    # -----------------------------------------------------------------------
    # Phase 6: Write metadata logs
    # -----------------------------------------------------------------------
    logger.info("=== Phase 6: Writing metadata logs ===")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def _write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
        if not rows:
            return
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
        logger.info("Written: %s (%d rows)", path, len(rows))

    _write_csv(metadata_dir / "rename_log.csv",           records,          _RENAME_COLS)
    _write_csv(metadata_dir / "papers_catalog.csv",       records,          _CATALOG_COLS)
    _write_csv(metadata_dir / "low_confidence_review.csv", low_conf_records, [
        "source_folder", "original_filename", "original_raw_path",
        "title", "first_author", "year", "venue",
        "primary_theme", "confidence", "extraction_notes", "new_filename", "dest_path",
    ])
    _write_csv(metadata_dir / "duplicate_candidates.csv", dup_records, [
        "source_folder", "original_filename", "original_raw_path",
        "new_filename", "title", "primary_theme", "year", "confidence",
        "dup_match_type", "copy_status",
    ])

    # Append new records to papers_catalog.json (incremental) or write fresh (first_run)
    if run_mode == "incremental" and existing_records:
        new_canonical = {r["new_filename"] for r in records}
        merged = [r for r in existing_records if r["new_filename"] not in new_canonical]
        merged.extend(records)
    else:
        merged = records

    with open(catalog_path, "w", encoding="utf-8") as fh:
        json.dump(merged, fh, indent=2, ensure_ascii=False, default=str)
    logger.info("Written: %s (%d total records)", catalog_path, len(merged))

    run_log = {
        "run_timestamp":           timestamp,
        "run_mode":                run_mode,
        "dry_run":                 dry_run,
        "source_dir":              source_dir,
        "total_pdfs":              len(records),
        "low_confidence":          len(low_conf_records),
        "duplicates_resolved":     len(dup_names_before),
        "duplicate_canonical_names": sorted(dup_names_before),
        "catalog_total":           len(merged),
        "theme_breakdown": {t: len(e) for t, e in theme_entries.items()},
        "application_breakdown":   {a: len(e) for a, e in app_entries.items()},
    }
    log_path = metadata_dir / f"run_log_{timestamp}.json"
    with open(log_path, "w", encoding="utf-8") as fh:
        json.dump(run_log, fh, indent=2)
    logger.info("Written: %s", log_path)

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------
    run_label = "DRY RUN" if dry_run else "LIVE RUN"
    print("\n" + "=" * 60)
    print(f"  Paper Wiki Organiser  [{run_label} / {run_mode}]")
    print("=" * 60)
    print(f"  PDFs processed   : {len(records)}")
    print(f"  Low-confidence   : {len(low_conf_records)}  (threshold={conf_threshold})")
    print(f"  Disambiguated    : {len(dup_names_before)} name collision(s)")
    print()
    print("  Theme breakdown:")
    for theme in sorted(theme_entries):
        yrs = sorted({str(r["year"]) if r["year"] else "Unknown" for r in records if r["primary_theme"] == theme})
        print(f"    {theme:<36} {len(theme_entries[theme]):>3} papers  [{', '.join(yrs)}]")
    print()
    print(f"  rename_log.csv  -> {metadata_dir / 'rename_log.csv'}")
    print(f"  papers_catalog  -> {catalog_path}")
    print(f"  Notes           -> {notes_dir}")
    print(f"  Summaries       -> {summary_dir}")
    print("=" * 60)

    if dry_run:
        print("\nReview rename_log.csv, then run with --run to copy PDFs.")


if __name__ == "__main__":
    main()
