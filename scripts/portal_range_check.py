#!/usr/bin/env python3
"""Diagnose the portal error "Predicted values must be in range [0, 1]".

This is a read-only fact report for ONE single-band GeoTIFF. It does not
generate, repair, or clear anything, and it cannot predict whether the portal
accepts a file: the portal's validator is not in this repository and the
organizer data/portal are not reachable from the sandbox.

Two different interpretations of "in range" are reported side by side:

* ``naive_whole_array_pass``: ``np.all((a >= 0) & (a <= 1))`` over every pixel.
  NaN fails this test, so a NaN-outside file fails it even though the official
  rule allows NaN outside the bounds. This is the most likely way a naive
  range check fails a valid file (a hypothesis, not a confirmed portal rule).
* ``nan_aware_pass``: every finite value lies in [0, 1]; NaN/null is ignored.

Usage:  python scripts/portal_range_check.py FILE.tif [FILE2.tif ...] [--out report.json]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
import rasterio

SCHEMA = "portal-range-check-v1"
NOT_ESTABLISHED = (
    "Portal acceptance is not established by this report. The portal validator, "
    "its error logic and the official sample grid are not available in this sandbox."
)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _json_safe(value):
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    return value


def check(path: Path) -> dict:
    report: dict = {"file": str(path), "schema": SCHEMA, "not_established": NOT_ESTABLISHED}
    if not path.is_file():
        report.update(ok_format=False, error="file not found")
        return report
    report["file_sha256"] = _sha256(path)
    if path.suffix.lower() != ".tif":
        report.update(ok_format=False, error="input must be a single .tif (unzip archives first)")
        return report
    try:
        src_ctx = rasterio.open(path)
    except (rasterio.errors.RasterioIOError, OSError) as exc:
        report.update(ok_format=False, error=f"unreadable GeoTIFF: {exc}")
        return report
    with src_ctx as src:
        report["count"] = int(src.count)
        report["dtype"] = src.dtypes[0]
        report["nodata"] = None if src.nodata is None else (None if math.isnan(src.nodata) else float(src.nodata))
        report["nodata_is_nan"] = bool(src.nodata is not None and math.isnan(src.nodata))
        report["width"], report["height"] = int(src.width), int(src.height)
        report["crs_epsg"] = src.crs.to_epsg() if src.crs else None
        report["transform"] = [float(v) for v in src.transform[:6]]
        if src.count != 1:
            report.update(ok_format=False, error="must have exactly one band")
            return report
        data = src.read(1).astype(np.float64)
    nan_count = int(np.count_nonzero(np.isnan(data)))
    inf_count = int(np.count_nonzero(np.isinf(data)))
    finite = data[np.isfinite(data)]
    outside = int(np.count_nonzero((finite < 0) | (finite > 1)))
    report.update(
        nan_count=nan_count,
        inf_count=inf_count,
        finite_count=int(finite.size),
        finite_min=float(finite.min()) if finite.size else None,
        finite_max=float(finite.max()) if finite.size else None,
        finite_outside_01_count=outside,
        positive_count=int(np.count_nonzero(finite > 0)),
        naive_whole_array_pass=bool(np.all((data >= 0) & (data <= 1))),
        nan_aware_pass=bool(finite.size > 0 and outside == 0 and inf_count == 0),
    )
    report["ok_format"] = True
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--out", type=Path, default=None, help="optional JSON report path")
    args = parser.parse_args(argv)
    reports = [check(p) for p in args.paths]
    text = json.dumps(_json_safe(reports if len(reports) > 1 else reports[0]), indent=2,
                      sort_keys=True, allow_nan=False) + "\n"
    if args.out:
        tmp = args.out.with_name(args.out.name + ".partial")
        tmp.write_text(text, encoding="utf8")
        tmp.replace(args.out)
    else:
        sys.stdout.write(text)
    return 0 if all(r.get("ok_format") for r in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
