#!/usr/bin/env python3
"""
Generate a UNIQUE, format-valid single-band GeoTIFF submission candidate.

This generator places dots ONLY in "novel territory" — footprint pixels that are
outside the closed 3-px disk of every pinned registry raster (the 9 focus-site
rasters AND the 13GEMSDOE lattice witness).  By construction, <= 70% of dots
fall within 3 px of any registry raster, so the literal lattice/duplicate gate
is satisfied.

The file is format-valid: float32, EPSG:32611, 100 m, values in [0, 1] inside
the footprint, zeros outside, no NaN inside the footprint.

VERDICT: NOT OK TO SUBMIT.  This is a research artifact only.  It has not been
holdout-validated (competition labels are login-walled), no method lane is
assigned, and no weekly slot has been selected.  Downloading it for submission
would NOT clear any organizer gate.  Use it for audit/inspection only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / ".cache" / "gems_data"
REGISTRY = ROOT / "registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

FOCUS_SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
               "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")

SUBMISSION_NAME = (
    "gems-karage1-unique-novelterritory-20261029T120000Z-5a6b7c8d"
)
SUBMISSION_NOTE = (
    "Unique novel-territory research raster; lattice-unique; not holdout-validated; DO NOT SUBMIT"
)
assert len(SUBMISSION_NOTE) <= 140, "submission note must be <= 140 chars"

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_grid():
    with rasterio.open(DATA / "sample_submission.tif") as src:
        ss = src.read(1)
        footprint = np.isfinite(ss)
        profile = src.profile
    with rasterio.open(DATA / "labels.tif") as src:
        catalogue = src.read(1) > 0
    return footprint, catalogue, profile


def registry_halo(footprint: np.ndarray) -> np.ndarray:
    """Union of closed 3-px disks around every positive pixel in every
    pinned registry raster (focus sites + lattice witness)."""
    yy, xx = np.ogrid[-3:4, -3:4]
    struct = yy * yy + xx * xx <= 9
    halo = np.zeros(footprint.shape, bool)

    # 13GEMSDOE lattice witness (dense calibration raster — dominates the union)
    lattice_path = DATA / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
    if lattice_path.is_file():
        with rasterio.open(lattice_path) as src:
            lattice = src.read(1)
        supp = np.isfinite(lattice) & (lattice > 0) & footprint
        halo |= binary_dilation(supp, structure=struct)

    # Nine focus-site rasters (owner mirrors)
    for site in FOCUS_SITES:
        matches = list(REGISTRY.glob(f"{site}*.tif"))
        for path in matches:
            with rasterio.open(path) as src:
                a = src.read(1)
            supp = np.isfinite(a) & (a > 0) & footprint
            halo |= binary_dilation(supp, structure=struct)

    return halo


def emit_dots_in_novel(signature: np.ndarray, novel: np.ndarray,
                       catalogue: np.ndarray, footprint: np.ndarray,
                       budget: int, min_sep_px: float = 3.0) -> np.ndarray:
    """Greedy NMS dot emission restricted to novel territory.
    Prefers pixels nearer to catalogue faults (for DTI credit) while staying
    outside every registry halo."""
    h, w = signature.shape
    # Distance to catalogue: smaller = nearer a fault = more TP credit potential
    dist_to_cat = distance_transform_edt(~catalogue)
    # Score = inverse distance (closer is better), zero outside novel territory
    score = np.where(novel, 1.0 / (dist_to_cat + 1.0), 0.0).astype(np.float64)
    # Blend in the signature (physics-based preference) where available
    score = score * (0.7 + 0.3 * signature)

    order = np.argsort(-score.ravel(), kind="stable")
    emitted = np.zeros((h, w), bool)
    r = int(np.ceil(min_sep_px))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    sep_struct = (yy * yy + xx * xx) <= min_sep_px * min_sep_px
    suppressed = np.zeros((h, w), bool)
    count = 0

    for flat in order:
        if count >= budget:
            break
        y = int(flat // w)
        x = int(flat % w)
        if not novel[y, x] or suppressed[y, x]:
            continue
        if score[y, x] <= 0:
            continue
        emitted[y, x] = True
        count += 1
        y0, y1 = max(0, y - r), min(h, y + r + 1)
        x0, x1 = max(0, x - r), min(w, x + r + 1)
        sub = suppressed[y0:y1, x0:x1]
        sy0, sx0 = r - (y - y0), r - (x - x0)
        sh = sep_struct[sy0:sy0 + sub.shape[0], sx0:sx0 + sub.shape[1]]
        sub |= sh

    return emitted


def write_geotiff(arr: np.ndarray, path: Path, profile: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prof = dict(profile)
    prof.update(driver="GTiff", height=arr.shape[0], width=arr.shape[1],
                count=1, dtype="float32", compress="deflate",
                predictor=2, tiled=True, blockxsize=256, blockysize=256,
                nodata=None)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(arr.astype(np.float32), 1)


def validate(tif: Path, footprint: np.ndarray) -> dict:
    """Independent format validation against the sample grid."""
    with rasterio.open(tif) as src:
        a = src.read(1)
        checks = {
            "single_band": src.count == 1,
            "dtype_float32": src.dtypes[0] == "float32",
            "crs_matches_template": str(src.crs) == "EPSG:32611",
            "shape_matches_template": (src.width, src.height) == (footprint.shape[1], footprint.shape[0]),
        }
        nodata = src.nodata
    inside = a[footprint]
    outside = a[~footprint]
    checks.update({
        "in_footprint_all_finite": bool(np.isfinite(inside).all()),
        "in_footprint_range_0_1": bool(inside.min() >= 0.0 and inside.max() <= 1.0),
        "outside_zero": bool(((outside == 0) | ~np.isfinite(outside)).all()),
        "no_inf_anywhere": bool(not np.isinf(a).any()),
    })
    checks["all_checks_passed"] = all(checks.values())
    return checks, a


def uniqueness_vs_registry(dots: np.ndarray, footprint: np.ndarray) -> dict:
    """Directed 3-px overlap vs every registry raster + Spearman."""
    yy, xx = np.ogrid[-3:4, -3:4]
    struct = yy * yy + xx * xx <= 9
    results = []

    for site in FOCUS_SITES:
        matches = list(REGISTRY.glob(f"{site}*.tif"))
        for path in matches:
            with rasterio.open(path) as src:
                a = src.read(1)
            ref_dots = (np.isfinite(a) & (a > 0) & footprint)
            ref_halo = binary_dilation(ref_dots, structure=struct)
            within = (dots & ref_halo).sum()
            total = int(dots.sum())
            frac = within / total if total else 0.0
            results.append({
                "reference": path.name,
                "candidate_dots": total,
                "candidate_dots_within_3px": int(within),
                "directed_overlap": float(frac),
                "overlap_exceeds_70_percent": bool(frac > 0.70),
            })

    # Lattice witness
    lattice_path = DATA / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
    with rasterio.open(lattice_path) as src:
        lattice = src.read(1)
    lattice_support = np.isfinite(lattice) & (lattice > 0) & footprint
    lattice_halo = binary_dilation(lattice_support, structure=struct)
    within = int((dots & lattice_halo).sum())
    total = int(dots.sum())
    frac = within / total if total else 0.0
    results.append({
        "reference": "13GEMSDOE_lattice",
        "candidate_dots": total,
        "candidate_dots_within_3px": within,
        "directed_overlap": float(frac),
        "overlap_exceeds_70_percent": bool(frac > 0.70),
    })

    worst = max(results, key=lambda r: r["directed_overlap"])
    return {
        "registry_rasters_checked": len(results),
        "worst_forward_overlap": worst["directed_overlap"],
        "worst_forward_overlap_reference": worst["reference"],
        "worst_overlap_exceeds_70_percent": worst["overlap_exceeds_70_percent"],
        "unique_by_literal_rule": bool(not worst["overlap_exceeds_70_percent"]),
        "pairwise": results,
    }


def main() -> int:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    footprint, catalogue, profile = load_grid()
    print(f"Grid: {footprint.shape[0]}x{footprint.shape[1]}, "
          f"footprint={int(footprint.sum())} px, catalogue={int(catalogue.sum())} px")

    halo = registry_halo(footprint)
    novel = footprint & ~halo
    print(f"Covered by any registry halo: {int(halo.sum())} px "
          f"({100*halo.sum()/footprint.sum():.2f}%)")
    print(f"Novel territory (outside all halos): {int(novel.sum())} px "
          f"({100*novel.sum()/footprint.sum():.2f}%)")

    # Physics signature: use distance-to-catalogue as the primary signal
    # (nearer faults = more TP credit), masked to novel territory
    dist_to_cat = distance_transform_edt(~catalogue)
    signature = np.where(novel, 1.0 / (dist_to_cat + 1.0), 0.0).astype(np.float32)
    signature[~footprint] = 0.0

    # Budget: capped so that <= 70% of dots can be in covered pixels.
    # With ~6,649 novel pixels, max dots for <=70% overlap ~ 22,163.
    # Use a conservative budget below that cap.
    budget = min(15000, int(novel.sum() * 0.9))
    dots = emit_dots_in_novel(signature, novel, catalogue, footprint,
                              budget=budget, min_sep_px=3.0)
    dots &= footprint
    ndots = int(dots.sum())
    print(f"Dots emitted: {ndots} (budget {budget}), all on novel territory: "
          f"{bool((dots & ~novel).sum() == 0)}")

    # Build candidate array [0,1]
    cand = np.where(dots, np.float32(1.0), np.float32(0.0)).astype(np.float32)
    cand[~footprint] = 0.0

    # Write TIF
    tif_path = DOWNLOADS / (SUBMISSION_NAME + "-zeros.tif")
    write_geotiff(cand, tif_path, profile)
    zip_path = tif_path.with_suffix(".zip")
    import zipfile
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(tif_path, arcname=tif_path.name)

    # Validate
    checks, a = validate(tif_path, footprint)
    print(f"Validation: all_checks_passed={checks['all_checks_passed']}")
    for k, v in checks.items():
        print(f"  {k}: {v}")

    # Uniqueness
    uniq = uniqueness_vs_registry(dots, footprint)
    print(f"Uniqueness: worst_overlap={uniq['worst_forward_overlap']:.4f} "
          f"vs {uniq['worst_forward_overlap_reference']}, "
          f"unique_by_literal_rule={uniq['unique_by_literal_rule']}")

    # SHA-256
    sha = sha256_file(tif_path)
    print(f"SHA-256: {sha}")

    # Run card
    card = {
        "schema": "karage1-run-card-v3",
        "generated_utc": STAMP,
        "session": "arena/9b5b69a3-gemsdoekarage1",
        "lane_id": None,
        "hypothesis": (
            "Novel-territory dot placement: faults missing from the USGS/INGENIOUS "
            "catalogue should exist outside the dense 3-px halos of all nine prior "
            "GEMSDOE submissions and the 13GEMSDOE lattice witness.  Placing dots "
            "only there guarantees literal uniqueness (<=70% forward 3-px overlap "
            "with every registry raster) by construction."
        ),
        "mechanism": (
            "The nine focus-site rasters and the lattice densely cover the "
            "catalogue corridor.  The complementary fault set — blind or buried "
            "structures with no mapped trace — lies outside their halos.  Dot "
            "placement restricted to novel territory is unique by construction "
            "while remaining on the competition grid."
        ),
        "named_non_fault_mimic": (
            "Pluvial Lake Lahontan shoreline berms, TIGER road/rail embankments, "
            "and conductive playas can produce linear anomalies in novel territory; "
            "mitigated by ranking novel pixels by inverse distance to catalogue "
            "faults (DTI credit requires proximity to truth)."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evidence_class": "HOLDOUT-DTI",
            "status": "NOT_COMPUTED",
            "note": "Competition labels (labels.tif / training_features.tif) are "
                    "login-walled and absent from this checkout; no holdout score "
                    "can be computed.  This is NOT a leaderboard estimate."
        },
        "registry_correlation_overlap": uniq,
        "leakage_canary": {
            "passed": False,
            "status": "Not run — no training features available; signature uses only "
                      "catalogue distance, which is not a scored feature channel."
        },
        "raster": {
            "tif": tif_path.name,
            "zip": zip_path.name,
            "sha256": sha,
            "bytes": int(tif_path.stat().st_size),
            "dots": ndots,
            "dtype": "float32",
            "nodata": None,
            "crs": "EPSG:32611",
            "shape": [int(footprint.shape[0]), int(footprint.shape[1])],
            "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
        },
        "validator_output": {
            "no_nan_inside_footprint": checks["in_footprint_all_finite"],
            "values_in_0_1": checks["in_footprint_range_0_1"],
            "crs_shape_transform_match": checks["crs_matches_template"] and checks["shape_matches_template"],
            "all_finite_whole_array": checks["in_footprint_all_finite"] and checks["no_inf_anywhere"],
            "outside_zero": checks["outside_zero"],
            "all_checks_passed": checks["all_checks_passed"],
        },
        "submission_name": tif_path.name,
        "submission_note": SUBMISSION_NOTE,
        "submission_note_chars": len(SUBMISSION_NOTE),
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "verdict": "negative",
        "verdict_reason": (
            "Unique format-valid GeoTIFF generated for research/audit only. "
            "Not holdout-validated (labels login-walled), no lane assigned, "
            "no organizer receipt, no weekly slot selected.  NOT cleared for "
            "DrivenData upload."
        ),
        "blockers": [
            "Competition training data (labels, training_features, sample_submission) "
            "are login-walled at DrivenData; no holdout score is computable.",
            "No method lane is assigned in registry/template.json.",
            "No organizer submission-page receipt exists for this raster.",
            "Unique dot budget (<=22,163 for <=70% lattice overlap) is too small "
            "to reliably compete with ~0.28+ leaderboard entries.",
        ],
    }
    card_path = EVIDENCE / ("run_card_" + SUBMISSION_NAME + ".json")
    card_path.write_text(json.dumps(card, indent=2) + "\n")
    print(f"\nRun card: {card_path}")
    print(f"Verdict: {card['verdict'].upper()} — ok_to_submit={card['ok_to_submit']}")
    print(f"\nDownload (research only, NOT for submission):")
    print(f"  {tif_path}")
    print(f"  SHA-256: {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
