"""Regression coverage for PDF discovery and conflicting execution flags."""
import subprocess
import sys
import pytest
from robotics_paper_wiki.organise_papers import scan_pdfs


def test_scan_accepts_mixed_case_pdf_suffixes(tmp_path):
    for name in ('paper.pdf', 'PAPER.PDF', 'mixed.PdF', 'notes.txt'):
        (tmp_path / name).touch()
    (tmp_path / 'folder.pdf').mkdir()
    assert [path.name for path in scan_pdfs(str(tmp_path))] == ['PAPER.PDF', 'mixed.PdF', 'paper.pdf']


def test_missing_source_is_not_reported_as_empty_library(tmp_path):
    with pytest.raises(NotADirectoryError, match='source directory'):
        scan_pdfs(str(tmp_path / 'missing'))


def test_conflicting_run_flags_fail_before_config_or_file_access(tmp_path):
    result = subprocess.run(
        [sys.executable, '-m', 'robotics_paper_wiki.organise_papers', '--dry-run', '--run'],
        cwd=tmp_path, text=True, capture_output=True)
    assert result.returncode == 2
    assert 'not allowed with argument' in result.stderr
    assert not list(tmp_path.iterdir())
