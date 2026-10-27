"""Grid template, footprint, catalogue and per-band cache for the GEMS competition rasters.

Everything here is read from the SHA-256-verified files restored by ``scripts/restore_data.py``.
The official grid (read from the bytes, not transcribed):

* shape 3730 rows x 3292 cols, EPSG:32611, transform (100, 0, 243350, 0, -100, 4508550)
* footprint = finite pixels of ``sample_submission.tif`` (5,167,373 px)
* catalogue = ``labels.tif`` > 0 (60,988 px); ``existing_faults.tif`` is byte-identical
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / ".cache" / "gems_data"
BANDS = ROOT / ".cache" / "bands"
PIXEL_M = 100.0

BAND_NAMES = [
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope", "tc", "geod_shearrate",
    "geod_dilaterate", "tmi_vg", "deq_n100a15", "iso_grav_anom_vg", "det_elev", "iso_grav_anom",
    "tmi", "depth_to_base_surf", "ieq_n100a15", "cond_surf", "iso_grav_anom_hg", "det_elev_slope",
]
LIDAR_NAMES = ["ex_max", "ex_mean", "step_max", "lapneg_max", "lappos_max", "downface_max",
               "upface_max", "cross_max", "relief", "coh100", "strike", "valid"]
RAD_NAMES = ["K", "Th", "U", "TC"]


def template_profile() -> dict:
    import rasterio

    with rasterio.open(DATA / "sample_submission.tif") as src:
        return {"crs": src.crs, "transform": src.transform, "width": src.width, "height": src.height,
                "dtype": "float32", "count": 1}


def prepare_bands(force: bool = False) -> dict:
    """Write every official band, the footprint and the catalogue as .npy files (memmap-friendly)."""
    import rasterio

    BANDS.mkdir(parents=True, exist_ok=True)
    meta_path = BANDS / "meta.json"
    if meta_path.exists() and not force:
        return json.loads(meta_path.read_text())
    with rasterio.open(DATA / "sample_submission.tif") as src:
        ss = src.read(1)
        foot = np.isfinite(ss)
        prof = {"crs": str(src.crs), "transform": list(src.transform)[:6], "width": src.width, "height": src.height}
    np.save(BANDS / "footprint.npy", foot)
    with rasterio.open(DATA / "labels.tif") as src:
        cat = src.read(1) > 0
    np.save(BANDS / "catalogue.npy", cat)
    meta = {"profile": prof, "footprint_px": int(foot.sum()), "catalogue_px": int(cat.sum()),
            "catalogue_in_footprint_px": int((cat & foot).sum()), "bands": {}}
    with rasterio.open(DATA / "training_features.tif") as src:
        nd = src.nodata
        for i, name in enumerate(BAND_NAMES, start=1):
            desc = src.descriptions[i - 1]
            assert desc.split(" - ")[0] == name, (desc, name)
            b = src.read(i).astype(np.float32)
            valid = np.isfinite(b) & (b != nd)
            b[~valid] = np.nan
            np.save(BANDS / f"b{i:02d}_{name}.npy", b)
            meta["bands"][name] = {"index": i, "description": desc, "valid_in_footprint": int((valid & foot).sum())}
    lid = DATA / "external" / "lidar_scarp_features_u8.tif"
    if lid.exists():
        with rasterio.open(lid) as src:
            assert list(src.descriptions) == LIDAR_NAMES
            for i, name in enumerate(LIDAR_NAMES, start=1):
                np.save(BANDS / f"lidar_{name}.npy", src.read(i))
        meta["lidar"] = LIDAR_NAMES
    rad = DATA / "external" / "geodawn_rad_u8.tif"
    if rad.exists():
        with rasterio.open(rad) as src:
            assert list(src.descriptions) == RAD_NAMES
            for i, name in enumerate(RAD_NAMES, start=1):
                np.save(BANDS / f"rad_{name}.npy", src.read(i))
        meta["radiometrics"] = RAD_NAMES
    meta_path.write_text(json.dumps(meta, indent=2) + "\n")
    return meta


def band(name: str) -> np.ndarray:
    """Load an official band by name (float32, NaN where invalid)."""
    i = BAND_NAMES.index(name) + 1
    return np.load(BANDS / f"b{i:02d}_{name}.npy")


def lidar(name: str) -> np.ndarray:
    return np.load(BANDS / f"lidar_{name}.npy")


def footprint() -> np.ndarray:
    return np.load(BANDS / "footprint.npy")


def catalogue() -> np.ndarray:
    return np.load(BANDS / "catalogue.npy")
