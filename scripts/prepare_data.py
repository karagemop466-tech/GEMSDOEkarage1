#!/usr/bin/env python
"""
Validate real competition data placed in ./data/ against this repo's
cached grid spec (src/gems/grid.py). Run this immediately after
scripts/download_competition_data.sh.

If any assertion below fails, TRUST THE FILE, NOT THIS REPO: open an issue /
fix src/gems/grid.py to match the real sample_submission.tif, because the
cached GEMS_GRID constant was cross-replicated from third-party research
logs, not read directly from the organizer's file (see
docs/LIMITATIONS.md). This script is what finally closes that gap, the
moment real data is available.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rasterio

from gems.grid import GEMS_GRID

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
REQUIRED_FILES = [
    "training_features.tif",
    "labels.tif",
    "sample_submission.tif",
]


def main() -> int:
    missing = [f for f in REQUIRED_FILES if not (DATA_DIR / f).exists()]
    if missing:
        print(f"BLOCKED: missing files in {DATA_DIR}: {missing}")
        print("Run scripts/download_competition_data.sh first (see its header "
              "for the manual steps -- this sandbox cannot fetch them itself).")
        return 1

    ok = True
    for fname in ["sample_submission.tif", "labels.tif", "training_features.tif"]:
        path = DATA_DIR / fname
        with rasterio.open(path) as src:
            shape = (src.height, src.width)
            crs_ok = src.crs is not None and src.crs.to_epsg() == 32611
            transform = tuple(src.transform)[:6]
            transform_ok = all(
                abs(a - b) < 1e-3 for a, b in zip(transform, tuple(GEMS_GRID.transform)[:6])
            )
            shape_ok = shape == GEMS_GRID.shape
        status = "OK" if (crs_ok and transform_ok and shape_ok) else "MISMATCH"
        if status != "OK":
            ok = False
        print(
            f"{fname}: shape={shape} (expect {GEMS_GRID.shape}) "
            f"crs_epsg32611={crs_ok} transform_match={transform_ok} -> {status}"
        )

    if ok:
        print("\nAll files match the cached GEMS_GRID. Proceed to training.")
        return 0
    print(
        "\nBLOCKED: real data does not match src/gems/grid.py::GEMS_GRID. "
        "Update GEMS_GRID from these real files (they are ground truth) "
        "before generating any submission."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
