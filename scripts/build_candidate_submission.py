#!/usr/bin/env python3
"""Build the 2026-10-29 research candidate GeoTIFF through the SHARED writer.

Recipe (the best OWN-model arm in the holdout, `model_K37654_r3`):
  1. Model: HistGradientBoosting on the 19 organiser feature bands, trained on ALL
     mapped catalogue pixels (positives) vs footprint pixels > 5 px from the catalogue
     (negatives). Same code path as the holdout (`run_probcollar_holdout.fit_probability`).
  2. Collar: exclude footprint pixels within 3 px (<= 300 m) of the mapped catalogue.
  3. Emission: top-37,654 footprint pixels by model probability -> binary 1.0.
  4. Write with `vendor/gems57/submission_writer.write_submission` (format, range,
     footprint and no-positive-on-catalogue checks; name/note <= 140 chars).

This writes a FILE ONLY. It does not decide clearance. Clearance requires the
uniqueness gate, a holdout win over the controls, and a separate selector step
(see evidence/run_card_probcollar_20261029.json).
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src", "scripts"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57.grid import DATA_DIR, load_grid  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402

from run_probcollar_holdout import fit_probability, load_feature_stack  # noqa: E402

K = 37654
COLLAR_PX = 3
NAME = "karage1-probcollar-gbm-K37654-collar3-20261029"
NOTE = "GBM top-37654 pixels, 3px catalogue collar, 19 organiser bands; research candidate, not cleared"
OUT_DIR = ROOT / "docs" / "candidates"


def main() -> int:
    grid = load_grid(DATA_DIR)
    fp = grid.footprint
    X, _names = load_feature_stack(grid)
    p_fp = fit_probability(X, grid, grid.catalogue)                     # all visible = full catalogue
    dist_fp = ndi.distance_transform_edt(~grid.catalogue)[fp]
    ok = dist_fp > COLLAR_PX
    score = np.where(ok, p_fp, -np.inf)
    k = min(K, int(ok.sum()))
    sel = np.zeros(score.shape, bool)
    sel[np.argpartition(-score, k - 1)[:k]] = True
    pred = np.zeros(grid.shape, np.float32)
    pred[fp] = sel.astype(np.float32)
    receipt = write_submission(
        OUT_DIR / f"{NAME}.tif", pred, DATA_DIR / "sample_submission.tif", fp,
        note=NOTE, name=NAME, catalogue=grid.catalogue,
        metadata=dict(recipe="model_K37654_r3", collar_px=COLLAR_PX, K=k, features="19 organiser bands",
                      training="all mapped catalogue pixels", status="research candidate; NOT CLEARED"),
    )
    print({k_: receipt[k_] for k_ in receipt if k_ in ("file", "sha256", "bytes", "note_chars")})
    print(f"dots={int(sel.sum())} collar_px={COLLAR_PX}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
