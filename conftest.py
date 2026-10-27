from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
for rel in ("", "src", "vendor"):
    cand = str(ROOT / rel) if rel else str(ROOT)
    if cand not in sys.path:
        sys.path.insert(0, cand)
