#!/usr/bin/env python3
"""Compatibility entrypoint for dashboard generation."""

from pathlib import Path
import runpy


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    runpy.run_path(str(repo_root / "china_semiconductor_report.py"), run_name="__main__")
