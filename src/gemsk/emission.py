"""Dot emission: turn a continuous surface into a sparse binary raster the metric rewards.

Why dots (metric algebra, see metric.py): for a fixed support, binary {0,1} emission dominates any
down-scaled soft version, and every emitted pixel whose realised kernel credit is below
alpha * DTI lowers the score. So the emission problem is: choose the N pixels with the highest
expected kernel credit, spaced so they do not pay twice for the same truth pixel.

Pipeline
1. ``nms_thin``       - optional Canny-style thinning of a non-thinned surface (ridge of the surface
                        along its own gradient direction) so candidate pixels are 1-px lines.
2. ``poisson_select`` - greedy selection in descending score with a Euclidean exclusion disk of
                        radius ``spacing`` px, stopped at ``budget`` dots.
3. ``apron_prune``    - delete dots within ``apron_px`` of the catalogue that is VISIBLE to the run
                        (fold-visible faults in the holdout; the full catalogue in the final build).
                        The live scorer only credits *new* faults, so mass on or next to the
                        catalogue is pure false-positive mass.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage


def rank_normalise(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Map a surface to its percentile rank in [0, 1] over the footprint (0 outside)."""
    out = np.zeros(a.shape, np.float32)
    v = a[foot]
    order = np.argsort(v, kind="stable")
    ranks = np.empty(v.size, np.float32)
    ranks[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    out[foot] = ranks
    return out


def nms_thin(score: np.ndarray, sigma: float = 1.0) -> np.ndarray:
    """Keep local maxima of ``score`` across its own gradient direction (ridge of the surface)."""
    s = ndimage.gaussian_filter(score, sigma, mode="nearest")
    gy = ndimage.sobel(s, axis=0)
    gx = ndimage.sobel(s, axis=1)
    ang = np.mod(np.arctan2(gy, gx), np.pi)
    sector = np.floor((ang + np.pi / 8) / (np.pi / 4)).astype(int) % 4
    pad = np.pad(s, 1, mode="edge")
    c = pad[1:-1, 1:-1]
    nb = {0: (pad[1:-1, :-2], pad[1:-1, 2:]), 1: (pad[:-2, 2:], pad[2:, :-2]),
          2: (pad[:-2, 1:-1], pad[2:, 1:-1]), 3: (pad[:-2, :-2], pad[2:, 2:])}
    keep = np.zeros(s.shape, bool)
    for k, (a, b) in nb.items():
        keep |= (sector == k) & (c >= a) & (c >= b)
    out = np.where(keep, score, 0).astype(np.float32)
    return out


def _disk_offsets(spacing: float):
    r = int(np.floor(spacing))
    offs = [(dy, dx) for dy in range(-r, r + 1) for dx in range(-r, r + 1) if 0 < np.hypot(dy, dx) < spacing]
    return np.array(offs, dtype=np.int64)


def poisson_select(score: np.ndarray, budget: int, spacing: float = 2.8, candidates: np.ndarray | None = None) -> np.ndarray:
    """Greedy max-score selection with a Euclidean exclusion disk. Returns a boolean dot raster."""
    H, W = score.shape
    cand = (score > 0) if candidates is None else (candidates & (score > 0))
    yy, xx = np.nonzero(cand)
    order = np.argsort(-score[yy, xx], kind="stable")
    yy, xx = yy[order], xx[order]
    offs = _disk_offsets(spacing)
    blocked = np.zeros((H + 2 * 8, W + 2 * 8), bool)        # padded so neighbourhood writes never go out of range
    dots = np.zeros((H, W), bool)
    n = 0
    oy, ox = offs[:, 0], offs[:, 1]
    for y, x in zip(yy, xx):
        if blocked[y + 8, x + 8]:
            continue
        dots[y, x] = True
        blocked[y + 8 + oy, x + 8 + ox] = True
        blocked[y + 8, x + 8] = True
        n += 1
        if n >= budget:
            break
    return dots


def apron_prune(dots: np.ndarray, visible_catalogue: np.ndarray, apron_px: int = 2) -> np.ndarray:
    """Remove dots within ``apron_px`` (Euclidean) of any visible catalogue pixel (on-catalogue too)."""
    if apron_px <= 0:
        return dots & ~visible_catalogue
    d = ndimage.distance_transform_edt(~visible_catalogue)
    return dots & (d > apron_px)


def emit(score: np.ndarray, budget: int, visible_catalogue: np.ndarray, *, spacing: float = 2.8, apron_px: int = 2,
         thin: bool = False, overshoot: float = 1.35) -> np.ndarray:
    """Full emission: (thin) -> select ``budget*overshoot`` -> apron prune -> trim to ``budget`` by score."""
    s = nms_thin(score) if thin else score
    # exclude the apron from candidacy up-front so the budget is spent on eligible pixels only
    d = ndimage.distance_transform_edt(~visible_catalogue)
    eligible = d > apron_px
    dots = poisson_select(s, int(budget * overshoot), spacing, candidates=eligible)
    dots = apron_prune(dots, visible_catalogue, apron_px)
    if dots.sum() > budget:
        yy, xx = np.nonzero(dots)
        keep = np.argsort(-s[yy, xx], kind="stable")[:budget]
        dots = np.zeros_like(dots)
        dots[yy[keep], xx[keep]] = True
    return dots
