#!/usr/bin/env python3
"""H-TILTGRAV (2026-10-29): label-free tilt zero-crossings x gravity horizontal-gradient ridges.

Hypothesis (one sentence): a buried contact or fault that offsets magnetic and density basement
produces a tilt-angle zero crossing (magnetic source edge) that coincides with a strong isostatic
gravity horizontal-gradient ridge (density edge), and these coincident ridges mark unmapped faults.

Stages (run with --stage):
  canary   EXP-1 leakage canary: every feature band ALONE, AUC on the holdout (alarm > 0.90).
  holdout  EXP-2 shared hide-and-recover holdout (vendor/gems57 evaluate + pooled_summary),
           candidate vs matched random-null vs proximity-shell control.
  final    builds the NaN-outside GeoTIFF (scripts/nan_outside_adapter.py) using ALL mapped faults
           only as the apron, and the registry overlap audit (shared gems57.uniqueness).

Budget: 2 experiments (canary, holdout); final build is not an experiment. No weekly slot is selected.
Scores from this script are HOLDOUT-DTI (evaluator named in the output) and are never organizer scores.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))
from gems57 import evaluate_holdout as ev  # noqa: E402
from gems57 import uniqueness as uq  # noqa: E402
import nan_outside_adapter as nao  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"
EVID = ROOT / "evidence"
BUDGET_PER_FOLD = 37654          # = GEMSDOE32 B2 dot count (matched budget)
APRON_PX = 2.0                   # dots must be > 2 px from VISIBLE faults (fold-local)
SPACING_PX = 6
NAME = "karage1-tiltgrav-ridge-sp6-37654-20261029"
NOTE = ("tc-ridge x abs gravity-hgrad, label-free, 6px spacing, 37654 dots. NEGATIVE: below random null. DO NOT SUBMIT.")


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_inputs():
    with rasterio.open(DATA / "sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    with rasterio.open(DATA / "labels.tif") as ds:
        lab = ds.read(1)
    truth_all = (lab == 1) & fp
    with rasterio.open(DATA / "training_features.tif") as ds:
        names = [d.split(" - ")[0] for d in ds.descriptions]
        idx = {n: i + 1 for i, n in enumerate(names)}
    return fp, truth_all, idx, names


def read_band(idx_1based, fp):
    with rasterio.open(DATA / "training_features.tif") as ds:
        a = ds.read(idx_1based).astype(np.float32)
    bad = ~np.isfinite(a) | (np.abs(a) > 1e30)
    valid = fp & ~bad
    a = np.where(valid, a, 0.0).astype(np.float32)
    return a, valid


def pct_rank(values, mask):
    """Percentile rank in (0,1] over masked pixels; zero elsewhere."""
    out = np.zeros(values.shape, np.float32)
    v = values[mask]
    if v.size == 0:
        return out
    r = rankdata(v, method="average").astype(np.float32) / float(v.size)
    out[mask] = r
    return out


def candidate_score(fp, idx):
    """Label-free score in [0,1] on the footprint; uses only the tc and gravity-gradient bands.

    Verified band facts (training_features.tif, 2026-10-29 read): tc is strictly positive
    (2.95..88.57), so a sign-change zero-crossing is impossible; iso_grav_anom_hg is signed
    (-15.44..12.86), so its magnitude |hg| is used. The score is a ridge (3x3 local maximum)
    of tc, weighted by the percentile of |hg|.
    """
    t, tv = read_band(idx["tc"], fp)
    gh, gv = read_band(idx["iso_grav_anom_hg"], fp)
    ridge = tv & (t >= ndimage.maximum_filter(np.where(tv, t, -np.inf), size=3)) & (t > 0)
    r_tc = pct_rank(t, ridge)                    # magnetic edge (tilt/total-curvature ridge)
    r_hg = pct_rank(np.abs(gh), fp & gv)         # gravity horizontal-gradient magnitude
    s = (r_tc * r_hg).astype(np.float32)
    s[~fp] = 0.0
    return np.clip(s, 0.0, 1.0), dict(tc_ridge_pixels=int(ridge.sum()), valid_hg=int((fp & gv).sum()))


def ridge_dots(score, n, mask):
    """Greedy top-n local maxima (3x3) inside mask; fills from non-maxima only if needed."""
    s = np.where(mask, score, 0.0)
    peaks = (s > 0) & (s == ndimage.maximum_filter(s, size=3))
    cand = np.flatnonzero(peaks)
    if cand.size < n:
        cand = np.flatnonzero(s > 0)
    order = cand[np.argsort(-s.ravel()[cand], kind="stable")]
    chosen = order[:n]
    out = np.zeros(s.shape, np.float32)
    out.ravel()[chosen] = 1.0
    return out


def folds(truth_all, fp):
    """Four spatially blocked folds: whole fault segments assigned by centroid quadrant."""
    lab, n = ndimage.label(truth_all, structure=np.ones((3, 3)))
    cy, cx = fp.shape[0] / 2.0, fp.shape[1] / 2.0
    seg_fold = np.full(n + 1, -1, np.int8)
    coms = ndimage.center_of_mass(truth_all, lab, index=np.arange(1, n + 1))
    for i, (y, x) in enumerate(coms, start=1):
        seg_fold[i] = (0 if y < cy else 2) + (0 if x < cx else 1)
    fold_id = seg_fold[lab]
    out = []
    for k in range(4):
        withheld = truth_all & (fold_id == k)
        visible = truth_all & ~withheld
        out.append(dict(k=k, withheld=withheld, visible=visible, segments=int((seg_fold[1:] == k).sum())))
    return out, n


def dist_to(mask):
    return ndimage.distance_transform_edt(~mask)


def stage_canary(fp, truth_all, idx, names, score, folds_):
    rng = np.random.default_rng(20261029)
    results = {}
    feats = {n: None for n in names}
    for name, i in idx.items():
        feats[name] = i
    arms = [(n, feats[n]) for n in names] + [("CANDIDATE_SCORE", None)]
    for name, i in arms:
        if i is None:
            arr, valid = score, fp
        else:
            arr, valid = read_band(i, fp)
        aucs = []
        for f in folds_:
            pos = f["withheld"] & valid
            neg_pool = valid & ~f["visible"] & ~truth_all
            npos = int(pos.sum())
            if npos == 0:
                continue
            ys, xs = np.nonzero(neg_pool)
            pick = rng.choice(ys.size, size=min(200000, ys.size), replace=False)
            ny, nx = ys[pick], xs[pick]
            py, px = np.nonzero(pos)
            X = np.concatenate([arr[py, px], arr[ny, nx]])
            Y = np.concatenate([np.ones(py.size), np.zeros(ny.size)])
            aucs.append(float(roc_auc_score(Y, X)))
        a = float(np.mean(aucs))
        results[name] = dict(auc_mean_over_folds=a, auc_per_fold=aucs,
                             single_feature_alone=True,
                             leakage_alarm=bool(a > 0.90 or a < 0.10))
        log(f"canary {name:28s} AUC={a:.4f} alarm={results[name]['leakage_alarm']}")
    return results


def stage_holdout(fp, truth_all, idx, score, folds_):
    rng = np.random.default_rng(520810)
    terms = {"candidate": [], "random_null": [], "proximity_shell": []}
    per_fold = {}
    total_withheld = 0
    for f in folds_:
        k = f["k"]
        vis = f["visible"]
        withheld = f["withheld"]
        total_withheld += int(withheld.sum())
        d = dist_to(vis)
        apron = d <= APRON_PX
        mask_c = fp & ~apron
        arms = {}
        arms["candidate"] = ridge_dots(score, BUDGET_PER_FOLD, mask_c)
        pool_r = np.flatnonzero(mask_c)
        pr = np.zeros(fp.shape, np.float32)
        pr.ravel()[rng.choice(pool_r, size=BUDGET_PER_FOLD, replace=False)] = 1.0
        arms["random_null"] = pr
        shell = fp & (d >= 3) & (d <= 6) & ~vis
        pool_s = np.flatnonzero(shell)
        ps = np.zeros(fp.shape, np.float32)
        ps.ravel()[rng.choice(pool_s, size=BUDGET_PER_FOLD, replace=False)] = 1.0
        arms["proximity_shell"] = ps
        fold = dict(region=fp, masked_known=vis, truth=withheld, visible=vis)
        per_fold[k] = dict(withheld_positive_pixels=int(withheld.sum()),
                           segments_withheld=f["segments"], emitted={})
        for arm, pred in arms.items():
            res, tb = ev.evaluate(pred.astype(np.float64), fold, fp, block_side=200)
            terms[arm].append(tb)
            per_fold[k]["emitted"][arm] = dict(n_dots=int((pred > 0).sum()), dti_fold=float(res["dti"]))
            log(f"fold {k} {arm:16s} dots={int((pred > 0).sum()):6d} fold_DTI={res['dti']:.5f}")
    stacked = {a: np.sum(np.stack(v), axis=0) for a, v in terms.items()}
    summary = ev.pooled_summary({a: stacked[a] for a in stacked}, draws=1000, seed=520810,
                                candidate="candidate")
    summary["withheld_positive_pixels_total"] = total_withheld
    summary["folds"] = per_fold
    return summary


def spaced_pick(order_idx, shape, n, spacing):
    """Greedy Chebyshev-spacing selection in the given priority order (no two dots closer than spacing)."""
    occ = np.zeros(shape, bool)
    out = np.zeros(shape, np.float32)
    got = 0
    h, w = shape
    r = spacing - 1
    for flat in order_idx:
        y, x = divmod(int(flat), w)
        if occ[y, x]:
            continue
        out[y, x] = 1.0
        occ[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1] = True
        got += 1
        if got >= n:
            break
    return out, got


def stage_spacing(fp, truth_all, idx, score, folds_, spacing=6):
    """EXP-3 (last budgeted experiment): spacing-matched candidate vs spacing-matched random null."""
    rng = np.random.default_rng(7301)
    terms = {"candidate_spaced": [], "random_spaced_null": []}
    per_fold = {}
    for f in folds_:
        k = f["k"]
        vis = f["visible"]
        d = dist_to(vis)
        mask_c = fp & (d > APRON_PX)
        s = np.where(mask_c, score, 0.0)
        order = np.flatnonzero(s > 0)
        order = order[np.argsort(-s.ravel()[order], kind="stable")]
        cand, nc = spaced_pick(order, fp.shape, BUDGET_PER_FOLD, spacing)
        rord = rng.permutation(np.flatnonzero(mask_c))
        rnd, nr = spaced_pick(rord, fp.shape, BUDGET_PER_FOLD, spacing)
        fold = dict(region=fp, masked_known=vis, truth=f["withheld"], visible=vis)
        per_fold[k] = {}
        for arm, pred, n in (("candidate_spaced", cand, nc), ("random_spaced_null", rnd, nr)):
            res, tb = ev.evaluate(pred.astype(np.float64), fold, fp, block_side=200)
            terms[arm].append(tb)
            per_fold[k][arm] = dict(n_dots=int(n), dti_fold=float(res["dti"]))
            log(f"spacing fold {k} {arm:20s} dots={n:6d} fold_DTI={res['dti']:.5f}")
    stacked = {a: np.sum(np.stack(v), axis=0) for a, v in terms.items()}
    summary = ev.pooled_summary(stacked, draws=1000, seed=520810, candidate="candidate_spaced")
    summary["folds"] = per_fold
    summary["spacing_px"] = spacing
    return summary


def stage_final(fp, truth_all, idx, score):
    catalogue = truth_all
    apron = dist_to(catalogue) <= APRON_PX
    mask = fp & ~apron
    s_ = np.where(mask, score, 0.0)
    order = np.flatnonzero(s_ > 0)
    order = order[np.argsort(-s_.ravel()[order], kind="stable")]
    dots, n_got = spaced_pick(order, fp.shape, BUDGET_PER_FOLD, SPACING_PX)
    dots = dots.astype(np.float32)
    out_nan = ROOT / "docs" / "downloads" / f"{NAME}.tif"
    rec = nao.write_nan_outside(out_nan, dots, DATA / "sample_submission.tif", fp,
                                name=NAME, note=NOTE, catalogue=catalogue,
                                metadata=dict(hypothesis="H-TILTGRAV", n_dots=int(dots.sum()), spacing_px=SPACING_PX,
                                       verdict="NEGATIVE / DO NOT SUBMIT"))
    log(f"final tif sha256={rec['sha256']} dots={int(dots.sum())}")
    return rec, dots


def registry_audit(dots, fp):
    """Measured overlap vs the 15 restored registry rasters (shared gems57.uniqueness functions)."""
    import glob
    rows = []
    mine = np.where(fp, dots, 0).astype(np.float32)
    for f in sorted(glob.glob(str(DATA / "registry" / "*.tif"))):
        with rasterio.open(f) as ds:
            theirs = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
        theirs = np.where(fp, theirs, 0).astype(np.float32)
        fwd = uq.dot_overlap(mine, theirs)
        rev = uq.dot_overlap(theirs, mine)
        sr = uq.surface_rho(mine, theirs, fp)
        rows.append(dict(registry_file=Path(f).name, my_dots_within_3px_of_theirs=round(fwd, 6),
                         their_dots_within_3px_of_mine=round(rev, 6),
                         spearman_full_footprint=sr["spearman_full_footprint"],
                         jaccard_dot_sets=sr["jaccard_dot_sets"],
                         duplicate_by_overlap=bool(fwd > uq.OVERLAP_LIMIT),
                         duplicate_by_rho=bool(sr["spearman_full_footprint"] is not None
                                               and sr["spearman_full_footprint"] > uq.RHO_LIMIT)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, choices=["canary", "holdout", "spacing", "final", "all"])
    args = ap.parse_args()
    fp, truth_all, idx, names = load_inputs()
    log(f"footprint={int(fp.sum())} truth(all mapped faults)={int(truth_all.sum())} bands={len(idx)}")
    score, meta = candidate_score(fp, idx)
    log(f"candidate score: {meta}, max={float(score.max()):.4f}, nonzero={int((score > 0).sum())}")
    folds_, nseg = folds(truth_all, fp)
    log(f"fault segments={nseg}; per-fold withheld={[int(f['withheld'].sum()) for f in folds_]}")
    EVID.mkdir(exist_ok=True)
    run = dict(hypothesis="H-TILTGRAV", evaluator="gems57-pooled-hide-v2 (vendor/gems57/evaluate_holdout.py)",
               evaluator_implementation_sha256=ev.implementation_hashes(),
               candidate_meta=meta, fault_segments=nseg,
               protocol="whole-segment fold assignment by centroid quadrant; candidate label-free; "
                        "fold-local apron = visible faults (pixel-exact mask, 2 px dot exclusion); "
                        "truth = withheld segments only",
               budget_per_fold=BUDGET_PER_FOLD)
    if args.stage in ("canary", "all"):
        run["exp1_canary"] = stage_canary(fp, truth_all, idx, names, score, folds_)
        (EVID / "tiltgrav_exp1_canary_20261029.json").write_text(json.dumps(run, indent=2, default=float) + "\n")
    if args.stage in ("holdout", "all"):
        run["exp2_holdout"] = stage_holdout(fp, truth_all, idx, score, folds_)
        (EVID / "tiltgrav_exp2_holdout_20261029.json").write_text(json.dumps(run, indent=2, default=float) + "\n")
    if args.stage == "spacing":
        run["exp3_spacing_sweep"] = stage_spacing(fp, truth_all, idx, score, folds_)
        (EVID / "tiltgrav_exp3_spacing_20261029.json").write_text(json.dumps(run, indent=2, default=float) + "\n")
    if args.stage in ("final", "all"):
        rec, dots = stage_final(fp, truth_all, idx, score)
        run["final_receipt"] = rec
        run["registry_audit"] = registry_audit(dots, fp)
        (EVID / "tiltgrav_final_20261029.json").write_text(json.dumps(run, indent=2, default=float) + "\n")
    log("done")


if __name__ == "__main__":
    main()
