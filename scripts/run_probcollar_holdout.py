#!/usr/bin/env python3
"""Hide-and-recover HOLDOUT-DTI for a label-free-feature probability model with a
catalogue-collar exclusion (one of the three budgeted experiments, 2026-10-29).

Protocol mapping
----------------
* Holdout geometry, withheld segments, erosion and pixel-exact masking of visible
  faults come from the SHARED template ``vendor/gems57/holdout.py`` (not forked).
* Scoring is the shared exact per-cell DTI ``holdout.score_cell`` (alpha 0.2,
  beta 0.8, 3 px triangular kernel).  Pooled terms and the paired bootstrap come
  from ``gems57.evaluate_holdout.pooled_summary``.
* Model inputs are the 19 organiser feature bands only.  No catalogue-derived
  feature is used.  Training positives are VISIBLE catalogue pixels; training
  negatives are footprint pixels > 5 px from the VISIBLE catalogue.  Withheld
  pixels are never used for fitting, selection or the collar.
* Emission is top-K of the model probability inside each fold quadrant, with K
  scaled to the quadrant's footprint share, after excluding pixels within r px of
  the visible catalogue (r = collar).  Controls: uniform random placement, and
  catalogue-proximity ranking (no model).
* Leakage canary: direction-invariant single-band AUC on the holdout (truth vs
  in-domain background).  Any AUC > 0.90 is flagged as leakage until disproven.

Output: ``evidence/holdout_probcollar_20261029.json``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57 import holdout as H  # noqa: E402
from gems57.holdout import build_holdout  # noqa: E402
from gems57.evaluate_holdout import VERSION as EVAL_VERSION, from_terms, pooled_summary  # noqa: E402
from gems57.grid import DATA_DIR, load_grid  # noqa: E402
from gems57.metric import ALPHA, BETA  # noqa: E402

OUT = ROOT / "evidence" / "holdout_probcollar_20261029.json"
TRAIN_TIF = DATA_DIR / "training_features.tif"
R_LIST = (0, 1, 2, 3)
K_LIST = (22163, 37654)         # 22,163 = largest K not ruled out by the lattice bound; 37,654 = champion size
N_POS, N_NEG = 60_000, 120_000
RNG_SEED = 20261029


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_feature_stack(grid) -> tuple[np.ndarray, list[str]]:
    """Footprint-only feature matrix (n_fp x 19), float32, nodata -> NaN -> median."""
    fp = grid.footprint
    n_fp = int(fp.sum())
    with rasterio.open(TRAIN_TIF) as src:
        if src.count != 19 or (src.height, src.width) != grid.shape:
            raise ValueError(f"training_features shape/bands unexpected: {src.count}, {src.shape}")
        names = [d or f"band{i+1}" for i, d in enumerate(src.descriptions)]
        X = np.empty((n_fp, src.count), np.float32)
        for b in range(1, src.count + 1):
            a = src.read(b).astype(np.float32)
            a[(a < -1e30) | ~np.isfinite(a)] = np.nan          # -3.4028235e+38 sentinel -> NaN
            med = np.nanmedian(a[fp])
            a = np.where(np.isfinite(a), a, med)
            X[:, b - 1] = a[fp]
            del a
    return X, names


def truth_full(cell: H.Cell, shape) -> np.ndarray:
    t = np.zeros(shape, bool)
    view = t[cell.bbox]
    view[cell.truth_yx] = True
    return t


def active_full(cell: H.Cell, shape) -> np.ndarray:
    a = np.zeros(shape, bool)
    a[cell.bbox] = cell.active
    return a


def band_canary(X, names, grid, ctx) -> dict:
    """Single-feature AUC (direction-invariant) on each holdout cell."""
    fp_idx = np.flatnonzero(grid.footprint)
    rng = np.random.default_rng(RNG_SEED)
    per = {n: [] for n in names}
    for cell in ctx.cells:
        t = truth_full(cell, grid.shape)[grid.footprint]
        act = active_full(cell, grid.shape)[grid.footprint]
        pos = np.flatnonzero(t & act)
        neg_pool = np.flatnonzero(act & ~t)
        if pos.size < 20 or neg_pool.size < 100:
            continue
        neg = rng.choice(neg_pool, size=min(50_000, neg_pool.size), replace=False)
        idx = np.concatenate([pos, neg])
        y = np.concatenate([np.ones(pos.size), np.zeros(neg.size)])
        for j, n in enumerate(names):
            v = X[idx, j]
            auc = roc_auc_score(y, v)
            per[n].append(max(auc, 1.0 - auc))
    summary = {n: dict(auc_dir_inv_mean=float(np.mean(v)), auc_dir_inv_max=float(np.max(v)), n_cells=len(v))
               for n, v in per.items() if v}
    worst = max(summary, key=lambda n: summary[n]["auc_dir_inv_max"])
    return dict(
        per_band=summary,
        max_auc=summary[worst]["auc_dir_inv_max"],
        max_feature=worst,
        leakage_flag=bool(summary[worst]["auc_dir_inv_max"] > 0.90),
        note="AUC > 0.90 on a single feature = leakage until disproven (protocol rule 4).",
    )


def fit_probability(X, grid, visible: np.ndarray) -> np.ndarray:
    """Fit on VISIBLE catalogue only; return footprint-flat probability."""
    fp = grid.footprint
    dist_vis = ndi.distance_transform_edt(~visible)
    pos_all = np.flatnonzero((visible & fp).ravel())
    neg_all = np.flatnonzero((fp & (dist_vis > 5)).ravel())
    rng = np.random.default_rng(RNG_SEED)
    pos = rng.choice(pos_all, size=min(N_POS, pos_all.size), replace=False)
    neg = rng.choice(neg_all, size=min(N_NEG, neg_all.size), replace=False)
    # map full-grid flat indices -> footprint row indices
    fp_flat = np.flatnonzero(fp.ravel())
    row = np.full(grid.shape[0] * grid.shape[1], -1, np.int64)
    row[fp_flat] = np.arange(fp_flat.size)
    rows = np.concatenate([row[pos], row[neg]])
    y = np.concatenate([np.ones(pos.size), np.zeros(neg.size)])
    clf = HistGradientBoostingClassifier(max_iter=150, learning_rate=0.1, max_leaf_nodes=31,
                                         random_state=0)
    clf.fit(X[rows], y)
    out = np.empty(X.shape[0], np.float32)
    for i in range(0, X.shape[0], 1_000_000):   # chunked: 3.9 GB RAM host
        out[i:i+1_000_000] = clf.predict_proba(X[i:i+1_000_000])[:, 1]
    return out


def select(score_fp, region_fp, excl_fp, k) -> np.ndarray:
    """Top-k of score within region and not excluded; returns footprint-flat bool."""
    ok = region_fp & ~excl_fp
    s = np.where(ok, score_fp, -np.inf)
    n_ok = int(ok.sum())
    k = min(k, n_ok)
    out = np.zeros(score_fp.shape, bool)
    if k <= 0:
        return out
    idx = np.argpartition(-s, k - 1)[:k]
    out[idx] = True
    return out


def main() -> int:
    global OUT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", default="all", choices=["all", "detached"],
                    help="holdout segment eligibility: all (primary) or detached (conservative)")
    ap.add_argument("--out", default=str(OUT), help="output JSON path")
    args = ap.parse_args()
    OUT = Path(args.out).resolve()
    t0 = time.time()
    grid = load_grid(DATA_DIR)
    fp = grid.footprint
    ctx = build_holdout(grid, seeds=(20, 21), modes=(args.mode,))
    print(f"[holdout] cells={len(ctx.cells)} footprint={int(fp.sum())} catalogue={int(grid.catalogue.sum())}", flush=True)

    X, names = load_feature_stack(grid)
    print(f"[features] {X.shape} bands={names[:3]}... ({time.time()-t0:.0f}s)", flush=True)

    canary = band_canary(X, names, grid, ctx)
    print(f"[canary] max single-band AUC={canary['max_auc']:.4f} ({canary['max_feature']}) leakage={canary['leakage_flag']}", flush=True)

    fp_total = int(fp.sum())
    arms_terms: dict[str, list[list[float]]] = {}
    arm_meta: dict[str, dict] = {}

    def add(arm, cell_terms, meta):
        arms_terms.setdefault(arm, []).append(cell_terms)
        arm_meta.setdefault(arm, meta)

    rng = np.random.default_rng(RNG_SEED)
    for cell in ctx.cells:
        visible = ctx.visible(cell.key)
        hidden = ctx.hidden_by_cell[cell.key]
        dist_vis_full = ndi.distance_transform_edt(~visible)
        quad = (ctx.quad == cell.fold)
        region_full = quad & fp
        region_fp = region_full[fp]
        share = float(region_fp.sum()) / fp_total
        dist_fp = dist_vis_full[fp]
        t0c = time.time()
        p_fp = fit_probability(X, grid, visible)
        p_time = time.time() - t0c

        cell_summary = {}
        for K in K_LIST:
            Kc = int(round(K * share))
            for r in R_LIST:
                excl = dist_fp <= r
                em = select(p_fp, region_fp, excl, Kc)
                emit_full = np.zeros(grid.shape, bool)
                emit_full[fp] = em
                s = H.score_cell(cell, emit_full)
                add(f"model_K{K}_r{r}", [s["tp"], s["fp"], s["fn"], float(s["n_truth"])],
                    dict(K=K, r=r, kind="model"))
                cell_summary[f"model_K{K}_r{r}"] = s["dti"]

            # control: catalogue-proximity ranking (no model): nearest first, collar r=0
            prox_score = -dist_fp.astype(np.float64)
            em = select(prox_score, region_fp, dist_fp <= 0, Kc)
            emit_full = np.zeros(grid.shape, bool)
            emit_full[fp] = em
            s = H.score_cell(cell, emit_full)
            add(f"ctrl_proximity_K{K}", [s["tp"], s["fp"], s["fn"], float(s["n_truth"])],
                dict(K=K, r=0, kind="control_no_model"))

            # control: uniform random placement inside region, not on visible catalogue
            rnd = rng.random(p_fp.shape)
            em = select(rnd, region_fp, dist_fp <= 0, Kc)
            emit_full = np.zeros(grid.shape, bool)
            emit_full[fp] = em
            s = H.score_cell(cell, emit_full)
            add(f"ctrl_random_K{K}", [s["tp"], s["fp"], s["fn"], float(s["n_truth"])],
                dict(K=K, r=0, kind="control_random"))
        print(f"[cell {cell.key}] n_truth={cell.n_truth} visible={int(visible.sum())} "
              f"fit+predict={p_time:.0f}s dti(model_K22163_r0..3)="
              f"{[round(cell_summary[f'model_K22163_r{r}'],4) for r in R_LIST]}", flush=True)

    arms = {k: np.asarray(v, float) for k, v in arms_terms.items()}
    # pooled_summary needs a candidate arm; use each model arm as candidate in turn
    summaries = {}
    for arm in arms:
        ps = pooled_summary(arms, draws=1000, seed=520810, candidate=arm)
        summaries[arm] = dict(
            dti=ps["scores"][arm]["dti"],
            ci95=ps["scores"][arm]["ci95"],
            withheld_positive_pixels=ps["scores"][arm]["withheld_positive_pixels"],
            tpw=ps["scores"][arm]["tpw"], fpw=ps["scores"][arm]["fpw"], fnw=ps["scores"][arm]["fnw"],
            meta=arm_meta[arm],
            paired_vs_controls=ps["paired_differences"],
        )
    best_model = max((a for a in summaries if a.startswith("model_")), key=lambda a: summaries[a]["dti"])
    card = dict(
        schema="karage1-probcollar-holdout-v1",
        created_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        evidence_class="HOLDOUT-DTI",
        evaluator_version=EVAL_VERSION,
        scope="Hide-and-recover on the organiser catalogue (labels.tif = USGS/INGENIOUS). Score is against WITHHELD CATALOGUE segments, not the organiser's hidden new-fault set. Not a leaderboard estimate.",
        alpha=ALPHA, beta=BETA, radius_px=3,
        holdout=dict(module="vendor/gems57/holdout.py", cells=[c.key for c in ctx.cells],
                     withheld_fraction=0.20, domain_erode_px=H.DOMAIN_ERODE, modes=[args.mode]),
        features=dict(source=str(TRAIN_TIF.name), bands=names, sha256=sha256(TRAIN_TIF) if TRAIN_TIF.exists() else None,
                      nodata_handling="-3.4e38 -> NaN -> per-band footprint median"),
        model=dict(kind="HistGradientBoostingClassifier", max_iter=150, lr=0.1, leaves=31,
                   positives="visible catalogue pixels", negatives="footprint pixels > 5 px from visible catalogue",
                   n_pos=N_POS, n_neg=N_NEG, seed=RNG_SEED),
        emission=dict(rule="top-K of p in fold quadrant (K scaled by footprint share) after collar r px from visible catalogue",
                      K_list=list(K_LIST), r_list=list(R_LIST)),
        leakage_canary=canary,
        arms=summaries,
        best_model_arm=best_model,
        software=dict(python=platform.python_version(), numpy=np.__version__,
                      rasterio=rasterio.__version__),
        inputs=dict(training_features_sha256=sha256(TRAIN_TIF), labels_sha256=sha256(DATA_DIR / "labels.tif")),
        runtime_s=round(time.time() - t0, 1),
        caveats=[
            "Holdout withheld units are catalogue segments; new-fault adjacency to catalogue (the mechanism the h33 collar may exploit) is NOT measured by this design.",
            "Only 8 fold-cells (2 draws x 4 quadrants); the paired bootstrap resamples cells, so CIs are low-power and optimistic in width.",
            "The shared holdout masks visible faults pixel-exactly, consistent with the organiser's 2026-09-16 answer (community.drivendata.org/t/11516).",
        ],
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(card, indent=2, default=float) + "\n")
    print(f"[done] wrote {OUT} best={best_model} dti={summaries[best_model]['dti']:.4f} "
          f"ci={summaries[best_model]['ci95']} ({time.time()-t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
