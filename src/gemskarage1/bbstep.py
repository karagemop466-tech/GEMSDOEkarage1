"""Label-free Buried Basement-Step (BB-STEP) surfaces.

Lane: H-K1-BBSTEP. Nothing in this module reads labels.tif, existing_faults.tif,
or any scored / registry raster. Catalogue distance is applied only by the
caller, fold-locally, after the surface is built.

Physical target
---------------
Intra-basin normal faults buried by alluvium still juxtapose basement of
different density. That produces linear ridges in the isostatic-gravity
horizontal gradient and in the depth-to-conductive-base gradient, *without*
a topographic scarp. USGS Qfaults / INGENIOUS catalogues are scarp-based, so
this signature can exist off-catalogue.

Named non-fault mimic: lithologic contacts, volcanic-flow density edges, and
basin-fill compaction steps.

This is the opposite of the H19-5 / GPC-Z topographic-ridge family: high
topographic slope is a veto, not a vote.
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from gemsk import grid

LANE = "H-K1-BBSTEP"
SIGMAS = (1.6, 2.5, 4.0)


def _fill(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    a = np.asarray(a, np.float32).copy()
    bad = ~np.isfinite(a)
    if bad.any():
        idx = ndimage.distance_transform_edt(bad, return_distances=False, return_indices=True)
        a = a[tuple(idx)]
    a[~foot] = 0.0
    return a


def _nms(mag: np.ndarray, gx: np.ndarray, gy: np.ndarray) -> np.ndarray:
    ang = np.mod(np.arctan2(gy, gx), np.pi)
    sector = np.floor((ang + np.pi / 8) / (np.pi / 4)).astype(int) % 4
    out = np.zeros_like(mag)
    pad = np.pad(mag, 1, mode="edge")
    c = pad[1:-1, 1:-1]
    nbrs = {
        0: (pad[1:-1, :-2], pad[1:-1, 2:]),
        1: (pad[:-2, 2:], pad[2:, :-2]),
        2: (pad[:-2, 1:-1], pad[2:, 1:-1]),
        3: (pad[:-2, :-2], pad[2:, 2:]),
    }
    for s, (left, right) in nbrs.items():
        keep = (sector == s) & (c >= left) & (c >= right)
        out[keep] = c[keep]
    return out


def _multiscale_ridge(field: np.ndarray, foot: np.ndarray, sigmas=SIGMAS) -> np.ndarray:
    best = np.zeros(field.shape, np.float32)
    gx_mid = gy_mid = None
    for i, s in enumerate(sigmas):
        gy = ndimage.gaussian_filter(field, s, order=(1, 0), mode="nearest")
        gx = ndimage.gaussian_filter(field, s, order=(0, 1), mode="nearest")
        mag = np.hypot(gx, gy) * s
        best = np.maximum(best, _nms(mag, gx, gy).astype(np.float32))
        if i == len(sigmas) // 2:
            gx_mid, gy_mid = gx, gy
    best[~foot] = 0.0
    return best, gx_mid, gy_mid


def rank01(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    out = np.zeros(a.shape, np.float32)
    v = a[foot]
    order = np.argsort(v, kind="stable")
    ranks = np.empty(v.size, np.float32)
    ranks[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    out[foot] = ranks
    return out


def build_components(foot: np.ndarray | None = None) -> dict[str, np.ndarray]:
    """Return label-free component surfaces on the competition grid."""
    foot = grid.footprint() if foot is None else foot
    grav = _fill(grid.band("iso_grav_anom"), foot)
    dtb = _fill(grid.band("depth_to_base_surf"), foot)
    slope = _fill(grid.band("det_elev_slope"), foot)
    grav_hg = _fill(grid.band("iso_grav_anom_hg"), foot)
    rtp = _fill(grid.band("rtp"), foot)

    grav_ridge, ggx, ggy = _multiscale_ridge(grav, foot)
    dtb_ridge, dgx, dgy = _multiscale_ridge(dtb, foot)
    mag_ridge, _, _ = _multiscale_ridge(rtp, foot)

    eps = 1e-8
    gnorm = np.hypot(ggx, ggy) + eps
    dnorm = np.hypot(dgx, dgy) + eps
    # Parallelism of gravity vs basement gradient, sign-invariant (fault polarity either way).
    align = ((ggx * dgx + ggy * dgy) / (gnorm * dnorm)) ** 2
    align = np.clip(align, 0.0, 1.0).astype(np.float32)
    align[~foot] = 0.0

    low_slope = 1.0 - rank01(slope, foot)
    # Strict buried gate: keep only the lower half of topographic slope.
    buried = (low_slope >= 0.50).astype(np.float32)
    buried[~foot] = 0.0

    return {
        "grav_ridge": grav_ridge,
        "dtb_ridge": dtb_ridge,
        "mag_ridge": mag_ridge,
        "grav_hg": grav_hg,
        "align": align,
        "low_slope": low_slope,
        "buried": buried,
        "slope": slope,
    }


def combine(comp: dict[str, np.ndarray], foot: np.ndarray, *, slope_gate: float = 0.50,
            use_magnetic: bool = False) -> np.ndarray:
    """Weighted buried basement-step surface in [0, 1] inside the footprint."""
    rg = rank01(comp["grav_ridge"], foot)
    rd = rank01(comp["dtb_ridge"], foot)
    rh = rank01(np.abs(comp["grav_hg"]), foot)
    buried = (comp["low_slope"] >= slope_gate).astype(np.float32)
    buried[~foot] = 0.0
    body = 0.40 * rg + 0.35 * rd + 0.25 * rh
    body *= 0.25 + 0.75 * comp["align"]
    if use_magnetic:
        body = 0.85 * body + 0.15 * rank01(comp["mag_ridge"], foot)
    body *= buried
    body[~foot] = 0.0
    return body.astype(np.float32)
