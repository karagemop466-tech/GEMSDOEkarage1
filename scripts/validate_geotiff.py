#!/usr/bin/env python3
"""Reopen a GeoTIFF and diagnose format/range against a supplied sample grid.

This tool never generates predictions, repairs values, checks novelty/holdout,
proves that the template is official, or authorizes a competition submission.
It reports the mutually different null/NaN-outside and strict-whole-array checks
separately because actual portal behavior is unknown.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import tempfile

import numpy as np
import rasterio

try:
    from scripts.audit_references import raster_checks, read_grid, sha256
except ModuleNotFoundError:
    # Direct `python scripts/validate_geotiff.py` makes scripts/ the import root.
    from audit_references import raster_checks, read_grid, sha256


def diagnose(candidate: Path, template: Path, expected_template_sha256: str | None = None) -> dict:
    if candidate.resolve() == template.resolve() or (
        candidate.exists() and template.exists() and os.path.samefile(candidate, template)
    ):
        raise ValueError("candidate and template must be distinct files")
    template_hash = sha256(template)
    if expected_template_sha256 is not None:
        if not re.fullmatch(r"[0-9a-f]{64}", expected_template_sha256):
            raise ValueError("template SHA-256 must be 64 lowercase hex characters")
        if template_hash != expected_template_sha256:
            raise ValueError("template SHA-256 mismatch")
    # Use both the metadata nodata mask and actual finiteness. This prevents
    # finite nodata sentinels from being mistaken for footprint pixels.
    with rasterio.open(template) as t:
        if t.count != 1:
            raise ValueError("template must have exactly one band")
        tdata = t.read(1, masked=True)
        footprint = ~np.ma.getmaskarray(tdata) & np.isfinite(tdata.data)
        tmeta = {
            "driver": t.driver, "shape": list(t.shape),
            "crs": t.crs.to_string() if t.crs else None,
            "transform": list(t.transform)[:6], "dtype": t.dtypes[0],
            "nodata_is_nan": bool(t.nodata is not None and np.isnan(t.nodata)),
        }
    if not footprint.any():
        raise ValueError("sample footprint is empty")
    if (tmeta["driver"] != "GTiff" or tmeta["crs"] != "EPSG:32611" or
            tmeta["transform"][:2] != [100.0, 0.0] or tmeta["transform"][3:5] != [0.0, -100.0]):
        raise ValueError("template is not an EPSG:32611, 100 m, unrotated GeoTIFF")
    data, meta = read_grid(candidate)
    if data.shape != footprint.shape:
        raise ValueError("candidate shape does not match supplied sample")
    checks = raster_checks(data, meta, tmeta, footprint)
    with rasterio.open(candidate) as ds:
        masked = ds.read_masks(1) == 0
    checks["masked_inside_count"] = int(np.count_nonzero(masked & footprint))
    checks["outside_null_or_nan_count"] = int(np.count_nonzero((masked | np.isnan(data)) & ~footprint))
    checks["outside_all_null_or_nan"] = checks["outside_null_or_nan_count"] == int((~footprint).sum())
    checks["outside_unmasked_positive_count"] = int(np.count_nonzero(~footprint & ~masked & np.isfinite(data) & (data > 0)))
    base = bool(checks["mirror_grid_and_inside_values_pass"] and checks["masked_inside_count"] == 0)
    return {
        "schema": "karage1-format-diagnostics-v1",
        "candidate": str(candidate),
        "candidate_sha256": sha256(candidate),
        "template": str(template),
        "template_sha256": template_hash,
        "template_hash_matched_requested_pin": expected_template_sha256 is not None,
        "template_official_authenticity": "not established by this tool",
        "grid": meta,
        "footprint_pixels": int(footprint.sum()),
        "checks": checks,
        "diagnostics": {
            "grid_and_inside_pass": base,
            "nan_outside_variant_pass": bool(base and checks["outside_all_nan"]),
            "null_or_nan_outside_variant_pass": bool(base and checks["outside_all_null_or_nan"]),
            "strict_whole_array_variant_pass": bool(base and checks["whole_array_strict_finite_0_1"] and not checks["outside_unmasked_positive_count"]),
            "note": "These are separate local checks, not guarantees of organizer acceptance.",
        },
        "uniqueness_holdout_and_selector_checked": False,
        "submission_authorized": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("--template", type=Path, required=True)
    ap.add_argument("--template-sha256", help="Optional independently obtained sample hash pin")
    ap.add_argument("--out", type=Path, help="Optional JSON report path; stdout otherwise")
    args = ap.parse_args()
    try:
        if args.out:
            # Do not replace input bytes, even via an alias, symlink, or hard link.
            for source in (args.candidate, args.template):
                if args.out.resolve() == source.resolve() or (
                    args.out.exists() and source.exists() and os.path.samefile(args.out, source)
                ):
                    raise ValueError("report output must not overwrite candidate or template")
        result = diagnose(args.candidate, args.template, args.template_sha256)
        text = json.dumps(result, indent=2, allow_nan=False) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix='.' + args.out.name + '.', suffix='.partial', dir=args.out.parent)
            temp = Path(name)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                    fh.write(text)
                temp.replace(args.out)
            finally:
                temp.unlink(missing_ok=True)
            print(f"Diagnostic written to {args.out}; this is not upload authorization.")
        else:
            print(text, end="")
        return 0 if result["diagnostics"]["grid_and_inside_pass"] else 1
    except (OSError, ValueError) as exc:
        print(f"FORMAT DIAGNOSTIC FAILED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
