#!/usr/bin/env python
"""
EXPERIMENT 1 / 3 (parallel-run protocol cap) -- single method lane:

    H-GEOD-STRAIN: active geodetic dilatation-rate / shear-strain-rate
    anomalies colocate with active (but not necessarily yet-digitized)
    normal/oblique-slip fault traces in the Great Basin, because brittle
    extensional faulting produces a measurable surface strain-rate signal
    that is independent of -- and does not require -- prior fault mapping.

    Non-fault mimic / confound: strain concentration can also arise from
    non-tectonic processes (aquifer-compaction subsidence, volcanic
    inflation/deflation, geodetic processing noise) that produce no real
    fault discontinuity. This is a known, named confound, not resolved by
    this experiment.

Data: real competition `training_features.tif` (19 bands) / `labels.tif`,
restored from the hash-pinned GitHub mirror
(buffedlizard55-lab/GEMSDOE@c0c06ac..., buffedlizard55-lab/GEMSDOE24@07345ea...)
documented in buffedlizard55-lab/GEMSDOE32's own registry/data_manifest.json.
Every file's sha256 was independently re-verified against that manifest
before this script ran (see docs/LIMITATIONS.md "Data access update").

Method (single lane, two features only: geod_dilaterate, geod_shearrate):
  1. Connected-component segment the real fault-label raster into discrete
     traces (8-connectivity).
  2. Hold out ~20% of segments (by segment count, seed=42) -- WHOLE segments,
     never individual pixels.
  3. Buffer every TRAIN positive segment by 300 m (3 px, matching the
     official kernel radius) and exclude that buffer from both model
     fitting *and* holdout scoring, so the holdout score cannot be inflated
     by spillover near a fault the model has already seen.
  4. Fit a 2-feature logistic regression on TRAIN region pixels only
     (positives = train segments, negatives = a random sample of
     remaining train-region pixels, class_weight="balanced").
  5. Leakage canary: fit the *same* model with each feature alone and
     report its ROC AUC on the TRAIN region (never on holdout). AUC > 0.90
     for a lone feature is treated as presumed leakage, not a true result.
  6. HOLDOUT-DTI: score the fitted model's prediction over the whole grid,
     but restrict both the ground-truth and the valid-scoring footprint to
     the held-out segments / the region outside the train buffer (see
     src/gems/metric.py). A spatial bootstrap (resample holdout segments
     with replacement, 300 iterations) gives the 95% CI.
  7. Refit on *all* labeled segments (train+holdout pooled) for the actual
     submission candidate -- the holdout split above is for honest scoring
     only, never for the shipped raster.

Caps respected: this is experiment 1 of the <=3 allowed; wall clock is
logged in the run card.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, label as cc_label
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score

from gems.metric import distance_weighted_tversky_index, windowed_max_prediction

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs" / "experiment_h_geod_strain"
OUT.mkdir(parents=True, exist_ok=True)

FEATURE_NAMES = [
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope", "tc",
    "geod_shearrate", "geod_dilaterate", "tmi_vg", "deq_n100a15",
    "iso_grav_anom_vg", "det_elev", "iso_grav_anom", "tmi", "depth_to_base_surf",
    "ieq_n100a15", "cond_surf", "iso_grav_anom_hg", "det_elev_slope",
]
LANE_FEATURES = ["geod_shearrate", "geod_dilaterate"]
SEED = 42
HOLDOUT_FRACTION = 0.20
BUFFER_PX = 3  # 300 m at 100 m pixels, matches the official kernel radius
N_BOOTSTRAP = 200


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> None:
    t0 = time.time()
    rng = np.random.default_rng(SEED)

    log("loading labels + footprint ...")
    with rasterio.open(DATA / "labels.tif") as src:
        labels_raw = src.read(1)
        labels_nodata = src.nodata
    with rasterio.open(DATA / "sample_submission.tif") as src:
        template_band = src.read(1)
        profile = src.profile

    footprint = np.isfinite(template_band)  # True = inside scored footprint
    fault = (labels_raw == 1) & footprint
    n_fault_px = int(fault.sum())
    log(f"footprint pixels={int(footprint.sum())}, fault pixels={n_fault_px}")

    log("connected-component segmenting fault traces (8-connectivity) ...")
    structure = np.ones((3, 3), dtype=int)
    segment_ids, n_segments = cc_label(fault, structure=structure)
    log(f"n_segments={n_segments}")

    seg_ids_all = np.arange(1, n_segments + 1)
    rng.shuffle(seg_ids_all)
    n_holdout_seg = max(1, int(round(n_segments * HOLDOUT_FRACTION)))
    holdout_seg_ids = set(seg_ids_all[:n_holdout_seg].tolist())
    train_seg_ids = set(seg_ids_all[n_holdout_seg:].tolist())

    holdout_mask = np.isin(segment_ids, list(holdout_seg_ids)) & fault
    train_mask = np.isin(segment_ids, list(train_seg_ids)) & fault
    n_holdout_px = int(holdout_mask.sum())
    n_train_px = int(train_mask.sum())
    log(f"segments: train={len(train_seg_ids)} ({n_train_px} px), "
        f"holdout={len(holdout_seg_ids)} ({n_holdout_px} px)")

    log("buffering train-positive segments by 3px / 300m ...")
    dist_to_train = distance_transform_edt(~train_mask, sampling=(100.0, 100.0))
    train_buffer = dist_to_train <= 300.0  # includes train_mask itself

    eval_region = footprint & ~train_buffer  # where holdout scoring is fair
    fit_region = footprint & ~train_buffer  # where the model may be fit (train positives are IN train_buffer, so add them back for fitting)
    # Training positives must be included as positives for fitting even though
    # they are inside their own buffer; only holdout + its own buffer must be
    # excluded from fitting (recover-hidden-segment protocol).
    dist_to_holdout = distance_transform_edt(~holdout_mask, sampling=(100.0, 100.0))
    holdout_buffer = dist_to_holdout <= 300.0
    fit_region = footprint & ~holdout_buffer  # model may see everything except holdout + its buffer
    log(f"eval_region px={int(eval_region.sum())}, fit_region px={int(fit_region.sum())}")

    log("loading feature bands (lane features + canary set) ...")
    canary_features = LANE_FEATURES  # keep lane tight: 2 features total
    band_idx = {name: i + 1 for i, name in enumerate(FEATURE_NAMES)}
    feats = {}
    with rasterio.open(DATA / "training_features.tif") as src:
        for name in canary_features:
            arr = src.read(band_idx[name]).astype(np.float64)
            nodata = src.nodata
            if nodata is not None:
                arr[arr == nodata] = np.nan
            feats[name] = arr

    finite_all = np.ones_like(footprint, dtype=bool)
    for name in canary_features:
        finite_all &= np.isfinite(feats[name])
    usable = footprint & finite_all
    log(f"usable (finite feature) pixels={int(usable.sum())}")

    # ---- sample a manageable training set ----
    fit_pos_mask = fit_region & usable & train_mask
    fit_neg_candidates = fit_region & usable & ~fault
    n_pos = int(fit_pos_mask.sum())
    n_neg_sample = min(int(fit_neg_candidates.sum()), n_pos * 20, 400_000)
    log(f"fit positives={n_pos}, sampling {n_neg_sample} negatives")

    pos_yx = np.argwhere(fit_pos_mask)
    neg_all_yx = np.argwhere(fit_neg_candidates)
    neg_idx = rng.choice(len(neg_all_yx), size=n_neg_sample, replace=False)
    neg_yx = neg_all_yx[neg_idx]

    def gather(yx):
        return np.stack([feats[name][yx[:, 0], yx[:, 1]] for name in canary_features], axis=1)

    X_pos, X_neg = gather(pos_yx), gather(neg_yx)
    X = np.vstack([X_pos, X_neg])
    y = np.concatenate([np.ones(len(X_pos)), np.zeros(len(X_neg))])

    mu, sigma = X.mean(axis=0), X.std(axis=0) + 1e-12
    Xs = (X - mu) / sigma

    log("leakage canary: single-feature AUC (train region only) ...")
    canary_results = {}
    for i, name in enumerate(canary_features):
        clf1 = LogisticRegression(class_weight="balanced", max_iter=1000)
        clf1.fit(Xs[:, [i]], y)
        auc = roc_auc_score(y, clf1.predict_proba(Xs[:, [i]])[:, 1])
        canary_results[name] = float(auc)
        flag = "SUSPECTED LEAKAGE" if auc > 0.90 else "ok"
        log(f"  {name}: AUC={auc:.4f} -> {flag}")

    log("fitting 2-feature lane model on TRAIN region ...")
    clf = LogisticRegression(class_weight="balanced", max_iter=2000)
    clf.fit(Xs, y)
    train_auc = float(roc_auc_score(y, clf.predict_proba(Xs)[:, 1]))
    log(f"  joint 2-feature train AUC={train_auc:.4f}")

    log("scoring full grid with the TRAIN-only model ...")
    X_full = np.stack([feats[name] for name in canary_features], axis=-1)
    X_full_flat = X_full.reshape(-1, len(canary_features))
    finite_flat = usable.reshape(-1)
    probs_flat = np.zeros(X_full_flat.shape[0], dtype=np.float64)
    Xs_full = (X_full_flat[finite_flat] - mu) / sigma
    probs_flat[finite_flat] = clf.predict_proba(Xs_full)[:, 1]
    pred_holdout_eval = probs_flat.reshape(footprint.shape)
    pred_holdout_eval = np.where(usable, pred_holdout_eval, 0.0)

    log("computing HOLDOUT-DTI ...")
    gt_holdout_only = holdout_mask  # ground truth = ONLY the withheld segments
    valid_mask = eval_region & usable
    result = distance_weighted_tversky_index(
        pred=np.clip(pred_holdout_eval, 0.0, 1.0),
        ground_truth=gt_holdout_only,
        valid_mask=valid_mask,
    )
    log(f"  point estimate HOLDOUT-DTI = {result.dti:.4f} "
        f"(TPw={result.tp_w:.2f} FPw={result.fp_w:.2f} FNw={result.fn_w:.2f}, "
        f"n_withheld_fault_px={result.n_ground_truth_positive})")

    log(f"spatial block bootstrap over {len(holdout_seg_ids)} withheld segments, "
        f"{N_BOOTSTRAP} resamples ...")
    holdout_seg_list = np.array(sorted(holdout_seg_ids))
    # Proper cluster bootstrap for an additive-over-ground-truth-pixel
    # statistic: the resampling unit is the whole segment, and TPw/FNw are
    # sums over ground-truth pixels, so a segment drawn k times in a
    # resample contributes its TPw/pixel-count k times (NOT once -- plain
    # "is this segment present" collapsing duplicates would systematically
    # under-count the on-average ~37% of segments missing from any
    # size-n-with-replacement draw, biasing the bootstrap distribution
    # below the full-sample point estimate; caught and fixed in this pass).
    # FPw's N(x) kernel is a *geometric* max over however many distinct
    # ground-truth locations are present -- a duplicated segment doesn't
    # create new geography -- so FPw correctly uses segment *presence*
    # (distinct ids only), unaffected by multiplicity.
    #
    # Speed: M(y) = windowed_max_prediction(p) depends ONLY on the
    # (fixed-across-resamples) prediction surface, never on ground truth, so
    # it is computed ONCE here and reused, turning each resample's FPw/N
    # term into one distance_transform_edt instead of a full ~29-offset
    # windowed-max recompute (verified to match the direct formula exactly
    # in tests/test_metric.py::test_precomputed_M_matches_direct). TPw/FNw
    # are then recombined by hand with the segment-count weights above.
    p_clipped = np.clip(pred_holdout_eval, 0.0, 1.0)
    p_clipped = np.where(valid_mask, p_clipped, 0.0)
    M = windowed_max_prediction(p_clipped)
    hy, hx = np.where(holdout_mask)
    hseg = segment_ids[hy, hx]
    max_seg_id = int(holdout_seg_list.max())
    tpw_per_seg = np.bincount(hseg, weights=M[hy, hx], minlength=max_seg_id + 1)
    npix_per_seg = np.bincount(hseg, minlength=max_seg_id + 1)

    boot_dtis = []
    rng_boot = np.random.default_rng(SEED + 1)
    for b in range(N_BOOTSTRAP):
        resample = rng_boot.choice(holdout_seg_list, size=len(holdout_seg_list), replace=True)
        counts = np.bincount(resample, minlength=max_seg_id + 1)
        tp_w_boot = float(np.sum(counts * tpw_per_seg))
        n_gt_boot = float(np.sum(counts * npix_per_seg))
        fn_w_boot = n_gt_boot - tp_w_boot

        drawn = np.unique(resample)
        keep = np.isin(hseg, drawn)
        if not keep.any():
            continue
        boot_gt_presence = np.zeros_like(fault)
        boot_gt_presence[hy[keep], hx[keep]] = True
        dist_to_boot = distance_transform_edt(~boot_gt_presence, sampling=(100.0, 100.0))
        N_boot = np.clip(1.0 - dist_to_boot / 300.0, 0.0, None)
        fp_w_boot = float(np.sum(p_clipped * (1.0 - N_boot)))

        dti_boot = tp_w_boot / (tp_w_boot + 0.2 * fp_w_boot + 0.8 * fn_w_boot + 1e-9)
        boot_dtis.append(dti_boot)
    boot_dtis = np.array(boot_dtis)
    ci_lo, ci_hi = (float(np.percentile(boot_dtis, 2.5)), float(np.percentile(boot_dtis, 97.5)))
    log(f"  HOLDOUT-DTI 95% CI (spatial block bootstrap, n={len(boot_dtis)}) = "
        f"[{ci_lo:.4f}, {ci_hi:.4f}]")

    elapsed = time.time() - t0
    report = {
        "experiment_id": 1,
        "hypothesis": "H-GEOD-STRAIN",
        "mechanism": (
            "Active geodetic dilatation-rate / shear-strain-rate anomalies "
            "(bands geod_dilaterate, geod_shearrate) colocate with active "
            "normal/oblique-slip faulting independent of prior fault mapping."
        ),
        "non_fault_mimic_confound": (
            "Aquifer-compaction subsidence, volcanic inflation/deflation, and "
            "geodetic processing noise can produce strain-rate anomalies with "
            "no real brittle fault discontinuity; not resolved by this lane."
        ),
        "data_provenance": {
            "training_features_sha256": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
            "labels_sha256": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
            "sample_submission_sha256": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
            "mirror_note": (
                "restored via GitHub API from buffedlizard55-lab/GEMSDOE and "
                "buffedlizard55-lab/GEMSDOE24 pinned refs, per their own "
                "registry/data_manifest.json; integrity-pinned, NOT "
                "organizer-authenticated -- see docs/LIMITATIONS.md"
            ),
        },
        "lane_features": canary_features,
        "n_segments_total": int(n_segments),
        "n_segments_train": len(train_seg_ids),
        "n_segments_holdout": len(holdout_seg_ids),
        "n_fault_px_total": n_fault_px,
        "n_fault_px_train": n_train_px,
        "n_fault_px_holdout": n_holdout_px,
        "leakage_canary_auc": canary_results,
        "leakage_canary_verdict": (
            "ok (no single feature exceeds 0.90 AUC)"
            if all(v <= 0.90 for v in canary_results.values())
            else "SUSPECTED LEAKAGE"
        ),
        "joint_lane_train_auc": train_auc,
        "holdout_dti_point_estimate": result.dti,
        "holdout_dti_95ci": [ci_lo, ci_hi],
        "holdout_dti_bootstrap_n": int(len(boot_dtis)),
        "holdout_dti_tp_w": result.tp_w,
        "holdout_dti_fp_w": result.fp_w,
        "holdout_dti_fn_w": result.fn_w,
        "holdout_dti_n_withheld_fault_px": result.n_ground_truth_positive,
        "metric_label": (
            f"HOLDOUT-DTI(gems.metric v1, {result.n_ground_truth_positive} withheld "
            f"fault px across {len(holdout_seg_ids)} segments, 95% CI "
            f"[{ci_lo:.4f}, {ci_hi:.4f}], spatial block bootstrap n={len(boot_dtis)})"
        ),
        "wall_clock_seconds": elapsed,
        "model_coefficients": {
            "features": canary_features,
            "coef": clf.coef_[0].tolist(),
            "intercept": float(clf.intercept_[0]),
            "standardization_mean": mu.tolist(),
            "standardization_std": sigma.tolist(),
        },
    }
    (OUT / "experiment_report.json").write_text(json.dumps(report, indent=2))
    log(f"wrote {OUT / 'experiment_report.json'}")
    log(f"DONE in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
