# Claude Code Prompts for the Paper Wiki

A reference collection of prompts for common tasks. Copy and paste into Claude Code.

---

## Setup and first run

```
I have a collection of robotics PDFs in /path/to/raw/PDFs.
I want to organise them into an Obsidian wiki.

1. Copy examples/config.example.yaml to config.yaml
2. Update the paths in config.yaml to point to my folders
3. Run the dry-run command and show me the output summary
4. Show me the first 10 rows of rename_log.csv
```

---

## Review and fix classifications

```
Read 90_Metadata/rename_log.csv.

Find all papers where:
- primary_theme is "Unclassified"
- OR confidence is below 0.6
- OR the title looks mismatched to the assigned theme

For each, suggest the correct theme and which keywords to add to config.yaml.
Show the config.yaml additions as a YAML snippet.
```

---

## Add a new venue

```
I'm getting papers from "IEEE Transactions on Medical Robotics and Bionics".
Add it to the venues section of config.yaml with short name "TMRB".
Include variations like "T-MRB", "TMRB", "Medical Robotics and Bionics".
```

---

## Extend a theme's keywords

```
The Multimodal_Perception theme is missing some papers about force sensing.
Add these keywords to its keyword list in config.yaml:
- force sensing
- force sensor
- force measurement
- torque sensing
- F/T sensor
- wrench estimation

Keep the YAML formatting consistent with the existing entries.
```

---

## Find papers for a literature review

```
I'm writing a literature review on "tactile perception for robotic manipulation".

Search through 02_Obsidian_Notes/Papers/ using Grep for papers tagged with
both "tactile-sensing" and "robotic-arm-manipulation".

For each matching paper, extract:
- title
- year
- venue
- one-sentence takeaway (from the Presentation_Summaries/ file)

Format as a numbered list sorted by year (newest first).
```

---

## Generate a comparison table

```
Read all papers in 02_Obsidian_Notes/By_Application/Tactile_Sensing/
and extract from each corresponding Papers/ note:
- title
- year
- venue
- primary_theme
- key method (first bullet from Key Contributions in the summary)

Create a Markdown comparison table and save it to:
02_Obsidian_Notes/Synthesis/Tactile_Sensing_Comparison.md
```

---

## Fill in placeholder sections

```
Open 02_Obsidian_Notes/Presentation_Summaries/2024-ICRA-ExamplePaper-Zhang_summary.md

Several sections show "_Not extracted — open the PDF._"

Open the PDF at 01_Renamed_PDFs_By_Research_Theme/Design_and_Fabrication/2024/2024-ICRA-ExamplePaper-Zhang.pdf

Read the paper and fill in:
- Research Problem
- Key Contributions  
- Experiments
- Key Results
- Limitations

Keep the existing Markdown structure. Do not overwrite sections that already have content.
```

---

## Update all index notes

```
Re-run the organiser to refresh all index notes:

python -m robotics_paper_wiki.organise_papers --config config.yaml --mode first_run --dry-run

Then set overwrite_existing_notes: true in config.yaml and run again to regenerate index notes only.
After that, set it back to false.
```

---

## Check for papers needing manual review

```
Read 90_Metadata/low_confidence_review.csv

For each paper, look at the extraction_notes column to understand why the confidence is low.
Group papers by the most common issue (no abstract, no venue, no year, etc.)
and suggest how to fix the extraction for each group.
```

---

## Generate a slide deck outline

```
I need to give a 45-minute talk on "tactile sensing and learning for surgical robots".

From 02_Obsidian_Notes/Papers/, find the most relevant papers across these themes:
- Tactile sensing hardware
- Tactile perception algorithms
- Learning-based control
- Surgical robot applications

Suggest a 10-slide outline with:
- Slide title
- Which paper(s) to reference
- One key figure or result to show
```

---

## Check Obsidian links are valid

```
Search all .md files in 02_Obsidian_Notes/Papers/ for PDF links of the form:
[[01_Renamed_PDFs_By_Research_Theme/...]]

For each link, check that the referenced PDF actually exists at that path.
List any broken links with the note they appear in and the missing PDF path.
```

---

## Incremental import

```
I have 5 new papers in 03_New_Papers_Inbox/To_Process/

Run:
python -m robotics_paper_wiki.organise_papers --config config.yaml --mode incremental --dry-run

Show me the output and the new rows in rename_log.csv.
Flag any that are detected as duplicates and tell me why.
```

---

## Export a bibliography

```
Read 90_Metadata/papers_catalog.json and extract all papers with:
- venue = "ICRA" OR venue = "IROS" OR venue = "RAL"
- year >= 2022

Format as a BibTeX bibliography file and save to 90_Metadata/conference_papers_2022_plus.bib

Use the canonical filename stem as the BibTeX key.
```
