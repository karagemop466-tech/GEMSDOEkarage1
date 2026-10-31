#!/usr/bin/env python3
"""Re-measure the nine focus-site rasters committed under registry/ (session arena/946f7668 successor, 2026-10-31).

Everything here is computed from the committed bytes; nothing is downloaded and no
score is produced. Uses the shared primitive ``gems57.uniqueness.dot_overlap``
(forward share of row dots within 3 px of column dots). Writes
evidence/nine_site_verification_20261031.json.

Scores are the user-supplied ledger values (USER-REPORTED / UNVERIFIED).
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
from gems57.uniqueness import dot_overlap  # noqa: E402

OUT = ROOT / "evidence" / "nine_site_verification_20261031.json"

# site, committed registry file, ledger score (USER-REPORTED / UNVERIFIED)
SITES = [
    ("GEMSDOE24", "GEMSDOE24_gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif", 0.2477),
    ("GEMSDOE25", "GEMSDOE25_d28.tif", 0.2600),
    ("GEMSDOE27", "GEMSDOE27_gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif", 0.2449),
    ("GEMSDOE28", "GEMSDOE28_gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif", 0.2710),
    ("GEMSDOE30", "GEMSDOE30_gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif", 0.2600),
    ("GEMSDOE31", "GEMSDOE31_gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif", 0.2708),
    ("GEMSDOE32", "GEMSDOE32_B2.tif", 0.2778),
    ("GEMSDOE33", "GEMSDOE33_GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif", 0.2632),
    ("GEMSDOE36", "GEMSDOE36_gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif", 0.2750),
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    rows, arrays, grids = [], {}, {}
    for site, fname, score in SITES:
        p = ROOT / "registry" / fname
        with rasterio.open(p) as ds:
            a = ds.read(1).astype(np.float64)
            grids[site] = (str(ds.crs), tuple(ds.shape), tuple(ds.transform)[:6])
        finite = np.isfinite(a)
        arrays[site] = np.where(finite, a, 0.0).astype(np.float32)
        rows.append({
            "site": site,
            "file": f"registry/{fname}",
            "sha256": sha256(p),
            "ledger_score_user_reported": score,
            "positives_gt0": int((finite & (a > 0)).sum()),
            "positives_gt_0p5": int((finite & (a > 0.5)).sum()),
            "fractional_cells_0_lt_v_lt_1": int((finite & (a > 0) & (a < 1)).sum()),
            "nan_cells": int((~finite).sum()),
            "finite_cells": int(finite.sum()),
        })

    distinct_grids = {g for g in grids.values()}
    grid_ok = len(distinct_grids) == 1
    grid = next(iter(distinct_grids)) if grid_ok else None

    names = [s for s, _, _ in SITES]
    matrix = {a: {} for a in names}
    for a_name in names:
        for b_name in names:
            if a_name == b_name:
                matrix[a_name][b_name] = 1.0
            else:
                matrix[a_name][b_name] = round(dot_overlap(arrays[a_name] > 0, arrays[b_name] > 0), 6)

    subsets = {}
    for a_name in names:
        for b_name in names:
            if a_name == b_name:
                continue
            A = arrays[a_name] > 0
            B = arrays[b_name] > 0
            n_a = int(A.sum())
            inter = int((A & B).sum())
            if inter == 0:
                continue
            subsets[f"{a_name}_in_{b_name}"] = {
                "a_positives": n_a,
                "shared_exact_cells": inter,
                "fraction_of_a_exactly_in_b": round(inter / n_a, 6) if n_a else None,
            }

    b2 = arrays["GEMSDOE32"] > 0
    p25 = arrays["GEMSDOE25"] > 0
    removed = int((p25 & ~b2).sum())
    added = int((b2 & ~p25).sum())
    result = {
        "schema": "nine-site-verification-v1",
        "session_note": "arena/946f7668 successor, 2026-10-31; committed registry bytes only; no score estimated",
        "grid_identical_across_nine": grid_ok,
        "grid": None if grid is None else {"crs": grid[0], "shape": list(grid[1]), "transform_first6": list(grid[2])},
        "files": rows,
        "forward_dot_overlap_matrix_3px": matrix,
        "exact_subset_table_nonzero_overlap": subsets,
        "gemsdoe32_vs_gemsdoe25": {"removed_from_25": removed, "added_to_25": added,
                                  "is_strict_subset": bool(removed > 0 and added == 0)},
        "claim_checks": {
            "gemsdoe32_pct_of_dots_within_3px_of_gemsdoe24": round(100 * matrix["GEMSDOE32"]["GEMSDOE24"], 4),
            "gemsdoe36_pct_of_dots_within_3px_of_gemsdoe27": round(100 * matrix["GEMSDOE36"]["GEMSDOE27"], 4),
            "gemsdoe28_pct_of_dots_within_3px_of_gemsdoe24": round(100 * matrix["GEMSDOE28"]["GEMSDOE24"], 4),
            "gemsdoe31_pct_of_dots_within_3px_of_gemsdoe24": round(100 * matrix["GEMSDOE31"]["GEMSDOE24"], 4),
        },
        "labels": {"scores": "USER-REPORTED / UNVERIFIED", "not_organizer_receipt": True},
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("grid_identical_across_nine", "grid", "gemsdoe32_vs_gemsdoe25", "claim_checks")}, indent=2))
    print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
