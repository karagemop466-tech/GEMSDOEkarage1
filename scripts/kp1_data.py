"""Shared data access for lane K-PROXY-DETECT (H-KP1).

Everything here is a thin, declared wrapper over the *pinned* inputs that the
vendored shared template already knows about:

* ``data/official/training_features.tif``  sha256 4371c82e…3bc5  (19 bands)
* ``data/official/existing_faults.tif``    sha256 7ba308cc…4093  (== labels.tif)
* ``data/official/sample_submission.tif``  sha256 2176d08e…5cbc  (grid template)
* ``data/external/derived_sgmc_faults_100m_u8.tif`` sha256 643cbe99…2da0
  (off-catalogue proxy; the same digest is the ``derived_sgmc_faults_100m.tif``
  pin inside ``vendor/gems57/prepare_data.py``)
* ``data/external/lidar_scarp_features_u8.tif``     sha256 d580bb8b…5568
* ``data/external/geodawn_rad_u8.tif``              sha256 c22420f7…a682

No file here is organizer-authenticated: the DrivenData data page is
login-walled (https://www.drivendata.org/competitions/306/competition-doe-gems/data/).
The digests prove byte consistency with the pinned mirrors, nothing more.

Band-order note: the order below was read back from the file's own
``descriptions`` with rasterio (see ``evidence/kp1_band_audit.json``); it is not
copied from documentation.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OFFICIAL = DATA / "official"
EXTERNAL = DATA / "external"
CACHE = ROOT / ".cache" / "kp1"

SHAPE = (3730, 3292)
EPSG = 32611
TRANSFORM = (100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)

SHA = {
    "training_features.tif": "4371c82e3b8339b807bdffcf4ef59a225520fe2988d521be208ae33743123bc5",
    "existing_faults.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
    "labels.tif": "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093",
    "sample_submission.tif": "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc",
    "derived_sgmc_faults_100m_u8.tif": "643cbe992ef4ba37588fb469163ed8291e3ceb23d6c1f78a3cfaa462430c2da0",
    "lidar_scarp_features_u8.tif": "d580bb8bdcdb941e32fefb8b38044bc5bf04e199bf2e83498c3576e6fc465568",
    "geodawn_rad_u8.tif": "c22420f75999030d7cc65c9e31e50d232ea6158423bca051613a18a8b20ba682",
    "gdr_qfaults_traces.csv": "9702f2e5c382a4f472ae834d22b94990983b059677a37adfafd51c50f75e643c",
}

# 1-based band index -> name, transcribed from the file's band descriptions.
FEATURE_BANDS = {
    1: "mag_anom", 2: "rtp", 3: "tmi_hg", 4: "geod_2ndinv",
    5: "iso_grav_anom_slope", 6: "tc", 7: "geod_shearrate", 8: "geod_dilaterate",
    9: "tmi_vg", 10: "deq_n100a15", 11: "iso_grav_anom_vg", 12: "det_elev",
    13: "iso_grav_anom", 14: "tmi", 15: "depth_to_base_surf", 16: "ieq_n100a15",
    17: "cond_surf", 18: "iso_grav_anom_hg", 19: "det_elev_slope",
}
LIDAR_BANDS = ["ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max",
               "downface_max", "upface_max", "cross_max", "relief", "coh100",
               "strike", "valid"]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_inputs() -> dict:
    """Fail closed if any pinned byte string differs."""
    paths = {**{n: OFFICIAL / n for n in ("training_features.tif", "existing_faults.tif",
                                          "labels.tif", "sample_submission.tif")},
             **{n: EXTERNAL / n for n in ("derived_sgmc_faults_100m_u8.tif",
                                          "lidar_scarp_features_u8.tif",
                                          "geodawn_rad_u8.tif", "gdr_qfaults_traces.csv")}}
    out = {}
    for name, path in paths.items():
        if not path.is_file():
            raise SystemExit(f"missing pinned input: {path}")
        got = sha256(path)
        if got != SHA[name]:
            raise SystemExit(f"{path}: sha256 {got} != pinned {SHA[name]}")
        out[name] = {"sha256": got, "bytes": path.stat().st_size}
    return out


def _raster(path: Path, band: int = 1) -> np.ndarray:
    with rasterio.open(path) as src:
        if (src.height, src.width) != SHAPE:
            raise ValueError(f"{path}: shape {(src.height, src.width)} != {SHAPE}")
        if tuple(float(v) for v in src.transform)[:6] != TRANSFORM:
            raise ValueError(f"{path}: transform {tuple(src.transform)} != {TRANSFORM}")
        if str(src.crs) != f"EPSG:{EPSG}":
            raise ValueError(f"{path}: crs {src.crs}")
        return src.read(band)


def footprint() -> np.ndarray:
    """Scored study-area cells: finite values in the organizer sample raster."""
    sub = _raster(OFFICIAL / "sample_submission.tif").astype(np.float32)
    return np.isfinite(sub)


def catalogue() -> np.ndarray:
    """Mapped USGS/INGENIOUS catalogue inside the footprint (60,988 px)."""
    cat = _raster(OFFICIAL / "existing_faults.tif")
    return (cat > 0) & footprint()


def proxy_truth(min_gap_px: int = 0) -> np.ndarray:
    """Independent-compilation fault pixels (USGS SGMC-derived) minus the catalogue.

    ``min_gap_px`` additionally removes proxy pixels within that many pixels of a
    catalogue pixel, giving a 'detached' variant that cannot be recovered by
    proximity to a mapped trace.
    """
    from scipy import ndimage as ndi
    sg = _raster(EXTERNAL / "derived_sgmc_faults_100m_u8.tif") > 0
    cat = catalogue()
    out = sg & ~cat & footprint()
    if min_gap_px:
        d = ndi.distance_transform_edt(~cat)
        out &= d > float(min_gap_px)
    return out


_BAND_CACHE = {}


def band(name: str) -> np.ndarray:
    """One competition band (float32, NaN where GDAL wrote its float sentinel)."""
    if name in _BAND_CACHE:
        return _BAND_CACHE[name]
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"band_{name}.npy"
    if path.is_file():
        arr = np.load(path, mmap_mode="r")
        _BAND_CACHE[name] = arr
        return arr
    index = {v: k for k, v in FEATURE_BANDS.items()}[name]
    out = np.lib.format.open_memmap(path, mode="w+", dtype=np.float32, shape=SHAPE)
    src = OFFICIAL / "training_features.tif"
    with rasterio.open(src) as ds:
        for y in range(0, SHAPE[0], 256):
            h = min(256, SHAPE[0] - y)
            blk = ds.read(index, window=Window(0, y, SHAPE[1], h), masked=True)
            a = blk.filled(np.nan).astype(np.float32)
            a[~np.isfinite(a) | (np.abs(a) > 1e30)] = np.nan
            out[y:y + h] = a
    out.flush()
    del out
    arr = np.load(path, mmap_mode="r")
    _BAND_CACHE[name] = arr
    return arr


def lidar_band(name: str) -> np.ndarray:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"lidar_{name}.npy"
    if path.is_file():
        return np.load(path, mmap_mode="r")
    index = LIDAR_BANDS.index(name) + 1
    a = _raster(EXTERNAL / "lidar_scarp_features_u8.tif", index).astype(np.float32)
    np.save(path, a)
    return np.load(path, mmap_mode="r")


def rad_band(index: int) -> np.ndarray:
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / f"rad_{index}.npy"
    if path.is_file():
        return np.load(path, mmap_mode="r")
    a = _raster(EXTERNAL / "geodawn_rad_u8.tif", index).astype(np.float32)
    np.save(path, a)
    return np.load(path, mmap_mode="r")


def robust_z(a: np.ndarray, mask: np.ndarray, clip: float = 8.0) -> np.ndarray:
    """Median/MAD z-score inside ``mask``; NaN -> 0; clipped to ±``clip``."""
    a = np.asarray(a, np.float32)
    v = a[mask]
    v = v[np.isfinite(v)]
    out = np.zeros(a.shape, np.float32)
    if v.size == 0:
        return out
    med = float(np.median(v))
    mad = float(np.median(np.abs(v - med)))
    scale = 1.4826 * mad if mad > 0 else (float(v.std()) or 1.0)
    z = (a - med) / scale
    z[~np.isfinite(z)] = 0.0
    np.clip(z, -clip, clip, out=z)
    out[mask] = z[mask]
    return out


def write_report(name: str, payload: dict) -> Path:
    (ROOT / "evidence").mkdir(exist_ok=True)
    path = ROOT / "evidence" / name
    path.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n")
    return path
