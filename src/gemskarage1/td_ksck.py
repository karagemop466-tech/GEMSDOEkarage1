"""`TD-KSCK` dedicated method lane (`H-K1-S2-1` .. `H-K1-S2-4`):
True Miller-Singh/Cooper-Cowan Magnetic & Gravity Tilt Contacts, 10 m USGS 3DEP
Geomorphic Breaklines & Fluvial Chi/Ksn Knickzone Strike-Bridging, Orthometric
Lahontan/Pluton De-Confounding, and Two-Stage Leak-Free Structural-Network OOF.

Memory discipline: streaming float32 2-D arrays + disk-backed memmaps (< 850 MB RSS).
"""
from __future__ import annotations

import gc
import json
import math
from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (str(_REPO_ROOT / "vendor"), str(_REPO_ROOT / "src")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import lightgbm as lgb
import numpy as np
import rasterio
from numpy.lib.format import open_memmap
from scipy.ndimage import binary_dilation, distance_transform_edt, gaussian_filter, shift
from sklearn.metrics import roc_auc_score

from gems57 import evaluate_holdout as eh57
from gems57 import grid as G57
from gems57 import holdout as H57
from gemskarage1.emitter import sharpen_axial_crest
from gemskarage1.features import ALL_CHANNELS, BASE_CHANNELS, MSUB_INDICES
from gemskarage1.holdout_eval import (
    _block_ids_256,
    _bootstrap_ci_and_delta,
    _pooled_dti_blocks,
    _quantile_match_to_ref,
    build_hr3_draws,
    quadrant_folds_with_collar,
)

HEIGHT = G57.HEIGHT
WIDTH = G57.WIDTH

TD_KSCK_CHANNELS: tuple[str, ...] = (
    "true_neg_mag_tilt_slot",           # 0 (repairs IR-KARAGE1-BAND6-01 dead-zero ch 36)
    "mag_tilt_angle_rad",               # 1 Miller & Singh (1994) magnetic tilt angle
    "mag_tdx_contact_crest",            # 2 Cooper & Cowan (2006) / Salem (2007) zero-contour crest
    "grav_tilt_angle_rad",              # 3 Isostatic gravity tilt angle
    "grav_tdx_contact_crest",           # 4 Gravity basement contact zero-contour crest
    "listric_grav_mag_dip_offset",      # 5 H-K1-S2-2 cross-potential-field listric dip offset
    "dem10_slope_p90_deg",              # 6 Seamless 10 m 3DEP p90 slope (100% footprint)
    "dem10_curv_prof_absmax",           # 7 Seamless 10 m 3DEP max |profile curvature|
    "dem10_aspect_coherence",           # 8 Seamless 10 m 3DEP sub-pixel aspect coherence
    "dem10_hs_lineament",               # 9 Seamless 10 m 3DEP hillshade lineament energy
    "dem10_relief_local_m",             # 10 Seamless 10 m 3DEP local relief
    "dem10_scarp_breakline_index",      # 11 Low-relief piedmont scarp breakline composite
    "fluvial10_chi_step_pos",           # 12 Perron-Royden 10 m convex chi-steepness step
    "fluvial10_ksn_knick_density",      # 13 10 m normalized channel steepness x knickpoint count
    "fluvial10_knick_strike_bridge_1200m",  # 14 Anisotropic range-front knickzone fan-mouth bridge
    "orthometric_elev_zmean_m",         # 15 Exact orthometric elevation (1,032..3,141 m ASL)
    "lahontan_dixie_shoreline_mimic",   # 16 Orthometric Lahontan (1335m/1272m) & Dixie (1095m) mimic
    "pluton_core_nonq_mimic",           # 17 Pre-Cenozoic high-elevation granitic pluton core mimic
    "riedel_relay_junction_invariant",  # 18 H-K1-S2-3 Hessian/tensor fault-intersection invariant
)


def _oriented_gaussian_2d(arr: np.ndarray, angle_rad: float, sigma_along: float, sigma_across: float) -> np.ndarray:
    """Fast 2-D anisotropic Gaussian via separable rotated kernel on compact support."""
    rad = int(min(max(math.ceil(2.5 * sigma_along), 3), 24))
    y, x = np.mgrid[-rad : rad + 1, -rad : rad + 1].astype(np.float32)
    ca = float(math.cos(angle_rad))
    sa = float(math.sin(angle_rad))
    u = x * ca + y * sa
    v = -x * sa + y * ca
    kern = np.exp(-0.5 * ((u / sigma_along) ** 2 + (v / sigma_across) ** 2)).astype(np.float32)
    kern /= float(kern.sum()) + 1e-12
    from scipy.signal import fftconvolve

    out = fftconvolve(arr.astype(np.float32, copy=False), kern, mode="same")
    return out.astype(np.float32, copy=False)


def build_td_ksck_extension_stack(
    base_stack_path: Path,
    ddir: Path,
    cdir: Path,
    *,
    force: bool = False,
    log=print,
) -> dict:
    """Build or reuse the 19-channel float32 `TD-KSCK` companion stack (100% footprint coverage)."""
    ext_path = cdir / "karage1_td_ksck_19ch_f32.memmap"
    meta_path = cdir / "karage1_td_ksck_19ch_meta.json"
    if not force and ext_path.is_file() and meta_path.is_file():
        meta = json.loads(meta_path.read_text())
        if meta.get("n_channels") == len(TD_KSCK_CHANNELS) and ext_path.stat().st_size >= len(TD_KSCK_CHANNELS) * HEIGHT * WIDTH * 4:
            log(f"[td_ksck] Reusing cached 19-channel TD-KSCK stack at {ext_path}")
            return meta

    with rasterio.open(ddir / "sample_submission.tif") as ds_s:
        foot = np.isfinite(ds_s.read(1))

    base_mm = open_memmap(base_stack_path, mode="r")
    ext_mm = open_memmap(ext_path, mode="w+", dtype="float32", shape=(len(TD_KSCK_CHANNELS), HEIGHT, WIDTH))

    def _put(idx: int, arr: np.ndarray) -> None:
        clean = np.where(foot & np.isfinite(arr), arr, 0.0).astype(np.float32, copy=False)
        ext_mm[idx] = clean

    log("[td_ksck] Computing true Miller-Singh/Cooper-Cowan magnetic & gravity tilt contact mechanics...")
    # Base stack indices (0-based):
    # band02=1 (rtp), band06=5 (tc radiometric!), band07=6 (shearrate), band08=7 (dilaterate),
    # band09=8 (tmi_vg), band11=10 (iso_grav_anom_vg), band13=12 (iso_grav_anom),
    # band15=14 (depth_to_base_surf), band17=16 (cond_surf), band18=17 (iso_grav_anom_hg)
    rtp = gaussian_filter(base_mm[1].astype(np.float32, copy=True), sigma=1.0)
    rtp_gy, rtp_gx = np.gradient(rtp)
    rtp_hg = np.hypot(rtp_gx, rtp_gy).astype(np.float32)
    tmi_vg = base_mm[8].astype(np.float32, copy=True)

    # Scale vertical derivative (nT/m) by 100 m grid spacing to match per-pixel horizontal gradient (nT/100m)
    mag_tilt = np.arctan2(tmi_vg * np.float32(100.0), rtp_hg + np.float32(1e-3)).astype(np.float32)
    mt_gy, mt_gx = np.gradient(gaussian_filter(mag_tilt, sigma=0.9))
    mt_grad = np.hypot(mt_gx, mt_gy).astype(np.float32)
    mag_tdx = (
        np.arctan2(mt_grad, np.abs(tmi_vg) * np.float32(0.05) + np.float32(0.08))
        * np.exp(-0.5 * (mag_tilt / np.float32(0.38)) ** 2)
    ).astype(np.float32)

    cond_pos = np.log1p(np.maximum(base_mm[16].astype(np.float32, copy=True), 0.0)).astype(np.float32)
    true_neg_slot = (
        np.maximum(-mag_tilt, 0.0)
        * mt_grad
        * (np.float32(0.5) + np.float32(0.5) * cond_pos / (float(np.percentile(cond_pos[foot][::16], 95)) + 1e-5))
    ).astype(np.float32)

    _put(0, true_neg_slot)
    _put(1, mag_tilt)
    _put(2, mag_tdx)
    del rtp, rtp_gy, rtp_gx, rtp_hg, tmi_vg, mt_gy, mt_gx, mt_grad, true_neg_slot, cond_pos

    # Gravity tilt angle & listric dip-concordant offset (H-K1-S2-2)
    grav_vg = base_mm[10].astype(np.float32, copy=True)
    grav_hg = np.maximum(base_mm[17].astype(np.float32, copy=True), 0.0)
    # Harmonize physical units via robust footprint MAD so zero-crossing & phase angle are scale-invariant
    gvg_scale = float(np.percentile(np.abs(grav_vg[foot][::16]), 75)) + 1e-6
    ghg_scale = float(np.percentile(grav_hg[foot][::16], 75)) + 1e-6
    grav_tilt = np.arctan2(grav_vg / np.float32(gvg_scale), grav_hg / np.float32(ghg_scale) + np.float32(1e-3)).astype(np.float32)
    gt_gy, gt_gx = np.gradient(gaussian_filter(grav_tilt, sigma=1.1))
    gt_grad = np.hypot(gt_gx, gt_gy).astype(np.float32)
    grav_tdx = (gt_grad * np.exp(-0.5 * (grav_tilt / np.float32(0.40)) ** 2)).astype(np.float32)

    depth_b = np.maximum(base_mm[14].astype(np.float32, copy=True), 0.0)
    db_gy, db_gx = np.gradient(gaussian_filter(depth_b, sigma=2.5))
    db_grad = np.hypot(db_gx, db_gy).astype(np.float32)
    db_p90 = float(np.percentile(db_grad[foot][::16], 90)) + 1e-5
    dip_offset = ((mag_tilt - grav_tilt) * np.tanh(db_grad / np.float32(db_p90))).astype(np.float32)

    _put(3, grav_tilt)
    _put(4, grav_tdx)
    _put(5, dip_offset)
    del grav_vg, grav_hg, grav_tilt, gt_gy, gt_gx, gt_grad, db_gy, db_gx, db_grad, dip_offset, mag_tilt
    gc.collect()

    log("[td_ksck] Unpacking 100%-footprint USGS 3DEP 10 m geomorphic & fluvial chi/ksn stacks...")
    topo_manifest = json.loads((ddir / "external" / "topo_10m_derived_100m_u8.manifest.json").read_text())
    band_scales = {b["band_name"]: (float(b["lo"]), float(b["hi"])) for b in topo_manifest["bands"]}

    def _read_topo10(b_idx_1based: int, b_name: str, ds_t) -> np.ndarray:
        q = ds_t.read(b_idx_1based)
        lo, hi = band_scales[b_name]
        val = np.where(q > 0, lo + (q.astype(np.float32) - 1.0) * ((hi - lo) / 254.0), 0.0).astype(np.float32)
        if b_name == "aspect_coherence":
            # Fill tiny 1.07% flat-playa undefined aspect cells with neutral low coherence
            val = np.where((q == 0) & foot, np.float32(lo), val)
        return val

    with rasterio.open(ddir / "external" / "topo_10m_derived_100m_u8.tif") as ds_t:
        slp_p90 = _read_topo10(1, "slope_p90", ds_t)
        rel_10m = _read_topo10(5, "relief_local", ds_t)
        curv_10m = _read_topo10(6, "curv_prof_absmax", ds_t)
        asp_coh = _read_topo10(7, "aspect_coherence", ds_t)
        hs_lin = _read_topo10(8, "hs_lineament", ds_t)

    _put(6, slp_p90)
    _put(7, curv_10m)
    _put(8, asp_coh)
    _put(9, hs_lin)
    _put(10, rel_10m)

    scarp_raw = (curv_10m * (asp_coh ** 2) / (np.float32(1.0) + np.float32(0.05) * rel_10m)).astype(np.float32)
    # Multi-azimuth strike enhancement (500 m) of 10 m piedmont scarp breaklines
    scarp_max = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    for m in range(6):
        ang = m * math.pi / 6.0
        scarp_max = np.maximum(scarp_max, _oriented_gaussian_2d(scarp_raw, ang, sigma_along=5.0, sigma_across=1.0))
    _put(11, scarp_max)
    del scarp_raw

    with rasterio.open(ddir / "external" / "dem10_chi_100m_i16.tif") as ds_ci:
        step_i16 = ds_ci.read(1)
        ksn_i16 = ds_ci.read(3)
        zmean_i16 = ds_ci.read(5)
    with rasterio.open(ddir / "external" / "dem10_chi_100m_u8.tif") as ds_cu:
        knick_u8 = ds_cu.read(2)

    chi_step_pos = np.where((step_i16 > -32768) & (step_i16 > 0), step_i16.astype(np.float32) * 0.001, 0.0).astype(np.float32)
    chi_step_sm = gaussian_filter(chi_step_pos, sigma=2.2).astype(np.float32)
    ksn_pos = np.where((ksn_i16 > -32768) & (ksn_i16 > 0), ksn_i16.astype(np.float32), 0.0).astype(np.float32)
    ksn_knick = gaussian_filter(ksn_pos * np.log1p(knick_u8.astype(np.float32)), sigma=2.5).astype(np.float32)
    zmean_m = np.where(zmean_i16 > -32768, zmean_i16.astype(np.float32), 1500.0).astype(np.float32)

    _put(12, chi_step_sm)
    _put(13, ksn_knick)
    _put(15, zmean_m)
    del step_i16, ksn_i16, zmean_i16, knick_u8

    # Anisotropic Range-Front Knickzone Strike-Bridge (1,200 m) perpendicular to regional elevation gradient
    z_smooth = gaussian_filter(zmean_m, sigma=6.0)
    z_gy, z_gx = np.gradient(z_smooth)
    z_gnorm = np.hypot(z_gx, z_gy) + np.float32(1e-4)
    # Strike angle = perpendicular to regional slope gradient
    strike_ang = np.arctan2(z_gy, z_gx) + np.float32(0.5 * math.pi)
    piedmont_gate = np.exp(-0.5 * (np.maximum(rel_10m - np.float32(32.0), 0.0) / np.float32(18.0)) ** 2).astype(np.float32)
    knick_seed = ((chi_step_pos + np.float32(0.015) * ksn_knick) * piedmont_gate).astype(np.float32)
    knick_bridge = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    n_az = 6
    for m in range(n_az):
        phi = m * math.pi / n_az
        resp = _oriented_gaussian_2d(knick_seed, phi, sigma_along=11.5, sigma_across=2.0)
        # Weight by alignment with local range-front contour strike
        align = np.cos(strike_ang - phi) ** 2
        knick_bridge = np.maximum(knick_bridge, (resp * align).astype(np.float32))
    _put(14, knick_bridge)
    del chi_step_pos, chi_step_sm, ksn_pos, ksn_knick, knick_seed, piedmont_gate, z_smooth

    log("[td_ksck] Computing orthometric Lake Lahontan/Dixie shoreline & pluton-core de-confounders + Riedel junctions...")
    # Orthometric Lake Lahontan Sehoo/Eetza (1336 m +- 8 m), Fallon/Dendritic (1273 m +- 9 m), Lake Dixie (1097 m +- 8 m)
    lahontan_band = (
        np.exp(-0.5 * ((zmean_m - np.float32(1336.0)) / np.float32(8.5)) ** 2)
        + np.float32(0.80) * np.exp(-0.5 * ((zmean_m - np.float32(1273.0)) / np.float32(9.0)) ** 2)
        + np.float32(0.75) * np.exp(-0.5 * ((zmean_m - np.float32(1097.0)) / np.float32(8.5)) ** 2)
    ).astype(np.float32)
    # Shoreline benches have scarp breaklines on gentle slopes with weak basement gravity/magnetic tilt contacts
    tdx_sum = mag_tdx + grav_tdx
    tdx_p75 = float(np.percentile(tdx_sum[foot][::16], 75)) + 1e-5
    weak_geophys = np.exp(-tdx_sum / np.float32(tdx_p75)).astype(np.float32)
    lahontan_mimic = (lahontan_band * np.tanh(scarp_max / (float(np.percentile(scarp_max[foot][::16], 80)) + 1e-5)) * weak_geophys).astype(np.float32)
    _put(16, lahontan_mimic)

    # Pre-Cenozoic high-elevation granitic pluton interior mimic (z > 1920 m, exposed bedrock, high Radiometric TC)
    rad_tc = np.maximum(base_mm[5].astype(np.float32, copy=True), 0.0)
    tc_p75 = float(np.percentile(rad_tc[foot][::16], 75)) + 1e-5
    high_elev_gate = (1.0 / (1.0 + np.exp(-(zmean_m - np.float32(1920.0)) / np.float32(110.0)))).astype(np.float32)
    shallow_base_gate = np.exp(-depth_b / np.float32(35.0)).astype(np.float32)
    pluton_mimic = (high_elev_gate * shallow_base_gate * np.tanh(rad_tc / np.float32(tc_p75))).astype(np.float32)
    _put(17, pluton_mimic)
    del rad_tc, high_elev_gate, shallow_base_gate, lahontan_band, weak_geophys, lahontan_mimic, pluton_mimic, z_gy, z_gx, z_gnorm

    # H-K1-S2-3 Multi-Physics Riedel / Relay-Intersection Structure-Tensor Corner Invariant
    mp_ridge = (
        hs_lin / (float(np.percentile(hs_lin[foot][::16], 90)) + 1e-5)
        + np.float32(0.75) * mag_tdx / (float(np.percentile(mag_tdx[foot][::16], 90)) + 1e-5)
        + np.float32(0.75) * grav_tdx / (float(np.percentile(grav_tdx[foot][::16], 90)) + 1e-5)
    ).astype(np.float32)
    ry, rx = np.gradient(gaussian_filter(mp_ridge, sigma=1.2))
    j_xx = gaussian_filter(rx * rx, sigma=3.2)
    j_yy = gaussian_filter(ry * ry, sigma=3.2)
    j_xy = gaussian_filter(rx * ry, sigma=3.2)
    det_j = np.maximum(j_xx * j_yy - j_xy * j_xy, 0.0)
    tr_j = j_xx + j_yy + np.float32(1e-5)
    geod_strain = np.hypot(base_mm[6].astype(np.float32, copy=True), base_mm[7].astype(np.float32, copy=True))
    geod_norm = geod_strain / (float(np.percentile(geod_strain[foot][::16], 75)) + 1e-5)
    junction_inv = (np.sqrt(det_j / tr_j) * (np.float32(0.70) + np.float32(0.30) * np.tanh(geod_norm))).astype(np.float32)
    _put(18, junction_inv)

    ext_mm.flush()
    del ext_mm, mp_ridge, ry, rx, j_xx, j_yy, j_xy, det_j, tr_j, geod_strain, junction_inv, slp_p90, rel_10m, curv_10m, asp_coh, hs_lin, scarp_max, mag_tdx, grav_tdx, depth_b, zmean_m
    gc.collect()

    meta = {
        "schema_version": "karage1-td-ksck-ext-v1",
        "ext_stack_path": str(ext_path),
        "n_channels": len(TD_KSCK_CHANNELS),
        "channels": list(TD_KSCK_CHANNELS),
        "height": HEIGHT,
        "width": WIDTH,
        "footprint_pixels": int(foot.sum()),
        "repairs": ["IR-KARAGE1-BAND6-01", "IR-KARAGE1-ELEV-01", "IR-KARAGE1-RESTORE-01"],
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    log(f"[td_ksck] Saved 19-channel TD-KSCK companion stack -> {meta_path}")
    return meta


def run_td_ksck_leakage_canary(
    base_stack_path: Path,
    ext_stack_path: Path,
    foot: np.ndarray,
    labels: np.ndarray,
    *,
    ceiling_auc: float = 0.90,
) -> dict:
    """Protocol Rule 4 solo Leakage Canary across all 58 base + 19 TD-KSCK = 77 channels."""
    grid = G57.Grid(
        footprint=foot,
        catalogue=labels,
        crs=G57.CRS_EPSG,
        transform=G57.TRANSFORM,
        height=HEIGHT,
        width=WIDTH,
    )
    ctx = H57.build_holdout(grid, seeds=(20,), modes=("detached",))
    pos_mask = np.zeros_like(foot, dtype=bool)
    active_union = np.zeros_like(foot, dtype=bool)
    for cell in ctx.cells_of("detached"):
        sy, sx = cell.bbox
        pos_mask |= ctx.hidden_by_cell[cell.key]
        act_full = np.zeros_like(foot, dtype=bool)
        act_full[sy, sx] = cell.active
        active_union |= act_full

    vis_all = labels & ~pos_mask
    d_vis = distance_transform_edt(~vis_all)
    det_union = pos_mask & (d_vis > 3.0)
    bg_mask = active_union & ~labels & (d_vis > 3.0)
    rng = np.random.default_rng(20261028)
    pos_idx = np.flatnonzero(det_union)
    bg_all = np.flatnonzero(bg_mask)
    bg_idx = rng.choice(bg_all, size=min(120_000, bg_all.size), replace=False)
    eval_idx = np.concatenate([pos_idx, bg_idx])
    y_true = np.concatenate([np.ones(pos_idx.size, dtype=np.int32), np.zeros(bg_idx.size, dtype=np.int32)])
    ys, xs = eval_idx // WIDTH, eval_idx % WIDTH

    base_mm = open_memmap(base_stack_path, mode="r")
    ext_mm = open_memmap(ext_stack_path, mode="r")

    rows = []
    max_dir_auc = 0.0
    max_ch = ""
    leaking = []

    all_specs = [("base", i, name) for i, name in enumerate(ALL_CHANNELS)] + [
        ("td_ksck", j, name) for j, name in enumerate(TD_KSCK_CHANNELS)
    ]
    for src, idx, name in all_specs:
        vals = (base_mm[idx, ys, xs] if src == "base" else ext_mm[idx, ys, xs]).astype(np.float64)
        vals = np.nan_to_num(vals, nan=0.0, posinf=0.0, neginf=0.0)
        raw_auc = 0.5 if float(np.std(vals)) < 1e-12 else float(roc_auc_score(y_true, vals))
        dir_auc = max(raw_auc, 1.0 - raw_auc)
        flag = dir_auc > ceiling_auc
        if flag:
            leaking.append(name)
        if dir_auc > max_dir_auc:
            max_dir_auc = dir_auc
            max_ch = name
        rows.append(
            {
                "source": src,
                "channel_index": idx,
                "feature": name,
                "nonzero_eval_fraction": round(float((np.abs(vals) > 1e-12).mean()), 5),
                "raw_auc": round(raw_auc, 5),
                "direction_invariant_auc": round(dir_auc, 5),
                "leaking": bool(flag),
            }
        )

    return {
        "protocol_rule": "Rule-4-Single-Feature-Leakage-Canary",
        "evaluator_holdout": eh57.VERSION,
        "auc_ceiling": ceiling_auc,
        "n_channels_tested": len(all_specs),
        "n_withheld_detached_positives": int(pos_idx.size),
        "n_background_samples": int(bg_idx.size),
        "repaired_neg_mag_tilt_nonzero_fraction": rows[len(ALL_CHANNELS)]["nonzero_eval_fraction"],
        "legacy_ch36_neg_tmi_tc_nonzero_fraction": rows[36]["nonzero_eval_fraction"],
        "max_direction_invariant_auc": round(max_dir_auc, 5),
        "max_feature": max_ch,
        "leaking_features": leaking,
        "all_passed": len(leaking) == 0,
        "channels": rows,
    }


def _extract_stage2_network_features(
    p_s1: np.ndarray,
    base_mm: np.ndarray,
    ext_mm: np.ndarray,
    foot: np.ndarray,
) -> np.ndarray:
    """Compute 18-channel multi-scale anisotropic structural-network features strictly from OOF `p_s1` + physics.

    Returns shape `(18, HEIGHT, WIDTH)` float32 (~885 MB peak, freed right after Stage-2 fit/predict).
    """
    p = np.where(foot & np.isfinite(p_s1), np.clip(p_s1, 0.0, 1.0), 0.0).astype(np.float32)
    out = np.zeros((18, HEIGHT, WIDTH), dtype=np.float32)
    out[0] = p

    n_az = 8
    max_400 = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    max_900 = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    min_900 = np.full((HEIGHT, WIDTH), 1e9, dtype=np.float32)
    best_az_idx = np.zeros((HEIGHT, WIDTH), dtype=np.uint8)
    max_1800 = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    min_1800 = np.full((HEIGHT, WIDTH), 1e9, dtype=np.float32)

    for m in range(n_az):
        phi = m * math.pi / n_az
        r4 = _oriented_gaussian_2d(p, phi, sigma_along=4.0, sigma_across=0.9)
        max_400 = np.maximum(max_400, r4)
        del r4

        r9 = _oriented_gaussian_2d(p, phi, sigma_along=9.0, sigma_across=1.1)
        better = r9 > max_900
        best_az_idx[better] = m
        max_900 = np.where(better, r9, max_900)
        min_900 = np.minimum(min_900, r9)
        del r9, better

        r18 = _oriented_gaussian_2d(p, phi, sigma_along=18.0, sigma_across=1.4)
        max_1800 = np.maximum(max_1800, r18)
        min_1800 = np.minimum(min_1800, r18)
        del r18

    out[1] = max_400
    out[2] = max_900
    out[3] = max_1800
    out[4] = (max_900 - min_900) / (max_900 + np.float32(1e-4))
    out[5] = (max_1800 - min_1800) / (max_1800 + np.float32(1e-4))
    del max_400, min_900, min_1800

    # Transverse crest sharpness & Two-Sided Alluvial-Gap Tip-Bridge along dominant strike phi*
    crest_sharp = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    bridge_600 = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    bridge_1100 = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    p_sm = gaussian_filter(p, sigma=1.2).astype(np.float32)

    for m in range(n_az):
        mask_m = (best_az_idx == m) & foot
        if not np.any(mask_m):
            continue
        phi = m * math.pi / n_az
        dx_a = math.cos(phi)
        dy_a = math.sin(phi)
        # Normal perpendicular to strike
        dx_n = -dy_a
        dy_n = dx_a

        # Transverse crest excess at +-2.5 px perpendicular to strike
        p_n1 = shift(p_sm, shift=(2.5 * dy_n, 2.5 * dx_n), order=1, mode="nearest")
        p_n2 = shift(p_sm, shift=(-2.5 * dy_n, -2.5 * dx_n), order=1, mode="nearest")
        crest_sharp[mask_m] = p[mask_m] - np.float32(0.5) * (p_n1[mask_m] + p_n2[mask_m])
        del p_n1, p_n2

        # Two-sided strike-bridge across 600 m (+-6 px) and 1,100 m (+-11 px) alluvial fan gaps
        p_f6 = shift(max_900, shift=(6.0 * dy_a, 6.0 * dx_a), order=1, mode="nearest")
        p_b6 = shift(max_900, shift=(-6.0 * dy_a, -6.0 * dx_a), order=1, mode="nearest")
        bridge_600[mask_m] = np.minimum(p_f6[mask_m], p_b6[mask_m])
        del p_f6, p_b6

        p_f11 = shift(max_1800, shift=(11.0 * dy_a, 11.0 * dx_a), order=1, mode="nearest")
        p_b11 = shift(max_1800, shift=(-11.0 * dy_a, -11.0 * dx_a), order=1, mode="nearest")
        bridge_1100[mask_m] = np.minimum(p_f11[mask_m], p_b11[mask_m])
        del p_f11, p_b11

    out[6] = crest_sharp
    out[7] = bridge_600
    out[8] = bridge_1100
    bg_3km = gaussian_filter(p, sigma=28.0).astype(np.float32)
    out[9] = p - bg_3km
    del crest_sharp, bridge_600, bridge_1100, bg_3km, p_sm, max_900, max_1800, best_az_idx

    # Physical tectonic & mimic moderators (strictly label-free)
    out[10] = ext_mm[2]   # mag_tdx_contact_crest
    out[11] = ext_mm[4]   # grav_tdx_contact_crest
    out[12] = ext_mm[11]  # dem10_scarp_breakline_index
    out[13] = ext_mm[14]  # fluvial10_knick_strike_bridge_1200m
    out[14] = ext_mm[16]  # lahontan_dixie_shoreline_mimic
    out[15] = ext_mm[17]  # pluton_core_nonq_mimic
    out[16] = base_mm[14] # depth_to_base_surf
    out[17] = base_mm[51] # c_hmas_composite
    return out


def fit_td_ksck_two_stage_oof(
    base_stack_path: Path,
    ext_stack_path: Path,
    grid: G57.Grid,
    lidar_valid: np.ndarray,
    cdir: Path,
    *,
    force: bool = False,
    log=print,
) -> dict[str, np.ndarray]:
    """Fit leak-free Stage-1 (`76ch` Full / `70ch` Sub) + Stage-2 (`18ch` Structural-Network) OOF surfaces."""
    cache_npz = cdir / "karage1_td_ksck_oof_v1.npz"
    if not force and cache_npz.is_file():
        log(f"[td_ksck] Reusing cached Two-Stage OOF surfaces at {cache_npz}")
        data = np.load(cache_npz)
        return {k: data[k] for k in data.files}

    foot = grid.footprint
    labels = grid.catalogue
    base_mm = open_memmap(base_stack_path, mode="r")
    ext_mm = open_memmap(ext_stack_path, mode="r")
    h, w = HEIGHT, WIDTH

    # Stage-1 folds (15 px = 1.5 km collar) & Stage-2 folds (36 px = 3.6 km collar >= 15 + 21 px kernel support)
    folds_q, collars_s1_q = quadrant_folds_with_collar(foot, buffer_px=15.0)
    _, collars_s2_q = quadrant_folds_with_collar(foot, buffer_px=36.0)

    yy_idx, xx_idx = np.nonzero(foot)
    u_coord = (yy_idx - float(yy_idx.mean())) + (xx_idx - float(xx_idx.mean()))
    v_coord = (yy_idx - float(yy_idx.mean())) - (xx_idx - float(xx_idx.mean()))
    um, vm = float(np.median(u_coord)), float(np.median(v_coord))
    diag_folds, diag_collars_s1, diag_collars_s2 = [], [], []
    for su in (False, True):
        for sv in (False, True):
            fm = np.zeros((h, w), dtype=bool)
            fm[yy_idx, xx_idx] = ((u_coord >= um) if su else (u_coord < um)) & ((v_coord >= vm) if sv else (v_coord < vm))
            diag_folds.append(fm)
            edt_fm = distance_transform_edt(~fm)
            diag_collars_s1.append(edt_fm <= 15.0)
            diag_collars_s2.append(edt_fm <= 36.0)

    # Mask union of ALL withheld segments across both `gems57-pooled-hide-v2` and `HIDE-RECOVER-v3.0`
    any_hidden = np.zeros((h, w), dtype=bool)
    ctx57 = H57.build_holdout(grid, seeds=(20, 21), modes=("all", "detached"))
    for hid_m in ctx57.hidden_by_cell.values():
        any_hidden |= hid_m
    for d in build_hr3_draws(foot, labels, seeds=(101, 202)):
        any_hidden |= d["hidden"]

    hidden_buf_s1 = binary_dilation(any_hidden, iterations=4)
    # Stage-2 excludes 19 px (1.9 km) around every hidden holdout segment so even 1.8 km line integrals never touch hidden truth
    hidden_buf_s2 = binary_dilation(any_hidden, iterations=19)

    d_lbl_vis = distance_transform_edt(~(labels & ~any_hidden))
    safe_pos_s1 = labels & ~hidden_buf_s1 & foot
    safe_neg_s1 = foot & ~labels & ~hidden_buf_s1 & (d_lbl_vis > 3.0)
    safe_pos_s2 = labels & ~hidden_buf_s2 & foot
    safe_neg_s2 = foot & ~labels & ~hidden_buf_s2 & (d_lbl_vis > 3.0)

    # Drop dead-zero ch 36 (`neg_tmi_tc`) from base stack; append all 19 100%-coverage TD-KSCK channels
    base_full_keep = [i for i in range(len(ALL_CHANNELS)) if i != 36]
    base_sub_keep = [i for i in MSUB_INDICES if i != 36]
    ext_all = list(range(len(TD_KSCK_CHANNELS)))

    lgb_s1_params = dict(
        n_estimators=290,
        learning_rate=0.05,
        num_leaves=51,
        min_child_samples=80,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.72,
        reg_alpha=1.5,
        reg_lambda=4.5,
        n_jobs=2,
        random_state=20261028,
        verbose=-1,
    )

    def _gather_combo(ys: np.ndarray, xs: np.ndarray, b_cols: list[int], e_cols: list[int]) -> np.ndarray:
        X = np.empty((ys.size, len(b_cols) + len(e_cols)), dtype=np.float32)
        for j, ch in enumerate(b_cols):
            X[:, j] = base_mm[ch, ys, xs]
        off = len(b_cols)
        for j, ch in enumerate(e_cols):
            X[:, off + j] = ext_mm[ch, ys, xs]
        return X

    def _sample_s1(train_dom: np.ndarray, b_cols: list[int], e_cols: list[int], seed_i: int) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(seed_i)
        p_flat = np.flatnonzero(safe_pos_s1 & train_dom)
        n_flat = np.flatnonzero(safe_neg_s1 & train_dom)
        if p_flat.size > 48_000:
            p_flat = rng.choice(p_flat, size=48_000, replace=False)
        n_keep = min(n_flat.size, max(p_flat.size * 4, 96_000))
        n_flat = rng.choice(n_flat, size=n_keep, replace=False)
        all_f = np.concatenate([p_flat, n_flat])
        y = np.concatenate([np.ones(p_flat.size, dtype=np.int32), np.zeros(n_flat.size, dtype=np.int32)])
        ys, xs = all_f // w, all_f % w
        return _gather_combo(ys, xs, b_cols, e_cols), y

    def _predict_s1(clf: lgb.LGBMClassifier, dom: np.ndarray, b_cols: list[int], e_cols: list[int]) -> np.ndarray:
        flat = np.flatnonzero(dom)
        ys, xs = flat // w, flat % w
        out = np.zeros(flat.size, dtype=np.float32)
        chunk = 250_000
        for s in range(0, flat.size, chunk):
            Xc = _gather_combo(ys[s : s + chunk], xs[s : s + chunk], b_cols, e_cols)
            out[s : s + chunk] = clf.predict_proba(Xc)[:, 1].astype(np.float32)
        return out

    def _run_stage1_scheme(scheme_name: str, folds_list: list[np.ndarray], collars_list: list[np.ndarray], seed_base: int) -> np.ndarray:
        p_out = np.zeros((h, w), dtype=np.float32)
        for q in range(4):
            tr_dom = foot & ~collars_list[q]
            te_dom = folds_list[q]
            log(f"[td_ksck] Stage-1 {scheme_name} fold {q}/3 (76ch Full / 70ch 10m-Sub)...")
            Xf, yf = _sample_s1(tr_dom & lidar_valid, base_full_keep, ext_all, seed_base + 10 * q)
            clf_full = lgb.LGBMClassifier(**lgb_s1_params)
            clf_full.fit(Xf, yf)
            del Xf, yf

            Xs, ys_l = _sample_s1(tr_dom, base_sub_keep, ext_all, seed_base + 10 * q + 1)
            clf_sub = lgb.LGBMClassifier(**lgb_s1_params)
            clf_sub.fit(Xs, ys_l)
            del Xs, ys_l

            rng_cal = np.random.default_rng(seed_base + 10 * q + 2)
            cal_flat = rng_cal.choice(np.flatnonzero(tr_dom & lidar_valid & safe_neg_s1), size=40_000, replace=False)
            c_ys, c_xs = cal_flat // w, cal_flat % w
            ref_cal = clf_full.predict_proba(_gather_combo(c_ys, c_xs, base_full_keep, ext_all))[:, 1].astype(np.float32)
            sub_cal = clf_sub.predict_proba(_gather_combo(c_ys, c_xs, base_sub_keep, ext_all))[:, 1].astype(np.float32)

            te_lid = te_dom & lidar_valid
            te_gap = te_dom & ~lidar_valid
            if np.any(te_lid):
                pf = _predict_s1(clf_full, te_lid, base_full_keep, ext_all)
                ps = _quantile_match_to_ref(_predict_s1(clf_sub, te_lid, base_sub_keep, ext_all), ref_cal, sub_cal)
                # 10m 3DEP + fluvial chi gives M_Sub stronger blind/piedmont fidelity -> 0.68 / 0.32 blend
                p_out[te_lid] = np.float32(0.68) * pf + np.float32(0.32) * ps
            if np.any(te_gap):
                p_out[te_gap] = _quantile_match_to_ref(_predict_s1(clf_sub, te_gap, base_sub_keep, ext_all), ref_cal, sub_cal)

            del clf_full, clf_sub
            gc.collect()
        return p_out

    p_s1_quad = _run_stage1_scheme("Quadrant", folds_q, collars_s1_q, seed_base=1100)
    p_s1_diag = _run_stage1_scheme("Diagonal", diag_folds, diag_collars_s1, seed_base=1200)
    p_s1_prod = (np.float32(0.5) * p_s1_quad + np.float32(0.5) * p_s1_diag).astype(np.float32)

    # Stage-2 Anisotropic Structural-Network Continuation OOF (36 px fold collars + 19 px hidden-fault buffer)
    lgb_s2_params = dict(
        n_estimators=190,
        learning_rate=0.045,
        num_leaves=31,
        min_child_samples=120,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.85,
        reg_alpha=2.5,
        reg_lambda=6.0,
        n_jobs=2,
        random_state=20261028,
        verbose=-1,
    )

    def _run_stage2_scheme(scheme_name: str, p_s1_in: np.ndarray, folds_list: list[np.ndarray], collars_s2_list: list[np.ndarray], seed_base: int) -> np.ndarray:
        log(f"[td_ksck] Extracting 18-channel Stage-2 structural-network features ({scheme_name})...")
        s2_feats = _extract_stage2_network_features(p_s1_in, base_mm, ext_mm, foot)
        p_s2_out = np.zeros((h, w), dtype=np.float32)
        for q in range(4):
            tr_dom = foot & ~collars_s2_list[q]
            te_dom = folds_list[q]
            rng = np.random.default_rng(seed_base + q)
            p_flat = np.flatnonzero(safe_pos_s2 & tr_dom)
            n_flat = np.flatnonzero(safe_neg_s2 & tr_dom)
            if p_flat.size > 40_000:
                p_flat = rng.choice(p_flat, size=40_000, replace=False)
            n_keep = min(n_flat.size, max(p_flat.size * 4, 90_000))
            n_flat = rng.choice(n_flat, size=n_keep, replace=False)
            all_f = np.concatenate([p_flat, n_flat])
            y = np.concatenate([np.ones(p_flat.size, dtype=np.int32), np.zeros(n_flat.size, dtype=np.int32)])
            ys, xs = all_f // w, all_f % w
            X = s2_feats[:, ys, xs].T.copy()

            clf_s2 = lgb.LGBMClassifier(**lgb_s2_params)
            clf_s2.fit(X, y)
            del X, y

            te_flat = np.flatnonzero(te_dom)
            tys, txs = te_flat // w, te_flat % w
            preds = np.zeros(te_flat.size, dtype=np.float32)
            chunk = 300_000
            for s in range(0, te_flat.size, chunk):
                Xc = s2_feats[:, tys[s : s + chunk], txs[s : s + chunk]].T.copy()
                preds[s : s + chunk] = clf_s2.predict_proba(Xc)[:, 1].astype(np.float32)
            p_s2_out[te_dom] = preds
            del clf_s2, preds
            gc.collect()
        del s2_feats
        gc.collect()
        return p_s2_out

    p_s2_quad = _run_stage2_scheme("Quadrant", p_s1_quad, folds_q, collars_s2_q, seed_base=2100)
    p_s2_diag = _run_stage2_scheme("Diagonal", p_s1_diag, diag_folds, diag_collars_s2, seed_base=2200)
    p_s2_prod = (np.float32(0.5) * p_s2_quad + np.float32(0.5) * p_s2_diag).astype(np.float32)

    # Label-free Cenozoic Piedmont & Hydrothermal Habitat Weight (for EXP3_TD_KSCK_PIED_OPT)
    # Suppresses un-sedimented Mesozoic pluton interiors; boosts piedmont/basin-margin hydrothermal & knickzone corridors
    pluton_m = ext_mm[17].astype(np.float32, copy=True)
    lahontan_m = ext_mm[16].astype(np.float32, copy=True)
    depth_b = np.maximum(base_mm[14].astype(np.float32, copy=True), 0.0)
    knick_br = ext_mm[14].astype(np.float32, copy=True)
    mag_tdx = ext_mm[2].astype(np.float32, copy=True)
    grav_tdx = ext_mm[4].astype(np.float32, copy=True)
    c_hmas = np.maximum(base_mm[51].astype(np.float32, copy=True), 0.0)

    kn_p95 = float(np.percentile(knick_br[foot][::16], 95)) + 1e-5
    tdx_p90 = float(np.percentile((mag_tdx + grav_tdx)[foot][::16], 90)) + 1e-5
    hm_p95 = float(np.percentile(c_hmas[foot][::16], 95)) + 1e-5

    basin_pied_gate = (1.0 / (1.0 + np.exp(-(depth_b - np.float32(95.0)) / np.float32(55.0)))).astype(np.float32)
    active_corridor = np.clip(
        np.float32(0.40) * basin_pied_gate
        + np.float32(0.25) * np.tanh(knick_br / np.float32(kn_p95))
        + np.float32(0.20) * np.tanh((mag_tdx + grav_tdx) / np.float32(tdx_p90))
        + np.float32(0.15) * np.tanh(c_hmas / np.float32(hm_p95)),
        0.0,
        1.0,
    ).astype(np.float32)
    pied_habitat_w = (
        (np.float32(0.84) + np.float32(0.30) * active_corridor)
        * (np.float32(1.0) - np.float32(0.30) * np.clip(pluton_m, 0.0, 1.0))
        * (np.float32(1.0) - np.float32(0.20) * np.clip(lahontan_m, 0.0, 1.0))
    ).astype(np.float32)
    pied_habitat_w = np.where(foot, pied_habitat_w, 0.0).astype(np.float32)

    np.savez_compressed(
        cache_npz,
        p_s1_quad=p_s1_quad,
        p_s1_prod=p_s1_prod,
        p_s2_quad=p_s2_quad,
        p_s2_prod=p_s2_prod,
        pied_habitat_w=pied_habitat_w,
    )
    log(f"[td_ksck] Saved Two-Stage TD-KSCK OOF surfaces -> {cache_npz}")
    return {
        "p_s1_quad": p_s1_quad,
        "p_s1_prod": p_s1_prod,
        "p_s2_quad": p_s2_quad,
        "p_s2_prod": p_s2_prod,
        "pied_habitat_w": pied_habitat_w,
    }


def build_piedmont_conduit_envelope(
    base_stack_path: Path,
    ext_stack_path: Path,
    p_ref: np.ndarray,
    foot: np.ndarray,
) -> tuple[np.ndarray, np.ndarray]:
    """Build strictly label-free Cenozoic Piedmont Habitat Weight + Physical Conduit Crest Envelope (`H-K1-S2-4`)."""
    base_mm = open_memmap(base_stack_path, mode="r")
    ext_mm = open_memmap(ext_stack_path, mode="r")

    def _pnorm(arr: np.ndarray, q: float = 95.0) -> np.ndarray:
        a = np.maximum(arr.astype(np.float32, copy=False), 0.0)
        sc = float(np.percentile(a[foot][::16], q)) + 1e-6
        return np.tanh(a / np.float32(sc)).astype(np.float32)

    neg_slot = _pnorm(ext_mm[0], 96.0)
    mag_tdx = _pnorm(ext_mm[2], 94.0)
    grav_tdx = _pnorm(ext_mm[4], 94.0)
    slp10 = ext_mm[6].astype(np.float32, copy=True)
    rel10 = ext_mm[10].astype(np.float32, copy=True)
    scarp10 = _pnorm(ext_mm[11], 95.0)
    knick_br = _pnorm(ext_mm[14], 96.0)
    lahontan_m = np.clip(ext_mm[16].astype(np.float32, copy=True), 0.0, 1.5)
    pluton_m = np.clip(ext_mm[17].astype(np.float32, copy=True), 0.0, 1.5)
    junc_inv = _pnorm(ext_mm[18], 95.0)

    depth_b = np.maximum(base_mm[14].astype(np.float32, copy=True), 0.0)
    grav_pers = _pnorm(base_mm[38], 94.0)
    bench_inf = _pnorm(base_mm[41], 94.0)
    c_hmas = _pnorm(base_mm[51], 95.0)

    # Cenozoic piedmont & intrabasin habitat gate: depth >= 160 m, low-to-moderate local 10m relief/slope
    deep_pied_gate = (
        (1.0 / (1.0 + np.exp(-(depth_b - np.float32(185.0)) / np.float32(55.0))))
        * (1.0 / (1.0 + np.exp((rel10 - np.float32(28.0)) / np.float32(8.0))))
        * (1.0 / (1.0 + np.exp((slp10 - np.float32(16.5)) / np.float32(4.0))))
    ).astype(np.float32)

    # Require multi-physics axial crest concordance in piedmont/basin (suppresses uniform basin blobs & shorelines)
    subsurf_crest = (
        np.float32(0.30) * grav_tdx
        + np.float32(0.22) * grav_pers
        + np.float32(0.20) * mag_tdx
        + np.float32(0.14) * bench_inf
        + np.float32(0.14) * neg_slot
    )
    tect_geomorph = (
        np.float32(0.36) * scarp10
        + np.float32(0.34) * knick_br
        + np.float32(0.16) * c_hmas
        + np.float32(0.14) * junc_inv
    )
    raw_conduit = (
        deep_pied_gate
        * np.sqrt(np.maximum(subsurf_crest * (np.float32(0.25) + np.float32(0.75) * tect_geomorph), 0.0))
        * (np.float32(1.0) - np.float32(0.55) * np.clip(lahontan_m, 0.0, 1.0))
        * (np.float32(1.0) - np.float32(0.75) * np.clip(pluton_m, 0.0, 1.0))
    ).astype(np.float32)
    raw_conduit = sharpen_axial_crest(raw_conduit, foot, crest_boost=0.42)

    rng = np.random.default_rng(20261028)
    fp_idx = rng.choice(np.flatnonzero(foot), size=160_000, replace=False)
    fy, fx = fp_idx // WIDTH, fp_idx % WIDTH
    pied_env_cal = np.zeros((HEIGHT, WIDTH), dtype=np.float32)
    pied_env_cal[foot] = _quantile_match_to_ref(raw_conduit[foot], p_ref[fy, fx], raw_conduit[fy, fx])

    pied_hab_w = (
        (np.float32(0.86) + np.float32(0.24) * deep_pied_gate)
        * (np.float32(1.0) - np.float32(0.26) * np.clip(pluton_m, 0.0, 1.0))
        * (np.float32(1.0) - np.float32(0.22) * np.clip(lahontan_m, 0.0, 1.0))
    ).astype(np.float32)
    pied_hab_w = np.where(foot, pied_hab_w, 0.0).astype(np.float32)
    return pied_hab_w, pied_env_cal


def compose_td_ksck_arm(
    arm_id: str,
    p_s1: np.ndarray,
    p_s2: np.ndarray,
    pied_habitat_w: np.ndarray,
    foot: np.ndarray,
    pied_conduit_env: np.ndarray | None = None,
) -> tuple[np.ndarray, float, float]:
    """Return `(belief_surface, min_sep_px, b_collar_px)` for the 3 pre-registered `TD-KSCK` experiments."""
    if arm_id == "EXP1_TD_10M_STAGE1":
        s = sharpen_axial_crest(p_s1, foot, crest_boost=0.18)
        return np.where(foot, s, np.float32(0.0)).astype(np.float32), 3.0, 2.2
    if arm_id == "EXP2_TD_KSCK_STAGE2":
        blend = np.float32(0.55) * p_s1 + np.float32(0.45) * p_s2
        s = sharpen_axial_crest(blend, foot, crest_boost=0.22)
        return np.where(foot, s, np.float32(0.0)).astype(np.float32), 3.0, 2.2
    if arm_id == "EXP3_TD_KSCK_PIED_OPT":
        sup = (np.float32(0.60) * p_s1 + np.float32(0.40) * p_s2) * pied_habitat_w
        if pied_conduit_env is not None:
            sup = np.maximum(sup, np.float32(0.36) * pied_conduit_env)
        s = sharpen_axial_crest(sup, foot, crest_boost=0.26)
        return np.where(foot, s, np.float32(0.0)).astype(np.float32), 3.18, 2.2
    raise ValueError(f"Unknown TD-KSCK arm_id: {arm_id}")


def load_c_pied_mask(ddir: Path, foot: np.ndarray, labels: np.ndarray) -> np.ndarray:
    """Exact verbatim `Instrument C_pied` (`n=9,949`, Spearman rho = +0.8667 across 22 live submissions)."""
    with rasterio.open(ddir / "external" / "derived_sgmc_faults_100m_u8.tif") as ds_s:
        sgmc = (ds_s.read(1) > 0) & foot
    with rasterio.open(ddir / "external" / "topo_10m_derived_100m_u8.tif") as ds_t:
        slp_u8 = ds_t.read(1)
        rel_u8 = ds_t.read(5)
    with rasterio.open(ddir / "training_features.tif") as ds_f:
        b15 = ds_f.read(15)
    depth_m = np.where(foot & np.isfinite(b15) & (b15 > -1e30), b15, 0.0).astype(np.float32)

    cat_fp = labels & foot
    rel10_p75_cat = float(np.percentile(rel_u8[cat_fp], 75))
    slp10_p80_cat = float(np.percentile(slp_u8[cat_fp], 80))
    d_cat = distance_transform_edt(~labels)

    c_pied = (
        sgmc
        & (~labels)
        & (d_cat > 2.5)
        & (rel_u8 <= rel10_p75_cat)
        & (slp_u8 <= slp10_p80_cat)
        & (depth_m >= 250.0)
    )
    return c_pied


def evaluate_c_pied_instrument(
    pred: np.ndarray,
    foot: np.ndarray,
    labels: np.ndarray,
    c_pied_mask: np.ndarray,
    ref_blocks: tuple[np.ndarray, np.ndarray, np.ndarray] | None = None,
) -> tuple[dict, tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """Evaluate off-catalogue Cenozoic piedmont SGMC faults (`GEMSDOE70-C-PIED-v1.0`, n=9,949)."""
    d_lbl = distance_transform_edt(~labels)
    eval_mask = foot & (d_lbl > 3.0)
    blk = _block_ids_256(foot.shape)
    raw_dti, tp_b, fp_b, fn_b = _pooled_dti_blocks(pred, c_pied_mask, eval_mask, blk, n_blocks=256)
    boot = _bootstrap_ci_and_delta(
        tp_b,
        fp_b,
        fn_b,
        *(ref_blocks if ref_blocks is not None else (None, None, None)),
    )
    res = {
        "evidence_class": "HOLDOUT-DTI",
        "evaluator_version": "GEMSDOE70-C-PIED-v1.0",
        "withheld_positives": int((c_pied_mask & eval_mask).sum()),
        "c_pied_pooled_dti": round(raw_dti, 6),
        "c_pied_ci95": boot["ci95"],
    }
    if "delta_vs_ref_ci95" in boot:
        res["delta_vs_champion"] = boot["delta_vs_ref_mean"]
        res["delta_vs_champion_ci95"] = boot["delta_vs_ref_ci95"]
        res["prob_beats_champion"] = boot["prob_beats_ref"]
    return res, (tp_b, fp_b, fn_b)
