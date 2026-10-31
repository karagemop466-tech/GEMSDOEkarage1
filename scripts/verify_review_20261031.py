#!/usr/bin/env python3
"""Independent re-check used by the 2026-10-31 repo review (branch arena/afe07cea).

Reads local rasters only. Focus-site files were downloaded via the GitHub
contents API (api.github.com, not raw.githubusercontent.com) into a scratch
directory; their SHA-256 values are compared with the values the public
GEMSDOE pages print, so the bytes checked are the bytes the pages cite.

Usage:
    python scripts/verify_review_20261031.py --focus-dir /tmp/focus \
        --out evidence/review_afe07cea_20261031.json

Every number in the output is MEASURED on these bytes. None is a leaderboard
score. Nothing here selects or spends a submission slot.
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
import os
import sys

import numpy as np
import rasterio
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KP1 = "docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif"

# Focus files: name -> (expected sha256, local file name).
# Expected values are copied from the repo's public pages:
#   GEMSDOE24 / GEMSDOE25 -> docs/index.html (16-char prefixes; full value is
#     compared by prefix in the review note)
#   GEMSDOE32 B2          -> docs/GEMSDOE32.html (full 64-char value)
FOCUS = {
    "GEMSDOE24 nan (listed 0.2477)": (
        "68d0e2e4fcc594f9a23f56c44b885fee733d026d39be55e18ad2a07289525310",
        "g24n.tif",
    ),
    "GEMSDOE25 zeros (listed 0.2600)": (
        "3e78737f0da8dd2ca66cc6caac0ce8eeefcd6715707f8d1bd3091845cd9bcc30",
        "g25z.tif",
    ),
    "GEMSDOE32 B2 zeros (listed 0.2778)": (
        "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9",
        "g32b2.tif",
    ),
}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: str) -> np.ndarray:
    with rasterio.open(path) as ds:
        return ds.read(1).astype("float64")


def dot_cells(a: np.ndarray) -> np.ndarray:
    return np.argwhere(np.nan_to_num(a, nan=0.0) > 0)


def footprint_summary() -> dict:
    """Count NaN-outside vs zero-outside encodings across the repo's downloads."""
    out = {"nan_outside": [], "zeros_outside": [], "other": []}
    for p in sorted(glob.glob(os.path.join(REPO, "docs", "downloads", "*.tif"))):
        a = read(p)
        name = os.path.relpath(p, REPO)
        if np.isnan(a).any():
            out["nan_outside"].append(name)
        elif np.nanmin(a) >= 0 and np.nanmax(a) <= 1:
            out["zeros_outside"].append(name)
        else:
            out["other"].append(name)
    return {k: {"count": len(v), "files": v} for k, v in out.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--focus-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    kp_path = os.path.join(REPO, KP1)
    kp = read(kp_path)
    with rasterio.open(kp_path) as ds:
        kp_meta = {
            "crs_epsg": ds.crs.to_epsg(),
            "shape": list(ds.shape),
            "transform": list(ds.transform)[:6],
            "dtype": ds.dtypes[0],
            "count": ds.count,
            "nodata": ds.nodata,
        }
    kp_nan = int(np.isnan(kp).sum())
    kp_dots = dot_cells(kp)
    kp_checks = {
        "sha256": sha256(kp_path),
        "meta": kp_meta,
        "nan_cells": kp_nan,
        "min": float(np.nanmin(kp)),
        "max": float(np.nanmax(kp)),
        "positive_cells": int(len(kp_dots)),
        "values_in_0_1": bool(np.nanmin(kp) >= 0 and np.nanmax(kp) <= 1),
    }

    rng = np.random.default_rng(0)
    comparisons = {}
    focus_cells = {}
    for label, (expected, fname) in FOCUS.items():
        fp = os.path.join(args.focus_dir, fname)
        if not os.path.exists(fp):
            comparisons[label] = {"error": f"missing {fp}"}
            continue
        f = read(fp)
        with rasterio.open(fp) as ds:
            same_grid = (
                ds.crs.to_epsg() == kp_meta["crs_epsg"]
                and list(ds.shape) == kp_meta["shape"]
                and list(ds.transform)[:6] == kp_meta["transform"]
            )
        fd = dot_cells(f)
        focus_cells[label] = fd
        d, _ = cKDTree(fd).query(kp_dots)
        valid = np.flatnonzero(np.isfinite(f).ravel())
        idx = rng.choice(valid, size=min(200_000, valid.size), replace=False)
        rho, _ = spearmanr(kp.ravel()[idx], np.nan_to_num(f, nan=0.0).ravel()[idx])
        comparisons[label] = {
            "sha256": sha256(fp),
            "sha256_matches_public_page": sha256(fp) == expected,
            "same_grid_as_kp1": bool(same_grid),
            "nan_cells": int(np.isnan(f).sum()),
            "positive_cells": int(len(fd)),
            "share_of_kp1_dots_within_3px": round(float((d <= 3).mean()), 4),
            "spearman_200k_random_cells": round(float(rho), 4),
        }

    # Strict-subset check for the 0.2778 mechanism (B2 inside GEMSDOE25 D2.8).
    subset = {}
    b2 = read(os.path.join(args.focus_dir, "g32b2.tif")) > 0 if os.path.exists(
        os.path.join(args.focus_dir, "g32b2.tif")) else None
    d28 = read(os.path.join(args.focus_dir, "g25z.tif")) > 0 if os.path.exists(
        os.path.join(args.focus_dir, "g25z.tif")) else None
    if b2 is not None and d28 is not None:
        subset = {
            "b2_positive": int(b2.sum()),
            "d28_positive": int(d28.sum()),
            "b2_inside_d28": int((b2 & d28).sum()),
            "b2_not_in_d28": int((b2 & ~d28).sum()),
            "d28_not_in_b2": int((d28 & ~b2).sum()),
            "strict_subset": bool((b2 & ~d28).sum() == 0),
        }

    receipt = {
        "schema": "gems-review-receipt-v1",
        "branch": "arena/afe07cea-gemsdoekarage1",
        "date": "2026-10-31",
        "kp1_candidate": kp_checks,
        "uniqueness_vs_downloaded_focus_files": comparisons,
        "b2_vs_d28_subset": subset,
        "encoding_census_docs_downloads": footprint_summary(),
        "evidence_labels": {
            "all_numbers": "MEASURED on the bytes named above; not a leaderboard score",
            "projection_0_2789": "PROJECTED in evidence/kp1_run_card.json; not checked here",
        },
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=2)
    print(json.dumps(receipt, indent=2)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
