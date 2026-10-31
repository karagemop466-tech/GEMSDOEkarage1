#!/usr/bin/env python3
"""Reproduce the registry-overlap and format checks used in knowledge/review-arena-d454d34a-20261031.md.

Reads only local files (registry/*.tif and the kp1 candidate in docs/downloads/).
Writes evidence/registry_overlap_matrix_20261031.json. Does not generate or edit any raster.

Definitions (binary dot rasters: value == 1 is a dot; NaN is treated as 0):
* share(i -> j) = fraction of file i's dots within 3 px (Euclidean) of some dot of file j.
* rho           = Pearson correlation on the full footprint. For binary variables this equals
                  Spearman, because the rank transform of a two-valued variable is affine.
"""
from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif"
EXPECTED_SHA256 = "30a5fc28ff060ad38681d9b721024aea5aec3b070f407537dd28354efbe0ff0d"
OUT = ROOT / "evidence/registry_overlap_matrix_20261031.json"
RADIUS_PX = 3.0


def load(path: Path):
    with rasterio.open(path) as s:
        arr = s.read(1).astype(np.float64)
        meta = dict(crs=s.crs.to_string(), shape=list(s.shape),
                    transform=list(s.transform)[:6], dtype=s.dtypes[0])
    return arr, meta


def main() -> None:
    cand, cmeta = load(CANDIDATE)
    sha = hashlib.sha256(CANDIDATE.read_bytes()).hexdigest()
    fmt = dict(
        sha256=sha, sha256_matches_card=(sha == EXPECTED_SHA256),
        dtype=cmeta["dtype"], crs=cmeta["crs"], shape=cmeta["shape"], transform=cmeta["transform"],
        nan_count=int(np.isnan(cand).sum()), min=float(np.nanmin(cand)), max=float(np.nanmax(cand)),
        distinct_values=[float(v) for v in np.unique(cand[np.isfinite(cand)])],
        dot_count=int((cand == 1).sum()),
    )

    names, rasters, metas = [], [], []
    for p in sorted(glob.glob(str(ROOT / "registry/*.tif"))):
        a, m = load(Path(p))
        names.append(Path(p).name.split("_")[0].replace(".tif", ""))
        rasters.append(a)
        metas.append(m)
    names.append("KP1-candidate")
    rasters.append(cand)
    metas.append(cmeta)

    grid_match = {n: bool(m["transform"] == cmeta["transform"] and m["crs"] == cmeta["crs"]
                          and m["shape"] == cmeta["shape"])
                  for n, m in zip(names, metas)}

    dots = [np.nan_to_num(a, nan=0.0) == 1 for a in rasters]
    dist = [ndimage.distance_transform_edt(~d) for d in dots]
    k = len(dots)
    share = np.zeros((k, k))
    for i in range(k):
        for j in range(k):
            share[i, j] = 1.0 if i == j else float((dist[j][dots[i]] <= RADIUS_PX).mean())

    rho = {}
    flat_c = np.nan_to_num(cand, nan=0.0).ravel()
    for n, a in zip(names[:-1], rasters[:-1]):
        fin = np.isfinite(a)
        rho[n] = float(np.corrcoef(cand[fin], a[fin])[0, 1])

    focus = list(range(k - 1))
    result = dict(
        schema="registry-overlap-matrix-v1",
        date="2026-10-31",
        radius_px=RADIUS_PX,
        names=names,
        dot_counts=[int(d.sum()) for d in dots],
        share_row_within_3px_of_col=share.round(6).tolist(),
        kp1_max_share_into_focus=float(max(share[k - 1, j] for j in focus)),
        focus_max_share_into_kp1=float(max(share[j, k - 1] for j in focus)),
        focus_pairwise_max_share=float(max(share[i, j] for i in focus for j in focus if i != j)),
        focus_each_max_share_into_other_focus={names[i]: float(max(share[i, j] for j in focus if j != i))
                                               for i in focus},
        rho_candidate_vs_focus=rho,
        rho_max_abs=float(max(abs(v) for v in rho.values())),
        grid_matches_candidate=grid_match,
        format=fmt,
        note=("Overlap uses Euclidean distance <= 3 px. The literal gate is 70 % (registry rule). "
              "rho limit 0.90. Official template is not in this checkout, so the sample-grid match "
              "is not checked here."),
    )
    OUT.write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k2: result[k2] for k2 in ("kp1_max_share_into_focus", "focus_max_share_into_kp1",
                                               "focus_pairwise_max_share", "rho_max_abs")}, indent=1))
    print("sha256 matches card:", fmt["sha256_matches_card"], " dots:", fmt["dot_count"],
          " nan:", fmt["nan_count"], " grid match all:", all(grid_match.values()))


if __name__ == "__main__":
    main()
