#!/usr/bin/env python3
"""NaN-outside GeoTIFF adapter for the GEMS submission format (LOCAL, not the shared template).

Why this file exists
--------------------
* Public spec (DrivenData, "Submission format"): single-band float32 GeoTIFF, EPSG:32611,
  same CRS/shape/geotransform as the sample, values in [0, 1], and "data outside the bounds
  is null or nan".
* The organizer's sample_submission.tif encodes the footprint this way: its 7,111,787 cells
  outside the 5,167,373-cell footprint are NaN (nodata = NaN).
* The shared template (vendor/gems57, pinned to upstream bytes by vendor/PROVENANCE.json and
  tests/test_template_integrity.py) writes zeros outside the footprint and rejects any NaN.
  That policy is internally consistent but is NOT the literal public encoding. Editing the
  pinned vendor files would be a private fork, so this adapter leaves them untouched and
  implements the NaN encoding separately. The discrepancy is reported as an open item for the
  template owner; it is not resolved here.

This module writes and re-reads the bytes on disk. It never clips, fills or repairs values.
Local format validity is NOT uniqueness clearance, organizer acceptance, or a slot selection.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]
SENTINELS = (-9999.0, -999.0, 9999.0, -3.4e38, 1e30)  # same list as the shared validator
EPSG = 32611
CELL_M = 100.0
NAME_NOTE_MAX = 140


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _reference(sample: Path) -> dict:
    with rasterio.open(sample) as ref:
        return dict(shape=(ref.height, ref.width), crs=str(ref.crs),
                    transform=tuple(ref.transform)[:6], bounds=tuple(ref.bounds),
                    res=tuple(ref.res))


def validate_nan_outside(path: Path, sample: Path, footprint: np.ndarray,
                         catalogue: np.ndarray | None = None) -> dict:
    """Re-read the GeoTIFF bytes and check every official-format rule. Returns a receipt."""
    path, sample = Path(path), Path(sample)
    fp = np.asarray(footprint, dtype=bool)
    ref = _reference(sample)
    with rasterio.open(path) as ds:
        a = ds.read(1)
        meta = dict(count=ds.count, dtype=ds.dtypes[0], crs=str(ds.crs), shape=[ds.height, ds.width],
                    transform=list(tuple(ds.transform)[:6]), bounds=list(ds.bounds),
                    res=list(ds.res), nodata=("nan" if ds.nodata is not None and np.isnan(ds.nodata)
                                              else ds.nodata))
    if a.shape != fp.shape or a.shape != ref["shape"]:
        raise ValueError(f"shape {a.shape} != footprint {fp.shape} != sample {ref['shape']}")
    finite = np.isfinite(a)
    inside = fp
    fin_vals = a[inside & finite]
    catalogue_hits = None
    if catalogue is not None:
        catalogue_hits = int(((a > 0) & np.asarray(catalogue, bool) & finite).sum())
    checks = {
        "single_band": meta["count"] == 1,
        "dtype_float32": meta["dtype"] == "float32",
        "crs_epsg_32611": meta["crs"] == f"EPSG:{EPSG}",
        "shape_matches_sample": tuple(meta["shape"]) == ref["shape"],
        "transform_matches_sample": tuple(meta["transform"]) == ref["transform"],
        "bounds_match_sample": tuple(meta["bounds"]) == ref["bounds"],
        "cell_100m": tuple(meta["res"]) == (CELL_M, CELL_M),
        "no_inf_anywhere": not np.isinf(a).any(),
        "in_footprint_all_finite": bool(inside.any() and finite[inside].all()),
        "outside_footprint_all_nan": bool(not finite[~inside].any()),
        "range_0_1_inside_footprint": bool(fin_vals.size and fin_vals.min() >= 0.0 and fin_vals.max() <= 1.0),
        "no_sentinel_values_inside": bool(not np.isin(fin_vals, SENTINELS).any()),
        "nodata_is_nan": meta["nodata"] == "nan",
    }
    if catalogue is not None:
        checks["zero_dots_on_mapped_catalogue"] = catalogue_hits == 0
    return dict(file=str(path), sha256=sha256_file(path), checks=checks,
                all_checks_passed=bool(all(checks.values())),
                in_footprint_positive=int((fin_vals > 0).sum()),
                in_footprint_min=float(fin_vals.min()) if fin_vals.size else None,
                in_footprint_max=float(fin_vals.max()) if fin_vals.size else None,
                outside_nan_cells=int((~finite & ~inside).sum()),
                outside_finite_cells=int((finite & ~inside).sum()),
                catalogue_positive_hits=catalogue_hits, meta=meta,
                validation_class="local official-format preflight on the bytes on disk; "
                                 "not organizer acceptance, uniqueness clearance or slot selection")


def write_nan_outside(path: Path, prediction: np.ndarray, sample: Path, footprint: np.ndarray, *,
                      name: str, note: str, catalogue: np.ndarray | None = None,
                      metadata: dict | None = None) -> dict:
    """Write TIF + single-TIF ZIP + JSON receipt atomically; refuse to overwrite or repair."""
    if not isinstance(name, str) or not name.strip() or len(name) > NAME_NOTE_MAX:
        raise ValueError("name must be non-empty and at most 140 characters")
    if not isinstance(note, str) or not note.strip() or len(note) > NAME_NOTE_MAX:
        raise ValueError("note must be non-empty and at most 140 characters")
    p = np.asarray(prediction)
    fp = np.asarray(footprint, dtype=bool)
    if p.ndim != 2 or p.shape != fp.shape or not fp.any():
        raise ValueError("prediction and footprint must be matching non-empty 2-D arrays")
    if not np.issubdtype(p.dtype, np.number):
        raise ValueError("prediction must be numeric")
    if not np.isfinite(p).all() or (p < 0).any() or (p > 1).any():
        raise ValueError("prediction must be finite and in [0,1]; no silent repair")
    if np.any((p > 0) & ~fp):
        raise ValueError("positive prediction mass outside the footprint")
    cat = None
    if catalogue is not None:
        cat = np.asarray(catalogue, dtype=bool)
        if cat.shape != p.shape:
            raise ValueError("catalogue shape must match the prediction grid")
        if np.any((p > 0) & cat):
            raise ValueError("positive prediction mass on the mapped catalogue")

    path = Path(path)
    if path.suffix.lower() not in {".tif", ".tiff"}:
        raise ValueError("path must end in .tif or .tiff")
    zip_path, receipt_path = path.with_suffix(".zip"), path.with_suffix(".json")
    existing = [c for c in (path, zip_path, receipt_path) if c.exists()]
    if existing:
        raise FileExistsError(f"refusing to overwrite: {existing}")
    path.parent.mkdir(parents=True, exist_ok=True)
    ref = _reference(Path(sample))
    arr = np.where(fp, p.astype(np.float32), np.float32("nan")).astype(np.float32)
    tmp_tif = tmp_zip = tmp_json = None
    committed: list[Path] = []
    try:
        fd, n = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".tif", dir=path.parent)
        os.close(fd)
        tmp_tif = Path(n)
        profile = dict(driver="GTiff", height=arr.shape[0], width=arr.shape[1], count=1,
                       dtype="float32", crs=f"EPSG:{EPSG}", transform=from_origin(
                           ref["transform"][2], ref["transform"][5], ref["transform"][0],
                           -ref["transform"][4]), nodata=float("nan"),
                       tiled=True, blockxsize=256, blockysize=256, compress="deflate", predictor=2)
        with rasterio.open(tmp_tif, "w", **profile) as dst:
            dst.write(arr, 1)
            dst.set_band_description(1, "predicted_new_fault_probability")
        validation = validate_nan_outside(tmp_tif, Path(sample), fp, cat)
        if not validation["all_checks_passed"]:
            raise ValueError(f"on-disk NaN-outside validator rejected output: {validation['checks']}")
        if validation["in_footprint_positive"] != int((p[fp] > 0).sum()):
            raise ValueError("on-disk positive support changed during serialization")

        fd, n = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".zip", dir=path.parent)
        os.close(fd)
        tmp_zip = Path(n)
        with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
            info = zipfile.ZipInfo(path.name, date_time=(2026, 10, 29, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, tmp_tif.read_bytes())
        with zipfile.ZipFile(tmp_zip) as z:
            if z.namelist() != [path.name] or z.read(path.name) != tmp_tif.read_bytes():
                raise IOError("single-TIFF ZIP round trip failed")

        receipt = dict(
            file=path.name, zip_file=zip_path.name, receipt_file=receipt_path.name,
            sha256=validation["sha256"], bytes=tmp_tif.stat().st_size,
            zip_sha256=sha256_file(tmp_zip),
            submission_name=name, submission_note=note, submission_note_chars=len(note),
            outside_encoding="nan", validator=validation,
            approved_for_weekly_slot=False, promoted=False, submission_slots_used=0,
            status="locally validated on the bytes on disk; NOT uniqueness-cleared; NOT organizer acceptance",
            metadata=metadata or {},
        )
        fd, n = tempfile.mkstemp(prefix=f".{path.stem}.", suffix=".json", dir=path.parent)
        os.close(fd)
        tmp_json = Path(n)
        tmp_json.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        for src, dst in ((tmp_zip, zip_path), (tmp_json, receipt_path), (tmp_tif, path)):
            os.chmod(src, 0o644)
            os.replace(src, dst)
            committed.append(dst)
        return receipt
    except Exception:
        for dst in committed:
            dst.unlink(missing_ok=True)
        raise
    finally:
        for tmp in (tmp_tif, tmp_zip, tmp_json):
            if tmp is not None:
                tmp.unlink(missing_ok=True)
