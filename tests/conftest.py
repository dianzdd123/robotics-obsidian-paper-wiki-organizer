"""
conftest.py — adds src/ to sys.path so tests run without pip install -e .
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
