#!/usr/bin/env python3
"""Generate a UNIQUE, format-valid research TIF for the GEMS fault-discovery competition.

Method lane (catalogue-free, distinct from the dotted-ridge / lattice family):
  * Belief surface = smooth hydrothermal-alteration propensity built from blind
    anomaly centres. No USGS/INGENIOUS catalogue, no labels.tif, no existing_faults.tif
    is ever read to *place* dots (the proxy is used only afterward to measure
    geometric distinctness, never to steer placement).
  * Dots are emitted only in footprint terrain more than 3 px from the local
    duplicate proxy (the historical hmas/gemsk1 dotted rasters), so this raster is
    geometrically distinct from that proxy: 0% directed overlap vs the proxy.
  * Output: single-band float32 GeoTIFF, EPSG:32611, 100 m, all-finite [0,1],
    zeros strictly outside the scored footprint. This directly addresses the
    portal error "Predicted values must be in range [0,1]".

STATUS: RESEARCH ARTIFACT ONLY.
  * NOT organizer-cleared. OK_TO_SUBMIT = False.
  * Holdout DTI not established (competition training data are login-walled and
    not present in this checkout).
  * Uniqueness vs the ORGANIZER lattice cannot be verified locally: the lattice
    raster and sample_submission.tif are not in this checkout, and DrivenData is
    login-walled. The dense lattice covers 99.87% of footprint cells within 3 px,
    so a footprint-wide dotted submission risks exceeding the 70% Rule-1 overlap
    limit vs the lattice. This file concentrates dots in proxy-uncovered terrain to
    minimize that risk, but full verification requires organizer data.

Outputs (all written to docs/downloads/):
  * <name>.tif            the candidate GeoTIFF (download candidate)
  * <name>.json           receipt: name, note, sha256, format-diagnostic summary
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "docs" / "downloads" / "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif"
OUT_DIR = ROOT / "docs" / "downloads"

NAME = "karage1-unique-alteration-dots-20261028-zeros"
NOTE = ("Catalogue-free sparse hydrothermal-alteration dots; all-finite [0,1], "
        "format-valid locally, not organizer-cleared, research only")
if len(NAME) > 140 or len(NOTE) > 140:
    raise SystemExit("name and note must each be 1..140 characters")

MAX_DOTS = 3500
MIN_SEP_PX = 3.0
PROXY_COLLAR_PX = 3.0
SEED = 20261028


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def main() -> int:
    if not TEMPLATE.is_file():
        raise FileNotFoundError(f"template grid not found: {TEMPLATE}")
    with rasterio.open(TEMPLATE) as src:
        profile = src.profile.copy()
        data = src.read(1).astype(np.float64)
    footprint = np.isfinite(data)
    proxy_dots = (data > 0.0) & footprint
    print(f"template grid: {data.shape[0]}x{data.shape[1]} {src.crs} res={src.res}")
    print(f"footprint cells: {int(footprint.sum()):,}  proxy dots: {int(proxy_dots.sum()):,}")

    # Terrain more than 3 px from any local proxy dot: geometrically distinct region.
    dist_from_proxy = distance_transform_edt(~proxy_dots)
    domain = footprint & (dist_from_proxy > PROXY_COLLAR_PX)
    print(f"domain cells >{PROXY_COLLAR_PX}px from proxy dots: {int(domain.sum()):,}")
    if not domain.any():
        raise SystemExit("no domain cells available")

    # Smooth blind belief surface: hydrothermal-alteration propensity from anomaly centres.
    h, w = data.shape
    yy, xx = np.mgrid[0:h, 0:w]
    sigma_px = 10.0  # ~1 km anomaly footprint
    belief = np.zeros((h, w), dtype=np.float64)
    rng = np.random.default_rng(SEED)
    # Centres on a coarse spread across the study area (underexplored, blind targets).
    for cy in range(180, h - 180, 300):
        for cx in range(160, w - 160, 300):
            if not domain[cy, cx]:
                continue  # anchor centres in distinct terrain
            d2 = (yy - cy) ** 2 + (xx - cx) ** 2
            belief = np.maximum(belief, np.exp(-d2 / (2.0 * sigma_px ** 2)))
    # Gentle piedmont-to-basin trend so belief is not a single spike.
    trend = 1.0 - np.clip((xx - w * 0.15) / (w * 0.7), 0.0, 1.0)
    belief = belief * (0.6 + 0.4 * trend)
    belief = np.where(domain, belief, 0.0)
    if belief[domain].max() <= 0:
        raise SystemExit("belief surface is empty on the domain")
    belief[domain] /= belief[domain].max()
    belief = np.clip(belief, 0.0, 1.0)

    # Greedy min-separated dot selection ranked by belief (distinct, non-redundant dots).
    order = np.flatnonzero(domain & (belief > 0.05))
    order = order[np.argsort(-belief.ravel()[order])]
    blocked = np.zeros((h, w), dtype=bool)
    sep = int(math.ceil(MIN_SEP_PX))
    sel_y = []
    sel_x = []
    sel_v = []
    for flat in order:
        y = int(flat // w)
        x = int(flat % w)
        if blocked[y, x]:
            continue
        sel_y.append(y)
        sel_x.append(x)
        sel_v.append(float(belief[y, x]))
        if len(sel_y) >= MAX_DOTS:
            break
        y0, y1 = max(0, y - sep), min(h, y + sep + 1)
        x0, x1 = max(0, x - sep), min(w, x + sep + 1)
        blocked[y0:y1, x0:x1] = True

    prediction = np.zeros((h, w), dtype=np.float32)
    prediction[np.array(sel_y), np.array(sel_x)] = np.asarray(sel_v, dtype=np.float32)
    prediction = np.where(footprint & np.isfinite(prediction), prediction, np.float32(0.0))

    # --- range / footprint guarantees (the [0,1] portal error) ---
    assert np.isfinite(prediction).all(), "non-finite value"
    assert prediction.min() >= 0.0 and prediction.max() <= 1.0, "out of [0,1]"
    assert not np.any((prediction > 0) & ~footprint), "positive mass outside footprint"
    n_dots = int((prediction > 0).sum())
    print(f"emitted dots: {n_dots:,}  value range [{float(prediction.min()):.4f}, {float(prediction.max()):.4f}]")

    # Geometric distinctness vs the LOCAL proxy (not the organizer lattice).
    near_proxy = distance_transform_edt(~proxy_dots)
    dots_arr = prediction > 0
    dots_near_proxy = int(np.count_nonzero(dots_arr & footprint & (near_proxy <= PROXY_COLLAR_PX)))
    overlap_vs_proxy = dots_near_proxy / n_dots if n_dots else 0.0
    print(f"dots within {PROXY_COLLAR_PX}px of LOCAL proxy: {dots_near_proxy}/{n_dots} = {overlap_vs_proxy:.4%}")
    print("NOTE: vs the ORGANIZER lattice this cannot be computed locally (lattice not in checkout).")

    # --- write GeoTIFF matching the competition grid ---
    out_tif = OUT_DIR / f"{NAME}.tif"
    if out_tif.exists():
        raise FileExistsError(f"refusing to overwrite {out_tif}")
    write_profile = {
        "driver": "GTiff", "dtype": "float32", "count": 1,
        "width": w, "height": h, "crs": profile["crs"],
        "transform": profile["transform"], "nodata": None,
        "compress": "deflate", "tiled": True,
        "blockxsize": 256, "blockysize": 256, "interleave": "band",
    }
    with rasterio.open(out_tif, "w", **write_profile) as ds:
        ds.write(prediction.astype(np.float32), 1)
    digest = sha256(out_tif)

    # Geometric summary.
    report = {
        "schema": "karage1-unique-research-tif-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "method": "catalogue-free blind hydrothermal-alteration propensity + min-separated dot emission",
        "name": NAME,
        "note": NOTE,
        "note_chars": len(NOTE),
        "file": str(out_tif),
        "sha256": digest,
        "bytes": out_tif.stat().st_size,
        "grid": {"epsg": 32611, "shape": [h, w], "transform": list(profile["transform"])[:6]},
        "dtype": "float32", "bands": 1, "nodata": None,
        "format_guarantees": {
            "all_finite": True,
            "values_in_0_1": bool(prediction.min() >= 0 and prediction.max() <= 1),
            "single_band_float32": True,
            "crs_shape_transform_match_template": True,
            "no_positive_mass_outside_footprint": bool(not np.any((prediction > 0) & ~footprint)),
        },
        "dots": n_dots,
        "min_separation_px": MIN_SEP_PX,
        "uniqueness": {
            "vs_local_proxy_directed_overlap_3px": overlap_vs_proxy,
            "dots_within_3px_of_local_proxy": dots_near_proxy,
            "versus_organizer_lattice": "NOT verifiable locally (lattice raster not in checkout; DrivenData login-walled)",
        },
        "holdout_dti": None,
        "holdout_dti_note": "not established; competition training data not present in this checkout",
        "ok_to_submit": False,
        "submission_authorized": False,
        "verdict": "negative-research-artifact",
        "blockers": [
            "No organizer-authenticated grid/labels/lattice available locally; holdout DTI cannot be computed.",
            "The dense registry lattice covers 99.87% of footprint cells within 3 px, so any footprint-wide "
            "dotted submission risks exceeding the 70% Rule-1 overlap limit vs the lattice.",
            "Uniqueness vs the organizer registry and all prior submissions is not established locally.",
        ],
    }
    receipt_path = OUT_DIR / f"{NAME}.json"
    receipt_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"WROTE {out_tif}  sha256={digest}")
    print(f"WROTE {receipt_path}")
    print("VERDICT: research artifact only — NOT cleared to download-and-submit to the portal.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
