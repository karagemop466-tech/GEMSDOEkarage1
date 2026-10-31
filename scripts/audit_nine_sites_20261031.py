#!/usr/bin/env python3
"""Reproducible audit of the nine focus-site rasters and the pinned scored rasters.

Computes, from bytes on disk only (no network, no organizer data):
  * file SHA-256, dtype, CRS, shape, transform, NaN count, value range;
  * dot count (cells with value > 0 inside the sample footprint);
  * overlap with the INGENIOUS/USGS catalogue labels (data/labels.tif == 1);
  * pairwise: byte equality, pixel equality, Jaccard of dot sets,
    forward 3-px overlap (fraction of A's dots within 3 px of any B dot),
    and footprint rank correlation (Spearman, the registry's definition).

Outputs evidence/nine_site_audit_20261031.json and prints a compact table.
Labels: every number here is a LOCAL MEASUREMENT on mirror bytes. None is a
leaderboard score. Scores in the prompt are USER-REPORTED and are not read here.
"""
from __future__ import annotations

import glob
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata


def _strict(o):
    """Replace NaN/Inf with None so every artifact is strict JSON."""
    if isinstance(o, float) and not math.isfinite(o):
        return None
    if isinstance(o, dict):
        return {k: _strict(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [_strict(v) for v in o]
    return o

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "nine_site_audit_20261031.json"

FOCUS_KEYS = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
              "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_inventory() -> list[dict]:
    rows = []
    for p in sorted(glob.glob(str(ROOT / "registry" / "GEMSDOE*.tif"))):
        key = next((k for k in FOCUS_KEYS if os.path.basename(p).startswith(k)), None)
        rows.append({"path": Path(p), "group": "focus", "site": key or "other"})
    for p in sorted(glob.glob(str(ROOT / "data" / "scored" / "*.tif"))):
        rows.append({"path": Path(p), "group": "scored", "site": "scored"})
    return rows


def main() -> int:
    labels_path = ROOT / "data" / "labels.tif"
    sample_path = ROOT / "data" / "sample_submission.tif"
    feat_path = ROOT / "data" / "training_features.tif"
    for pth in (labels_path, sample_path, feat_path):
        if not pth.exists():
            print(f"MISSING {pth}; run scripts/restore_karage1_data.py --group core", file=sys.stderr)
            return 2

    with rasterio.open(sample_path) as ds:
        ref_shape, ref_crs, ref_tr = (ds.height, ds.width), ds.crs.to_string(), tuple(ds.transform)[:6]
        sample = ds.read(1)
    footprint = np.isfinite(sample)  # sample submission encodes outside-footprint as NaN
    with rasterio.open(feat_path) as ds:
        feat_valid = ds.read(1) > -1e38
    with rasterio.open(labels_path) as ds:
        catalogue = ds.read(1) == 1

    cat_edt = ndi.distance_transform_edt(~catalogue)
    entries = []
    dots = {}
    ranks = {}
    edts = {}
    for row in load_inventory():
        path = row["path"]
        with rasterio.open(path) as ds:
            a = ds.read(1)
            meta = {"crs": ds.crs.to_string(), "shape": [ds.height, ds.width],
                    "transform": list(tuple(ds.transform)[:6]), "dtype": ds.dtypes[0],
                    "nodata": ds.nodata}
        fin = np.isfinite(a)
        val = np.where(fin, a, 0.0).astype(np.float32)
        dot = (val > 0) & footprint
        vals_in_fp = val[footprint]
        name = path.name
        key = f"{row['group']}/{name}"
        dots[key] = dot
        rk = np.zeros(footprint.shape, dtype=np.float32)
        rk[footprint] = rankdata(vals_in_fp, method="average").astype(np.float32)
        ranks[key] = rk[footprint]
        edts[key] = ndi.distance_transform_edt(~dot) if dot.any() else np.full(footprint.shape, np.inf)
        n = int(dot.sum())
        entries.append({
            "key": key, "site": row["site"], "group": row["group"], "file": name,
            "sha256": sha256(path), "bytes": path.stat().st_size, **meta,
            "shape_matches_sample": meta["shape"] == list(ref_shape),
            "crs_matches_sample": meta["crs"] == ref_crs,
            "transform_matches_sample": np.allclose(meta["transform"], ref_tr, rtol=0, atol=1e-6),
            "nan_count": int((~fin).sum()),
            "min": float(np.nanmin(a)), "max": float(np.nanmax(a)),
            "in_unit_interval": bool(np.nanmin(a) >= 0 and np.nanmax(a) <= 1),
            "dots_gt0_in_footprint": n,
            "dots_on_catalogue": int((dot & catalogue).sum()),
            "dots_within_2px_catalogue": int((dot & (cat_edt <= 2.0)).sum()),
            "dots_within_3px_catalogue": int((dot & (cat_edt <= 3.0)).sum()),
            "distinct_values_sample": int(np.unique(vals_in_fp[:2_000_000]).size),
        })

    keys = [e["key"] for e in entries]
    sha = {e["key"]: e["sha256"] for e in entries}
    pairs = []
    for i, ka in enumerate(keys):
        for kb in keys[i + 1:]:
            A, B = dots[ka], dots[kb]
            na, nb = int(A.sum()), int(B.sum())
            inter = int((A & B).sum())
            union = na + nb - inter
            fwd = float((edts[kb][A] <= 3.0).mean()) if na else float("nan")
            rev = float((edts[ka][B] <= 3.0).mean()) if nb else float("nan")
            ra, rb = ranks[ka], ranks[kb]
            if np.std(ra) == 0 or np.std(rb) == 0:
                rho = float("nan")
            else:
                rho = float(np.corrcoef(ra, rb)[0, 1])
            pairs.append({
                "a": ka, "b": kb, "byte_identical": sha[ka] == sha[kb],
                "dots_a": na, "dots_b": nb, "dot_jaccard": (inter / union) if union else float("nan"),
                "subset_a_in_b": bool(na and inter == na), "subset_b_in_a": bool(nb and inter == nb),
                "forward_3px_a_to_b": fwd, "reverse_3px_b_to_a": rev,
                "spearman_footprint": rho,
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "schema": "karage1-nine-site-audit-v1", "date_utc": "2026-10-31",
        "label": "LOCAL MEASUREMENT on SHA-pinned mirror bytes; not organizer-authenticated; not a leaderboard score",
        "sample_footprint_cells": int(footprint.sum()),
        "feature_valid_cells": int(feat_valid.sum()),
        "catalogue_cells": int(catalogue.sum()),
        "reference_grid": {"shape": list(ref_shape), "crs": ref_crs, "transform": list(ref_tr)},
        "entries": entries, "pairs": pairs,
    }
    OUT.write_text(json.dumps(_strict(doc), indent=2, allow_nan=False) + "\n")
    print(f"footprint(sample NaN mask)={footprint.sum()} feature-valid={feat_valid.sum()} "
          f"catalogue={catalogue.sum()}")
    print(f"wrote {OUT.relative_to(ROOT)} ({len(entries)} rasters, {len(pairs)} pairs)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
