#!/usr/bin/env python3
"""Close the two errored comparisons in the E1 registry gate (session arena/9cf124bb, 2026-10-31).

The archived H-UNQ-1 prototype rasters (archive/prototype/docs/downloads/gemsdoe-unique-hunq1-*)
sit on a different origin (500000, 4500000) from the registry grid (243350, 4508550), so the
cell-index comparison in run_o2_halo_prune_lidar.py could not run. Here dots are compared in
metres: a dot "overlaps" when another set's dot lies within 300 m (3 px at 100 m), the same
radius the official kernel uses. Nothing is written except an evidence JSON.

Usage: .venv/bin/python scripts/check_archived_hunq1_overlap_20261031.py
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / 'docs/downloads/DO-NOT-SUBMIT_karage1-o2-lidar-scarp-halo-prune-37654-20261031-zeros.tif'
HUNQ1_DOTS = ROOT / 'archive/prototype/docs/downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-dots.tif'
HUNQ1_ZEROS = ROOT / 'archive/prototype/docs/downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-zeros.tif'
OUT = ROOT / 'evidence/gate_archived_hunq1_20261031.json'
RADIUS_M = 300.0
BLANKET_CELLS = 100_000


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def positive_xy(path: Path):
    with rasterio.open(path) as s:
        a = s.read(1)
        t = s.transform
        crs = str(s.crs)
        rows, cols = np.nonzero(a > 0)
    x = t.c + (cols + 0.5) * t.a
    y = t.f + (rows + 0.5) * t.e
    return np.column_stack([x, y]), crs, int(a.size)


def nearest_within(src: np.ndarray, dst: np.ndarray, radius: float) -> np.ndarray:
    """Boolean per src point: is any dst point within radius (metres)? Grid-binned, exact."""
    cell = radius
    keys = {}
    for j, (x, y) in enumerate(dst):
        keys.setdefault((int(np.floor(x / cell)), int(np.floor(y / cell))), []).append(j)
    out = np.zeros(len(src), dtype=bool)
    r2 = radius * radius
    for i, (x, y) in enumerate(src):
        kx, ky = int(np.floor(x / cell)), int(np.floor(y / cell))
        hit = False
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for j in keys.get((kx + dx, ky + dy), ()):
                    if (dst[j, 0] - x) ** 2 + (dst[j, 1] - y) ** 2 <= r2:
                        hit = True
                        break
                if hit:
                    break
            if hit:
                break
        out[i] = hit
    return out


def main() -> None:
    cand, cand_crs, _ = positive_xy(CANDIDATE)
    dots, dots_crs, _ = positive_xy(HUNQ1_DOTS)
    blanket, blanket_crs, blanket_size = positive_xy(HUNQ1_ZEROS)
    if not (cand_crs == dots_crs == blanket_crs == 'EPSG:32611'):
        raise SystemExit(f'unexpected CRS: {cand_crs} {dots_crs} {blanket_crs}')
    my_in_dots = nearest_within(cand, dots, RADIUS_M)
    their_in_mine = nearest_within(dots, cand, RADIUS_M)
    my_in_blanket = nearest_within(cand, blanket, RADIUS_M)
    result = {
        'schema': 'karage1-archived-overlap-v1',
        'session': 'arena/9cf124bb-gemsdoekarage1',
        'date_utc': '2026-10-31',
        'method': 'metric nearest-neighbour: dot overlaps if another set has a dot within 300 m (3 px at 100 m); grids differ by a half-cell offset so index comparison is invalid',
        'radius_m': RADIUS_M,
        'candidate': {'file': CANDIDATE.name, 'sha256': sha256(CANDIDATE), 'dots': int(len(cand))},
        'compared': [
            {
                'file': HUNQ1_DOTS.relative_to(ROOT).as_posix(),
                'sha256': sha256(HUNQ1_DOTS),
                'dots': int(len(dots)),
                'candidate_dots_within_3px': round(float(my_in_dots.mean()), 6),
                'their_dots_within_3px_of_candidate': round(float(their_in_mine.mean()), 6),
                'blanket_or_parent_mask': len(dots) > BLANKET_CELLS,
                'ok_under_0_70_literal_gate': bool(my_in_dots.mean() <= 0.70),
            },
            {
                'file': HUNQ1_ZEROS.relative_to(ROOT).as_posix(),
                'sha256': sha256(HUNQ1_ZEROS),
                'positive_cells': int(len(blanket)),
                'grid_cells': blanket_size,
                'candidate_dots_within_3px': round(float(my_in_blanket.mean()), 6),
                'blanket_or_parent_mask': len(blanket) > BLANKET_CELLS,
                'ok_under_0_70_literal_gate': bool(my_in_blanket.mean() <= 0.70),
            },
        ],
        'interpretation': 'H-UNQ-1 zeros file is a probability blanket (positive cells > 100,000); the literal 70% gate is unsatisfiable against it, as registry/registry_roles.json already records. Report, do not clear.',
        'ok_to_submit': False,
    }
    OUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result['compared'], indent=2))


if __name__ == '__main__':
    main()
