"""Physics-only predictor planes for lane H-KP1 (cached, one .npy per plane).

Design rule that separates this lane from the fleet's catalogue-anatomy lanes:
**no plane in ``PLANES`` is derived from the fault catalogue.** They are all
remote-sensing / geophysical / hydrologic measurements of the ground. The mapped
catalogue enters only twice, both declared:

* as the *label* during training and as the scored truth in the spatially blocked
  holdout (that is the instrument, not a predictor), and
* as a *suppression mask* at emission time (``d_cat`` — the empirical evidence in
  ``evidence/kp1_exp1_forensics.json`` is that the two best-scoring registry files
  place exactly 0.0 % of their dots within 2 px of the catalogue).

New layers relative to the 19-band organizer stack (all from the pinned GeoDAWN
release, DOI 10.5066/P93LGLVQ):
* ``up150_grad``  — horizontal gradient of TMI upward-continued to 150 m
  (channel 4 of ``geodawn_extensions_u8.tif``). Upward continuation attenuates
  shallow, near-surface sources, so this plane emphasises deeper/basement
  structure that is otherwise buried by the near-surface magnetic texture.
* ``ThK``, ``UK``, ``UTh`` — contractor radiometric ratio grids (channels 1-3).
  Potassium metasomatism (adularia/sericite) in hydrothermal alteration halos
  lowers Th/K and raises K; these ratios are the classical alteration mapping
  products and are absent from the provided 19 bands.
* ``spring_kde``  — thermal-spring / well density (``gdr_wellspring_in_footprint.csv``,
  27,092 records with ``thermalclass`` and ``temp_c``). Fluid conduits in the
  Great Basin discharge along fault damage zones and at fault intersections.
* ``vent_kde``    — Quaternary volcanic vent density (21 vents). Vents in the
  northern Walker Lane align on structural trends.

Named non-fault mimics (declared, not hidden): playa/evaporite clay mineralogy
produces low Th/K with no fault (clay, not alteration); Quaternary basalt flows
produce high K and strong magnetic signal; upward continuation rings around
large magnetic bodies can mimic a linear gradient; springs also discharge from
permeable basin-fill contacts and from playa margins.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import ndimage as ndi

from . import kp1_data as D

PLANE_DIR = D.CACHE / "planes"

# name -> (source description, builder key)
PLANES = {
    # organizer 19-band stack, robust-z scored inside the footprint
    "tmi_hg": "official band 3 (TMI horizontal gradient)",
    "tmi_vg": "official band 9 (TMI vertical gradient)",
    "tc": "official band 6 (tilt derivative / total curvature)",
    "iso_grav_anom_hg": "official band 18 (isostatic gravity horizontal gradient)",
    "iso_grav_anom_slope": "official band 5",
    "det_elev_slope": "official band 19",
    "geod_2ndinv": "official band 4 (strain-rate second invariant)",
    "geod_shearrate": "official band 7",
    "ieq": "official band 16 (earthquake density)",
    "deq": "official band 10 (distance to earthquake)",
    "cond_surf": "official band 17 (conductivity surface)",
    "depth_to_base_surf": "official band 15",
    "det_elev": "official band 12",
    # derived
    "curv2": "Laplacian of det_elev at sigma 2 px (scarp curvature)",
    "base_edge": "gradient magnitude of depth_to_base_surf (basement step)",
    "elev_ridge3": "structure-tensor ridge strength of det_elev at sigma 3 px",
    # 1 m LiDAR scarp metrics (12-band uint8 product)
    "lidar_step": "lidar band 3 step_max / 255",
    "lidar_lapneg": "lidar band 4 lapneg_max / 255",
    "lidar_coh": "lidar band 10 coh100 / 255",
    "lidar_ex": "lidar band 1 ex_max / 255",
    "lidar_relief": "lidar band 9 relief / 255",
    "lidar_valid": "lidar band 12 valid mask (0/1)",
    # GeoDAWN extensions (not in the 19-band stack)
    "up150_grad": "horizontal gradient of TMI upward-continued 150 m",
    "ThK": "contractor Th/K ratio grid (u8-quantised)",
    "UK": "contractor U/K ratio grid",
    "UTh": "contractor U/Th ratio grid",
    # hydrologic / volcanic
    "spring_kde": "thermal spring & well kernel density (sigma 3 px)",
    "spring_hot": "hot-spring-only kernel density (sigma 3 px)",
    "vent_kde": "volcanic vent kernel density (sigma 6 px)",
}


def _z(name: str, arr: np.ndarray, mask: np.ndarray) -> np.ndarray:
    return D.robust_z(arr, mask)


def _ext(index: int) -> np.ndarray:
    import rasterio
    with rasterio.open(D.EXTERNAL / "geodawn_extensions_u8.tif") as ds:
        return ds.read(index).astype(np.float32)


def _kde(rows: np.ndarray, cols: np.ndarray, weights: np.ndarray | None, sigma: float,
         shape: tuple[int, int] = D.SHAPE) -> np.ndarray:
    acc = np.zeros(shape, np.float32)
    ok = (rows >= 0) & (rows < shape[0]) & (cols >= 0) & (cols < shape[1])
    w = np.ones(rows.size, np.float32) if weights is None else weights.astype(np.float32)
    np.add.at(acc, (rows[ok], cols[ok]), w[ok])
    if sigma > 0:
        acc = ndi.gaussian_filter(acc, sigma, mode="constant").astype(np.float32)
    return acc


def _springs() -> tuple[np.ndarray, np.ndarray]:
    df = pd.read_csv(D.EXTERNAL / "gdr_wellspring_in_footprint.csv")
    rows = pd.to_numeric(df["row"], errors="coerce").to_numpy()
    cols = pd.to_numeric(df["col"], errors="coerce").to_numpy()
    temp = pd.to_numeric(df["temp_c"], errors="coerce").to_numpy(dtype=float)
    thermal = df["thermalclass"].astype(str).str.lower().to_numpy()
    hot = np.where(np.isin(thermal, ("hot", "boiling", "steam")), 1.0,
                   np.where(np.isfinite(temp), np.clip((temp - 20.0) / 60.0, 0.0, 1.0), 0.25))
    ok = np.isfinite(rows) & np.isfinite(cols)
    return (rows[ok].astype(np.int64), cols[ok].astype(np.int64)), hot[ok]


def build(names: list[str] | None = None) -> dict:
    """Write (or reuse) every requested plane and return a small receipt."""
    PLANE_DIR.mkdir(parents=True, exist_ok=True)
    mask = D.footprint()
    names = list(PLANES) if names is None else names
    receipt = {}
    for name in names:
        path = PLANE_DIR / f"{name}.npy"
        if path.is_file():
            receipt[name] = {"path": str(path.relative_to(D.ROOT)), "cached": True,
                             "source": PLANES[name]}
            continue
        if name == "curv2":
            z = np.asarray(D.band("det_elev"), np.float32)
            plane = _z(name, np.abs(ndi.gaussian_filter(z, 2.0, order=(0, 2)) +
                                    ndi.gaussian_filter(z, 2.0, order=(2, 0))), mask)
        elif name == "base_edge":
            z = np.asarray(D.band("depth_to_base_surf"), np.float32)
            gy, gx = np.gradient(ndi.gaussian_filter(z, 1.5))
            plane = _z(name, np.hypot(gx, gy), mask)
        elif name == "elev_ridge3":
            z = np.asarray(D.band("det_elev"), np.float32)
            gy, gx = np.gradient(ndi.gaussian_filter(z, 3.0))
            jxx = ndi.gaussian_filter(gx * gx, 6.0)
            jyy = ndi.gaussian_filter(gy * gy, 6.0)
            jxy = ndi.gaussian_filter(gx * gy, 6.0)
            tr = jxx + jyy
            disc = np.sqrt(np.maximum((jxx - jyy) ** 2 / 4.0 + jxy ** 2, 0.0))
            plane = _z(name, (tr / 2.0 + disc) - (tr / 2.0 - disc), mask)
        elif name in ("lidar_step", "lidar_lapneg", "lidar_coh", "lidar_ex",
                      "lidar_relief", "lidar_valid"):
            band = {"lidar_step": "step_max", "lidar_lapneg": "lapneg_max",
                    "lidar_coh": "coh100", "lidar_ex": "ex_max",
                    "lidar_relief": "relief", "lidar_valid": "valid"}[name]
            plane = np.asarray(D.lidar_band(band), np.float32) / 255.0
        elif name == "up150_grad":
            a = _ext(4)
            a = np.where(a > 0, a, np.nan).astype(np.float32)
            filled = a.copy()
            bad = ~np.isfinite(filled)
            if bad.any():
                idx = ndi.distance_transform_edt(bad, return_distances=False, return_indices=True)
                filled = filled[tuple(idx)]
            gy, gx = np.gradient(ndi.gaussian_filter(filled, 1.0))
            plane = _z(name, np.hypot(gx, gy), mask)
        elif name in ("ThK", "UK", "UTh"):
            plane = _z(name, _ext({"ThK": 1, "UK": 2, "UTh": 3}[name]), mask)
        elif name in ("spring_kde", "spring_hot"):
            (rows, cols), hot = _springs()
            if name == "spring_kde":
                plane = _z(name, _kde(rows, cols, hot + 0.25, 3.0), mask)
            else:
                sel = hot >= 0.9
                plane = _z(name, _kde(rows[sel], cols[sel], None, 3.0), mask)
        elif name == "vent_kde":
            df = pd.read_csv(D.EXTERNAL / "gdr_volcanic_vents_in_footprint.csv")
            rows = pd.to_numeric(df["row"], errors="coerce").to_numpy()
            cols = pd.to_numeric(df["col"], errors="coerce").to_numpy()
            ok = np.isfinite(rows) & np.isfinite(cols)
            plane = _z(name, _kde(rows[ok].astype(np.int64), cols[ok].astype(np.int64), None, 6.0), mask)
        else:
            src = {"ieq": "ieq_n100a15", "deq": "deq_n100a15"}.get(name, name)
            plane = _z(name, np.asarray(D.band(src), np.float32), mask)
        plane = np.asarray(plane, np.float32)
        plane[~mask] = 0.0
        np.save(path, plane)
        receipt[name] = {"path": str(path.relative_to(D.ROOT)), "cached": False,
                         "source": PLANES[name]}
    return receipt


def load(name: str) -> np.ndarray:
    return np.load(PLANE_DIR / f"{name}.npy", mmap_mode="r")


if __name__ == "__main__":
    print(json.dumps(build(), indent=2))
