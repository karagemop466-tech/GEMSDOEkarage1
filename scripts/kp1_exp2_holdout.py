#!/usr/bin/env python3
"""EXP2 — spatially blocked instrument calibration + physics-only fault detector.

Three questions, in the order the protocol requires them:

1. **Leakage canary** (protocol rule 4).  Each physics plane alone, scored on the
   withheld quadrant.  AUC > 0.90 would mean the plane is carrying the labels.

2. **Instrument calibration** — the question earlier sessions never asked.  If a
   holdout instrument is to justify promoting a *new* candidate, it must at least
   reproduce the ordering that the organizer has already reported for the nine
   focus files.  Nine live scores are known (0.2449 … 0.2778).  This script scores
   all nine pinned registry rasters on the same hide-and-recover folds and reports
   the rank correlation with those known scores.  A negative correlation means the
   instrument measures the *opposite* population to the leaderboard (it rewards
   recovering already-mapped traces, which earns nothing in the real metric).

3. **Candidate detector.**  Gradient-boosted classifier trained on
   leave-one-quadrant-out folds to separate mapped faults from background using
   *physics-only* planes (no catalogue-derived predictor), then emitted by the
   exact DTI marginal-acceptance rule in ``vendor/gems57/emit.py``.  Compared at a
   fixed dot budget against: uniform random, spacing-matched random, and the
   pinned GEMSDOE32 B2 geometry.

All DTI numbers are HOLDOUT-DTI under evaluator ``gems57-pooled-hide-v2`` with
paired spatial-cluster bootstrap CIs.  None of them is a leaderboard score.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import spearmanr
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT))

from gems57 import emit, evaluate_holdout                        # noqa: E402
from gems57.holdout import quadrant_ids                          # noqa: E402
from gems57.uniqueness import dot_overlap                        # noqa: E402
from scripts import kp1_data as D                                # noqa: E402
from scripts import kp1_planes as P                              # noqa: E402
from scripts.kp1_exp1_forensics import FILES, SCORES, load       # noqa: E402

FEATURES = ["tmi_hg", "tmi_vg", "tc", "iso_grav_anom_hg", "iso_grav_anom_slope",
            "det_elev_slope", "geod_2ndinv", "geod_shearrate", "ieq", "deq",
            "cond_surf", "depth_to_base_surf", "curv2", "base_edge", "elev_ridge3",
            "lidar_step", "lidar_lapneg", "lidar_coh", "lidar_ex", "lidar_relief",
            "up150_grad", "ThK", "UK", "UTh", "spring_kde", "spring_hot", "vent_kde"]
BUDGET = 37654          # the champion's dot count, used to hold budget fixed
MIN_SEP_PX = 4.0        # > kernel radius: no two dots can share a truth cell's credit
SEED = 20261031


def quadrants(fp: np.ndarray) -> np.ndarray:
    return quadrant_ids(fp)


def _stack(rows: slice) -> np.ndarray:
    return np.stack([np.asarray(P.load(n)[rows], np.float32) for n in FEATURES], axis=-1)


def fit_predict_oof(cat: np.ndarray, fp: np.ndarray, quad: np.ndarray,
                    rng: np.random.Generator) -> tuple[np.ndarray, dict]:
    """Leave-one-quadrant-out classifier; returns the out-of-fold surface."""
    d_cat = ndi.distance_transform_edt(~cat)
    bg_ok = fp & (d_cat > 8)
    oof = np.zeros(fp.shape, np.float32)
    info = {}
    for f in range(4):
        test_q = quad == f
        train_hard = fp & ~test_q
        pos = np.flatnonzero((cat & train_hard).ravel())
        neg_pool = np.flatnonzero(bg_ok.ravel())
        neg = rng.choice(neg_pool, size=min(250_000, neg_pool.size), replace=False)
        idx = np.concatenate([pos, neg])
        y_r = np.concatenate([np.ones(pos.size, np.int8), np.zeros(neg.size, np.int8)])
        X = _stack(()).reshape(-1, len(FEATURES))[idx]
        clf = HistGradientBoostingClassifier(
            max_iter=250, learning_rate=0.06, max_leaf_nodes=63,
            min_samples_leaf=40, l2_regularization=1.0, random_state=SEED)
        clf.fit(X, y_r)
        del X
        # OOF prediction on the held-out quadrant, in row blocks
        q_rows = np.flatnonzero(test_q.any(axis=1))
        for y0 in range(q_rows.min(), q_rows.max() + 1, 128):
            sl = slice(y0, min(y0 + 128, fp.shape[0]))
            Xb = _stack(sl).reshape(-1, len(FEATURES))
            pb = clf.predict_proba(Xb)[:, 1].astype(np.float32).reshape(sl.stop - sl.start, fp.shape[1])
            pb[~test_q[sl]] = 0.0
            oof[sl] = pb
            del Xb, pb
        info[f"fold{f}"] = dict(train_positives=int(pos.size), train_negatives=int(neg.size),
                                quad_cells=int(test_q.sum()))
        print(f"[exp2] fold {f} trained ({pos.size} pos / {neg.size} neg)", flush=True)
    return oof, info


def spaced_random(allowed: np.ndarray, n: int, rng: np.random.Generator,
                  min_sep: float = MIN_SEP_PX) -> np.ndarray:
    """Spacing-matched random dots: uniform sampling with a hard exclusion disc."""
    ys, xs = np.nonzero(allowed)
    order = rng.permutation(ys.size)
    out = np.zeros(allowed.shape, bool)
    r = int(np.ceil(min_sep))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disc = (yy * yy + xx * xx) <= min_sep ** 2
    H, W = allowed.shape
    taken = 0
    for k in order:
        y, x = int(ys[k]), int(xs[k])
        if out[y, x]:
            continue
        out[y, x] = True
        taken += 1
        y0, y1 = max(0, y - r), min(H, y + r + 1)
        x0, x1 = max(0, x - r), min(W, x + r + 1)
        out[y0:y1, x0:x1] &= ~disc[y0 - (y - r):y1 - (y - r), x0 - (x - r):x1 - (x - r)]
        if taken >= n:
            break
    return out


def uniform_random(allowed: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    idx = np.flatnonzero(allowed.ravel())
    pick = rng.choice(idx, size=min(n, idx.size), replace=False)
    out = np.zeros(allowed.size, bool)
    out[pick] = True
    return out.reshape(allowed.shape)


def main() -> None:
    pins = D.verify_inputs()
    fp = D.footprint()
    cat = D.catalogue()
    quad = quadrants(fp)
    rng = np.random.default_rng(SEED)
    P.build()
    d_cat = ndi.distance_transform_edt(~cat)

    # ------------------------------------------------------------------ canary
    canary = {}
    for f in range(4):
        test_q = quad == f
        held = cat & test_q
        bg_rows = np.flatnonzero((fp & test_q & ~ndi.binary_dilation(cat, iterations=8)).ravel())
        bg = rng.choice(bg_rows, size=min(120_000, bg_rows.size), replace=False)
        pos = np.flatnonzero(held.ravel())
        idx = np.concatenate([pos, bg])
        y = np.zeros(fp.size, np.int8)
        y[pos] = 1
        for name in FEATURES:
            x = np.asarray(P.load(name), np.float32).ravel()[idx]
            canary.setdefault(name, []).append(float(roc_auc_score(y[idx], x)))
    canary = {k: dict(auc_mean=round(float(np.mean(v)), 4), auc_by_fold=[round(a, 4) for a in v],
                      leakage_alarm=bool(np.mean(v) > 0.90)) for k, v in canary.items()}
    print("[exp2] canary max", max(v["auc_mean"] for v in canary.values()), flush=True)

    # ------------------------------------------------- instrument calibration
    # score the nine pinned registry rasters on the same folds
    registry_terms = {}
    for site in FILES:
        a = load(site)
        terms = []
        for f in range(4):
            region = quad == f
            visible = cat & ~region
            fold = dict(region=region & fp, visible=visible, masked_known=visible,
                        truth=cat)
            res, t = evaluate_holdout.evaluate(a * fp, fold, fp)
            terms.append(t)
        registry_terms[site] = np.stack(terms).sum(axis=0)
    reg_scores = np.array([float(evaluate_holdout.from_terms(registry_terms[s].sum(axis=0)))
                           for s in FILES])
    known = np.array([SCORES[s] for s in FILES])
    calibration = dict(
        evaluator=evaluate_holdout.VERSION,
        holdout_dti={s: round(float(reg_scores[i]), 6) for i, s in enumerate(FILES)},
        known_user_reported_scores={s: SCORES[s] for s in FILES},
        spearman_instrument_vs_known=round(float(spearmanr(reg_scores, known).statistic), 4),
        n=len(FILES),
        interpretation=("A near-zero or negative rank correlation means this instrument does not "
                        "measure the population the leaderboard scores (expert-identified faults "
                        "absent from the catalogue); it measures recovery of already-mapped traces."),
    )
    print("[exp2] instrument calibration", calibration["spearman_instrument_vs_known"], flush=True)

    # ------------------------------------------------------- candidate detector
    oof, model_info = fit_predict_oof(cat, fp, quad, rng)
    np.save(D.CACHE / "kp1_oof_surface.npy", oof)
    allowed = fp & (d_cat > 2.0)
    alloc = emit.allocate_by_marginal_bar(oof, allowed, k_truth=float(cat.sum()),
                                          floor=0.0, max_dots=BUDGET)
    cand = alloc.emitted
    print("[exp2] emitted", alloc.n_dots, "dots; surrogate DTI", round(alloc.surrogate_dti, 4), flush=True)

    arms = {
        "candidate_physics_gbm": cand,
        "uniform_random_matched": uniform_random(allowed, alloc.n_dots, rng),
        "spaced_random_matched": spaced_random(allowed, alloc.n_dots, rng),
        "registry_GEMSDOE32_B2": (load("GEMSDOE32") > 0) & fp,
    }
    terms = {}
    for name, pred in arms.items():
        per_fold = []
        for f in range(4):
            region = quad == f
            visible = cat & ~region
            fold = dict(region=region & fp, visible=visible, masked_known=visible,
                        truth=cat)
            _, t = evaluate_holdout.evaluate(pred.astype(np.float32) * fp, fold, fp)
            per_fold.append(t)
        terms[name] = np.stack(per_fold).sum(axis=0)
    summary = evaluate_holdout.pooled_summary(terms, draws=400, candidate="candidate_physics_gbm")

    # ------------------------------------------------------------- budget sweep
    sweep = {}
    for cap in (10_000, 20_000, 30_000, 50_000, 70_000):
        a = emit.allocate_by_marginal_bar(oof, allowed, k_truth=float(cat.sum()),
                                          floor=0.0, max_dots=cap)
        per_fold = []
        for f in range(4):
            region = quad == f
            visible = cat & ~region
            fold = dict(region=region & fp, visible=visible, masked_known=visible, truth=cat)
            _, t = evaluate_holdout.evaluate(a.emitted.astype(np.float32) * fp, fold, fp)
            per_fold.append(t)
        tt = np.stack(per_fold).sum(axis=0)
        sweep[str(cap)] = dict(n_dots=int(a.n_dots),
                               dti=round(float(evaluate_holdout.from_terms(tt.sum(axis=0))), 6))
    print("[exp2] sweep", sweep, flush=True)

    np.save(D.CACHE / "kp1_candidate_dots.npy", cand)
    payload = dict(
        evidence_class="HOLDOUT-DTI",
        evaluator=evaluate_holdout.VERSION,
        lane="H-KP1 (K-PROXY-DETECT)",
        alpha=0.2, beta=0.8, kernel_radius_m=300,
        folds="leave-one-quadrant-out, 4 fixed quadrants, catalogue segments of the held "
              "quadrant withheld from training; no buffer erosion inside the scored quadrant",
        features=FEATURES,
        feature_provenance="physics-only; no plane is derived from the fault catalogue",
        leakage_canary=canary,
        instrument_calibration=calibration,
        model=model_info,
        emission=dict(rule="vendor gems57.emit.allocate_by_marginal_bar (exact two-sided DTI test)",
                      k_truth=int(cat.sum()), dot_cap=BUDGET, n_dots=int(alloc.n_dots),
                      min_sep_search_px=MIN_SEP_PX, forbidden="within 2 px of the mapped catalogue"),
        arms=summary,
        budget_sweep=sweep,
        pins=pins,
        caveat=("HOLDOUT-DTI measures recovery of withheld *mapped* traces. It is not the "
                "organizer metric and, per instrument_calibration, it is not even positively "
                "rank-correlated with the known leaderboard ordering of the nine focus files."),
    )
    out = D.write_report("kp1_exp2_holdout.json", payload)
    print("wrote", out)
    print(json.dumps(summary["scores"], indent=1))
    print(json.dumps(summary["paired_differences"], indent=1))


if __name__ == "__main__":
    main()
