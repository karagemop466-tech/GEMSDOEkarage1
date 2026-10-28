#!/usr/bin/env python3
"""Experiment 2 - GPC-Z on both holdout schemes (pre-registered in docs/research/preregistration-gpcz-20261027.md).

Arms at each budget (same emission everywhere: Poisson 2.8 px, apron 2 px from VISIBLE faults):
  physics            : gpc_fused (rank-fused step/curvbreak/lidar_step x concordance gate)  [Exp-1 best label-free]
  prior_only         : g(d) x 1e-3*rank(lidar_step) tiebreaker (is the physics doing anything?)
  gpcz               : physics x g(d)              <- the lane
  gpcz_sqrt          : physics x sqrt(g(d))        (sensitivity of the coupling strength)
  control_h195       : H19-5 source field re-emitted (catalogue-trained in its own repo: leaky control)
g(d) for fold k is estimated from the other three folds only.
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
from gemsk import emission, features, grid, holdout, prior  # noqa: E402

BUDGETS = [int(b) for b in (sys.argv[1].split(",") if len(sys.argv) > 1 else ["30000", "37654", "44090"])]
SCHEMES = sys.argv[2].split(",") if len(sys.argv) > 2 else ["interleaved", "blocked"]
REG = grid.DATA / "registry"


def main() -> None:
    from gemskarage1.guard import stop_inherited_driver
    stop_inherited_driver()
    t0 = time.time()
    foot = grid.footprint()
    cat = grid.catalogue()
    S = features.build_all()
    rk = {k: emission.rank_normalise(v, foot) for k, v in S.items()}
    gate = 0.25 + 0.75 * S["concord"]
    physics = emission.nms_thin((0.45 * rk["step"] + 0.25 * rk["curvbreak"] + 0.30 * rk["lidar_step"]) * gate)
    physics[~foot] = 0
    with rasterio.open(REG / "GEMS19_h19-5-powerlaw-budget-multiline-corroborated_nan.tif") as src:
        h195 = np.nan_to_num(src.read(1), nan=0.0).astype(np.float32)
    results = {"evaluator": holdout.VERSION, "evaluator_hash": holdout.implementation_hash(), "budgets": BUDGETS, "schemes": {}}
    for scheme in SCHEMES:
        folds = holdout.make_folds(cat, foot, scheme=scheme)
        tables = [prior.fold_table(f) for f in folds]
        # leave-one-fold-out prior per fold + canary AUC of the prior alone
        g_maps, g_dens, canary = [], [], []
        for i, f in enumerate(folds):
            dens = prior.density_from_tables([t for j, t in enumerate(tables) if j != i])
            g_dens.append(dens.tolist())
            gm = prior.apply(dens, f["visible"])
            g_maps.append(gm)
            canary.append(holdout.auc_on_fold(gm, f))
        sch = {"folds": [{k: f[k] for k in ("fold", "n_withheld", "n_visible", "n_segments_withheld")} for f in folds],
               "prior_density_loo": g_dens, "prior_only_auc_canary": canary, "arms": {}}
        print(f"[{scheme}] prior-only AUC canary per fold: {np.round(canary, 3)}", flush=True)
        terms_by_arm = {}
        for budget in BUDGETS:
            arms = {
                "physics": lambda i: physics,
                "prior_only": lambda i: g_maps[i] * (1e-3 + rk["lidar_step"] * 1e-3) * foot,
                "gpcz": lambda i: physics * g_maps[i],
                "gpcz_sqrt": lambda i: physics * np.sqrt(g_maps[i]),
                "control_h195": lambda i: h195,
            }
            for name, fn in arms.items():
                terms, per_fold, ndots = [], [], []
                for i, f in enumerate(folds):
                    fld = fn(i)
                    dots = emission.emit(fld, budget, f["visible"], spacing=2.8, apron_px=2, thin=False)
                    r, t = holdout.evaluate_dots(dots, f)
                    terms.append(t); per_fold.append(r["dti"]); ndots.append(int(dots.sum()))
                pooled = holdout.pooled(terms)
                key = f"{name}@{budget}"
                sch["arms"][key] = {"pooled": pooled, "per_fold_dti": per_fold, "n_dots_per_fold": ndots}
                terms_by_arm[key] = terms
                print(f"[{scheme}] {key:28s} pooled DTI {pooled['dti']:.5f} per-fold {np.round(per_fold, 4)} dots {ndots} [{time.time()-t0:.0f}s]", flush=True)
        # paired bootstrap: reference arm = physics at the middle budget
        ref = f"physics@{BUDGETS[len(BUDGETS)//2]}"
        ordered = {ref: terms_by_arm[ref], **{k: v for k, v in terms_by_arm.items() if k != ref}}
        sch["bootstrap_vs_" + ref] = holdout.bootstrap_ci(ordered)
        results["schemes"][scheme] = sch
    out = ROOT / "evidence" / "exp2_gpcz_holdout.json"
    out.write_text(json.dumps(results, indent=1) + "\n")
    print("wrote", out)


if __name__ == "__main__":
    main()
