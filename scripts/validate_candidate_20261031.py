#!/usr/bin/env python3
"""Format validation and literal duplicate-gate check for one candidate GeoTIFF.

Format checks follow the official submission-format text (DrivenData competition 306,
page 967, fetched 31 Oct 2026): single-band float32 GeoTIFF, EPSG:32611, 100 m grid,
same bounds/shape/transform as the training data, values in [0, 1], outside-bounds
null or NaN (zero is also accepted by the top-scored B2 file, see the review).

Duplicate gate (registry_roles.json, role "discrete_submission"): a candidate is
duplicate/stop if forward 3-px overlap > 0.70 (fraction of ITS dots within 3 px of a
registry raster's dots) OR footprint Spearman > 0.90. Dots = value > 0 in the footprint.

Writes evidence/candidate_validation_<tag>_20261031.json. Labels: LOCAL MEASUREMENT.
Usage: python scripts/validate_candidate_20261031.py <candidate.tif> <tag>
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
DATA = ROOT / "data"
EVID = ROOT / "evidence"
GATE_FWD, GATE_RHO = 0.70, 0.90


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 1
    cand_path = Path(argv[1]).resolve()
    tag = argv[2]
    with rasterio.open(DATA / "sample_submission.tif") as ref:
        ref_crs = ref.crs.to_string()
        ref_shape = (ref.height, ref.width)
        ref_tr = tuple(ref.transform)[:6]
        footprint = np.isfinite(ref.read(1))
    with rasterio.open(DATA / "labels.tif") as ds:
        catalogue = ds.read(1) == 1
    cat_edt = ndi.distance_transform_edt(~catalogue)

    with rasterio.open(cand_path) as ds:
        a = ds.read(1)
        fmt = {
            "driver": ds.driver, "band_count": ds.count, "dtype": ds.dtypes[0],
            "crs": ds.crs.to_string(), "shape": [ds.height, ds.width],
            "transform": list(tuple(ds.transform)[:6]), "nodata": ds.nodata,
        }
    checks = {
        "single_band": fmt["band_count"] == 1,
        "float32": fmt["dtype"] == "float32",
        "crs_EPSG_32611": fmt["crs"] == ref_crs == "EPSG:32611",
        "shape_matches_training": tuple(fmt["shape"]) == ref_shape,
        "transform_matches_training": bool(np.allclose(fmt["transform"], ref_tr, atol=1e-6)),
        "no_nan_anywhere": bool(np.isfinite(a).all()),
        "values_in_unit_interval": bool(a.min() >= 0.0 and a.max() <= 1.0),
        "zero_outside_footprint": bool((a[~footprint] == 0).all()),
        "no_nan_inside_footprint": bool(np.isfinite(a[footprint]).all()),
    }
    vals_fp = a[footprint].astype(np.float64)
    dot = (a > 0) & footprint
    n_dots = int(dot.sum())
    checks["dots_present"] = n_dots > 0
    rank_c = np.zeros(footprint.shape, np.float32)
    rank_c[footprint] = rankdata(vals_fp, method="average").astype(np.float32)
    rc = rank_c[footprint]
    dot_edt = ndi.distance_transform_edt(~dot) if n_dots else np.full(footprint.shape, np.inf)

    rows = []
    paths = sorted(glob.glob(str(ROOT / "registry" / "GEMSDOE*.tif"))) + \
        sorted(glob.glob(str(DATA / "scored" / "*.tif")))
    for p in paths:
        p = Path(p)
        with rasterio.open(p) as ds:
            b = ds.read(1)
        fin = np.isfinite(b)
        bv = np.where(fin, b, 0.0).astype(np.float32)
        bdot = (bv > 0) & footprint
        rb = np.zeros(footprint.shape, np.float32)
        rb[footprint] = rankdata(bv[footprint], method="average").astype(np.float32)
        rho = float(np.corrcoef(rc, rb[footprint])[0, 1]) if np.std(rb[footprint]) > 0 else float("nan")
        bd_edt = ndi.distance_transform_edt(~bdot) if bdot.any() else np.full(footprint.shape, np.inf)
        fwd = float((bd_edt[dot] <= 3.0).mean()) if n_dots else float("nan")
        rev = float((dot_edt[bdot] <= 3.0).mean()) if bdot.any() else float("nan")
        inter = int((dot & bdot).sum())
        union = int((dot | bdot).sum())
        dup = (fwd > GATE_FWD) or (rho > GATE_RHO)
        rows.append({
            "registry_file": str(p.relative_to(ROOT)), "sha256": sha256(p),
            "byte_identical": sha256(p) == sha256(cand_path),
            "dots_registry": int(bdot.sum()), "dots_candidate": n_dots,
            "pixel_identical_dot_sets": bool(inter == n_dots == int(bdot.sum())),
            "forward_3px_candidate_to_registry": fwd,
            "reverse_3px_registry_to_candidate": rev,
            "spearman_footprint": rho,
            "dot_jaccard": (inter / union) if union else float("nan"),
            "literal_gate_duplicate": bool(dup),
        })
    lattice = [r for r in rows if "13gems" in r["registry_file"]]
    doc = {
        "schema": "karage1-candidate-validation-v1", "date_utc": "2026-10-31", "tag": tag,
        "candidate": str(cand_path.relative_to(ROOT)) if cand_path.is_relative_to(ROOT) else str(cand_path),
        "candidate_sha256": sha256(cand_path), "candidate_bytes": cand_path.stat().st_size,
        "format": fmt, "format_checks": checks,
        "format_pass": all(checks.values()),
        "dots_gt0_in_footprint": n_dots,
        "catalogue_pixels_on_candidate_dots": int((dot & catalogue).sum()),
        "dots_within_2px_catalogue": int((dot & (cat_edt <= 2.0)).sum()),
        "gate": {"forward_threshold": GATE_FWD, "spearman_threshold": GATE_RHO},
        "registry_compared": len(rows),
        "duplicates_vs_registry_literal": [r["registry_file"] for r in rows if r["literal_gate_duplicate"]],
        "max_forward_3px": max(r["forward_3px_candidate_to_registry"] for r in rows),
        "max_spearman": max(r["spearman_footprint"] for r in rows if r["spearman_footprint"] == r["spearman_footprint"]),
        "lattice_13gems_forward_3px": lattice[0]["forward_3px_candidate_to_registry"] if lattice else None,
        "rows": rows,
        "label": "LOCAL MEASUREMENT on SHA-pinned mirror bytes; not organizer-authenticated; not a leaderboard score",
    }
    out = EVID / f"candidate_validation_{tag}_20261031.json"
    out.write_text(json.dumps(_strict(doc), indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: doc[k] for k in ("format_pass", "dots_gt0_in_footprint", "max_forward_3px",
                                           "max_spearman", "lattice_13gems_forward_3px",
                                           "duplicates_vs_registry_literal")}, indent=1))
    print("format_checks", checks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
