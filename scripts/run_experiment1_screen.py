#!/usr/bin/env python3
"""Experiment 1 - field screen on the hide-and-recover holdout (pooled DTI, 4 folds).

Arms (all emitted with the same rule: Poisson spacing 2.8 px, apron 2 px from VISIBLE faults):
  step            : multi-scale step-edge (NMS) of det_elev
  step_x_concord  : step * concordance gate
  curvbreak       : |profile curvature| thinned
  lidar_step      : 1 m LiDAR step_max thinned
  gpc_fused       : rank-fused step + curvbreak + lidar_step, gated by concordance
Control: the GEMSDOE32 champion raster (0.2778 OWNER-REPORT) scored on this evaluator with the
same fold masks, plus the H19-5 source field re-emitted with our rule at the same budget.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsk import emission, features, grid, holdout  # noqa: E402

BUDGETS = [int(b) for b in (sys.argv[1].split(",") if len(sys.argv) > 1 else ["37654"])]
REG = grid.DATA / "registry"


def load_raster(p: Path) -> np.ndarray:
    with rasterio.open(p) as src:
        a = src.read(1)
    return np.nan_to_num(a, nan=0.0) > 0.5


def main() -> None:
    from gemskarage1.guard import stop_inherited_driver
    stop_inherited_driver()
    t0 = time.time()
    foot = grid.footprint()
    cat = grid.catalogue()
    S = features.build_all()
    folds = holdout.make_folds(cat, foot)
    rk = {k: emission.rank_normalise(v, foot) for k, v in S.items()}
    gate = 0.25 + 0.75 * S["concord"]                     # soft gate: range-facing scarps keep 25%
    fields = {
        "step": S["step"],
        "step_x_concord": S["step"] * gate,
        "curvbreak": S["curvbreak"],
        "lidar_step": S["lidar_step"],
        "gpc_fused": (0.45 * rk["step"] + 0.25 * rk["curvbreak"] + 0.30 * rk["lidar_step"]) * gate,
    }
    thin_flag = {"step": False, "step_x_concord": False, "curvbreak": True, "lidar_step": True, "gpc_fused": True}
    champion = load_raster(REG / "GEMSDOE32_h33-h33-2-b2_e5eb6e7e_zeros.tif")
    h195 = None
    p = REG / "GEMS19_h19-5-powerlaw-budget-multiline-corroborated_nan.tif"
    if p.exists():
        with rasterio.open(p) as src:
            h195 = np.nan_to_num(src.read(1), nan=0.0).astype(np.float32)
    results = {"evaluator": holdout.VERSION, "evaluator_hash": holdout.implementation_hash(), "budgets": BUDGETS,
               "folds": [{k: f[k] for k in ("fold", "n_withheld", "n_visible", "n_segments_withheld")} for f in folds], "arms": {}}
    terms_by_arm = {}
    # control arm: champion raster as-is (its dots were pruned around the FULL catalogue, which is a
    # mild advantage in this holdout: it never emits near withheld segments either)
    terms = []
    per_fold = []
    for f in folds:
        r, t = holdout.evaluate_dots(champion, f)
        terms.append(t); per_fold.append(r["dti"])
    pooled = holdout.pooled(terms)
    results["arms"]["control_champion_02778_asis"] = {"pooled": pooled, "per_fold_dti": per_fold, "n_dots": int(champion.sum())}
    terms_by_arm["control_champion_02778_asis"] = terms
    print(f"control champion as-is  pooled DTI {pooled['dti']:.5f}  per-fold {np.round(per_fold, 4)}", flush=True)
    for budget in BUDGETS:
        arms = dict(fields)
        if h195 is not None:
            arms["control_h195_field_reemitted"] = h195
        for name, fld in arms.items():
            thin = thin_flag.get(name, True)
            terms = []; per_fold = []; ndots = []
            for f in folds:
                dots = emission.emit(fld, budget, f["visible"], spacing=2.8, apron_px=2, thin=thin)
                r, t = holdout.evaluate_dots(dots, f)
                terms.append(t); per_fold.append(r["dti"]); ndots.append(int(dots.sum()))
            pooled = holdout.pooled(terms)
            key = f"{name}@{budget}"
            results["arms"][key] = {"pooled": pooled, "per_fold_dti": per_fold, "n_dots_per_fold": ndots, "thin": thin}
            terms_by_arm[key] = terms
            print(f"{key:40s} pooled DTI {pooled['dti']:.5f}  per-fold {np.round(per_fold, 4)}  dots {ndots[0]}  [{time.time()-t0:.0f}s]", flush=True)
    results["bootstrap"] = holdout.bootstrap_ci(terms_by_arm)
    out = ROOT / "evidence" / "exp1_field_screen.json"
    out.write_text(json.dumps(results, indent=1) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
