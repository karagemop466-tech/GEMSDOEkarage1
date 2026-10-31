#!/usr/bin/env python3
"""Check GeoTIFFs against the OFFICIAL submission format (DrivenData page 967).

Official text (https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/):
  * EPSG:32611, 100 m grid, same shape and bounds as the training data
    (reference: data/sample_submission.tif, 3730 x 3292, EPSG:32611);
  * single band, float32;
  * values between 0 and 1;
  * data outside the bounds is null or NaN.

Literal checks reported per file: CRS, shape, transform, dtype, band count,
NaN count, finite min/max, out-of-range count, and whether outside-footprint
cells are NaN (official) or 0 (repo "zeros" variants, which the official text
does not list). The footprint is taken from the reference sample's finite cells.
This is a format check only. It is NOT submission approval and NOT a score.

Usage: python scripts/check_official_format.py FILE [FILE ...] [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
REF = ROOT / "data" / "sample_submission.tif"


def check(path: Path, ref_shape, ref_transform, ref_crs, ref_footprint) -> dict:
    with rasterio.open(path) as src:
        a = src.read(1).astype(np.float64)
        rec = {
            "file": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
            "crs_ok": str(src.crs) == str(ref_crs),
            "shape_ok": src.shape == ref_shape,
            "transform_ok": src.transform == ref_transform,
            "dtype_ok": src.dtypes[0] == "float32",
            "single_band": src.count == 1,
        }
    nan_mask = np.isnan(a)
    fin = a[~nan_mask]
    rec["nan_count"] = int(nan_mask.sum())
    rec["min"] = float(fin.min()) if fin.size else None
    rec["max"] = float(fin.max()) if fin.size else None
    rec["out_of_range_count"] = int(((fin < 0) | (fin > 1)).sum())
    if rec["shape_ok"]:
        outside = ~ref_footprint
        rec["outside_footprint_nan"] = int(nan_mask[outside].sum())
        rec["outside_footprint_zero"] = int((a[outside] == 0).sum())
        rec["outside_footprint_other"] = int((~nan_mask[outside] & (a[outside] != 0)).sum())
        rec["outside_encoding"] = (
            "nan" if rec["outside_footprint_nan"] == outside.sum() else
            "zero" if rec["outside_footprint_zero"] == outside.sum() else "mixed_or_nonzero"
        )
        rec["positive_cells"] = int((fin > 0).sum())
    rec["official_pass"] = bool(
        rec["crs_ok"] and rec["shape_ok"] and rec["transform_ok"] and rec["dtype_ok"]
        and rec["single_band"] and rec["out_of_range_count"] == 0
        and rec.get("outside_encoding") == "nan"
    )
    rec["note"] = ("passes literal official text" if rec["official_pass"] else
                   "fails literal official text (see fields); zero-encoded outside is a literal deviation")
    return rec


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", default="")
    args = ap.parse_args()
    with rasterio.open(REF) as ref:
        ref_shape, ref_transform, ref_crs = ref.shape, ref.transform, ref.crs
        ref_footprint = np.isfinite(ref.read(1))
    results = [check(Path(f).resolve(), ref_shape, ref_transform, ref_crs, ref_footprint) for f in args.files]
    text = json.dumps(results, indent=2)
    if args.json:
        Path(args.json).write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
