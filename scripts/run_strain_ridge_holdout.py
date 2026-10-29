#!/usr/bin/env python3
"""Experiment 3 (holdout only, no submission file): geodetic strain-rate ridge.

Hypothesis H1 (see knowledge/session-review-2026-10-29-thd-ridge.md): shear localisation in
the geodetic strain-rate second invariant (`geod_2ndinv`) marks active strike-slip/normal
structures. Same label-free ridge recipe, same 3-px catalogue collar (fold-visible only),
same shared gems57 hide-and-recover holdout. Pre-registered: one arm, percentile 98.0.
Not a submission; no slot; no uniqueness result is claimed from this script.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "vendor"))

from run_thd_ridge_candidate import (  # noqa: E402
    DATA, EVIDENCE, bootstrap_ci, holdout_score, pooled, ridge_candidates,
)
from gems57 import grid as G57  # noqa: E402

BAND = "geod_2ndinv"
PCT = 98.0


def main():
    with rasterio.open(DATA / "sample_submission.tif") as ds:
        footprint = np.isfinite(ds.read(1))
        crs = ds.crs
    with rasterio.open(DATA / "labels.tif") as ds:
        raw = ds.read(1)
    catalogue = np.isfinite(raw) & (raw > 0.5) & footprint
    with rasterio.open(DATA / "training_features.tif") as ds:
        names = [d.split(" - ")[0] for d in ds.descriptions]
        field = ds.read(names.index(BAND) + 1).astype(np.float32)
    valid = footprint & np.isfinite(field) & (field > -1e30)
    grid = G57.Grid(footprint=footprint, catalogue=catalogue, crs=crs,
                    transform=G57.TRANSFORM, height=G57.HEIGHT, width=G57.WIDTH)
    ctx, cells = holdout_score(grid, field, valid, PCT)
    prim = pooled(cells, "all")
    det = pooled(cells, "detached")
    lo, hi = bootstrap_ci(cells, "all")
    n_cands_full = int(ridge_candidates(field, valid, PCT).sum())
    result = dict(
        hypothesis="H1 geodetic strain-rate ridge (geod_2ndinv), label-free, 3x3 maxima, pct 98, 3-px visible collar",
        experiment="3 of 3 (holdout only)",
        evaluator="gems57-pooled-hide-v2 (gems57.holdout.build_holdout / score_cell)",
        holdout_all=prim, holdout_detached=det,
        ci95_all=[lo, hi],
        ridge_candidates_before_collar=n_cands_full,
        label="HOLDOUT-DTI",
        verdict="negative" if prim["dti"] <= 0.0318 else "inconclusive-review",
        comparison_note=("Reference 0.0318 is the BB-STEP HOLDOUT-DTI recorded in the repo under gemsk-hide-recover-v1 "
                         "(n=60,988). It used a different withheld-positive set, so the comparison is indicative only."),
        cells=cells,
    )
    out = EVIDENCE / "strain_ridge_holdout_20261029.json"
    out.write_text(json.dumps(result, indent=2, default=float) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "cells"}, indent=2, default=float))


if __name__ == "__main__":
    main()
