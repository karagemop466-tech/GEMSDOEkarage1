#!/usr/bin/env python3
"""Experiment 3 of the 2026-10-29 budget (the last one): does the model's ranking
add DTI *within* the catalogue-adjacent ring, against a fair random tie-break?

Why this experiment exists
--------------------------
In ``run_probcollar_holdout.py`` the ``ctrl_proximity`` arm used ``argpartition``
to pick K pixels from the 1-px ring around the visible catalogue. At K = 37,654
that ring (about 2 x catalogue pixels) is far larger than K, so the arm's pixels
were chosen by an arbitrary, index-order tie-break. That makes it a weak control.
This script replaces it with two controls that differ only in tie-break:

* ``ring_model``  : rank = (catalogue distance ascending, then model p descending)
* ``ring_random`` : rank = (catalogue distance ascending, then uniform random)

Pre-registered hypothesis H3: ring_model - ring_random > 0 with a 95% CI above 0 in
both holdout modes ('all' and 'detached'). If not, the model adds no measurable
value inside the ring and the holdout cannot promote it.

Both arms use the same K (37,654, scaled per quadrant), the same holdout cells,
the same visible-only training, and the shared scorer (``holdout.score_cell``).
Collar r = 0 for both (the ring is the thing being ranked).
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src", "scripts"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57 import holdout as H  # noqa: E402
from gems57.evaluate_holdout import VERSION as EVAL_VERSION, pooled_summary  # noqa: E402
from gems57.grid import DATA_DIR, load_grid  # noqa: E402
from gems57.metric import ALPHA, BETA  # noqa: E402

from run_probcollar_holdout import (  # noqa: E402
    K_LIST, RNG_SEED, TRAIN_TIF, band_canary, fit_probability, load_feature_stack, sha256,
)

K = 37654


def ring_select(dist_fp, p_fp, region_fp, k, tiebreak, rng) -> np.ndarray:
    """Top-k by (distance asc, tiebreak desc). Distances are >= 0.41 apart, so the
    tie-break term (<= 0.1) can never reorder two different distances."""
    ok = region_fp & (dist_fp > 0)                       # collar r = 0: never on the catalogue
    if tiebreak == "model":
        t = p_fp
    elif tiebreak == "random":
        t = rng.random(p_fp.shape).astype(np.float32)
    else:
        raise ValueError(tiebreak)
    score = np.where(ok, -dist_fp + 0.1 * t, -np.inf)
    n_ok = int(ok.sum())
    kk = min(k, n_ok)
    out = np.zeros(score.shape, bool)
    if kk > 0:
        out[np.argpartition(-score, kk - 1)[:kk]] = True
    return out


def run(mode: str, out_path: Path) -> dict:
    t0 = time.time()
    grid = load_grid(DATA_DIR)
    fp = grid.footprint
    ctx = H.build_holdout(grid, seeds=(20, 21), modes=(mode,))
    X, names = load_feature_stack(grid)
    canary = band_canary(X, names, grid, ctx)
    fp_total = int(fp.sum())
    rng = np.random.default_rng(RNG_SEED + 3)
    terms: dict[str, list[list[float]]] = {"ring_model": [], "ring_random": []}
    for cell in ctx.cells:
        visible = ctx.visible(cell.key)
        dist_fp = ndi.distance_transform_edt(~visible)[fp]
        region_fp = (ctx.quad == cell.fold)[fp]
        share = float(region_fp.sum()) / fp_total
        Kc = int(round(K * share))
        p_fp = fit_probability(X, grid, visible)
        for arm, tb in (("ring_model", "model"), ("ring_random", "random")):
            em = ring_select(dist_fp, p_fp, region_fp, Kc, tb, rng)
            full = np.zeros(grid.shape, bool)
            full[fp] = em
            s = H.score_cell(cell, full)
            terms[arm].append([s["tp"], s["fp"], s["fn"], float(s["n_truth"])])
    arms = {k_: np.asarray(v, float) for k_, v in terms.items()}
    ps = pooled_summary(arms, draws=2000, seed=520810, candidate="ring_model")
    diff = ps["paired_differences"]["ring_random"]
    result = dict(
        mode=mode,
        K=K,
        ring_model=dict(dti=ps["scores"]["ring_model"]["dti"], ci95=ps["scores"]["ring_model"]["ci95"],
                        withheld_positive_pixels=ps["scores"]["ring_model"]["withheld_positive_pixels"]),
        ring_random=dict(dti=ps["scores"]["ring_random"]["dti"], ci95=ps["scores"]["ring_random"]["ci95"]),
        delta_ring_model_minus_ring_random=dict(delta=diff["delta"], ci95=diff["ci95"]),
        H3_supported=bool(diff["ci95"][0] > 0.0),
        canary_max_auc=canary["max_auc"], canary_max_feature=canary["max_feature"],
        canary_leakage_flag=canary["leakage_flag"],
        runtime_s=round(time.time() - t0, 1),
    )
    out_path.write_text(json.dumps(result, indent=2, default=float) + "\n")
    print(f"[{mode}] ring_model={result['ring_model']['dti']:.4f} ring_random={result['ring_random']['dti']:.4f} "
          f"delta={diff['delta']:+.4f} CI={[round(x,4) for x in diff['ci95']]} H3={result['H3_supported']} "
          f"({result['runtime_s']}s)", flush=True)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["all", "detached"], required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = Path(args.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    r = run(args.mode, out)
    r["software"] = dict(python=platform.python_version(), evaluator_version=EVAL_VERSION,
                         alpha=ALPHA, beta=BETA, training_features_sha256=sha256(TRAIN_TIF))
    out.write_text(json.dumps(r, indent=2, default=float) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
