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
NAME = "karage1-probcollar-gbm-K37654-collar3-20261029"  # twins: -nan.tif (primary), -zeros.tif
NOTE = "GBM top-37654 pixels, 3px catalogue collar, 19 organiser bands; research candidate, not cleared"
OUT_DIR = ROOT / "docs" / "candidates"


def main() -> int:
    import hashlib
    import json
    import rasterio
    from gems57.grid import EPSG, HEIGHT, WIDTH, TRANSFORM
    from gems57 import gates

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

    # Twin 1: zeros outside. Shared writer = the repo's all-finite export policy (validator of record).
    receipt = write_submission(
        OUT_DIR / f"{NAME}-zeros.tif", pred, DATA_DIR / "sample_submission.tif", fp,
        note=NOTE, name=NAME, catalogue=grid.catalogue,
        metadata=dict(recipe="model_K37654_r3", collar_px=COLLAR_PX, K=k, features="19 organiser bands",
                      training="all mapped catalogue pixels", outside="zeros",
                      status="research candidate; NOT CLEARED"),
    )

    # Twin 2: NaN outside (the official format; the user-required encoding). The shared writer
    # refuses NaN by design, so this twin is written here with the SAME grid profile and values, then
    # re-read and checked. The shared gate is run and its refusal reasons are recorded, not hidden.
    zeros_path = OUT_DIR / f"{NAME}-zeros.tif"
    with rasterio.open(zeros_path) as src:
        arr = src.read(1)
        prof = src.profile.copy()
    assert np.array_equal(arr[fp], pred[fp]) and int(((arr > 0) & ~fp).sum()) == 0
    nan_arr = np.where(fp, arr, np.float32(np.nan)).astype(np.float32)
    prof.update(nodata=np.nan)
    nan_path = OUT_DIR / f"{NAME}-nan.tif"
    with rasterio.open(nan_path, "w", **prof) as dst:
        dst.write(nan_arr, 1)
    with rasterio.open(nan_path) as src:
        back = src.read(1)
        assert src.count == 1 and src.dtypes[0] == "float32"
        assert src.crs.to_epsg() == EPSG and (src.height, src.width) == (HEIGHT, WIDTH)
        assert tuple(src.transform)[:6] == tuple(TRANSFORM)[:6]
    assert np.isnan(back[~fp]).all() and np.isfinite(back[fp]).all()
    assert np.array_equal(back[fp] > 0, pred[fp] > 0)
    shared = gates.format_report(nan_path, DATA_DIR / "sample_submission.tif", footprint=fp)
    refusal = [pr for pr in shared.get("problems", [])]
    expected_refusals = (
        any("all-finite export policy" in pr for pr in refusal)
        and all(("all-finite export policy" in pr) or ("nodata tag outside all-finite" in pr) for pr in refusal)
    )
    assert expected_refusals, refusal
    nan_receipt = dict(
        schema="karage1-candidate-nan-twin-v1", name=NAME, file=(str(nan_path.relative_to(ROOT)) if nan_path.is_relative_to(ROOT) else str(nan_path)),
        sha256=hashlib.sha256(nan_path.read_bytes()).hexdigest(),
        bytes=nan_path.stat().st_size, note=NOTE, note_chars=len(NOTE),
        encoding="NaN outside footprint (official format); values in [0,1] inside",
        outside_nan_cells=int(np.isnan(back[~fp]).sum()), inside_finite=bool(np.isfinite(back[fp]).all()),
        dots=int((back[fp] > 0).sum()), same_dots_as_zeros_twin=True,
        shared_gate_refusals=refusal,
        shared_gate_note="gems57.gates.format_report refuses NaN outside by its local all-finite export policy; the official spec permits NaN outside. Conflict recorded, not waived.",
        approved_for_weekly_slot=False, promoted=False, submission_slots_used=0,
        status="research-only; NOT CLEARED; DO NOT SUBMIT",
    )
    (OUT_DIR / f"{NAME}-nan.json").write_text(json.dumps(nan_receipt, indent=2, allow_nan=False) + "\n")
    print({k_: receipt[k_] for k_ in ("file", "sha256", "bytes", "note_chars")})
    print({k_: nan_receipt[k_] for k_ in ("file", "sha256", "bytes", "outside_nan_cells", "dots")})
    print(f"dots={int(sel.sum())} collar_px={COLLAR_PX} shared_gate_refusals={len(refusal)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
