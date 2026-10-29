#!/usr/bin/env python3
"""Measured pairwise dot overlap among the nine focus-site best files, the lattice and the candidate.

Uses the shared gems57.uniqueness.dot_overlap (forward = share of row's dots within 3 px of column's
dots). Writes evidence/site_overlap_matrix_20261029.json. Registry bytes come from the
SHA-pinned restore (scripts/restore_data.py --group registry); nothing is downloaded here.
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
from gems57.uniqueness import dot_overlap, _dots  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"
OUT = ROOT / "evidence" / "site_overlap_matrix_20261029.json"

# Best user-reported file per focus site (USER-REPORTED / UNVERIFIED; no organizer receipt) and its
# restored registry file. Keys are the labels used on the hub page.
SITES = [
    ("GEMSDOE24", "h25-1-dotted-h19-5-d1-5", 0.2477, "GEMSDOE24_h25-1-dotted-h19-5-d1-5_allfinite.tif"),
    ("GEMSDOE25", "dotted-h19-5-d2-8", 0.2600, "GEMSDOE25_dotted-h19-5-d2-8_zeros.tif"),
    ("GEMSDOE27", "topo-gap-closure-t-v2-on-d1-5", 0.2449, "GEMSDOE27_topo-gap-closure-t-v2-on-d1-5_allfinite.tif"),
    ("GEMSDOE28", "h36-1-rung30-blind-r1", 0.2710, "GEMSDOE28_h36-1-rung30-blind-r1_allfinite.tif"),
    ("GEMSDOE30", "d28-poisson300m-offcat-44090", 0.2600, "GEMSDOE30_d28-poisson300m-offcat-44090.tif"),
    ("GEMSDOE31", "h27-4-solo-d28", 0.2708, "GEMSDOE31_h27-4-solo-d28_allfinite.tif"),
    ("GEMSDOE32", "h33-h33-2-b2", 0.2778, "GEMSDOE32_h33-h33-2-b2_e5eb6e7e_zeros.tif"),
    ("GEMSDOE33", "h33d-analog-tip-stepover-r30", 0.2632, "GEMSDOE33_h33d-analog-tip-stepover-r30.tif"),
    ("GEMSDOE36", "anderson-geothermal-pinn-38854", 0.2750, "GEMSDOE36_anderson-geothermal-pinn-38854_zeros.tif"),
]
LATTICE = "13GEMSDOE_r13-lattice-s5_v2_nan-outside.tif"
CANDIDATE = "docs/downloads/karage1-tiltgrav-ridge-sp6-37654-20261029.tif"


def load_dots(path: Path, fp: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as ds:
        a = np.nan_to_num(ds.read(1).astype(np.float32), nan=0.0)
    return np.where(fp, a, 0).astype(np.float32)


def main():
    with rasterio.open(DATA / "sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    items = []
    for site, name, score, fname in SITES:
        p = DATA / "registry" / fname
        items.append(dict(label=site, file=name, reported=score, path=f"registry/{fname}", source=p))
    items.append(dict(label="13GEMSDOE lattice (calibration)", file=LATTICE, reported=0.0904,
                      path=f"registry/{LATTICE}", source=DATA / "registry" / LATTICE))
    cand = ROOT / CANDIDATE
    items.append(dict(label="NEW candidate (H-TILTGRAV)", file=cand.name, reported=None,
                      path=CANDIDATE, source=cand))
    arrays = []
    for it in items:
        arr = load_dots(it["source"], fp)
        arrays.append(arr)
        it["sha256"] = hashlib.sha256(Path(it["source"]).read_bytes()).hexdigest()
        it["dots"] = int((_dots(arr) & fp).sum())
    n = len(items)
    matrix = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 1.0
            else:
                matrix[i][j] = round(float(dot_overlap(arrays[i], arrays[j])), 6)
    # The lattice row is the calibration probe: report, not hide.
    out = dict(
        schema="karage1-site-overlap-matrix-v1", date="2026-10-29",
        measure="forward: share of ROW dots within 3 px (300 m) of COLUMN dots (gems57.uniqueness.dot_overlap)",
        limit_literal=0.70,
        items=[{k: v for k, v in it.items() if k != "source"} for it in items],
        matrix=matrix,
        evaluator_note="Lattice row/column are calibration-probe context; see knowledge/ for the gate question.",
    )
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
