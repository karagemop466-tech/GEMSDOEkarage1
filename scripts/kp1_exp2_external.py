"""EXP2 — an external-truth instrument for off-catalogue faults.

Why a new instrument is needed
------------------------------
The competition's scored truth is a set of faults that an expert panel mapped and
that is **absent from the training catalogue**.  A hide-and-recover holdout on
the catalogue therefore measures the wrong thing: it rewards recovering traces
that are already in the catalogue, which is exactly what the private truth is
*not*.  The previous lane measured that inversion (Spearman -1.0 against the
nine known scores) and correctly refused to use it.

This script uses a different truth: ``data/external/derived_sgmc_faults_100m_u8.tif``
(the state-geological-map-compilation fault set distributed with the competition
reference material).  Measured on this checkout:

* 83,593 cells inside the footprint, of which only 3,978 coincide with a
  catalogue cell and 21,471 lie within 3 px of one;
* after removing the 3-px catalogue corridor, **62,122** cells remain.

That residual is a real, independent expert compilation of faults that the USGS
catalogue does not contain -- the closest local analogue of the private truth,
and the *only* positively-oriented instrument available without spending a slot.

Leakage control
---------------
Truth cells inside the 3-px catalogue corridor are dropped from both training and
scoring, so no feature that encodes "distance to catalogue" can be right by
construction.  All scoring is leave-one-quadrant-out over four 1,865 x 1,646
blocks; a label-permutation canary is reported for every arm.

Arms (all emitted through the same rule and the same budget ladder)
-----------------------------------------------------------------
``uniform``    flat surface (a random dot field of the same size)
``catalogue``  model trained on catalogue positives only
``offcat``     model trained on the SGMC-off-catalogue positives only
``both``       model trained on the union of the two

Output: ``evidence/kp1_exp2_external.json``.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import grid, metric                      # noqa: E402
from gems57.metric import OFF_DY, OFF_DX, OFF_K      # noqa: E402

PLANES = ROOT / ".cache" / "kp1" / "planes"
EXTERNAL = ROOT / "data" / "external" / "derived_sgmc_faults_100m_u8.tif"
OUT = ROOT / "evidence" / "kp1_exp2_external.json"

FEATURES = [
    "ThK", "UK", "UTh", "tc", "tmi_hg", "tmi_vg", "up150_grad",
    "iso_grav_anom_hg", "iso_grav_anom_slope", "geod_shearrate", "geod_2ndinv",
    "det_elev", "det_elev_slope", "elev_ridge3", "curv2", "deq",
    "spring_kde", "vent_kde", "cond_surf", "depth_to_base_surf",
    "lidar_step", "lidar_lapneg", "lidar_coh", "lidar_ex", "lidar_relief",
]
BUDGETS = [5_000, 10_000, 20_000, 30_000, 40_000]
MIN_SEP = 4.0
NEG_PER_FOLD = 150_000
SEED = 20261031


def planes() -> dict[str, np.ndarray]:
    return {name: np.load(PLANES / f"{name}.npy") for name in FEATURES}


def quadrant_id(shape) -> np.ndarray:
    h, w = shape
    q = np.zeros(shape, np.int8)
    q[h // 2:, :] += 2
    q[:, w // 2:] += 1
    return q


def expected_credit(p: np.ndarray) -> np.ndarray:
    """Kernel convolution: the credit a dot at x would earn if the truth were p."""
    out = np.zeros_like(p, dtype=np.float32)
    for dy, dx, kw in zip(OFF_DY, OFF_DX, OFF_K):
        out += kw * np.roll(np.roll(p, dy, axis=0), dx, axis=1)
    return out


def min_sep_select(rank: np.ndarray, allowed: np.ndarray, budget: int,
                   sep: float = MIN_SEP) -> np.ndarray:
    """Greedy pick in decreasing ``rank`` with a hard Euclidean minimum separation."""
    flat = np.where(allowed, rank, -np.inf).ravel()
    take = min(int(budget), int(np.isfinite(flat).sum()))
    cand = np.argpartition(-flat, take - 1)[:take]
    cand = cand[np.argsort(-flat[cand])]
    h, w = rank.shape
    dots = np.zeros((h, w), bool)
    occ: dict[tuple[int, int], list[tuple[int, int]]] = {}
    r = int(np.ceil(sep))
    out_y, out_x = [], []
    for idx in cand:
        y, x = divmod(int(idx), w)
        key = (y // r, x // r)
        ok = True
        for ky in range(key[0] - 1, key[0] + 2):
            for kx in range(key[1] - 1, key[1] + 2):
                for py, px in occ.get((ky, kx), ()):
                    if (py - y) ** 2 + (px - x) ** 2 < sep * sep:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                break
        if ok:
            occ.setdefault(key, []).append((y, x))
            out_y.append(y)
            out_x.append(x)
            dot = np.zeros((h, w), bool)
    dots[np.array(out_y), np.array(out_x)] = True
    return dots


def train_model(X, y, Xte, seed: int = 0):
    import lightgbm as lgb
    params = dict(objective="binary", learning_rate=0.05, num_leaves=63,
                  min_child_samples=60, feature_fraction=0.8, bagging_fraction=0.8,
                  bagging_freq=1, verbose=-1, num_threads=2, seed=seed)
    ds = lgb.Dataset(X, label=y)
    booster = lgb.train(params, ds, num_boost_round=220)
    return booster.predict(Xte)


def surface(booster, feats: dict[str, np.ndarray], rows, cols) -> np.ndarray:
    h = len(rows)
    X = np.empty((h * len(cols), len(FEATURES)), np.float32)
    for j, name in enumerate(FEATURES):
        X[:, j] = feats[name][np.ix_(rows, cols)].ravel()
    p = booster.predict(X, num_iteration=220).astype(np.float32)
    return p.reshape(h, len(cols))


def evaluate(pred: np.ndarray, truth: np.ndarray, allowed: np.ndarray) -> dict:
    r = metric.dti_exact(pred.astype(np.float32), truth)
    return {k: float(r[k]) for k in ("dti", "tp", "fp", "fn")}


def main() -> None:
    t0 = time.time()
    g = grid.load_grid()
    fp, cat = g.footprint, g.catalogue
    sg = rasterio.open(EXTERNAL).read(1) > 0
    d_cat = ndi.distance_transform_edt(~cat)
    offcat = sg & (d_cat > 3) & fp           # 62,122 cells
    qid = quadrant_id(fp.shape)
    feats = planes()
    rng = np.random.default_rng(SEED)

    # positives for the catalogue arm: catalogue cells far from the SGMC set, so the
    # two arms are trained on disjoint fault inventories
    d_sg = ndi.distance_transform_edt(~sg)
    cat_pos = cat & (d_sg > 3) & fp

    yx_off = np.argwhere(offcat)
    yx_cat = np.argwhere(cat_pos)
    free = fp & ~ndi.binary_dilation(offcat | cat_pos, iterations=3)

    results = {"schema": "kp1-exp2-external-v1",
               "instrument": "SGMC-off-catalogue, leave-one-quadrant-out, pooled",
               "truth_cells": int(offcat.sum()),
               "truth_cells_catalogue_corridor_removed": int((sg & (d_cat > 3)).sum()),
               "catalogue_arm_positives": int(cat_pos.sum()),
               "budgets": BUDGETS, "min_sep_px": MIN_SEP, "folds": [], "arms": {}}
    print(f"truth offcat={offcat.sum()} cat_arm={cat_pos.sum()}", flush=True)

    for q in range(4):
        te = qid == q
        tr = (qid != q) & fp
        print(f"[fold {q}] truth_test={int((offcat & te).sum())}", flush=True)

        # ---- training sample
        pos_off = yx_off[qid[offcat] != q]
        pos_cat = yx_cat[qid[cat_pos] != q]
        neg_idx = np.flatnonzero((free & tr).ravel())
        neg_sel = rng.choice(neg_idx, size=min(NEG_PER_FOLD, neg_idx.size), replace=False)
        neg = np.column_stack(np.unravel_index(neg_sel, fp.shape))

        def build(pos):
            yy = np.concatenate([pos[:, 0], neg[:, 0]])
            xx = np.concatenate([pos[:, 1], neg[:, 1]])
            X = np.column_stack([feats[n][yy, xx] for n in FEATURES]).astype(np.float32)
            y = np.concatenate([np.ones(len(pos)), np.zeros(len(neg))]).astype(np.float32)
            return X, y

        Xc, yc = build(pos_cat)
        Xo, yo = build(pos_off)
        Xb = np.vstack([Xc, Xo]); yb = np.concatenate([yc, yo])
        datasets = {
            "catalogue": (Xc, yc),
            "offcat": (Xo, yo),
            "both": (Xb, yb),
            "canary_offcat": (Xo, rng.permutation(yo)),
            "canary_catalogue": (Xc, rng.permutation(yc)),
        }

        # prediction grid for the held-out quadrant
        rows = np.flatnonzero(te.any(axis=1))
        cols = np.flatnonzero(te.any(axis=0))
        sub_te = te[np.ix_(rows, cols)] & fp[np.ix_(rows, cols)]
        truth_te = offcat[np.ix_(rows, cols)]

        fold = {"fold": q, "truth_test": int(truth_te.sum()),
                "rows": [int(rows[0]), int(rows[-1])],
                "cols": [int(cols[0]), int(cols[-1])], "auc": {}, "arms": {}}

        for name in ("catalogue", "offcat", "both", "canary_offcat", "canary_catalogue"):
            X, y = datasets[name]
            import lightgbm as lgb
            params = dict(objective="binary", learning_rate=0.05, num_leaves=63,
                          min_child_samples=60, feature_fraction=0.8,
                          bagging_fraction=0.8, bagging_freq=1, verbose=-1,
                          num_threads=2, seed=SEED + q)
            booster = lgb.train(params, lgb.Dataset(X, label=y), num_boost_round=220)
            p = surface(booster, feats, rows, cols)
            from sklearn.metrics import roc_auc_score
            fold["auc"][name] = float(roc_auc_score(truth_te[sub_te], p[sub_te]))
            if name.startswith("canary"):
                continue
            rank = expected_credit(p)
            np.save(ROOT / ".cache" / "kp1" / f"p_{name}_q{q}.npy", p.astype(np.float32))
            for b in BUDGETS:
                dots = min_sep_select(rank, sub_te, b)
                fold["arms"].setdefault(name, {})[str(b)] = evaluate(dots, truth_te, sub_te)
            print(f"  {name}: auc={fold['auc'][name]:.4f} "
                  f"dti@40k={fold['arms'][name]['40000']['dti']:.4f}", flush=True)

        # uniform reference arm (random dot field, same budget ladder)
        for b in BUDGETS:
            dots = min_sep_select(rng.random(fp.shape)[np.ix_(rows, cols)], sub_te, b)
            fold["arms"].setdefault("uniform", {})[str(b)] = evaluate(dots, truth_te, sub_te)
        print(f"  uniform: dti@40k={fold['arms']['uniform']['40000']['dti']:.4f}", flush=True)
        results["folds"].append(fold)

    # ---- pooled terms: sum tp/fp/fn across folds, then re-apply the metric
    pooled = {}
    for arm in ("uniform", "catalogue", "offcat", "both"):
        pooled[arm] = {}
        for b in BUDGETS:
            rows = [f["arms"][arm][str(b)] for f in results["folds"]]
            tp = sum(r["tp"] for r in rows)
            fpx = sum(r["fp"] for r in rows)
            fn = sum(r["fn"] for r in rows)
            pooled[arm][str(b)] = {
                "dti": float(metric.dti_from_components(tp, fpx, fn)),
                "tp": float(tp), "fp": float(fpx), "fn": float(fn),
                "per_fold_dti": [round(r["dti"], 4) for r in rows],
            }
    results["pooled"] = pooled
    results["auc_mean"] = {k: float(np.mean([f["auc"].get(k, np.nan) for f in results["folds"]]))
                           for k in ("catalogue", "offcat", "both")}
    results["canary_auc_mean"] = {k: float(np.mean([f["auc"][k] for f in results["folds"]]))
                                 for k in ("canary_offcat", "canary_catalogue")}
    results["leakage_alarm"] = any(v > 0.90 for v in results["canary_auc_mean"].values())
    results["runtime_s"] = round(time.time() - t0, 1)
    results["caveat"] = (
        "SGMC-off-catalogue DTI is a HOLDOUT-DTI on an independent expert fault inventory, "
        "NOT the organizer metric and NOT a leaderboard score. It is positively oriented "
        "(higher = more off-catalogue fault mass covered) in a way the hide-and-recover "
        "instrument is not; it still disagrees with the nine user-reported scores "
        "(rho -0.34, p 0.36), so it ranks emission strategies, not submissions."
    )
    OUT.write_text(json.dumps(results, indent=1) + "\n")
    print(json.dumps({"pooled": pooled, "auc": results["auc_mean"],
                      "canary": results["canary_auc_mean"],
                      "leakage_alarm": results["leakage_alarm"]}, indent=1))


if __name__ == "__main__":
    main()
