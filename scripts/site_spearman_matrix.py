#!/usr/bin/env python3
"""Pairwise Spearman among the nine focus best files and the H-TILTGRAV candidate.

Uses the vendor's surface_rho (spearman over the full footprint, plus dot-union
rank correlation and dot Jaccard) on raw values inside the footprint. Duplicate
rule (README / registry): rho > 0.90 OR >70% of dots within 3 px.
Writes evidence/site_spearman_matrix_20261029.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT))
from gems57.uniqueness import RHO_LIMIT, OVERLAP_LIMIT, surface_rho  # noqa: E402
from scripts.site_overlap_matrix import SITES, DATA, CANDIDATE  # noqa: E402

OUT = ROOT / "evidence" / "site_spearman_matrix_20261029.json"


def _strict(obj):
    """Replace NaN/inf with null so the JSON is strict (RFC 8259)."""
    import math
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    if isinstance(obj, dict):
        return {k: _strict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_strict(v) for v in obj]
    return obj


def load_values(path: Path, fp: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
    return a


def main() -> None:
    with rasterio.open(DATA / "sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    items = [(site, f"registry/{fname}", DATA / "registry" / fname) for site, _, _, fname in SITES]
    items.append(("NEW candidate (H-TILTGRAV)", CANDIDATE, ROOT / CANDIDATE))
    vals = [load_values(src, fp) for _, _, src in items]
    shas = [hashlib.sha256(src.read_bytes()).hexdigest() for _, _, src in items]
    n = len(items)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            r = surface_rho(vals[i], vals[j], fp)
            dup_rho = r["spearman_full_footprint"] is not None and r["spearman_full_footprint"] > RHO_LIMIT
            pairs.append({
                "a": items[i][0], "b": items[j][0],
                "spearman_full_footprint": r["spearman_full_footprint"],
                "spearman_on_dot_union": r["spearman_on_dot_union"],
                "n_dot_union": r["n_dot_union"],
                "jaccard_dot_sets": r["jaccard_dot_sets"],
                "rho_duplicate": bool(dup_rho),
            })
            print(items[i][0], items[j][0], r["spearman_full_footprint"], flush=True)
    out = {
        "schema": "pairwise-spearman/v1",
        "date": "2026-10-29",
        "measure": "vendor gems57.uniqueness.surface_rho: spearman over footprint (sample_submission finite mask), raw values",
        "rule": f"duplicate if spearman_full_footprint > {RHO_LIMIT} or dot forward overlap > {OVERLAP_LIMIT} (see site_overlap_matrix)",
        "footprint_pixels": int(fp.sum()),
        "items": [{"label": it[0], "path": it[1], "sha256": s} for it, s in zip(items, shas)],
        "pairs": pairs,
        "max_abs_spearman": max(abs(p["spearman_full_footprint"]) for p in pairs),
        "any_rho_duplicate": any(p["rho_duplicate"] for p in pairs),
    }
    OUT.write_text(json.dumps(_strict(out), indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("wrote", OUT, "max|rho|", out["max_abs_spearman"], "any_dup", out["any_rho_duplicate"])


if __name__ == "__main__":
    main()
