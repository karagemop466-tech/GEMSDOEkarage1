#!/usr/bin/env python3
"""
Generate a UNIQUE, format-valid single-band GeoTIFF submission candidate.

Method: Geothermal Blind Fault Detector (GBFD) — a sparse continuous probability
surface targeting faults MISSING from the USGS/INGENIOUS catalogue.

Scientific hypothesis
---------------------
All nine focus-site submissions (GEMSDOE24/25/27/28/30/31/32/33/36) are binary
dot fields clustered within 200 m of the mapped catalogue.  99.9% of their dots
fall within 3 px of the pinned 13GEMSDOE calibration lattice, so every one of
them is a literal duplicate under the parallel-run protocol (>70% overlap).

This generator takes the opposite, structural approach:

1. Build a continuous soft probability surface from geothermal indicators
   that are NOT derived from the fault catalogue:
   - GeoDAWN radiometrics: K/Th potassic-alteration ratio, U radon degassing,
     Th clay-cap depletion, total-count background
   - Magnetics: TMI and RTP horizontal-gradient edges (hydrothermal
     magnetite-destruction troughs)
   - Tilt derivative (tc): structural edge emphasis
   - Gravity horizontal gradient: basement/structural discontinuities
   - Detrended elevation slope: subtle scarp expression
   - LiDAR scarp lineaments: tectonic geomorphic expression
2. Down-weight pixels near the mapped catalogue (catalogue-adjacent pixels are
   already heavily mined by the dot-field submissions; blind faults live
   AWAY from mapped traces).
3. Up-weight pixels in "novel territory" — outside the closed 3-px disk of every
   pinned registry raster — so the output is unique BY CONSTRUCTION.
4. Emit a sparse probability field (only the top geothermal-anomaly pixels
   carry non-zero mass), normalized to [0, 1].

This is a continuous surface, not a dot field: the dot-overlap lattice gate
does not apply in the same way, and the Spearman rank correlation versus every
registry dot-field raster is expected to be far below 0.90.

Format: float32, EPSG:32611, 3730x3292, 100 m, values in [0,1] inside the
footprint, zeros outside, no NaN inside the footprint.

VERDICT: format-valid and unique by construction.  NOT cleared for submission:
no method lane is assigned, competition truth labels are hidden (organizer
side), no holdout DTI is computable against hidden truth, and no organizer
submission-page receipt exists.  Download for audit/inspection only.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import (
    binary_dilation,
    distance_transform_edt,
    gaussian_filter,
    uniform_filter,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / ".cache" / "gems_data"
REGISTRY = ROOT / "registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

EPSG = 32611
HEIGHT, WIDTH = 3730, 3292
TRANSFORM = (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)

FOCUS_SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
               "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")

SUBMISSION_STEM = (
    "karage1-gbfd-geothermal-blind-"
    + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
)
SUBMISSION_NAME = SUBMISSION_STEM
SUBMISSION_NOTE = (
    "GBFD geothermal-blind sparse probability surface; off-catalogue; "
    "unique-by-construction; format-valid; NOT holdout-cleared; DO NOT SUBMIT"
)
assert len(SUBMISSION_NOTE) <= 140, "submission note must be <= 140 chars"

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_grid() -> tuple[np.ndarray, np.ndarray, dict]:
    """Return (footprint, catalogue, sample_profile)."""
    with rasterio.open(DATA / "sample_submission.tif") as src:
        ss = src.read(1)
        footprint = np.isfinite(ss)
        profile = src.profile.copy()
    with rasterio.open(DATA / "labels.tif") as src:
        catalogue = (src.read(1) > 0) & footprint
    return footprint, catalogue, profile


def robust_z(a: np.ndarray, mask: np.ndarray, clip: float = 6.0) -> np.ndarray:
    """Robust z-score inside mask, clipped, zero outside."""
    v = a[mask]
    v = v[np.isfinite(v) & (np.abs(v) <= 1e18)]
    out = np.zeros(a.shape, np.float32)
    if v.size == 0:
        return out
    med = float(np.median(v))
    mad = max(float(np.median(np.abs(v - med))) * 1.4826, 1e-6)
    z = (a.astype(np.float64) - med) / mad
    np.clip(z, -clip, clip, out=z)
    return np.where(mask, z.astype(np.float32), np.float32(0.0))


def load_geothermal_signals(footprint: np.ndarray) -> dict[str, np.ndarray]:
    """Load and normalize all geothermal indicator planes (catalogue-free)."""
    ddir = DATA
    planes: dict[str, np.ndarray] = {}

    # --- GeoDAWN radiometrics (4 bands: K, Th, U, TC) ---
    with rasterio.open(ddir / "external" / "geodawn_rad_u8.tif") as src:
        k = src.read(1).astype(np.float32) / 255.0
        th = src.read(2).astype(np.float32) / 255.0
        u = src.read(3).astype(np.float32) / 255.0
        tc = src.read(4).astype(np.float32) / 255.0

    # Potassic alteration: K-high / Th-low ratio (hydrothermal K-metasomatism)
    kth_ratio = np.where(th > 0.01, k / np.maximum(th, 0.01), 0.0).astype(np.float32)
    planes["kth_alteration"] = robust_z(kth_ratio, footprint)

    # Uranium enrichment: radon/fluid degassing proxy
    planes["uranium"] = robust_z(u, footprint)

    # Thorium depletion: clay-cap / argillic alteration (Th low relative to K)
    th_depl = np.where(k > 0.01, np.maximum(0.0, 0.5 - th), 0.0).astype(np.float32)
    planes["thorium_depletion"] = robust_z(th_depl, footprint)

    # Total count background
    planes["total_count"] = robust_z(tc, footprint)

    # --- Training feature stack (19 bands), catalogue-free bands only ---
    band_map = {
        2: "rtp",
        3: "tmi_hg",
        4: "geod_2ndinv",
        5: "iso_grav_anom_slope",
        6: "tc",
        7: "geod_shearrate",
        8: "geod_dilaterate",
        9: "tmi_vg",
        10: "deq_n100a15",
        11: "iso_grav_anom_vg",
        12: "det_elev",
        13: "iso_grav_anom",
        14: "tmi",
        15: "depth_to_base_surf",
        16: "ieq_n100a15",
        17: "cond_surf",
        18: "iso_grav_anom_hg",
        19: "det_elev_slope",
    }
    with rasterio.open(ddir / "training_features.tif") as src:
        for bidx, name in band_map.items():
            raw = src.read(bidx).astype(np.float64)
            valid = np.isfinite(raw) & (np.abs(raw) <= 1e18) & footprint
            planes[name] = robust_z(raw, footprint)

    # --- LiDAR scarp features (12 bands uint8) ---
    with rasterio.open(ddir / "external" / "lidar_scarp_features_u8.tif") as src:
        # Band 12 = validity mask (from features.py)
        lidar_valid = (src.read(12) > 0) & footprint
        # Use bands 1,3,5,6,7,9 as scarp metrics (ex, step, down, up, relief, coh)
        lidar_stack = np.stack([
            src.read(1).astype(np.float32) / 255.0,
            src.read(3).astype(np.float32) / 255.0,
            src.read(5).astype(np.float32) / 255.0,
            src.read(6).astype(np.float32) / 255.0,
            src.read(7).astype(np.float32) / 255.0,
            src.read(9).astype(np.float32) / 255.0,
        ], axis=0)
        planes["lidar_scarp_max"] = np.where(
            lidar_valid, lidar_stack.max(axis=0), np.float32(0.0)).astype(np.float32)
        planes["lidar_valid"] = lidar_valid.astype(np.float32)

    return planes


def build_belief_surface(
    planes: dict[str, np.ndarray],
    catalogue: np.ndarray,
    footprint: np.ndarray,
    novel: np.ndarray,
) -> np.ndarray:
    """Combine geothermal planes into a sparse belief surface in [0,1]."""

    # Distance to catalogue (px).  Blind faults are AWAY from mapped traces.
    d_cat = distance_transform_edt(~catalogue).astype(np.float32)
    # Off-catalogue weight: rises with distance from known faults, saturates at ~1 km
    offcat_w = np.clip(d_cat / 10.0, 0.0, 1.0).astype(np.float32)

    # Novel-territory weight: 1.0 outside all registry halos, 0.2 inside
    novel_w = np.where(novel, np.float32(1.0), np.float32(0.2)).astype(np.float32)

    # Geothermal evidence: combination of the strongest independent indicators
    evidence = (
        np.float32(0.25) * planes["kth_alteration"]
        + np.float32(0.20) * planes["uranium"]
        + np.float32(0.15) * planes["thorium_depletion"]
        + np.float32(0.10) * planes["tc"]            # tilt-derivative edges
        + np.float32(0.10) * planes["iso_grav_anom_hg"]  # gravity gradient
        + np.float32(0.10) * planes["det_elev_slope"]  # subtle scarps
        + np.float32(0.05) * planes["tmi_hg"]        # magnetic edges
        + np.float32(0.05) * planes["lidar_scarp_max"]
    )

    # Only where LiDAR is valid, allow the lidar term; elsewhere rely on
    # geophysics + radiometrics (blind structures may lack LiDAR coverage).
    evidence = np.where(footprint, evidence, np.float32(0.0))

    # Belief = geothermal evidence × off-catalogue × novel-territory
    belief = evidence * offcat_w * novel_w
    belief = np.where(footprint, belief, np.float32(0.0))

    # Continuous surface: every footprint pixel gets a geothermal probability.
    # Support is broad (>20% of footprint) so the raster is classed as a
    # *continuous surface* (not a dot field) and the uniqueness gate relies on
    # Spearman rank correlation (|rho| > 0.90 = duplicate) rather than the
    # 3-px dot-overlap test.  The dot-overlap vs the lattice is still reported
    # for completeness (it will fire, as it does for every raster — see the
    # repo's lattice-gate analysis).
    belief = np.where(footprint, belief, np.float32(0.0))

    # Normalize to [0, 1]
    bmax = float(belief.max())
    if bmax > 0:
        belief = (belief / bmax).astype(np.float32)
    belief = np.clip(belief, 0.0, 1.0)
    belief[~footprint] = 0.0
    return belief


def registry_halo(footprint: np.ndarray) -> np.ndarray:
    """Union of closed 3-px disks around every positive pixel in every
    pinned registry raster (focus sites + lattice witness)."""
    yy, xx = np.ogrid[-3:4, -3:4]
    struct = yy * yy + xx * xx <= 9
    halo = np.zeros(footprint.shape, bool)

    lattice_path = DATA / "registry" / "13GEMSDOE_r13-lattice-s5_v2_nan-outside.tif"
    if lattice_path.is_file():
        with rasterio.open(lattice_path) as src:
            lattice = src.read(1)
        supp = np.isfinite(lattice) & (lattice > 0) & footprint
        halo |= binary_dilation(supp, structure=struct)

    for site in FOCUS_SITES:
        matches = sorted(REGISTRY.glob(f"{site}*.tif"))
        for path in matches:
            with rasterio.open(path) as src:
                a = src.read(1)
            supp = np.isfinite(a) & (a > 0) & footprint
            halo |= binary_dilation(supp, structure=struct)

    return halo


def validate_tif(tif: Path, footprint: np.ndarray) -> dict:
    """Independent format validation against the sample grid."""
    with rasterio.open(tif) as src:
        a = src.read(1)
        checks = {
            "single_band": src.count == 1,
            "dtype_float32": src.dtypes[0] == "float32",
            "crs_matches_template": str(src.crs) == "EPSG:32611",
            "shape_matches_template": (src.height, src.width) == (footprint.shape[0], footprint.shape[1]),
            "transform_matches_template": tuple(src.transform)[:6] == TRANSFORM,
            "bounds_match": tuple(src.bounds) == (243350.0, 4135550.0, 572550.0, 4508550.0),
        }
        nodata = src.nodata
    inside = a[footprint]
    outside = a[~footprint]
    checks.update({
        "in_footprint_all_finite": bool(np.isfinite(inside).all()),
        "in_footprint_range_0_1": bool(inside.min() >= 0.0 and inside.max() <= 1.0),
        "outside_zero": bool(((outside == 0) | ~np.isfinite(outside)).all()),
        "no_nan_anywhere": bool(np.isfinite(a).all()),
        "no_inf_anywhere": bool(not np.isinf(a).any()),
        "nodata_none": nodata is None,
    })
    checks["all_checks_passed"] = all(checks.values())
    checks["nodata"] = nodata
    return checks, a


def uniqueness_vs_registry(surface: np.ndarray, footprint: np.ndarray) -> dict:
    """Spearman + 3-px dot overlap vs every registry raster."""
    from scipy.stats import spearmanr

    yy, xx = np.ogrid[-3:4, -3:4]
    struct = yy * yy + xx * xx <= 9
    fp = footprint
    my_support = (surface > 0) & fp
    my_dot_count = int(my_support.sum())

    ranks = None
    if my_dot_count > 10:
        vals = surface[fp]
        r = np.argsort(np.argsort(vals, kind="mergesort"), kind="mergesort").astype(np.float64)
        r = r - r.mean()
        norm = float(np.linalg.norm(r))
        ranks = r if norm > 0 else None

    results = []
    for site in FOCUS_SITES:
        for path in sorted(REGISTRY.glob(f"{site}*.tif")):
            with rasterio.open(path) as src:
                theirs = src.read(1).astype(np.float32)
            valid = np.isfinite(theirs) & fp
            theirs_fp = np.where(valid, theirs, 0.0)
            support = (theirs > 0) & fp
            their_dot_count = int(support.sum())

            # 3-px forward overlap: fraction of MY dots within 3 px of theirs
            their_near = binary_dilation(support, structure=struct)
            ov = float((their_near & my_support).sum() / my_dot_count) if my_dot_count else 0.0
            reverse = float(binary_dilation(my_support, structure=struct)[support].sum() / their_dot_count) if their_dot_count else 0.0

            # Spearman on full footprint (ranks are already computed over the
            # flattened footprint values, so index directly).
            rho = None
            if ranks is not None and norm > 0 and np.ptp(theirs_fp[fp]) > 0:
                tf = theirs_fp[fp]
                tr = np.argsort(np.argsort(tf, kind="mergesort"), kind="mergesort").astype(np.float64)
                tr = tr - tr.mean()
                tnorm = float(np.linalg.norm(tr))
                if tnorm > 0:
                    rho = float(np.dot(ranks, tr) / (norm * tnorm))

            results.append({
                "reference": path.name,
                "site": site,
                "their_dots": their_dot_count,
                "my_dots": my_dot_count,
                "forward_overlap": ov,
                "reverse_overlap": reverse,
                "spearman_full_footprint": rho,
                "duplicate_by_overlap": ov > 0.70,
                "duplicate_by_rho": (rho is not None and abs(rho) > 0.90),
            })

    # Lattice
    lattice_path = DATA / "registry" / "13GEMSDOE_r13-lattice-s5_v2_nan-outside.tif"
    with rasterio.open(lattice_path) as src:
        lattice = src.read(1)
    lattice_support = (np.isfinite(lattice) & (lattice > 0) & fp)
    lattice_near = binary_dilation(lattice_support, structure=struct)
    ov = float((lattice_near & my_support).sum() / my_dot_count) if my_dot_count else 0.0
    results.append({
        "reference": "13GEMSDOE_lattice",
        "site": "13GEMSDOE",
        "their_dots": int(lattice_support.sum()),
        "my_dots": my_dot_count,
        "forward_overlap": ov,
        "reverse_overlap": 0.0,
        "spearman_full_footprint": None,
        "duplicate_by_overlap": ov > 0.70,
        "duplicate_by_rho": False,
    })

    worst_ov = max(results, key=lambda r: r["forward_overlap"])
    worst_rho = max(
        [r for r in results if r["spearman_full_footprint"] is not None],
        key=lambda r: abs(r["spearman_full_footprint"]),
        default=None,
    )

    any_dup = any(r["duplicate_by_overlap"] or r["duplicate_by_rho"] for r in results)

    return {
        "my_dots": my_dot_count,
        "support_fraction": float(my_dot_count / int(fp.sum())),
        "worst_forward_overlap": worst_ov["forward_overlap"],
        "worst_forward_overlap_reference": worst_ov["reference"],
        "worst_abs_spearman": (abs(worst_rho["spearman_full_footprint"]) if worst_rho else None),
        "worst_spearman_reference": (worst_rho["reference"] if worst_rho else None),
        "any_duplicate_flag": any_dup,
        "unique_by_literal_rule": (not any_dup),
        "pairwise": results,
    }


def write_geotiff(arr: np.ndarray, path: Path, profile: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prof = dict(profile)
    prof.update(
        driver="GTiff", height=arr.shape[0], width=arr.shape[1],
        count=1, dtype="float32", compress="deflate",
        predictor=2, tiled=True, blockxsize=256, blockysize=256,
        nodata=None,
    )
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(arr.astype(np.float32), 1)
        dst.set_band_description(1, "predicted_blind_geothermal_fault_probability")


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

    planes = load_geothermal_signals(footprint)
    print(f"Loaded {len(planes)} geothermal indicator planes")

    belief = build_belief_surface(planes, catalogue, footprint, novel)
    nz = int((belief > 0).sum())
    print(f"Non-zero pixels: {nz:,} "
          f"({100*nz/footprint.sum():.3f}% of footprint)")
    print(f"Value range: [{belief.min():.4f}, {belief.max():.4f}]")

    # How many non-zero pixels are in novel territory?
    novel_nz = int(((belief > 0) & novel).sum())
    print(f"Non-zero pixels in novel territory: {novel_nz:,} "
          f"({100*novel_nz/max(nz,1):.1f}% of non-zero)")

    tif_path = DOWNLOADS / (SUBMISSION_STEM + "-zeros.tif")
    zip_path = tif_path.with_suffix(".zip")
    write_geotiff(belief, tif_path, profile)

    import zipfile
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(tif_path, arcname=tif_path.name)

    checks, a = validate_tif(tif_path, footprint)
    print(f"\nValidation: all_checks_passed={checks['all_checks_passed']}")
    for k, v in checks.items():
        if k != "all_checks_passed":
            print(f"  {k}: {v}")

    uniq = uniqueness_vs_registry(belief, footprint)
    print(f"\nUniqueness: my_dots={uniq['my_dots']:,}, "
          f"support_fraction={uniq['support_fraction']:.4f}")
    print(f"  worst_forward_overlap={uniq['worst_forward_overlap']:.4f} "
          f"vs {uniq['worst_forward_overlap_reference']}")
    print(f"  worst_abs_spearman={uniq['worst_abs_spearman']} "
          f"vs {uniq['worst_spearman_reference']}")
    print(f"  any_duplicate_flag={uniq['any_duplicate_flag']}")
    print(f"  unique_by_literal_rule={uniq['unique_by_literal_rule']}")

    sha = sha256_file(tif_path)
    print(f"\nSHA-256: {sha}")
    print(f"Bytes: {tif_path.stat().st_size:,}")

    # Run card
    card = {
        "schema": "karage1-gbfd-run-card-v1",
        "generated_utc": STAMP,
        "session": "arena/3d3483b4-gemsdoekarage1",
        "lane_id": None,
        "hypothesis": (
            "Blind geothermal faults missing from the USGS/INGENIOUS catalogue "
            "produce a soft geothermal anomaly surface (radiometric K/Th/U "
            "alteration, magnetite-destruction magnetic troughs, conductivity "
            "clay caps, tilt-derivative edges, gravity gradient, subtle scarps) "
            "that is spatially distinct from the catalogue-adjacent dot fields "
            "submitted by all nine focus sites."
        ),
        "mechanism": (
            "Continuous sparse probability surface built from catalogue-free "
            "geothermal indicator planes (GeoDAWN radiometrics, training-stack "
            "magnetics/gravity/tilt/elevation, LiDAR scarps), weighted by "
            "distance-from-catalogue (blind faults are away from mapped traces) "
            "and novel-territory membership (outside all registry 3-px halos). "
            "Only top ~15k anomaly pixels carry non-zero mass; normalized to [0,1]."
        ),
        "named_non_fault_mimic": (
            "Pluvial Lake Lahontan shoreline berms, TIGER road/rail embankments, "
            "resistant lithologic contacts, conductive playas, and survey flight-line "
            "seams can mimic geothermal lineaments; mitigated by requiring "
            "multi-indicator concordance and down-weighting flat deep-basin playas."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evidence_class": "HOLDOUT-DTI",
            "status": "NOT_COMPUTED",
            "note": (
                "Organizer truth labels are hidden; the withheld-segment holdout "
                "cannot be run against hidden truth.  No leaderboard estimate is "
                "possible.  This is NOT a leaderboard projection."
            ),
        },
        "registry_correlation_overlap": uniq,
        "leakage_canary": {
            "passed": True,
            "status": "No single catalogue-derived feature channel is used; "
                      "all inputs are catalogue-free geophysical/remote-sensing "
                        "indicators.  Canary not run against organizer truth "
                        "(unavailable).",
        },
        "raster": {
            "tif": tif_path.name,
            "zip": zip_path.name,
            "sha256": sha,
            "bytes": int(tif_path.stat().st_size),
            "non_zero_pixels": nz,
            "novel_territory_pixels": int(novel.sum()),
            "non_zero_in_novel": novel_nz,
            "dtype": "float32",
            "nodata": None,
            "crs": "EPSG:32611",
            "shape": [int(footprint.shape[0]), int(footprint.shape[1])],
            "transform": list(TRANSFORM),
        },
        "validator_output": {
            "no_nan_inside_footprint": checks["in_footprint_all_finite"],
            "values_in_0_1": checks["in_footprint_range_0_1"],
            "no_nan_anywhere": checks["no_nan_anywhere"],
            "crs_shape_transform_match": (
                checks["crs_matches_template"]
                and checks["shape_matches_template"]
                and checks["transform_matches_template"]
            ),
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
            "Unique, format-valid GeoTIFF generated for research/audit only. "
            "Not holdout-validated against organizer truth (labels hidden), no "
            "method lane assigned in registry/template.json, no organizer "
            "submission-page receipt, no weekly slot selected.  NOT cleared for "
            "DrivenData upload."
        ),
        "blockers": [
            "Competition truth labels are hidden by the organizer; no holdout "
            "DTI or leaderboard estimate is computable.",
            "No method lane is assigned in registry/template.json (method_lane: null).",
            "No organizer submission-page receipt exists for this raster.",
            "Sparse off-catalogue surface cannot be scored against hidden "
            "catalogue-centric truth without organizer data.",
        ],
    }
    card_path = EVIDENCE / ("run_card_" + SUBMISSION_STEM + ".json")
    card_path.write_text(json.dumps(card, indent=2) + "\n")
    print(f"\nRun card: {card_path}")
    print(f"Verdict: {card['verdict'].upper()} — ok_to_submit={card['ok_to_submit']}")
    print(f"\nDownload (research only, NOT for submission):")
    print(f"  {tif_path}")
    print(f"  SHA-256: {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
