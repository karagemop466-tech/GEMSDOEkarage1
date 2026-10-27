"""Submission writer + validator for the DrivenData GEMS format.

Format (from the competition submission page, transcribed by the owner into the standing brief):
single-band GeoTIFF (.tif) or a .zip containing one, matching the submission format's CRS, shape and
geotransform; predicted values must be in [0, 1]. The organizer's page rejected a file with the
message "Predicted values must be in range [0, 1]" once; the cause in the sibling repositories was
non-finite / sentinel values. We therefore ship the **zeros** variant as the file to submit:
float32, every one of the 12,278,160 pixels finite, 0 outside the footprint, dots = 1.0, no nodata
tag. A **nan** variant (NaN outside the footprint, as the problem page describes for "null outside
bounds") is written alongside for completeness but is not the recommended upload.
"""
from __future__ import annotations

import hashlib
import json
import zipfile
from pathlib import Path

import numpy as np
import rasterio

from . import grid


def sha256_path(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write(dots: np.ndarray, out_tif: Path, mode: str = "zeros") -> Path:
    """Write a binary dot raster as a float32 GeoTIFF on the official grid."""
    prof = grid.template_profile()
    foot = grid.footprint()
    arr = np.where(dots & foot, 1.0, 0.0).astype(np.float32)
    nodata = None
    if mode == "nan":
        arr[~foot] = np.nan
        nodata = np.nan
    elif mode != "zeros":
        raise ValueError(mode)
    out_tif.parent.mkdir(parents=True, exist_ok=True)
    with rasterio.open(out_tif, "w", driver="GTiff", height=prof["height"], width=prof["width"], count=1,
                       dtype="float32", crs=prof["crs"], transform=prof["transform"], nodata=nodata,
                       compress="deflate", predictor=2, tiled=True, blockxsize=256, blockysize=256) as dst:
        dst.write(arr, 1)
    return out_tif


def zip_single(tif: Path) -> Path:
    z = tif.with_suffix(".zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(tif, arcname=tif.name)
    return z


def validate(tif: "Path | str") -> dict:
    """Independent re-read of the written bytes against the sample_submission template."""
    tif = Path(tif)
    with rasterio.open(grid.DATA / "sample_submission.tif") as t:
        t_crs, t_tr, t_w, t_h = t.crs, t.transform, t.width, t.height
        foot = np.isfinite(t.read(1))
    with rasterio.open(tif) as src:
        a = src.read(1)
        checks = {
            "single_band": src.count == 1,
            "dtype_float32": src.dtypes[0] == "float32",
            "crs_matches_template": src.crs == t_crs,
            "transform_matches_template": src.transform == t_tr,
            "shape_matches_template": (src.width, src.height) == (t_w, t_h),
            "crs_is_epsg_32611": src.crs.to_epsg() == 32611,
        }
        nodata = src.nodata
    inside = a[foot]
    outside = a[~foot]
    checks.update({
        "in_footprint_all_finite": bool(np.isfinite(inside).all()),
        "in_footprint_range_0_1": bool(np.nanmin(inside) >= 0.0 and np.nanmax(inside) <= 1.0),
        "outside_footprint_zero_or_nan": bool(np.all((outside == 0) | ~np.isfinite(outside))),
        "no_inf_anywhere": bool(not np.isinf(a).any()),
    })
    whole_finite = bool(np.isfinite(a).all())
    checks["whole_array_finite_(zeros_mode)"] = whole_finite or bool(np.isnan(outside).any() and np.isfinite(inside).all())
    cat = grid.catalogue()
    from scipy import ndimage
    d = ndimage.distance_transform_edt(~cat)
    dots = (a > 0) & foot
    summary = {
        "file": tif.name, "bytes": tif.stat().st_size, "sha256": sha256_path(tif),
        "emitted_positive_pixels": int(dots.sum()), "unique_values_in_footprint": [float(v) for v in np.unique(inside)[:5]],
        "on_catalogue_dots": int((dots & cat).sum()), "dots_within_2px_of_catalogue": int((dots & (d <= 2)).sum()),
        "whole_array_finite": whole_finite, "nodata_tag": None if nodata is None else ("nan" if np.isnan(nodata) else float(nodata)),
        "checks": checks, "all_checks_passed": all(checks.values()),
    }
    return summary


def write_bundle(dots: np.ndarray, out_dir: Path, slug: str, note: str) -> dict:
    """Write zeros + nan GeoTIFFs, a zip of the zeros file, validate each and return the receipt."""
    out_dir.mkdir(parents=True, exist_ok=True)
    rec = {"slug": slug, "submission_note": note, "note_length": len(note), "files": {}}
    assert len(note) <= 140, "submission note must be <= 140 characters"
    for mode in ("zeros", "nan"):
        p = write(dots, out_dir / f"{slug}-{mode}.tif", mode)
        rec["files"][mode] = validate(p)
    z = zip_single(out_dir / f"{slug}-zeros.tif")
    rec["files"]["zeros_zip"] = {"file": z.name, "bytes": z.stat().st_size, "sha256": sha256_path(z)}
    (out_dir / f"{slug}-receipt.json").write_text(json.dumps(rec, indent=1) + "\n")
    return rec
