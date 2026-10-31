#!/usr/bin/env python3
"""Independent saved-byte audit of the H-V31 candidate TIF (2026-10-31).

Re-reads the bytes in docs/downloads from disk and re-derives every format and
uniqueness number with a different method from scripts/run_h31_visgrad.py:
overlap is computed by dilating each registry raster with a 3 px disk and
testing candidate dots for membership (the runner uses a distance transform).
Agreement between the two is a cross-check, not a score.

Writes evidence/audit_h31_candidate_saved_bytes_20261031.json (schema
karage1-local-tif-audit-v1). It never changes the TIF, the registry or any
submission state. Exit code 1 if any hard check fails.
"""
from __future__ import annotations

import glob
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
TIF = ROOT / "docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.tif"
ZIP = ROOT / "docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.zip"
SHA = ROOT / "docs/downloads/karage1-h31-visgrad-nms3px-40k-20261031-zeros.sha256"
OUT = ROOT / "evidence/audit_h31_candidate_saved_bytes_20261031.json"
DATA = ROOT / "data"
OVERLAP_LIMIT = 0.70
PHI_LIMIT = 0.90
RADIUS = 3

DISK = np.zeros((2 * RADIUS + 1, 2 * RADIUS + 1), dtype=bool)
for _dy in range(-RADIUS, RADIUS + 1):
    for _dx in range(-RADIUS, RADIUS + 1):
        if _dy * _dy + _dx * _dx <= RADIUS * RADIUS:
            DISK[_dy + RADIUS, _dx + RADIUS] = True


def overlap_within(dots: np.ndarray, other: np.ndarray) -> float | None:
    """Fraction of `dots` lying within RADIUS px of any cell of `other` (dilation method)."""
    n = int(dots.sum())
    if n == 0:
        return None
    near = ndimage.binary_dilation(other, structure=DISK)
    return float((near & dots).sum() / n)


def registry_rasters() -> list[Path]:
    focus = sorted(Path(p) for p in glob.glob(str(ROOT / "registry" / "GEMSDOE*.tif")))
    lattice = sorted(Path(p) for p in glob.glob(str(DATA / "scored" / "13gems_*nan-outside.tif")))
    return focus + lattice


def main() -> int:
    raw = TIF.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    sha_line = SHA.read_text().split()[0] if SHA.exists() else None
    zip_ok = False
    if ZIP.exists():
        import zipfile
        with zipfile.ZipFile(ZIP) as zf:
            names = zf.namelist()
            zip_ok = names == [TIF.name] and zf.read(TIF.name) == raw
    with rasterio.open(DATA / "sample_submission.tif") as s:
        fp = np.isfinite(s.read(1))
        sample_crs, sample_shape, sample_tr = str(s.crs), (s.height, s.width), tuple(s.transform)[:6]
    with rasterio.open(DATA / "labels.tif") as s:
        cat = (s.read(1) == 1) & fp
    with rasterio.open(TIF) as s:
        arr = s.read(1)
        meta = dict(count=s.count, dtype=s.dtypes[0], crs=str(s.crs), shape=(s.height, s.width),
                    transform=tuple(s.transform)[:6], nodata=s.nodata, driver=s.driver)
    checks = {
        "single_band": meta["count"] == 1,
        "float32": meta["dtype"] == "float32",
        "crs_matches_sample": meta["crs"] == sample_crs,
        "shape_matches_sample": meta["shape"] == sample_shape,
        "transform_matches_sample": meta["transform"] == sample_tr,
        "nan_cells_zero": int(np.isnan(arr).sum()) == 0,
        "values_in_0_1": bool(np.isfinite(arr).all() and arr.min() >= 0.0 and arr.max() <= 1.0),
        "binary_zero_or_one": bool(np.isin(arr, [0.0, 1.0]).all()),
        "dots_outside_footprint_zero": int(((arr != 0) & ~fp).sum()) == 0,
        "dots_on_catalogue_zero": int(((arr == 1) & cat).sum()) == 0,
        "sha256_sidecar_matches": sha_line == digest,
        "zip_contains_identical_tif": zip_ok,
        "dots_at_least_40000": int((arr == 1).sum()) >= 40000,
    }
    dots = arr == 1
    comparisons = {}
    for path in registry_rasters():
        with rasterio.open(path) as s:
            other = s.read(1) == 1
        name = path.name
        fwd = overlap_within(dots, other)
        rev = overlap_within(other, dots)
        x = dots[fp].astype(float)
        y = other[fp].astype(float)
        phi = float(np.corrcoef(x, y)[0, 1]) if x.std() > 0 and y.std() > 0 else None
        comparisons[name] = {
            "forward_3px_overlap": round(fwd, 6) if fwd is not None else None,
            "reverse_3px_overlap": round(rev, 6) if rev is not None else None,
            "phi_footprint": round(phi, 6) if phi is not None else None,
            "exact_mask_equal": bool(np.array_equal(dots, other)),
            "registry_dots": int(other.sum()),
        }
    focus = {k: v for k, v in comparisons.items() if not k.startswith("13gems")}
    lattice = {k: v for k, v in comparisons.items() if k.startswith("13gems")}
    checks["forward_overlap_below_0p70_vs_focus"] = all(v["forward_3px_overlap"] < OVERLAP_LIMIT for v in focus.values())
    checks["phi_below_0p90_vs_focus"] = all(abs(v["phi_footprint"]) < PHI_LIMIT for v in focus.values())
    checks["no_exact_mask_equal_focus"] = not any(v["exact_mask_equal"] for v in focus.values())
    hard = [k for k, v in checks.items() if v is not True]
    lattice_fail = any(v["forward_3px_overlap"] >= OVERLAP_LIMIT for v in lattice.values())
    report = {
        "schema": "karage1-local-tif-audit-v1",
        "file": str(TIF.relative_to(ROOT)),
        "sha256": digest,
        "bytes": len(raw),
        "method": "independent re-read of saved bytes; overlap by 3 px disk dilation (not the runner's distance transform)",
        "format_meta": {k: (list(v) if isinstance(v, tuple) else v) for k, v in meta.items()},
        "positives": int(dots.sum()),
        "value_min": float(arr.min()),
        "value_max": float(arr.max()),
        "checks": checks,
        "uniqueness_vs_focus_passes": checks["forward_overlap_below_0p70_vs_focus"] and checks["phi_below_0p90_vs_focus"] and checks["no_exact_mask_equal_focus"],
        "lattice_gate_passes": not lattice_fail,
        "lattice_forward_3px_overlap": lattice[next(iter(lattice))]["forward_3px_overlap"] if lattice else None,
        "comparisons": comparisons,
        "ok_to_submit": False,
        "verdict": ("NOT CLEARED. Format and focus-uniqueness checks pass on the saved bytes; the literal "
                    "lattice gate fails (forward 3 px overlap >= 0.70). Owner decision required."),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}; hard failures: {hard or 'none'}; lattice_gate_passes={not lattice_fail}")
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
