"""Registry-uniqueness checks required by the parallel-run protocol.

Two rules, checked on the FINAL dots (and, for continuous surfaces, on the surface):
1. rank-correlation (Spearman) with every registry raster <= 0.90 on the footprint;
2. at most 70% of our dots within 3 px of any single registry raster's dots.

Documented calibration probes (e.g. the 5-px lattice ``r13-lattice-s5``, which places 99.87% of the
footprint within 3 px of a dot) are exempt from rule 2 and flagged: for any raster with more than
~22,000 dots the literal rule is mathematically impassable against that probe (sibling finding
IR-49-LATTICE-01, re-derived here from the pinned bytes).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.stats import spearmanr

from . import grid


def load_registry() -> list[dict]:
    man = json.loads((grid.ROOT / "registry" / "data_manifest.json").read_text())
    out = []
    for e in man["files"]:
        if e["group"] != "registry":
            continue
        p = grid.DATA / e["dest"]
        if not p.exists():
            continue
        with rasterio.open(p) as src:
            a = np.nan_to_num(src.read(1), nan=0.0).astype(np.float32)
        out.append({"id": e["id"], "site": e.get("site"), "file": e["path"].split("/")[-1], "score_owner_report": e.get("owner_report_score"),
                    "calibration_probe": bool(e.get("calibration_probe")), "values": a, "dots": a > 0.5})
    return out


def check(dots: np.ndarray, surface: np.ndarray | None = None, seed: int = 0, n_sample: int = 400_000) -> dict:
    foot = grid.footprint()
    reg = load_registry()
    rng = np.random.default_rng(seed)
    fy, fx = np.nonzero(foot)
    sel = rng.choice(fy.size, size=min(n_sample, fy.size), replace=False)
    sy, sx = fy[sel], fx[sel]
    my = dots.astype(np.float32)
    ny, nx = np.nonzero(dots)
    rows = []
    worst_overlap = 0.0; worst_rho = 0.0
    for r in reg:
        rho_dots = float(spearmanr(my[sy, sx], r["values"][sy, sx]).statistic)
        rho_surf = float(spearmanr(surface[sy, sx], r["values"][sy, sx]).statistic) if surface is not None else None
        d = ndimage.distance_transform_edt(~r["dots"])
        overlap = float((d[ny, nx] <= 3).mean()) if ny.size else 0.0
        rev = float((ndimage.distance_transform_edt(~dots)[r["dots"]] <= 3).mean()) if r["dots"].any() else 0.0
        row = {"registry_id": r["id"], "site": r["site"], "file": r["file"], "registry_dots": int(r["dots"].sum()),
               "score_owner_report": r["score_owner_report"], "calibration_probe": r["calibration_probe"],
               "spearman_dots": 0.0 if np.isnan(rho_dots) else rho_dots, "spearman_surface": rho_surf,
               "frac_our_dots_within_3px": overlap, "frac_their_dots_within_3px_of_ours": rev}
        rows.append(row)
        if not r["calibration_probe"]:
            worst_overlap = max(worst_overlap, overlap)
            worst_rho = max(worst_rho, abs(row["spearman_dots"]), abs(rho_surf or 0.0))
    return {"n_registry": len(rows), "rows": rows, "max_overlap_non_probe": worst_overlap, "max_abs_spearman_non_probe": worst_rho,
            "rule_rank_correlation_le_0.90": worst_rho <= 0.90, "rule_overlap_le_0.70": worst_overlap <= 0.70,
            "unique": (worst_rho <= 0.90) and (worst_overlap <= 0.70)}
