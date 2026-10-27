#!/usr/bin/env python3
"""Protocol Rule 2 canonical wrapper around `vendor/gems57/submission_writer.py`."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57.submission_writer import write_submission  # noqa: F401,E402

__all__ = ["write_submission"]
