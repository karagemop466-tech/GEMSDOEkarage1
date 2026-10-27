"""Shared 35-channel template base stack + 23-channel H-K1-1 (HMAS-SINTER-ENV) discovery stack.

Strictly memory-engineered (< 750 MB peak RSS on 3.8 GiB zero-swap hosts) using float32 disk-backed
memmaps and explicit garbage collection.

Zero catalogue-derived features are ever computed in this module:
- `labels.tif` / `existing_faults.tif` is NEVER read.
- `derived_sgmc_faults_100m_u8.tif` is NEVER read (reserved strictly for off-catalogue evaluation).
- `dist_known_fault_px` in `gdr_wellspring_in_footprint.csv` is explicitly ignored (`IR-KARAGE1-GDR-01`).
"""
from __future__ import annotations

import csv
import gc
import io
import json
import struct
import tempfile
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from numpy.lib.format import open_memmap
from rasterio.warp import transform as warp_transform
from scipy import ndimage
from scipy.fft import fftfreq, irfft2, rfft2, rfftfreq
from scipy.ndimage import (
    convolve,
    distance_transform_edt,
    gaussian_filter,
    grey_opening,
    maximum_filter,
    minimum_filter,
    sobel,
    uniform_filter,
)

NODATA_THRESHOLD = np.float32(-1e30)

BASE_CHANNELS: tuple[str, ...] = (
    *[f"band{i:02d}" for i in range(1, 20)],
    "curv_s1",
    "curv_s2",
    "ridge_s1",
    "ridge_s2",
    "ridge_s3",
    "relief5",
    "tophat2",
    "tmi_edge",
    "rtp_edge",
    "grav_edge",
    "cond_edge",
    "depth_grad",
    "coherence_s2",
    "strike_cos",
    "strike_sin",
    "footprint",
)

HMAS_CHANNELS: tuple[str, ...] = (
    # --- 17 Strictly 1m-LiDAR-Free & 100% Catalogue-Free Subsurface / Geothermal Channels (0..16) ---
    "hmas_analytic_sig_log",         # 35: Log 3-D magnetic analytic signal sqrt((dx RTP)^2+(dy RTP)^2+(tmi_vg)^2)
    "hmas_mag_destruct_trough",      # 36: Hydrothermal magnetite-destruction trough flanked by tilt walls & clay cap
    "ppgr_grav_ortho_excess",        # 37: Poisson pseudo-gravity orthogonal residual (non-magnetic basement throw)
    "grav_uc400_1800_persist",       # 38: 2-D Fourier upward-continued (400m, 1800m) gravity h-grad persistence
    "rtp_uc400_1800_persist",        # 39: 2-D Fourier upward-continued (400m, 1800m + 150m) RTP magnetic persistence
    "listric_dip_migration",         # 40: Hanging-wall z=0->1800m gravity crest migration into deepening cover
    "basin_margin_inflection",       # 41: Piedmont basement-bench inflection (-Laplacian depth_to_base_surf, 50-650m)
    "cond_claycap_gradient",         # 42: Smectite clay-cap lateral conductivity ridge (playa-vetoed)
    "geodawn_blk_bi214_radon_ridge", # 43: 4-block standardized 214Bi (eU - beta*eTh) radon fault-degassing crest
    "geodawn_blk_kth_alteration",    # 44: 4-block standardized DoG potassic/silicic (K/Th + low-TC) alteration halo
    "ing_f2mdab_aniso_plume",        # 45: INGENIOUS 2m temperature probe (F2mDAB) strike-projected thermal plume
    "ing_paleo_sinter_aniso_plume",  # 46: INGENIOUS Quaternary sinter/silicified-breccia/travertine strike plume
    "ing_quartz_geotherm_plume",     # 47: INGENIOUS quartz-geothermometer & thermal-spring strike corridor
    "walker_transtension_coupling",  # 48: Walker Lane / Great Basin transtensional strain-dilation x seismic edge
    "lahontan_road_confound_score",  # 49: Pluvial Lake Lahontan contour-parallel shoreline & TIGER road confound score
    "subsurf_aniso_corridor_1p2km",  # 50: 1.2 km directional along-strike continuity of subsurface crests
    "hmas_unsup_conduit_crest",      # 51: Unified LiDAR-free & catalogue-free subsurface geothermal conduit crest
    # --- 6 USGS 3DEP 1m LiDAR Tectonic Scarp Channels (17..22 -> global 52..57; M_Full ONLY) ---
    "lidar_ex_max",                  # 52
    "lidar_step_max",                # 53
    "lidar_coh100",                  # 54
    "lidar_relief",                  # 55
    "lidar_tectonic_asymm_chain",    # 56: Unidirectional scarp polarity |down-up| x 800m chain (road/shoreline vetoed)
    "lidar_valid_flag",              # 57
)

ALL_CHANNELS: tuple[str, ...] = BASE_CHANNELS + HMAS_CHANNELS
LIDAR_GLOBAL_INDICES: frozenset[int] = frozenset({52, 53, 54, 55, 56, 57})
MSUB_INDICES: tuple[int, ...] = tuple(i for i in range(len(ALL_CHANNELS)) if i not in LIDAR_GLOBAL_INDICES)
assert len(ALL_CHANNELS) == 58
assert len(MSUB_INDICES) == 52


def _fill_nearest(
    raw: np.ndarray,
    valid: np.ndarray,
    base_valid: np.ndarray | None = None,
    base_idx: tuple[np.ndarray, np.ndarray] | None = None,
) -> tuple[np.ndarray, tuple[np.ndarray, np.ndarray]]:
    if not np.any(valid):
        z = np.zeros(raw.shape, dtype=np.float32)
        zi = np.zeros(raw.shape, dtype=np.intp)
        return z, (zi, zi.copy())
    if base_idx is not None and base_valid is not None and np.array_equal(valid, base_valid):
        idx = base_idx
    else:
        _, idx = distance_transform_edt(~valid, return_distances=True, return_indices=True)
    filled = raw.astype(np.float32, copy=True)
    bad = ~valid
    if bad.any():
        filled[bad] = filled[idx[0][bad], idx[1][bad]]
    return filled, idx


def _grad_mag_and_vec(a: np.ndarray, sigma: float = 1.0) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    s = gaussian_filter(a.astype(np.float32, copy=False), sigma, mode="nearest") if sigma > 0 else a.astype(np.float32, copy=False)
    gy = sobel(s, axis=0).astype(np.float32) * np.float32(0.125)
    gx = sobel(s, axis=1).astype(np.float32) * np.float32(0.125)
    return np.hypot(gx, gy).astype(np.float32), gy, gx


def _hessian_ridge(a: np.ndarray, sigma: float, bright: bool = True) -> np.ndarray:
    """Sato/Frangi 2-D Hessian ridge (`bright=True`) or valley/trough (`bright=False`) detector."""
    src = (-a).astype(np.float32) if not bright else a.astype(np.float32, copy=False)
    axx = gaussian_filter(src, sigma, order=(0, 2), mode="nearest")
    ayy = gaussian_filter(src, sigma, order=(2, 0), mode="nearest")
    axy = gaussian_filter(src, sigma, order=(1, 1), mode="nearest")
    tmp = np.sqrt(np.maximum(((axx - ayy) * 0.5) ** 2 + axy**2, 0.0))
    l1 = (axx + ayy) * 0.5 + tmp
    l2 = (axx + ayy) * 0.5 - tmp
    big = np.where(np.abs(l1) >= np.abs(l2), l1, l2)
    small = np.where(np.abs(l1) >= np.abs(l2), l2, l1)
    return (-small * (big < 0).astype(np.float32)).astype(np.float32)


def _structure_tensor(a: np.ndarray, sigma: float) -> tuple[np.ndarray, np.ndarray]:
    gx = gaussian_filter(a, sigma, order=(0, 1), mode="nearest")
    gy = gaussian_filter(a, sigma, order=(1, 0), mode="nearest")
    jxx = gaussian_filter(gx * gx, sigma, mode="nearest")
    jyy = gaussian_filter(gy * gy, sigma, mode="nearest")
    jxy = gaussian_filter(gx * gy, sigma, mode="nearest")
    tr = jxx + jyy + 1e-12
    coh = np.sqrt(np.maximum(((jxx - jyy) * 0.5) ** 2 + jxy**2, 0.0)) / tr
    theta = 0.5 * np.arctan2(2.0 * jxy, (jxx - jyy) + 1e-12)
    return coh.astype(np.float32), theta.astype(np.float32)


def _robust_pos_norm(a: np.ndarray, foot: np.ndarray, clip_z: float = 6.0) -> np.ndarray:
    sub = a[foot][::8]
    med = float(np.median(sub))
    mad = max(float(np.median(np.abs(sub - med))) * 1.4826, 1e-6)
    z = np.clip((a - np.float32(med)) / np.float32(mad), -clip_z, clip_z)
    out = np.where(foot, np.maximum(z, np.float32(0.0)) / np.float32(clip_z), np.float32(0.0))
    return out.astype(np.float32)


def _block_zscore(a: np.ndarray, block_id: np.ndarray, valid: np.ndarray) -> np.ndarray:
    out = np.zeros(a.shape, dtype=np.float32)
    for bid in (1, 2, 3, 4):
        m = valid & (block_id == bid)
        if not m.any():
            continue
        sub = a[m][::4]
        med = np.float32(np.median(sub))
        mad = np.float32(max(float(np.median(np.abs(sub - med))) * 1.4826, 1e-4))
        out[m] = np.clip((a[m] - med) / mad, -8.0, 8.0)
    return out


def _harmonic_upward_and_pseudograv(
    field: np.ndarray,
    foot: np.ndarray,
    heights_m: tuple[float, float] = (400.0, 1800.0),
    compute_vertical_integral: bool = False,
    dx_m: float = 100.0,
    pad_px: int = 64,
) -> tuple[np.ndarray, ...]:
    """Exact 2-D Fourier upward continuation (Blakely 1995 Eq. 12.8) + optional Poisson 1/|k| integral."""
    h, w = field.shape
    med = np.float32(np.median(field[foot][::8]))
    work = np.where(foot & np.isfinite(field), field - med, np.float32(0.0)).astype(np.float32)
    padded = np.pad(work, ((pad_px, pad_px), (pad_px, pad_px)), mode="reflect")
    del work

    ph, pw = padded.shape
    spec = rfft2(padded, workers=2)
    del padded

    ky = fftfreq(ph, d=dx_m).astype(np.float32)[:, None]
    kx = rfftfreq(pw, d=dx_m).astype(np.float32)[None, :]
    k_rad = np.hypot(ky, kx).astype(np.float32)
    del ky, kx

    outs = []
    for z in heights_m:
        u = irfft2(spec * np.exp(-np.float32(2.0 * np.pi * z) * k_rad), s=(ph, pw), workers=2)[
            pad_px : pad_px + h, pad_px : pad_px + w
        ].astype(np.float32)
        outs.append(u)

    if compute_vertical_integral:
        # Band-limited 1/(2*pi*|k|) vertical integral (Poisson pseudo-gravity transform, Baranov 1957)
        # Taper ultra-long wavelengths (> 80 km) to avoid DC blow-up while preserving 0.3..40 km fault steps
        k0 = np.float32(1.0 / 80_000.0)
        inv_k = (k_rad / (k_rad * k_rad + k0 * k0)) * np.exp(-np.float32(2.0 * np.pi * 150.0) * k_rad)
        inv_k[0, 0] = 0.0
        pg = irfft2(spec * inv_k, s=(ph, pw), workers=2)[pad_px : pad_px + h, pad_px : pad_px + w].astype(np.float32)
        outs.append(pg)

    del spec, k_rad
    return tuple(outs)


def _anisotropic_strike_diffuse(
    seeds_grid: np.ndarray,
    cos2t: np.ndarray,
    sin2t: np.ndarray,
    foot: np.ndarray,
    sigma_iso: float = 3.5,
    along_len_px: int = 15,
) -> np.ndarray:
    """Project sparse hydrothermal point anomalies anisotropically (3:1) along local structural strike."""
    base = gaussian_filter(seeds_grid.astype(np.float32), sigma=sigma_iso, mode="constant", cval=0.0)
    # 4-azimuth directional kernels (0 deg E-W, 45 deg NE-SW, 90 deg N-S, 135 deg NW-SE)
    # Note: gradient vector angle phi has strike angle theta_s = phi + pi/2, so cos(2*theta_s) = -cos(2*phi).
    r = along_len_px
    acc = np.zeros_like(base)
    angles_rad = (0.0, np.pi * 0.25, np.pi * 0.5, np.pi * 0.75)
    h, w = base.shape
    step_stride = 2 if r >= 10 else 1
    for ang in angles_rad:
        # Exact sparse 1-D line convolution (O(r) instead of dense O((2r+1)^2) 2-D convolve: ~150x faster!)
        resp = np.zeros_like(base)
        w_sum = 0.0
        for step in range(-r, r + 1, step_stride):
            dy = int(round(-step * np.sin(ang)))
            dx = int(round(step * np.cos(ang)))
            wt = np.float32(np.exp(-0.5 * (step / (0.55 * r)) ** 2))
            w_sum += float(wt)
            y0_dst = max(0, dy); y1_dst = min(h, h + dy)
            y0_src = max(0, -dy); y1_src = min(h, h - dy)
            x0_dst = max(0, dx); x1_dst = min(w, w + dx)
            x0_src = max(0, -dx); x1_src = min(w, w - dx)
            resp[y0_dst:y1_dst, x0_dst:x1_dst] += wt * base[y0_src:y1_src, x0_src:x1_src]
        resp *= np.float32(1.0 / max(w_sum, 1e-6))
        # Alignment weight between strike and kernel azimuth `ang`: 0.5*(1 + cos(2*(theta_strike - ang)))
        align = np.float32(0.5) * (
            np.float32(1.0) + cos2t * np.float32(np.cos(2.0 * ang)) + sin2t * np.float32(np.sin(2.0 * ang))
        )
        acc += resp * (np.float32(0.25) + np.float32(0.75) * np.maximum(align, 0.0))
    return np.where(foot, acc, np.float32(0.0)).astype(np.float32)


def _rasterize_ingenious_geothermal_layers(
    ddir: Path,
    foot: np.ndarray,
    aff: rasterio.Affine,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Rasterize INGENIOUS GDR #1391 2m temperature probes, Quaternary sinter/paleo deposits, and thermal springs.

    Audit safeguard (`IR-KARAGE1-GDR-01`): `dist_known_fault_px` in `gdr_wellspring_in_footprint.csv`
    is NEVER read or referenced.
    """
    h, w = foot.shape
    f2m_grid = np.zeros((h, w), dtype=np.float32)
    paleo_grid = np.zeros((h, w), dtype=np.float32)
    qtz_grid = np.zeros((h, w), dtype=np.float32)

    # 1. 2-meter temperature probes (F2mDAB & T2m)
    z2m = ddir / "external" / "2m_temperature_probe_INGENIOUS_regional_data.zip"
    if z2m.is_file():
        with tempfile.TemporaryDirectory() as td:
            with zipfile.ZipFile(z2m) as zf:
                zf.extractall(td)
            dbf_files = list(Path(td).rglob("*.dbf"))
            if dbf_files:
                with dbf_files[0].open("rb") as fh:
                    numrec, lenheader, lenrec = struct.unpack("<4xIHH20x", fh.read(32))
                    fields = []
                    while True:
                        b = fh.read(32)
                        if not b or b[0] == 0x0D:
                            break
                        fields.append((b[:11].split(b"\x00")[0].decode("ascii", "ignore"), b[16]))
                    fh.seek(lenheader)
                    lons, lats, weights = [], [], []
                    for _ in range(numrec):
                        rec = fh.read(lenrec)
                        if not rec or rec[0] == 0x2A:
                            continue
                        off = 1
                        row_d = {}
                        for fn, fl in fields:
                            row_d[fn] = rec[off : off + fl].decode("utf-8", "ignore").strip()
                            off += fl
                        try:
                            lat = float(row_d["LatDegreeN"])
                            lon = float(row_d["LongDegree"])
                            dab = float(row_d["F2mDAB"]) if row_d.get("F2mDAB") else 0.0
                            t2 = float(row_d["T2m"]) if row_d.get("T2m") else 0.0
                            if -125.0 < lon < -110.0 and 35.0 < lat < 45.0:
                                w_anom = max(0.0, dab - 0.5) + 0.35 * max(0.0, t2 - 22.0)
                                if w_anom > 0.0:
                                    lons.append(lon)
                                    lats.append(lat)
                                    weights.append(min(w_anom, 25.0))
                        except Exception:
                            continue
                if lons:
                    xs, ys = warp_transform("EPSG:4269", "EPSG:32611", lons, lats)
                    for x, y, wt in zip(xs, ys, weights):
                        c_f, r_f = ~aff * (x, y)
                        ri, ci = int(round(r_f)), int(round(c_f))
                        if 0 <= ri < h and 0 <= ci < w and foot[ri, ci]:
                            if wt > f2m_grid[ri, ci]:
                                f2m_grid[ri, ci] = np.float32(wt)

    # 2. Paleogeothermal sinter / silicified fault breccia / travertine / explosion craters
    zpaleo = ddir / "external" / "paleo_geothermal_regional.zip"
    type_weights = {
        "Sinter": 4.0,
        "Silicified fault breccia": 4.5,
        "Explosion craters": 4.0,
        "Silica vein": 3.8,
        "Calcite-qtz veins": 3.5,
        "Silica-cemented sand": 3.0,
        "Silica-cemented mud or ash": 2.8,
        "Sulfur": 3.2,
        "Alteration": 2.6,
        "Argillic alteration": 2.6,
        "Travertine": 2.4,
        "Tufa": 1.6,
        "Sulfate crust": 2.0,
    }
    if zpaleo.is_file():
        with zipfile.ZipFile(zpaleo) as zf:
            csv_text = zf.read("Paleo_geothermal_final.csv").decode("utf-8", errors="replace")
        lons, lats, weights = [], [], []
        for row in csv.DictReader(io.StringIO(csv_text)):
            try:
                lon = float(row["Long_deg_NAD83"])
                lat = float(row["Lat_deg_NAD83"])
                wt = type_weights.get(row.get("Deposit_type", "").strip(), 2.0)
                lons.append(lon)
                lats.append(lat)
                weights.append(wt)
            except Exception:
                continue
        if lons:
            xs, ys = warp_transform("EPSG:4269", "EPSG:32611", lons, lats)
            for x, y, wt in zip(xs, ys, weights):
                c_f, r_f = ~aff * (x, y)
                ri, ci = int(round(r_f)), int(round(c_f))
                if 0 <= ri < h and 0 <= ci < w and foot[ri, ci]:
                    paleo_grid[ri, ci] = max(paleo_grid[ri, ci], np.float32(wt))

    # 3. Well & spring temperature + quartz/chalcedony/cation geothermometers (NO dist_known_fault_px!)
    ws_csv = ddir / "external" / "gdr_wellspring_in_footprint.csv"
    if ws_csv.is_file():
        with ws_csv.open("r", encoding="utf-8", errors="replace") as fh:
            for row in csv.DictReader(fh):
                try:
                    ri = int(float(row["row"]))
                    ci = int(float(row["col"]))
                    if not (0 <= ri < h and 0 <= ci < w and foot[ri, ci]):
                        continue
                    tc = float(row["temp_c"]) if row.get("temp_c") else 0.0
                    tq = float(row["geothermquartz_c"]) if row.get("geothermquartz_c") else 0.0
                    tchal = float(row["geothermchalc_c"]) if row.get("geothermchalc_c") else 0.0
                    tbest = max(tq, tchal)
                    enth = 0.04 * max(0.0, tbest - 80.0) + 0.08 * max(0.0, tc - 28.0)
                    if enth > 0.0:
                        qtz_grid[ri, ci] = max(qtz_grid[ri, ci], np.float32(min(enth, 10.0)))
                except Exception:
                    continue

    return f2m_grid, paleo_grid, qtz_grid


def build_feature_stack(ddir: Path, cdir: Path, force: bool = False, log=print) -> dict:
    """Build or reuse the 58-channel float32 memmap (`35` shared base + `23` H-K1-1 discovery channels)."""
    stack_path = cdir / "karage1_stack_58ch_f32.memmap"
    meta_path = cdir / "karage1_stack_58ch_meta.json"
    if not force and stack_path.is_file() and meta_path.is_file():
        meta = json.loads(meta_path.read_text())
        if meta.get("n_channels") == len(ALL_CHANNELS):
            log(f"[features] Reusing cached 58-channel stack at {stack_path}")
            return meta

    features_tif = ddir / "training_features.tif"
    sample_tif = ddir / "sample_submission.tif"
    with rasterio.open(sample_tif) as ds_sub:
        foot = np.isfinite(ds_sub.read(1))
        aff = ds_sub.transform
        h, w = ds_sub.height, ds_sub.width

    log(f"[features] Building 58-channel float32 stack ({len(ALL_CHANNELS)}x{h}x{w} CHW, footprint={int(foot.sum())})...")
    mm = open_memmap(stack_path, mode="w+", dtype=np.float32, shape=(len(ALL_CHANNELS), h, w))

    keep_bands = {2, 3, 4, 6, 7, 8, 9, 12, 13, 14, 15, 16, 17, 18, 19}
    kept: dict[int, np.ndarray] = {}
    base_valid = None
    base_idx = None

    with rasterio.open(features_tif) as src:
        for b in range(1, 20):
            raw = src.read(b)
            valid = np.isfinite(raw) & (raw > NODATA_THRESHOLD)
            filled, idx = _fill_nearest(raw, valid, base_valid, base_idx)
            if base_valid is None:
                base_valid, base_idx = valid, idx
            del raw
            mm[b - 1] = np.where(foot, filled, np.float32(0.0))
            if b in keep_bands:
                kept[b] = filled
            else:
                del filled
            if b % 5 == 0 or b == 19:
                mm.flush()
                log(f"  read official bands 1..{b}/19")

    # --- Shared Template Channels 19..34 (exact 35-ch base stack compatibility) ---
    dem = kept[12]
    c = 19
    mm[c] = np.where(foot, ndimage.gaussian_laplace(dem, 1.0, mode="nearest"), 0.0); c += 1
    mm[c] = np.where(foot, ndimage.gaussian_laplace(dem, 2.5, mode="nearest"), 0.0); c += 1
    for sig in (1.0, 2.0, 3.5):
        mm[c] = np.where(foot, _hessian_ridge(dem, sig, bright=True), 0.0); c += 1
    mm[c] = np.where(foot, maximum_filter(dem, size=5) - minimum_filter(dem, size=5), 0.0); c += 1
    mm[c] = np.where(foot, dem - grey_opening(dem, size=(5, 5)), 0.0); c += 1
    mm[c] = np.where(foot, _grad_mag_and_vec(kept[14], 1.0)[0], 0.0); c += 1
    rtp_edge, rtp_gy, rtp_gx = _grad_mag_and_vec(kept[2], 1.0)
    mm[c] = np.where(foot, rtp_edge, 0.0); c += 1
    grav_edge, grav_gy, grav_gx = _grad_mag_and_vec(kept[13], 1.5)
    mm[c] = np.where(foot, grav_edge, 0.0); c += 1
    cond_edge = _grad_mag_and_vec(kept[17], 1.5)[0]
    mm[c] = np.where(foot, cond_edge, 0.0); c += 1
    depth_edge, depth_gy, depth_gx = _grad_mag_and_vec(kept[15], 1.5)
    mm[c] = np.where(foot, depth_edge, 0.0); c += 1
    coh_dem, theta_dem = _structure_tensor(dem, 2.0)
    mm[c] = np.where(foot, coh_dem, 0.0); c += 1
    mm[c] = np.where(foot, np.cos(2.0 * theta_dem), 0.0); c += 1
    mm[c] = np.where(foot, np.sin(2.0 * theta_dem), 0.0); c += 1
    mm[c] = foot.astype(np.float32); c += 1
    assert c == 35
    mm.flush()
    del coh_dem, theta_dem
    gc.collect()
    log("  built shared 35-channel base stack")

    # --- H-K1-1 (HMAS-SINTER-ENV) Channels 35..57 ---
    # 35 & 36: 3-D Magnetic Analytic Signal & Hydrothermal Magnetite-Destruction Trough
    # Scale tmi_vg (nT/m) to match 100m Sobel RTP gradient units before forming 3D analytic signal
    vg_scaled = kept[9] * np.float32(100.0)
    asig = np.sqrt(rtp_gx * rtp_gx + rtp_gy * rtp_gy + vg_scaled * vg_scaled + np.float32(1e-6))
    asig_log = np.log1p(np.maximum(asig, 0.0)).astype(np.float32)
    mm[35] = np.where(foot, asig_log, 0.0)

    # Magnetite-destruction trough: negative magnetic tilt-curvature (-tmi_tc, Band 6) + valley of log 3D analytic signal
    neg_tmi_tc = _robust_pos_norm(np.maximum(-kept[6], np.float32(0.0)), foot)
    trough_s20 = _robust_pos_norm(_hessian_ridge(asig_log, 2.0, bright=False), foot)
    cond_norm = _robust_pos_norm(np.log1p(np.maximum(kept[17], 0.0)), foot)
    slope_deg = kept[19]
    depth_b = kept[15]
    playa_flat = (slope_deg < np.float32(1.8)) & (depth_b > np.float32(320.0))
    playa_gate = np.where(playa_flat, np.float32(0.18), np.float32(1.0)).astype(np.float32)

    hmas_trough = (
        (np.float32(0.65) * neg_tmi_tc + np.float32(0.35) * trough_s20)
        * (np.float32(0.60) + np.float32(0.40) * cond_norm)
        * playa_gate
    ).astype(np.float32)
    mm[36] = np.where(foot, np.nan_to_num(hmas_trough, nan=0.0), 0.0)
    del vg_scaled, asig, asig_log, neg_tmi_tc, trough_s20
    gc.collect()

    # 37, 38, 39, 40: Harmonic Upward Continuation (400m, 1800m) + Poisson Pseudo-Gravity Orthogonal Residual
    grav_u400, grav_u1800 = _harmonic_upward_and_pseudograv(kept[13], foot, heights_m=(400.0, 1800.0), compute_vertical_integral=False)
    rtp_u400, rtp_u1800, pseudo_grav = _harmonic_upward_and_pseudograv(kept[2], foot, heights_m=(400.0, 1800.0), compute_vertical_integral=True)

    pg_hg = _grad_mag_and_vec(pseudo_grav, 1.5)[0]
    iso_hg = np.maximum(kept[18], np.float32(0.0))
    # Windowed orthogonal regression slope beta(x) = cov(iso_hg, pg_hg) / (var(pg_hg) + eps) over 1.5 km window
    m_iso = uniform_filter(iso_hg, size=15, mode="nearest")
    m_pg = uniform_filter(pg_hg, size=15, mode="nearest")
    cov_ip = uniform_filter(iso_hg * pg_hg, size=15, mode="nearest") - m_iso * m_pg
    var_pg = uniform_filter(pg_hg * pg_hg, size=15, mode="nearest") - m_pg * m_pg
    beta_loc = np.clip(cov_ip / (var_pg + np.float32(1e-4)), np.float32(0.0), np.float32(5.0))
    ppgr_excess = np.maximum(iso_hg - beta_loc * pg_hg, np.float32(0.0))
    ppgr_ridge = np.float32(0.55) * _robust_pos_norm(ppgr_excess, foot) + np.float32(0.45) * _robust_pos_norm(
        _hessian_ridge(ppgr_excess, 1.6, bright=True), foot
    )
    mm[37] = np.where(foot, ppgr_ridge, 0.0)
    del pseudo_grav, pg_hg, m_iso, m_pg, cov_ip, var_pg, beta_loc, ppgr_excess
    gc.collect()

    g400_hg = _grad_mag_and_vec(grav_u400, 1.0)[0]
    g1800_hg, g1800_gy, g1800_gx = _grad_mag_and_vec(grav_u1800, 1.0)
    grav_persist = np.cbrt(
        _robust_pos_norm(iso_hg, foot) * _robust_pos_norm(g400_hg, foot) * _robust_pos_norm(g1800_hg, foot) + np.float32(1e-8)
    ).astype(np.float32)
    mm[38] = np.where(foot, grav_persist, 0.0)

    # Include GeoDAWN 150m upward-continued TMI if present
    ext_tif = ddir / "external" / "geodawn_extensions_u8.tif"
    with rasterio.open(ext_tif) as ds_ext:
        thk_u8 = ds_ext.read(1).astype(np.float32)
        uk_u8 = ds_ext.read(2).astype(np.float32)
        uth_u8 = ds_ext.read(3).astype(np.float32)
        tmi150_u8 = ds_ext.read(4).astype(np.float32)

    r400_hg = _grad_mag_and_vec(rtp_u400, 1.0)[0]
    r1800_hg = _grad_mag_and_vec(rtp_u1800, 1.0)[0]
    t150_hg = _grad_mag_and_vec(tmi150_u8, 1.0)[0]
    rtp_persist = np.power(
        _robust_pos_norm(rtp_edge, foot)
        * _robust_pos_norm(t150_hg, foot)
        * _robust_pos_norm(r400_hg, foot)
        * _robust_pos_norm(r1800_hg, foot)
        + np.float32(1e-10),
        0.25,
    ).astype(np.float32)
    mm[39] = np.where(foot, rtp_persist, 0.0)

    # 40: Listric/normal hanging-wall dip-migration asymmetry (alignment of deep->shallow shift with cover deepening)
    # Normal fault dipping into basin: deep z=1800m anomaly shifts basinward (where depth_to_base_surf increases)
    d_norm = np.hypot(depth_gx, depth_gy) + np.float32(1e-5)
    g0_shift_x = sobel(iso_hg, axis=1).astype(np.float32)
    g0_shift_y = sobel(iso_hg, axis=0).astype(np.float32)
    dip_align = np.maximum(-(g0_shift_x * depth_gx + g0_shift_y * depth_gy) / d_norm, np.float32(0.0))
    listric_mig = (_robust_pos_norm(dip_align, foot) * grav_persist).astype(np.float32)
    mm[40] = np.where(foot, listric_mig, 0.0)
    del grav_u400, grav_u1800, rtp_u400, rtp_u1800, g400_hg, r400_hg, r1800_hg, t150_hg, tmi150_u8, g0_shift_x, g0_shift_y, dip_align
    gc.collect()

    # 41: Piedmont basement-bench inflection (-Laplacian of depth_to_base_surf in 40..650m piedmont zone)
    piedmont_weight = np.exp(-0.5 * ((np.clip(depth_b, 0.0, 1500.0) - np.float32(220.0)) / np.float32(240.0)) ** 2).astype(np.float32)
    bench_inflect = _robust_pos_norm(_hessian_ridge(depth_edge, 2.0, bright=True), foot) * (
        np.float32(0.35) + np.float32(0.65) * piedmont_weight
    )
    mm[41] = np.where(foot, bench_inflect, 0.0)

    # 42: Smectite clay-cap lateral conductivity boundary (vetoed on flat playas)
    cond_ridge = _robust_pos_norm(_hessian_ridge(cond_edge, 1.8, bright=True), foot) * playa_gate
    mm[42] = np.where(foot, cond_ridge, 0.0)

    # 43 & 44: GeoDAWN 4-Block Contractor-Standardized 214Bi Radon & K/Th Potassic-Silicic Alteration
    rad_tif = ddir / "external" / "geodawn_rad_u8.tif"
    blk_tif = ddir / "external" / "acquisition_block_id_100m.tif"
    with rasterio.open(rad_tif) as ds_rad:
        k_u8 = ds_rad.read(1).astype(np.float32)
        th_u8 = ds_rad.read(2).astype(np.float32)
        u_u8 = ds_rad.read(3).astype(np.float32)
        tc_rad_u8 = ds_rad.read(4).astype(np.float32)
    with rasterio.open(blk_tif) as ds_blk:
        blk_id = ds_blk.read(1)

    rad_valid = foot & (tc_rad_u8 > 0) & (blk_id > 0)
    kz = _block_zscore(k_u8, blk_id, rad_valid)
    thz = _block_zscore(th_u8, blk_id, rad_valid)
    uz = _block_zscore(u_u8, blk_id, rad_valid)
    tcz = _block_zscore(tc_rad_u8, blk_id, rad_valid)
    ukz = _block_zscore(uk_u8, blk_id, rad_valid)
    uthz = _block_zscore(uth_u8, blk_id, rad_valid)

    # 214Bi radon degassing excess over thorium lithologic baseline, sharpened onto linear fault crests
    bi214_excess = np.maximum(uz - np.float32(0.65) * thz + np.float32(0.35) * uthz + np.float32(0.25) * ukz, np.float32(0.0))
    radon_ridge = (
        np.float32(0.5) * _robust_pos_norm(_hessian_ridge(bi214_excess, 1.6, bright=True), foot)
        + np.float32(0.5) * _robust_pos_norm(_grad_mag_and_vec(bi214_excess, 1.2)[0], foot)
    ) * playa_gate
    mm[43] = np.where(foot, radon_ridge, 0.0)

    # Concentric Difference-of-Gaussians potassic (K-high / Th-low) + silicified low-TC core zonation
    k_over_th = kz - np.float32(0.6) * thz
    silica_core = gaussian_filter(-tcz, 1.5, mode="nearest") - gaussian_filter(-tcz, 6.0, mode="nearest")
    potassic_halo = gaussian_filter(k_over_th, 2.0, mode="nearest") - gaussian_filter(k_over_th, 7.0, mode="nearest")
    kth_alt = (
        np.float32(0.55) * _robust_pos_norm(potassic_halo, foot) + np.float32(0.45) * _robust_pos_norm(silica_core, foot)
    ) * playa_gate
    mm[44] = np.where(foot, kth_alt, 0.0)
    mm.flush()
    del k_u8, th_u8, u_u8, tc_rad_u8, thk_u8, uk_u8, uth_u8, kz, thz, uz, tcz, ukz, uthz, bi214_excess, k_over_th, silica_core, potassic_halo
    gc.collect()
    log("  built potential-field upward-continuation, PPGR, and GeoDAWN block-normalized radiometric channels")

    # Local potential-field structural strike unit double-angle (cos 2*theta_strike, sin 2*theta_strike)
    # Gradient normal is (gx, gy), so strike tangent is (-gy, gx) -> cos(2*theta_s) = (gy^2 - gx^2)/(gx^2+gy^2)
    pf_gx = np.float32(0.65) * g1800_gx + np.float32(0.35) * rtp_gx
    pf_gy = np.float32(0.65) * g1800_gy + np.float32(0.35) * rtp_gy
    pf_n2 = pf_gx * pf_gx + pf_gy * pf_gy + np.float32(1e-8)
    cos2t_pf = gaussian_filter((pf_gy * pf_gy - pf_gx * pf_gx) / pf_n2, 2.5, mode="nearest").astype(np.float32)
    sin2t_pf = gaussian_filter((-2.0 * pf_gx * pf_gy) / pf_n2, 2.5, mode="nearest").astype(np.float32)
    del pf_gx, pf_gy, pf_n2, g1800_gx, g1800_gy, g1800_hg
    gc.collect()

    # 45, 46, 47: INGENIOUS GDR #1391 2m Temperature Probes (F2mDAB), Quaternary Sinter/Breccia, Quartz Geothermometers
    f2m_seeds, paleo_seeds, qtz_seeds = _rasterize_ingenious_geothermal_layers(ddir, foot, aff)
    f2m_plume = _robust_pos_norm(_anisotropic_strike_diffuse(f2m_seeds, cos2t_pf, sin2t_pf, foot, sigma_iso=3.0, along_len_px=14), foot)
    paleo_plume = _robust_pos_norm(_anisotropic_strike_diffuse(paleo_seeds, cos2t_pf, sin2t_pf, foot, sigma_iso=3.5, along_len_px=16), foot)
    qtz_plume = _robust_pos_norm(_anisotropic_strike_diffuse(qtz_seeds, cos2t_pf, sin2t_pf, foot, sigma_iso=4.0, along_len_px=16), foot)
    mm[45] = f2m_plume
    mm[46] = paleo_plume
    mm[47] = qtz_plume
    mm.flush()
    del f2m_seeds, paleo_seeds, qtz_seeds
    gc.collect()
    log("  built INGENIOUS F2mDAB, Quaternary sinter/breccia, and quartz-geothermometer strike plumes")

    # 48: Walker Lane / Great Basin Transtensional Strain-Dilation x Microseismicity Lateral Gradient
    dil_pos = _robust_pos_norm(kept[8], foot)
    shr_pos = _robust_pos_norm(kept[7], foot)
    inv2_pos = _robust_pos_norm(kept[4], foot)
    seis_edge = _robust_pos_norm(_grad_mag_and_vec(kept[16], 2.0)[0], foot)
    # Favor NNE/NNW Great Basin / Walker Lane strikes (cos(2*theta_s) < 0 corresponds to |theta_s| near 60..120 deg N-S)
    ns_favor = np.clip(np.float32(0.55) - np.float32(0.45) * cos2t_pf, np.float32(0.15), np.float32(1.0))
    walker_coup = ((np.float32(0.35) * dil_pos + np.float32(0.35) * shr_pos + np.float32(0.30) * inv2_pos) * (np.float32(0.5) + np.float32(0.5) * seis_edge) * ns_favor).astype(np.float32)
    mm[48] = np.where(foot, walker_coup, 0.0)
    del dil_pos, shr_pos, inv2_pos, seis_edge, ns_favor

    # 49: Non-Fault Mimic Detector (Lake Lahontan Pluvial Shorelines + US Census TIGER Roads)
    road_tif = ddir / "external" / "tiger_road_distance_m.tif"
    if road_tif.is_file():
        with rasterio.open(road_tif) as ds_rd:
            rd_raw = ds_rd.read(1).astype(np.float32)
        rd_m = np.where(np.isfinite(rd_raw) & (rd_raw >= 0.0), rd_raw, np.float32(1e5))
        near_road = np.exp(-0.5 * (rd_m / np.float32(140.0)) ** 2).astype(np.float32)
        del rd_raw, rd_m
    else:
        near_road = np.zeros((h, w), dtype=np.float32)

    # Pluvial shoreline mimic: sharp small-scale DEM step inside low-lying basin with near-zero gravity/basement gradient
    dem_step = _robust_pos_norm(mm[21], foot)  # ridge_s1
    weak_crustal = np.exp(-3.0 * (grav_persist + ppgr_ridge)).astype(np.float32)
    low_relief_basin = (depth_b > np.float32(180.0)).astype(np.float32)
    confound_score = np.clip(
        np.nan_to_num(np.float32(0.55) * near_road + np.float32(0.45) * (dem_step * weak_crustal * low_relief_basin), nan=0.0),
        np.float32(0.0),
        np.float32(1.0),
    ).astype(np.float32)
    mm[49] = np.where(foot, confound_score, 0.0)

    # 50 & 51: 1.2 km Subsurface Anisotropic Corridor & Unified LiDAR-Free Geothermal Conduit Crest
    grav_edge_norm = _robust_pos_norm(grav_edge, foot)
    raw_subsurf_crest = (
        np.float32(0.24) * grav_persist
        + np.float32(0.20) * grav_edge_norm
        + np.float32(0.18) * hmas_trough
        + np.float32(0.14) * ppgr_ridge
        + np.float32(0.10) * radon_ridge
        + np.float32(0.08) * bench_inflect
        + np.float32(0.06) * walker_coup
    ) * playa_gate * (np.float32(1.0) - np.float32(0.35) * confound_score)
    raw_subsurf_crest = np.nan_to_num(raw_subsurf_crest, nan=0.0, posinf=0.0, neginf=0.0).astype(np.float32)

    aniso_sub = _robust_pos_norm(
        _anisotropic_strike_diffuse(raw_subsurf_crest, cos2t_pf, sin2t_pf, foot, sigma_iso=1.0, along_len_px=6), foot
    )
    mm[50] = np.nan_to_num(aniso_sub, nan=0.0)

    upflow_boost = (
        np.float32(1.0)
        + np.float32(0.40) * f2m_plume
        + np.float32(0.35) * paleo_plume
        + np.float32(0.25) * qtz_plume
        + np.float32(0.22) * kth_alt
        + np.float32(0.15) * cond_ridge
    )
    # Combine subsurface structural crests + 100m detrended topographic tectonic crests (still 100% 1m-LiDAR-free!)
    dem_tectonic_ridge = (
        np.float32(0.45) * _robust_pos_norm(mm[24], foot)  # relief5
        + np.float32(0.35) * _robust_pos_norm(mm[18], foot)  # det_elev_slope
        + np.float32(0.20) * _robust_pos_norm(-mm[20], foot)  # -curv_s2
    ) * (np.float32(1.0) - np.float32(0.55) * confound_score) * playa_gate

    unsup_conduit = _robust_pos_norm(
        (np.float32(0.55) * raw_subsurf_crest + np.float32(0.23) * aniso_sub + np.float32(0.22) * dem_tectonic_ridge)
        * upflow_boost,
        foot,
    )
    mm[51] = np.nan_to_num(unsup_conduit, nan=0.0)
    del grav_edge_norm, raw_subsurf_crest, aniso_sub, upflow_boost, dem_tectonic_ridge, f2m_plume, paleo_plume, qtz_plume
    gc.collect()

    # 52..57: USGS 3DEP 1m LiDAR Scarp Channels (strictly quarantined to M_Full inside lidar_valid == 1)
    lid_tif = ddir / "external" / "lidar_scarp_features_u8.tif"
    with rasterio.open(lid_tif) as ds_lid:
        l_ex = ds_lid.read(1).astype(np.float32) * np.float32(1.0 / 255.0)
        l_step = ds_lid.read(3).astype(np.float32) * np.float32(1.0 / 255.0)
        l_down = ds_lid.read(6).astype(np.float32) * np.float32(1.0 / 255.0)
        l_up = ds_lid.read(7).astype(np.float32) * np.float32(1.0 / 255.0)
        l_rel = ds_lid.read(9).astype(np.float32) * np.float32(1.0 / 255.0)
        l_coh = ds_lid.read(10).astype(np.float32) * np.float32(1.0 / 255.0)
        l_val = (ds_lid.read(12) > 0) & foot

    mm[52] = np.where(l_val, l_ex, 0.0)
    mm[53] = np.where(l_val, l_step, 0.0)
    mm[54] = np.where(l_val, l_coh, 0.0)
    mm[55] = np.where(l_val, l_rel, 0.0)
    # Tectonic scarp asymmetry: single-facing |down - up| * step * coherence, vetoed by road/shoreline confound
    asymm = np.abs(l_down - l_up) * (np.float32(0.4) + np.float32(0.6) * l_step) * (np.float32(0.3) + np.float32(0.7) * l_coh)
    asymm_chain = uniform_filter(np.where(l_val, asymm, 0.0), size=5, mode="constant") * (np.float32(1.0) - np.float32(0.6) * confound_score)
    mm[56] = np.where(l_val, np.nan_to_num(_robust_pos_norm(asymm_chain, l_val), nan=0.0), 0.0)
    mm[57] = l_val.astype(np.float32)

    # Final strict non-finite sweep across all 58 channels
    for ci in range(len(ALL_CHANNELS)):
        plane = mm[ci]
        if not np.isfinite(plane).all():
            mm[ci] = np.nan_to_num(plane, nan=0.0, posinf=0.0, neginf=0.0)

    mm.flush()
    del kept, mm
    gc.collect()

    meta = {
        "schema_version": 1,
        "lane_id": "H-K1-1-HMAS-SINTER-ENV",
        "stack_path": str(stack_path),
        "layout": "CHW",
        "shape": [len(ALL_CHANNELS), h, w],
        "n_channels": len(ALL_CHANNELS),
        "n_msub_lidar_free_channels": len(MSUB_INDICES),
        "channels": list(ALL_CHANNELS),
        "lidar_only_indices": sorted(LIDAR_GLOBAL_INDICES),
        "msub_indices": list(MSUB_INDICES),
        "footprint_pixels": int(foot.sum()),
        "lidar_valid_pixels": int(l_val.sum()),
        "lidar_gap_fraction": round(float(1.0 - l_val[foot].mean()), 6),
        "catalogue_derived_channels": 0,
    }
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    log(f"[features] Saved 58-channel float32 stack & receipt -> {meta_path}")
    return meta
