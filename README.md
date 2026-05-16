# robotics-obsidian-paper-wiki-organizer

A Python + Claude Code workflow for organising robotics research papers into a structured [Obsidian](https://obsidian.md) wiki.

Inspired by and compatible with: [llm-wiki-paper-organizer](https://github.com/dianzdd123/llm-wiki-paper-organizer)

---

## Features

- **Metadata extraction** — title, authors, year, venue, DOI, abstract from PDF layout, text, filename, and document metadata
- **Keyword classification** — rule-based assignment of research themes and application tags
- **Canonical renaming** — `YEAR-VENUE-Keyword1-Keyword2-Keyword3-FirstAuthor.pdf`
- **Vault-relative Obsidian links** — no absolute Windows paths inside generated notes
- **Extended paper analysis** — problem, motivation, contributions, method, experiments, strengths, limitations, future work, slide summary
- **Dry-run mode** — preview all proposed renames before any file is touched
- **Incremental import** — add new papers without reprocessing the full collection
- **Duplicate detection** — by DOI, normalised title, canonical filename, and PDF SHA-256 hash
- **Metadata catalog** — `rename_log.csv`, `papers_catalog.csv/json`, `low_confidence_review.csv`, `duplicate_candidates.csv`

---

## Research Themes

| Theme | Scope |
|---|---|
| `Design_and_Fabrication` | Sensor design, device fabrication, hardware platforms |
| `Multimodal_Perception` | Sensing, detection, localisation, tactile perception, multi-sensor fusion |
| `Robot_Learning` | RL, imitation learning, sim-to-real, diffusion policies |
| `Human_Robot_Interaction` | Teleoperation, shared control, haptics, VR/AR |

## Application Tags

`Assistive_Robot` · `Robotic_Arm_Manipulation` · `Surgical_Robot` · `Micro_Nano_Robots` · `Wearable_Haptic_Device` · `Soft_Robot` · `Tactile_Sensing` · `General_Robotics`

---

## Installation

**Requirements:** Python 3.10+

```bash
# Clone the repository
git clone https://github.com/<your-username>/robotics-obsidian-paper-wiki-organizer.git
cd robotics-obsidian-paper-wiki-organizer

# Install in editable mode (recommended for development)
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

---

## Quick Start

### Step 1 — Configure

```bash
cp examples/config.example.yaml config.yaml
```

Edit `config.yaml` to set your paths:

```yaml
raw_data_root:   "/path/to/your/raw/PDFs"
output_root:     "/path/to/your/Publications"
```

### Step 2 — Dry run (safe preview)

```bash
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run
```

This generates all notes and logs — **no PDFs are copied or renamed**.

### Step 3 — Review

Open `Publications/90_Metadata/rename_log.csv` and check the proposed renames.

### Step 4 — Import

```bash
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run
```

---

## CLI Reference

| Command | Effect |
|---|---|
| `--mode first_run --dry-run` | Scan `raw_data_root`, preview only |
| `--mode first_run` | Scan `raw_data_root`, copy + rename PDFs |
| `--mode incremental --dry-run` | Scan `new_papers_inbox`, preview only |
| `--mode incremental` | Scan inbox, copy + rename, archive originals |

Additional flags:

```
--config PATH     Path to config.yaml (default: config.yaml)
--dry-run         Force dry-run even if config says dry_run: false
--run             Force live run even if config says dry_run: true
```

---

## Output Structure

```
Publications/
├── 00_Inbox_Review/                        Low-confidence papers for manual review
├── 01_Renamed_PDFs_By_Research_Theme/
│   ├── Design_and_Fabrication/
│   │   ├── 2024/
│   │   │   └── 2024-ICRA-Tactile-Sensor-Design-Zhang.pdf
│   ├── Multimodal_Perception/
│   ├── Robot_Learning/
│   └── Human_Robot_Interaction/
├── 02_Obsidian_Notes/
│   ├── Papers/                             Main note per paper
│   ├── Presentation_Summaries/             Extended analysis per paper
│   ├── By_Research_Theme/                  Theme-grouped link stubs
│   ├── By_Application/                     Application-grouped link stubs
│   ├── By_Year/                            Year-grouped link stubs
│   ├── Synthesis/                          (for your own cross-paper notes)
│   └── Indexes/                            Auto-generated index notes
├── 03_New_Papers_Inbox/
│   ├── To_Process/                         Drop new PDFs here
│   ├── Processed_Originals/                Archived after import
│   └── Needs_Review/                       Low-confidence new papers
├── 90_Metadata/
│   ├── rename_log.csv                      Primary review file
│   ├── papers_catalog.csv
│   ├── papers_catalog.json
│   ├── low_confidence_review.csv
│   ├── duplicate_candidates.csv
│   └── run_log_<timestamp>.json
└── 99_Duplicates_or_Unclear/
```

---

## Obsidian Note Format

Each paper gets a Markdown note with YAML frontmatter and vault-relative PDF link:

```markdown
---
title: "Tactile Sensor Design for Surgical Robots"
authors:
  - "Dandan Zhang"
year: 2024
venue: ICRA
primary_theme: Design_and_Fabrication
applications:
  - Surgical_Robot
  - Tactile_Sensing
confidence: 0.95
---

# Tactile Sensor Design for Surgical Robots

## Abstract
> ...

## One-Sentence Takeaway
> ...

## Key Contributions
- ...

**PDF:** [[01_Renamed_PDFs_By_Research_Theme/Design_and_Fabrication/2024/2024-ICRA-Tactile-Sensor-Design-Zhang.pdf|Open PDF]]
```

See [examples/paper-note-template.md](examples/paper-note-template.md) for the full template.

---

## Using with Claude Code

This project is designed to work alongside [Claude Code](https://claude.ai/code). See [docs/claude-code-workflow.md](docs/claude-code-workflow.md) for:

- Prompts for extending theme keyword lists
- Prompts for reviewing rename_log.csv
- Prompts for adding new venues
- Prompts for generating synthesis notes

---

## Configuration

See [examples/config.example.yaml](examples/config.example.yaml) for all options.

Key settings:

```yaml
dry_run: true                # Always start true; switch to false after reviewing logs
confidence:
  threshold: 0.50            # Papers below this go to 00_Inbox_Review

overwrite_existing_pdfs:     false
overwrite_existing_notes:    false
regenerate_existing_summaries: false
```

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Project Structure

```
robotics-obsidian-paper-wiki-organizer/
├── src/
│   └── robotics_paper_wiki/
│       ├── organise_papers.py      Main orchestrator + CLI
│       ├── metadata_extract.py     PDF metadata extraction
│       ├── classify_paper.py       Theme + application classification
│       ├── obsidian_notes.py       Obsidian note generation
│       ├── summarise_paper.py      Extended paper analysis
│       ├── duplicate_detection.py  Duplicate detection
│       └── utils.py                Shared utilities
├── docs/                           Tutorials and design docs
├── examples/                       Config template, note templates, prompts
└── tests/                          Unit tests
```

---

## Contributing

Contributions welcome. To add support for a new:

- **Research theme** — add keywords to `config.yaml` under `theme_keywords`
- **Application** — add to `applications` list and `application_keywords`
- **Venue** — add to `venues` section

---

## License

MIT — see [LICENSE](LICENSE).
