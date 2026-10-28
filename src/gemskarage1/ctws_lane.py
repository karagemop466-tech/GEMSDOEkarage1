"""CTWS-2D lane: Crustal Tilt-Worm Zero-Crossing, 3DEP 10 m Piedmont-Toe / Chi-Knickpoint,
and Fold-Safe Crack-Tip Relay 2-D Spatial-Context Submodular Network.

Fixes irregularities IR-KARAGE1-01..03 (true embedded band mappings for training_features.tif,
geodawn_extensions_u8.tif, and lidar_scarp_features_u8.tif) and integrates:
  - H-K1-2A (PTZW): Multi-depth Verduzco potential-field tilt-angle zero-crossing worms,
    cover-thickness throw gradients (B15 depth_to_base_surf), and MT conductivity boundaries (B17).
  - H-K1-2B (PTCF-CHI): Full-footprint USGS 3DEP 10 m subgrid geomorphology, piedmont-toe concave
    flexure, Perron-Royden drainage chi-knickpoints, and 1 m LiDAR antislope graben scarps.
  - H-K1-2C (ACTR-2D): Catalogue-free 8-azimuth 2-D multi-scale lineament context pyramid (EXP2)
    plus strictly fold-visible crack-tip propagation cones, opposing-tip gap bridges, and
    two-host en-echelon relay-ramp superposition (EXP3, reusing vendor/gems57/relay_bend_anatomy.py).
  - H-K1-2D (EPITH-BLM): BLM closed lode/epithermal vein corridor x K/Th x RTP demagnetization.
  - H-K1-2E (RADON-FLUX): Playa-detrended 222Rn -> 214Bi U/Th fracture degassing x INGENIOUS 2 m T.
"""
from __future__ import annotations

import csv
import gc
import io
import json
import math
from pathlib import Path
import sys
import zipfile

import lightgbm as lgb
import numpy as np
from numpy.lib.format import open_memmap
import rasterio
from scipy import ndimage as ndi
from scipy.ndimage import (
    binary_dilation,
    distance_transform_edt,
    gaussian_filter,
    maximum_filter,
)
from scipy.spatial import cKDTree
from skimage.morphology import skeletonize
from sklearn.metrics import roc_auc_score

REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (REPO_ROOT / "vendor", REPO_ROOT / "src"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from gems57 import evaluate_holdout as eh57  # noqa: E402
from gems57 import grid as G57  # noqa: E402
from gems57 import holdout as H57  # noqa: E402
from gems57.network import local_strike, segments as g57_segments  # noqa: E402
from gems57.relay_bend_anatomy import two_host_frame  # noqa: E402

from .emitter import emit_submodular_300m, sharpen_axial_crest  # noqa: E402
from .features import _rasterize_ingenious_geothermal_layers  # noqa: E402
from .holdout_eval import (  # noqa: E402
    _block_ids_256,
    _bootstrap_ci_and_delta,
    _pooled_dti_blocks,
    _quantile_match_to_ref,
    build_hr3_draws,
    quadrant_folds_with_collar,
)
from .paths import cache_dir, data_dir  # noqa: E402

# Verified official 19-band training_features.tif names (IR-KARAGE1-01 fix)
TF19_NAMES = [
    "tf_mag_anom",          # B01
    "tf_rtp",               # B02
    "tf_tmi_hg",            # B03
    "tf_geod_2ndinv",       # B04
    "tf_iso_grav_slope",    # B05
    "tf_tc",                # B06
    "tf_geod_shear",        # B07
    "tf_geod_dilate",       # B08
    "tf_tmi_vg",            # B09
    "tf_deq_dist",          # B10
    "tf_iso_grav_vg",       # B11
    "tf_det_elev",          # B12
    "tf_iso_grav",          # B13
    "tf_tmi",               # B14
    "tf_depth_basement",    # B15
    "tf_ieq_intens",        # B16
    "tf_cond_surf",         # B17
    "tf_iso_grav_hg",       # B18
    "tf_det_elev_slope",    # B19
]

# Verified GeoDAWN radiometric & extension channels (IR-KARAGE1-02 fix)
GD8_NAMES = [
    "gd_rad_K",
    "gd_rad_Th",
    "gd_rad_U",
    "gd_rad_TC",
    "gd_ext_ThK",
    "gd_ext_UK",
    "gd_ext_UTh",
    "gd_ext_TMI_up150",
]

# Newly integrated full-footprint USGS 3DEP 10 m geomorphology & Perron-Royden chi-knickpoints
DEM10_CHI_NAMES = [
    "dem10_slope_p90",
    "dem10_slope_max",
    "dem10_steep_frac",
    "dem10_slope_std",
    "dem10_relief_local",
    "dem10_curv_prof_absmax",
    "dem10_aspect_coherence",
    "dem10_hs_lineament",
    "dem10_elev_m",
    "chi_step_pos_300m",
    "chi_step_pos_800m",
    "chi_step_antithetic_400m",
    "chi_ksn_norm",
]

# Newly unlocked 12-band USGS 3DEP 1 m LiDAR scarp transforms (IR-KARAGE1-03 fix; quarantined to M_Full)
LIDAR13_NAMES = [
    "lidar_ex_max",
    "lidar_ex_mean",
    "lidar_step_max",
    "lidar_lapneg_max",
    "lidar_lappos_max",
    "lidar_downface_max",
    "lidar_upface_max",
    "lidar_cross_max",
    "lidar_coh100",
    "lidar_antislope_net",
    "lidar_scarp_hinge",
    "lidar_sin2_strike",
    "lidar_cos2_strike",
]

# Pre-registered geophysical, geomorphological & hydrothermal discovery operators (H-K1-2A/B/D/E)
DISCOVERY16_NAMES = [
    "ptzw_tmi_worm",
    "ptzw_rtp_worm_0m",
    "ptzw_rtp_worm_800m",
    "ptzw_grav_worm",
    "ptzw_joint_concordance",
    "basement_throw_grad",
    "mt_cond_grad",
    "hmas_rtp_trough",
    "ptcf_piedmont_hinge",
    "mimic_lahontan_crag_gate",
    "epith_blm_corridor",
    "radon_playa_detrended",
    "ing_f2mdab_plume",
    "ing_well_geotherm",
    "ing_sinter_vent_halo",
    "geodawn_block_id",
]

CTWS_STATIC_CHANNELS = (
    TF19_NAMES + GD8_NAMES + DEM10_CHI_NAMES + LIDAR13_NAMES + DISCOVERY16_NAMES
)  # 69 verified static channels

LIDAR_START = len(TF19_NAMES) + len(GD8_NAMES) + len(DEM10_CHI_NAMES)  # 40
CTWS_LIDAR_INDICES = list(range(LIDAR_START, LIDAR_START + len(LIDAR13_NAMES)))  # 40..52
CTWS_MSUB_INDICES = [i for i in range(len(CTWS_STATIC_CHANNELS)) if i not in CTWS_LIDAR_INDICES]

CTX2D_NAMES = [
    "ctx_p1_raw",
    "ctx_p1_g2",
    "ctx_p1_g6",
    "ctx_p1_g16",
    "ctx_p1_dog_2_8",
    "ctx_line_max_5",
    "ctx_line_orth_5",
    "ctx_line_max_13",
    "ctx_line_orth_13",
    "ctx_line_max_29",
    "ctx_line_orth_29",
    "ctx_multiscale_align",
    "ctx_worm_line_13",
    "ctx_ptcf_line_13",
    "ctx_chi_corridor",
    "ctx_cover_depth",
    "ctx_slope_10m",
    "ctx_mimic_gate",
]

STRUCTURAL_NAMES = [
    "st_d1_px",
    "st_d_perp",
    "st_d_par",
    "st_log_len1",
    "st_bend_turn",
    "st_relay_ratio",
    "st_d2_px",
    "st_relay_zone",
    "st_strike_align_p2",
    "st_phys_x_relay",
]


def _robust_z(arr: np.ndarray, foot: np.ndarray) -> np.ndarray:
    v = arr[foot][::8]
    v = v[np.isfinite(v)]
    if v.size == 0:
        return np.zeros_like(arr, dtype=np.float32)
    med = float(np.median(v))
    iqr = float(np.percentile(v, 75) - np.percentile(v, 25))
    scale = max(iqr / 1.349, 1e-6)
    z = np.clip((arr - med) / scale, -8.0, 8.0).astype(np.float32)
    z[~foot] = 0.0
    return z


def _grad_mag_and_spin2(arr: np.ndarray, sigma: float = 1.2) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    sm = gaussian_filter(arr.astype(np.float32), sigma=sigma) if sigma > 0 else arr.astype(np.float32)
    gy, gx = np.gradient(sm)
    mag = np.hypot(gx, gy).astype(np.float32)
    # Tangent orientation is perpendicular to gradient: tx = -gy, ty = gx
    # cos(2*psi) = (tx^2 - ty^2)/(tx^2+ty^2) = (gy^2 - gx^2)/mag^2
    # sin(2*psi) = 2*tx*ty/mag^2 = -2*gx*gy/mag^2
    denom = np.maximum(mag * mag, 1e-12)
    cos2 = ((gy * gy - gx * gx) / denom).astype(np.float32)
    sin2 = ((-2.0 * gx * gy) / denom).astype(np.float32)
    return mag, cos2, sin2


def _read_u8_scaled(path: Path, band_idx_1: int, foot: np.ndarray, lo: float = 0.0, hi: float = 1.0, mode: str = "linear") -> tuple[np.ndarray, np.ndarray]:
    with rasterio.open(path) as src:
        raw = src.read(band_idx_1)
    valid = (raw > 0) & foot
    q01 = np.zeros(raw.shape, dtype=np.float32)
    q01[valid] = np.clip((raw[valid].astype(np.float32) - 1.0) / 254.0, 0.0, 1.0)
    if mode == "sqrt":
        val = (q01 * q01) * float(hi)
    else:
        val = float(lo) + q01 * float(hi - lo)
    if np.any(valid) and not np.all(valid[foot]):
        med = float(np.median(val[valid][::8]))
        val[foot & ~valid] = med
    val[~foot] = 0.0
    return val.astype(np.float32), valid


def _world_to_rc(easting: np.ndarray, northing: np.ndarray, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    cols = np.floor((easting - 243350.0) / 100.0).astype(np.int32)
    rows = np.floor((4508550.0 - northing) / 100.0).astype(np.int32)
    ok = (rows >= 0) & (rows < shape[0]) & (cols >= 0) & (cols < shape[1])
    return rows[ok], cols[ok], ok


def build_ctws_static_stack(
    *,
    force: bool = False,
    log=print,
) -> tuple[Path, np.ndarray]:
    """Build or reuse the 69-channel leak-free CTWS-2D static memmap stack (< 750 MB RSS)."""
    ddir = data_dir()
    cdir = cache_dir()
    stack_path = cdir / "ctws_static_69ch_v1.npy"
    meta_path = cdir / "ctws_static_69ch_v1.meta.json"
    lidar_mask_path = cdir / "ctws_lidar_valid_v1.npy"

    if not force and stack_path.is_file() and meta_path.is_file() and lidar_mask_path.is_file():
        meta = json.loads(meta_path.read_text())
        if meta.get("channels") == CTWS_STATIC_CHANNELS:
            log(f"[ctws-features] Reusing cached 69-channel stack at {stack_path}")
            return stack_path, np.load(lidar_mask_path)

    with rasterio.open(ddir / "sample_submission.tif") as ds_s:
        foot = np.isfinite(ds_s.read(1))
        aff = ds_s.transform
        h, w = ds_s.height, ds_s.width

    n_ch = len(CTWS_STATIC_CHANNELS)
    log(f"[ctws-features] Building {n_ch}-channel stack ({h}x{w}) -> {stack_path}")
    mm = open_memmap(stack_path, mode="w+", dtype=np.float32, shape=(n_ch, h, w))

    # --- Group A: Verified 19-band training_features.tif (0..18) ---
    with rasterio.open(ddir / "training_features.tif") as src:
        assert src.count == 19, f"Expected 19 bands in training_features.tif, got {src.count}"
        for b in range(19):
            arr = src.read(b + 1).astype(np.float32)
            bad = (~np.isfinite(arr)) | (arr < -1e30)
            valid = foot & ~bad
            med = float(np.median(arr[valid][::8])) if np.any(valid) else 0.0
            arr[bad] = med
            arr[~foot] = 0.0
            mm[b] = arr
            del arr, bad, valid
    mm.flush()

    # --- Group B: GeoDAWN radiometric & extension grids (19..26) ---
    rad_p = ddir / "external" / "geodawn_rad_u8.tif"
    for b in range(4):
        val, _ = _read_u8_scaled(rad_p, b + 1, foot, 0.0, 1.0, "linear")
        mm[19 + b] = val
    ext_p = ddir / "external" / "geodawn_extensions_u8.tif"
    for b in range(4):
        val, _ = _read_u8_scaled(ext_p, b + 1, foot, 0.0, 1.0, "linear")
        mm[23 + b] = val
    mm.flush()

    # --- Group C: Full-footprint USGS 3DEP 10 m geomorphology & Perron-Royden chi-knickpoints (27..39) ---
    topo_manifest = json.loads((ddir / "external" / "topo_10m_derived_100m_u8.manifest.json").read_text())
    topo_p = ddir / "external" / "topo_10m_derived_100m_u8.tif"
    for b_info in topo_manifest["bands"]:
        bi = int(b_info["index"])  # 1..9
        val, _ = _read_u8_scaled(topo_p, bi, foot, float(b_info["lo"]), float(b_info["hi"]), "linear")
        mm[27 + (bi - 1)] = val

    chi_p = ddir / "external" / "dem10_chi_100m_i16.tif"
    with rasterio.open(chi_p) as src_chi:
        s_max = src_chi.read(1)
        s_min = src_chi.read(2)
        ksn = src_chi.read(3)
    ch_valid = (s_max > -32000) & foot
    step_pos = np.zeros((h, w), dtype=np.float32)
    step_pos[ch_valid] = np.maximum(s_max[ch_valid].astype(np.float32) / 1000.0, 0.0)
    step_neg = np.zeros((h, w), dtype=np.float32)
    step_neg[ch_valid & (s_min > -32000)] = np.maximum(-s_min[ch_valid & (s_min > -32000)].astype(np.float32) / 1000.0, 0.0)
    ksn_f = np.zeros((h, w), dtype=np.float32)
    ksn_valid = (ksn > -32000) & foot
    ksn_f[ksn_valid] = np.maximum(ksn[ksn_valid].astype(np.float32), 0.0)
    del s_max, s_min, ksn

    # Lateral Nadaraya-Watson / max-corridor propagation across interfluves
    ch_w3 = gaussian_filter(ch_valid.astype(np.float32), sigma=3.0)
    ch_w8 = gaussian_filter(ch_valid.astype(np.float32), sigma=8.0)
    ch_w4 = gaussian_filter(ch_valid.astype(np.float32), sigma=4.0)
    mm[36] = np.where(foot, gaussian_filter(step_pos, sigma=3.0) / np.maximum(ch_w3, 0.04), 0.0).astype(np.float32)
    mm[37] = np.where(foot, gaussian_filter(step_pos, sigma=8.0) / np.maximum(ch_w8, 0.04), 0.0).astype(np.float32)
    mm[38] = np.where(foot, gaussian_filter(step_neg, sigma=4.0) / np.maximum(ch_w4, 0.04), 0.0).astype(np.float32)
    mm[39] = np.where(foot, np.log1p(gaussian_filter(ksn_f, sigma=4.0) / np.maximum(ch_w4, 0.04)), 0.0).astype(np.float32)
    del step_pos, step_neg, ksn_f, ch_valid, ksn_valid, ch_w3, ch_w8, ch_w4
    mm.flush()

    # --- Group D: 12-band USGS 3DEP 1 m LiDAR scarp features (40..52, quarantined to lidar_valid) ---
    lid_json = json.loads((ddir / "external" / "lidar_scarp_features.json").read_text())
    lid_p = ddir / "external" / "lidar_scarp_features_u8.tif"
    q_spec = lid_json["quantisation"]
    # Bands: 1:ex_max, 2:ex_mean, 3:step_max, 4:lapneg_max, 5:lappos_max,
    #        6:downface_max, 7:upface_max, 8:cross_max, 9:relief, 10:coh100, 11:strike, 12:valid
    _, lid_valid_12 = _read_u8_scaled(lid_p, 12, foot, 0.0, 1.0, "linear")
    with rasterio.open(lid_p) as src_l:
        lidar_valid = (src_l.read(12) > 0) & foot
    np.save(lidar_mask_path, lidar_valid)
    del lid_valid_12

    lid_bands_keep = [
        (1, "ex_max"),
        (2, "ex_mean"),
        (3, "step_max"),
        (4, "lapneg_max"),
        (5, "lappos_max"),
        (6, "downface_max"),
        (7, "upface_max"),
        (8, "cross_max"),
        (10, "coh100"),
    ]
    lid_cache: dict[str, np.ndarray] = {}
    for offset, (b1, bname) in enumerate(lid_bands_keep):
        hi_v, q_mode = q_spec[bname]
        arr, _ = _read_u8_scaled(lid_p, b1, foot, 0.0, float(hi_v), str(q_mode))
        arr[~lidar_valid] = 0.0
        mm[40 + offset] = arr
        if bname in {"lapneg_max", "lappos_max", "upface_max", "cross_max", "coh100"}:
            lid_cache[bname] = arr

    strike_deg, _ = _read_u8_scaled(lid_p, 11, foot, 0.0, 180.0, "linear")
    coh = lid_cache["coh100"]
    mm[49] = np.where(lidar_valid, (lid_cache["upface_max"] - 0.65 * lid_cache["cross_max"]) * coh, 0.0).astype(np.float32)
    mm[50] = np.where(
        lidar_valid,
        np.sqrt(np.maximum(lid_cache["lapneg_max"] * lid_cache["lappos_max"], 0.0)) * coh / (1.0 + 2.0 * lid_cache["cross_max"]),
        0.0,
    ).astype(np.float32)
    rad2 = np.radians(2.0 * strike_deg)
    mm[51] = np.where(lidar_valid, coh * np.sin(rad2), 0.0).astype(np.float32)
    mm[52] = np.where(lidar_valid, coh * np.cos(rad2), 0.0).astype(np.float32)
    del lid_cache, strike_deg, coh, rad2
    mm.flush()

    # --- Group E: Novel Geophysical, Geomorphological & Hydrothermal Discovery Operators (53..68) ---
    # H1 (PTZW): Multi-depth Verduzco tilt-angle zero-crossing worms
    tmi_hg = np.maximum(mm[2].astype(np.float32), 1e-4)
    tmi_vg = mm[8].astype(np.float32)
    th_tmi = np.arctan2(tmi_vg, tmi_hg)
    s_tmi = float(np.percentile(tmi_hg[foot][::8], 75)) + 1e-4
    w_tmi = (np.exp(-np.abs(th_tmi) / 0.32) * np.tanh(tmi_hg / s_tmi)).astype(np.float32)
    w_tmi[~foot] = 0.0
    mm[53] = w_tmi
    del tmi_hg, tmi_vg, th_tmi

    rtp = mm[1].astype(np.float32, copy=True)
    # Surface RTP tilt worm via vertical continuation difference (dz ~ 200 m -> sigma_uc = 2 px)
    rtp_s1 = gaussian_filter(rtp, sigma=1.2)
    rtp_s3 = gaussian_filter(rtp, sigma=3.2)
    rtp_vdr0 = (rtp_s1 - rtp_s3) / 2.0
    rtp_hg0, rtp_cos2, rtp_sin2 = _grad_mag_and_spin2(rtp, sigma=1.4)
    s_rtp0 = float(np.percentile(rtp_hg0[foot][::8], 75)) + 1e-4
    w_rtp0 = (np.exp(-np.abs(np.arctan2(rtp_vdr0, np.maximum(rtp_hg0, 1e-4))) / 0.32) * np.tanh(rtp_hg0 / s_rtp0)).astype(np.float32)
    w_rtp0[~foot] = 0.0
    mm[54] = w_rtp0
    del rtp_s1, rtp_s3, rtp_vdr0, rtp_hg0

    # Deep 800 m upward-continued RTP tilt worm (sigma=8 vs sigma=14)
    rtp_s8 = gaussian_filter(rtp, sigma=8.0)
    rtp_s14 = gaussian_filter(rtp, sigma=14.0)
    rtp_vdr8 = (rtp_s8 - rtp_s14) / 6.0
    rtp_hg8, _, _ = _grad_mag_and_spin2(rtp_s8, sigma=1.0)
    s_rtp8 = float(np.percentile(rtp_hg8[foot][::8], 75)) + 1e-4
    w_rtp8 = (np.exp(-np.abs(np.arctan2(rtp_vdr8, np.maximum(rtp_hg8, 1e-4))) / 0.32) * np.tanh(rtp_hg8 / s_rtp8)).astype(np.float32)
    w_rtp8[~foot] = 0.0
    mm[55] = w_rtp8
    del rtp_s14, rtp_vdr8, rtp_hg8

    # Analytical Isostatic Gravity Verduzco Tilt-Zero Worm (B11 = iso_grav_vg, B05 = iso_grav_slope)
    grav_hg = np.maximum(mm[4].astype(np.float32), 1e-5)
    grav_vg = mm[10].astype(np.float32)
    s_grav = float(np.percentile(grav_hg[foot][::8], 75)) + 1e-5
    w_grav = (np.exp(-np.abs(np.arctan2(grav_vg, grav_hg)) / 0.34) * np.tanh(grav_hg / s_grav)).astype(np.float32)
    w_grav[~foot] = 0.0
    mm[56] = w_grav
    _, grav_cos2, grav_sin2 = _grad_mag_and_spin2(mm[12].astype(np.float32), sigma=2.0)
    align_mg = np.maximum(0.0, rtp_cos2 * grav_cos2 + rtp_sin2 * grav_sin2)
    mm[57] = np.where(foot, (0.45 * w_rtp0 + 0.55 * w_rtp8) * (0.35 + 0.65 * w_grav) * (0.4 + 0.6 * align_mg), 0.0).astype(np.float32)
    del grav_hg, grav_vg, w_tmi, w_rtp0, w_rtp8, w_grav, rtp_cos2, rtp_sin2, grav_cos2, grav_sin2, align_mg

    # Sedimentary cover basement-throw gradient (B15 depth_to_base_surf) & MT conductivity boundary (B17 cond_surf)
    base_grad, _, _ = _grad_mag_and_spin2(mm[14].astype(np.float32), sigma=1.5)
    mm[58] = _robust_z(np.log1p(base_grad), foot)
    del base_grad

    cond = mm[16].astype(np.float32, copy=True)
    cond_grad, _, _ = _grad_mag_and_spin2(cond, sigma=1.5)
    cond_ridge = cond - gaussian_filter(cond, sigma=10.0)
    mm[59] = _robust_z(0.6 * _robust_z(cond_grad, foot) + 0.4 * _robust_z(cond_ridge, foot), foot)
    del cond, cond_grad, cond_ridge

    # Corrected HMAS: True RTP magnetic-destruction trough coupled with K/Th potassic alteration
    rtp_trough = np.maximum(0.0, rtp_s8 - gaussian_filter(rtp, sigma=1.3))
    k_over_th = mm[19].astype(np.float32) / np.maximum(mm[20].astype(np.float32), 0.04)
    z_kth = _robust_z(k_over_th, foot)
    sig_kth = 1.0 / (1.0 + np.exp(-np.clip(z_kth, -6.0, 6.0)))
    mm[60] = _robust_z(np.log1p(rtp_trough) * (0.4 + 0.6 * sig_kth), foot)
    del rtp, rtp_s8, rtp_trough, k_over_th

    # H2 (PTCF): Piedmont-Toe Concave Flexure & Lake Lahontan / Crag / Road Mimic Gate
    s10 = mm[27].astype(np.float32, copy=True)          # dem10_slope_p90 (deg)
    rel10 = mm[31].astype(np.float32, copy=True)        # dem10_relief_local (m)
    curv10 = mm[32].astype(np.float32, copy=True)       # dem10_curv_prof_absmax
    acoh10 = mm[33].astype(np.float32, copy=True)       # dem10_aspect_coherence
    elev10 = mm[35].astype(np.float32, copy=True)       # dem10_elev_m (m ASL)

    upslope_relief = maximum_filter(gaussian_filter(rel10, sigma=2.5), size=15)
    piedmont_slope_bell = np.exp(-0.5 * ((s10 - 6.0) / 4.8) ** 2) * (s10 >= 1.0)
    ptcf = np.log1p(upslope_relief / 25.0) * piedmont_slope_bell * np.sqrt(np.maximum(curv10, 0.0)) * acoh10
    mm[61] = _robust_z(ptcf, foot)
    del upslope_relief, piedmont_slope_bell, ptcf

    with rasterio.open(ddir / "external" / "tiger_road_distance_m.tif") as src_rd:
        d_road = src_rd.read(1).astype(np.float32)
    d_road = np.where(np.isfinite(d_road), np.maximum(d_road, 0.0), 5000.0)
    road_prism = np.exp(-d_road / 150.0)
    del d_road
    lahontan_bench = np.exp(-0.5 * ((elev10 - 1334.0) / 14.0) ** 2) * (s10 < 9.0)
    steep_crag = np.clip((s10 - 22.0) / 12.0, 0.0, 1.5) * (1.0 - np.clip(mm[57].astype(np.float32) * 2.5, 0.0, 0.85))
    mm[62] = np.where(foot, 0.45 * lahontan_bench + 0.40 * steep_crag + 0.35 * road_prism, 0.0).astype(np.float32)
    del curv10, acoh10, rel10, elev10, road_prism, lahontan_bench, steep_crag

    # H4 (EPITH-BLM): BLM closed lode/epithermal claim corridor
    with rasterio.open(ddir / "external" / "blm_closed_claim_distance_m.tif") as src_blm:
        d_blm = src_blm.read(1).astype(np.float32)
    d_blm = np.where(np.isfinite(d_blm), np.maximum(d_blm, 0.0), 10000.0)
    blm_prox = np.exp(-d_blm / 1200.0).astype(np.float32)
    del d_blm
    playa_flat = (s10 < 0.85) & (mm[11].astype(np.float32) < -75.0)
    mm[63] = np.where(foot, blm_prox * (1.0 - 0.65 * playa_flat.astype(np.float32)) * (0.45 + 0.55 * sig_kth), 0.0).astype(np.float32)
    del blm_prox, sig_kth, z_kth

    # H5 (RADON-FLUX): Playa-detrended 222Rn -> 214Bi UTh fracture degassing + INGENIOUS 2 m T / Wells / Sinter
    z_uth = _robust_z(mm[25].astype(np.float32), foot)
    mm[64] = np.where(foot, z_uth - 0.75 * playa_flat.astype(np.float32), 0.0).astype(np.float32)
    del z_uth, playa_flat, s10

    # Reuse verified INGENIOUS GDR #1391 loader (2m T .dbf EPSG:4269, Paleo sinter CSV, thermal wells/geotherm)
    f2m_grid, paleo_grid, qtz_grid = _rasterize_ingenious_geothermal_layers(ddir, foot, aff)
    mm[65] = _robust_z(0.65 * gaussian_filter(f2m_grid, sigma=12.0) + 0.35 * gaussian_filter(f2m_grid, sigma=28.0), foot)
    mm[66] = _robust_z(np.log1p(0.65 * gaussian_filter(qtz_grid, sigma=12.0) + 0.35 * gaussian_filter(qtz_grid, sigma=26.0)), foot)
    del f2m_grid, qtz_grid

    sv_mask = paleo_grid > 0.0
    with (ddir / "external" / "gdr_volcanic_vents_in_footprint.csv").open("r", encoding="utf-8", errors="replace") as fh:
        for row in csv.DictReader(fh):
            try:
                if row.get("row") and row.get("col"):
                    ri, ci = int(float(row["row"])), int(float(row["col"]))
                    if 0 <= ri < h and 0 <= ci < w and foot[ri, ci]:
                        sv_mask[ri, ci] = True
            except ValueError:
                continue
    if np.any(sv_mask):
        d_sv = distance_transform_edt(~sv_mask).astype(np.float32)
        mm[67] = np.where(foot, 0.65 * np.exp(-d_sv / 32.0) + 0.35 * gaussian_filter(paleo_grid, sigma=14.0), 0.0).astype(np.float32)
        del d_sv
    else:
        mm[67] = 0.0
    del sv_mask, paleo_grid

    # GeoDAWN acquisition survey block control (1..4)
    with rasterio.open(ddir / "external" / "acquisition_block_id_100m.tif") as src_blk:
        blk_id = src_blk.read(1).astype(np.float32)
    blk_id[~foot] = 0.0
    mm[68] = blk_id
    del blk_id

    mm.flush()
    del mm
    gc.collect()

    meta_path.write_text(
        json.dumps(
            {
                "schema": "ctws_static_69ch_v1",
                "n_channels": len(CTWS_STATIC_CHANNELS),
                "channels": CTWS_STATIC_CHANNELS,
                "lidar_indices": CTWS_LIDAR_INDICES,
                "msub_indices": CTWS_MSUB_INDICES,
            },
            indent=2,
        )
        + "\n"
    )
    return stack_path, lidar_valid


# --- Stage-2 2-D Multi-Scale Anisotropic Lineament Context Pyramid (Catalogue-Free) ---

def _directional_line_stats(field: np.ndarray, foot: np.ndarray, length_px: int, pre_sigma: float = 0.0) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """8-azimuth line-integral mean, orthogonal ridge contrast, and spin-2 best azimuth."""
    src = gaussian_filter(field.astype(np.float32), sigma=pre_sigma) if pre_sigma > 0 else field.astype(np.float32)
    src = np.where(foot, src, 0.0)
    w_foot = gaussian_filter(foot.astype(np.float32), sigma=max(pre_sigma, 0.5)) if pre_sigma > 0 else foot.astype(np.float32)
    h, w = src.shape
    half = length_px // 2
    if length_px <= 7:
        steps = np.linspace(-half, half, 5)
    elif length_px <= 15:
        steps = np.linspace(-half, half, 7)
    else:
        steps = np.linspace(-half, half, 9)

    pad = half + 1
    p_src = np.pad(src, pad, mode="constant", constant_values=0.0)
    p_wt = np.pad(w_foot, pad, mode="constant", constant_values=0.0)

    mus = np.empty((8, h, w), dtype=np.float32)
    for k in range(8):
        ang = k * (math.pi / 8.0)  # azimuth in (y, x): dx = cos(ang), dy = sin(ang)
        dy_f = math.sin(ang)
        dx_f = math.cos(ang)
        acc = np.zeros((h, w), dtype=np.float32)
        wsum = np.zeros((h, w), dtype=np.float32)
        for s in steps:
            dy = int(round(s * dy_f))
            dx = int(round(s * dx_f))
            y0, x0 = pad + dy, pad + dx
            acc += p_src[y0 : y0 + h, x0 : x0 + w]
            wsum += p_wt[y0 : y0 + h, x0 : x0 + w]
        mus[k] = np.where(foot, acc / np.maximum(wsum, 1e-4), 0.0)

    line_max = mus.max(axis=0)
    orth_diff = np.empty_like(mus)
    for k in range(8):
        orth_diff[k] = mus[k] - mus[(k + 4) % 8]
    best_k = np.argmax(orth_diff, axis=0)
    line_orth = np.take_along_axis(orth_diff, best_k[None, :, :], axis=0)[0]

    # Convert best_k to standard strike convention matching gems57.network.local_strike:
    # local_strike returns degrees in [0, 180) clockwise from North (or standard image x/y);
    # let's check: here dx = cos(ang), dy = sin(ang) in image (row=y, col=x).
    best_ang = best_k.astype(np.float32) * np.float32(math.pi / 8.0)
    cos2 = np.where(foot, np.cos(2.0 * best_ang), 0.0).astype(np.float32)
    sin2 = np.where(foot, np.sin(2.0 * best_ang), 0.0).astype(np.float32)
    del mus, orth_diff, p_src, p_wt
    return line_max, line_orth, cos2, sin2


def build_ctx2d_memmap(
    p1_surface: np.ndarray,
    static_stack_path: Path,
    foot: np.ndarray,
    out_path: Path,
) -> tuple[Path, np.ndarray, np.ndarray]:
    """Compute 18-channel 2-D multi-scale anisotropic lineament context stack on disk."""
    h, w = foot.shape
    mm_s = open_memmap(static_stack_path, mode="r")
    mm_c = open_memmap(out_path, mode="w+", dtype=np.float32, shape=(len(CTX2D_NAMES), h, w))

    p1 = np.where(foot, p1_surface.astype(np.float32), 0.0)
    g2 = gaussian_filter(p1, sigma=2.0)
    g6 = gaussian_filter(p1, sigma=6.0)
    g8 = gaussian_filter(p1, sigma=8.0)
    g16 = gaussian_filter(p1, sigma=16.0)

    mm_c[0] = p1
    mm_c[1] = np.where(foot, g2, 0.0)
    mm_c[2] = np.where(foot, g6, 0.0)
    mm_c[3] = np.where(foot, g16, 0.0)
    mm_c[4] = np.where(foot, g2 - g8, 0.0)
    del g2, g6, g8, g16

    lmax5, lorth5, _, _ = _directional_line_stats(p1, foot, length_px=5, pre_sigma=0.5)
    mm_c[5] = lmax5
    mm_c[6] = lorth5
    del lmax5, lorth5

    lmax13, lorth13, cos2_13, sin2_13 = _directional_line_stats(p1, foot, length_px=13, pre_sigma=0.9)
    mm_c[7] = lmax13
    mm_c[8] = lorth13

    lmax29, lorth29, cos2_29, sin2_29 = _directional_line_stats(p1, foot, length_px=29, pre_sigma=1.5)
    mm_c[9] = lmax29
    mm_c[10] = lorth29
    mm_c[11] = np.where(foot, np.maximum(0.0, cos2_13 * cos2_29 + sin2_13 * sin2_29) * lorth13, 0.0)
    del lmax29, lorth29, cos2_29, sin2_29

    worm_max13, _, _, _ = _directional_line_stats(mm_s[57].astype(np.float32), foot, length_px=13, pre_sigma=0.8)
    mm_c[12] = worm_max13
    del worm_max13

    ptcf_max13, _, _, _ = _directional_line_stats(mm_s[61].astype(np.float32), foot, length_px=13, pre_sigma=0.8)
    mm_c[13] = ptcf_max13
    del ptcf_max13

    chi_corr = gaussian_filter(mm_s[36].astype(np.float32), sigma=5.0) * lmax13
    mm_c[14] = np.where(foot, chi_corr, 0.0)
    del chi_corr, lmax13, lorth13

    mm_c[15] = mm_s[14]  # tf_depth_basement
    mm_c[16] = mm_s[27]  # dem10_slope_p90
    mm_c[17] = mm_s[62]  # mimic_lahontan_crag_gate

    mm_c.flush()
    del mm_c, mm_s
    gc.collect()
    return out_path, cos2_13, sin2_13


# --- Fold-Safe Visible-Only Crack-Tip, Gap-Bridge & En-Echelon Relay-Ramp Mechanics ---

def compute_visible_structural_stack(
    visible_mask: np.ndarray,
    domain_mask: np.ndarray,
    p2_blind: np.ndarray,
    p2_cos2: np.ndarray,
    p2_sin2: np.ndarray,
) -> np.ndarray:
    """Compute 10 fold-safe structural features strictly from ``visible_mask``.

    Returns shape ``(10, H_crop, W_crop)`` float32 array. Never accesses withheld truth.
    """
    vis = np.asarray(visible_mask, dtype=bool)
    dom = np.asarray(domain_mask, dtype=bool)
    hc, wc = vis.shape
    out = np.zeros((len(STRUCTURAL_NAMES), hc, wc), dtype=np.float32)
    if int(vis.sum()) < 8:
        return out

    # Reuse vendor/gems57/relay_bend_anatomy.py::two_host_frame for exact C1 != C2 bitplane EDT
    try:
        thf = two_host_frame(vis)
        d1 = thf["d1"]
        iy1 = thf["iy1"].astype(np.int32, copy=False)
        ix1 = thf["ix1"].astype(np.int32, copy=False)
        c1 = thf["c1"]
        d2 = np.minimum(thf["d2"], 80.0).astype(np.float32)
        comp_len = thf["comp_len"]
        del thf
        gc.collect()
    except ValueError:
        d1, (iy1, ix1) = distance_transform_edt(~vis, return_indices=True)
        d1 = d1.astype(np.float32)
        d2 = np.full((hc, wc), 80.0, dtype=np.float32)
        comp_lbl, _ = ndi.label(vis, structure=np.ones((3, 3), dtype=np.int8))
        c1 = comp_lbl[iy1, ix1]
        comp_len = np.bincount(comp_lbl.ravel()).astype(np.float32)

    # Anchor local strike strictly from visible_mask (vendor/gems57/network.py::local_strike)
    # Note: local_strike returns strike in degrees clockwise from North (dy=-cos, dx=sin),
    # or let's compute exact image-coordinate tangent directly on visible_mask skeleton so
    # image (dy, dx) frame matches p2_cos2 / p2_sin2 identically!
    vis_sm = gaussian_filter(vis.astype(np.float32), sigma=2.2)
    gy_v, gx_v = np.gradient(vis_sm)
    # Normal to fault trace is (gy_v, gx_v); tangent along fault trace is (-gy_v, gx_v) in (x, y)
    # Let's keep explicit (ty, tx) unit vectors in (row, col) coordinates:
    # Gradient (gy_v, gx_v) is normal to ridge -> tangent (ty, tx) = (-gx_v, gy_v) / hypot
    g_norm = np.maximum(np.hypot(gy_v, gx_v), 1e-6)
    ty_grid = (-gx_v / g_norm).astype(np.float32)
    tx_grid = (gy_v / g_norm).astype(np.float32)
    del vis_sm, gy_v, gx_v, g_norm

    ty_anc = ty_grid[iy1, ix1]
    tx_anc = tx_grid[iy1, ix1]
    del ty_grid, tx_grid

    yy, xx = np.ogrid[:hc, :wc]
    dy1 = yy.astype(np.float32) - iy1.astype(np.float32)
    dx1 = xx.astype(np.float32) - ix1.astype(np.float32)
    d_par = np.abs(dy1 * ty_anc + dx1 * tx_anc)
    d_perp = np.abs(-dy1 * tx_anc + dx1 * ty_anc)
    del dy1, dx1

    # Spin-2 angle in image (dx=cos, dy=sin): cos(2*ang) = tx^2 - ty^2, sin(2*ang) = 2*tx*ty
    vis_cos2 = tx_anc * tx_anc - ty_anc * ty_anc
    vis_sin2 = 2.0 * tx_anc * ty_anc
    strike_align = np.maximum(0.0, vis_cos2 * p2_cos2 + vis_sin2 * p2_sin2).astype(np.float32)
    del ty_anc, tx_anc, vis_cos2, vis_sin2

    # Relay facing: -grad(d1) . grad(d2)
    g1y, g1x = np.gradient(np.minimum(d1, 60.0))
    g2y, g2x = np.gradient(np.minimum(d2, 60.0))
    n1 = np.maximum(np.hypot(g1y, g1x), 1e-5)
    n2 = np.maximum(np.hypot(g2y, g2x), 1e-5)
    facing = np.maximum(0.0, -(g1y * g2y + g1x * g2x) / (n1 * n2))
    del g1y, g1x, g2y, g2x, n1, n2
    d_sum = np.maximum(d1 + d2, 1.0)
    relay_ratio = np.clip(d1 / d_sum, 0.0, 0.5).astype(np.float32)
    balance = (4.0 * d1 * d2) / (d_sum * d_sum)
    relay_zone = (np.exp(-d_sum / 24.0) * facing * balance).astype(np.float32)
    del facing, d_sum, balance

    # Multi-scale visible-trace bend hinge turning (sigma=2.5 vs sigma=8.5 spin-2 director difference;
    # cut-endpoint-invariant unlike degree-1 skeleton tip cones caught at AUC=0.911 by Rule-4 canary)
    vf_3 = gaussian_filter(vis.astype(np.float32), sigma=2.5)
    gy3, gx3 = np.gradient(vf_3)
    n3 = np.maximum(np.hypot(gy3, gx3), 1e-6)
    c2_3 = (gy3 * gy3 - gx3 * gx3) / (n3 * n3)
    s2_3 = (-2.0 * gx3 * gy3) / (n3 * n3)
    del vf_3, gy3, gx3, n3

    vf_9 = gaussian_filter(vis.astype(np.float32), sigma=8.5)
    gy9, gx9 = np.gradient(vf_9)
    n9 = np.maximum(np.hypot(gy9, gx9), 1e-6)
    c2_9 = (gy9 * gy9 - gx9 * gx9) / (n9 * n9)
    s2_9 = (-2.0 * gx9 * gy9) / (n9 * n9)
    del vf_9, gy9, gx9, n9

    turn_grid = np.hypot(c2_3 - c2_9, s2_3 - s2_9).astype(np.float32)
    del c2_3, s2_3, c2_9, s2_9
    bend_turn = turn_grid[iy1, ix1]
    del turn_grid

    phys_x_relay = (
        p2_blind * (0.65 * relay_zone + 0.35 * strike_align * np.exp(-d_perp / 12.0))
    ).astype(np.float32)

    out[0] = np.where(dom, np.minimum(d1, 60.0), 0.0)
    out[1] = np.where(dom, np.minimum(d_perp, 60.0), 0.0)
    out[2] = np.where(dom, np.minimum(d_par, 60.0), 0.0)
    out[3] = np.where(dom, np.log1p(comp_len[c1]), 0.0)
    out[4] = np.where(dom, bend_turn, 0.0)
    out[5] = np.where(dom, relay_ratio, 0.0)
    out[6] = np.where(dom, np.minimum(d2, 80.0), 0.0)
    out[7] = np.where(dom, relay_zone, 0.0)
    out[8] = np.where(dom, strike_align, 0.0)
    out[9] = np.where(dom, phys_x_relay, 0.0)
    return out


# --- Leakage Canary Across All 69 Static + 18 CTX2D + 10 Structural Features ---

def run_ctws_leakage_canary(
    static_stack_path: Path,
    ctx2d_path: Path,
    grid: G57.Grid,
    p2_blind: np.ndarray,
    p2_cos2: np.ndarray,
    p2_sin2: np.ndarray,
    ceiling_auc: float = 0.90,
) -> dict:
    """Protocol Rule 4: Test every single static, 2-D context, and fold-visible structural feature solo."""
    ctx = H57.build_holdout(grid, seeds=(20, 21), modes=("all", "detached"))
    mm_s = open_memmap(static_stack_path, mode="r")
    mm_c = open_memmap(ctx2d_path, mode="r")

    # Test static & CTX2D features on pooled detached withheld truth vs background
    det_hidden = np.zeros(grid.shape, dtype=bool)
    for k, m in ctx.hidden_by_cell.items():
        if k.endswith("_detached"):
            det_hidden |= m
    rng = np.random.default_rng(20261028)
    pos_f = np.flatnonzero(det_hidden & grid.footprint)
    bg_pool = np.flatnonzero(grid.footprint & ~grid.catalogue)
    bg_f = rng.choice(bg_pool, size=min(120_000, bg_pool.size), replace=False)
    eval_f = np.concatenate([pos_f, bg_f])
    y_det = np.concatenate([np.ones(pos_f.size, dtype=np.int32), np.zeros(bg_f.size, dtype=np.int32)])
    ys, xs = eval_f // grid.shape[1], eval_f % grid.shape[1]

    feature_aucs: dict[str, float] = {}
    rows: list[dict] = []
    leaking: list[str] = []

    def _rec(name: str, vals: np.ndarray, y_vec: np.ndarray, group: str) -> None:
        v = np.nan_to_num(vals.astype(np.float64), nan=0.0, posinf=0.0, neginf=0.0)
        raw_auc = 0.5 if np.all(v == v[0]) else float(roc_auc_score(y_vec, v))
        dir_auc = max(raw_auc, 1.0 - raw_auc)
        flag = dir_auc > ceiling_auc
        if flag:
            leaking.append(name)
        feature_aucs[name] = round(dir_auc, 5)
        rows.append(
            {
                "feature": name,
                "group": group,
                "raw_auc": round(raw_auc, 5),
                "direction_invariant_auc": round(dir_auc, 5),
                "leaking": bool(flag),
            }
        )

    for i, name in enumerate(CTWS_STATIC_CHANNELS):
        _rec(name, mm_s[i, ys, xs], y_det, "static_69ch")
    for i, name in enumerate(CTX2D_NAMES):
        _rec(name, mm_c[i, ys, xs], y_det, "ctx2d_18ch")

    # Test fold-visible structural features across pooled `all` cells strictly from ctx.visible(cell.key)
    st_vals_list = [[] for _ in STRUCTURAL_NAMES]
    st_y_list = []
    rng_st = np.random.default_rng(20261029)
    H_g, W_g = grid.shape
    halo_c = 40
    for cell in ctx.cells_of("all"):
        sy, sx = cell.bbox
        ey0, ey1 = max(0, int(sy.start) - halo_c), min(H_g, int(sy.stop) + halo_c)
        ex0, ex1 = max(0, int(sx.start) - halo_c), min(W_g, int(sx.stop) + halo_c)
        vis_full_c = ctx.visible(cell.key)
        st_ext = compute_visible_structural_stack(
            vis_full_c[ey0:ey1, ex0:ex1],
            grid.footprint[ey0:ey1, ex0:ex1],
            p2_blind[ey0:ey1, ex0:ex1],
            p2_cos2[ey0:ey1, ex0:ex1],
            p2_sin2[ey0:ey1, ex0:ex1],
        )
        act_c = cell.active
        iy0 = int(sy.start) - ey0
        ix0 = int(sx.start) - ex0
        st_crop = st_ext[:, iy0 : iy0 + act_c.shape[0], ix0 : ix0 + act_c.shape[1]]
        del st_ext
        truth_c = np.zeros(act_c.shape, dtype=bool)
        truth_c[cell.truth_yx] = True
        p_idx = np.flatnonzero(truth_c & act_c)
        n_pool = np.flatnonzero(act_c & ~truth_c)
        n_idx = rng_st.choice(n_pool, size=min(15_000, n_pool.size), replace=False)
        comb = np.concatenate([p_idx, n_idx])
        cy, cx = comb // act_c.shape[1], comb % act_c.shape[1]
        for j in range(len(STRUCTURAL_NAMES)):
            st_vals_list[j].append(st_crop[j, cy, cx])
        st_y_list.append(np.concatenate([np.ones(p_idx.size, dtype=np.int32), np.zeros(n_idx.size, dtype=np.int32)]))

    y_st = np.concatenate(st_y_list)
    for j, name in enumerate(STRUCTURAL_NAMES):
        _rec(name, np.concatenate(st_vals_list[j]), y_st, "fold_visible_structural_10ch")

    max_feat = max(feature_aucs, key=lambda k: feature_aucs[k])
    return {
        "protocol_rule": "Rule-4-Single-Feature-Leakage-Canary",
        "evaluator_holdout": eh57.VERSION,
        "auc_ceiling": ceiling_auc,
        "all_features_tested": True,
        "n_features_tested": len(feature_aucs),
        "max_direction_invariant_auc": feature_aucs[max_feat],
        "max_feature": max_feat,
        "leaking_features": leaking,
        "all_passed": len(leaking) == 0,
        "feature_aucs": feature_aucs,
        "rows": rows,
    }


# --- Stage-1 & Stage-2 Buffered Out-of-Fold Fitting + Dual-Regime Submodular Allocation ---

# Key static physical channels paired with 18 CTX2D features in Stage-2
STAGE2_STATIC_EXTRA = [
    1,   # tf_rtp
    2,   # tf_tmi_hg
    4,   # tf_iso_grav_slope
    7,   # tf_geod_dilate
    14,  # tf_depth_basement
    16,  # tf_cond_surf
    27,  # dem10_slope_p90
    32,  # dem10_curv_prof_absmax
    33,  # dem10_aspect_coherence
    34,  # dem10_hs_lineament
    36,  # chi_step_pos_300m
    53,  # ptzw_tmi_worm
    55,  # ptzw_rtp_worm_800m
    56,  # ptzw_grav_worm
    57,  # ptzw_joint_concordance
    58,  # basement_throw_grad
    59,  # mt_cond_grad
    60,  # hmas_rtp_trough
    61,  # ptcf_piedmont_hinge
    62,  # mimic_lahontan_crag_gate
    63,  # epith_blm_corridor
    64,  # radon_playa_detrended
    65,  # ing_f2mdab_plume
    66,  # ing_well_geotherm
    67,  # ing_sinter_vent_halo
]


def _diagonal_folds_with_collar(foot: np.ndarray, buffer_px: float = 15.0) -> tuple[list[np.ndarray], list[np.ndarray]]:
    h, w = foot.shape
    yy_idx, xx_idx = np.nonzero(foot)
    u_c = (yy_idx - float(yy_idx.mean())) + (xx_idx - float(xx_idx.mean()))
    v_c = (yy_idx - float(yy_idx.mean())) - (xx_idx - float(xx_idx.mean()))
    um, vm = float(np.median(u_c)), float(np.median(v_c))
    folds, collars = [], []
    for su in (False, True):
        for sv in (False, True):
            fm = np.zeros((h, w), dtype=bool)
            fm[yy_idx, xx_idx] = ((u_c >= um) if su else (u_c < um)) & ((v_c >= vm) if sv else (v_c < vm))
            folds.append(fm)
            collars.append(distance_transform_edt(~fm) <= buffer_px)
    return folds, collars


def fit_ctws_pipeline(
    static_stack_path: Path,
    grid: G57.Grid,
    lidar_valid: np.ndarray,
    *,
    force: bool = False,
    log=print,
) -> dict:
    """Fit EXP1 (Stage-1 69-ch OOF), EXP2 (Stage-2 Blind 2-D Lineament Context OOF),
    and EXP3 (Stage-2 Fold-Safe Crack-Tip & En-Echelon Relay-Ramp OOF models)."""
    cdir = cache_dir()
    surf_cache = cdir / "ctws_stage12_surfaces_v1.npz"
    ctx_quad_path = cdir / "ctws_ctx2d_quad_v1.npy"
    ctx_prod_path = cdir / "ctws_ctx2d_prod_v1.npy"

    foot = grid.footprint
    labels = grid.catalogue
    mm_s = open_memmap(static_stack_path, mode="r")
    _, h, w = mm_s.shape

    folds, collars = quadrant_folds_with_collar(foot, buffer_px=15.0)
    diag_folds, diag_collars = _diagonal_folds_with_collar(foot, buffer_px=15.0)

    # Mask union of all hidden evaluation segments across gems57-pooled-hide-v2 & HIDE-RECOVER-v3.0
    any_hidden = np.zeros((h, w), dtype=bool)
    ctx57 = H57.build_holdout(grid, seeds=(20, 21), modes=("all", "detached"))
    for hid_m in ctx57.hidden_by_cell.values():
        any_hidden |= hid_m
    hr3_draws = build_hr3_draws(foot, labels, seeds=(101, 202))
    for d in hr3_draws:
        any_hidden |= d["hidden"]
    hidden_buf = binary_dilation(any_hidden, iterations=3)

    d_lbl_vis = distance_transform_edt(~(labels & ~any_hidden))
    safe_pos_all = labels & ~hidden_buf & foot
    safe_neg_all = foot & ~labels & ~hidden_buf & (d_lbl_vis > 3.0)
    del d_lbl_vis

    lgb_s1 = dict(
        n_estimators=320,
        learning_rate=0.05,
        num_leaves=55,
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

    def _gather_mm(mm_arr, ys: np.ndarray, xs: np.ndarray, cols: list[int]) -> np.ndarray:
        X = np.empty((ys.size, len(cols)), dtype=np.float32)
        for j, c in enumerate(cols):
            X[:, j] = mm_arr[c, ys, xs]
        return X

    def _sample_s1(tr_dom: np.ndarray, cols: list[int], seed_i: int) -> tuple[np.ndarray, np.ndarray]:
        rng = np.random.default_rng(seed_i)
        pf = np.flatnonzero(safe_pos_all & tr_dom)
        nf = np.flatnonzero(safe_neg_all & tr_dom)
        if pf.size > 48_000:
            pf = rng.choice(pf, size=48_000, replace=False)
        n_keep = min(nf.size, max(pf.size * 5, 120_000))
        nf = rng.choice(nf, size=n_keep, replace=False)
        af = np.concatenate([pf, nf])
        yv = np.concatenate([np.ones(pf.size, dtype=np.int32), np.zeros(nf.size, dtype=np.int32)])
        return _gather_mm(mm_s, af // w, af % w, cols), yv

    def _pred_s1(clf: lgb.LGBMClassifier, dom: np.ndarray, cols: list[int]) -> np.ndarray:
        flat = np.flatnonzero(dom)
        ys, xs = flat // w, flat % w
        out = np.zeros(flat.size, dtype=np.float32)
        chunk = 280_000
        for s in range(0, flat.size, chunk):
            Xc = _gather_mm(mm_s, ys[s : s + chunk], xs[s : s + chunk], cols)
            out[s : s + chunk] = clf.predict_proba(Xc)[:, 1].astype(np.float32)
        return out

    full_idx = list(range(len(CTWS_STATIC_CHANNELS)))
    msub_idx = list(CTWS_MSUB_INDICES)

    if not force and surf_cache.is_file() and ctx_quad_path.is_file() and ctx_prod_path.is_file():
        log(f"[ctws-fit] Reusing cached Stage-1 & Stage-2 blind OOF surfaces from {surf_cache}")
        z = np.load(surf_cache)
        p1_quad = z["p1_quad"]
        p1_prod = z["p1_prod"]
        p2_blind_quad = z["p2_blind_quad"]
        p2_blind_prod = z["p2_blind_prod"]
        q_cos2 = z["q_cos2"]
        q_sin2 = z["q_sin2"]
        p_cos2 = z["p_cos2"]
        p_sin2 = z["p_sin2"]
    else:
        p1_quad = np.zeros((h, w), dtype=np.float32)
        for q in range(4):
            tr_dom = foot & ~collars[q]
            te_dom = folds[q]
            log(f"[ctws-s1] Fitting Stage-1 Quadrant {q}/3 Dual-Cover OOF (69ch / 56ch)...")
            Xf, yf = _sample_s1(tr_dom & lidar_valid, full_idx, 1100 + q)
            clf_f = lgb.LGBMClassifier(**lgb_s1)
            clf_f.fit(Xf, yf)
            del Xf, yf

            Xs, ys_v = _sample_s1(tr_dom, msub_idx, 1200 + q)
            clf_s = lgb.LGBMClassifier(**lgb_s1)
            clf_s.fit(Xs, ys_v)
            del Xs, ys_v

            rng_c = np.random.default_rng(1300 + q)
            cf = rng_c.choice(np.flatnonzero(tr_dom & lidar_valid & safe_neg_all), size=40_000, replace=False)
            ref_c = clf_f.predict_proba(_gather_mm(mm_s, cf // w, cf % w, full_idx))[:, 1].astype(np.float32)
            sub_c = clf_s.predict_proba(_gather_mm(mm_s, cf // w, cf % w, msub_idx))[:, 1].astype(np.float32)

            te_l = te_dom & lidar_valid
            te_g = te_dom & ~lidar_valid
            if np.any(te_l):
                pf_l = _pred_s1(clf_f, te_l, full_idx)
                ps_l = _quantile_match_to_ref(_pred_s1(clf_s, te_l, msub_idx), ref_c, sub_c)
                p1_quad[te_l] = np.float32(0.75) * pf_l + np.float32(0.25) * ps_l
            if np.any(te_g):
                p1_quad[te_g] = _quantile_match_to_ref(_pred_s1(clf_s, te_g, msub_idx), ref_c, sub_c)
            del clf_f, clf_s
            gc.collect()

        p1_diag = np.zeros((h, w), dtype=np.float32)
        for q in range(4):
            tr_dom = foot & ~diag_collars[q]
            te_dom = diag_folds[q]
            log(f"[ctws-s1] Fitting Stage-1 Diagonal {q}/3 Dual-Cover OOF...")
            Xf, yf = _sample_s1(tr_dom & lidar_valid, full_idx, 1400 + q)
            clf_f = lgb.LGBMClassifier(**lgb_s1)
            clf_f.fit(Xf, yf)
            del Xf, yf

            Xs, ys_v = _sample_s1(tr_dom, msub_idx, 1500 + q)
            clf_s = lgb.LGBMClassifier(**lgb_s1)
            clf_s.fit(Xs, ys_v)
            del Xs, ys_v

            rng_c = np.random.default_rng(1600 + q)
            cf = rng_c.choice(np.flatnonzero(tr_dom & lidar_valid & safe_neg_all), size=40_000, replace=False)
            ref_c = clf_f.predict_proba(_gather_mm(mm_s, cf // w, cf % w, full_idx))[:, 1].astype(np.float32)
            sub_c = clf_s.predict_proba(_gather_mm(mm_s, cf // w, cf % w, msub_idx))[:, 1].astype(np.float32)

            te_l = te_dom & lidar_valid
            te_g = te_dom & ~lidar_valid
            if np.any(te_l):
                pf_l = _pred_s1(clf_f, te_l, full_idx)
                ps_l = _quantile_match_to_ref(_pred_s1(clf_s, te_l, msub_idx), ref_c, sub_c)
                p1_diag[te_l] = np.float32(0.75) * pf_l + np.float32(0.25) * ps_l
            if np.any(te_g):
                p1_diag[te_g] = _quantile_match_to_ref(_pred_s1(clf_s, te_g, msub_idx), ref_c, sub_c)
            del clf_f, clf_s
            gc.collect()

        p1_prod = (np.float32(0.5) * p1_quad + np.float32(0.5) * p1_diag).astype(np.float32)
        del p1_diag

        # Build Stage-2 18-ch 2-D multi-scale anisotropic lineament context stacks
        log("[ctws-s2] Building 18-ch 2-D Multi-Scale Anisotropic Lineament Context Pyramid (quad & prod)...")
        _, q_cos2, q_sin2 = build_ctx2d_memmap(p1_quad, static_stack_path, foot, ctx_quad_path)
        _, p_cos2, p_sin2 = build_ctx2d_memmap(p1_prod, static_stack_path, foot, ctx_prod_path)

        mm_cq = open_memmap(ctx_quad_path, mode="r")
        mm_cp = open_memmap(ctx_prod_path, mode="r")

        lgb_s2_blind = dict(
            n_estimators=260,
            learning_rate=0.045,
            num_leaves=43,
            min_child_samples=100,
            subsample=0.8,
            subsample_freq=1,
            colsample_bytree=0.75,
            reg_alpha=2.0,
            reg_lambda=5.0,
            n_jobs=2,
            random_state=20261028,
            verbose=-1,
        )

        def _gather_s2_blind(mm_ctx, ys: np.ndarray, xs: np.ndarray) -> np.ndarray:
            n_c = len(CTX2D_NAMES)
            n_e = len(STAGE2_STATIC_EXTRA)
            X = np.empty((ys.size, n_c + n_e), dtype=np.float32)
            for j in range(n_c):
                X[:, j] = mm_ctx[j, ys, xs]
            for j, sc in enumerate(STAGE2_STATIC_EXTRA):
                X[:, n_c + j] = mm_s[sc, ys, xs]
            return X

        def _sample_s2_blind(mm_ctx, tr_dom: np.ndarray, seed_i: int) -> tuple[np.ndarray, np.ndarray]:
            rng = np.random.default_rng(seed_i)
            pf = np.flatnonzero(safe_pos_all & tr_dom)
            nf = np.flatnonzero(safe_neg_all & tr_dom)
            if pf.size > 48_000:
                pf = rng.choice(pf, size=48_000, replace=False)
            n_keep = min(nf.size, max(pf.size * 5, 130_000))
            nf = rng.choice(nf, size=n_keep, replace=False)
            af = np.concatenate([pf, nf])
            yv = np.concatenate([np.ones(pf.size, dtype=np.int32), np.zeros(nf.size, dtype=np.int32)])
            return _gather_s2_blind(mm_ctx, af // w, af % w), yv

        def _pred_s2_blind(clf: lgb.LGBMClassifier, mm_ctx, dom: np.ndarray) -> np.ndarray:
            flat = np.flatnonzero(dom)
            ys, xs = flat // w, flat % w
            out = np.zeros(flat.size, dtype=np.float32)
            chunk = 280_000
            for s in range(0, flat.size, chunk):
                Xc = _gather_s2_blind(mm_ctx, ys[s : s + chunk], xs[s : s + chunk])
                out[s : s + chunk] = clf.predict_proba(Xc)[:, 1].astype(np.float32)
            return out

        p2_blind_quad = np.zeros((h, w), dtype=np.float32)
        for q in range(4):
            tr_dom = foot & ~collars[q]
            te_dom = folds[q]
            log(f"[ctws-s2] Fitting EXP2 Blind 2-D Context GBDT Quadrant {q}/3...")
            X2, y2 = _sample_s2_blind(mm_cq, tr_dom, 2100 + q)
            clf2 = lgb.LGBMClassifier(**lgb_s2_blind)
            clf2.fit(X2, y2)
            del X2, y2
            p2_blind_quad[te_dom] = _pred_s2_blind(clf2, mm_cq, te_dom)
            del clf2
            gc.collect()

        p2_blind_diag = np.zeros((h, w), dtype=np.float32)
        for q in range(4):
            tr_dom = foot & ~diag_collars[q]
            te_dom = diag_folds[q]
            log(f"[ctws-s2] Fitting EXP2 Blind 2-D Context GBDT Diagonal {q}/3...")
            X2, y2 = _sample_s2_blind(mm_cp, tr_dom, 2200 + q)
            clf2 = lgb.LGBMClassifier(**lgb_s2_blind)
            clf2.fit(X2, y2)
            del X2, y2
            p2_blind_diag[te_dom] = _pred_s2_blind(clf2, mm_cp, te_dom)
            del clf2
            gc.collect()

        p2_blind_prod = (np.float32(0.5) * p2_blind_quad + np.float32(0.5) * p2_blind_diag).astype(np.float32)
        del p2_blind_diag, mm_cq, mm_cp
        gc.collect()

        np.savez_compressed(
            surf_cache,
            p1_quad=p1_quad,
            p1_prod=p1_prod,
            p2_blind_quad=p2_blind_quad,
            p2_blind_prod=p2_blind_prod,
            q_cos2=q_cos2,
            q_sin2=q_sin2,
            p_cos2=p_cos2,
            p_sin2=p_sin2,
        )
        log(f"[ctws-fit] Cached Stage-1 & Stage-2 blind surfaces -> {surf_cache}")

    # Combine Stage-1 69-ch local physics OOF with Stage-2 8-azimuth 2-D multi-scale context OOF,
    # and couple with slope-unbiased HMAS Dual-Cover crustal/hydrothermal OOF (`karage1_oof_surfaces_v1.npz`
    # if present) so intra-range bedrock & blind hydrothermal faults (`slope ~19.6 deg`) are not suppressed
    # by 10 m subgrid Quaternary piedmont roughness (`slope ~9.5 deg`).
    p2_blind_quad = (np.float32(0.68) * p1_quad + np.float32(0.32) * p2_blind_quad).astype(np.float32)
    p2_blind_prod = (np.float32(0.68) * p1_prod + np.float32(0.32) * p2_blind_prod).astype(np.float32)

    hk1_npz = cdir / "karage1_oof_surfaces_v1.npz"
    if hk1_npz.is_file():
        zh = np.load(hk1_npz)
        c_hm = zh["c_hmas_cal"].astype(np.float32)
        p98_hm = float(np.percentile(c_hm[foot][::8], 98)) + 1e-6
        hm_mod = np.float32(0.82) + np.float32(0.28) * np.clip(c_hm / np.float32(p98_hm), 0.0, 1.5)
        hk1_q_raw = np.maximum(zh["p_dual_quad"].astype(np.float32) * hm_mod, np.float32(0.56) * c_hm)
        hk1_p_raw = np.maximum(zh["p_dual_prod"].astype(np.float32) * hm_mod, np.float32(0.56) * c_hm)
        del zh, c_hm, hm_mod
        hk1_q_cal = np.zeros_like(p2_blind_quad)
        hk1_p_cal = np.zeros_like(p2_blind_prod)
        hk1_q_cal[foot] = _quantile_match_to_ref(hk1_q_raw[foot], p2_blind_quad[foot][::8], hk1_q_raw[foot][::8])
        hk1_p_cal[foot] = _quantile_match_to_ref(hk1_p_raw[foot], p2_blind_prod[foot][::8], hk1_p_raw[foot][::8])
        del hk1_q_raw, hk1_p_raw
        p2_blind_quad = np.maximum(
            np.float32(0.62) * p2_blind_quad + np.float32(0.38) * hk1_q_cal,
            np.float32(0.76) * hk1_q_cal,
        ).astype(np.float32)
        p2_blind_prod = np.maximum(
            np.float32(0.62) * p2_blind_prod + np.float32(0.38) * hk1_p_cal,
            np.float32(0.76) * hk1_p_cal,
        ).astype(np.float32)
        del hk1_q_cal, hk1_p_cal
        gc.collect()

    # --- Fit EXP3 Nested Synthetic-Withheld Fold-Safe Structural Models (1 per Quadrant) ---
    mm_cq = open_memmap(ctx_quad_path, mode="r")
    seg_grid, n_seg = g57_segments(safe_pos_all, max_len_px=12)[:2]

    lgb_s3_struct = dict(
        n_estimators=240,
        learning_rate=0.045,
        num_leaves=39,
        min_child_samples=90,
        subsample=0.8,
        subsample_freq=1,
        colsample_bytree=0.80,
        reg_alpha=2.0,
        reg_lambda=5.0,
        n_jobs=2,
        random_state=20261028,
        verbose=-1,
    )

    def _assemble_s3_matrix(
        ys: np.ndarray,
        xs: np.ndarray,
        p2_arr: np.ndarray,
        mm_ctx_arr,
        st_arr: np.ndarray,
        oy: int = 0,
        ox: int = 0,
    ) -> np.ndarray:
        # Features: [p2_blind] + 18 CTX2D + 10 STRUCTURAL = 29 features
        n_c = len(CTX2D_NAMES)
        n_st = len(STRUCTURAL_NAMES)
        X = np.empty((ys.size, 1 + n_c + n_st), dtype=np.float32)
        gy = ys + oy
        gx = xs + ox
        X[:, 0] = p2_arr[ys, xs]
        for j in range(n_c):
            X[:, 1 + j] = mm_ctx_arr[j, gy, gx]
        for j in range(n_st):
            X[:, 1 + n_c + j] = st_arr[j, ys, xs]
        return X

    log("[ctws-s3] Sampling 2 leak-free synthetic segment withholding draws on safe training faults...")
    q_parts: list[list[tuple[np.ndarray, np.ndarray, np.ndarray]]] = [[] for _ in range(4)]
    all_sids = np.arange(1, n_seg + 1)
    for m_idx, sim_seed in enumerate((3301, 3302)):
        rng_m = np.random.default_rng(sim_seed)
        perm = rng_m.permutation(all_sids)
        hid_sids = perm[: int(round(0.22 * perm.size))]
        y_sim_hid = np.isin(seg_grid, hid_sids) & safe_pos_all
        v_sim_vis = safe_pos_all & ~y_sim_hid
        d_v_sim = distance_transform_edt(~v_sim_vis).astype(np.float32)
        st_full = compute_visible_structural_stack(v_sim_vis, foot, p2_blind_quad, q_cos2, q_sin2)
        log(f"  [sim-draw {m_idx}] sim_hidden_px={int(y_sim_hid.sum())}, sim_visible_px={int(v_sim_vis.sum())}")

        for q in range(4):
            tr_dom = foot & ~collars[q] & ~hidden_buf
            rng_q = np.random.default_rng(3400 + 10 * m_idx + q)
            pos_mask = y_sim_hid & tr_dom & (d_v_sim > 1.5)
            neg_mask = tr_dom & ~labels & (d_v_sim > 1.5)
            pf = np.flatnonzero(pos_mask)
            nf_near = np.flatnonzero(neg_mask & (d_v_sim <= 18.0))
            nf_far = np.flatnonzero(neg_mask & (d_v_sim > 18.0))
            k_near = min(nf_near.size, max(pf.size * 3, 25_000))
            k_far = min(nf_far.size, max(pf.size * 3, 25_000))
            nf = np.concatenate([
                rng_q.choice(nf_near, size=k_near, replace=False),
                rng_q.choice(nf_far, size=k_far, replace=False),
            ])
            af = np.concatenate([pf, nf])
            ay, ax = af // w, af % w
            Xp = _assemble_s3_matrix(ay, ax, p2_blind_quad, mm_cq, st_full, 0, 0)
            yp = np.concatenate([np.ones(pf.size, dtype=np.int32), np.zeros(nf.size, dtype=np.int32)])
            pos_d = d_v_sim[ay[: pf.size], ax[: pf.size]]
            wp = np.ones(yp.size, dtype=np.float32)
            wp[: pf.size] = np.where(pos_d >= 5.0, 1.35, 1.0)
            q_parts[q].append((Xp, yp, wp))

        del y_sim_hid, v_sim_vis, d_v_sim, st_full
        gc.collect()

    struct_models: list[lgb.LGBMClassifier] = []
    for q in range(4):
        X_tr = np.vstack([t[0] for t in q_parts[q]])
        y_tr = np.concatenate([t[1] for t in q_parts[q]])
        w_tr = np.concatenate([t[2] for t in q_parts[q]])
        q_parts[q].clear()
        log(f"[ctws-s3] Fitting EXP3 Fold-Safe Structural GBDT Quadrant {q}/3 (n={y_tr.size}, pos={int(y_tr.sum())})...")
        clf3 = lgb.LGBMClassifier(**lgb_s3_struct)
        clf3.fit(X_tr, y_tr, sample_weight=w_tr)
        struct_models.append(clf3)
        del X_tr, y_tr, w_tr
        gc.collect()

    del q_parts, seg_grid
    gc.collect()

    return {
        "p1_quad": p1_quad,
        "p1_prod": p1_prod,
        "p2_blind_quad": p2_blind_quad,
        "p2_blind_prod": p2_blind_prod,
        "q_cos2": q_cos2,
        "q_sin2": q_sin2,
        "p_cos2": p_cos2,
        "p_sin2": p_sin2,
        "ctx_quad_path": ctx_quad_path,
        "ctx_prod_path": ctx_prod_path,
        "struct_models": struct_models,
        "hr3_draws": hr3_draws,
    }


def predict_exp3_crop(
    clf_or_list,
    vis_full: np.ndarray,
    foot_full: np.ndarray,
    p2_full: np.ndarray,
    cos2_full: np.ndarray,
    sin2_full: np.ndarray,
    mm_ctx,
    sy: slice,
    sx: slice,
    active_crop: np.ndarray,
    halo: int = 40,
) -> tuple[np.ndarray, np.ndarray]:
    """Predict EXP3 structural surface on ``(sy, sx)`` using halo-padded ``vis_full`` ONLY.

    Returns ``(p3_crop, d_vis_crop)`` of shape ``active_crop.shape``.
    """
    H, W = vis_full.shape
    ey0 = max(0, int(sy.start) - halo)
    ey1 = min(H, int(sy.stop) + halo)
    ex0 = max(0, int(sx.start) - halo)
    ex1 = min(W, int(sx.stop) + halo)
    es_y = slice(ey0, ey1)
    es_x = slice(ex0, ex1)

    vis_ext = vis_full[es_y, es_x]
    dom_ext = foot_full[es_y, es_x]
    p2_ext = p2_full[es_y, es_x]
    st_ext = compute_visible_structural_stack(
        vis_ext, dom_ext, p2_ext, cos2_full[es_y, es_x], sin2_full[es_y, es_x]
    )

    iy0 = int(sy.start) - ey0
    iy1 = iy0 + (int(sy.stop) - int(sy.start))
    ix0 = int(sx.start) - ex0
    ix1 = ix0 + (int(sx.stop) - int(sx.start))

    st_crop = st_ext[:, iy0:iy1, ix0:ix1]
    d_vis_crop = st_crop[0].copy()  # exact d1 capped at 60 px
    del st_ext

    p2_crop = p2_full[sy, sx]
    flat = np.flatnonzero(active_crop)
    p3_crop = np.zeros(active_crop.shape, dtype=np.float32)
    if flat.size == 0:
        return p3_crop, d_vis_crop

    wc = active_crop.shape[1]
    ys, xs = flat // wc, flat % wc
    n_c = len(CTX2D_NAMES)
    n_st = len(STRUCTURAL_NAMES)
    models = clf_or_list if isinstance(clf_or_list, list) else [clf_or_list]

    out_f = np.zeros(flat.size, dtype=np.float32)
    chunk = 280_000
    for s in range(0, flat.size, chunk):
        yc = ys[s : s + chunk]
        xc = xs[s : s + chunk]
        gy = yc + int(sy.start)
        gx = xc + int(sx.start)
        Xm = np.empty((yc.size, 1 + n_c + n_st), dtype=np.float32)
        Xm[:, 0] = p2_crop[yc, xc]
        for j in range(n_c):
            Xm[:, 1 + j] = mm_ctx[j, gy, gx]
        for j in range(n_st):
            Xm[:, 1 + n_c + j] = st_crop[j, yc, xc]
        acc = np.zeros(yc.size, dtype=np.float32)
        for m in models:
            acc += m.predict_proba(Xm)[:, 1].astype(np.float32)
        out_f[s : s + chunk] = acc / float(len(models))

    p3_crop[ys, xs] = out_f
    return p3_crop, d_vis_crop


def emit_ctws_dual_regime_300m(
    p3_struct: np.ndarray,
    p2_blind: np.ndarray,
    domain_mask: np.ndarray,
    visible_faults: np.ndarray,
    budget_dots: int,
    *,
    b_collar_px: float = 2.2,
    near_horizon_px: float = 15.0,
    far_floor_frac: float = 0.52,
    far_cap_frac: float = 0.60,
    min_sep_px: float = 2.9,
) -> np.ndarray:
    """Two-regime coupled 300 m CELF submodular allocator with explicit far-field basin floor.

    Allocates ``[far_floor_frac, far_cap_frac]`` of dots into far-field blind basins/ranges
    (``d_vis > 15 px``) ranked by axial-sharpened ``p2_blind``, and the complementary
    accommodation budget into ``b_collar_px < d_vis <= 15 px`` ranked by axial-sharpened
    ``p3_struct``, preserving strict ``> min_sep_px`` Euclidean separation across the boundary.
    """
    dom = np.asarray(domain_mask, dtype=bool)
    vis = np.asarray(visible_faults, dtype=bool)
    if budget_dots <= 0 or not np.any(dom):
        return np.zeros(dom.shape, dtype=bool)

    d_vis = distance_transform_edt(~vis) if np.any(vis) else np.full(dom.shape, 999.0, dtype=np.float32)
    elig = dom & (d_vis > b_collar_px)
    n_elig = int(elig.sum())
    if n_elig == 0:
        return np.zeros(dom.shape, dtype=bool)

    dom_near = elig & (d_vis <= near_horizon_px)
    dom_far = elig & (d_vis > near_horizon_px)

    s_near = sharpen_axial_crest(p3_struct, dom, crest_boost=0.25)
    s_far = sharpen_axial_crest(p2_blind, dom, crest_boost=0.26)

    if not np.any(dom_near):
        return emit_submodular_300m(s_far, dom_far, vis, budget_dots, b_collar_px=b_collar_px, min_sep_px=min_sep_px)
    if not np.any(dom_far):
        return emit_submodular_300m(s_near, dom_near, vis, budget_dots, b_collar_px=b_collar_px, min_sep_px=min_sep_px)

    nat_far = float(dom_far.sum()) / float(n_elig)
    # Adapt cleanly if the cell itself is detached-only (nat_far > 0.78) vs full-domain (~0.62)
    if nat_far > 0.78:
        far_frac = min(max(0.88 * nat_far, far_floor_frac), 0.85)
    else:
        far_frac = min(max(0.88 * nat_far, far_floor_frac), far_cap_frac)

    b_far = int(round(budget_dots * far_frac))
    b_near = max(0, budget_dots - b_far)
    mc_near = max(90_000, b_near * 14)
    mc_far = max(130_000, b_far * 14)

    em_near = emit_submodular_300m(
        s_near,
        dom_near,
        vis,
        b_near,
        b_collar_px=b_collar_px,
        min_sep_px=min_sep_px,
        max_candidates=mc_near,
    )
    # Pass `em_near` with `min_sep_px` exclusion into far-field emission so boundary spacing is exact
    d_em_near = distance_transform_edt(~em_near) if np.any(em_near) else np.full(dom.shape, 999.0, dtype=np.float32)
    dom_far_clean = dom_far & (d_em_near > min_sep_px)
    shortfall = max(0, b_near - int(em_near.sum()))
    em_far = emit_submodular_300m(
        s_far,
        dom_far_clean,
        vis,
        b_far + shortfall,
        b_collar_px=b_collar_px,
        min_sep_px=min_sep_px,
        max_candidates=mc_far,
    )
    return em_near | em_far

