"""Leakage canary, buffered Dual-Cover OOF training, and multi-benchmark DTI evaluation.

Delegates directly to `vendor/gems57` (`gems57-pooled-hide-v2`) per Parallel-Run Protocol Rule 2,
and additionally evaluates `GEMSDOE32-HIDE-RECOVER-v3.0` and `GEMSDOE32-SGMC-CAL-v3.0` (`n=62,703`
off-catalogue USGS SGMC bedrock fault pixels > 300 m outside `labels.tif`) for exact comparability
against the `0.2778` `GEMSDOE32` Champion (`h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif`).
"""
from __future__ import annotations

import gc
from pathlib import Path

import lightgbm as lgb
import numpy as np
import rasterio
from numpy.lib.format import open_memmap
from scipy.ndimage import binary_dilation, binary_erosion, distance_transform_edt, label
from skimage.morphology import skeletonize
from sklearn.metrics import roc_auc_score

from gems57 import evaluate_holdout as eh57
from gems57 import grid as G57
from gems57 import holdout as H57
from gems57 import metric as M57
from gemskarage1.emitter import emit_submodular_300m, sharpen_axial_crest
from gemskarage1.features import ALL_CHANNELS, BASE_CHANNELS, MSUB_INDICES


def load_reference_masks(ddir: Path) -> dict[str, object]:
    with rasterio.open(ddir / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
        crs = ds.crs
    with rasterio.open(ddir / "labels.tif") as ds:
        raw_lbl = ds.read(1)
        labels = np.isfinite(raw_lbl) & (raw_lbl > 0.5) & foot
    with rasterio.open(ddir / "external" / "derived_sgmc_faults_100m_u8.tif") as ds:
        sgmc_raw = (ds.read(1) > 0) & foot
    d_lbl = distance_transform_edt(~labels)
    sgmc_off_cat = sgmc_raw & (d_lbl > 3.0)
    with rasterio.open(ddir / "external" / "lidar_scarp_features_u8.tif") as ds:
        lidar_valid = (ds.read(12) > 0) & foot
    grid = G57.Grid(
        footprint=foot,
        catalogue=labels,
        crs=crs,
        transform=G57.TRANSFORM,
        height=G57.HEIGHT,
        width=G57.WIDTH,
    )
    return {
        "grid": grid,
        "footprint": foot,
        "labels": labels,
        "dist_labels_px": d_lbl.astype(np.float32),
        "sgmc_off_cat": sgmc_off_cat,
        "lidar_valid": lidar_valid,
    }


def quadrant_folds_with_collar(foot: np.ndarray, buffer_px: float = 15.0) -> tuple[list[np.ndarray], list[np.ndarray]]:
    qid = H57.quadrant_ids(foot)
    folds = [(qid == k) for k in range(4)]
    collars = [(distance_transform_edt(~f) <= buffer_px) for f in folds]
    return folds, collars


def score_canary_feature(values: np.ndarray, labels: np.ndarray, ceiling_auc: float = 0.90) -> dict:
    """Evaluate one feature; undefined or non-finite inputs are NOT a pass.

    A constant feature gives AUC 0.5 when both classes are present, but it
    cannot demonstrate that a meaningful feature channel was tested. It fails
    closed pending removal or data-quality review; this is not a leakage
    finding. Replacing NaN or infinity with zeros can hide a data error.
    """
    values = np.asarray(values, dtype=np.float64)
    labels = np.asarray(labels)
    if values.ndim != 1 or labels.ndim != 1 or values.shape != labels.shape or values.size == 0:
        return {"raw_auc": None, "direction_invariant_auc": None, "status": "invalid_shape_or_empty", "passed": False}
    if not np.isfinite(values).all():
        return {"raw_auc": None, "direction_invariant_auc": None, "status": "nonfinite", "passed": False}
    if not np.isin(labels, (0, 1)).all() or np.unique(labels).size != 2:
        return {"raw_auc": None, "direction_invariant_auc": None, "status": "missing_class", "passed": False}
    if np.all(values == values[0]):
        return {"raw_auc": None, "direction_invariant_auc": None, "status": "constant_no_variation", "passed": False}
    auc = float(roc_auc_score(labels, values))
    directional = max(auc, 1.0 - auc)
    return {"raw_auc": auc, "direction_invariant_auc": directional,
            "status": "tested" if directional <= ceiling_auc else "leakage_alarm",
            "passed": bool(directional <= ceiling_auc)}


def run_leakage_canary(
    stack_path: Path,
    foot: np.ndarray,
    labels: np.ndarray,
    *,
    ceiling_auc: float = 0.90,
) -> dict:
    """Protocol Rule 4: Solo single-feature ROC-AUC canary on withheld fault segments across all 58 channels."""
    mm = open_memmap(stack_path, mode="r")
    grid = G57.Grid(
        footprint=foot,
        catalogue=labels,
        crs=G57.CRS_EPSG,
        transform=G57.TRANSFORM,
        height=G57.HEIGHT,
        width=G57.WIDTH,
    )
    ctx = H57.build_holdout(grid, seeds=(20,), modes=("detached",))
    pos_mask = np.zeros(foot.shape, dtype=bool)
    active_union = np.zeros(foot.shape, dtype=bool)
    for cell in ctx.cells_of("detached"):
        sy, sx = cell.bbox
        pos_mask |= ctx.hidden_by_cell[cell.key]
        act_full = np.zeros(foot.shape, dtype=bool)
        act_full[sy, sx] = cell.active
        active_union |= act_full

    vis_all = labels & ~pos_mask
    d_vis = distance_transform_edt(~vis_all)
    eval_pos = pos_mask & (d_vis > 3.0)
    eval_bg = active_union & ~labels & (d_vis > 3.0)

    rng = np.random.default_rng(20261027)
    pos_idx = np.flatnonzero(eval_pos)
    bg_idx = np.flatnonzero(eval_bg)
    if bg_idx.size > 120_000:
        bg_idx = rng.choice(bg_idx, size=120_000, replace=False)

    idx_all = np.concatenate([pos_idx, bg_idx])
    y_true = np.concatenate([np.ones(pos_idx.size, dtype=np.int8), np.zeros(bg_idx.size, dtype=np.int8)])
    ys = idx_all // foot.shape[1]
    xs = idx_all % foot.shape[1]

    rows = []
    max_dir_auc = 0.0
    max_ch = ""
    leaking = []
    untestable = []
    for ch_i, name in enumerate(ALL_CHANNELS):
        vals = mm[ch_i, ys, xs]
        result = score_canary_feature(vals, y_true, ceiling_auc)
        direction = result["direction_invariant_auc"]
        if result["status"] == "leakage_alarm":
            leaking.append(name)
        elif not result["passed"]:
            untestable.append(name)
        if direction is not None and direction > max_dir_auc:
            max_dir_auc = direction
            max_ch = name
        rows.append({"channel_index": ch_i, "feature": name, **result})

    return {
        "protocol_rule": "Rule-4-Single-Feature-Leakage-Canary",
        "implementation": "karage1-canary-v2-fail-closed",
        "evaluator_holdout": eh57.VERSION,
        "auc_ceiling": ceiling_auc,
        "n_channels_tested": len(ALL_CHANNELS),
        "n_withheld_detached_positives": int(pos_idx.size),
        "n_background_samples": int(bg_idx.size),
        "max_direction_invariant_auc": max_dir_auc if max_ch else None,
        "max_feature": max_ch or None,
        "leaking_features": leaking,
        "untestable_features": untestable,
        "all_passed": len(leaking) == 0 and len(untestable) == 0,
        "channels": rows,
    }


def _quantile_match_to_ref(src_vals: np.ndarray, ref_sample: np.ndarray, src_sample: np.ndarray) -> np.ndarray:
    qs = np.linspace(0.0, 1.0, 1001)
    sq = np.maximum.accumulate(np.quantile(src_sample, qs))
    rq = np.quantile(ref_sample, qs)
    return np.interp(src_vals, sq, rq).astype(np.float32)


def fit_buffered_dual_cover_oof(
    stack_path: Path,
    grid: G57.Grid,
    lidar_valid: np.ndarray,
    cdir: Path,
    *,
    force: bool = False,
    log=print,
) -> dict[str, np.ndarray]:
    """Fit leak-free Buffered Quadrant Cross-Fitted models (`BASE-35`, `M_Full-58`, `M_Sub-52`) + Diagonal OOF."""
    cache_npz = cdir / "karage1_oof_surfaces_v1.npz"
    if not force and cache_npz.is_file():
        log(f"[oof] Reusing cached buffered OOF surfaces at {cache_npz}")
        data = np.load(cache_npz)
        return {k: data[k] for k in data.files}

    foot = grid.footprint
    labels = grid.catalogue
    mm = open_memmap(stack_path, mode="r")
    _, h, w = mm.shape
    folds, collars = quadrant_folds_with_collar(foot, buffer_px=15.0)

    # Mask union of all hidden segments across both `gems57-pooled-hide-v2` and `HIDE-RECOVER-v3.0`
    any_hidden = np.zeros((h, w), dtype=bool)
    ctx57 = H57.build_holdout(grid, seeds=(20, 21), modes=("all", "detached"))
    for hid_m in ctx57.hidden_by_cell.values():
        any_hidden |= hid_m
    for d in build_hr3_draws(foot, labels, seeds=(101, 202)):
        any_hidden |= d["hidden"]
    hidden_buf = binary_dilation(any_hidden, iterations=3)

    d_lbl_vis = distance_transform_edt(~(labels & ~any_hidden))
    safe_pos_all = labels & ~hidden_buf & foot
    safe_neg_all = foot & ~labels & ~hidden_buf & (d_lbl_vis > 3.0)

    base_idx = list(range(len(BASE_CHANNELS)))
    full_idx = list(range(len(ALL_CHANNELS)))
    msub_idx = list(MSUB_INDICES)

    p_base_quad = np.zeros((h, w), dtype=np.float32)
    p_dual_quad = np.zeros((h, w), dtype=np.float32)

    lgb_params = dict(
        n_estimators=260,
        learning_rate=0.055,
        num_leaves=47,
        min_child_samples=80,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.75,
        reg_alpha=1.5,
        reg_lambda=4.0,
        n_jobs=2,
        random_state=20261027,
        verbose=-1,
    )

    def _gather_features(ys: np.ndarray, xs: np.ndarray, feat_cols: list[int]) -> np.ndarray:
        X = np.empty((ys.size, len(feat_cols)), dtype=np.float32)
        for j, ch in enumerate(feat_cols):
            X[:, j] = mm[ch, ys, xs]
        return X

    def _sample_xy(train_domain: np.ndarray, feat_cols: list[int], seed_i: int) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(seed_i)
        p_flat = np.flatnonzero(safe_pos_all & train_domain)
        n_flat = np.flatnonzero(safe_neg_all & train_domain)
        if p_flat.size > 45_000:
            p_flat = rng.choice(p_flat, size=45_000, replace=False)
        n_keep = min(n_flat.size, max(p_flat.size * 4, 90_000))
        n_flat = rng.choice(n_flat, size=n_keep, replace=False)
        all_f = np.concatenate([p_flat, n_flat])
        y = np.concatenate([np.ones(p_flat.size, dtype=np.int32), np.zeros(n_flat.size, dtype=np.int32)])
        ys, xs = all_f // w, all_f % w
        return _gather_features(ys, xs, feat_cols), y

    def _predict_domain(clf: lgb.LGBMClassifier, dom: np.ndarray, feat_cols: list[int]) -> np.ndarray:
        flat = np.flatnonzero(dom)
        ys, xs = flat // w, flat % w
        X_all = _gather_features(ys, xs, feat_cols)
        out = np.zeros(flat.size, dtype=np.float32)
        chunk = 300_000
        for s in range(0, flat.size, chunk):
            out[s : s + chunk] = clf.predict_proba(X_all[s : s + chunk])[:, 1].astype(np.float32)
        del X_all
        return out

    for q in range(4):
        tr_dom = foot & ~collars[q]
        te_dom = folds[q]
        log(f"[oof] Training buffered Quadrant {q}/3 models (train={int(tr_dom.sum())}, test={int(te_dom.sum())})...")

        Xb, yb = _sample_xy(tr_dom, base_idx, 100 + q)
        clf_base = lgb.LGBMClassifier(**lgb_params)
        clf_base.fit(Xb, yb)
        del Xb, yb
        p_base_quad[te_dom] = _predict_domain(clf_base, te_dom, base_idx)
        del clf_base

        Xf, yf = _sample_xy(tr_dom & lidar_valid, full_idx, 200 + q)
        clf_full = lgb.LGBMClassifier(**lgb_params)
        clf_full.fit(Xf, yf)
        del Xf, yf

        Xs, ys_l = _sample_xy(tr_dom, msub_idx, 300 + q)
        clf_sub = lgb.LGBMClassifier(**lgb_params)
        clf_sub.fit(Xs, ys_l)
        del Xs, ys_l

        rng_cal = np.random.default_rng(400 + q)
        cal_flat = rng_cal.choice(np.flatnonzero(tr_dom & lidar_valid & safe_neg_all), size=40_000, replace=False)
        c_ys, c_xs = cal_flat // w, cal_flat % w
        ref_cal = clf_full.predict_proba(_gather_features(c_ys, c_xs, full_idx))[:, 1].astype(np.float32)
        sub_cal = clf_sub.predict_proba(_gather_features(c_ys, c_xs, msub_idx))[:, 1].astype(np.float32)

        te_lid = te_dom & lidar_valid
        te_gap = te_dom & ~lidar_valid
        if np.any(te_lid):
            p_full_lid = _predict_domain(clf_full, te_lid, full_idx)
            p_sub_lid = _quantile_match_to_ref(_predict_domain(clf_sub, te_lid, msub_idx), ref_cal, sub_cal)
            p_dual_quad[te_lid] = np.float32(0.75) * p_full_lid + np.float32(0.25) * p_sub_lid
        if np.any(te_gap):
            p_dual_quad[te_gap] = _quantile_match_to_ref(_predict_domain(clf_sub, te_gap, msub_idx), ref_cal, sub_cal)

        del clf_full, clf_sub
        gc.collect()

    # Complementary 45-degree Rotated Diagonal 4-Fold Cross-Fit for seam-free full-map production surface
    yy_idx, xx_idx = np.nonzero(foot)
    u_coord = (yy_idx - float(yy_idx.mean())) + (xx_idx - float(xx_idx.mean()))
    v_coord = (yy_idx - float(yy_idx.mean())) - (xx_idx - float(xx_idx.mean()))
    um = float(np.median(u_coord))
    vm = float(np.median(v_coord))
    diag_folds = []
    diag_collars = []
    for su in (False, True):
        for sv in (False, True):
            fm = np.zeros((h, w), dtype=bool)
            fm[yy_idx, xx_idx] = ((u_coord >= um) if su else (u_coord < um)) & ((v_coord >= vm) if sv else (v_coord < vm))
            diag_folds.append(fm)
            diag_collars.append(distance_transform_edt(~fm) <= 15.0)

    p_dual_diag = np.zeros((h, w), dtype=np.float32)
    for q in range(4):
        tr_dom = foot & ~diag_collars[q]
        te_dom = diag_folds[q]
        log(f"[oof] Training rotated Diagonal {q}/3 Dual-Cover models for seam-free full-map stitch...")
        Xf, yf = _sample_xy(tr_dom & lidar_valid, full_idx, 500 + q)
        clf_full = lgb.LGBMClassifier(**lgb_params)
        clf_full.fit(Xf, yf)
        del Xf, yf

        Xs, ys_l = _sample_xy(tr_dom, msub_idx, 600 + q)
        clf_sub = lgb.LGBMClassifier(**lgb_params)
        clf_sub.fit(Xs, ys_l)
        del Xs, ys_l

        rng_cal = np.random.default_rng(700 + q)
        cal_flat = rng_cal.choice(np.flatnonzero(tr_dom & lidar_valid & safe_neg_all), size=40_000, replace=False)
        c_ys, c_xs = cal_flat // w, cal_flat % w
        ref_cal = clf_full.predict_proba(_gather_features(c_ys, c_xs, full_idx))[:, 1].astype(np.float32)
        sub_cal = clf_sub.predict_proba(_gather_features(c_ys, c_xs, msub_idx))[:, 1].astype(np.float32)

        te_lid = te_dom & lidar_valid
        te_gap = te_dom & ~lidar_valid
        if np.any(te_lid):
            p_f = _predict_domain(clf_full, te_lid, full_idx)
            p_s = _quantile_match_to_ref(_predict_domain(clf_sub, te_lid, msub_idx), ref_cal, sub_cal)
            p_dual_diag[te_lid] = np.float32(0.75) * p_f + np.float32(0.25) * p_s
        if np.any(te_gap):
            p_dual_diag[te_gap] = _quantile_match_to_ref(_predict_domain(clf_sub, te_gap, msub_idx), ref_cal, sub_cal)
        del clf_full, clf_sub
        gc.collect()

    p_dual_prod = (np.float32(0.5) * p_dual_quad + np.float32(0.5) * p_dual_diag).astype(np.float32)

    raw_c_hmas = mm[51].astype(np.float32, copy=True)
    rng_env = np.random.default_rng(888)
    fp_flat = rng_env.choice(np.flatnonzero(foot), size=150_000, replace=False)
    f_ys, f_xs = fp_flat // w, fp_flat % w
    c_hmas_cal = np.zeros((h, w), dtype=np.float32)
    c_hmas_cal[foot] = _quantile_match_to_ref(raw_c_hmas[foot], p_dual_quad[f_ys, f_xs], raw_c_hmas[f_ys, f_xs])

    np.savez_compressed(
        cache_npz,
        p_base_quad=p_base_quad,
        p_dual_quad=p_dual_quad,
        p_dual_prod=p_dual_prod,
        c_hmas_cal=c_hmas_cal,
    )
    log(f"[oof] Saved buffered OOF surfaces -> {cache_npz}")
    return {
        "p_base_quad": p_base_quad,
        "p_dual_quad": p_dual_quad,
        "p_dual_prod": p_dual_prod,
        "c_hmas_cal": c_hmas_cal,
    }


def compose_arm_surface(
    arm_id: str,
    p_dual: np.ndarray,
    c_hmas_cal: np.ndarray,
    foot: np.ndarray,
) -> tuple[np.ndarray, float]:
    """Return `(belief_surface, min_sep_px)` for each preregistered arm in the `H-K1-1` lane."""
    if arm_id == "BASE_35":
        return np.where(foot, p_dual, np.float32(0.0)).astype(np.float32), 2.9
    if arm_id == "EXP1_HMAS_MULT":
        p98 = float(np.percentile(c_hmas_cal[foot][::8], 98)) + 1e-6
        s = p_dual * (np.float32(0.40) + np.float32(0.60) * np.clip(c_hmas_cal / np.float32(p98), 0.0, 1.5))
        return np.where(foot, s, np.float32(0.0)).astype(np.float32), 2.9
    if arm_id == "EXP2_HMAS_MAXENV_RAW":
        p98 = float(np.percentile(c_hmas_cal[foot][::8], 98)) + 1e-6
        mod = p_dual * (np.float32(0.82) + np.float32(0.28) * np.clip(c_hmas_cal / np.float32(p98), 0.0, 1.5))
        s = np.maximum(mod, np.float32(0.56) * c_hmas_cal)
        return np.where(foot, s, np.float32(0.0)).astype(np.float32), 0.0
    if arm_id == "EXP3_HMAS_MAXENV_AXIAL29":
        p98 = float(np.percentile(c_hmas_cal[foot][::8], 98)) + 1e-6
        mod = p_dual * (np.float32(0.82) + np.float32(0.28) * np.clip(c_hmas_cal / np.float32(p98), 0.0, 1.5))
        env = np.maximum(mod, np.float32(0.56) * c_hmas_cal)
        s = sharpen_axial_crest(env, foot, crest_boost=0.24)
        return np.where(foot, s, np.float32(0.0)).astype(np.float32), 2.9
    raise ValueError(f"Unknown arm_id: {arm_id}")


def evaluate_gems57_holdout_suite(
    arm_surfaces: dict[str, tuple[np.ndarray, float]],
    grid: G57.Grid,
    *,
    full_budget: int = 38_200,
    b_collar_px: float = 2.2,
    candidate_arm: str = "EXP3_HMAS_MAXENV_AXIAL29",
    log=print,
) -> dict:
    """Official `vendor/gems57/evaluate_holdout.py` (`gems57-pooled-hide-v2`) evaluation across all arms."""
    ctx = H57.build_holdout(grid, seeds=(20, 21), modes=("all", "detached"))
    fp_total = float(grid.footprint.sum())
    out = {}

    for mode in ("all", "detached"):
        cells = ctx.cells_of(mode)
        terms_by_arm: dict[str, np.ndarray] = {}
        for arm_name, (surf, min_sep) in arm_surfaces.items():
            arm_terms = None
            for cell in cells:
                sy, sx = cell.bbox
                vis_crop = ctx.visible(cell.key)[sy, sx]
                foot_crop = grid.footprint[sy, sx]
                active_crop = cell.active
                cell_budget = max(1, int(round(full_budget * (float(active_crop.sum()) / fp_total))))
                emitted_crop = emit_submodular_300m(
                    surf[sy, sx],
                    active_crop,
                    vis_crop,
                    cell_budget,
                    b_collar_px=b_collar_px,
                    min_sep_px=min_sep,
                    max_candidates=90_000,
                ).astype(np.float32)

                truth_crop = np.zeros(active_crop.shape, dtype=bool)
                truth_crop[cell.truth_yx] = True
                fold_dict = {
                    "region": active_crop | (vis_crop & foot_crop),
                    "visible": vis_crop,
                    "truth": truth_crop,
                }
                _, terms = eh57.evaluate(
                    emitted_crop,
                    fold_dict,
                    foot_crop,
                    block_side=200,
                    origin=(int(sy.start), int(sx.start)),
                    global_shape=grid.shape,
                )
                arm_terms = terms if arm_terms is None else (arm_terms + terms)
            assert arm_terms is not None
            terms_by_arm[arm_name] = arm_terms
            sc = float(eh57.from_terms(arm_terms.sum(axis=0)))
            log(f"  [gems57-pooled-hide-v2 mode={mode:8s}] {arm_name:26s} -> HOLDOUT-DTI = {sc:.6f}")

        out[mode] = eh57.pooled_summary(terms_by_arm, draws=1000, seed=520810, candidate=candidate_arm)
        out[f"{mode}_raw_terms"] = terms_by_arm

    return out


# --- GEMSDOE32-HIDE-RECOVER-v3.0 & SGMC-CAL-v3.0 Exact Champion-Comparable Evaluators ---

def build_hr3_draws(foot: np.ndarray, labels: np.ndarray, seeds: tuple[int, ...] = (101, 202)) -> list[dict]:
    skel = skeletonize(labels)
    ys, xs = np.nonzero(skel)
    cnt = np.zeros(labels.shape, dtype=np.int16)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny = np.clip(ys + dy, 0, labels.shape[0] - 1)
            nx = np.clip(xs + dx, 0, labels.shape[1] - 1)
            cnt[ys, xs] += skel[ny, nx]
    junc = np.zeros_like(skel)
    junc[ys, xs] = cnt[ys, xs] >= 3
    seg_skel = skel & ~binary_dilation(junc, np.ones((3, 3), dtype=bool))
    comp_s, _ = label(seg_skel, structure=np.ones((3, 3), dtype=np.int8))
    _, idx = distance_transform_edt(comp_s == 0, return_distances=True, return_indices=True)
    comp = np.zeros(labels.shape, dtype=np.int32)
    comp[labels] = comp_s[idx[0][labels], idx[1][labels]]
    all_ids = np.unique(comp[labels])
    all_ids = all_ids[all_ids > 0]

    folds, _ = quadrant_folds_with_collar(foot, buffer_px=15.0)
    interior = [binary_erosion(f, iterations=12) & foot for f in folds]

    draws = []
    for seed in seeds:
        rng = np.random.default_rng(seed)
        perm = rng.permutation(all_ids)
        hidden_ids = perm[: int(round(0.25 * perm.size))]
        hidden = np.isin(comp, hidden_ids) & labels
        visible = labels & ~hidden
        d_vis = distance_transform_edt(~visible)
        for q in range(4):
            dom = interior[q]
            hid_dom = hidden & dom
            det_dom = hid_dom & (d_vis >= 6.0)
            draws.append(
                {
                    "seed": seed,
                    "quadrant": q,
                    "test_domain": dom,
                    "visible": visible,
                    "hidden": hid_dom,
                    "detached": det_dom,
                }
            )
    return draws


def _block_ids_256(shape: tuple[int, int], n_rows: int = 16, n_cols: int = 16) -> np.ndarray:
    h, w = shape
    rb = np.minimum((np.arange(h) * n_rows) // h, n_rows - 1)
    cb = np.minimum((np.arange(w) * n_cols) // w, n_cols - 1)
    return (rb[:, None] * n_cols + cb[None, :]).astype(np.int32)


def _pooled_dti_blocks(
    pred: np.ndarray,
    gt: np.ndarray,
    eval_mask: np.ndarray,
    blk_grid: np.ndarray,
    n_blocks: int = 256,
) -> tuple[float, np.ndarray, np.ndarray, np.ndarray]:
    p = np.where(eval_mask & np.isfinite(pred), np.clip(pred, 0.0, 1.0), 0.0).astype(np.float32)
    g = np.asarray(gt, dtype=bool) & eval_mask
    covers, q_near, _ = M57.max_cover(p, g)
    tp_pix = covers.astype(np.float64)
    fn_pix = (1.0 - covers).astype(np.float64)
    g_blk = blk_grid[g]

    p_pos = p > 0.0
    fp_pix = (p[p_pos] * (1.0 - q_near[p_pos])).astype(np.float64)
    p_blk = blk_grid[p_pos]

    tp_b = np.bincount(g_blk, weights=tp_pix, minlength=n_blocks)
    fn_b = np.bincount(g_blk, weights=fn_pix, minlength=n_blocks)
    fp_b = np.bincount(p_blk, weights=fp_pix, minlength=n_blocks)

    tp = float(tp_b.sum())
    fp = float(fp_b.sum())
    fn = float(fn_b.sum())
    denom = tp + 0.2 * fp + 0.8 * fn
    return (tp / denom if denom > 0 else 0.0), tp_b, fp_b, fn_b


def _bootstrap_ci_and_delta(
    tp_b: np.ndarray,
    fp_b: np.ndarray,
    fn_b: np.ndarray,
    ref_tp_b: np.ndarray | None = None,
    ref_fp_b: np.ndarray | None = None,
    ref_fn_b: np.ndarray | None = None,
    n_boot: int = 800,
    seed: int = 20261027,
) -> dict:
    rng = np.random.default_rng(seed)
    nb = tp_b.size
    idx = rng.integers(0, nb, size=(n_boot, nb))
    tp_s = tp_b[idx].sum(axis=1)
    fp_s = fp_b[idx].sum(axis=1)
    fn_s = fn_b[idx].sum(axis=1)
    dti_s = tp_s / np.maximum(tp_s + 0.2 * fp_s + 0.8 * fn_s, 1e-12)
    out = {
        "ci95": [round(float(np.percentile(dti_s, 2.5)), 6), round(float(np.percentile(dti_s, 97.5)), 6)],
    }
    if ref_tp_b is not None and ref_fp_b is not None and ref_fn_b is not None:
        rtp = ref_tp_b[idx].sum(axis=1)
        rfp = ref_fp_b[idx].sum(axis=1)
        rfn = ref_fn_b[idx].sum(axis=1)
        rdti = rtp / np.maximum(rtp + 0.2 * rfp + 0.8 * rfn, 1e-12)
        diff = dti_s - rdti
        out["delta_vs_ref_mean"] = round(float(diff.mean()), 6)
        out["delta_vs_ref_ci95"] = [round(float(np.percentile(diff, 2.5)), 6), round(float(np.percentile(diff, 97.5)), 6)]
        out["prob_beats_ref"] = round(float((diff > 0.0).mean()), 4)
    return out


def evaluate_sgmc_off_catalogue(
    pred: np.ndarray,
    foot: np.ndarray,
    labels: np.ndarray,
    sgmc_off_cat: np.ndarray,
    ref_blocks: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None,
    prevalence_mult: float = 4.92,
) -> tuple[dict, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    d_lbl = distance_transform_edt(~labels)
    eval_mask = foot & (d_lbl > 3.0)
    blk = _block_ids_256(foot.shape)
    raw_dti, tp_b, fp_b, fn_b = _pooled_dti_blocks(pred, sgmc_off_cat, eval_mask, blk, n_blocks=256)
    boot = _bootstrap_ci_and_delta(
        tp_b,
        fp_b,
        fn_b,
        *(ref_blocks if ref_blocks is not None else (None, None, None)),
    )
    tp = float(tp_b.sum())
    fp = float(fp_b.sum())
    fn = float(fn_b.sum())
    cal_dti = (prevalence_mult * tp) / max(prevalence_mult * tp + 0.2 * fp + 0.8 * prevalence_mult * fn, 1e-12)
    res = {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": "GEMSDOE32-SGMC-CAL-v3.0",
        "withheld_positives": int((sgmc_off_cat & eval_mask).sum()),
        "sgmc_raw_pooled_dti": round(raw_dti, 6),
        "sgmc_raw_ci95": boot["ci95"],
        "sgmc_prevalence_calibrated_ref": round(float(cal_dti), 6),
    }
    if "delta_vs_ref_ci95" in boot:
        res["delta_vs_champion_raw"] = boot["delta_vs_ref_mean"]
        res["delta_vs_champion_ci95"] = boot["delta_vs_ref_ci95"]
        res["prob_beats_champion"] = boot["prob_beats_ref"]
    return res, (tp_b, fp_b, fn_b)


def evaluate_hr3_per_cell(
    belief_quad: np.ndarray,
    draws: list[dict],
    foot: np.ndarray,
    *,
    full_budget: int = 38_200,
    min_sep_px: float = 2.9,
    b_collar_px: float = 2.2,
    ref_blocks_all: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None,
    ref_blocks_det: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None,
) -> tuple[dict, tuple[np.ndarray, np.ndarray, np.ndarray], tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Per-cell `GEMSDOE32-HIDE-RECOVER-v3.0` (`all` n=22,232 & `detached >= 600m` n=15,504), masking ONLY `d['visible']`."""
    blk = _block_ids_256(foot.shape)
    fp_total = float(foot.sum())
    tp_all = np.zeros(256, dtype=np.float64)
    fp_all = np.zeros(256, dtype=np.float64)
    fn_all = np.zeros(256, dtype=np.float64)
    tp_det = np.zeros(256, dtype=np.float64)
    fp_det = np.zeros(256, dtype=np.float64)
    fn_det = np.zeros(256, dtype=np.float64)
    n_all = 0
    n_det = 0

    for d in draws:
        eval_m = d["test_domain"] & ~d["visible"]
        cell_budget = max(1, int(round(full_budget * (float(eval_m.sum()) / fp_total))))
        emitted = emit_submodular_300m(
            belief_quad,
            d["test_domain"],
            d["visible"],
            cell_budget,
            b_collar_px=b_collar_px,
            min_sep_px=min_sep_px,
            max_candidates=95_000,
        ).astype(np.float32)

        _, tpa, fpa, fna = _pooled_dti_blocks(emitted, d["hidden"], eval_m, blk, n_blocks=256)
        tp_all += tpa; fp_all += fpa; fn_all += fna
        n_all += int(d["hidden"].sum())

        d_vis = distance_transform_edt(~d["visible"])
        det_m = d["test_domain"] & (d_vis >= 6.0)
        _, tpd, fpd, fnd = _pooled_dti_blocks(emitted, d["detached"], det_m, blk, n_blocks=256)
        tp_det += tpd; fp_det += fpd; fn_det += fnd
        n_det += int(d["detached"].sum())

    dti_all = float(tp_all.sum() / max(tp_all.sum() + 0.2 * fp_all.sum() + 0.8 * fn_all.sum(), 1e-12))
    dti_det = float(tp_det.sum() / max(tp_det.sum() + 0.2 * fp_det.sum() + 0.8 * fn_det.sum(), 1e-12))
    b_all = _bootstrap_ci_and_delta(tp_all, fp_all, fn_all, *(ref_blocks_all or (None, None, None)))
    b_det = _bootstrap_ci_and_delta(tp_det, fp_det, fn_det, *(ref_blocks_det or (None, None, None)))
    res = {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": "GEMSDOE32-HIDE-RECOVER-v3.0",
        "all": {
            "dti": round(dti_all, 6),
            "withheld_positives": n_all,
            **b_all,
        },
        "detached": {
            "dti": round(dti_det, 6),
            "withheld_positives": n_det,
            **b_det,
        },
    }
    return res, (tp_all, fp_all, fn_all), (tp_det, fp_det, fn_det)
