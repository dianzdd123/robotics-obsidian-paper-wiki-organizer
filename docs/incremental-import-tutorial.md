# Incremental Import Tutorial

After the first-time import, use incremental mode to add new papers without reprocessing your entire collection.

---

## How incremental mode works

1. You drop new PDFs into `03_New_Papers_Inbox/To_Process/`
2. The tool processes only those PDFs
3. Duplicate detection runs against the existing `papers_catalog.json`
4. New papers are copied to `01_Renamed_PDFs_By_Research_Theme/`
5. Original PDFs are archived to `03_New_Papers_Inbox/Processed_Originals/`
6. The metadata catalog is **appended** (not replaced)

---

## Step 1 — Drop new PDFs into the inbox

```
03_New_Papers_Inbox/
└── To_Process/
    ├── new-paper-1.pdf
    ├── new-paper-2.pdf
    └── 2025-ICRA-NewPaper-Author.pdf
```

Any filename is fine. Structured filenames (`YEAR-VENUE-...-Author.pdf`) give better metadata extraction.

---

## Step 2 — Dry run

```bash
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental --dry-run
```

This scans only `To_Process/`, checks duplicates against the existing catalog, and shows what would happen — **without copying or archiving anything**.

Check:
- `90_Metadata/rename_log.csv` — the new rows at the bottom
- `90_Metadata/duplicate_candidates.csv` — any papers flagged as duplicates

---

## Step 3 — Inspect duplicates

Open `duplicate_candidates.csv`. Each duplicate row shows:

| Column | Description |
|---|---|
| `match_type` | How the duplicate was detected: `doi`, `hash`, `title`, or `filename` |
| `matched_record` | The existing paper this matched against |

**Duplicate detection methods (in priority order):**

1. **DOI match** — strongest: same DOI in two files means same paper
2. **SHA-256 hash** — same binary content = identical files
3. **Normalised title match** — same title after stripping punctuation/case
4. **Canonical filename match** — same proposed `YEAR-VENUE-Kw-Kw-Kw-Author` stem

If a paper is wrongly flagged as a duplicate, you can manually add it:
1. Remove it from `To_Process/`
2. Copy it directly into `01_Renamed_PDFs_By_Research_Theme/Theme/Year/` with the correct name
3. Generate its note manually or update `config.yaml` to force reprocessing

---

## Step 4 — Run the import

```bash
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental
```

After a successful run:
- New PDFs appear in `01_Renamed_PDFs_By_Research_Theme/`
- New notes appear in `02_Obsidian_Notes/Papers/`
- Original PDFs are moved to `03_New_Papers_Inbox/Processed_Originals/`
- `papers_catalog.json` is updated with the new entries
- Index notes in `Indexes/` are regenerated

---

## Overwrite behaviour

By default the tool skips files that already exist:

```yaml
overwrite_existing_pdfs:            false   # skip dest PDF if already there
overwrite_existing_notes:           false   # skip note .md if already exists
regenerate_existing_summaries:      false   # skip summary .md if already exists
```

To force regeneration of notes for papers that already exist:

```yaml
overwrite_existing_notes:           true
regenerate_existing_summaries:      true
```

---

## Maintaining the catalog across runs

The tool loads `90_Metadata/papers_catalog.json` at startup (in incremental mode) and uses it as the reference set for duplicate detection. Keep this file — it is the single source of truth for what has already been imported.

If you need to rebuild the catalog from scratch (e.g. after manually reorganising):

```bash
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run
```

This regenerates the catalog without touching any PDFs.

---

## Recommended workflow for ongoing use

```
Every time you download new papers:
  1. Move them to To_Process/
  2. Run: python -m robotics_paper_wiki.organise_papers --mode incremental --dry-run
  3. Review rename_log.csv (new rows)
  4. Run: python -m robotics_paper_wiki.organise_papers --mode incremental
  5. Open Obsidian — new notes and index updates are live
```
