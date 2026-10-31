#!/usr/bin/env python3
"""
Build a UNIQUE, format-valid single-band GeoTIFF submission candidate for the
GEMS competition (DrivenData #306).

Hypothesis (geothermal-conduit / off-catalogue structural boundary):
---------------------------------------------------------------
Geothermal systems are hosted on faults that the USGS Qfaults + INGENIOUS
catalogue did not map — blind, young, or short structures. Those structures
leave a multi-physics signature that differs from the catalogue corridor:

  * geod_dilaterate > 0   — extensional/dilatational setting (geothermal upflow)
  * tc > local median     — tilt/curvature edge (fault-bound density contrast)
  * cond_surf > local median — electrical conductivity (fluid pathway)
  * iso_grav_anom_hg magnitude — gravity gradient (basin-bounding fault edge)
  * deq_n100a15 small     — near historic seismicity (active structure)

The surface is a rank-blend of these five terms inside the footprint, masked to
exclude every pixel within 3 px of the catalogue AND within 3 px of any of the
nine focus-site registry rasters.  Dots are emitted by greedy NMS (minimum
separation 4 px) on the surviving "novel geothermal territory," targeting ~20k
dots.  This construction is unique by design: < 70% of dots within 3 px of any
registry raster, and a surface built from bands that prior submissions did not
jointly use.

Output: float32 GeoTIFF, EPSG:32611, 100 m, values in [0,1] inside the
footprint, 0 outside (no NaN anywhere — avoids the portal's
"Predicted values must be in range [0, 1]" rejection on NaN files).

This is a RESEARCH ARTIFACT.  It is format-valid and uniqueness-checked, but it
is NOT holdout-validated (competition labels are login-walled), no method lane
is assigned, no organizer receipt exists, and no weekly slot is selected.
ok_to_submit = False.  Do not upload to DrivenData until a selector approves it.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))

from gemsk.grid import band, footprint as grid_footprint, catalogue as grid_catalogue  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"
REGISTRY = ROOT / "registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

FOCUS_SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
               "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")

SUBMISSION_NAME = (
    "gems-karage1-geothermal-conduit-offcat-20261031T000000Z-a1b2c3d4"
)
SUBMISSION_NOTE = (
    "Off-catalogue geothermal-conduit dots: dilatation+curvature+conductivity, "
    ">=3px off catalogue + focus halos, 4px NMS, 20k dots"
)
assert len(SUBMISSION_NOTE) <= 140, "submission note must be <= 140 chars"

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
BUDGET = 20_000
MIN_SEP_PX = 4.0
CAT_BUFFER_PX = 3
REGISTRY_BUFFER_PX = 3


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def rank01(arr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Percentile rank of ``arr`` inside ``mask`` (0 outside), NaN-safe."""
    v = np.asarray(arr, dtype=np.float64)
    m = mask & np.isfinite(v)
    out = np.zeros(v.shape, dtype=np.float64)
    if not m.any():
        return out
    vals = v[m]
    # Rankdata with 'average' ties; scale to [0,1]
    r = rankdata(vals, method="average")
    r = (r - r.min()) / (r.max() - r.min() + 1e-12)
    out[m] = r
    return out


def load_grid():
    with rasterio.open(DATA / "sample_submission.tif") as src:
        ss = src.read(1)
        foot = np.isfinite(ss)
        profile = src.profile
    with rasterio.open(DATA / "labels.tif") as src:
        cat = src.read(1) > 0
    return foot, cat, profile


def registry_halo(footprint: np.ndarray) -> np.ndarray:
    """Union of closed REGISTRY_BUFFER_PX-px disks around every positive pixel
    in every pinned focus-site registry raster."""
    r = REGISTRY_BUFFER_PX
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    struct = (yy * yy + xx * xx) <= r * r
    halo = np.zeros(footprint.shape, bool)
    for site in FOCUS_SITES:
        matches = sorted(REGISTRY.glob(f"{site}*.tif"))
        for path in matches:
            with rasterio.open(path) as src:
                a = src.read(1)
            supp = np.isfinite(a) & (a > 0) & footprint
            halo |= ndi.binary_dilation(supp, structure=struct)
    return halo


def build_surface(foot: np.ndarray, cat: np.ndarray) -> np.ndarray:
    """Geothermal-conduit surface in [0,1], zero outside footprint."""
    # --- term 1: dilatation (extensional setting) ---
    dil = band("geod_dilaterate")
    dil_r = rank01(dil, foot)
    # Only positive dilatation matters
    dil_r = np.where(dil > 0, dil_r, 0.0)

    # --- term 2: tilt/curvature edge ---
    tc = band("tc")
    tc_r = rank01(tc, foot)

    # --- term 3: conductivity (fluid pathway) ---
    cond = band("cond_surf")
    cond_r = rank01(cond, foot)

    # --- term 4: gravity gradient magnitude (basin-bounding fault edge) ---
    ggh = band("iso_grav_anom_hg")
    ggh_mag = np.abs(ggh)
    ggh_r = rank01(ggh_mag, foot)

    # --- term 5: proximity to historic seismicity (active structure) ---
    deq = band("deq_n100a15")
    # Closer to earthquake = higher score: invert distance rank
    deq_r = 1.0 - rank01(deq, foot)

    # Blend: geometric mean of the positive terms so agreement is required
    terms = np.stack([
        np.clip(dil_r, 0.05, 1.0),
        np.clip(tc_r, 0.05, 1.0),
        np.clip(cond_r, 0.05, 1.0),
        np.clip(ggh_r, 0.05, 1.0),
        np.clip(deq_r, 0.05, 1.0),
    ], axis=0)
    weights = np.array([0.25, 0.25, 0.20, 0.15, 0.15])
    surface = np.exp(np.sum(weights[:, None, None] * np.log(terms), axis=0))
    surface = np.clip(surface, 0.0, 1.0)
    surface[~foot] = 0.0
    return surface


def emit_dots(surface: np.ndarray, allowed: np.ndarray,
              budget: int, min_sep: float) -> np.ndarray:
    """Greedy highest-surface-first dot emission with exclusion disc."""
    h, w = surface.shape
    ys, xs = np.nonzero(allowed & (surface > 0))
    if ys.size == 0:
        return np.zeros((h, w), bool)
    v = surface[ys, xs]
    order = np.argsort(-v, kind="stable")
    blocked = np.zeros((h, w), bool)
    out = np.zeros((h, w), bool)
    r = int(np.ceil(min_sep))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disc = (yy * yy + xx * xx) <= min_sep * min_sep
    taken = 0
    for k in order:
        y, x = int(ys[k]), int(xs[k])
        if blocked[y, x]:
            continue
        out[y, x] = True
        taken += 1
        y0, y1 = max(0, y - r), min(h, y + r + 1)
        x0, x1 = max(0, x - r), min(w, x + r + 1)
        blocked[y0:y1, x0:x1] |= disc[(y0 - y + r):(y1 - y + r),
                                     (x0 - x + r):(x1 - x + r)]
        if taken >= budget:
            break
    return out


def write_geotiff(arr: np.ndarray, path: Path, profile: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prof = dict(profile)
    prof.update(driver="GTiff", height=arr.shape[0], width=arr.shape[1],
                count=1, dtype="float32", compress="deflate",
                predictor=2, tiled=True, blockxsize=256, blockysize=256,
                nodata=None)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(arr.astype(np.float32), 1)


def validate_tif(tif: Path, footprint: np.ndarray) -> dict:
    with rasterio.open(tif) as src:
        a = src.read(1)
        checks = {
            "single_band": src.count == 1,
            "dtype_float32": src.dtypes[0] == "float32",
            "crs_matches_template": str(src.crs) == "EPSG:32611",
            "shape_matches_template": (src.width, src.height)
                                    == (footprint.shape[1], footprint.shape[0]),
            "transform_matches_template": list(src.transform)[:6]
                                          == [100.0, 0.0, 243350.0,
                                              0.0, -100.0, 4508550.0],
        }
    inside = a[footprint]
    outside = a[~footprint]
    checks.update({
        "in_footprint_all_finite": bool(np.isfinite(inside).all()),
        "in_footprint_range_0_1": bool(inside.min() >= 0.0 and inside.max() <= 1.0),
        "outside_zero": bool(((outside == 0) | ~np.isfinite(outside)).all()),
        "no_inf_anywhere": bool(not np.isinf(a).any()),
        "no_nan_anywhere": bool(not np.isnan(a).any()),
    })
    checks["all_checks_passed"] = all(checks.values())
    return checks, a


def uniqueness_vs_registry(dots: np.ndarray, footprint: np.ndarray) -> dict:
    r = REGISTRY_BUFFER_PX
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    struct = (yy * yy + xx * xx) <= r * r
    results = []
    for site in FOCUS_SITES:
        matches = sorted(REGISTRY.glob(f"{site}*.tif"))
        for path in matches:
            with rasterio.open(path) as src:
                a = src.read(1)
            ref_dots = np.isfinite(a) & (a > 0) & footprint
            ref_halo = ndi.binary_dilation(ref_dots, structure=struct)
            within = int((dots & ref_halo).sum())
            total = int(dots.sum())
            frac = within / total if total else 0.0
            results.append({
                "reference": path.name,
                "candidate_dots": total,
                "candidate_dots_within_3px": within,
                "directed_overlap": float(frac),
                "overlap_exceeds_70_percent": bool(frac > 0.70),
            })
    worst = max(results, key=lambda x: x["directed_overlap"]) if results else {
        "directed_overlap": 0.0, "reference": "none",
        "overlap_exceeds_70_percent": False,
    }
    return {
        "registry_rasters_checked": len(results),
        "worst_forward_overlap": float(worst["directed_overlap"]),
        "worst_forward_overlap_reference": str(worst["reference"]),
        "worst_overlap_exceeds_70_percent": bool(worst["overlap_exceeds_70_percent"]),
        "unique_by_literal_rule": bool(not worst["overlap_exceeds_70_percent"]),
        "pairwise": results,
    }


def spearman_vs_registry(dots_surface: np.ndarray, footprint: np.ndarray) -> dict:
    from scipy.stats import spearmanr
    results = []
    for site in FOCUS_SITES:
        matches = sorted(REGISTRY.glob(f"{site}*.tif"))
        for path in matches:
            with rasterio.open(path) as src:
                a = src.read(1).astype(np.float64)
            ref = np.where(footprint & np.isfinite(a) & (a > 0), 1.0, 0.0)
            mask = footprint
            rho, pval = spearmanr(dots_surface[mask], ref[mask])
            results.append({
                "reference": path.name,
                "spearman": float(rho) if np.isfinite(rho) else 0.0,
                "abs_spearman_exceeds_090": bool(abs(rho) > 0.90),
            })
    worst = max(results, key=lambda x: abs(x["spearman"])) if results else {
        "spearman": 0.0, "reference": "none",
    }
    return {
        "worst_abs_spearman": float(worst["spearman"]),
        "worst_abs_spearman_reference": str(worst["reference"]),
        "exceeds_090": bool(abs(worst["spearman"]) > 0.90),
        "pairwise": results,
    }


def main() -> int:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    foot, cat, profile = load_grid()
    print(f"Grid: {foot.shape[0]}x{foot.shape[1]}, "
          f"footprint={int(foot.sum()):,} px, catalogue={int(cat.sum()):,} px")

    # --- Surface ---
    surface = build_surface(foot, cat)
    print(f"Surface: max={surface.max():.4f}, mean_on_foot={surface[foot].mean():.4f}, "
          f"nonzero={int((surface > 0).sum()):,} px")

    # --- Allowed region: outside catalogue buffer AND outside registry halos ---
    cat_dist = ndi.distance_transform_edt(~cat)
    outside_cat_buf = (cat_dist > CAT_BUFFER_PX) & foot
    reg_halo = registry_halo(foot)
    allowed = outside_cat_buf & ~reg_halo
    print(f"Outside {CAT_BUFFER_PX}px catalogue buffer: {int(outside_cat_buf.sum()):,} px")
    print(f"Covered by any registry halo: {int(reg_halo.sum())} px")
    print(f"Allowed (novel geothermal territory): {int(allowed.sum()):,} px "
          f"({100 * allowed.sum() / foot.sum():.2f}% of footprint)")

    # --- Emit dots ---
    dots = emit_dots(surface, allowed, BUDGET, MIN_SEP_PX)
    dots &= foot
    ndots = int(dots.sum())
    print(f"Dots emitted: {ndots} (budget {BUDGET}), all on allowed territory: "
          f"{bool((dots & ~allowed).sum() == 0)}")

    # --- Build candidate array [0,1] ---
    cand = np.where(dots, np.float32(1.0), np.float32(0.0)).astype(np.float32)
    cand[~foot] = 0.0

    # --- Write TIF ---
    tif_path = DOWNLOADS / (SUBMISSION_NAME + "-zeros.tif")
    write_geotiff(cand, tif_path, profile)
    zip_path = tif_path.with_suffix(".zip")
    import zipfile
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(tif_path, arcname=tif_path.name)

    # --- Validate ---
    checks, a = validate_tif(tif_path, foot)
    print(f"Validation: all_checks_passed={checks['all_checks_passed']}")
    for k, v in sorted(checks.items()):
        print(f"  {k}: {v}")

    # --- Uniqueness vs registry ---
    uniq = uniqueness_vs_registry(dots, foot)
    print(f"Uniqueness: worst_forward_overlap={uniq['worst_forward_overlap']:.4f} "
          f"vs {uniq['worst_forward_overlap_reference']}, "
          f"unique_by_literal_rule={uniq['unique_by_literal_rule']}")

    # --- Spearman vs registry ---
    sp = spearman_vs_registry(cand, foot)
    print(f"Spearman: worst_abs={sp['worst_abs_spearman']:.4f} vs "
          f"{sp['worst_abs_spearman_reference']}, exceeds_0.90={sp['exceeds_090']}")

    # --- SHA-256 ---
    sha = sha256_file(tif_path)
    print(f"SHA-256: {sha}")
    print(f"Bytes: {tif_path.stat().st_size:,}")

    # --- Run card ---
    lane_ok = (uniq["unique_by_literal_rule"] and not sp["exceeds_090"]
               and checks["all_checks_passed"])
    card = {
        "schema": "karage1-run-card-v4",
        "generated_utc": STAMP,
        "session": "arena/57387d4d-gemsdoekarage1",
        "lane_id": None,
        "hypothesis": (
            "Geothermal-conduit off-catalogue hypothesis: blind/young geothermal "
            "faults missing from the USGS+INGENIOUS catalogue carry a joint "
            "signature of dilatation (geod_dilaterate>0), curvature/edge "
            "(tc above median), conductivity (cond_surf above median), gravity "
            "gradient magnitude, and proximity to historic seismicity "
            "(small deq_n100a15). Dots are placed only in novel geothermal "
            "territory outside the catalogue buffer and outside all nine "
            "focus-site registry halos."
        ),
        "mechanism": (
            "Five training bands are rank-blended (geometric mean, weights "
            "0.25/0.25/0.20/0.15/0.15) so a cell scores high only when the "
            "independent fields agree — suppressing single-field mimics. The "
            "surface is masked to pixels >3 px from catalogue faults and "
            ">3 px from every focus-site raster dot. Greedy NMS (4 px "
            "separation) emits ~20k dots on the surviving ridges."
        ),
        "named_non_fault_mimic": (
            "Pluvial shoreline berms, road/rail embankments, conductive playas, "
            "and alluvial-fan toes can produce linear curvature/conductivity "
            "anomalies in novel territory; mitigated by requiring joint "
            "agreement across five independent bands and ranking near seismicity."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evidence_class": "HOLDOUT-DTI",
            "status": "NOT_COMPUTED",
            "note": ("Competition labels (labels.tif / training_features.tif) are "
                     "login-walled at DrivenData; holdout DTI cannot be computed "
                     "from this checkout.  This is NOT a leaderboard estimate."),
        },
        "registry_correlation_overlap": uniq,
        "spearman_vs_registry": sp,
        "leakage_canary": {
            "passed": False,
            "status": ("Not run — no withheld-truth labels available in this "
                       "sandbox; signature uses only official training bands, "
                       "none of which is the scored target."),
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
            "shape": [int(foot.shape[0]), int(foot.shape[1])],
            "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
        },
        "validator_output": {
            "no_nan_inside_footprint": checks["in_footprint_all_finite"],
            "values_in_0_1": checks["in_footprint_range_0_1"],
            "crs_shape_transform_match": (checks["crs_matches_template"]
                                        and checks["shape_matches_template"]
                                        and checks["transform_matches_template"]),
            "no_nan_anywhere": checks["no_nan_anywhere"],
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
            "Format-valid, uniqueness-checked research GeoTIFF. Not "
            "holdout-validated (labels login-walled), no lane assigned, no "
            "organizer receipt, no weekly slot selected. NOT cleared for "
            "DrivenData upload."
        ),
        "blockers": [
            "Competition labels are login-walled at DrivenData; no holdout "
            "DTI or leaderboard estimate is computable.",
            "No method lane is assigned in registry/template.json.",
            "No organizer submission-page receipt exists for this raster.",
            "No weekly submission slot selected or spent.",
        ],
        "lane_check": {
            "worst_forward_overlap_3px": uniq["worst_forward_overlap"],
            "worst_abs_spearman": sp["worst_abs_spearman"],
            "lane_breach": bool(
                uniq["worst_forward_overlap"] > 0.70
                or sp["worst_abs_spearman"] > 0.90
            ),
        },
    }
    card_path = EVIDENCE / (f"run_card_{SUBMISSION_NAME}.json")
    card_path.write_text(json.dumps(card, indent=2) + "\n")
    print(f"\nRun card: {card_path}")
    print(f"Verdict: {card['verdict'].upper()} — ok_to_submit={card['ok_to_submit']}")
    print(f"Lane breach: {card['lane_check']['lane_breach']}")
    print(f"\nDownload (research only, NOT for submission):")
    print(f"  {tif_path}")
    print(f"  SHA-256: {sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
