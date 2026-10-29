#!/usr/bin/env python3
"""Reproducible grid + overlap check for two registry GeoTIFFs (session arena/23ef16f9).

Checks, for each raster: EPSG:32611, shape, 100 m transform, float32, no NaN, values in [0,1].
Pairwise: share of dots within 3 px of the other raster's dots, and subset counts.
Also computes the largest dot count for which the literal 70% / 3-px gate is satisfiable
against the recorded 13GEMSDOE calibration lattice (witness numbers from registry/registry_roles.json).
Writes evidence/registry_pair_check_23ef16f9.json. Needs numpy, scipy, rasterio (requirements.txt).
"""
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
RASTERS = {
    "GEMSDOE25_d28": "registry/GEMSDOE25_d28.tif",
    "GEMSDOE32_B2": "registry/GEMSDOE32_B2.tif",
}
GRID = dict(crs="EPSG:32611", shape=[3730, 3292], res=[100.0, 100.0],
            transform=[100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0])


def load(path):
    with rasterio.open(ROOT / path) as ds:
        a = ds.read(1).astype("float64")
        info = dict(
            sha256=hashlib.sha256((ROOT / path).read_bytes()).hexdigest(),
            crs=str(ds.crs), shape=[ds.height, ds.width], res=list(ds.res),
            transform=list(ds.transform)[:6], dtype=ds.dtypes[0], count=ds.count,
            nodata=ds.nodata,
        )
    fin = np.isfinite(a)
    info.update(nonfinite=int((~fin).sum()),
                min=float(a[fin].min()), max=float(a[fin].max()),
                outside_0_1=int(((a < 0) | (a > 1))[fin].sum()),
                positive_px=int(((a > 0) & fin).sum()))
    info["grid_matches_template"] = (
        info["crs"] == GRID["crs"] and info["shape"] == GRID["shape"]
        and info["res"] == GRID["res"] and info["transform"] == GRID["transform"]
    )
    return info, (a > 0) & fin


def within(src, tgt, r=3):
    d = ndimage.distance_transform_edt(~tgt)
    return float((d[src] <= r).mean())


def main():
    infos, pos = {}, {}
    for name, p in RASTERS.items():
        infos[name], pos[name] = load(p)
    a, b = pos["GEMSDOE25_d28"], pos["GEMSDOE32_B2"]
    pair = dict(
        b_dots_within_3px_of_a=round(within(b, a), 6),
        a_dots_within_3px_of_b=round(within(a, b), 6),
        b_subset_of_a=bool(np.all(a[b])),
        a_minus_b=int((a & ~b).sum()), b_minus_a=int((b & ~a).sum()),
        both=int((a & b).sum()),
    )
    # Witness numbers recorded in registry/registry_roles.json (13GEMSDOE calibration lattice)
    beyond_3px = 6649
    gate = 0.70
    # Share within 3 px >= 1 - beyond/N. Gate needs share <= 0.70 => beyond >= 0.30 N.
    max_n_satisfiable = int(beyond_3px / (1 - gate))
    out = dict(
        schema="karage1-registry-pair-check-v1", session="arena/23ef16f9",
        template_grid=GRID, rasters=infos, pair=pair,
        lattice_gate=dict(
            footprint_beyond_3px_of_lattice=beyond_3px, gate_share=gate,
            max_dots_satisfiable=max_n_satisfiable,
            note="Above this many dots every raster exceeds 70% within-3px overlap with the witness, "
                 "whatever the placement. The gate is a count-driven saturation, not a uniqueness test.",
        ),
        submit_authorized=False,
    )
    (ROOT / "evidence" / "registry_pair_check_23ef16f9.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
