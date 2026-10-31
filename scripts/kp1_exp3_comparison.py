#!/usr/bin/env python3
"""EXP3b — is the candidate better than a random field of the same size?

The only positively-oriented truth available locally is the SGMC compilation of
faults that the USGS catalogue does not contain (``evidence/kp1_exp2_external.json``).
This script asks the one question that instrument can answer honestly:

    on an independent off-catalogue fault inventory, does the candidate cover
    more fault mass than a random dot field with the same number of dots?

If the answer is no, the surface is decoration and should not be submitted.  If
the answer is yes, the surface carries real off-catalogue signal and the
remaining uncertainty is about *which* off-catalogue faults the private truth
contains -- a question no local raster can settle.

Also reported, for context and with the correct caveat:

* the same comparison for the nine focus rasters at their own budgets;
* a random field at B2's budget, to show the candidate's coverage efficiency
  (dots spent per unit of fault mass covered);
* a block bootstrap (200 x 200 px blocks, 400 draws) for the candidate-vs-random
  difference, which is the only uncertainty statement that is meaningful here.

Output: ``evidence/kp1_exp3_comparison.json``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import grid, metric                       # noqa: E402

CANDIDATE = ROOT / "docs" / "downloads" / "karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif"
OUT = ROOT / "evidence" / "kp1_exp3_comparison.json"
BLOCK = 200
DRAWS = 400
SEEDS = (0, 1, 2)


def dti(pred, truth) -> dict:
    r = metric.dti_exact(pred.astype(np.float32), truth)
    return {k: float(r[k]) for k in ("dti", "tp", "fp", "fn")}


def uniform_dots(n: int, pool: np.ndarray, shape, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    idx = np.flatnonzero(pool.ravel())
    pick = rng.choice(idx, size=min(n, idx.size), replace=False)
    out = np.zeros(shape, np.float32)
    out.ravel()[pick] = 1.0
    return out


def _equivalent_dots(n_cand: int, target: float, pool, shape, truth,
                     hi: int = 200_000) -> int:
    """Smallest random-dot count whose off-catalogue DTI reaches ``target`` (bisection)."""
    lo, hi = n_cand, hi
    while lo < hi:
        mid = (lo + hi) // 2
        if dti(uniform_dots(mid, pool, shape, 0), truth)["dti"] >= target:
            hi = mid
        else:
            lo = mid + 1
    return int(lo)


def main() -> None:
    g = grid.load_grid()
    fp, cat = g.footprint, g.catalogue
    sg = rasterio.open(ROOT / "data" / "external" / "derived_sgmc_faults_100m_u8.tif").read(1) > 0
    d_cat = ndi.distance_transform_edt(~cat)
    truth = sg & (d_cat > 3) & fp
    pool = fp & (d_cat > 2)     # the constraint every submission must respect

    cand = rasterio.open(CANDIDATE).read(1).astype(np.float32)
    cand = np.nan_to_num(cand, nan=0.0)
    n_cand = int((cand > 0).sum())
    cand_res = dti(cand, truth)

    uniform = {}
    for seed in SEEDS:
        u = uniform_dots(n_cand, pool, fp.shape, seed)
        uniform[str(seed)] = dti(u, truth)
    uni_mean = {k: float(np.mean([uniform[str(s)][k] for s in SEEDS]))
                for k in ("dti", "tp", "fp", "fn")}

    # ---- block bootstrap of the difference (candidate minus matched random)
    h, w = fp.shape
    raw = (np.arange(h) // BLOCK)[:, None] * 10_000 + (np.arange(w) // BLOCK)[None, :]
    _, bids = np.unique(raw, return_inverse=True)
    bids = bids.reshape(fp.shape)
    blocks = np.arange(bids.max() + 1).tolist()
    rng = np.random.default_rng(20261031)
    base_u = uniform_dots(n_cand, pool, fp.shape, 0)
    diff = []
    for _ in range(DRAWS):
        pick = rng.choice(len(blocks), size=len(blocks), replace=True)
        mask = np.isin(bids, pick)
        tc = truth & mask
        if tc.sum() < 200:
            continue
        r_c = metric.dti_exact(cand, tc)
        r_u = metric.dti_exact(base_u, tc)
        diff.append(float(r_c["dti"]) - float(r_u["dti"]))
    diff = np.array(diff)

    rows = {}
    for f in sorted((ROOT / "registry").glob("*.tif")):
        site = f.name.split("_")[0]
        p = rasterio.open(f).read(1).astype(np.float32)
        p = np.nan_to_num(p, nan=0.0)
        rows[site] = {"n": int((p > 0).sum()), "dti_offcat": dti(p, truth)["dti"]}

    b2 = rows["GEMSDOE32"]["n"]
    big_uniform = {str(s): dti(uniform_dots(b2, pool, fp.shape, s), truth)["dti"] for s in SEEDS}

    out = {
        "schema": "kp1-exp3-comparison-v1",
        "truth": "SGMC faults inside the footprint, >3 px from the catalogue",
        "truth_px": int(truth.sum()),
        "candidate": {"file": CANDIDATE.name, "dots": n_cand, **cand_res,
                      "covered_truth_credit": cand_res["tp"]},
        "matched_uniform": {"dots": n_cand, "per_seed": uniform, "mean": uni_mean,
                            "relative_gain_of_candidate": float(cand_res["dti"] / uni_mean["dti"] - 1.0)},
        "uniform_at_champion_budget": {"dots": b2, "per_seed": big_uniform,
                                       "mean": float(np.mean(list(big_uniform.values())))},
        "coverage_efficiency": {
            "candidate_dots": n_cand,
            "candidate_equivalent_uniform_dots": _equivalent_dots(n_cand, cand_res["dti"],
                                                                pool, fp.shape, truth),
            "interpretation": ("the number of random dots needed to match the candidate's "
                               "off-catalogue fault coverage; a lower ratio means each dot "
                               "buys more expected truth credit"),
        },
        "nine_focus_files": rows,
        "block_bootstrap": {"block_px": BLOCK, "draws": int(diff.size),
                            "mean_diff": float(diff.mean()),
                            "p2.5": float(np.quantile(diff, 0.025)),
                            "p97.5": float(np.quantile(diff, 0.975)),
                            "fraction_of_draws_positive": float((diff > 0).mean())},
        "caveats": [
            "This is a HOLDOUT-DTI on an independent expert fault inventory, not the organizer "
            "metric and not a leaderboard score.",
            "The inventory disagrees with the observed leaderboard ordering (rho -0.34, p 0.36 "
            "on the nine files), so it cannot be used to predict a score; it is used only to "
            "test whether the candidate's surface beats a random field of the same size.",
            "The nine files score higher on this inventory because they spend more dots over "
            "more of the map, which is exactly the behaviour the organizer metric punishes; the "
            "instrument therefore ranks *emission strategies* and not submissions.",
        ],
    }
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("candidate", "matched_uniform",
                                          "uniform_at_champion_budget", "coverage_efficiency",
                                          "block_bootstrap")}, indent=1)[:2500])


if __name__ == "__main__":
    main()
