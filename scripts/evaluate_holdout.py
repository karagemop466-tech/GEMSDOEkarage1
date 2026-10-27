#!/usr/bin/env python3
"""Protocol Rule 2 canonical wrapper around `vendor/gems57/evaluate_holdout.py`."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57.evaluate_holdout import (  # noqa: F401,E402
    VERSION,
    evaluate,
    from_terms,
    implementation_hashes,
    pooled_summary,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hashes", action="store_true", help="Print shared evaluator SHA-256 provenance hashes")
    args = ap.parse_args()
    if args.hashes:
        print(json.dumps({"evaluator_version": VERSION, "implementation_sha256": implementation_hashes()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
