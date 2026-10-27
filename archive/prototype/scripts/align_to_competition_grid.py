"""align_to_competition_grid.py — re-grid a prediction to the competition grid.

Re-projects / resamples a prediction GeoTIFF so its CRS, shape and geotransform
match sample_submission.tif EXACTLY (submission gate G6). Uses rasterio
reproject with nearest-neighbor (appropriate for binary/dotted predictions)
or bilinear (for continuous propensity surfaces).

This is the step that turns a format-valid synthetic TIF into a competition-
ready submission once DrivenData training data are placed in data/.

Usage:
    python scripts/align_to_competition_grid.py \
        --input submissions/gemsdoe-unique-hunq1-....-zeros.tif \
        --reference data/sample_submission.tif \
        --output submissions/gemsdoe-unique-hunq1-....-aligned.tif \
        --resampling nearest
"""

from __future__ import annotations

import argparse
import sys
from typing import Optional

import os
import numpy as np

try:
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.warp import reproject
except Exception as exc:  # pragma: no cover
    rasterio = None
    Resampling = None
    reproject = None


def align(input_path: str, reference_path: str, output_path: str,
          resampling: str = "nearest") -> dict:
    if rasterio is None:
        raise RuntimeError("rasterio is required")

    resample_map = {
        "nearest": Resampling.nearest,
        "bilinear": Resampling.bilinear,
        "cubic": Resampling.cubic,
        "average": Resampling.average,
    }
    if resampling not in resample_map:
        raise ValueError(f"unknown resampling {resampling}; options: {list(resample_map)}")

    with rasterio.open(reference_path) as ref:
        ref_profile = ref.profile.copy()
        ref_transform = ref.transform
        ref_crs = ref.crs
        ref_height = ref.height
        ref_width = ref.width
        ref_nodata = ref.nodata

    with rasterio.open(input_path) as src:
        src_data = src.read(1).astype(np.float32)
        src_transform = src.transform
        src_crs = src.crs

    # Allocate output array on the reference grid.
    out_data = np.empty((ref_height, ref_width), dtype=np.float32)
    out_nodata = ref_nodata if ref_nodata is not None else 0.0

    reproject(
        source=src_data,
        destination=out_data,
        src_transform=src_transform,
        src_crs=src_crs,
        dst_transform=ref_transform,
        dst_crs=ref_crs,
        resampling=resample_map[resampling],
        dst_nodata=out_nodata,
    )

    # Enforce submission value range [0,1] and finite everywhere (zeros encoding).
    out_data = np.where(np.isfinite(out_data), out_data, 0.0)
    out_data = np.clip(out_data, 0.0, 1.0).astype(np.float32)

    profile = ref_profile.copy()
    profile.update(driver="GTiff", dtype="float32", count=1,
                   height=ref_height, width=ref_width,
                   crs=ref_crs, transform=ref_transform,
                   compress="deflate", tiled=True, bigtiff="IF_NEEDED",
                   nodata=out_nodata)

    os_makedirs(output_path)
    with rasterio.open(output_path, "w", **profile) as dst:
        dst.write(out_data, 1)

    return {
        "output": output_path,
        "shape": [int(ref_height), int(ref_width)],
        "crs": str(ref_crs),
        "transform": [ref_transform.a, ref_transform.b, ref_transform.c,
                      ref_transform.d, ref_transform.e, ref_transform.f],
        "min": float(out_data.min()),
        "max": float(out_data.max()),
        "finite": bool(np.all(np.isfinite(out_data))),
        "in_range": bool(np.all((out_data >= 0.0) & (out_data <= 1.0))),
        "resampling": resampling,
    }


def os_makedirs(path: str) -> None:
    d = os.path.dirname(os.path.abspath(path))
    if d:
        os.makedirs(d, exist_ok=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Re-grid a prediction to exactly match sample_submission.tif.")
    parser.add_argument("--input", required=True, help="Input prediction GeoTIFF.")
    parser.add_argument("--reference", required=True,
                        help="sample_submission.tif (grid reference).")
    parser.add_argument("--output", required=True, help="Output aligned GeoTIFF.")
    parser.add_argument("--resampling", default="nearest",
                        help="nearest|bilinear|cubic|average (default nearest).")
    args = parser.parse_args(argv)

    if rasterio is None:
        print("ERROR: rasterio is required.", file=sys.stderr)
        return 2

    result = align(args.input, args.reference, args.output, args.resampling)
    import json
    print(json.dumps(result, indent=2))
    print("\nGrid match: CRS/shape/transform now identical to sample_submission.tif.")
    print("Next: run scripts/submission_writer.py --reference data/sample_submission.tif "
          "to produce the audit receipt, then upload via the DrivenData submission page.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
