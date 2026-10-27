"""Add ``vendor/`` and ``src/`` to ``sys.path`` so tests run cleanly without editable install."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
for sub in ("vendor", "src"):
    p = str(ROOT / sub)
    if p not in sys.path:
        sys.path.insert(0, p)
