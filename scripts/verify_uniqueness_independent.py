#!/usr/bin/env python3
"""Independent uniqueness recheck of one candidate against the nine focus rasters.

Reads only the GeoTIFFs. Reports, per registry raster:
  * Spearman rank correlation on a fixed random sample of pixels inside the
    candidate footprint (sampled, so an estimate, not a full-raster value);
  * share of candidate dots within 3 px (Euclidean) of a registry dot;
  * share of registry dots within 3 px of a candidate dot.
Dots are cells with value > 0. NaN is treated as "no dot".
Usage: python scripts/verify_uniqueness_independent.py CANDIDATE.tif --out evidence/x.json
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage, stats

SAMPLE = 2_000_000
SEED = 20261031


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(p: Path) -> np.ndarray:
    with rasterio.open(p) as s:
        return s.read(1).astype(np.float64)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("candidate", type=Path)
    ap.add_argument("--registry-glob", default="registry/*.tif")
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    cand = load(a.candidate)
    cand_dots = np.nan_to_num(cand, nan=0.0) > 0
    rng = np.random.default_rng(SEED)
    finite_idx = np.flatnonzero(np.isfinite(cand).ravel())
    pick = rng.choice(finite_idx, size=min(SAMPLE, finite_idx.size), replace=False)
    cv = cand.ravel()[pick]
    # distance from every cell to nearest candidate dot (Euclidean, px)
    d_cand = ndimage.distance_transform_edt(~cand_dots)
    n_cand = int(cand_dots.sum())

    rows = []
    for reg_path in sorted(glob.glob(a.registry_glob)):
        p = Path(reg_path)
        reg = load(p)
        if reg.shape != cand.shape:
            rows.append({"file": p.name, "error": "shape mismatch"})
            continue
        rv = reg.ravel()[pick]
        ok = np.isfinite(rv)
        rho = stats.spearmanr(cv[ok], rv[ok]).statistic
        reg_dots = np.nan_to_num(reg, nan=0.0) > 0
        d_reg = ndimage.distance_transform_edt(~reg_dots)
        cand_near = float((d_reg[cand_dots] <= 3.0).mean()) if n_cand else float("nan")
        reg_near = float((d_cand[reg_dots] <= 3.0).mean()) if reg_dots.sum() else float("nan")
        rows.append({
            "file": p.name,
            "sha256": sha256(p),
            "spearman_sampled": round(float(rho), 6),
            "candidate_dots_within_3px_of_registry": round(cand_near, 6),
            "registry_dots_within_3px_of_candidate": round(reg_near, 6),
            "registry_dot_count": int(reg_dots.sum()),
        })

    summary = {
        "candidate": str(a.candidate),
        "candidate_sha256": sha256(a.candidate),
        "candidate_dot_count": n_cand,
        "sample_pixels": int(pick.size),
        "sample_seed": SEED,
        "max_abs_spearman": max(abs(r["spearman_sampled"]) for r in rows if "spearman_sampled" in r),
        "max_candidate_dots_within_3px": max(r["candidate_dots_within_3px_of_registry"] for r in rows if "error" not in r),
        "thresholds": {"spearman": 0.90, "dot_overlap_3px": 0.70},
        "rows": rows,
    }
    summary["passes_literal_gate"] = bool(
        summary["max_abs_spearman"] <= 0.90 and summary["max_candidate_dots_within_3px"] <= 0.70)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("max_abs_spearman", "max_candidate_dots_within_3px", "passes_literal_gate")}, indent=2))


if __name__ == "__main__":
    main()
