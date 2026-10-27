#!/usr/bin/env python
"""CLI wrapper: validate any candidate submission GeoTIFF.

Usage:
    python scripts/validate_submission.py path/to/candidate.tif [--allow-nan]

Exits non-zero (and the JSON report prints `"all_checks_passed": false`) if
the file would fail the official format rules. Run this before every
DrivenData upload.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from gems.validator import main  # noqa: E402

if __name__ == "__main__":
    main()
