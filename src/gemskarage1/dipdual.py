"""DIPDUAL lane surfaces (session arena/147b0f11, preregistered 2026-10-28).

Label-free dual-regime fault surfaces. Nothing in this module reads
``labels.tif``; catalogue handling (apron) is applied only by callers,
fold-locally, at emission time.

Regimes
-------
* Exposed (slope rank upper part): DEM step-edge + profile-curvature break +
  1 m LiDAR step polarity, gated by gravity-polarity concordance and contour
  obliquity (GPC components in ``gemsk.features``), with a TIGER
  road-distance veto. Named mimics: Lake Lahontan shoreline benches
  (contour-parallel -> obliquity gate), road/rail embankments (road veto).
* Buried (flattest terrain): BB-STEP gravity/depth-to-basement gradient
  ridges (``gemskarage1.bbstep`` components) shifted **updip** toward shallow
  basement by ``clip(dtb, 0, 2500 m) / tan(60 deg)`` (capped at 8 px).
  A dipping normal fault's basement offset at depth ``d`` lies basinward of
  its surface trace by ``d / tan(dip)``; the gravity ridge tracks the deep
  offset, an expert surface trace extrapolates updip. Named mimics:
  lithologic contacts and volcanic-flow density edges (also shifted, but
  their surface geology is not a fault trace either way).
"""
from __future__ import annotations

import gc
from pathlib import Path

import numpy as np
from scipy import ndimage

from gemsk import emission, features, grid
from gemskarage1.bbstep import build_components, rank01

LANE = "H-K1-DIPDUAL"
CACHE = grid.ROOT / ".cache" / "surfaces"
DIP_DEG = 60.0
MAX_SHIFT_PX = 8.0
DTB_CLIP_M = 2500.0


def _save(name: str, a: np.ndarray) -> np.ndarray:
    CACHE.mkdir(parents=True, exist_ok=True)
    a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)
    np.save(CACHE / f"{name}.npy", a)
    return a


def _load(name: str) -> np.ndarray | None:
    p = CACHE / f"{name}.npy"
    return np.load(p) if p.exists() else None


def _fill(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, np.float32).copy()
    bad = ~np.isfinite(a)
    if bad.any():
        idx = ndimage.distance_transform_edt(bad, return_distances=False, return_indices=True)
        a = a[tuple(idx)]
    return a


def road_factor(foot: np.ndarray) -> np.ndarray:
    """1.0 far from roads, 0.30 on a road centreline (TIGER distance, metres)."""
    cached = _load("dipdual_road_factor")
    if cached is not None:
        return cached
    import rasterio

    p = grid.DATA / "external" / "tiger_road_distance_m.tif"
    with rasterio.open(p) as src:
        d = src.read(1).astype(np.float32)
    d = np.where(np.isfinite(d), d, 1000.0)
    f = np.clip(d / 300.0, 0.30, 1.0).astype(np.float32)
    f[~foot] = 0.0
    return _save("dipdual_road_factor", f)


def lidar_polarity(foot: np.ndarray) -> np.ndarray:
    """Step strength weighted by one-sided facing polarity and coherence."""
    cached = _load("dipdual_lidar_pol")
    if cached is not None:
        return cached
    step = grid.lidar("step_max").astype(np.float32) / 255.0
    down = grid.lidar("downface_max").astype(np.float32)
    up = grid.lidar("upface_max").astype(np.float32)
    coh = grid.lidar("coh100").astype(np.float32) / 255.0
    valid = grid.lidar("valid") > 0
    pol = np.abs(down - up) / (down + up + 1.0)
    out = step * pol.astype(np.float32) * (0.5 + 0.5 * coh)
    out[~valid] = 0.0
    out[~foot] = 0.0
    del step, down, up, coh
    gc.collect()
    return _save("dipdual_lidar_pol", out)


def exposed_surface(foot: np.ndarray, S: dict | None = None) -> np.ndarray:
    cached = _load("dipdual_exposed")
    if cached is not None:
        return cached
    S = features.build_all() if S is None else S
    pol = lidar_polarity(foot)
    rk = {
        "step": emission.rank_normalise(S["step"], foot),
        "curv": emission.rank_normalise(S["curvbreak"], foot),
        "lid": emission.rank_normalise(S["lidar_step"], foot),
        "pol": emission.rank_normalise(pol, foot),
    }
    raw = 0.35 * rk["step"] + 0.20 * rk["curv"] + 0.20 * rk["lid"] + 0.25 * rk["pol"]
    gate = (0.25 + 0.75 * S["concord"]) * (0.40 + 0.60 * S["oblique"])
    out = emission.nms_thin(raw * gate * road_factor(foot))
    out[~foot] = 0.0
    del rk, raw, gate, pol
    gc.collect()
    return _save("dipdual_exposed", out)


def buried_body(comp: dict, foot: np.ndarray) -> np.ndarray:
    """BB-STEP weighted body without the slope gate (mirrors bbstep.combine)."""
    rg = rank01(comp["grav_ridge"], foot)
    rd = rank01(comp["dtb_ridge"], foot)
    rh = rank01(np.abs(comp["grav_hg"]), foot)
    body = 0.40 * rg + 0.35 * rd + 0.25 * rh
    body *= 0.25 + 0.75 * comp["align"]
    body = 0.85 * body + 0.15 * rank01(comp["mag_ridge"], foot)
    body[~foot] = 0.0
    return body.astype(np.float32)


def dip_shift(body: np.ndarray, foot: np.ndarray, dip_deg: float = DIP_DEG) -> np.ndarray:
    """Move ridge mass updip: S(y) = body(y + s*u), u = unit grad(dtb)."""
    dtb = _fill(grid.band("depth_to_base_surf"))
    gy = ndimage.gaussian_filter(dtb, 3.0, order=(1, 0), mode="nearest")
    gx = ndimage.gaussian_filter(dtb, 3.0, order=(0, 1), mode="nearest")
    n = np.hypot(gx, gy) + 1e-9
    uy, ux = (gy / n).astype(np.float32), (gx / n).astype(np.float32)
    s = np.clip(dtb, 0.0, DTB_CLIP_M) / float(np.tan(np.deg2rad(dip_deg))) / 100.0
    s = np.clip(s, 0.0, MAX_SHIFT_PX).astype(np.float32)
    del dtb, gy, gx, n
    gc.collect()
    out = np.zeros(body.shape, np.float32)
    H, W = body.shape
    block = 400
    xs = np.arange(W, dtype=np.float32)[None, :]
    for y0 in range(0, H, block):
        y1 = min(H, y0 + block)
        ys = np.arange(y0, y1, dtype=np.float32)[:, None]
        cy = ys + s[y0:y1] * uy[y0:y1]
        cx = xs + s[y0:y1] * ux[y0:y1]
        out[y0:y1] = ndimage.map_coordinates(body, [cy, cx], order=1, mode="nearest")
    out[~foot] = 0.0
    return out.astype(np.float32)


def build_surfaces(foot: np.ndarray | None = None, log=print) -> dict:
    """Build (or load cached) every DIPDUAL surface. Keys documented in runner."""
    foot = grid.footprint() if foot is None else foot
    out: dict[str, np.ndarray] = {}
    log("[dipdual] GPC components (gemsk.features.build_all) ...", flush=True)
    S = features.build_all()
    out["gpc_step"], out["gpc_curv"] = S["step"], S["curvbreak"]
    out["gpc_concord"], out["gpc_oblique"] = S["concord"], S["oblique"]
    out["lidar_step"] = S["lidar_step"]
    log("[dipdual] exposed surface ...", flush=True)
    out["exposed"] = exposed_surface(foot, S)
    out["lidar_pol"] = lidar_polarity(foot)
    # GPC-physics control exactly as src/gemsk/pipeline.physics_field
    rk = {k: emission.rank_normalise(S[k], foot) for k in ("step", "curvbreak", "lidar_step")}
    gate = 0.25 + 0.75 * S["concord"]
    gpc = emission.nms_thin((0.45 * rk["step"] + 0.25 * rk["curvbreak"] + 0.30 * rk["lidar_step"]) * gate)
    gpc[~foot] = 0.0
    out["gpc_physics"] = _save("dipdual_gpc_physics", gpc)
    del S, rk, gate, gpc
    gc.collect()

    log("[dipdual] BB-STEP components ...", flush=True)
    comp = build_components(foot)
    out["grav_ridge"], out["dtb_ridge"] = comp["grav_ridge"], comp["dtb_ridge"]
    out["mag_ridge"], out["align"] = comp["mag_ridge"], comp["align"]
    out["low_slope"] = comp["low_slope"]
    body = _load("dipdual_buried_body")
    if body is None:
        body = _save("dipdual_buried_body", buried_body(comp, foot))
    out["buried_body"] = body
    buried_regime = (comp["low_slope"] >= 0.55) & foot
    np.save(CACHE / "dipdual_buried_regime.npy", buried_regime)
    out["buried_regime"] = buried_regime
    out["exposed_regime"] = foot & ~buried_regime

    nodip = _load("dipdual_buried_nodip")
    if nodip is None:
        t = emission.nms_thin(body)
        t[~buried_regime] = 0.0
        nodip = _save("dipdual_buried_nodip", t)
    out["buried_nodip"] = nodip

    dip = _load("dipdual_buried_dip")
    if dip is None:
        log("[dipdual] dip shift ...", flush=True)
        shifted = dip_shift(body, foot)
        _save("dipdual_buried_body_shifted", shifted)
        t = emission.nms_thin(shifted)
        t[~buried_regime] = 0.0
        dip = _save("dipdual_buried_dip", t)
        del shifted, t
    out["buried_dip"] = dip
    out["buried_body_shifted"] = _load("dipdual_buried_body_shifted")

    # BB-STEP control surface: repo combine() best EXP3 config, thinned once
    # so every arm shares the same emission code path.
    from gemskarage1.bbstep import combine

    bb = _load("dipdual_bbstep_control")
    if bb is None:
        t = emission.nms_thin(combine(comp, foot, slope_gate=0.55, use_magnetic=True))
        t[~foot] = 0.0
        bb = _save("dipdual_bbstep_control", t)
    out["bbstep"] = bb

    # Combined rank surface for pre-placement Spearman (regime-local ranks).
    dual = np.where(
        out["exposed_regime"],
        rank01(out["exposed"], foot),
        rank01(out["buried_body_shifted"], foot),
    ).astype(np.float32)
    dual[~foot] = 0.0
    out["dual_surface"] = _save("dipdual_dual_surface", dual)
    del comp
    gc.collect()
    return out


def emit_dual(
    exposed: np.ndarray,
    buried: np.ndarray,
    exposed_regime: np.ndarray,
    buried_regime: np.ndarray,
    dual_surface: np.ndarray,
    visible: np.ndarray,
    budget: int,
    frac_exposed: float = 0.65,
    *,
    spacing: float = 2.8,
    apron_px: int = 2,
) -> tuple[np.ndarray, dict]:
    """Quota emission: exposed dots first, then buried, spacing enforced across regimes."""
    dvis = ndimage.distance_transform_edt(~np.asarray(visible, bool))
    elig = dvis > apron_px
    n_a = int(round(budget * frac_exposed))
    n_b = budget - n_a
    dots_a = emission.poisson_select(
        exposed, n_a, spacing, candidates=elig & exposed_regime & (exposed > 0)
    )
    cand_b = elig & buried_regime & (buried > 0)
    if dots_a.any():
        cand_b &= ndimage.distance_transform_edt(~dots_a) >= spacing
    dots_b = emission.poisson_select(buried, n_b, spacing, candidates=cand_b)
    dots = dots_a | dots_b
    info = {"n_exposed": int(dots_a.sum()), "n_buried": int(dots_b.sum()), "n_topup": 0}
    short = budget - int(dots.sum())
    if short > 0:  # a regime ran out of eligible ridge pixels; top up anywhere
        cand = elig & (dual_surface > 0)
        if dots.any():
            cand &= ndimage.distance_transform_edt(~dots) >= spacing
        extra = emission.poisson_select(dual_surface, short, spacing, candidates=cand)
        dots |= extra
        info["n_topup"] = int(extra.sum())
    dots &= elig  # apron is a hard guarantee, reasserted
    info["n_total"] = int(dots.sum())
    return dots, info
