# Claude Code Workflow

This document explains how to use [Claude Code](https://claude.ai/code) alongside the paper organiser to curate, extend, and synthesise your Obsidian wiki.

---

## Setup

Open Claude Code in your Publications vault:

```bash
cd /path/to/Publications
claude
```

Or open it in the project root alongside the scripts:

```bash
cd /path/to/robotics-obsidian-paper-wiki-organizer
claude
```

---

## Prompts for common tasks

### 1. Review rename_log.csv and fix misclassifications

```
Read 90_Metadata/rename_log.csv and identify:
1. Papers where primary_theme looks wrong based on the title
2. Papers with confidence below 0.6
3. Papers with "Unclassified" as primary_theme

For each issue, suggest which theme or application keywords to add to config.yaml
to fix the classification. Show me the config.yaml additions.
```

### 2. Add a new research theme

```
I want to add a new research theme called "Soft_Robotics" to the organiser.

Look at config.yaml and add:
- "Soft_Robotics" to the research_themes list
- A keyword list for it under theme_keywords, covering:
  soft actuators, pneumatic systems, hydrogel robots,
  compliant mechanisms, deformable robots

Keep the style consistent with the existing theme keyword lists.
```

### 3. Add a new venue

```
Add these venue aliases to the venues section of config.yaml:
- "TRO" for "IEEE Transactions on Robotics"
- "IJRR" for "International Journal of Robotics Research"
- "RSS" for "Robotics: Science and Systems"

Use the same format as existing entries.
```

### 4. Generate a synthesis note across papers

```
Look at all the papers in 02_Obsidian_Notes/By_Application/Tactile_Sensing/
and generate a synthesis note that:
1. Groups papers by method type (optical, magnetic, resistive, etc.)
2. Creates a comparison table: paper | method | sensor type | resolution | year
3. Identifies the most cited trends
4. Suggests 3 open research questions

Save the result to 02_Obsidian_Notes/Synthesis/Tactile_Sensing_Survey.md
```

### 5. Find papers relevant to a specific presentation

```
I'm preparing a 20-minute talk on "Learning-based tactile sensing for surgical robots".

Search through 02_Obsidian_Notes/Papers/ and find the 5-8 most relevant papers.
For each, extract:
- One-sentence summary
- Key contribution (from the Key Contributions section)
- Main result

Then suggest a narrative arc for the talk with these papers in order.
```

### 6. Check for papers that should be re-classified

```
Read all .md files in 02_Obsidian_Notes/Papers/ and find any where:
- The primary_theme is "Unclassified"
- The confidence field is below 0.6
- The title contains keywords that suggest a different theme from what's assigned

For each misclassification, suggest the correct theme and the keyword
that should be added to config.yaml.
```

### 7. Generate a reading list for a collaborator

```
A collaborator is joining who specialises in surgical robotics.
They need a reading list of our best papers in Surgical_Robot application.

From 02_Obsidian_Notes/By_Application/Surgical_Robot/, create a reading list Markdown file that:
- Groups papers by year
- Includes a one-sentence description of each
- Marks the 3 most important papers with a star
- Saves to 02_Obsidian_Notes/Synthesis/Surgical_Robot_Reading_List.md
```

### 8. Extend the extended analysis for a specific paper

```
Open 02_Obsidian_Notes/Presentation_Summaries/2024-ICRA-Tactile-Sensor-Zhang_summary.md

The abstract extraction left several sections as placeholders.
Open the corresponding PDF at 01_Renamed_PDFs_By_Research_Theme/Design_and_Fabrication/2024/2024-ICRA-Tactile-Sensor-Zhang.pdf and:
1. Fill in the Research Problem section
2. Fill in the Key Contributions section
3. Fill in the Experiments section
4. Fill in the Limitations section

Keep the same Markdown format.
```

### 9. Update all index notes

```
The papers_catalog.json may have changed since the index notes were last generated.
Re-run the organiser in dry-run mode to regenerate all index notes:

python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run

Then set overwrite_existing_notes: true in config.yaml and re-run to update them.
```

### 10. Find duplicate or near-duplicate papers

```
Read 90_Metadata/duplicate_candidates.csv and 90_Metadata/papers_catalog.csv.
Identify any papers that:
- Have the same first author and year but different titles (possible erratum/version)
- Have very similar titles (edit distance < 5 words)

List them with the match reason and suggest which to keep.
```

---

## Tips for working with Claude Code in this project

- **Use the Grep tool** to find papers by keyword across all notes: search for a term in `02_Obsidian_Notes/Papers/`
- **Use the Read tool** to inspect a specific paper note before editing it
- **Use the Edit tool** to update the Notes or Related Papers section of a note without overwriting the auto-generated content
- **Never use Write to overwrite existing notes** unless you intend to replace the entire file — use Edit for surgical changes
- **Set regenerate_existing_summaries: true** in config.yaml before asking Claude to re-run the organiser if you want fresh summaries
- **The papers_catalog.json is authoritative** — point Claude to it for any cross-collection queries

---

## Running the organiser from within Claude Code

```
Run the paper organiser dry-run:
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run

Then show me the last 20 lines of the output and the first 5 rows of rename_log.csv.
```
