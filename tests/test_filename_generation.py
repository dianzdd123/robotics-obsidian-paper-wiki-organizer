"""
test_filename_generation.py
Tests for canonical PDF filename generation.
"""

import pytest
from robotics_paper_wiki.metadata_extract import PaperMetadata
from robotics_paper_wiki.classify_paper import Classification, proposed_filename


def _meta(year=None, venue=None, first_author=None, title=None):
    m = PaperMetadata(source_path="test.pdf", filename="test.pdf", source_folder="folder")
    m.year         = year
    m.venue        = venue
    m.first_author = first_author
    m.title        = title
    return m


def _clf(theme="Robot_Learning", keywords=None):
    c = Classification(primary_theme=theme)
    c.title_keywords = keywords or []
    return c


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------
class TestFilenameFormat:
    def test_full_fields(self):
        meta = _meta(year=2024, venue="ICRA", first_author="Zhang")
        clf  = _clf(keywords=["Tactile", "Sensing", "Deep"])
        name = proposed_filename(meta, clf)
        assert name == "2024-ICRA-Tactile-Sensing-Deep-Zhang.pdf"

    def test_ends_with_pdf(self):
        assert proposed_filename(_meta(), _clf()).endswith(".pdf")

    def test_no_spaces(self):
        meta = _meta(year=2024, venue="RAL", first_author="Smith")
        clf  = _clf(keywords=["Force", "Control"])
        assert " " not in proposed_filename(meta, clf)

    def test_hyphen_separated(self):
        meta = _meta(year=2024, venue="ICRA", first_author="Li")
        clf  = _clf(keywords=["A", "B", "C"])
        name = proposed_filename(meta, clf)
        parts = name.replace(".pdf", "").split("-")
        assert len(parts) >= 4


# ---------------------------------------------------------------------------
# Missing fields
# ---------------------------------------------------------------------------
class TestFilenameWithMissingFields:
    def test_missing_year_uses_placeholder(self):
        meta = _meta(venue="ICRA", first_author="Zhang")
        clf  = _clf(keywords=["Test"])
        name = proposed_filename(meta, clf)
        assert name.startswith("XXXX-")

    def test_missing_venue_uses_placeholder(self):
        meta = _meta(year=2024, first_author="Zhang")
        clf  = _clf(keywords=["Test"])
        name = proposed_filename(meta, clf)
        assert "Unknown-Venue" in name

    def test_missing_author_uses_placeholder(self):
        meta = _meta(year=2024, venue="ICRA")
        clf  = _clf(keywords=["Test"])
        name = proposed_filename(meta, clf)
        assert name.endswith("Unknown.pdf")

    def test_all_missing_returns_safe_string(self):
        meta = _meta()
        clf  = _clf()
        name = proposed_filename(meta, clf)
        assert name.endswith(".pdf")
        assert "/" not in name
        assert "\\" not in name


# ---------------------------------------------------------------------------
# Sanitisation
# ---------------------------------------------------------------------------
class TestFilenameSanitisation:
    def test_special_chars_removed(self):
        meta = _meta(year=2024, venue="ICRA", first_author="O'Brien")
        clf  = _clf(keywords=["Test"])
        name = proposed_filename(meta, clf)
        assert "'" not in name

    def test_spaces_replaced(self):
        meta = _meta(year=2024, venue="ICRA", first_author="Van Den Berg")
        clf  = _clf(keywords=["Test"])
        name = proposed_filename(meta, clf)
        assert " " not in name

    def test_max_component_length(self):
        meta = _meta(
            year=2024, venue="ICRA",
            first_author="A" * 50,  # very long name
        )
        clf  = _clf(keywords=["Test"])
        name = proposed_filename(meta, clf)
        for part in name.replace(".pdf", "").split("-"):
            assert len(part) <= 35, f"Component too long: {part!r}"

    def test_no_double_hyphens(self):
        meta = _meta(year=2024, venue="ICRA", first_author="Zhang")
        clf  = _clf(keywords=["Tactile"])
        name = proposed_filename(meta, clf)
        assert "--" not in name


# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------
class TestFilenameKeywords:
    def test_up_to_three_keywords(self):
        meta = _meta(year=2024, venue="ICRA", first_author="Zhang")
        clf  = _clf(keywords=["Tactile", "Sensing", "Deep", "Extra", "More"])
        name = proposed_filename(meta, clf)
        # YEAR-VENUE-Kw1-Kw2-Kw3-Author — only first 3 keywords
        parts = name.replace(".pdf", "").split("-")
        # parts[0]=year, parts[1]=venue, parts[-1]=author, middle=keywords
        keywords_in_name = parts[2:-1]
        assert len(keywords_in_name) == 3

    def test_fewer_than_three_keywords_ok(self):
        meta = _meta(year=2024, venue="ICRA", first_author="Zhang")
        clf  = _clf(keywords=["Tactile"])
        name = proposed_filename(meta, clf)
        assert name.endswith(".pdf")
        assert "/" not in name

    def test_empty_keywords_uses_fallback(self):
        meta = _meta(year=2024, venue="ICRA", first_author="Zhang")
        clf  = _clf(keywords=[])
        name = proposed_filename(meta, clf)
        assert "Paper" in name  # default fallback keyword
