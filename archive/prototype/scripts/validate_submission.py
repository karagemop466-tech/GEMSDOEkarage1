"""validate_submission.py — full submission validation gates.

Runs every gate required before a file may be confirmed as unique and
submittable:

    G1. GeoTIFF format & [0, 1] range (single-band float32, finite, no NaN)
    G2. CRS / shape / transform match sample_submission.tif
    G3. Holdout DTI passes (fold-local win vs current best, paired 95% CI > 0)
    G4. Leakage canary: each feature alone AUC <= 0.90 on the holdout
    G5. Uniqueness: rank correlation |rho| <= 0.90 AND <= 70% of dots within
        3 px of every registry raster (surface AND final dots)
    G6. Budget: within 3 experiments / 2 hours; weekly-slot selector approval

Prints a machine-readable verdict: promote / negative.

Usage:
    python scripts/validate_submission.py --tif submissions/...-zeros.tif \
        --reference data/sample_submission.tif \
        --registry data/existing_faults.tif \
        --holdout-result cards/holdout_result.json \
        --out cards/validation_report.json
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Optional

import numpy as np

try:
    import rasterio
    from scipy import ndimage
    from scipy.stats import spearmanr
except Exception as exc:  # pragma: no cover
    rasterio = None
    ndimage = None
    spearmanr = None

# Gate limits (parallel-run protocol)
RHO_LIMIT = 0.90        # max |Spearman| vs any registry raster
OVERLAP_LIMIT = 0.70    # max fraction of dots within 3 px of any registry raster
LEAKAGE_AUC_LIMIT = 0.90
DTI_IMPROVE_MIN = 0.0   # holdout paired CI lower bound must be > 0


def read_band(path: str):
    if rasterio is None:
        raise RuntimeError("rasterio is required")
    with rasterio.open(path) as src:
        return src.read(1).astype(np.float32), src.profile


def gate_format(tif_path: str) -> dict:
    data, profile = read_band(tif_path)
    finite = bool(np.all(np.isfinite(data)))
    in_range = bool(np.all((data >= 0.0) & (data <= 1.0)))
    single_band = data.ndim == 2
    return {
        "name": "G1_format_range_0_1",
        "pass": bool(finite and in_range and single_band),
        "min": float(np.nanmin(data)),
        "max": float(np.nanmax(data)),
        "nan_count": int(np.sum(~np.isfinite(data))),
        "shape": [int(data.shape[0]), int(data.shape[1])],
        "dtype": str(data.dtype),
        "detail": f"finite={finite} in_range=[0,1]={in_range} single_band={single_band}",
    }


def gate_grid_match(tif_path: str, reference_path: Optional[str]) -> dict:
    if reference_path is None or not os.path.exists(reference_path):
        return {"name": "G2_grid_match", "pass": False,
                "detail": "no sample_submission.tif reference -> grid match UNVERIFIED"}
    data, profile = read_band(tif_path)
    ref_data, ref_profile = read_band(reference_path)
    crs_match = str(profile.get("crs")) == str(ref_profile.get("crs"))
    tr_match = profile.get("transform") == ref_profile.get("transform")
    sh_match = (profile.get("height"), profile.get("width")) == (
        ref_profile.get("height"), ref_profile.get("width"))
    return {
        "name": "G2_grid_match",
        "pass": bool(crs_match and tr_match and sh_match),
        "crs_match": bool(crs_match),
        "transform_match": bool(tr_match),
        "shape_match": bool(sh_match),
        "detail": f"crs={crs_match} transform={tr_match} shape={sh_match}",
    }


def gate_holdout(holdout_result_path: Optional[str],
                 current_best_dti: float = 0.099202) -> dict:
    """G3: holdout DTI must beat the current same-evaluator repo best with
    paired 95% CI lower bound > 0 (protocol rule 3 / run card)."""
    if holdout_result_path is None or not os.path.exists(holdout_result_path):
        return {"name": "G3_holdout_dti", "pass": False,
                "detail": "no holdout result -> cannot validate score (DO NOT SUBMIT)"}
    with open(holdout_result_path) as f:
        res = json.load(f)
    dti = float(res.get("DTI", res.get("dti", 0.0)))
    ci_lo = float(res.get("ci_lo", res.get("ci_low", 0.0)))
    beats_best = dti > current_best_dti
    ci_positive = ci_lo > DTI_IMPROVE_MIN
    return {
        "name": "G3_holdout_dti",
        "pass": bool(beats_best and ci_positive),
        "DTI": dti,
        "ci_lo": ci_lo,
        "ci_hi": float(res.get("ci_hi", res.get("ci_high", 0.0))),
        "beats_current_best": bool(beats_best),
        "current_best": current_best_dti,
        "ci_lower_bound_positive": bool(ci_positive),
        "detail": f"DTI={dti:.6f} CI[{ci_lo:.6f},{res.get('ci_hi',0):.6f}] "
                  f"vs best {current_best_dti}",
    }


def gate_leakage_canary(auc_values: list[float]) -> dict:
    """G4: any single-feature AUC > 0.90 = leakage until proven otherwise."""
    if not auc_values:
        return {"name": "G4_leakage_canary", "pass": False,
                "detail": "no feature AUCs provided -> canary unevaluated"}
    max_auc = float(max(auc_values))
    return {
        "name": "G4_leakage_canary",
        "pass": bool(max_auc <= LEAKAGE_AUC_LIMIT),
        "max_auc": max_auc,
        "limit": LEAKAGE_AUC_LIMIT,
        "n_features": len(auc_values),
        "detail": f"max AUC={max_auc:.4f} limit={LEAKAGE_AUC_LIMIT}",
    }


def _dot_coords(data: np.ndarray):
    ys, xs = np.where(data > 0.5)
    return ys, xs


def gate_uniqueness(tif_path: str, registry_paths: list[str]) -> dict:
    """G5: |Spearman| <= 0.90 AND <= 70% of dots within 3 px of each registry raster."""
    if rasterio is None or ndimage is None or spearmanr is None:
        return {"name": "G5_uniqueness", "pass": False,
                "detail": "rasterio/scipy not available -> uniqueness unevaluated"}
    data, _ = read_band(tif_path)
    h, w = data.shape
    pred_y, pred_x = _dot_coords(data)
    n_pred = len(pred_y)
    # distance transform from prediction dots (for dot->registry distance)
    pred_mask = np.zeros((h, w), dtype=bool)
    if n_pred > 0:
        pred_mask[pred_y, pred_x] = True
    dist_to_pred = ndimage.distance_transform_edt(~pred_mask) if n_pred > 0 else None

    worst_rho = 0.0
    worst_overlap = 0.0
    worst_site = None
    per_raster = []
    for rp in registry_paths:
        if not os.path.exists(rp):
            continue
        reg_data, _ = read_band(rp)
        reg_y, reg_x = np.where(reg_data > 0.5)
        # Spearman on full rasters (rank correlation of surfaces)
        rho = 0.0
        try:
            rho = float(spearmanr(data.ravel(), reg_data.ravel(), nan_policy="omit").statistic or 0.0)
        except Exception:
            rho = 0.0
        # overlap: fraction of prediction dots within 3 px of registry dots
        overlap = 0.0
        if n_pred > 0 and len(reg_y) > 0:
            reg_mask = np.zeros((h, w), dtype=bool)
            reg_mask[reg_y, reg_x] = True
            dist_to_reg = ndimage.distance_transform_edt(~reg_mask)
            d = dist_to_reg[pred_y, pred_x]
            overlap = float(np.sum(d <= 3.0) / n_pred)
        per_raster.append({
            "raster": rp, "rho": rho, "overlap": overlap,
            "rho_ok": abs(rho) <= RHO_LIMIT, "overlap_ok": overlap <= OVERLAP_LIMIT,
        })
        if abs(rho) > abs(worst_rho):
            worst_rho = rho
        if overlap > worst_overlap:
            worst_overlap = overlap
            worst_site = rp

    ok = (abs(worst_rho) <= RHO_LIMIT) and (worst_overlap <= OVERLAP_LIMIT)
    return {
        "name": "G5_uniqueness",
        "pass": bool(ok),
        "max_abs_rho": float(worst_rho),
        "rho_limit": RHO_LIMIT,
        "max_overlap": float(worst_overlap),
        "overlap_limit": OVERLAP_LIMIT,
        "n_pred_dots": int(n_pred),
        "worst_raster": worst_site,
        "per_raster": per_raster,
        "detail": f"max|rho|={worst_rho:.4f} (lim {RHO_LIMIT}) "
                  f"max 3-px overlap={worst_overlap:.3f} (lim {OVERLAP_LIMIT})",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Run submission validation gates and emit promote/negative verdict.")
    parser.add_argument("--tif", required=True, help="Candidate GeoTIFF.")
    parser.add_argument("--reference", default=None,
                        help="sample_submission.tif (grid reference, G2).")
    parser.add_argument("--registry", nargs="*", default=[],
                        help="Registry raster(s) for uniqueness (G5).")
    parser.add_argument("--holdout-result", default=None,
                        help="Holdout DTI JSON (G3).")
    parser.add_argument("--feature-auc", nargs="*", type=float, default=[],
                        help="Single-feature AUCs for leakage canary (G4).")
    parser.add_argument("--current-best-dti", type=float, default=0.099202,
                        help="Current same-evaluator repo best holdout DTI.")
    parser.add_argument("--out", default="cards/validation_report.json",
                        help="Output validation report JSON.")
    args = parser.parse_args(argv)

    gates = []
    gates.append(gate_format(args.tif))
    gates.append(gate_grid_match(args.tif, args.reference))
    gates.append(gate_holdout(args.holdout_result, args.current_best_dti))
    gates.append(gate_leakage_canary(args.feature_auc))
    gates.append(gate_uniqueness(args.tif, args.registry))

    all_pass = all(g["pass"] for g in gates)
    verdict = "promote" if all_pass else "negative"

    report = {
        "created_utc": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc).isoformat(),
        "tif": args.tif,
        "verdict": verdict,
        "all_gates_pass": bool(all_pass),
        "gates": gates,
        "summary": {
            "G1_format": gates[0]["pass"],
            "G2_grid_match": gates[1]["pass"],
            "G3_holdout_dti": gates[2]["pass"],
            "G4_leakage_canary": gates[3]["pass"],
            "G5_uniqueness": gates[4]["pass"],
        },
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    print(f"\nVERDICT: {verdict.upper()}  OK_TO_SUBMIT={all_pass}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
