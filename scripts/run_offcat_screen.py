#!/usr/bin/env python3
"""Experiment 1 of the off-catalogue geophysics lane.

Leakage canary (protocol rule 4): score each of the 19 feature bands ALONE
against the withheld holdout truth.  AUC > 0.90 for any single feature means
leakage (that feature is essentially the truth proxy) until proven otherwise.

Then rank features by holdout AUC and by off-catalogue separation (mean feature
value at withheld truth pixels vs at pixels far from any catalogue fault).

Outputs docs/data/offcat_feature_screen.json.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "src"))

from gems57.grid import DATA_DIR, load_grid  # noqa: E402
from gems57.holdout import build_holdout  # noqa: E402

FEATURES = ROOT / "data" / "bridge" / "training_features.tif"
BAND_NAMES = [
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope", "tc",
    "geod_shearrate", "geod_dilaterate", "tmi_vg", "deq_n100a15",
    "iso_grav_anom_vg", "det_elev", "iso_grav_anom", "tmi",
    "depth_to_base_surf", "ieq_n100a15", "cond_surf", "iso_grav_anom_hg",
    "det_elev_slope",
]


def auc_at_pixels(values: np.ndarray, truth: np.ndarray, active: np.ndarray,
                  n_bg: int = 200000, seed: int = 7) -> float:
    """AUC of `values` for classifying truth vs background within `active`."""
    rng = np.random.default_rng(seed)
    y = truth.astype(np.int8)
    pos_idx = np.nonzero(y & active)
    bg_pool = np.nonzero(active & ~y)
    if pos_idx[0].size == 0 or bg_pool[0].size == 0:
        return float("nan")
    n_pos = pos_idx[0].size
    n_bg = min(n_bg, bg_pool[0].size)
    bg_sel = rng.choice(bg_pool[0].size, size=n_bg, replace=False)
    sel_y = np.concatenate([np.ones(n_pos), np.zeros(n_bg)])
    sel_v = np.concatenate([values[pos_idx], values[bg_pool[0][bg_sel], bg_pool[1][bg_sel]]])
    order = np.argsort(-sel_v, kind="stable")
    try:
        return float(roc_auc_score(sel_y[order], sel_v[order]))
    except ValueError:
        return float("nan")


def main() -> int:
    grid = load_grid(DATA_DIR)
    foot, cat = grid.footprint, grid.catalogue
    ctx = build_holdout(grid)

    with rasterio.open(FEATURES) as src:
        feats = src.read()  # (19, H, W) float32
    print("Feature stack:", feats.shape, "dtype", feats.dtype)

    rows = []
    for b, name in enumerate(BAND_NAMES):
        v = feats[b].astype(np.float64)
        finite = np.isfinite(v)
        v = np.where(finite, v, 0.0)
        aucs = []
        seps = []
        for cell in ctx.cells:
            sl = cell.bbox
            v_sub = v[sl]
            act = cell.active
            truth = np.zeros(act.shape, bool)
            truth[cell.truth_yx] = True
            a = auc_at_pixels(v_sub, truth, act)
            aucs.append(a)
            # separation: mean at truth vs mean at active background
            tvals = v_sub[truth]
            bg = act & ~truth
            bvals = v_sub[bg]
            if tvals.size and bvals.size:
                seps.append(float(np.nanmean(tvals) - np.nanmean(bvals)))
        aucs = [a for a in aucs if a == a]  # drop nan
        rows.append({
            "band": b + 1, "name": name,
            "holdout_auc_mean": round(float(np.mean(aucs)), 4) if aucs else None,
            "holdout_auc_min": round(float(np.min(aucs)), 4) if aucs else None,
            "holdout_auc_max": round(float(np.max(aucs)), 4) if aucs else None,
            "truth_minus_bg_mean": round(float(np.mean(seps)), 5) if seps else None,
            "leakage_flag_auc_gt_0_90": bool(any(a > 0.90 for a in aucs)),
        })
        print(f"b{b+1:2d} {name:26s} auc_mean={rows[-1]['holdout_auc_mean']} "
              f"min={rows[-1]['holdout_auc_min']} max={rows[-1]['holdout_auc_max']} "
              f"sep={rows[-1]['truth_minus_bg_mean']} "
              f"LEAKAGE={rows[-1]['leakage_flag_auc_gt_0_90']}")

    out = {
        "schema": "karage1-offcat-feature-screen-v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "n_cells": len(ctx.cells),
        "n_truth_total": sum(c.n_truth for c in ctx.cells),
        "bands": rows,
    }
    (ROOT / "docs" / "data").mkdir(parents=True, exist_ok=True)
    p = ROOT / "docs" / "data" / "offcat_feature_screen.json"
    p.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nWrote {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
