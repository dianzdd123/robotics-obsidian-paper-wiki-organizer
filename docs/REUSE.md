# Reusing robotics-obsidian-paper-wiki-organizer

Python tools for organising robotics PDFs into an Obsidian vault.

**Current scope:** Python package with local metadata extraction, copy-based import and reviewable dry runs.


## Cross-platform quick start

Python 3.10 or newer is required by `pyproject.toml`.

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e '.[dev]'
python -m pytest
python scripts/check_repository.py
paper-wiki --help
```

Copy `examples/config.example.yaml` to a local `config.yaml` and replace every example path. Start with a small copied sample of papers. The installed `paper-wiki` entry point and `python -m robotics_paper_wiki.organise_papers` invoke the same CLI.

```bash
paper-wiki --config config.yaml --mode first_run --dry-run
```

Review metadata and planned destinations before running with `--run`. The two flags are mutually exclusive. A dry run still creates review logs/directories; it does not mean zero filesystem writes. In incremental mode, successful imports may archive inbox originals; keep the raw collection and backups separate.

## Code map

| Module | Responsibility |
|---|---|
| `organise_papers.py` | Configuration, scanning, import orchestration and CLI |
| `metadata_extract.py` | PDF metadata/text extraction |
| `classify_paper.py` | Theme/application classification and filenames |
| `duplicate_detection.py` | Duplicate candidates and canonical-name collisions |
| `obsidian_notes.py` | Paper notes, indexes and vault-relative links |
| `summarise_paper.py` | Presentation-summary scaffolding |
| `utils.py` | File operations and path/text helpers |

Implementation files live under `src/robotics_paper_wiki/`. Configuration, templates and complete first-time/incremental walkthroughs are linked from the main README.

## Inputs, outputs and checks

Input: a directory of PDF files plus YAML configuration. PDF suffix matching is case-insensitive, so `.PDF` files are included on Linux. A missing source directory raises an explicit error. Output: renamed PDF copies, Obsidian notes and metadata/review logs beneath configured paths. Keep output directories outside the raw-data tree to avoid re-importing generated copies.

The CLI rejects simultaneous `--run` and `--dry-run` before reading configuration. Tests cover filename generation, classification, vault links, PDF discovery and that flag conflict. Metadata extraction is heuristic; inspect uncertain fields and generated summaries against the paper. Scanned PDFs may need a separate OCR step.

## Adapting the tool

Change theme/application rules and venue aliases in a local copy of the example configuration. Preserve provenance and original files. Test new rules on a small known collection before importing a full library. The code's MIT licence does not grant redistribution rights for the papers you process.

## Attribution and reuse permissions

Read the existing [licence](../LICENSE) before redistributing code. External datasets, models, papers and images may have separate terms.

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for the local workflow and what to include with a proposed change.
