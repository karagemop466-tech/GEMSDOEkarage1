#!/usr/bin/env python3
"""Measure HOLDOUT-DTI + uniqueness for the nine focus-site registry rasters.

Reads the pinned registry rasters in ``registry/``, converts each to a binary
dot mask on the competition grid, scores each with the shared hide-and-recover
evaluator (vendor/gems57/holdout.py: pooled DTI, alpha 0.2, beta 0.8, 300 m
triangular kernel, withheld catalogue segments), and measures pairwise
3-px dot overlap vs the other eight sites plus the 13GEMSDOE lattice.

All numbers here are MEASURED from restored raster bytes. The owner-reported
leaderboard values are recorded alongside with an explicit evidence label.
NOTHING here is an organizer-confirmed score or a leaderboard estimate: the
hide-and-recover holdout scores recovery of withheld *catalogue* segments, not
the organizer's hidden new-fault set.

Writes ``docs/data/nine_site_eval.json``.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "src"))

from gems57.grid import DATA_DIR, load_grid  # noqa: E402
from gems57.holdout import build_holdout, evaluate  # noqa: E402

REGISTRY = ROOT / "registry"
DATA = ROOT / ".cache" / "gems_data"
DOCS_DATA = ROOT / "docs" / "data"

SITES = (
    "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
    "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36",
)

USER_REPORTED = {
    "GEMSDOE24": 0.2477, "GEMSDOE25": 0.2600, "GEMSDOE27": 0.2449,
    "GEMSDOE28": 0.2710, "GEMSDOE30": 0.2600, "GEMSDOE31": 0.2708,
    "GEMSDOE32": 0.2778, "GEMSDOE33": 0.2632, "GEMSDOE36": 0.2750,
}

PREFERRED = {
    "GEMSDOE24": "GEMSDOE24_gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "GEMSDOE25": "GEMSDOE25_d28.tif",
    "GEMSDOE27": "GEMSDOE27_gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "GEMSDOE28": "GEMSDOE28_gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
    "GEMSDOE30": "GEMSDOE30_gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
    "GEMSDOE31": "GEMSDOE31_gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "GEMSDOE32": "GEMSDOE32_B2.tif",
    "GEMSDOE33": "GEMSDOE33_GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
    "GEMSDOE36": "GEMSDOE36_gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dots_of(arr: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    return np.isfinite(arr) & (arr > 0) & footprint


def collar(dots: np.ndarray, r: int) -> np.ndarray:
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    struct = (yy * yy + xx * xx) <= r * r
    return ndi.binary_dilation(dots, structure=struct)


def main() -> int:
    grid = load_grid(DATA_DIR)
    foot, cat = grid.footprint, grid.catalogue
    ctx = build_holdout(grid)
    print(f"Holdout context: {len(ctx.cells)} cells, "
          f"withheld truth px total={sum(c.n_truth for c in ctx.cells)}")

    rasters = {}
    dots = {}
    for site in SITES:
        path = REGISTRY / PREFERRED[site]
        if not path.is_file():
            print(f"MISSING raster for {site}: {path}", file=sys.stderr)
            return 1
        with rasterio.open(path) as src:
            a = src.read(1).astype(np.float64)
        d = dots_of(a, foot)
        rasters[site] = a
        dots[site] = d
        print(f"{site}: {int(d.sum())} dots, sha256={sha256_file(path)[:12]}")

    # Holdout scores
    holdout = {}
    for site in SITES:
        r = evaluate(dots[site], ctx)
        holdout[site] = r
        print(f"{site}: pooled HOLDOUT-DTI={r['pooled_dti']:.6f} "
              f"coverage={r['pooled_coverage']:.4f} dots={r['emitted_pixels']}")

    # Pairwise uniqueness vs other eight sites + lattice
    latt_path = DATA / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
    lattice = None
    if latt_path.is_file():
        with rasterio.open(latt_path) as src:
            lattice = dots_of(src.read(1), foot)
    struct = ndi.generate_binary_structure(2, 2)
    halo3 = lambda m: ndi.binary_dilation(m, iterations=3)

    per_site = {}
    for site in SITES:
        d = dots[site]
        n = int(d.sum())
        overlaps = {}
        for other in SITES:
            if other == site:
                continue
            fwd = float((d & halo3(dots[other])).sum() / n) if n else 0.0
            overlaps[other] = round(fwd, 6)
        worst_other = max(overlaps, key=overlaps.get)
        lat_frac = None
        if lattice is not None:
            lat_frac = round(float((d & halo3(lattice)).sum() / n), 6) if n else 0.0

        # holdout per-site summary
        h = holdout[site]
        per_site[site] = {
            "raster": PREFERRED[site],
            "sha256": sha256_file(REGISTRY / PREFERRED[site]),
            "dots": n,
            "on_catalogue": int((d & cat).sum()),
            "within_1px_of_catalogue": int((d & collar(cat, 1)).sum()),
            "within_3px_of_catalogue": int((d & collar(cat, 3)).sum()),
            "user_reported_score": USER_REPORTED[site],
            "score_label": "USER-REPORTED / UNVERIFIED (no organizer receipt)",
            "holdout_dti": round(h["pooled_dti"], 6),
            "holdout_coverage": round(h["pooled_coverage"], 6),
            "holdout_emitted_pixels": h["emitted_pixels"],
            "holdout_n_truth": h["pooled_n_truth"],
            "worst_peer_3px_overlap": worst_other,
            "worst_peer_3px_overlap_value": overlaps[worst_other],
            "pairwise_3px_overlap": overlaps,
            "unique_vs_other_eight_literal": bool(max(overlaps.values()) <= 0.70),
            "lattice_3px_overlap_diagnostic": lat_frac,
        }

    best_reported = max(SITES, key=lambda s: USER_REPORTED[s])
    best_holdout = max(SITES, key=lambda s: holdout[s]["pooled_dti"])

    out = {
        "schema": "karage1-nine-site-eval-v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evaluator": "vendor/gems57/holdout.py gems57-pooled-hide-v2",
        "evidence_policy": {
            "USER-REPORTED": "owner-supplied leaderboard value; no organizer submission receipt in this repo tied to the raster SHA-256",
            "MEASURED": "geometry and holdout DTI computed from restored raster bytes in this run",
            "HOLDOUT_DTI_NOT_SCORE": "hide-and-recover on withheld catalogue segments; not an organizer score and not a leaderboard estimate",
        },
        "grid": {"shape": [int(foot.shape[0]), int(foot.shape[1])],
                 "footprint_px": int(foot.sum()), "catalogue_px": int(cat.sum())},
        "best_reported_site": best_reported,
        "best_reported_score": USER_REPORTED[best_reported],
        "best_holdout_site": best_holdout,
        "best_holdout_dti": round(holdout[best_holdout]["pooled_dti"], 6),
        "sites": per_site,
    }
    DOCS_DATA.mkdir(parents=True, exist_ok=True)
    out_path = DOCS_DATA / "nine_site_eval.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"\nWrote {out_path}")
    print(f"Best reported: {best_reported} {USER_REPORTED[best_reported]} | "
          f"Best holdout DTI: {best_holdout} {holdout[best_holdout]['pooled_dti']:.6f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
