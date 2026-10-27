"""4-Azimuth Axial-Crest Sharpening & Exact 300m Triangular-Kernel Lazy-Greedy Submodular Emitter.

Implements Minoux (1978) accelerated lazy-greedy maximization of the exact marginal coverage gain
under the official 300 m (3 px at 100 m resolution) triangular kernel k(d) = max(0, 1 - d / 3.0),
with configurable axial minimum inter-dot Euclidean spacing ``min_sep_px`` (e.g., 2.9 px) to prevent
redundant neighbor packing inside the non-additive max-cover radius.
"""
from __future__ import annotations

import heapq
import math
import numpy as np
from scipy.ndimage import binary_dilation, distance_transform_edt

from gems57 import metric as M57


def _disk_offsets(radius_px: float) -> list[tuple[int, int, float]]:
    r = int(math.ceil(radius_px))
    out: list[tuple[int, int, float]] = []
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            d = math.hypot(dy, dx)
            if d <= radius_px + 1e-9:
                out.append((dy, dx, max(0.0, 1.0 - d / 3.0)))
    return out


KERNEL_OFFSETS = [(dy, dx, kw) for dy, dx, kw in _disk_offsets(3.0) if kw > 0.0]


def sharpen_axial_crest(surface: np.ndarray, foot: np.ndarray, crest_boost: float = 0.52) -> np.ndarray:
    """4-azimuth non-maximum suppression crest sharpener preserving confidence ordering."""
    p = np.where(foot & np.isfinite(surface), np.maximum(surface, np.float32(0.0)), np.float32(0.0)).astype(np.float32)
    h, w = p.shape
    pad = np.pad(p, ((2, 2), (2, 2)), mode="edge")
    c = pad[2 : 2 + h, 2 : 2 + w]

    # 4 transverse directions: N-S, E-W, NE-SW, NW-SE (1 px and 2 px offsets)
    pairs = [
        (pad[1 : 1 + h, 2 : 2 + w], pad[3 : 3 + h, 2 : 2 + w], pad[0:h, 2 : 2 + w], pad[4 : 4 + h, 2 : 2 + w]),
        (pad[2 : 2 + h, 1 : 1 + w], pad[2 : 2 + h, 3 : 3 + w], pad[2 : 2 + h, 0:w], pad[2 : 2 + h, 4 : 4 + w]),
        (pad[1 : 1 + h, 3 : 3 + w], pad[3 : 3 + h, 1 : 1 + w], pad[0:h, 4 : 4 + w], pad[4 : 4 + h, 0:w]),
        (pad[1 : 1 + h, 1 : 1 + w], pad[3 : 3 + h, 3 : 3 + w], pad[0:h, 0:w], pad[4 : 4 + h, 4 : 4 + w]),
    ]
    best_crest = np.zeros_like(c)
    eps = np.float32(1e-7)
    for n1a, n1b, n2a, n2b in pairs:
        flank = np.maximum(np.float32(0.65) * np.maximum(n1a, n1b) + np.float32(0.35) * np.maximum(n2a, n2b), eps)
        is_peak = (c >= n1a) & (c >= n1b)
        prom = np.clip((c - np.float32(0.5) * (n1a + n1b)) / (c + eps), np.float32(0.0), np.float32(1.0))
        score = is_peak.astype(np.float32) * (np.float32(0.55) + np.float32(0.45) * prom) * np.minimum(c / flank, np.float32(1.5))
        best_crest = np.maximum(best_crest, np.clip(score, 0.0, 1.0))

    out = p * (np.float32(1.0 - crest_boost) + np.float32(crest_boost) * best_crest)
    return np.where(foot, out, np.float32(0.0)).astype(np.float32)


def emit_submodular_300m(
    belief: np.ndarray,
    active_domain: np.ndarray,
    visible_faults: np.ndarray,
    budget: int,
    *,
    b_collar_px: float = 2.2,
    min_sep_px: float = 2.9,
    max_candidates: int = 380_000,
) -> np.ndarray:
    """Lazy-greedy 300m triangular-kernel submodular dot allocation using ONLY visible faults.

    Guarantees:
    - Zero access to hidden truth (`visible_faults` is the only fault mask passed).
    - Strict Euclidean collar `EDT(~visible_faults) > b_collar_px`.
    - Exact incremental kernel gain `sum_delta w(x+delta) * max(0, k(delta) - cov(x+delta))`.
    - Minimum Euclidean inter-dot spacing `min_sep_px` (when > 0).
    """
    h, w = belief.shape
    eligible = np.asarray(active_domain, dtype=bool) & ~np.asarray(visible_faults, dtype=bool)
    if b_collar_px > 0.0 and np.any(visible_faults):
        d_vis = distance_transform_edt(~np.asarray(visible_faults, dtype=bool))
        eligible &= d_vis > float(b_collar_px)

    f = np.where(eligible & np.isfinite(belief), np.maximum(belief, np.float32(0.0)), np.float32(0.0))
    if budget <= 0 or not np.any(f > 0):
        return np.zeros((h, w), dtype=bool)

    # Restrict candidate heap to top `max_candidates` positive support pixels for O(K log K) speed
    pos_flat = np.flatnonzero(f > 0)
    if pos_flat.size > max_candidates:
        vals = f.ravel()[pos_flat]
        keep_idx = np.argpartition(vals, -max_candidates)[-max_candidates:]
        pos_flat = pos_flat[keep_idx]

    # Precompute initial upper-bound gain at each candidate
    cov = np.zeros((h, w), dtype=np.float32)
    blocked = np.zeros((h, w), dtype=bool)
    sep_offs = [(dy, dx) for dy, dx, _ in _disk_offsets(min_sep_px)] if min_sep_px > 0.0 else [(0, 0)]

    ys = (pos_flat // w).astype(np.int32)
    xs = (pos_flat % w).astype(np.int32)

    heap: list[tuple[float, int, int, int]] = []
    for idx_i in range(pos_flat.size):
        y = int(ys[idx_i])
        x = int(xs[idx_i])
        g0 = 0.0
        for dy, dx, kw in KERNEL_OFFSETS:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                g0 += float(f[ny, nx]) * kw
        if g0 > 0.0:
            # Deterministic tie-breaker via flat pixel index
            heap.append((-g0, int(pos_flat[idx_i]), y, x))
    heapq.heapify(heap)

    emitted = np.zeros((h, w), dtype=bool)
    n_sel = 0
    while heap and n_sel < budget:
        neg_ub, flat_id, y, x = heapq.heappop(heap)
        if blocked[y, x]:
            continue
        # Recompute exact live marginal gain
        gain = 0.0
        for dy, dx, kw in KERNEL_OFFSETS:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                rem = kw - float(cov[ny, nx])
                if rem > 0.0:
                    gain += float(f[ny, nx]) * rem
        if gain <= 1e-12:
            continue
        # Check if gain is still >= next best upper bound in heap
        if heap and (-gain > heap[0][0] + 1e-12):
            heapq.heappush(heap, (-gain, flat_id, y, x))
            continue

        # Accept (y, x)!
        emitted[y, x] = True
        n_sel += 1
        for dy, dx, kw in KERNEL_OFFSETS:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w and kw > cov[ny, nx]:
                cov[ny, nx] = kw
        for dy, dx in sep_offs:
            ny, nx = y + dy, x + dx
            if 0 <= ny < h and 0 <= nx < w:
                blocked[ny, nx] = True

    return emitted


def compute_spatial_forensics(
    dots: np.ndarray,
    foot: np.ndarray,
    labels: np.ndarray,
    lidar_valid: np.ndarray,
    slope_deg: np.ndarray,
    depth_base: np.ndarray,
) -> dict:
    """Measure the 3 Live-Score Spatial Laws on a binary dot raster."""
    d = np.asarray(dots, dtype=bool) & foot
    n = int(d.sum())
    if n == 0:
        return {"dots": 0}
    d_cat = distance_transform_edt(~(labels & foot))
    far_1p5km = float((d_cat[d] > 15.0).mean())
    in_lidar_gap = float((~lidar_valid[d]).mean())
    flat_deep_basin = float(((slope_deg[d] < 2.0) & (depth_base[d] > 300.0)).mean())

    # Clump>=3: fraction of emitted dots having >=3 OTHER emitted dots within <=3.0 px Euclidean
    r = 3
    yy, xx = np.mgrid[-r : r + 1, -r : r + 1]
    disk3 = (yy * yy + xx * xx <= 9) & ~((yy == 0) & (xx == 0))
    from scipy.ndimage import convolve

    nbrs = convolve(d.astype(np.int16), disk3.astype(np.int16), mode="constant", cval=0)
    clump_ge3 = float((nbrs[d] >= 3).mean())

    # Footprint 300m kernel coverage (fraction of footprint with k(d_dot) > 0, i.e., d_dot < 3.0)
    d_to_dot = distance_transform_edt(~d)
    k_cov = float(np.maximum(0.0, 1.0 - d_to_dot[foot] / 3.0).mean())
    disk_cov = float((d_to_dot[foot] <= 3.0).mean())
    return {
        "dots": n,
        "min_dist_to_catalogue_px": round(float(d_cat[d].min()), 4),
        "far_field_gt_1p5km_frac": round(far_1p5km, 5),
        "lidar_gap_frac": round(in_lidar_gap, 5),
        "flat_deep_basin_frac": round(flat_deep_basin, 5),
        "clump_ge3_in_3px_frac": round(clump_ge3, 5),
        "footprint_300m_weighted_cov": round(k_cov, 5),
        "footprint_300m_disk_cov": round(disk_cov, 5),
    }
