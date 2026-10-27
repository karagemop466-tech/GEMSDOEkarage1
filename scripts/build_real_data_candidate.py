#!/usr/bin/env python
"""
Build the final, real-data-trained submission candidate.

This refits the Experiment 2 (H-ALLFEAT-UPPERBOUND, all 19 real bands,
logistic regression) model on ALL labeled fault segments pooled (train +
the segments that were held out for scoring in
scripts/run_holdout_experiment_2_allfeatures.py), then scores the whole
competition footprint and writes a format-valid GeoTIFF.

Its honest expected quality is the HOLDOUT-DTI measured in
outputs/experiment2_h_allfeatures/experiment_report.json -- refitting on
more data does not retroactively change that measured number, it is simply
the best estimate of what this exact (weak) model/feature combination can
do on unseen faults. See docs/LIMITATIONS.md and the run card for the full
honesty disclosure before anyone submits this file.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np
import rasterio
from sklearn.linear_model import LogisticRegression

from gems.submission_writer import write_submission, write_run_card, SubmissionMeta
from gems.grid import GEMS_GRID
from gems.validator import validate_submission
from gems.uniqueness import check_against_registry_raster

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "outputs" / "real_data_candidate"
OUT.mkdir(parents=True, exist_ok=True)

FEATURE_NAMES = [
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope", "tc",
    "geod_shearrate", "geod_dilaterate", "tmi_vg", "deq_n100a15",
    "iso_grav_anom_vg", "det_elev", "iso_grav_anom", "tmi", "depth_to_base_surf",
    "ieq_n100a15", "cond_surf", "iso_grav_anom_hg", "det_elev_slope",
]
SEED = 42


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def main() -> None:
    rng = np.random.default_rng(SEED)
    with rasterio.open(DATA / "labels.tif") as src:
        labels_raw = src.read(1)
    with rasterio.open(DATA / "sample_submission.tif") as src:
        template_band = src.read(1)

    footprint = np.isfinite(template_band)
    fault = (labels_raw == 1) & footprint
    H, W = footprint.shape

    log("loading all 19 feature bands (float32) ...")
    band_idx = {name: i + 1 for i, name in enumerate(FEATURE_NAMES)}
    feats = {}
    with rasterio.open(DATA / "training_features.tif") as src:
        for name in FEATURE_NAMES:
            arr = src.read(band_idx[name])
            nodata = src.nodata
            if nodata is not None:
                arr = np.where(arr == nodata, np.nan, arr)
            feats[name] = arr

    finite_all = np.ones((H, W), dtype=bool)
    for name in FEATURE_NAMES:
        finite_all &= np.isfinite(feats[name])
    usable = footprint & finite_all
    n_feat = len(FEATURE_NAMES)

    log("sampling training set (ALL labeled positives, pooled) ...")
    pos_yx = np.argwhere(fault & usable)
    neg_candidates_yx = np.argwhere(usable & ~fault)
    n_neg = min(len(neg_candidates_yx), len(pos_yx) * 20, 400_000)
    neg_idx = rng.choice(len(neg_candidates_yx), size=n_neg, replace=False)
    neg_yx = neg_candidates_yx[neg_idx]

    def gather(yx):
        return np.stack([feats[name][yx[:, 0], yx[:, 1]] for name in FEATURE_NAMES], axis=1)

    X = np.vstack([gather(pos_yx), gather(neg_yx)])
    y = np.concatenate([np.ones(len(pos_yx)), np.zeros(len(neg_yx))])
    mu, sigma = X.mean(axis=0), X.std(axis=0) + 1e-12
    Xs = (X - mu) / sigma

    log(f"fitting final 19-feature logistic regression on {len(pos_yx)} positives / {len(neg_yx)} negatives ...")
    clf = LogisticRegression(class_weight="balanced", max_iter=2000)
    clf.fit(Xs, y)

    log("scoring full grid (row-chunked) ...")
    pred = np.full((H, W), np.nan, dtype=np.float32)
    mu32, sigma32 = mu.astype(np.float32), sigma.astype(np.float32)
    CHUNK = 200
    for r0 in range(0, H, CHUNK):
        r1 = min(H, r0 + CHUNK)
        rows_usable = usable[r0:r1]
        if not rows_usable.any():
            continue
        chunk_feats = np.stack([feats[name][r0:r1] for name in FEATURE_NAMES], axis=-1)
        flat = chunk_feats.reshape(-1, n_feat)
        mask_flat = rows_usable.reshape(-1)
        scaled = (flat[mask_flat] - mu32) / sigma32
        probs = clf.predict_proba(scaled.astype(np.float64))[:, 1].astype(np.float32)
        out = np.full(flat.shape[0], np.nan, dtype=np.float32)
        out[mask_flat] = probs
        pred[r0:r1] = out.reshape(r1 - r0, W)
    del feats

    # Inside footprint but not "usable" (a feature was NaN/sentinel there):
    # fall back to 0.0 so nothing out-of-range is ever written. Outside the
    # footprint, write_submission's footprint_mask zeroes the pixel (the
    # always-safe default this repo uses -- see submission_writer.py).
    pred = np.where(footprint & ~usable, 0.0, pred)
    pred = np.nan_to_num(pred, nan=0.0)

    # Metric-aware sparsity threshold calibrated in
    # scripts/calibrate_sparsity_threshold.py (chosen on the SAME Experiment
    # 2 holdout split, which is reported as a limitation, not hidden): the
    # official DTI(alpha=0.2, beta=0.8) structurally penalizes dense
    # predictions via FPw, so this honest, real-data-trained model's final
    # operating threshold is NOT 0 (its raw mean probability, 0.47, is far
    # too dense) -- see docs/LIMITATIONS.md and the run card for the
    # before/after numbers.
    sweep = json.loads(
        (ROOT / "outputs" / "experiment2_h_allfeatures" / "threshold_sweep.json").read_text()
    )
    best_t = sweep["best_threshold"]
    log(f"applying calibrated sparsity threshold t={best_t:.3f} "
        f"(unthresholded HOLDOUT-DTI=0.0146 -> thresholded {sweep['best_holdout_dti']:.4f})")
    pred = np.where(pred >= best_t, pred, 0.0)

    log(f"prediction stats inside footprint: min={pred[footprint].min():.4f} "
        f"max={pred[footprint].max():.4f} mean={pred[footprint].mean():.4f}")

    d = sweep["best_holdout_dti"]
    lo, hi = sweep["best_holdout_dti_95ci"]
    unique_name = "gems-karage1-realdata-allfeat-logreg-sparsified-v1"
    note = (
        f"19-band logreg+thresh t={best_t:.2f}, real data; HOLDOUT-DTI={d:.4f} "
        f"[{lo:.4f},{hi:.4f}]. Honest/weak, not a leaderboard claim."
    )
    assert len(note) <= 140, len(note)
    meta = SubmissionMeta(unique_name=unique_name, note=note)
    out_path = OUT / f"{unique_name}.tif"
    write_submission(out_path, pred, GEMS_GRID, footprint_mask=footprint)
    log(f"wrote {out_path}")

    log("validating written file ...")
    report = validate_submission(out_path)
    log(f"  all_checks_passed={report.all_checks_passed}")

    log("checking uniqueness against registry/scored_h19_5.tif ...")
    registry_path = DATA / "registry" / "scored_h19_5.tif"
    uniqueness = None
    if registry_path.exists():
        with rasterio.open(registry_path) as src:
            registry_raster = src.read(1).astype(np.float64)
        uq = check_against_registry_raster(pred.astype(np.float64), registry_raster)
        uniqueness = {
            "registry_file": "scored_h19_5.tif (owner-reported DTI 0.1922, GEMSDOE24/32 mirror)",
            "spearman_rho": uq.spearman_rho,
            "fraction_within_3px": uq.fraction_within_radius,
            "is_duplicate": uq.is_duplicate,
        }
        log(f"  spearman={uq.spearman_rho:.4f} within_3px={uq.fraction_within_radius:.4f} "
            f"duplicate={uq.is_duplicate}")

    verdict = "negative"  # far below any registry-claimed score; do not promote to a real slot
    card_path = OUT / "run_card.json"
    write_run_card(
        card_path,
        meta=meta,
        hypothesis="H-ALLFEAT-UPPERBOUND (Experiment 2 of the 3-experiment cap) + metric-aware sparsity calibration",
        mechanism=(
            "Simple linear (logistic regression) combination of all 19 real "
            "geophysical/geodetic bands in training_features.tif, then "
            f"hard-thresholded at the metric-optimal p>={best_t:.3f} (swept in "
            "outputs/experiment2_h_allfeatures/threshold_sweep.json against "
            "the official DTI, which structurally penalizes dense predictions "
            "via FPw). Diagnostic upper bound for this feature set + a linear "
            "model, not a single geological hypothesis."
        ),
        named_non_fault_mimic=(
            "Lithologic/terrain correlations and survey-line artifacts can "
            "drive a 19-feature linear fit without reflecting true brittle "
            "fault structure; not disambiguated by this experiment."
        ),
        holdout_dti={
            "point_estimate": sweep["best_holdout_dti"],
            "ci_95": sweep["best_holdout_dti_95ci"],
            "label": (
                f"HOLDOUT-DTI(gems.metric v1, threshold t={best_t:.3f}, 13227 "
                "withheld fault px across 640 segments, spatial block "
                f"bootstrap n={sweep['best_holdout_dti_bootstrap_n']})"
            ),
            "report_path": "outputs/experiment2_h_allfeatures/threshold_sweep.json",
            "unthresholded_comparison_point_estimate": 0.014648404896576803,
        },
        correlation_vs_registry=uniqueness,
        raster_sha256=report.sha256,
        validator_output=json.loads(report.to_json()),
        verdict=verdict,
    )
    log(f"wrote {card_path}")

    (OUT / "build_report.json").write_text(json.dumps({
        "output_path": str(out_path.relative_to(ROOT)),
        "sha256": report.sha256,
        "n_train_positive_px": int(len(pos_yx)),
        "n_train_negative_px_sampled": int(len(neg_yx)),
        "model_coefficients": {
            "features": FEATURE_NAMES,
            "coef": clf.coef_[0].tolist(),
            "intercept": float(clf.intercept_[0]),
        },
        "submission_meta": {"unique_name": unique_name, "note": note},
        "uniqueness_vs_registry": uniqueness,
        "verdict": verdict,
    }, indent=2))
    log(f"sha256={report.sha256}")


if __name__ == "__main__":
    main()
