"""Label-free structural surfaces for the GPC lane (gravity-polarity-concordant, contour-oblique
topographic step lineaments).

Nothing in this module reads ``labels.tif`` / ``existing_faults.tif`` or any scored raster.

Surfaces (all float32 on the full grid, NaN-free, 0 outside the footprint):

* ``step``      - multi-scale *step-edge* strength of detrended elevation: ridge of the gradient
                  magnitude after Canny-style non-maximum suppression along the gradient direction,
                  scale-normalised, max over sigma in {1.0, 1.6, 2.5} px. A scarp is a step in
                  elevation, not a crest, so this is an edge transform rather than the Hessian ridge
                  transform used by the H19-5 family.
* ``curvbreak`` - |profile curvature| (second derivative along the gradient) at sigma 1.6 px, the
                  slope-break signature of the piedmont junction / scarp crest and base.
* ``concord``   - polarity concordance in [0, 1]: 0.5 (1 + cos(phi - psi)) where phi is the
                  downslope azimuth of topography (sigma 2 px) and psi is the basin-deepening
                  azimuth, the mean of the directions of -grad(iso_grav_anom) and
                  +grad(depth_to_base_surf), both at sigma 25 px (2.5 km). A basin-bounding normal
                  fault throws its hanging wall toward the basin, so its scarp faces the gravity
                  low / thickening basin fill.
* ``oblique``   - contour obliquity in [0, 1]: along-strike share of the 1-km-scale elevation
                  structure tensor energy. Pluvial shorelines and terrace risers follow contours
                  (obliquity ~0); a fault trace is straight in map view while contours curve, so it
                  crosses contours obliquely over km baselines.
* ``lidar_step``- optional corroboration from the 1 m LiDAR product (``step_max`` band, uint8),
                  rescaled to [0, 1].
"""
from __future__ import annotations

import numpy as np
from scipy import ndimage

from . import grid

STEP_SIGMAS = (1.0, 1.6, 2.5)


def _fill(a: np.ndarray, foot: np.ndarray) -> np.ndarray:
    """Nearest-neighbour fill of invalid cells so derivative filters see no cliffs at the border."""
    a = np.asarray(a, np.float32).copy()
    bad = ~np.isfinite(a)
    if bad.any():
        idx = ndimage.distance_transform_edt(bad, return_distances=False, return_indices=True)
        a = a[tuple(idx)]
    return a


def _nms_along_gradient(mag: np.ndarray, gx: np.ndarray, gy: np.ndarray) -> np.ndarray:
    """Keep gradient-magnitude pixels that are maxima along the (quantised) gradient direction."""
    ang = np.mod(np.arctan2(gy, gx), np.pi)
    sector = np.floor((ang + np.pi / 8) / (np.pi / 4)).astype(int) % 4   # 0:E-W 1:NE 2:N-S 3:NW
    out = np.zeros_like(mag)
    pad = np.pad(mag, 1, mode="edge")
    c = pad[1:-1, 1:-1]
    nbrs = {
        0: (pad[1:-1, :-2], pad[1:-1, 2:]),      # gradient along x -> compare x-neighbours
        1: (pad[:-2, 2:], pad[2:, :-2]),         # gradient along +y+x diagonal
        2: (pad[:-2, 1:-1], pad[2:, 1:-1]),      # gradient along y
        3: (pad[:-2, :-2], pad[2:, 2:]),
    }
    for s, (a, b) in nbrs.items():
        m = (sector == s) & (c >= a) & (c >= b)
        out[m] = c[m]
    return out


def step_surface(z: np.ndarray, foot: np.ndarray, sigmas=STEP_SIGMAS) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (step, gx, gy) with gx/gy from the middle scale (used for facing direction)."""
    best = np.zeros(z.shape, np.float32)
    gx_mid = gy_mid = None
    for s in sigmas:
        gy = ndimage.gaussian_filter(z, s, order=(1, 0), mode="nearest")
        gx = ndimage.gaussian_filter(z, s, order=(0, 1), mode="nearest")
        mag = np.hypot(gx, gy) * s                       # scale-normalised (gamma = 1)
        nms = _nms_along_gradient(mag, gx, gy)
        best = np.maximum(best, nms.astype(np.float32))
        if s == sigmas[len(sigmas) // 2]:
            gx_mid, gy_mid = gx, gy
    best[~foot] = 0
    return best, gx_mid, gy_mid


def curvature_break(z: np.ndarray, foot: np.ndarray, sigma: float = 1.6) -> np.ndarray:
    gy = ndimage.gaussian_filter(z, sigma, order=(1, 0), mode="nearest")
    gx = ndimage.gaussian_filter(z, sigma, order=(0, 1), mode="nearest")
    zxx = ndimage.gaussian_filter(z, sigma, order=(0, 2), mode="nearest")
    zyy = ndimage.gaussian_filter(z, sigma, order=(2, 0), mode="nearest")
    zxy = ndimage.gaussian_filter(z, sigma, order=(1, 1), mode="nearest")
    g2 = gx * gx + gy * gy + 1e-6
    prof = (zxx * gx * gx + 2 * zxy * gx * gy + zyy * gy * gy) / g2
    out = np.abs(prof).astype(np.float32) * sigma ** 2
    out[~foot] = 0
    return out


def concordance(gx: np.ndarray, gy: np.ndarray, grav: np.ndarray, dtb: np.ndarray, sigma_basin: float = 25.0) -> np.ndarray:
    """0.5 (1 + cos(phi - psi)): downslope azimuth vs. basin-deepening azimuth."""
    Gy = ndimage.gaussian_filter(grav, sigma_basin, order=(1, 0), mode="nearest")
    Gx = ndimage.gaussian_filter(grav, sigma_basin, order=(0, 1), mode="nearest")
    Dy = ndimage.gaussian_filter(dtb, sigma_basin, order=(1, 0), mode="nearest")
    Dx = ndimage.gaussian_filter(dtb, sigma_basin, order=(0, 1), mode="nearest")
    # basin-deepening unit vectors: -grad(grav) and +grad(depth_to_basement); average them
    ug = np.stack([-Gx, -Gy]) / (np.hypot(Gx, Gy) + 1e-9)
    ud = np.stack([Dx, Dy]) / (np.hypot(Dx, Dy) + 1e-9)
    u = ug + ud
    u /= (np.hypot(u[0], u[1]) + 1e-9)
    # downslope unit vector of topography is -grad(z)
    dn = np.stack([-gx, -gy]) / (np.hypot(gx, gy) + 1e-9)
    cos = dn[0] * u[0] + dn[1] * u[1]
    return (0.5 * (1.0 + cos)).astype(np.float32)


def obliquity(z: np.ndarray, gx: np.ndarray, gy: np.ndarray, sigma_struct: float = 3.0, window: float = 8.0) -> np.ndarray:
    """Along-strike share of the km-scale elevation structure-tensor energy (0 = contour-parallel)."""
    zx = ndimage.gaussian_filter(z, sigma_struct, order=(0, 1), mode="nearest")
    zy = ndimage.gaussian_filter(z, sigma_struct, order=(1, 0), mode="nearest")
    jxx = ndimage.gaussian_filter(zx * zx, window, mode="nearest")
    jyy = ndimage.gaussian_filter(zy * zy, window, mode="nearest")
    jxy = ndimage.gaussian_filter(zx * zy, window, mode="nearest")
    # local strike unit vector = gradient rotated by 90 degrees
    n = np.hypot(gx, gy) + 1e-9
    sx, sy = -gy / n, gx / n
    along = sx * sx * jxx + 2 * sx * sy * jxy + sy * sy * jyy
    tr = jxx + jyy + 1e-9
    return np.clip(along / tr, 0, 1).astype(np.float32)


def build_all(cache: bool = True) -> dict[str, np.ndarray]:
    """Compute (or load) every surface. Cached as .npy under .cache/surfaces."""
    out_dir = grid.ROOT / ".cache" / "surfaces"
    out_dir.mkdir(parents=True, exist_ok=True)
    names = ["step", "curvbreak", "concord", "oblique", "lidar_step"]
    if cache and all((out_dir / f"{n}.npy").exists() for n in names):
        return {n: np.load(out_dir / f"{n}.npy") for n in names}
    foot = grid.footprint()
    z = _fill(grid.band("det_elev"), foot)
    grav = _fill(grid.band("iso_grav_anom"), foot)
    dtb = _fill(grid.band("depth_to_base_surf"), foot)
    step, gx, gy = step_surface(z, foot)
    surf = {
        "step": step,
        "curvbreak": curvature_break(z, foot),
        "concord": concordance(gx, gy, grav, dtb),
        "oblique": obliquity(z, gx, gy),
    }
    lid = grid.lidar("step_max").astype(np.float32) / 255.0
    lid[~foot] = 0
    surf["lidar_step"] = lid
    for k, v in surf.items():
        v = np.nan_to_num(v, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
        v[~foot] = 0
        surf[k] = v
        np.save(out_dir / f"{k}.npy", v)
    return surf
