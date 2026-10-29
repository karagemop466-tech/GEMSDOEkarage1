#!/usr/bin/env python3
"""Experiment 1 (session arena/5ee7ef4b): calibrate the SHARED holdout evaluator.

Uses only the vendored, unmodified template evaluator `vendor/gems57`
(`grid.load_grid`, `holdout.build_holdout`, `holdout.evaluate`). It does NOT use
`src/gemsk` or the lattice-gated experiment runners, which exit with BLOCKED.

Scores, on the same 8 hide-and-recover cells (2 draws x 4 quadrant folds,
mode "all"):
  * registry/GEMSDOE32_B2.tif   (the 0.2778 owner-reported champion raster)
  * registry/GEMSDOE25_d28.tif  (local registry raster; no receipt)
  * a random-dot null at the champion's dot count (3 seeds)

Labels: values are HOLDOUT-DTI (evaluator = gems57 holdout.evaluate, withheld
positives = sum of cell n_truth, 95% CI = percentile bootstrap over the 16
cells). The competition's withheld truth is NOT available, so these numbers
measure re-finding mapped USGS/INGENIOUS segments, not the organizer test set.

Usage: GEMS_DATA_DIR=/tmp/gems_data python scripts/exp1_shared_holdout_calibration.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import grid as G57  # noqa: E402
from gems57 import holdout as H57  # noqa: E402

DATA = Path(os.environ.get("GEMS_DATA_DIR", "/tmp/gems_data"))
OUT = ROOT / "evidence" / "exp1_shared_holdout_calibration_20261029.json"
RASTERS = {
    "champion_GEMSDOE32_B2": ROOT / "registry" / "GEMSDOE32_B2.tif",
    "GEMSDOE25_d28_local": ROOT / "registry" / "GEMSDOE25_d28.tif",
}


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_binary(p: Path, footprint: np.ndarray) -> tuple[np.ndarray, dict]:
    with rasterio.open(p) as ds:
        a = ds.read(1).astype(np.float64)
        info = dict(shape=list(ds.shape), crs=str(ds.crs), dtype=ds.dtypes[0], nodata=ds.nodata)
    finite = np.isfinite(a)
    info.update(nan_cells=int((~finite).sum()), min=float(np.nanmin(a)), max=float(np.nanmax(a)),
                unique_values=int(np.unique(a[finite]).size))
    # Dot rasters: any positive cell is an emitted dot (matches the evaluator's binary input).
    dots = (np.nan_to_num(a, nan=0.0) > 0) & footprint
    info["dots_in_footprint"] = int(dots.sum())
    return dots, info


def bootstrap_ci(values: np.ndarray, n: int = 2000, seed: int = 1) -> tuple[float, float]:
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, values.size, size=(n, values.size))
    stats = values[idx].mean(axis=1)
    return float(np.percentile(stats, 2.5)), float(np.percentile(stats, 97.5))


def score(dots: np.ndarray, ctx) -> dict:
    r = H57.evaluate(dots, ctx)
    cells = list(r["per_fold_dti"].values())
    lo, hi = bootstrap_ci(np.array(cells))  # bootstrap over the 16 cells
    return dict(pooled_dti=r["pooled_dti"], mean_fold_dti=r["mean_fold_dti"],
                per_cell_dti=r["per_fold_dti"], ci95_cell_bootstrap=[lo, hi],
                withheld_positives=r["pooled_n_truth"], emitted_pixels=r["emitted_pixels"],
                on_visible_catalogue=r["on_visible_catalogue"])


def main() -> None:
    grid = G57.load_grid(DATA)
    ctx = H57.build_holdout(grid)
    foot = grid.footprint
    receipt = dict(
        schema="karage1-exp1-shared-holdout-v1", session="arena/5ee7ef4b-gemsdoekarage1",
        date_utc="2026-10-29", evaluator="vendor/gems57 holdout.evaluate (unmodified)",
        evaluator_label=f"HOLDOUT-DTI gems57 alpha=0.2 beta=0.8 R=3px; cells={len(ctx.cells)} (2 draws x 4 folds x 2 modes)",
        data_dir=str(DATA), data_status="pinned third-party mirrors; organizer authenticity NOT established",
        cells=[dict(key=c.key, n_truth=c.n_truth) for c in ctx.cells],
        arms={},
    )
    results = {}
    for name, path in RASTERS.items():
        dots, info = load_binary(path, foot)
        s = score(dots, ctx)
        s.update(info)
        s["sha256"] = sha256(path)
        s["path"] = str(path.relative_to(ROOT))
        results[name] = s
        print(f"{name}: DTI={s['pooled_dti']:.4f} CI95={s['ci95_cell_bootstrap']} dots={info['dots_in_footprint']}", flush=True)

    n = results["champion_GEMSDOE32_B2"]["dots_in_footprint"]
    rng_scores = []
    foot_idx = np.flatnonzero(foot.ravel())
    for seed in (101, 202, 303):
        rng = np.random.default_rng(seed)
        pick = rng.choice(foot_idx, size=n, replace=False)
        dots = np.zeros(foot.size, bool)
        dots[pick] = True
        s = score(dots.reshape(foot.shape), ctx)
        rng_scores.append(s["pooled_dti"])
        print(f"random_null seed={seed}: DTI={s['pooled_dti']:.4f}", flush=True)
    results["random_null_matched_count"] = dict(
        dots=n, seeds=[101, 202, 303], pooled_dti_per_seed=rng_scores,
        mean=float(np.mean(rng_scores)), note="floor of this evaluator for a matched-count random placement")

    receipt["arms"] = results
    receipt["leaderboard_note"] = ("Internal holdout DTI is NOT the organizer score. Owner-reported 0.2778 "
                                   "(GEMSDOE32) is USER-REPORTED / UNVERIFIED and is not reproduced here.")
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True, default=float) + "\n")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
