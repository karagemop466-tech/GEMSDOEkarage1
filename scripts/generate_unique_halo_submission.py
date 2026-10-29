#!/usr/bin/env python3
"""
Generate a UNIQUE, format-valid GeoTIFF submission for the DOE GEMS Prize Challenge.

Method: Damage-zone halo probability field (contrarian to existing dot-field lanes).

Scientific hypothesis
---------------------
Existing submissions (GEMSDOE24/25/27/28/30/31/32/33/36) are all dot fields that
cluster within 3 px of the same pinned lattice — i.e. they predict on or within
~300 m of mapped USGS/INGENIOUS faults. Because known-fault pixels are masked in
scoring (DrivenData staff clarification thread 11516), dots on the catalogue add
false-positive mass without true-positive credit. The B2 collar result (thinning
dots near the catalogue from 44,090 to 37,654 raised the reported score from
0.2600 to 0.2778) shows the benefit of moving mass OFF the catalogue.

This generator takes the complementary, contrarian position: instead of placing
dots adjacent to mapped faults, it predicts a smooth probability field in the
damage-zone HALO around catalogue edges — the 100–300 m annulus where blind
splays, stepovers and relay ramps are geologically expected but unmapped by
construction. The field is:

  * ZERO on the catalogue (masked in scoring; no wasted mass)
  * ZERO outside the scored footprint
  * All-finite, float32, in [0, 1] everywhere — fixes the earlier
    "Predicted values must be in range [0, 1]" rejection
  * Structurally unique: a continuous halo field, not a discrete dot field;
    different spatial support from every existing submission

This is a RESEARCH ARTIFACT. It is NOT holdout-validated (organizer labels are
login-walled), NOT uniqueness-cleared against the complete organizer registry,
and NOT authorized for upload. Promotion to a weekly submission slot is a
separate selector decision.
"""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt, gaussian_filter

ROOT = Path(__file__).resolve().parents[1]
import sys as _sys
for _sub in ("vendor", "src"):
    if str(ROOT / _sub) not in _sys.path:
        _sys.path.insert(0, str(ROOT / _sub))

from gems57.grid import load_grid, DATA_DIR, HEIGHT, WIDTH, TRANSFORM, EPSG, PIXEL_M  # noqa: E402

# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
SUBMISSION_NAME = (
    f"karage1-halo-damagezone-d2p0-{STAMP}-zeros"
)
SUBMISSION_NOTE = (
    "Damage-zone halo probability field; research artifact; DO NOT SUBMIT"
)
assert len(SUBMISSION_NAME) <= 140, "name must be <= 140 chars"
assert len(SUBMISSION_NOTE) <= 140, "note must be <= 140 chars"

# Halo parameters (in pixels at 100 m grid)
HALO_CENTER_PX = 2.0      # 200 m from catalogue edge — damage-zone sweet spot
HALO_WIDTH_PX = 1.5       # width of the halo band
PEAK_VALUE = 0.6          # peak probability (keeps FP mass bounded)
BACKGROUND = 0.02         # low background across the rest of the footprint

DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_halo_field(footprint: np.ndarray, catalogue: np.ndarray) -> np.ndarray:
    """
    Build a damage-zone halo probability field.

    The field peaks at HALO_CENTER_PX pixels from the nearest catalogue edge
    and decays smoothly on both sides. Zero on catalogue and outside footprint.
    """
    # Distance to nearest catalogue pixel (0 on catalogue, grows outward)
    dist_to_cat = distance_transform_edt(~catalogue).astype(np.float64)

    # Only consider footprint pixels
    dist = np.where(footprint, dist_to_cat, np.inf)

    # Gaussian-like halo centred at HALO_CENTER_PX with width HALO_WIDTH_PX
    z = (dist - HALO_CENTER_PX) / HALO_WIDTH_PX
    halo = np.exp(-0.5 * z * z)

    # Apply peak value and background
    field = BACKGROUND + (PEAK_VALUE - BACKGROUND) * halo

    # Zero on catalogue and outside footprint
    field = np.where(footprint & ~catalogue, field, 0.0)

    # Ensure finite and in [0, 1]
    field = np.clip(field, 0.0, 1.0)
    field = np.where(np.isfinite(field), field, 0.0)

    return field.astype(np.float32)


def main() -> int:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    EVIDENCE.mkdir(parents=True, exist_ok=True)

    print("[1/6] Loading grid (footprint + catalogue)…")
    g = load_grid(DATA_DIR)
    footprint, catalogue = g.footprint, g.catalogue
    print(f"      footprint={int(footprint.sum()):,}  catalogue={int(catalogue.sum()):,}")

    print("[2/6] Building damage-zone halo probability field…")
    field = build_halo_field(footprint, catalogue)
    n_pos = int((field > 0).sum())
    print(f"      positive pixels: {n_pos:,} ({100 * n_pos / footprint.sum():.2f}% of footprint)")
    print(f"      max={field.max():.4f}  mean={field[field > 0].mean():.4f}")

    print("[3/6] Writing GeoTIFF on pinned grid…")
    tif_path = DOWNLOADS / f"{SUBMISSION_NAME}.tif"
    zip_path = DOWNLOADS / f"{SUBMISSION_NAME}.zip"
    receipt_path = DOWNLOADS / f"{SUBMISSION_NAME}.json"

    from gems57.grid import write_submission as gs_write_submission

    info = gs_write_submission(tif_path, field, mode="zeros")
    print(f"      wrote {tif_path} ({tif_path.stat().st_size:,} bytes)")

    # Re-read to verify what's on disk
    from gems57.grid import read_geotiff
    disk = read_geotiff(tif_path)
    print(f"      disk re-read: min={disk['min']} max={disk['max']} positive={disk['positive_pixels']:,}")

    print("[4/6] Writing single-TIF ZIP…")
    import zipfile
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
        zi = zipfile.ZipInfo(tif_path.name, date_time=(2026, 10, 8, 0, 0, 0))
        zi.compress_type = zipfile.ZIP_DEFLATED
        z.writestr(zi, tif_path.read_bytes())

    print("[5/6] Running local format validation…")
    from gems57.validate import validate
    from gems57.gates import format_report

    val = validate(tif_path, footprint=footprint, catalogue=catalogue)
    fmt = format_report(tif_path, DATA_DIR / "sample_submission.tif", footprint=footprint)

    print(f"      all_checks_passed: {val['all_checks_passed']}")
    print(f"      format ok: {fmt['ok']}")
    if not val["all_checks_passed"]:
        bad = [k for k, v in val["checks"].items() if not v]
        print(f"      FAILED CHECKS: {bad}")
    if not fmt["ok"]:
        print(f"      FORMAT PROBLEMS: {fmt['problems']}")

    print("[6/6] Writing run card…")
    card = {
        "schema": "karage1-run-card-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "session": "arena/968c17f0-gemsdoekarage1",
        "hypothesis": (
            "Blind splays/stepovers concentrate in the damage-zone halo "
            "100-300 m from mapped catalogue edges; a smooth halo probability "
            "field there is structurally unique versus all dot-field submissions."
        ),
        "mechanism": (
            "Distance-to-catalogue Gaussian halo peaking at 200 m, zero on "
            "catalogue and outside footprint, all-finite [0,1] float32."
        ),
        "named_non_fault_mimic": (
            "Pluvial shoreline berms, road/rail embankments, and conductive "
            "playas can produce linear anomalies near catalogue traces."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "value": None,
            "evaluator_version": None,
            "withheld_positives": None,
            "ci95": None,
            "status": "not run — organizer labels are login-walled; no truth available",
        },
        "correlation_overlap_vs_registry": {
            "preplacement_surface_spearman": None,
            "final_dot_overlap": None,
            "note": (
                "Registry rasters not fetched locally; uniqueness vs the nine "
                "focus-site dot fields is structural (continuous halo field vs "
                "discrete dots) but not yet measured against the lattice."
            ),
        },
        "raster_sha256": sha256_file(tif_path),
        "raster": {
            "tif": tif_path.name,
            "zip": zip_path.name,
            "receipt": receipt_path.name,
            "sha256": sha256_file(tif_path),
            "bytes": int(tif_path.stat().st_size),
            "positive_pixels": n_pos,
            "dtype": "float32",
            "nodata": None,
            "crs": "EPSG:32611",
            "shape": [HEIGHT, WIDTH],
            "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
        },
        "validator_output": {
            "all_checks_passed": bool(val["all_checks_passed"]),
            "format_ok": bool(fmt["ok"]),
            "no_nan_inside_footprint": bool(
                val["checks"].get("in_footprint_all_finite", False)
            ),
            "values_in_0_1": bool(val["checks"].get("range_0_1_guaranteed", False)),
            "crs_shape_transform_match": bool(
                val["checks"].get("crs_epsg_32611", False)
                and val["checks"].get("transform_matches_sample_submission", False)
                and val["checks"].get(f"dimensions_{HEIGHT}x{WIDTH}", False)
            ),
            "outside_footprint_zero": bool(
                val["checks"].get("outside_footprint_zero", False)
            ),
            "format_problems": fmt.get("problems", []),
        },
        "submission_name": f"{SUBMISSION_NAME}.tif",
        "submission_note": SUBMISSION_NOTE,
        "submission_note_chars": len(SUBMISSION_NOTE),
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "geological_experiments_run_this_session": 1,
        "verdict": (
            "negative — research artifact only; format-valid and structurally "
            "unique by design, but not holdout-validated and not registry-cleared"
        ),
        "blockers": [
            "Organizer truth labels are login-walled; HOLDOUT-DTI cannot be computed",
            "Complete organizer registry not accessible; literal lattice uniqueness not measured",
            "No assigned method lane (registry/template.json method_lane is null)",
            "No weekly submission slot selected or spent",
        ],
    }

    card_path = EVIDENCE / f"run_card_{SUBMISSION_NAME}.json"
    card_path.write_text(json.dumps(card, indent=2) + "\n")
    print(f"      run card -> {card_path}")

    # Also write a submission receipt adjacent to the TIF
    receipt = {
        "file": str(tif_path),
        "sha256": sha256_file(tif_path),
        "bytes": tif_path.stat().st_size,
        "name": f"{SUBMISSION_NAME}.tif",
        "note": SUBMISSION_NOTE,
        "format_valid": bool(val["all_checks_passed"] and fmt["ok"]),
        "ok_to_submit": False,
        "verdict": card["verdict"],
    }
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"      receipt -> {receipt_path}")

    print(f"\n=== SUMMARY ===")
    print(f"TIF: {tif_path}")
    print(f"ZIP: {zip_path}")
    print(f"SHA-256: {sha256_file(tif_path)}")
    print(f"Format valid: {val['all_checks_passed'] and fmt['ok']}")
    print(f"OK to submit: False (research artifact — not cleared)")
    print(f"Verdict: {card['verdict']}")

    return 0 if (val["all_checks_passed"] and fmt["ok"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
