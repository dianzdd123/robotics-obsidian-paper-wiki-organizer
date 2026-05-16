# Example Output Folder Structure

This shows what a typical Publications vault looks like after running the first-time import on a collection of 76 robotics papers.

```
Publications/
│
├── 00_Inbox_Review/
│   └── (empty — all 76 papers exceeded the 0.5 confidence threshold)
│
├── 01_Renamed_PDFs_By_Research_Theme/
│   │
│   ├── Design_and_Fabrication/
│   │   ├── 2021/
│   │   │   └── 2021-RAL-Gel-Sensor-Fabrication-Li.pdf
│   │   ├── 2023/
│   │   │   ├── 2023-ICRA-Tactile-Elastomer-Design-Zhang.pdf
│   │   │   └── 2023-Nature-MagicTac-Sensor-Wang.pdf
│   │   └── 2024/
│   │       └── 2024-TASE-Magnetic-Microstructure-Chen.pdf
│   │
│   ├── Multimodal_Perception/
│   │   ├── 2022/
│   │   │   └── 2022-ICRA-Visuotactile-Localisation-Zhang.pdf
│   │   └── 2024/
│   │       ├── 2024-ICRA-Depth-Estimation-Dataset-Wang.pdf
│   │       └── 2024-RAL-Tactile-Saliency-Detection-Li.pdf
│   │
│   ├── Robot_Learning/
│   │   ├── 2022/
│   │   │   └── 2022-ICRA-Diffusion-Policy-Tactile-Wen.pdf
│   │   └── 2024/
│   │       └── 2024-RAL-Sim-to-Real-Gripper-Chen.pdf
│   │
│   └── Human_Robot_Interaction/
│       ├── 2021/
│       │   └── 2021-ICRA-Surgical-Gesture-Recognition-Zhang.pdf
│       └── 2023/
│           └── 2023-TASE-Teleoperation-Haptic-Feedback-Li.pdf
│
├── 02_Obsidian_Notes/
│   │
│   ├── Papers/
│   │   ├── 2021-ICRA-Surgical-Gesture-Recognition-Zhang.md
│   │   ├── 2022-ICRA-Visuotactile-Localisation-Zhang.md
│   │   └── ... (one .md per paper)
│   │
│   ├── Presentation_Summaries/
│   │   ├── 2021-ICRA-Surgical-Gesture-Recognition-Zhang_summary.md
│   │   └── ... (one _summary.md per paper)
│   │
│   ├── By_Application/
│   │   ├── Surgical_Robot/
│   │   │   ├── 2021-ICRA-Surgical-Gesture-Recognition-Zhang_link.md
│   │   │   └── ...
│   │   ├── Tactile_Sensing/
│   │   │   └── ...
│   │   └── ... (one subfolder per application)
│   │
│   ├── By_Year/
│   │   ├── 2021/
│   │   │   └── 2021-ICRA-Surgical-Gesture-Recognition-Zhang_link.md
│   │   ├── 2022/
│   │   └── ...
│   │
│   ├── Indexes/
│   │   ├── Theme_Index_Design_and_Fabrication.md
│   │   ├── Theme_Index_Multimodal_Perception.md
│   │   ├── Theme_Index_Robot_Learning.md
│   │   ├── Theme_Index_Human_Robot_Interaction.md
│   │   ├── App_Index_Surgical_Robot.md
│   │   ├── App_Index_Tactile_Sensing.md
│   │   ├── Year_Index_2021.md
│   │   ├── Year_Index_2022.md
│   │   └── ...
│   │
│   └── Synthesis/
│       └── (empty — add your own cross-paper notes here)
│
├── 03_New_Papers_Inbox/
│   ├── To_Process/         ← drop new PDFs here
│   ├── Processed_Originals/
│   └── Needs_Review/
│
├── 90_Metadata/
│   ├── rename_log.csv             76 rows, 22 columns
│   ├── papers_catalog.csv         76 rows, 28 columns
│   ├── papers_catalog.json
│   ├── low_confidence_review.csv  (empty — all passed threshold)
│   ├── duplicate_candidates.csv   12 rows (6 resolved collisions x 2)
│   └── run_log_20260516_152403.json
│
└── 99_Duplicates_or_Unclear/
    └── (empty — all 6 collisions were resolved by suffix disambiguation)
```

## Example: Paper note

`02_Obsidian_Notes/Papers/2021-ICRA-Surgical-Gesture-Recognition-Zhang.md`

```yaml
---
title: "Surgical Gesture Recognition Based on Bidirectional Multi-Layer Independently RNN"
authors:
  - "Dandan Zhang"
year: 2021
venue: ICRA
doi: 10.1109/ICRA48506.2021.9561803
primary_theme: Human_Robot_Interaction
secondary_themes:
  - _none_
applications:
  - Surgical_Robot
year_bucket: "2020-2021"
confidence: 1.0
---
```

## Example: Theme index

`02_Obsidian_Notes/Indexes/Theme_Index_Human_Robot_Interaction.md`

```markdown
---
index_type: research_theme
theme: Human_Robot_Interaction
date_updated: 2026-05-16
---

# Human Robot Interaction — Paper Index

| Title | Year | Venue | Applications |
|---|---|---|---|
| [[2023-TASE-Teleoperation-Haptic-Feedback-Li|Teleoperation with Haptic Feedback]] | 2023 | TASE | Surgical_Robot |
| [[2021-ICRA-Surgical-Gesture-Recognition-Zhang|Surgical Gesture Recognition ...]] | 2021 | ICRA | Surgical_Robot |
```

## Example: Vault-relative PDF link

From any note in `02_Obsidian_Notes/Papers/`:
```
[[01_Renamed_PDFs_By_Research_Theme/Human_Robot_Interaction/2021/2021-ICRA-Surgical-Gesture-Recognition-Zhang.pdf|Open PDF]]
```

This is a vault-relative path. The vault root is the `Publications/` folder.
