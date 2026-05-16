# First-Time Import Tutorial

This guide walks you through importing a collection of raw PDFs for the first time.

**Time required:** 10–20 minutes setup, then a few minutes per run.

---

## Prerequisites

- Python 3.10+
- A folder of raw PDFs (can be nested, any filenames)
- An empty Publications output folder

## Step 1 — Install

```bash
git clone https://github.com/<your-username>/robotics-obsidian-paper-wiki-organizer.git
cd robotics-obsidian-paper-wiki-organizer
pip install -e .
```

## Step 2 — Create config.yaml

```bash
cp examples/config.example.yaml config.yaml
```

Edit `config.yaml`. At minimum, set these paths:

```yaml
raw_data_root:   "/absolute/path/to/your/raw/PDFs"
output_root:     "/absolute/path/to/your/Publications"
```

The tool will create all subfolders under `output_root` automatically.

> **Safety guarantee:** `raw_data_root` is **read-only**. The tool never modifies,
> renames, or deletes files there.

## Step 3 — Dry run

```bash
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run
```

What happens:
- All PDFs in `raw_data_root` are scanned recursively
- Metadata is extracted from each PDF
- Each paper is classified into a research theme and applications
- A canonical filename is proposed for each paper
- Obsidian notes and summaries are written to `02_Obsidian_Notes/`
- **No PDFs are copied yet**
- All logs are written to `90_Metadata/`

The terminal shows a summary:

```
============================================================
  Paper Organiser complete  [DRY RUN / first_run]
============================================================
  Total PDFs processed : 76
  Low-confidence       : 3  (threshold=0.5)
  Disambiguated names  : 6

  Theme breakdown:
    Design_and_Fabrication              14 papers  [2021, 2022, 2023, 2024]
    Human_Robot_Interaction             19 papers  [2020, 2021, 2022, 2023]
    Multimodal_Perception               28 papers  [2022, 2023, 2024, 2025]
    Robot_Learning                      14 papers  [2020, 2021, 2022, 2024]
    Unclassified                         1 papers  [Unknown_Year]
```

## Step 4 — Review rename_log.csv

Open `Publications/90_Metadata/rename_log.csv` in Excel, Numbers, or a CSV viewer.

Check:

| Column | What to look for |
|---|---|
| `new_filename` | Does the proposed name look correct? |
| `primary_theme` | Is the theme assignment right? |
| `title` | Was the title extracted correctly? |
| `first_author` | Is the author surname correct? |
| `year` | Was the year detected? |
| `confidence` | Papers below 0.5 go to `00_Inbox_Review/` |
| `is_low_confidence` | Review these manually |

**Common issues:**

- **Wrong first author** — if the filename has a topic word (e.g. "Control") instead of a name, add it to `_TOPIC_WORDS` in `metadata_extract.py`
- **Wrong theme** — add more keywords to the relevant theme in `config.yaml`
- **Year missing** — add the year to the filename using the `YEAR-VENUE-...` format; the tool will detect it

## Step 5 — Fix config.yaml if needed

To fix misclassifications, edit `config.yaml`:

```yaml
theme_keywords:
  Robot_Learning:
    keywords:
      - your-new-keyword       # add here
      - another-keyword
```

Re-run the dry run to see the changes before committing.

## Step 6 — Run the import

When satisfied with `rename_log.csv`:

```bash
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run
```

Note: `config.yaml` has `dry_run: true` by default. The `--run` flag forces a live run regardless:

```bash
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run
```

What happens now:
- PDFs are **copied** (never moved) to `01_Renamed_PDFs_By_Research_Theme/<Theme>/<Year>/`
- Obsidian notes are written (if not already written in dry run)
- All metadata files are updated

## Step 7 — Open in Obsidian

1. Open Obsidian → **Open another vault**
2. Select your `Publications/` folder as the vault root
3. The `01_Renamed_PDFs_By_Research_Theme/` PDF links in notes will resolve automatically

---

## Troubleshooting

### "No PDFs found"
Check that `raw_data_root` points to the correct folder. The tool scans recursively, so subfolders are fine.

### Many papers classified as "Unclassified"
The default keywords cover robotics. For other domains, extend `theme_keywords` in `config.yaml`.

### Wrong author surname extracted
The `metadata_extract.py` `_TOPIC_WORDS` set blocks common topic words from being treated as surnames. Add any words that keep being misidentified to that set.

### Low confidence scores
Confidence is based on which fields were extracted (title, year, venue, authors, DOI, abstract). Papers with no structured filename and no extractable metadata score low. Open those PDFs and check manually.

---

## Next steps

- [Incremental Import Tutorial](incremental-import-tutorial.md) — add new papers without redoing everything
- [Claude Code Workflow](claude-code-workflow.md) — use Claude Code to extend and curate the wiki
- [Obsidian Note Design](obsidian-note-design.md) — understand and customise the note format
