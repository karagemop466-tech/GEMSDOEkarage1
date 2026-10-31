#!/usr/bin/env python3
"""Session arena/55dc7b72 (31 Oct 2026): catalogue-halo-aware pixel model, three experiments.

Lane (chosen by this session; the prompt's "method paragraph" is absent in the
record, so the owner must confirm it): H-K1-CATEXCL -- a gradient-boosted pixel
classifier on catalogue-free features, cross-fitted over spatially blocked folds,
with a catalogue-halo exclusion radius r and a probability threshold t that are
both chosen on the hide-and-recover holdout.

Scoring rules, all from primary sources (see knowledge/review-arena-55dc7b72-20261031.md):
* Distance-weighted Tversky index, alpha=0.2, beta=0.8, triangular kernel R=3 px
  (300 m at 100 m): DrivenData competition page 967 (fetched 31 Oct 2026).
* Pixels on KNOWN USGS/INGENIOUS faults are masked from evaluation and do not
  count toward penalty terms: DrivenData staff, community topic 11516, post of
  16 Sep 2026 (fetched 31 Oct 2026). Halo pixels NEXT to a known fault are NOT
  masked and are scored as false positives unless a new fault is within 3 px.
* The scorer is the shared vendored implementation ``gems57.metric.dti_exact``
  (verified against brute force in tests/test_metric.py). It is reused, not forked.

Output labels: every holdout number is HOLDOUT-DTI (evaluator gems57 metric, withheld
positives reported, bootstrap 95% CI over spatial cells). No number here is an
ORGANIZER-CONFIRMED score; no number here is a leaderboard estimate.

Usage:  python scripts/run_catexcl_20261031.py canary|holdout|build
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "src"))

from gems57.metric import dti_exact  # noqa: E402  (shared official implementation)

DATA = ROOT / "data"
CACHE = ROOT / ".cache" / "karage1_catexcl_20261031"
EVID = ROOT / "evidence"
DOWN = ROOT / "docs" / "downloads"
SEED = 20261031
BUFFER_PX = 5          # buffer between withheld segments and training pixels
N_POS_MAX = 40_000
N_NEG_MAX = 160_000
HALO_GRID = (0, 1, 2, 3, 4, 6)
RAND_SEEDS = (0, 1, 2, 3, 4)
SPARSE_N = (5_000, 10_000, 20_000, 37_654, 60_000, 100_000, 300_000)
ALPHA, BETA = 0.2, 0.8
N_FEAT_RAW = 19
DERIVED_SRC = {"grad_mag_mag_anom": 1, "grad_mag_tmi": 14, "grad_mag_iso_grav_anom": 13,
               "grad_mag_det_elev": 12, "grad_mag_depth_to_base": 15}


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def footprint_and_grid():
    with rasterio.open(DATA / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
        tr = tuple(ds.transform)[:6]
        crs = ds.crs.to_string()
        shape = (ds.height, ds.width)
    cat = rasterio.open(DATA / "labels.tif").read(1) == 1
    return foot, tr, crs, shape, cat


def build_feature_cache(foot: np.ndarray, shape) -> tuple[Path, list[str]]:
    """Write a float32 (25, H, W) memmap: 19 raw bands + 5 gradient + 1 texture.

    Only catalogue-free inputs are used: the 19 mirrored feature bands and filters of them.
    Sentinel values (< -1e38) become NaN, outside the sample footprint is NaN.
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "feat25.npy"
    names_path = CACHE / "feat25_names.json"
    if path.exists() and names_path.exists():
        return path, json.loads(names_path.read_text())
    H, W = shape
    names = []
    with rasterio.open(DATA / "training_features.tif") as ds:
        for b in range(1, N_FEAT_RAW + 1):
            names.append(ds.descriptions[b - 1].split(" - ")[0])
        mm = np.lib.format.open_memmap(path, mode="w+", dtype=np.float32, shape=(25, H, W))
        for b in range(1, N_FEAT_RAW + 1):
            a = ds.read(b).astype(np.float32)
            a[a < -1e38] = np.nan
            a[~foot] = np.nan
            mm[b - 1] = a
        mm.flush()
    for name in DERIVED_SRC:
        names.append(name)
    names.append("tex_std5_tmi")
    with_names = {"names": names}  # written after derived for consistency
    mm = np.load(path, mmap_mode="r+")
    for j, (name, src) in enumerate(DERIVED_SRC.items()):
        a = np.array(mm[src - 1], dtype=np.float32)
        med = np.nanmedian(a[foot])
        f = np.where(np.isnan(a), med, a).astype(np.float32)
        f[~foot] = 0.0
        gx = ndi.sobel(f, axis=1)
        gy = ndi.sobel(f, axis=0)
        g = np.hypot(gx, gy).astype(np.float32)
        g[~foot] = np.nan
        mm[N_FEAT_RAW + j] = g
        del a, f, gx, gy, g
    a = np.array(mm[13], dtype=np.float32)   # tmi
    med = np.nanmedian(a[foot])
    f = np.where(np.isnan(a), med, a).astype(np.float32)
    f[~foot] = 0.0
    m1 = ndi.uniform_filter(f, 5)
    m2 = ndi.uniform_filter(f * f, 5)
    s = np.sqrt(np.maximum(m2 - m1 * m1, 0)).astype(np.float32)
    s[~foot] = np.nan
    mm[24] = s
    mm.flush()
    del mm
    names_path.write_text(json.dumps(with_names, indent=1))
    return path, names


def _quadrant_index(shape) -> np.ndarray:
    H, W = shape
    rr = np.arange(H)[:, None]
    cc = np.arange(W)[None, :]
    return (2 * (rr >= H // 2) + (cc >= W // 2)).astype(np.int8) * np.ones((H, W), np.int8)


def _cells4x4(shape) -> np.ndarray:
    """16 spatial cells (4x4); each quadrant is 2x2 of these."""
    H, W = shape
    rr = np.arange(H)[:, None] * 4 // H
    cc = np.arange(W)[None, :] * 4 // W
    return (np.minimum(rr, 3) * 4 + np.minimum(cc, 3)).astype(np.int8) * np.ones((H, W), np.int8)


def split_folds(cat: np.ndarray, shape):
    """Assign whole 8-connected catalogue segments to the quadrant of their centroid."""
    lab, n = ndi.label(cat, structure=np.ones((3, 3), dtype=int))
    H, W = shape
    cents = ndi.center_of_mass(cat, lab, index=np.arange(1, n + 1))
    quad_of_seg = np.array([2 * (r >= H // 2) + (c >= W // 2) for r, c in cents], dtype=np.int64)
    return lab, n, quad_of_seg


def _take(mm, rows, cols):
    return np.asarray(mm[:, rows, cols], dtype=np.float32).T


def train_model(mm, foot, cat, lab, seg_ids_out, domain, seed):
    """Train on visible catalogue (buffered away from withheld segments) vs far background."""
    import lightgbm as lgb

    rng = np.random.default_rng(seed)
    withheld = np.isin(lab, seg_ids_out) if seg_ids_out.size else np.zeros_like(cat)
    visible = cat & ~withheld
    buf = ndi.distance_transform_edt(~withheld) <= BUFFER_PX if withheld.any() else np.zeros_like(cat)
    dist_cat = ndi.distance_transform_edt(~cat)
    pos_mask = visible & foot & ~buf
    neg_mask = foot & ~domain & ~buf & (dist_cat > BUFFER_PX)
    pr, pc = np.nonzero(pos_mask)
    nr, nc = np.nonzero(neg_mask)
    if pr.size > N_POS_MAX:
        sel = rng.choice(pr.size, N_POS_MAX, replace=False)
        pr, pc = pr[sel], pc[sel]
    if nr.size > N_NEG_MAX:
        sel = rng.choice(nr.size, N_NEG_MAX, replace=False)
        nr, nc = nr[sel], nc[sel]
    X = np.vstack([_take(mm, pr, pc), _take(mm, nr, nc)])
    y = np.concatenate([np.ones(pr.size), np.zeros(nr.size)]).astype(np.int8)
    clf = lgb.LGBMClassifier(
        n_estimators=300, learning_rate=0.05, num_leaves=63, min_child_samples=100,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8, reg_lambda=1.0,
        random_state=seed, n_jobs=2, verbose=-1,
    )
    clf.fit(X, y)
    info = {"n_pos_train": int(pr.size), "n_neg_train": int(nr.size),
            "n_withheld_pixels": int(withheld.sum()), "n_buffer_pixels": int(buf.sum())}
    return clf, info


def predict_domain(clf, mm, domain) -> np.ndarray:
    H, W = domain.shape
    out = np.zeros((H, W), np.float32)
    rows, cols = np.nonzero(domain)
    step = 300_000
    for s in range(0, rows.size, step):
        r, c = rows[s:s + step], cols[s:s + step]
        out[r, c] = clf.predict_proba(_take(mm, r, c))[:, 1].astype(np.float32)
    return out


def auc_canary(mm, names, foot, cat, withheld_all, domain_all, n_neg=200_000, seed=7):
    """Single-feature leakage canary on the holdout: withheld fault pixels vs far background."""
    rng = np.random.default_rng(seed)
    dist_cat = ndi.distance_transform_edt(~cat)
    pos = withheld_all & domain_all & foot
    neg = domain_all & foot & ~withheld_all & (dist_cat > 10)
    pr, pc = np.nonzero(pos)
    nr, nc = np.nonzero(neg)
    nsel = rng.choice(nr.size, min(n_neg, nr.size), replace=False)
    nr, nc = nr[nsel], nc[nsel]
    res = []
    for j, name in enumerate(names):
        xp = np.asarray(mm[j][pr, pc], np.float64)
        xn = np.asarray(mm[j][nr, nc], np.float64)
        ok_p, ok_n = np.isfinite(xp), np.isfinite(xn)
        xp, xn = xp[ok_p], xn[ok_n]
        y = np.r_[np.ones(xp.size), np.zeros(xn.size)]
        s = np.r_[xp, xn]
        auc = float(roc_auc_score(y, s))
        res.append({"feature": name, "auc_signed": round(auc, 5),
                    "auc_direction_free": round(max(auc, 1 - auc), 5),
                    "n_pos": int(xp.size), "n_neg": int(xn.size)})
    return res


def halo_excluded(dist_vis: np.ndarray, r: float) -> np.ndarray:
    return dist_vis <= r


def score_fold(p, withheld_q, visible, dom, halo_r, thr, dist_vis):
    """Official DTI on one quadrant with organizer masking of visible known faults."""
    pe = np.where(halo_excluded(dist_vis, halo_r), 0.0, p).astype(np.float64)
    if thr > 0:
        pe = np.where(pe >= thr, pe, 0.0)
    res = dti_exact(pe, withheld_q, valid=dom, known=visible)
    return res, pe


def cmd_canary() -> int:
    foot, tr, crs, shape, cat = footprint_and_grid()
    path, names = build_feature_cache(foot, shape)
    mm = np.load(path, mmap_mode="r")
    lab, n_seg, quad_of_seg = split_folds(cat, shape)
    quad = _quadrant_index(shape)
    withheld_all = np.zeros(shape, bool)
    # fold-1 holdout is used for the canary: withhold quadrant 0 segments only
    seg_q0 = np.nonzero(quad_of_seg == 0)[0] + 1
    withheld_all = np.isin(lab, seg_q0)
    domain_all = foot & (quad == 0)
    t0 = time.time()
    res = auc_canary(mm, names, foot, cat, withheld_all, domain_all)
    worst = max(res, key=lambda d: d["auc_direction_free"])
    stop = worst["auc_direction_free"] > 0.90
    doc = {
        "experiment": "E1 leakage canary (single feature alone on holdout)",
        "label": "HOLDOUT-DTI-free diagnostic: AUC of single features; not a score",
        "ceiling_auc": 0.90, "stop_triggered": bool(stop),
        "n_segments": int(n_seg), "withheld_segments_quadrant0": int(seg_q0.size),
        "features": res, "worst": worst, "seconds": round(time.time() - t0, 1),
        "feature_stack_sha256": _sha(path),
    }
    (EVID / "catexcl_e1_canary_20261031.json").write_text(json.dumps(doc, indent=2) + "\n")
    print(json.dumps({"stop": stop, "worst": worst}, indent=1))
    return 2 if stop else 0


def cmd_holdout() -> int:
    foot, tr, crs, shape, cat = footprint_and_grid()
    path, names = build_feature_cache(foot, shape)
    mm = np.load(path, mmap_mode="r")
    lab, n_seg, quad_of_seg = split_folds(cat, shape)
    quad = _quadrant_index(shape)
    cells = _cells4x4(shape)
    t0 = time.time()
    folds = []
    pred_store = {}
    for q in range(4):
        seg_ids = np.nonzero(quad_of_seg == q)[0] + 1
        withheld = np.isin(lab, seg_ids)
        visible = cat & ~withheld
        dom = foot & (quad == q)
        clf, info = train_model(mm, foot, cat, lab, seg_ids, dom, SEED + q)
        p = predict_domain(clf, mm, dom)
        dist_vis = ndi.distance_transform_edt(~visible).astype(np.float32)
        pred_store[q] = (p, withheld & dom, visible, dom, dist_vis)
        folds.append({"quadrant": q, "withheld_segments": int(seg_ids.size),
                      "withheld_pixels_in_domain": int((withheld & dom).sum()),
                      "domain_pixels": int(dom.sum()), **info})
        print(f"fold {q}: {info} withheld_px={folds[-1]['withheld_pixels_in_domain']}", flush=True)
    # ---- grid search over halo radius r and threshold t, pooled across folds ----
    all_p = np.concatenate([pred_store[q][0][pred_store[q][3]] for q in range(4)])
    thr_grid = [0.0] + [float(np.quantile(all_p[all_p > 0], qq)) for qq in (0.5, 0.8, 0.9, 0.95, 0.98, 0.99)]
    grid = []
    for r in HALO_GRID:
        for t in thr_grid:
            tp = fp = fn = 0.0
            ndots = 0
            for q in range(4):
                p, wq, vis, dom, dv = pred_store[q]
                res, pe = score_fold(p, wq, vis, dom, r, t, dv)
                tp += res["tp"]; fp += res["fp"]; fn += res["fn"]
                ndots += int((pe > 0).sum())
            d = tp + ALPHA * fp + BETA * fn
            grid.append({"halo_r_px": r, "threshold": round(t, 6), "tp": tp, "fp": fp, "fn": fn,
                         "dti_pooled": tp / d if d > 0 else 0.0, "n_dots": ndots})
    grid.sort(key=lambda g: -g["dti_pooled"])
    best = grid[0]
    print("best", best, flush=True)
    # ---- cell-level bootstrap CI for best and random placement control ----
    parts = {"p": [], "t": [], "v": [], "k": []}
    rand_stats = []
    for q in range(4):
        p, wq, vis, dom, dv = pred_store[q]
        pe_full = np.where(halo_excluded(dv, best["halo_r_px"]), 0.0, p)
        if best["threshold"] > 0:
            pe_full = np.where(pe_full >= best["threshold"], pe_full, 0.0)
        n_dots_q = int((pe_full > 0).sum())
        active = dom & ~vis
        cand = np.nonzero(active)
        for seed in RAND_SEEDS:
            rng = np.random.default_rng(seed + 100 * q)
            pick = rng.choice(cand[0].size, min(n_dots_q, cand[0].size), replace=False)
            rp = np.zeros(shape, np.float64)
            rp[cand[0][pick], cand[1][pick]] = 1.0
            rr = dti_exact(rp, wq, valid=dom, known=vis)
            rand_stats.append({"quadrant": q, "seed": seed, "dti": rr["dti"], "tp": rr["tp"],
                               "fp": rr["fp"], "fn": rr["fn"]})
    # ---- sparse-N ranking control: top-N ACTIVE model pixels vs N random ACTIVE pixels ----
    sparse = []
    for N in SPARSE_N:
        nq = max(1, N // 4)
        m_tp = m_fp = m_fn = 0.0
        r_runs = []
        for q in range(4):
            p, wq, vis, dom, dv = pred_store[q]
            active = dom & ~vis
            pa = np.where(halo_excluded(dv, best["halo_r_px"]) | ~active, 0.0, p).astype(np.float64)
            flat = pa.ravel()
            k = min(nq, int((flat > 0).sum()))
            top = np.argpartition(-flat, k - 1)[:k] if k > 0 else np.array([], int)
            mp = np.zeros(flat.shape, np.float64)
            mp[top] = flat[top]
            mp = mp.reshape(shape)
            rr = dti_exact(mp, wq, valid=dom, known=vis)
            m_tp += rr["tp"]; m_fp += rr["fp"]; m_fn += rr["fn"]
        for seed in RAND_SEEDS:
            r_tp = r_fp = r_fn = 0.0
            for q in range(4):
                p, wq, vis, dom, dv = pred_store[q]
                active = dom & ~vis
                cand = np.nonzero(active)
                rng = np.random.default_rng(1000 * seed + q)
                pick = rng.choice(cand[0].size, min(nq, cand[0].size), replace=False)
                rp = np.zeros(shape, np.float64)
                rp[cand[0][pick], cand[1][pick]] = 1.0
                rr = dti_exact(rp, wq, valid=dom, known=vis)
                r_tp += rr["tp"]; r_fp += rr["fp"]; r_fn += rr["fn"]
            d = r_tp + ALPHA * r_fp + BETA * r_fn
            r_runs.append(r_tp / d if d > 0 else 0.0)
        d = m_tp + ALPHA * m_fp + BETA * m_fn
        m_dti = m_tp / d if d > 0 else 0.0
        sparse.append({"n_dots_total": nq * 4, "model_top_n_dti": m_dti,
                       "random_mean_dti": float(np.mean(r_runs)), "random_sd_dti": float(np.std(r_runs)),
                       "model_minus_random": m_dti - float(np.mean(r_runs))})
        print("sparse", sparse[-1], flush=True)
    # ---- holdout AUC of the model surface over active pixels (diagnostic only) ----
    from sklearn.metrics import roc_auc_score as _auc
    rng_a = np.random.default_rng(5)
    ys, ss = [], []
    dist_cat_full = ndi.distance_transform_edt(~cat)
    for q in range(4):
        p, wq, vis, dom, dv = pred_store[q]
        active = dom & ~vis
        pos_idx = np.nonzero(wq & active)
        neg_m = active & ~wq & (dist_cat_full > 10)
        neg_idx = np.nonzero(neg_m)
        sel = rng_a.choice(neg_idx[0].size, min(60000, neg_idx[0].size), replace=False)
        ys.append(np.ones(pos_idx[0].size)); ss.append(p[pos_idx])
        ys.append(np.zeros(sel.size)); ss.append(p[neg_idx[0][sel], neg_idx[1][sel]])
    holdout_auc = float(_auc(np.concatenate(ys), np.concatenate(ss)))
    print("holdout AUC (model surface, active pixels):", round(holdout_auc, 4), flush=True)
    best_fold_res = []
    for c in range(16):
        cell_mask = cells == c
        tot_tp = tot_fp = tot_fn = 0.0
        # use the best configuration on each quadrant, cell-restricted masks
        for q in range(4):
            p, wq, vis, dom, dv = pred_store[q]
            pe = np.where(halo_excluded(dv, best["halo_r_px"]), 0.0, p).astype(np.float64)
            if best["threshold"] > 0:
                pe = np.where(pe >= best["threshold"], pe, 0.0)
            cm = cell_mask & dom
            if not cm.any():
                continue
            rr = dti_exact(np.where(cm, pe, 0.0), wq & cm, valid=cm, known=vis & cm)
            tot_tp += rr["tp"]; tot_fp += rr["fp"]; tot_fn += rr["fn"]
        best_fold_res.append((tot_tp, tot_fp, tot_fn))
    arr = np.array(best_fold_res, float)
    vals = []
    rng = np.random.default_rng(13)
    for _ in range(2000):
        idx = rng.integers(0, 16, 16)
        tp, fp, fn = arr[idx].sum(axis=0)
        d = tp + ALPHA * fp + BETA * fn
        vals.append(tp / d if d > 0 else 0.0)
    ci = [float(np.percentile(vals, 2.5)), float(np.percentile(vals, 97.5))]
    rand_dti = [s["dti"] for s in rand_stats]
    n_withheld_total = int(sum(f["withheld_pixels_in_domain"] for f in folds))
    doc = {
        "experiment": "E2 hide-and-recover holdout: candidate vs random-placement control",
        "label": "HOLDOUT-DTI (evaluator: gems57.metric.dti_exact, organizer masking of visible known faults; pooled over 4 spatial quadrants)",
        "withheld_positives_pixels": n_withheld_total,
        "best_config": best,
        "ci95_cell_bootstrap_approx": {"low": ci[0], "high": ci[1],
                                       "note": "16 spatial cells, each cell-restricted; approximate"},
        "random_control": {"mean_dti": float(np.mean(rand_dti)), "sd_dti": float(np.std(rand_dti)),
                           "n_seeds": len(rand_dti), "per_run": rand_stats},
        "grid": grid, "folds": folds, "seed": SEED,
        "sparse_n_control": sparse, "holdout_auc_model_surface": holdout_auc,
        "thresholds_tested": thr_grid, "halo_grid": list(HALO_GRID),
        "seconds": round(time.time() - t0, 1),
        "feature_stack_sha256": _sha(path),
        "caveats": [
            "Holdout targets catalogue segments, not organizer new faults; it is a proxy.",
            "Halo and threshold are selected on the same holdout (in-sample selection).",
            "Quadrant boundary effects on the 3-px kernel are ignored (predictions only inside each quadrant).",
        ],
    }
    (EVID / "catexcl_e2_holdout_20261031.json").write_text(json.dumps(doc, indent=2) + "\n")
    print(json.dumps({k: doc[k] for k in ("best_config", "ci95_cell_bootstrap_approx", "random_control")}, indent=1))
    return 0


def cmd_build() -> int:
    """E3: train on all catalogue, apply holdout-chosen r and t, write a float32 GeoTIFF."""
    e2 = json.loads((EVID / "catexcl_e2_holdout_20261031.json").read_text())
    best = e2["best_config"]
    foot, tr, crs, shape, cat = footprint_and_grid()
    path, names = build_feature_cache(foot, shape)
    mm = np.load(path, mmap_mode="r")
    lab, n_seg, quad_of_seg = split_folds(cat, shape)
    dom = foot.copy()
    clf, info = train_model(mm, foot, cat, lab, np.array([], int), np.zeros_like(foot), SEED + 99)
    p = predict_domain(clf, mm, dom).astype(np.float64)
    dist_vis = ndi.distance_transform_edt(~cat).astype(np.float32)   # ALL catalogue is known at build time
    pe = np.where(halo_excluded(dist_vis, best["halo_r_px"]), 0.0, p)
    if best["threshold"] > 0:
        pe = np.where(pe >= best["threshold"], pe, 0.0)
    pe = np.clip(pe, 0.0, 1.0).astype(np.float32)
    pe[~foot] = 0.0                       # outside GeoDAWN footprint: zero (same encoding as the top-scored B2 file)
    pe[cat] = 0.0                         # known catalogue pixels are masked by the organizer; keep them empty
    DOWN.mkdir(parents=True, exist_ok=True)
    import datetime as _dt
    stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = DOWN / f"karage1-catexcl-halo-r{best['halo_r_px']}-t{best['threshold']:.3f}-{stamp}-zeros.tif"
    with rasterio.open(DATA / "sample_submission.tif") as ref:
        profile = ref.profile.copy()
    profile.update(dtype="float32", count=1, nodata=None, compress="deflate", predictor=2,
                   tiled=False, BIGTIFF="NO")
    with rasterio.open(out, "w", **profile) as dst:
        dst.write(pe, 1)
        dst.update_tags(AREA_OR_POINT="Area", note="karage1 catexcl 31 Oct 2026, LOCAL, NOT CLEARED")
    print(f"wrote {out.relative_to(ROOT)} dots={(pe > 0).sum()} sha={_sha(out)}")
    summary = {"output": str(out.relative_to(ROOT)), "sha256": _sha(out), "bytes": out.stat().st_size,
               "dots_gt0": int((pe > 0).sum()), "config": best, "training": info,
               "min": float(pe.min()), "max": float(pe.max()),
               "nan_count": int(np.isnan(pe).sum()), "seconds": None}
    (EVID / "catexcl_e3_build_20261031.json").write_text(json.dumps(summary, indent=2) + "\n")
    return 0


def main(argv) -> int:
    if len(argv) != 2 or argv[1] not in ("canary", "holdout", "build"):
        print(__doc__)
        return 1
    return {"canary": cmd_canary, "holdout": cmd_holdout, "build": cmd_build}[argv[1]]()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
