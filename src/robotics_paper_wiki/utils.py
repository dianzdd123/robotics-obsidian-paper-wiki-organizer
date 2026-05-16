"""
utils.py — Shared utilities for the robotics paper wiki organiser.
"""

from __future__ import annotations

import re
import shutil
import unicodedata
from pathlib import Path
from typing import Optional


def clean_text(text: str) -> str:
    """Normalise unicode and collapse whitespace."""
    text = unicodedata.normalize("NFKC", text)
    return re.sub(r"\s+", " ", text).strip()


def safe_component(text: str, max_len: int = 35) -> str:
    """Make *text* safe for use as a filename component."""
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    return text[:max_len].strip("-")


def vault_relative(path: Path, vault_root: Path) -> str:
    """Return *path* relative to *vault_root* with forward slashes.

    Falls back to the absolute path string if *path* is not under *vault_root*.
    """
    try:
        return str(path.relative_to(vault_root)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


def write_text_file(path: Path, content: str, overwrite: bool = True) -> str:
    """Write *content* to *path*.

    Returns:
        "WRITTEN"        — file was written successfully
        "SKIPPED_EXISTS" — file already existed and overwrite=False
    """
    if not overwrite and path.exists():
        return "SKIPPED_EXISTS"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return "WRITTEN"


def copy_pdf(src: Path, dst: Path, dry_run: bool, overwrite: bool = False) -> str:
    """Copy *src* PDF to *dst*.

    Returns:
        "DRY_RUN"        — dry_run=True, nothing was done
        "COPIED"         — file was copied successfully
        "SKIPPED_EXISTS" — dst already existed and overwrite=False
    """
    if dry_run:
        return "DRY_RUN"
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not overwrite:
        return "SKIPPED_EXISTS"
    shutil.copy2(str(src), str(dst))
    return "COPIED"


def year_folder(year: Optional[int]) -> str:
    """Return '2024' or 'Unknown_Year'."""
    return str(year) if year else "Unknown_Year"
