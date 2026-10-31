#!/usr/bin/env python3
"""Measure the nine focus GEMSDOE rasters against each other, the catalogue and the lattice witness.

Read-only analysis. It writes ``evidence/focus_nine_audit_20261031.json`` and produces
no submission raster and no score. Every number here is a geometry or overlap
measurement on files; none is a DTI, a leaderboard estimate or an organizer receipt.

Inputs (all paths relative to the repository root):
  registry/GEMSDOE{24,25,27,28,30,31,32,33,36}*.tif   user-listed focus submissions
  data/sample_submission.tif                          grid + footprint template (mirror, NOT organizer-authenticated)
  data/labels.tif, data/existing_faults.tif           catalogue fault pixels (mirror, byte-identical)
  data/scored/13gems_*_nan-outside.tif                13GEMS lattice probe (the registry witness)

Definitions:
  dots       = finite cells whose value == 1 (every focus raster is binary {0,1})
  fwd3(A->B) = fraction of A dots with a B dot at Euclidean distance <= 3 px (300 m)
  Spearman   = Spearman on the footprint; for binary rasters this equals Pearson (phi)
  exact      = identical positive masks (value == 1) on the whole grid
"""
from __future__ import annotations

import glob
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "focus_nine_audit_20261031.json"
RADIUS_PX = 3.0
PIXEL_M = 100.0

FOCUS = {
    "GEMSDOE24": "GEMSDOE24_*.tif",
    "GEMSDOE25": "GEMSDOE25_*.tif",
    "GEMSDOE27": "GEMSDOE27_*.tif",
    "GEMSDOE28": "GEMSDOE28_*.tif",
    "GEMSDOE30": "GEMSDOE30_*.tif",
    "GEMSDOE31": "GEMSDOE31_*.tif",
    "GEMSDOE32": "GEMSDOE32_*.tif",
    "GEMSDOE33": "GEMSDOE33_*.tif",
    "GEMSDOE36": "GEMSDOE36_*.tif",
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path):
    with rasterio.open(path) as src:
        arr = src.read(1)
        meta = {
            "crs": str(src.crs),
            "width": src.width,
            "height": src.height,
            "dtype": src.dtypes[0],
            "transform": [float(x) for x in src.transform][:6],
            "nodata": None if src.nodata is None else float(src.nodata),
        }
    return arr, meta


def grid_meta(meta: dict, ref: dict) -> dict:
    return {
        "same_crs_shape_transform": meta["crs"] == ref["crs"]
        and meta["width"] == ref["width"]
        and meta["height"] == ref["height"]
        and np.allclose(meta["transform"], ref["transform"]),
    }


def fwd3(a: np.ndarray, b: np.ndarray) -> float | None:
    """Fraction of A's dots that have a B dot within RADIUS_PX."""
    n = int(a.sum())
    if n == 0:
        return None
    if int(b.sum()) == 0:
        return 0.0
    dist_to_b = distance_transform_edt(~b)
    return float((dist_to_b[a] <= RADIUS_PX).mean())


def phi(a: np.ndarray, b: np.ndarray, fp: np.ndarray) -> float | None:
    """Spearman for binary rasters equals Pearson on the indicator (rank map is affine)."""
    x = a[fp].astype(np.float64)
    y = b[fp].astype(np.float64)
    sx, sy = x.std(), y.std()
    if sx == 0 or sy == 0:
        return None
    return float(np.corrcoef(x, y)[0, 1])


def main() -> int:
    ss, ss_meta = read(ROOT / "data" / "sample_submission.tif")
    fp = np.isfinite(ss)
    footprint_cells = int(fp.sum())
    labels, _ = read(ROOT / "data" / "labels.tif")
    catalogue = labels == 1
    cat_dist = distance_transform_edt(~catalogue)  # px distance to nearest catalogue cell

    lattice_paths = glob.glob(str(ROOT / "data" / "scored" / "13gems_*nan-outside.tif"))
    if len(lattice_paths) != 1:
        print("13GEMS lattice raster not restored; run scripts/restore_karage1_data.py", file=sys.stderr)
        return 2

    rasters = {}
    files = {}
    for site, pattern in FOCUS.items():
        matches = sorted(glob.glob(str(ROOT / "registry" / pattern)))
        if len(matches) != 1:
            print(f"expected exactly one file for {site}: {matches}", file=sys.stderr)
            return 2
        path = Path(matches[0])
        arr, meta = read(path)
        rasters[site] = arr == 1
        values = arr[np.isfinite(arr)]
        files[site] = {
            "file": path.name,
            "sha256": sha256(path),
            "bytes": path.stat().st_size,
            "grid": grid_meta(meta, ss_meta),
            "nodata": meta["nodata"],
            "nan_cells": int(np.isnan(arr).sum()),
            "nan_inside_footprint": int(np.isnan(arr[fp]).sum()),
            "values_unique": sorted(float(v) for v in np.unique(values)),
            "min": float(values.min()),
            "max": float(values.max()),
            "dots": int(rasters[site].sum()),
            "dots_outside_footprint": int((rasters[site] & ~fp).sum()),
            "dots_on_catalogue_px": int((rasters[site] & catalogue).sum()),
            "dots_1px_from_catalogue": int((rasters[site] & (cat_dist > 0) & (cat_dist <= 1.0)).sum()),
            "dots_1_to_2px_from_catalogue": int((rasters[site] & (cat_dist > 1.0) & (cat_dist <= 2.0)).sum()),
            "dots_2_to_3px_from_catalogue": int((rasters[site] & (cat_dist > 2.0) & (cat_dist <= 3.0)).sum()),
            "dots_beyond_3px_from_catalogue": int((rasters[site] & (cat_dist > 3.0)).sum()),
        }

    lat, lat_meta = read(Path(lattice_paths[0]))
    lattice = lat == 1
    files["13GEMS_lattice_probe"] = {
        "file": Path(lattice_paths[0]).name,
        "sha256": sha256(Path(lattice_paths[0])),
        "dots": int(lattice.sum()),
        "grid": grid_meta(lat_meta, ss_meta),
    }
    rasters["13GEMS_lattice_probe"] = lattice

    # The B2 relationship: is B2 a strict subset of the GEMSDOE25/30 parent, and which dots were removed?
    b2, d28 = rasters["GEMSDOE32"], rasters["GEMSDOE25"]
    removed = d28 & ~b2
    removed_dist = cat_dist[removed]
    b2_vs_d28 = {
        "b2_dots": int(b2.sum()),
        "d28_dots": int(d28.sum()),
        "b2_subset_of_d28": bool((b2 & ~d28).sum() == 0),
        "removed_dots": int(removed.sum()),
        "removed_on_catalogue_px_distance0": int((removed_dist == 0).sum()),
        "removed_distance_1px_or_less_excluding0": int(((removed_dist > 0) & (removed_dist <= 1)).sum()),
        "removed_distance_1_to_2px": int(((removed_dist > 1) & (removed_dist <= 2)).sum()),
        "removed_distance_gt2px": int((removed_dist > 2).sum()),
        "removed_max_distance_px": float(removed_dist.max()) if removed.any() else None,
        "removed_median_distance_px": float(np.median(removed_dist)) if removed.any() else None,
        "d28_dots_within_2px_of_catalogue_incl_on": int((d28 & (cat_dist <= 2.0)).sum()),
        "claim_checked": "B2 described as 'd2.8 minus dots at or within 2 px of the mirrored catalogue' (knowledge/session-review-arena-cfabff7e.md)",
    }

    # Pairwise matrix over the nine + lattice probe.
    names = list(rasters)
    pairwise = {}
    for a in names:
        pairwise[a] = {}
        for b in names:
            if a == b:
                continue
            pairwise[a][b] = {
                "exact_positive_mask_equal": bool(np.array_equal(rasters[a], rasters[b])),
                "fwd3_a_dots_within_3px_of_b": fwd3(rasters[a], rasters[b]),
                "phi_spearman_footprint": phi(rasters[a], rasters[b], fp),
            }
    # Lattice-only check, so the saturation claim in registry/registry_roles.json is re-measured here.
    lattice_fwd = {site: fwd3(rasters[site], lattice) for site in FOCUS}
    lattice_rev = {site: fwd3(lattice, rasters[site]) for site in FOCUS}

    report = {
        "schema": "karage1-focus-nine-audit-v1",
        "date_utc": "2026-10-31",
        "status_label": "MEASURED GEOMETRY ON LOCAL MIRROR FILES; NOT A SCORE",
        "scoring_label": "none (no HOLDOUT-DTI, no ORGANIZER-CONFIRMED value is produced by this script)",
        "grid": {**ss_meta, "footprint_cells": footprint_cells, "pixel_m": PIXEL_M,
                 "radius_px": RADIUS_PX, "sample_submission_sha256": sha256(ROOT / "data" / "sample_submission.tif")},
        "catalogue_source": "data/labels.tif (mirror; byte-identical to data/existing_faults.tif)",
        "files": files,
        "b2_vs_d28": b2_vs_d28,
        "pairwise_nine_plus_lattice": pairwise,
        "lattice_probe_fwd3_site_dots_within_3px_of_lattice": lattice_fwd,
        "lattice_probe_fwd3_lattice_dots_within_3px_of_site": lattice_rev,
        "limitations": [
            "Catalogue = mirror pixels, not organizer labels; hidden competition truth is unknown.",
            "The lattice probe is a covering grid; forward overlap against it saturates for any dotted raster.",
            "Only the nine listed focus files plus the lattice probe are measured; the wider GEMSDOE series is not restored.",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    def _no_nan(o):
        # Strict JSON: NaN is not a valid JSON constant, so write null instead.
        if isinstance(o, float) and not math.isfinite(o):
            return None
        if isinstance(o, dict):
            return {k: _no_nan(v) for k, v in o.items()}
        if isinstance(o, list):
            return [_no_nan(v) for v in o]
        return o
    OUT.write_text(json.dumps(_no_nan(report), indent=2, allow_nan=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
