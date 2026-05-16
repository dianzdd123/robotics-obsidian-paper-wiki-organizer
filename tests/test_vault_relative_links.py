"""
test_vault_relative_links.py
Tests that Obsidian notes use vault-relative PDF links and never contain
absolute Windows or POSIX paths.
"""

import pytest
from pathlib import Path

from robotics_paper_wiki.metadata_extract import PaperMetadata
from robotics_paper_wiki.classify_paper import Classification
from robotics_paper_wiki.obsidian_notes import (
    generate_paper_note,
    generate_application_link_note,
    generate_year_link_note,
    generate_theme_link_note,
)
from robotics_paper_wiki.utils import vault_relative


# ---------------------------------------------------------------------------
# vault_relative helper
# ---------------------------------------------------------------------------
class TestVaultRelativeHelper:
    def test_strips_vault_root(self):
        vault = Path("C:/Obsidian-Website/Publications")
        pdf   = Path("C:/Obsidian-Website/Publications/01_Renamed_PDFs/Theme/2024/paper.pdf")
        result = vault_relative(pdf, vault)
        assert result == "01_Renamed_PDFs/Theme/2024/paper.pdf"

    def test_uses_forward_slashes(self):
        vault = Path("C:/Obsidian-Website/Publications")
        pdf   = Path("C:/Obsidian-Website/Publications/01_Renamed_PDFs/paper.pdf")
        result = vault_relative(pdf, vault)
        assert "\\" not in result

    def test_falls_back_gracefully_when_not_under_vault(self):
        vault  = Path("C:/Publications")
        pdf    = Path("D:/OtherDrive/paper.pdf")
        result = vault_relative(pdf, vault)
        assert result  # non-empty string, no exception

    def test_posix_paths(self):
        vault = Path("/home/user/Publications")
        pdf   = Path("/home/user/Publications/01_Renamed_PDFs/Theme/2024/paper.pdf")
        result = vault_relative(pdf, vault)
        assert result == "01_Renamed_PDFs/Theme/2024/paper.pdf"
        assert "\\" not in result


# ---------------------------------------------------------------------------
# Paper note — vault-relative PDF link
# ---------------------------------------------------------------------------
def _make_meta(year=2024, venue="ICRA", title="Test Paper", first_author="Zhang"):
    m = PaperMetadata(source_path="raw/test.pdf", filename="test.pdf", source_folder="raw")
    m.year         = year
    m.venue        = venue
    m.title        = title
    m.first_author = first_author
    m.authors      = [f"{first_author}, A"]
    return m


def _make_clf(theme="Robot_Learning", apps=None):
    c = Classification(primary_theme=theme)
    c.applications   = apps or ["General_Robotics"]
    c.secondary_themes = []
    c.title_keywords  = ["Test", "Paper"]
    c.year_bucket    = "2024-2025"
    return c


class TestPaperNoteLinks:
    def test_contains_vault_relative_pdf_link(self):
        meta = _make_meta()
        clf  = _make_clf()
        note = generate_paper_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf")
        assert "[[01_Renamed_PDFs_By_Research_Theme" in note

    def test_no_absolute_windows_path_in_pdf_link(self):
        meta = _make_meta()
        clf  = _make_clf()
        note = generate_paper_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf")
        pdf_link_lines = [l for l in note.split("\n") if "[[01_Renamed_PDFs" in l]
        for line in pdf_link_lines:
            assert "C:\\" not in line
            assert "C:/" not in line

    def test_no_absolute_posix_path_in_pdf_link(self):
        meta = _make_meta()
        clf  = _make_clf()
        note = generate_paper_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf")
        pdf_link_lines = [l for l in note.split("\n") if "[[01_Renamed_PDFs" in l]
        for line in pdf_link_lines:
            assert not line.strip().startswith("[[/home")
            assert not line.strip().startswith("[[/Users")

    def test_pdf_link_includes_theme_and_year(self):
        meta = _make_meta(year=2024)
        clf  = _make_clf(theme="Robot_Learning")
        note = generate_paper_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf")
        assert "Robot_Learning" in note
        assert "2024" in note

    def test_pdf_link_pipe_alias(self):
        meta = _make_meta()
        clf  = _make_clf()
        note = generate_paper_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf")
        assert "|Open PDF]]" in note

    def test_unknown_year_uses_unknown_folder(self):
        meta = _make_meta(year=None)
        clf  = _make_clf()
        note = generate_paper_note(meta, clf, "XXXX-ICRA-Test-Paper-Zhang.pdf")
        assert "Unknown_Year" in note


# ---------------------------------------------------------------------------
# Application link stub — relative path (not vault-relative)
# ---------------------------------------------------------------------------
class TestApplicationLinkNote:
    def test_relative_path_not_absolute(self):
        meta = _make_meta()
        clf  = _make_clf(apps=["Surgical_Robot"])
        stub = generate_application_link_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf", "Surgical_Robot")
        assert "C:\\" not in stub
        assert "C:/" not in stub

    def test_uses_three_dots_up(self):
        meta = _make_meta()
        clf  = _make_clf()
        stub = generate_application_link_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf", "General_Robotics")
        assert "../../../01_Renamed_PDFs_By_Research_Theme" in stub

    def test_contains_canonical_filename(self):
        meta = _make_meta()
        clf  = _make_clf()
        stub = generate_application_link_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf", "General_Robotics")
        assert "2024-ICRA-Test-Paper-Zhang.pdf" in stub


# ---------------------------------------------------------------------------
# Year link stub
# ---------------------------------------------------------------------------
class TestYearLinkNote:
    def test_uses_three_dots_up(self):
        meta = _make_meta()
        clf  = _make_clf()
        stub = generate_year_link_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf")
        assert "../../../01_Renamed_PDFs_By_Research_Theme" in stub

    def test_no_absolute_paths(self):
        meta = _make_meta()
        clf  = _make_clf()
        stub = generate_year_link_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf")
        assert "C:\\" not in stub
        assert "C:/" not in stub


# ---------------------------------------------------------------------------
# YAML frontmatter — no absolute paths
# ---------------------------------------------------------------------------
class TestFrontmatterSafety:
    def test_source_file_uses_original_filename_only(self):
        meta = _make_meta()
        clf  = _make_clf()
        note = generate_paper_note(meta, clf, "2024-ICRA-Test-Paper-Zhang.pdf")
        # source_file should just be the filename, not a full path
        fm_lines = note.split("---")[1].split("\n")
        source_lines = [l for l in fm_lines if "source_file" in l]
        for line in source_lines:
            assert "C:\\" not in line
