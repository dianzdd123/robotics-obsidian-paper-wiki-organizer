# Robotics Obsidian Paper Wiki Organizer

## Start here


**Scope:** Python package with local metadata extraction, copy-based import and reviewable dry runs.

| Need | Where to start |
|---|---|
| Setup, file map, inputs/outputs and troubleshooting | [Reuse guide](docs/REUSE.md) |
| Local structural validation | `python scripts/check_repository.py` (Python 3.10+) |
| Proposed fixes and reproducibility details | [Contributing](CONTRIBUTING.md) |

The structural check does not run experiments or certify hardware, model accuracy or dependency compatibility. Read the existing licence and any separate asset terms before reuse.


A Python + Claude Code workflow for organising robotics research papers into a structured Obsidian wiki.

This project helps you take a messy folder of robotics PDFs, copy them safely into a clean publication library, rename them consistently, classify them by research theme/application/year, and generate Obsidian notes that link back to the renamed PDFs.

The workflow is designed for:

```text
Raw PDF folder
→ safe dry run
→ metadata review
→ copy + rename PDFs
→ group PDFs by research theme and year
→ generate Obsidian paper notes
→ build a browsable research wiki
```

---

## Key Features

- Safe dry-run workflow before copying or renaming PDFs
- Original raw PDFs are never renamed, moved, or deleted
- Copied PDFs are renamed using a consistent format
- Physical PDFs are grouped by research theme and year
- Obsidian notes are grouped by paper, research theme, application, and year
- Notes link to renamed PDFs using vault-relative Obsidian links
- Metadata logs are generated for review
- Duplicate candidates are detected
- Low-confidence papers are separated for manual review
- Supports first-time import and future incremental import
- Works well with VS Code + Claude Code
- Includes `pytest` tests for checking core project logic

---

## Main Use Case

You have a folder like this:

```text
C:\Obsidian-Website\Raw-Papers-All
```

containing many PDFs, possibly in messy subfolders.

You want to create this clean publication wiki:

```text
C:\Obsidian-Website\Publications
```

with renamed PDFs here:

```text
C:\Obsidian-Website\Publications\01_Renamed_PDFs_By_Research_Theme
```

and Obsidian notes here:

```text
C:\Obsidian-Website\Publications\02_Obsidian_Notes
```

---

## Output Structure

The generated `Publications` folder should look like this:

```text
Publications/
├── 00_Inbox_Review/
│
├── 01_Renamed_PDFs_By_Research_Theme/
│   ├── Design_and_Fabrication/
│   │   ├── 2026/
│   │   ├── 2025/
│   │   └── Unknown/
│   │
│   ├── Multimodal_Perception/
│   │   ├── 2026/
│   │   ├── 2025/
│   │   └── Unknown/
│   │
│   ├── Robot_Learning/
│   │   ├── 2026/
│   │   ├── 2025/
│   │   └── Unknown/
│   │
│   ├── Human_Robot_Interaction/
│   │   ├── 2026/
│   │   ├── 2025/
│   │   └── Unknown/
│   │
│   └── Unclassified/
│
├── 02_Obsidian_Notes/
│   ├── Papers/
│   ├── Presentation_Summaries/
│   ├── By_Research_Theme/
│   ├── By_Application/
│   ├── By_Year/
│   ├── Synthesis/
│   └── Indexes/
│
├── 03_New_Papers_Inbox/
│   ├── To_Process/
│   ├── Processed_Originals/
│   └── Needs_Review/
│
├── 90_Metadata/
│   ├── rename_log.csv
│   ├── papers_catalog.csv
│   ├── papers_catalog.json
│   ├── low_confidence_review.csv
│   ├── duplicate_candidates.csv
│   └── run_log_<timestamp>.json
│
└── 99_Duplicates_or_Unclear/
```

---

## PDF Organisation Rule

For the first-time import, copied PDFs are organised as:

```text
Research Theme → Year → Renamed PDF
```

Example:

```text
Publications/
└── 01_Renamed_PDFs_By_Research_Theme/
    └── Multimodal_Perception/
        └── 2026/
            └── 2026-ICRA-Diffusion-Tactile-Generation-Wen.pdf
```

Applications are **not** used as physical PDF folders. They are used only in metadata and Obsidian notes.

---

## Filename Format

Renamed PDFs use:

```text
YEAR-VENUE-Keyword1-Keyword2-Keyword3-FirstAuthor.pdf
```

Example:

```text
2026-ICRA-Diffusion-Tactile-Generation-Wen.pdf
```

If metadata is uncertain, fallback values may be used:

```text
Unknown-Venue-Tactile-Sensing-Grasping-Li.pdf
2025-arXiv-Vision-Tactile-Policy-Zhang.pdf
```

If canonical filename collisions occur, suffixes are added automatically.

---

## Research Themes

Physical PDF folders are based on the primary research theme.

| Theme | Description |
|---|---|
| `Design_and_Fabrication` | Sensor design, device fabrication, grippers, tactile skins, robotic hardware, material design |
| `Multimodal_Perception` | Tactile perception, vision-tactile fusion, sensing, recognition, contact estimation |
| `Robot_Learning` | Imitation learning, reinforcement learning, diffusion policy, robot foundation models, sim-to-real |
| `Human_Robot_Interaction` | Haptics, teleoperation, assistive interfaces, shared autonomy, user studies, wearable interfaces |

If a paper cannot be confidently classified, it is placed under:

```text
01_Renamed_PDFs_By_Research_Theme/Unclassified/
```

---

## Application Tags

Applications are used in metadata and notes.

Supported applications:

```text
Assistive_Robot
Robotic_Arm_Manipulation
Surgical_Robot
Micro_Nano_Robots
Wearable_Haptic_Device
Soft_Robot
Tactile_Sensing
General_Robotics
```

A paper can belong to multiple applications.

Example:

```yaml
applications:
  - Robotic_Arm_Manipulation
  - Tactile_Sensing
```

---

## Installation

### 1. Clone the repository

```powershell
git clone https://github.com/dianzdd123/robotics-obsidian-paper-wiki-organizer.git
cd robotics-obsidian-paper-wiki-organizer
```

### 2. Create a Python virtual environment

```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -e .
pip install -r requirements.txt
```

---

## Configuration

Create your local config file:

```powershell
copy examples\config.example.yaml config.yaml
```

Then edit `config.yaml`.

Example Windows configuration:

```yaml
raw_data_root: "C:\\Obsidian-Website\\Raw-Papers-All"

new_papers_inbox: "C:\\Obsidian-Website\\Publications\\03_New_Papers_Inbox\\To_Process"
new_papers_processed_archive: "C:\\Obsidian-Website\\Publications\\03_New_Papers_Inbox\\Processed_Originals"
new_papers_needs_review: "C:\\Obsidian-Website\\Publications\\03_New_Papers_Inbox\\Needs_Review"

output_root: "C:\\Obsidian-Website\\Publications"
pdf_output_root: "C:\\Obsidian-Website\\Publications\\01_Renamed_PDFs_By_Research_Theme"
notes_output_root: "C:\\Obsidian-Website\\Publications\\02_Obsidian_Notes"
metadata_folder: "C:\\Obsidian-Website\\Publications\\90_Metadata"

dry_run: true
mode: "copy"

filename_format: "{year}-{venue}-{kw1}-{kw2}-{kw3}-{first_author}.pdf"

overwrite_existing_pdfs: false
overwrite_existing_notes: false
regenerate_existing_summaries: false
```

Always start with:

```yaml
dry_run: true
```

---

# First-Time Usage

Use first-time mode when you want to process your existing large raw paper folder.

Your raw papers are in:

```text
C:\Obsidian-Website\Raw-Papers-All
```

Your organised output will be created in:

```text
C:\Obsidian-Website\Publications
```

---

## Step 1 — Run a dry run

```powershell
cd C:\Obsidian-Website\robotics-obsidian-paper-wiki-organizer
.venv\Scripts\activate

python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run
```

This scans the raw folder and generates review logs.

It should not perform the final import.

---

## Step 2 — Review the dry-run logs

Open:

```text
C:\Obsidian-Website\Publications\90_Metadata\rename_log.csv
```

Check columns such as:

```text
original_raw_path
renamed_pdf_path
vault_relative_pdf_path
new_filename
title
year
venue
first_author
primary_research_theme
secondary_research_themes
applications
keywords
doi
confidence
summary_status
```

Also review:

```text
C:\Obsidian-Website\Publications\90_Metadata\duplicate_candidates.csv
C:\Obsidian-Website\Publications\90_Metadata\low_confidence_review.csv
```

Look for:

```text
Unknown year
Unknown venue
Unknown author
Unclassified papers
Wrong research theme
Wrong application
Bad filename
Duplicate candidates
Name collision suffixes
```

---

## Step 3 — Understand what to expect after dry run

After a dry run, it is normal if this folder is still empty:

```text
C:\Obsidian-Website\Publications\01_Renamed_PDFs_By_Research_Theme
```

Dry run mainly creates metadata logs so you can review the proposed changes.

It may show output such as:

```text
Paper Wiki Organiser  [DRY RUN / first_run]
PDFs processed   : 76
rename_log.csv   -> C:\Obsidian-Website\Publications\90_Metadata\rename_log.csv
```

This means the tool has previewed the organisation, but has not copied PDFs yet.

---

## Step 4 — Run the real first-time import

After reviewing `rename_log.csv`, run:

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run
```

The `--run` flag is important.

If you do not pass `--run`, the command may still run in dry-run mode depending on your config.

---

## Step 5 — Check the renamed PDFs

After the real import, check:

```text
C:\Obsidian-Website\Publications\01_Renamed_PDFs_By_Research_Theme
```

You should see folders like:

```text
Design_and_Fabrication
Human_Robot_Interaction
Multimodal_Perception
Robot_Learning
Unclassified
```

Inside each theme folder, you should see year folders.

Example:

```text
C:\Obsidian-Website\Publications\01_Renamed_PDFs_By_Research_Theme\Multimodal_Perception\2026
```

---

## Step 6 — Check the Obsidian notes

Open:

```text
C:\Obsidian-Website\Publications\02_Obsidian_Notes\Papers
```

Open a `.md` file and check that it contains a link like:

```markdown
[[01_Renamed_PDFs_By_Research_Theme/Multimodal_Perception/2026/2026-ICRA-Diffusion-Tactile-Generation-Wen.pdf|Open PDF]]
```

It should not link to:

```text
C:\Obsidian-Website\Raw-Papers-All
```

---

# Second-Time / Incremental Usage

Use incremental mode when you add new papers later.

Do not add future papers to:

```text
C:\Obsidian-Website\Raw-Papers-All
```

That folder is for the first-time import.

Instead, put new papers here:

```text
C:\Obsidian-Website\Publications\03_New_Papers_Inbox\To_Process
```

---

## Step 1 — Add new PDFs

Copy new PDFs into:

```text
C:\Obsidian-Website\Publications\03_New_Papers_Inbox\To_Process
```

---

## Step 2 — Run incremental dry run

```powershell
cd C:\Obsidian-Website\robotics-obsidian-paper-wiki-organizer
.venv\Scripts\activate

python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental --dry-run
```

This should process only papers in the new-papers inbox.

---

## Step 3 — Review logs

Open:

```text
C:\Obsidian-Website\Publications\90_Metadata\rename_log.csv
C:\Obsidian-Website\Publications\90_Metadata\duplicate_candidates.csv
```

Check whether the new papers are correctly identified, renamed, and classified.

---

## Step 4 — Run real incremental import

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental --run
```

This should:

```text
Process only new papers
Avoid reprocessing the old library
Detect duplicates
Append metadata
Generate notes for new papers
Copy renamed PDFs into the correct theme/year folder
```

---

# Obsidian Workflow

Open Obsidian and choose:

```text
Open folder as vault
```

Select:

```text
C:\Obsidian-Website\Publications
```

Then browse:

```text
01_Renamed_PDFs_By_Research_Theme
02_Obsidian_Notes/Papers
02_Obsidian_Notes/By_Research_Theme
02_Obsidian_Notes/By_Application
02_Obsidian_Notes/By_Year
02_Obsidian_Notes/Presentation_Summaries
90_Metadata
```

---

## Obsidian PDF Links

Generated notes should use vault-relative links.

Correct:

```markdown
[[01_Renamed_PDFs_By_Research_Theme/Multimodal_Perception/2026/example.pdf|Open PDF]]
```

Incorrect:

```markdown
[[C:\Obsidian-Website\Raw-Papers-All\example.pdf]]
```

Incorrect:

```markdown
[[C:\Obsidian-Website\Publications\01_Renamed_PDFs_By_Research_Theme\...]]
```

The Obsidian vault root should be:

```text
C:\Obsidian-Website\Publications
```

So links should start from inside that folder.

---

## Paper Note Structure

Each paper note should include:

```text
Title
Authors
Year
Venue
First author
DOI
Keywords
Primary research theme
Secondary research themes
Applications
PDF link
Citation
One-sentence takeaway
Research problem
Motivation
Key contributions
Method
Experiments
Strengths
Limitations
Future work
Relevance to research presentation
Suggested slide summary
```

Example:

```markdown
---
title: "Diffusion-based Tactile Generation for Robot Manipulation"
authors:
  - "Wen et al."
year: 2026
venue: ICRA
first_author: Wen
primary_theme: Multimodal_Perception
secondary_themes:
  - Robot_Learning
applications:
  - Robotic_Arm_Manipulation
  - Tactile_Sensing
keywords:
  - Diffusion
  - Tactile
  - Generation
pdf_path: "01_Renamed_PDFs_By_Research_Theme/Multimodal_Perception/2026/2026-ICRA-Diffusion-Tactile-Generation-Wen.pdf"
---

# Diffusion-based Tactile Generation for Robot Manipulation

## PDF

[[01_Renamed_PDFs_By_Research_Theme/Multimodal_Perception/2026/2026-ICRA-Diffusion-Tactile-Generation-Wen.pdf|Open PDF]]

## One-Sentence Takeaway

...

## Research Problem

...

## Motivation

...

## Key Contributions

1. ...
2. ...
3. ...

## Method

...

## Experiments

...

## Strengths

...

## Limitations

...

## Future Work

...

## Relevance to Research Presentation

...

## Suggested Slide Summary

**Slide title:** ...

**Main message:** ...

**Recommended figure:** ...

**Talking point:** ...
```

---

# Regenerating Obsidian Notes

Use this if your PDFs are already renamed but you want to regenerate notes.

---

## Safe option: create missing notes only

Keep this in `config.yaml`:

```yaml
overwrite_existing_notes: false
regenerate_existing_summaries: false
overwrite_existing_pdfs: false
```

Then run:

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run
```

---

## Full note regeneration

First back up your current notes:

```powershell
Copy-Item "C:\Obsidian-Website\Publications\02_Obsidian_Notes" `
  "C:\Obsidian-Website\Publications\02_Obsidian_Notes_BACKUP" `
  -Recurse -Force
```

Then edit `config.yaml`:

```yaml
overwrite_existing_notes: true
regenerate_existing_summaries: true
overwrite_existing_pdfs: false
```

Then run:

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run
```

This should regenerate notes and summaries without overwriting PDFs.

---

# Duplicate Review

Potential duplicates are written to:

```text
C:\Obsidian-Website\Publications\90_Metadata\duplicate_candidates.csv
```

Review duplicates manually.

Classify them as:

```text
Exact duplicate
arXiv vs conference/journal version
Supplementary or appendix version
False positive
```

Do not delete anything automatically.

---

# Unclassified Paper Review

If the tool creates:

```text
01_Renamed_PDFs_By_Research_Theme/Unclassified
```

open those papers manually.

You can either:

```text
Move the renamed PDF to the correct theme/year folder
Update classifier rules
Rerun dry run
Leave it for later manual review
```

---

# CLI Reference

## First-time dry run

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run
```

## First-time real import

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run
```

## Incremental dry run

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental --dry-run
```

## Incremental real import

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental --run
```

---

# Metadata Outputs

## `rename_log.csv`

Primary review file before real import.

Important columns:

```text
original_raw_path
renamed_pdf_path
vault_relative_pdf_path
main_note_path
theme_note_paths
application_note_paths
year_note_path
new_filename
title
year
venue
first_author
primary_research_theme
secondary_research_themes
applications
keywords
doi
confidence
summary_status
```

## `papers_catalog.csv`

Spreadsheet-friendly catalog.

## `papers_catalog.json`

Persistent machine-readable catalog.

## `duplicate_candidates.csv`

Potential duplicate papers.

## `low_confidence_review.csv`

Papers below confidence threshold.

## `run_log_<timestamp>.json`

Timestamped run record.

---

# Tests with `pytest`

`pytest` is used to check whether the project code still works after you edit it.

It does **not** organise your papers.

It only runs small tests against the code.

Use `pytest` after editing source files such as:

```text
src/robotics_paper_wiki/organise_papers.py
src/robotics_paper_wiki/classify_paper.py
src/robotics_paper_wiki/obsidian_notes.py
src/robotics_paper_wiki/metadata_extract.py
src/robotics_paper_wiki/duplicate_detection.py
```

You do not need to run `pytest` every time you add new PDFs.

---

## How to run tests

```powershell
cd C:\Obsidian-Website\robotics-obsidian-paper-wiki-organizer
.venv\Scripts\activate
pytest tests/ -v
```

If `pytest` is not installed:

```powershell
pip install pytest
pytest tests/ -v
```

---

## What successful test output looks like

You want to see something like:

```text
============================= test session starts =============================
collected 3 items

tests/test_filename_generation.py::test_filename_generation PASSED
tests/test_vault_relative_links.py::test_vault_relative_link PASSED
tests/test_classification_rules.py::test_theme_classification PASSED

============================== 3 passed in 0.42s ==============================
```

This means the basic code checks passed.

---

## What failed test output looks like

A failed test may look like:

```text
FAILED tests/test_vault_relative_links.py::test_vault_relative_link
```

or:

```text
AssertionError: expected vault-relative path, got C:\Obsidian-Website\Raw-Papers-All\paper.pdf
```

This means the code has a problem. For example, it might be generating a bad Obsidian link.

---

## What the tests should check

### 1. Filename generation

Input metadata:

```text
year: 2026
venue: ICRA
keywords: Diffusion, Tactile, Generation
first author: Wen
```

Expected filename:

```text
2026-ICRA-Diffusion-Tactile-Generation-Wen.pdf
```

---

### 2. Obsidian PDF links

Expected:

```markdown
[[01_Renamed_PDFs_By_Research_Theme/Multimodal_Perception/2026/example.pdf|Open PDF]]
```

Not expected:

```markdown
[[C:\Obsidian-Website\Raw-Papers-All\example.pdf]]
```

---

### 3. Research theme classification

A paper about tactile sensing and visual-tactile perception should probably map to:

```text
Multimodal_Perception
```

A paper about diffusion policies or imitation learning should probably map to:

```text
Robot_Learning
```

---

### 4. Duplicate detection

If two papers have the same DOI or same PDF hash, the test should confirm they are detected as duplicate candidates.

---

## Difference between `pytest`, dry run, and live run

| Command | Purpose |
|---|---|
| `pytest tests/ -v` | Checks whether the code logic works |
| `python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run` | Previews how your actual PDFs will be renamed and classified |
| `python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run` | Actually copies, renames, groups PDFs, and writes notes |

Recommended order after changing project code:

```powershell
pytest tests/ -v
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run
```

If both look good, then run:

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run
```

Simple rule:

```text
Use pytest to check the software.
Use --dry-run to check the paper organisation result.
Use --run only after the dry-run output looks correct.
```

---

# Using with Claude Code

Useful Claude Code prompts:

## Review dry-run output

```text
Please inspect:
C:\Obsidian-Website\Publications\90_Metadata\rename_log.csv

Check whether filenames, years, venues, research themes, and applications look correct.
List suspicious metadata.
Do not modify Raw-Papers-All.
```

## Improve classification

```text
Please improve the classifier keyword rules for robotics papers.

Focus on:
- Design_and_Fabrication
- Multimodal_Perception
- Robot_Learning
- Human_Robot_Interaction

Use rename_log.csv and papers_catalog.csv as evidence.
Do not modify raw PDFs.
```

## Regenerate notes

```text
Please regenerate Obsidian notes only.
Do not overwrite PDFs.
Ensure every note links to the renamed PDF using vault-relative paths.
```

## Review duplicates

```text
Please review duplicate_candidates.csv and group duplicates into:
- exact duplicate
- arXiv vs conference/journal version
- supplementary version
- false positive

Do not delete anything.
```

---

# Troubleshooting

## `01_Renamed_PDFs_By_Research_Theme` is empty

You probably only ran dry run.

Fix:

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run
```

---

## Command still says `[DRY RUN]`

Use the explicit live flag:

```powershell
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --run
```

Or set:

```yaml
dry_run: false
```

---

## `PermissionError` writing `rename_log.csv`

Close the CSV in:

```text
Excel
VS Code
Obsidian
File Explorer preview pane
```

Then rerun.

You can also remove the old log:

```powershell
Remove-Item "C:\Obsidian-Website\Publications\90_Metadata\rename_log.csv" -Force -ErrorAction SilentlyContinue
```

---

## PDF links do not open in Obsidian

Make sure you opened this folder as the Obsidian vault:

```text
C:\Obsidian-Website\Publications
```

Then check that notes use links like:

```markdown
[[01_Renamed_PDFs_By_Research_Theme/Multimodal_Perception/2026/example.pdf|Open PDF]]
```

---

## Many `Unknown` years or venues

Improve metadata extraction rules or review manually.

Possible sources for metadata:

```text
PDF first page
filename
DOI
conference name
journal footer
arXiv ID
```

---

## Many unclassified papers

Update classifier keywords or manually review those papers.

---

# GitHub Hygiene

Do not commit:

```text
Raw PDFs
Renamed PDFs
Generated Publications folder
Generated Obsidian notes from private papers
CSV metadata
JSON metadata
Private logs
```

Recommended `.gitignore`:

```gitignore
*.pdf
*.bib
*.ris
*.csv
*.json
*.log

Raw-Papers-All/
Publications/
New-Papers-Inbox/

.venv/
__pycache__/
*.pyc
.pytest_cache/
dist/
build/
*.egg-info/

.DS_Store
Thumbs.db
.vscode/
```

Commit only:

```text
Source code
Docs
Examples
Tests
Templates
README
LICENSE
Configuration examples
```

---

# Project Structure

```text
robotics-obsidian-paper-wiki-organizer/
├── README.md
├── LICENSE
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── docs/
├── examples/
├── src/
│   └── robotics_paper_wiki/
│       ├── organise_papers.py
│       ├── metadata_extract.py
│       ├── classify_paper.py
│       ├── obsidian_notes.py
│       ├── summarise_paper.py
│       ├── duplicate_detection.py
│       └── utils.py
└── tests/
```

---

# Roadmap

Possible future improvements:

- Better DOI lookup
- Crossref or Semantic Scholar metadata enrichment
- Zotero and BibTeX integration
- Figure extraction for presentation slides
- Better arXiv vs published-version handling
- LLM-assisted summary generation
- Obsidian Dataview examples
- Web preview of generated wiki
- GitHub Actions tests

---

# License

MIT — see [LICENSE](LICENSE).

