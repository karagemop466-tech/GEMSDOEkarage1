#!/usr/bin/env python3
"""Compatibility entry point for the canonical fail-closed site renderer.

The former parallel-session builder displayed Conduitcrest as unique without
checking the registered lattice. Its saved bytes are independently audited in
``evidence/conduitcrest_lattice_reaudit_20261028.json`` and exceed the literal
3-pixel overlap gate. Keep a single renderer as the authority so alternate
entry points cannot restore stale approval or omit the current negative decision.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.render_site import main  # noqa: E402


if __name__ == "__main__":
    main()
