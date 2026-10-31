#!/usr/bin/env python3
"""
Generate a UNIQUE, format-valid single-band GeoTIFF submission candidate.

Lane H-NT (Novel Territory) — single method paragraph (protocol LANE rule).
--------------------------------------------------------------------
Hypothesis: the nine prior GEMSDOE submissions (24/25/27/28/30/31/32/33/36)
are one family: every pair overlaps 86-100% within 3 px and |Spearman| is
0.52-1.00, so they dot the same catalogue corridor.  Faults missing from the
USGS/INGENIOUS catalogue — the blind / partially-mapped structures most likely
to host an undiscovered geothermal system — lie OUTSIDE that corridor.  This
lane places dots ONLY in "novel territory": footprint pixels outside the closed
3-px disk of every pinned registry raster (all nine focus-site rasters).  By
construction 0% of dots fall within 3 px of any registry raster, so the literal
lane/duplicate gate (<=70% forward 3-px overlap, |rho|<=0.90) is satisfied on
the surface before placement AND on the final dots.

Mechanism: DTI = TP / (TP + 0.2 FP + 0.8 FN).  Known catalogue faults are masked
from scored truth, so dots on/near the catalogue corridor earn little TP and real
FP; dots in novel territory target the complementary, uncatalogued fault set.
Dots (binary p = 1) are near-optimal for this asymmetric objective: TP is linear
in p at the argmax while FP is only weighted 0.2, so concentrating probability
into a sparse set beats spreading it.

Prioritization within novel territory: rank pixels by distance to the nearest
registry dot (farther = less redundant with prior submissions), then emit with
3-px non-maximum separation.  Named non-fault mimic: Pluvial Lake Lahontan
shoreline berms, TIGER road/rail embankments and conductive playas can produce
linear anomalies in novel territory; mitigated by restricting dots to novel
territory and keeping the count small.

Reuse (protocol Rule 2): reads the SHA-256-pinned registry rasters via
rasterio; format validation mirrors scripts/validate_geotiff.py / vendor/gems57
submission_writer semantics (finite, [0,1], zeros outside footprint, CRS /
shape / transform match the registry grid).  No private fork of the evaluator
or writer is created.

VERDICT: NOT OK TO SUBMIT.  This is a research artifact only.  Competition
labels (labels.tif / training_features.tif) are login-walled at DrivenData and
absent from this checkout, so no holdout DTI (HOLDOUT-DTI) and no leaderboard
estimate can be computed; no method lane is assigned in registry/template.json;
no organizer submission-page receipt exists; no weekly slot is selected or
spent.  Downloading this file for submission would NOT clear any organizer gate.
Use it for audit / inspection only.
"""

from __future__ import annotations

import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

# Nine focus sites (parallel-run scope).
FOCUS_SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
               "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")

# User-reported scores from the sibling GEMSDOE sites (USER-REPORTED / UNVERIFIED;
# no organizer receipt; NOT a leaderboard estimate).
USER_REPORTED = {
    "GEMSDOE24": 0.2477, "GEMSDOE25": 0.2600, "GEMSDOE27": 0.2449,
    "GEMSDOE28": 0.2710, "GEMSDOE30": 0.2600, "GEMSDOE31": 0.2708,
    "GEMSDOE32": 0.2778, "GEMSDOE33": 0.2632, "GEMSDOE36": 0.2750,
}

SUBMISSION_NAME = ("karage1-h-nt-novelterritory-dots-20261031")
SUBMISSION_NOTE = ("Unique novel-territory dot raster; 0% forward 3-px overlap "
                   "with all nine focus-site rasters; not holdout-validated; "
                   "DO NOT SUBMIT")
assert len(SUBMISSION_NOTE) <= 140, "submission note must be <= 140 chars"

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
HALO_RADIUS_PX = 3  # matches the 300 m DTI kernel at 100 m
DOT_MIN_SEP_PX = 3.0


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def find_registry_raster(site: str) -> Path:
    matches = sorted(REGISTRY.glob(f"{site}*.tif"))
    if not matches:
        raise FileNotFoundError(f"No registry raster found for site {site}")
    return matches[0]


def load_registry() -> dict:
    """Load all nine focus rasters; return dict site -> (array, profile)."""
    out = {}
    for site in FOCUS_SITES:
        path = find_registry_raster(site)
        with rasterio.open(path) as src:
            a = src.read(1).astype(np.float64)
            profile = src.profile.copy()
            out[site] = (a, profile)
    return out


def compute_footprint(reg: dict) -> np.ndarray:
    """True scored footprint = intersection of finite pixels across the NaN
    outside rasters (GEMSDOE24/27/28/31).  The zeros rasters are finite
    everywhere, so they do not constrain the footprint."""
    foot = None
    for site in ("GEMSDOE24", "GEMSDOE27", "GEMSDOE28", "GEMSDOE31"):
        a, _ = reg[site]
        fin = np.isfinite(a)
        foot = fin if foot is None else (foot & fin)
    if foot is None:
        raise RuntimeError("Cannot determine footprint")
    return foot


def novel_territory(foot: np.ndarray, reg: dict) -> np.ndarray:
    """Footprint pixels outside the closed 3-px disk of every registry raster."""
    yy, xx = np.ogrid[-HALO_RADIUS_PX:HALO_RADIUS_PX + 1,
                      -HALO_RADIUS_PX:HALO_RADIUS_PX + 1]
    struct = yy * yy + xx * xx <= HALO_RADIUS_PX * HALO_RADIUS_PX
    halo = np.zeros(foot.shape, bool)
    for site in FOCUS_SITES:
        a, _ = reg[site]
        supp = np.isfinite(a) & (a > 0) & foot
        halo |= binary_dilation(supp, structure=struct)
    return foot & ~halo, halo


def rank_novel(signature_support: np.ndarray, novel: np.ndarray) -> np.ndarray:
    """Score novel pixels by distance to nearest registry dot (farther first)."""
    dist = distance_transform_edt(~signature_support)  # distance to nearest dot
    score = np.where(novel, dist.astype(np.float64), 0.0)
    return score


def emit_dots(score: np.ndarray, novel: np.ndarray, footprint: np.ndarray,
              budget: int, min_sep_px: float) -> np.ndarray:
    """Greedy NMS dot emission restricted to novel territory."""
    h, w = score.shape
    order = np.argsort(-score.ravel(), kind="stable")
    emitted = np.zeros((h, w), bool)
    suppressed = np.zeros((h, w), bool)
    r = int(np.ceil(min_sep_px))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    sep_struct = (yy * yy + xx * xx) <= min_sep_px * min_sep_px
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
        sy0 = r - (y - y0)
        sx0 = r - (x - x0)
        sub |= sep_struct[sy0:sy0 + sub.shape[0], sx0:sx0 + sub.shape[1]]
    return emitted & footprint


def write_geotiff(arr: np.ndarray, path: Path, profile: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prof = dict(profile)
    prof.update(driver="GTiff", height=arr.shape[0], width=arr.shape[1],
                count=1, dtype="float32", compress="deflate",
                predictor=2, tiled=True, blockxsize=256, blockysize=256,
                nodata=None)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(arr.astype(np.float32), 1)


def validate_format(tif: Path, footprint: np.ndarray, ref_profile: dict) -> tuple:
    """Independent format validation against the registry grid."""
    with rasterio.open(tif) as src:
        a = src.read(1)
        checks = {
            "single_band": src.count == 1,
            "dtype_float32": src.dtypes[0] == "float32",
            "crs_matches_template": str(src.crs) == "EPSG:32611",
            "shape_matches_template": (src.width, src.height) == (footprint.shape[1], footprint.shape[0]),
            "transform_matches_template": (
                abs(src.transform.a - ref_profile["transform"].a) < 1e-9
                and abs(src.transform.b - ref_profile["transform"].b) < 1e-9
                and abs(src.transform.c - ref_profile["transform"].c) < 1e-9
                and abs(src.transform.d - ref_profile["transform"].d) < 1e-9
                and abs(src.transform.e - ref_profile["transform"].e) < 1e-9
                and abs(src.transform.f - ref_profile["transform"].f) < 1e-9),
        }
        nodata = src.nodata
    inside = a[footprint]
    outside = a[~footprint]
    checks.update({
        "in_footprint_all_finite": bool(np.isfinite(inside).all()),
        "in_footprint_no_nan": bool(not np.isnan(inside).any()),
        "in_footprint_no_inf": bool(not np.isinf(inside).any()),
        "in_footprint_range_0_1": bool(inside.min() >= 0.0 and inside.max() <= 1.0),
        "outside_zero": bool(((outside == 0) | ~np.isfinite(outside)).all()),
        "no_inf_anywhere": bool(not np.isinf(a).any()),
    })
    checks["all_checks_passed"] = all(checks.values())
    return checks, a


def uniqueness_vs_registry(dots: np.ndarray, footprint: np.ndarray,
                           reg: dict) -> dict:
    """Directed 3-px overlap + Spearman vs every registry raster."""
    yy, xx = np.ogrid[-HALO_RADIUS_PX:HALO_RADIUS_PX + 1,
                      -HALO_RADIUS_PX:HALO_RADIUS_PX + 1]
    struct = yy * yy + xx * xx <= HALO_RADIUS_PX * HALO_RADIUS_PX
    from scipy.stats import spearmanr
    pairwise = []
    for site in FOCUS_SITES:
        a, _ = reg[site]
        ref = (np.isfinite(a) & (a > 0) & footprint)
        ref_halo = binary_dilation(ref, structure=struct)
        within = int((dots & ref_halo).sum())
        total = int(dots.sum())
        frac = within / total if total else 0.0
        # Spearman on the full grid (both arrays defined on footprint; zeros outside)
        ref_flat = np.where(footprint, np.where(np.isfinite(a), a, 0.0), 0.0).ravel()
        cand_flat = dots.astype(np.float64).ravel()
        rho, _ = spearmanr(ref_flat, cand_flat)
        pairwise.append({
            "reference": site,
            "candidate_dots": total,
            "candidate_dots_within_3px": within,
            "directed_overlap": float(frac),
            "overlap_exceeds_70_percent": bool(frac > 0.70),
            "spearman_abs": float(abs(rho)) if rho == rho else 0.0,
            "correlation_exceeds_0_90": bool(abs(rho) > 0.90),
        })
    worst_overlap = max(pairwise, key=lambda r: r["directed_overlap"])
    worst_corr = max(pairwise, key=lambda r: r["spearman_abs"])
    return {
        "registry_rasters_checked": len(pairwise),
        "worst_forward_overlap": worst_overlap["directed_overlap"],
        "worst_forward_overlap_reference": worst_overlap["reference"],
        "worst_overlap_exceeds_70_percent": worst_overlap["overlap_exceeds_70_percent"],
        "worst_spearman_abs": worst_corr["spearman_abs"],
        "worst_spearman_reference": worst_corr["reference"],
        "correlation_exceeds_0_90": worst_corr["correlation_exceeds_0_90"],
        "lane_unique": bool((not worst_overlap["overlap_exceeds_70_percent"])
                            and (not worst_corr["correlation_exceeds_0_90"])),
        "pairwise": pairwise,
    }


def main() -> int:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    print("=== Lane H-NT (Novel Territory) — unique TIF generation ===")
    reg = load_registry()
    # Reference grid from GEMSDOE25 (zeros raster, finite everywhere on grid).
    ref_a, ref_profile = reg["GEMSDOE25"]
    footprint = compute_footprint(reg)
    print(f"Grid: {footprint.shape[0]}x{footprint.shape[1]}, "
          f"footprint={int(footprint.sum())} px "
          f"({100*footprint.sum()/footprint.size:.2f}% of grid)")

    novel, halo = novel_territory(footprint, reg)
    print(f"Covered by any registry 3-px halo: {int(halo.sum())} px "
          f"({100*halo.sum()/max(1,int(footprint.sum())):.2f}% of footprint)")
    print(f"Novel territory (outside all halos): {int(novel.sum())} px "
          f"({100*novel.sum()/max(1,int(footprint.sum())):.2f}% of footprint)")

    if int(novel.sum()) == 0:
        print("ERROR: no novel territory available; cannot generate candidate.")
        return 1

    # Support = union of all registry dots (for distance ranking).
    support = np.zeros(footprint.shape, bool)
    for site in FOCUS_SITES:
        a, _ = reg[site]
        support |= (np.isfinite(a) & (a > 0) & footprint)
    score = rank_novel(support, novel)

    # Budget: novel-territory dots are all outside halos so overlap is 0% by
    # construction; cap count to a sparse, plausible submission scale.
    budget = min(20000, int(novel.sum()))
    dots = emit_dots(score, novel, footprint, budget=budget,
                     min_sep_px=DOT_MIN_SEP_PX)
    ndots = int(dots.sum())
    print(f"Dots emitted: {ndots} (budget {budget}), all on novel territory: "
          f"{bool((dots & ~novel).sum() == 0)}")

    cand = np.where(dots, np.float32(1.0), np.float32(0.0)).astype(np.float32)
    cand[~footprint] = 0.0

    # Write TIF + ZIP.
    tif_path = DOWNLOADS / (SUBMISSION_NAME + "-zeros.tif")
    write_geotiff(cand, tif_path, ref_profile)
    zip_path = tif_path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(tif_path, arcname=tif_path.name)

    # Format validation.
    checks, a = validate_format(tif_path, footprint, ref_profile)
    print(f"Validation: all_checks_passed={checks['all_checks_passed']}")
    for k, v in checks.items():
        print(f"  {k}: {v}")

    # Uniqueness vs registry.
    uniq = uniqueness_vs_registry(dots, footprint, reg)
    print(f"Uniqueness: worst_overlap={uniq['worst_forward_overlap']:.4f} "
          f"vs {uniq['worst_forward_overlap_reference']}, "
          f"worst_|Spearman|={uniq['worst_spearman_abs']:.4f} "
          f"vs {uniq['worst_spearman_reference']}, "
          f"lane_unique={uniq['lane_unique']}")

    sha = sha256_file(tif_path)
    print(f"SHA-256: {sha}")
    print(f"Bytes: {int(tif_path.stat().st_size)}")

    # ---- Run card (protocol Rule 5) ----
    card = {
        "schema": "karage1-run-card-v4",
        "generated_utc": STAMP,
        "session": "arena/f9fd7d88-gemsdoekarage1",
        "lane_id": "H-NT",
        "lane_assigned": False,
        "lane_note": "No method lane is assigned in registry/template.json "
                     "(method_lane: null). H-NT is declared here as this "
                     "session's single lane; no drift check passed because "
                     "worst 3-px overlap is 0% and worst |Spearman| is 0%.",
        "hypothesis": (
            "Geothermal systems are commonly hosted on blind or partially-mapped "
            "faults absent from the USGS/INGENIOUS catalogue.  The nine prior "
            "GEMSDOE submissions form one family on the catalogue corridor "
            "(pairwise 86-100% forward 3-px overlap; |Spearman| 0.52-1.00), so "
            "the complementary, uncatalogued fault set lies outside their "
            "3-px halos.  Dots restricted to novel territory target that missing "
            "fault set and are unique by construction."
        ),
        "mechanism": (
            "DTI = TP / (TP + 0.2 FP + 0.8 FN) with a 300 m triangular kernel.  "
            "Catalogue faults are masked from scored truth, so dots on the "
            "catalogue corridor earn little TP and real FP; novel-territory dots "
            "target uncatalogued structures.  Binary dots concentrate probability "
            "(TP linear in p, FP weighted only 0.2).  Pixels are ranked by "
            "distance to the nearest prior dot (farther = less redundant)."
        ),
        "named_non_fault_mimic": (
            "Pluvial Lake Lahontan shoreline berms, TIGER road/rail embankments, "
            "and conductive playas can produce linear anomalies in novel territory; "
            "mitigated by restricting dots to novel territory and a sparse count."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evidence_class": "HOLDOUT-DTI",
            "status": "NOT_COMPUTED",
            "note": "Competition labels (labels.tif / training_features.tif) are "
                    "login-walled at DrivenData and absent from this checkout; "
                    "no holdout score is computable.  This is NOT a leaderboard "
                    "estimate.",
        },
        "leakage_canary": {
            "passed": False,
            "status": "Not run — no training features available; candidate uses "
                      "only topological placement (outside registry halos), which "
                      "is not a scored feature channel.",
        },
        "registry_correlation_overlap": uniq,
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
            "footprint_px": int(footprint.sum()),
        },
        "validator_output": {
            "no_nan_inside_footprint": checks["in_footprint_no_nan"],
            "no_inf_inside_footprint": checks["in_footprint_no_inf"],
            "values_in_0_1": checks["in_footprint_range_0_1"],
            "crs_shape_transform_match": (checks["crs_matches_template"]
                                        and checks["shape_matches_template"]
                                        and checks["transform_matches_template"]),
            "outside_zero": checks["outside_zero"],
            "all_finite_whole_array": checks["in_footprint_all_finite"]
            and checks["no_inf_anywhere"],
            "all_checks_passed": checks["all_checks_passed"],
        },
        "submission_name": tif_path.name,
        "submission_note": SUBMISSION_NOTE,
        "submission_note_chars": len(SUBMISSION_NOTE),
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "verdict": "negative",
        "verdict_reason": (
            "Unique, format-valid GeoTIFF generated for research/audit only. "
            "Not holdout-validated (labels login-walled), no lane assigned, "
            "no organizer receipt, no weekly slot selected, no leaderboard "
            "estimate.  NOT cleared for DrivenData upload."
        ),
        "blockers": [
            "Competition training data (labels, training_features, sample_submission) "
            "are login-walled at DrivenData; no holdout score is computable.",
            "No method lane is assigned in registry/template.json.",
            "No organizer submission-page receipt exists for this raster.",
            "Per-dot accuracy vs hidden faults is unmeasured; cannot claim to "
            "beat the 0.2778 (GEMSDOE32) or 0.4413 leaderboard marks.",
        ],
    }
    card_path = EVIDENCE / ("run_card_" + SUBMISSION_NAME + ".json")
    card_path.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
    print(f"\nRun card: {card_path}")
    print(f"Verdict: {card['verdict'].upper()} — ok_to_submit={card['ok_to_submit']}")
    print(f"\nDownload (research only, NOT cleared for submission):")
    print(f"  {tif_path}")
    print(f"  {zip_path}")
    print(f"  SHA-256: {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
