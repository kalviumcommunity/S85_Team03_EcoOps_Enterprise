"""
Project paths configuration.

Defines commonly used project directories and files.
"""

from pathlib import Path

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Documentation
DOCS_DIR = PROJECT_ROOT / "docs"

# Reports
PROFILING_REPORT = DOCS_DIR / "profiling-report.md"