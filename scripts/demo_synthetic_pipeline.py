#!/usr/bin/env python
"""
SYNTHETIC / DEMO ONLY -- proves the train -> predict -> score -> validate
pipeline is wired correctly end-to-end, using fabricated data on a small
toy grid. This is NOT the competition grid, NOT real geophysics, and its
output must never be uploaded to DrivenData.

Why this exists: this sandbox cannot reach drivendata.org's authenticated
data tab or the Dropbox mirror listed in docs/PROJECT_BRIEF.md (see
docs/LIMITATIONS.md for the line-by-line connectivity test), so no real
training_features.tif / labels.tif is available to us here. Rather than
fabricate fake "real" results on the competition grid (which would be
scientific hallucination), we demonstrate correctness on an explicitly
synthetic toy problem where we KNOW the ground truth and can sanity-check
that the metric and validator behave exactly as specified.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
from scipy.ndimage import sobel

from gems.metric import distance_weighted_tversky_index
from gems.submission_writer import write_submission
from gems.validator import validate_submission
from gems.grid import GemsGrid
from rasterio.crs import CRS
from rasterio.transform import Affine

OUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "synthetic_demo"


def make_synthetic_scene(h=200, w=200, seed=0):
    rng = np.random.default_rng(seed)
    # Synthetic "ground truth fault": a diagonal line with a step offset,
    # mimicking a strike-slip fault trace.
    gt = np.zeros((h, w), dtype=bool)
    for x in range(w):
        y = int(0.4 * x) + 40
        if x > 120:
            y += 15  # step-over
        if 0 <= y < h:
            gt[y, x] = True

    # Synthetic "elevation" with a scarp aligned to the fault plus noise.
    elevation = np.zeros((h, w), dtype=np.float32)
    for x in range(w):
        y = int(0.4 * x) + 40
        if x > 120:
            y += 15
        elevation[max(0, y - 30):y, x] -= 2.0  # downthrown block
    elevation += rng.normal(0, 0.3, size=(h, w)).astype(np.float32)

    # A second, uninformative "nuisance" channel (e.g. stands in for a
    # non-fault process like a stream channel) to show the pipeline isn't
    # trivially cheating off ground truth.
    nuisance = rng.normal(0, 1, size=(h, w)).astype(np.float32)

    return gt, elevation, nuisance


def heuristic_predict(elevation: np.ndarray) -> np.ndarray:
    """A toy, fully-explainable 'model': normalized gradient magnitude of
    elevation (a scarp/edge detector), squashed to [0, 1]."""
    gy = sobel(elevation, axis=0)
    gx = sobel(elevation, axis=1)
    grad = np.hypot(gy, gx)
    grad = (grad - grad.min()) / (grad.max() - grad.min() + 1e-9)
    return grad.astype(np.float32)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    gt, elevation, nuisance = make_synthetic_scene()
    pred = heuristic_predict(elevation)

    result = distance_weighted_tversky_index(pred, gt, pixel_size_m=100.0)
    print("SYNTHETIC DEMO (toy 200x200 grid, not the real competition grid)")
    print(f"  TPw={result.tp_w:.4f} FPw={result.fp_w:.4f} FNw={result.fn_w:.4f}")
    print(f"  Synthetic-demo DTI = {result.dti:.4f}  (NOT a competition score)")

    # Leakage canary demo: score the *nuisance* channel the same way; it
    # should score near the "no signal" floor, unlike the real edge detector.
    nuisance_pred = heuristic_predict(nuisance)
    nuisance_result = distance_weighted_tversky_index(nuisance_pred, gt, pixel_size_m=100.0)
    print(f"  Nuisance-channel DTI = {nuisance_result.dti:.4f} (expect << real-signal DTI)")
    assert nuisance_result.dti < result.dti, "canary failed: nuisance channel scored as well as signal"

    toy_grid = GemsGrid(
        height=200,
        width=200,
        transform=Affine(100.0, 0.0, 0.0, 0.0, -100.0, 0.0),
        crs=CRS.from_epsg(32611),
    )
    tif_path = OUT_DIR / "synthetic_demo_prediction.tif"
    write_submission(tif_path, pred, grid=toy_grid)
    report = validate_submission(tif_path, expected_grid=toy_grid)
    print(f"  Validator all_checks_passed = {report.all_checks_passed}")
    assert report.all_checks_passed, report.checks
    print(f"  Wrote {tif_path} (sha256={report.sha256}) -- SYNTHETIC, DO NOT SUBMIT")


if __name__ == "__main__":
    main()
