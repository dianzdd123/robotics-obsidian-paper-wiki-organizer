"""
test_classification_rules.py
Tests for theme and application classification, year buckets, and keyword scoring.
"""

import pytest
from robotics_paper_wiki.metadata_extract import PaperMetadata
from robotics_paper_wiki.classify_paper import classify_paper, _year_bucket, _extract_title_keywords


# ---------------------------------------------------------------------------
# Test config (minimal — mirrors config.example.yaml structure)
# ---------------------------------------------------------------------------
_CONFIG = {
    "theme_keywords": {
        "Design_and_Fabrication": {
            "keywords": [
                "fabrication", "design", "manufacturing", "sensor design",
                "gel sensor", "elastomer", "magictac",
            ]
        },
        "Multimodal_Perception": {
            "keywords": [
                "perception", "localisation", "detection", "tactile sensing",
                "tactile sensor", "depth estimation", "visuotactile",
            ]
        },
        "Robot_Learning": {
            "keywords": [
                "reinforcement learning", "imitation learning", "deep learning",
                "sim-to-real", "diffusion policy", "neural network",
            ]
        },
        "Human_Robot_Interaction": {
            "keywords": [
                "teleoperation", "haptic", "human-robot", "shared control",
                "surgical gesture", "VR",
            ]
        },
    },
    "application_keywords": {
        "Surgical_Robot": {
            "keywords": ["surgical", "minimally invasive", "surgical robot", "surgical gesture"]
        },
        "Tactile_Sensing": {
            "keywords": ["tactile", "touch sensor", "visuotactile", "gel sensor"]
        },
        "Robotic_Arm_Manipulation": {
            "keywords": ["manipulation", "robotic arm", "gripper", "dexterous"]
        },
        "General_Robotics": {
            "keywords": ["robot", "robotic", "autonomous", "control", "system"]
        },
    },
}


def _meta(title="", abstract="", filename="test.pdf", folder="folder"):
    m = PaperMetadata(source_path=filename, filename=filename, source_folder=folder)
    m.title    = title
    m.abstract = abstract
    return m


# ---------------------------------------------------------------------------
# Primary theme assignment
# ---------------------------------------------------------------------------
class TestPrimaryTheme:
    def test_design_from_title(self):
        meta = _meta(title="A Novel Tactile Sensor Design and Fabrication Method")
        clf  = classify_paper(meta, _CONFIG)
        assert clf.primary_theme == "Design_and_Fabrication"

    def test_robot_learning_from_title(self):
        meta = _meta(title="Deep Learning for Robotic Manipulation")
        clf  = classify_paper(meta, _CONFIG)
        assert clf.primary_theme == "Robot_Learning"

    def test_hri_from_title(self):
        meta = _meta(title="Teleoperation System with Haptic Feedback")
        clf  = classify_paper(meta, _CONFIG)
        assert clf.primary_theme == "Human_Robot_Interaction"

    def test_perception_from_title(self):
        meta = _meta(title="Visuotactile Perception for Object Detection")
        clf  = classify_paper(meta, _CONFIG)
        assert clf.primary_theme == "Multimodal_Perception"

    def test_unclassified_with_no_keywords(self):
        meta = _meta(title="Abstract Philosophy and Theory of Knowledge")
        clf  = classify_paper(meta, _CONFIG)
        assert clf.primary_theme == "Unclassified"

    def test_title_hits_score_double(self):
        # "fabrication" in abstract only = 1 pt; "fabrication" in title = 2 pts
        meta_abstract = _meta(abstract="We propose a novel approach to fabrication of sensors.")
        meta_title    = _meta(title="Fabrication of Novel Sensors")
        clf_abstract  = classify_paper(meta_abstract, _CONFIG)
        clf_title     = classify_paper(meta_title,    _CONFIG)
        assert clf_title.theme_scores["Design_and_Fabrication"] > clf_abstract.theme_scores["Design_and_Fabrication"]

    def test_abstract_contributes_to_score(self):
        meta = _meta(
            title="A New Robotic System",
            abstract="We propose a tactile sensor design using gel-based elastomers.",
        )
        clf = classify_paper(meta, _CONFIG)
        assert clf.theme_scores["Design_and_Fabrication"] > 0

    def test_filename_contributes_to_score(self):
        meta = _meta(filename="2024-ICRA-Tactile-Sensor-Design.pdf")
        clf  = classify_paper(meta, _CONFIG)
        assert clf.theme_scores["Design_and_Fabrication"] > 0


# ---------------------------------------------------------------------------
# Secondary themes
# ---------------------------------------------------------------------------
class TestSecondaryThemes:
    def test_secondary_theme_present_when_overlap_high(self):
        meta = _meta(title="Tactile Sensor Design for Surgical Teleoperation")
        clf  = classify_paper(meta, _CONFIG)
        # Should have at least one secondary theme
        assert len(clf.secondary_themes) > 0

    def test_secondary_theme_not_same_as_primary(self):
        meta = _meta(title="Tactile Sensor Design for Surgical Teleoperation")
        clf  = classify_paper(meta, _CONFIG)
        assert clf.primary_theme not in clf.secondary_themes

    def test_low_overlap_no_secondary_theme(self):
        # Only strong signal for one theme
        meta = _meta(title="Deep Learning Imitation Learning Reinforcement Learning")
        clf  = classify_paper(meta, _CONFIG)
        # Primary should be Robot_Learning; check if no other theme has 45%+ of that score
        if clf.primary_theme == "Robot_Learning":
            for secondary in clf.secondary_themes:
                sec_score = clf.theme_scores[secondary]
                pri_score = clf.theme_scores["Robot_Learning"]
                assert sec_score >= pri_score * 0.45


# ---------------------------------------------------------------------------
# Application assignment
# ---------------------------------------------------------------------------
class TestApplicationAssignment:
    def test_surgical_application(self):
        meta = _meta(title="Minimally Invasive Surgical Robot Control")
        clf  = classify_paper(meta, _CONFIG)
        assert "Surgical_Robot" in clf.applications

    def test_tactile_sensing_application(self):
        meta = _meta(title="Visuotactile Gel Sensor for Robotic Touch")
        clf  = classify_paper(meta, _CONFIG)
        assert "Tactile_Sensing" in clf.applications

    def test_manipulation_application(self):
        meta = _meta(title="Dexterous Robotic Arm Manipulation with Gripper")
        clf  = classify_paper(meta, _CONFIG)
        assert "Robotic_Arm_Manipulation" in clf.applications

    def test_general_robotics_fallback(self):
        meta = _meta(title="Abstract Philosophy of Science")  # no robotics keywords
        clf  = classify_paper(meta, _CONFIG)
        assert "General_Robotics" in clf.applications

    def test_no_general_robotics_when_specific_app_matches(self):
        meta = _meta(title="Minimally Invasive Surgical Robot for Laparoscopic Procedures")
        clf  = classify_paper(meta, _CONFIG)
        assert "General_Robotics" not in clf.applications

    def test_multiple_applications_allowed(self):
        meta = _meta(title="Tactile Sensor for Minimally Invasive Surgical Robot Manipulation")
        clf  = classify_paper(meta, _CONFIG)
        assert len(clf.applications) >= 2


# ---------------------------------------------------------------------------
# Year bucket
# ---------------------------------------------------------------------------
class TestYearBucket:
    @pytest.mark.parametrize("year,expected", [
        (2017, "Pre-2018"),
        (2000, "Pre-2018"),
        (2018, "2018-2019"),
        (2019, "2018-2019"),
        (2020, "2020-2021"),
        (2021, "2020-2021"),
        (2022, "2022-2023"),
        (2023, "2022-2023"),
        (2024, "2024-2025"),
        (2025, "2024-2025"),
        (2026, "2026-2027"),
        (None, "Unknown"),
    ])
    def test_year_bucket(self, year, expected):
        assert _year_bucket(year) == expected


# ---------------------------------------------------------------------------
# Title keyword extraction
# ---------------------------------------------------------------------------
class TestTitleKeywords:
    def test_extracts_meaningful_words(self):
        kws = _extract_title_keywords("Tactile Sensor Design for Surgical Robots", n=3)
        assert "Tactile" in kws
        assert "Sensor" in kws

    def test_stopwords_excluded(self):
        kws = _extract_title_keywords("A Novel Deep Learning Based System for Robot", n=3)
        for kw in kws:
            assert kw.lower() not in {"a", "for", "the", "based", "novel"}

    def test_max_n_keywords(self):
        kws = _extract_title_keywords("Tactile Sensing Visuotactile Detection Perception", n=3)
        assert len(kws) <= 3

    def test_empty_title(self):
        assert _extract_title_keywords(None, n=3) == []
        assert _extract_title_keywords("", n=3) == []

    def test_capitalised(self):
        kws = _extract_title_keywords("tactile sensor design", n=3)
        for kw in kws:
            assert kw[0].isupper()

    def test_deduplication(self):
        kws = _extract_title_keywords("Tactile Tactile Sensing Sensing", n=5)
        assert len(kws) == len(set(kws))
