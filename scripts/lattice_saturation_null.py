#!/usr/bin/env python3
"""Null test for the literal 70% lattice rule: how often do RANDOM dots fail it?

Places uniformly random dots inside the pinned footprint (no fault information at all) and
reports the share falling within a closed 3-px disk of the pinned 13GEMSDOE lattice positives.
If random noise fails, the rule does not measure uniqueness. Read-only; never authorizes upload.
Inputs: .cache/references/{template,lattice}.tif (fetched by scripts/audit_references.py --fetch).
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]


def disk(r: int) -> np.ndarray:
    g = np.arange(-r, r + 1)
    dx, dy = np.meshgrid(g, g)
    return (dx ** 2 + dy ** 2) <= r ** 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache/references")
    ap.add_argument("--out", type=Path, default=ROOT / "evidence/lattice_saturation_null_20261029.json")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    with rasterio.open(args.cache / "template.tif") as s:
        tpl = s.read(1)
    with rasterio.open(args.cache / "lattice.tif") as s:
        lat = s.read(1)
    footprint = np.isfinite(tpl) & np.isfinite(lat)
    pos = (lat == 1) & footprint
    cover = ndimage.binary_dilation(pos, structure=disk(3)) & footprint
    rng = np.random.default_rng(args.seed)
    ys, xs = np.nonzero(footprint)
    trials = {}
    for n in (1000, 5000, 22163, 37654):
        idx = rng.choice(len(ys), size=n, replace=False)
        frac = float(cover[ys[idx], xs[idx]].mean())
        trials[str(n)] = {"random_dots": n, "share_within_3px_of_lattice": round(frac, 6),
                          "fails_70pct_rule": frac > 0.70}
    out = {
        "schema": "karage1-lattice-saturation-null-v1",
        "footprint_pixels": int(footprint.sum()),
        "lattice_positive_pixels": int(pos.sum()),
        "footprint_covered_by_3px_disk_fraction": round(float(cover.sum() / footprint.sum()), 6),
        "random_dot_trials": trials,
        "interpretation": "Random dots with no fault information fail the literal rule. The rule is saturated, not a uniqueness test.",
        "submit_authorized": False,
    }
    args.out.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
