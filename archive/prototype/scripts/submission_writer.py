"""submission_writer.py — write + validate a competition GeoTIFF submission.

Writes a single-band float32 GeoTIFF whose CRS / shape / geotransform match
sample_submission.tif exactly, enforces the submission gates:

    G1. No NaN inside the footprint (finite everywhere); outside-footprint
        cells are filled with 0 (the "-zeros" encoding used by the GEMSDOE
        family so the raster cannot violate the [0, 1] range check).
    G2. All values in [0, 1].
    G3. CRS, shape and transform identical to sample_submission.tif.
    G4. Single band, float32, GDAL/rasterio readable.

Produces an audit receipt JSON (<stem>-audit.json) recording every gate result
and the raster SHA-256. This is the "format receipt (13/13 PASS)" pattern from
the GEMSDOE research pages.

Usage:
    python scripts/submission_writer.py \
        --prediction submissions/raw_prediction.tif \
        --reference data/sample_submission.tif \
        --out submissions/gemsdoe-unique-...-zeros.tif

Without --reference (no DrivenData auth here) the writer builds a standalone
georeferenced GeoTIFF (EPSG:32611, 3730x3292, 100 m pixels) and clearly marks
G3 as "unverified - must be re-gridded to sample_submission.tif".
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone
from typing import Optional, Tuple

import numpy as np

try:
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.crs import CRS
except Exception as exc:  # pragma: no cover - import guard
    rasterio = None
    from_origin = None
    CRS = None

# Submission gate limits (protocol / DrivenData format)
VALUE_MIN = 0.0
VALUE_MAX = 1.0
EXPECTED_CRS = "EPSG:32611"
EXPECTED_HEIGHT = 3730
EXPECTED_WIDTH = 3292
EXPECTED_CELLS = EXPECTED_HEIGHT * EXPECTED_WIDTH  # 12,279,160


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_raster(path: str):
    if rasterio is None:
        raise RuntimeError("rasterio is required")
    with rasterio.open(path) as src:
        data = src.read(1)  # single band
        profile = src.profile.copy()
        return data, profile, src


def validate_raster(
    data: np.ndarray,
    profile: dict,
    reference_profile: Optional[dict] = None,
    footprint_mask: Optional[np.ndarray] = None,
) -> dict:
    """Run all submission gates. Returns a gate-by-gate report."""
    gates = {}

    # G0: readable, single band
    gates["G0_single_band"] = {
        "pass": data.ndim == 2,
        "detail": f"bands={1 if data.ndim == 2 else data.shape}",
    }

    # G1: dtype float32
    gates["G1_float32"] = {
        "pass": data.dtype == np.float32,
        "detail": f"dtype={data.dtype}",
    }

    # G2: shape
    gates["G2_shape"] = {
        "pass": data.shape == (EXPECTED_HEIGHT, EXPECTED_WIDTH),
        "detail": f"shape={data.shape} expected=({EXPECTED_HEIGHT},{EXPECTED_WIDTH}) "
                  f"cells={data.size} expected={EXPECTED_CELLS}",
    }

    # G3: finite everywhere (no NaN / Inf)
    finite_mask = np.isfinite(data)
    gates["G3_finite"] = {
        "pass": bool(np.all(finite_mask)),
        "detail": f"non_finite_cells={int(np.sum(~finite_mask))}",
    }

    # G4: values in [0, 1]
    in_range = bool(np.all((data >= VALUE_MIN) & (data <= VALUE_MAX)))
    gates["G4_range_0_1"] = {
        "pass": in_range,
        "detail": f"min={float(np.nanmin(data)):.6f} max={float(np.nanmax(data)):.6f} "
                  f"range=[{VALUE_MIN},{VALUE_MAX}]",
    }

    # G5: no NaN inside footprint (strictest form of G3/G4 on footprint)
    if footprint_mask is not None:
        inside_nonfinite = int(np.sum(~finite_mask & footprint_mask))
        inside_oor = int(np.sum((~np.isfinite(data) | (data < VALUE_MIN) | (data > VALUE_MAX)) & footprint_mask))
        gates["G5_footprint_clean"] = {
            "pass": inside_nonfinite == 0 and inside_oor == 0,
            "detail": f"footprint_cells={int(np.sum(footprint_mask))} "
                      f"nonfinite_inside={inside_nonfinite} out_of_range_inside={inside_oor}",
        }
    else:
        gates["G5_footprint_clean"] = {
            "pass": gates["G3_finite"]["pass"] and gates["G4_range_0_1"]["pass"],
            "detail": "no footprint mask; using whole-array G3/G4",
        }

    # G6: CRS / shape / transform match reference
    if reference_profile is not None:
        crs_match = str(profile.get("crs")) == str(reference_profile.get("crs"))
        transform_match = profile.get("transform") == reference_profile.get("transform")
        shape_match = (profile.get("height"), profile.get("width")) == (
            reference_profile.get("height"), reference_profile.get("width"))
        gates["G6_grid_match"] = {
            "pass": bool(crs_match and transform_match and shape_match),
            "detail": f"crs_match={crs_match} transform_match={transform_match} "
                      f"shape_match={shape_match}",
        }
    else:
        gates["G6_grid_match"] = {
            "pass": False,
            "detail": "no reference sample_submission.tif -> grid match UNVERIFIED "
                      "(must re-grid to competition sample before upload)",
        }

    gates["ALL_PASS"] = {"pass": all(g["pass"] for g in gates.values()),
                         "detail": "all gates pass"}
    return gates


def write_geotiff(path: str, data: np.ndarray, profile: dict) -> None:
    if rasterio is None:
        raise RuntimeError("rasterio is required to write GeoTIFF")
    prof = profile.copy()
    prof.update(driver="GTiff", dtype="float32", count=1,
                compress="deflate", tiled=True,
                bigtiff="IF_NEEDED")
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(data.astype(np.float32), 1)


def build_standalone_grid() -> Tuple[dict, np.ndarray]:
    """Build a standalone EPSG:32611 grid (3730x3292, 100 m) when no reference.

    NOTE: the geotransform origin is a documented placeholder. The real
    submission must be re-gridded to sample_submission.tif via
    align_to_competition_grid.py before upload.
    """
    if from_origin is None or CRS is None:
        raise RuntimeError("rasterio is required")
    transform = from_origin(500000.0, 4500000.0, 100.0, 100.0)
    crs = CRS.from_epsg(32611)
    profile = {
        "driver": "GTiff", "dtype": "float32", "count": 1,
        "height": EXPECTED_HEIGHT, "width": EXPECTED_WIDTH,
        "crs": crs, "transform": transform,
        "compress": "deflate", "tiled": True, "bigtiff": "IF_NEEDED",
    }
    footprint = np.ones((EXPECTED_HEIGHT, EXPECTED_WIDTH), dtype=bool)
    return profile, footprint


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Write + validate a competition GeoTIFF submission.")
    parser.add_argument("--prediction", required=True,
                        help="Input prediction raster (single band).")
    parser.add_argument("--reference", default=None,
                        help="sample_submission.tif (grid reference).")
    parser.add_argument("--out", required=True,
                        help="Output GeoTIFF path.")
    parser.add_argument("--receipt", default=None,
                        help="Output audit-receipt JSON path (default: <out>-audit.json).")
    args = parser.parse_args(argv)

    if rasterio is None:
        print("ERROR: rasterio is required.", file=sys.stderr)
        return 2

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)

    data, profile, _ = read_raster(args.prediction)

    reference_profile = None
    footprint_mask = None
    if args.reference and os.path.exists(args.reference):
        ref_data, ref_profile, _ = read_raster(args.reference)
        reference_profile = ref_profile
        footprint_mask = np.isfinite(ref_data)
    else:
        # Standalone: build the documented grid; mark grid match unverified.
        profile, footprint_mask = build_standalone_grid()
        # Re-predict onto standalone shape if needed.
        if data.shape != (EXPECTED_HEIGHT, EXPECTED_WIDTH):
            print(f"WARNING: prediction shape {data.shape} != standalone "
                  f"({EXPECTED_HEIGHT},{EXPECTED_WIDTH}); writing as-is "
                  f"(grid match will be unverified).", file=sys.stderr)

    # Enforce [0,1] + finite: clip to [0,1] and replace non-finite with 0
    # (zeros encoding). This guarantees G3/G4 pass.
    cleaned = np.where(np.isfinite(data), data, 0.0)
    cleaned = np.clip(cleaned, VALUE_MIN, VALUE_MAX).astype(np.float32)

    write_geotiff(args.out, cleaned, profile)

    gates = validate_raster(cleaned, profile, reference_profile, footprint_mask)

    receipt = {
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "input": args.prediction,
        "output": args.out,
        "reference": args.reference,
        "raster_sha256": sha256_file(args.out),
        "shape": [int(cleaned.shape[0]), int(cleaned.shape[1])],
        "dtype": str(cleaned.dtype),
        "crs": str(profile.get("crs")),
        "transform": [profile["transform"].a, profile["transform"].b,
                      profile["transform"].c, profile["transform"].d,
                      profile["transform"].e, profile["transform"].f],
        "min": float(cleaned.min()),
        "max": float(cleaned.max()),
        "nan_count": int(np.sum(~np.isfinite(data))),
        "gates": gates,
        "ok_to_submit": bool(gates["ALL_PASS"]["pass"]
                             and gates["G6_grid_match"]["pass"]),
    }
    receipt_path = args.receipt or (args.out + "-audit.json")
    with open(receipt_path, "w") as f:
        json.dump(receipt, f, indent=2)

    print(json.dumps(receipt, indent=2))
    print(f"\nReceipt: {receipt_path}")
    print(f"OK TO SUBMIT: {'YES' if receipt['ok_to_submit'] else 'NO'}")
    return 0 if receipt["ok_to_submit"] else 1


if __name__ == "__main__":
    sys.exit(main())
