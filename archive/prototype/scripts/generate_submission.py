"""generate_submission.py — generate a UNIQUE competition TIF submission.

Hypothesis H-UNQ-1 (radiometric-hydrothermal + fluvial-chi + gravity-margin
off-catalogue fault detector):

    Layers involved:
      * fluvial chi / channel-steepness anomaly (blind range-front uplift,
        knickzones) — from 10 m 3DEP-derived flow direction
      * GeoDAWN radiometric Th/K and eU/K alteration ratio (hydrothermal
        alteration along permeable fault zones)
      * isostatic-gravity margin edge (basement-involved faulting)
    Physical signature targeted:
      * linear hydrothermal alteration + gravity-margin edge co-located with
        fluvial chi knickzones — a blind/pre-Quaternary fault signature
    Why it catches faults missing from USGS/INGENIOUS catalogue:
      * catalogue only maps mapped/Quaternary surface faults; blind,
        low-relief, pre-Quaternary and hydrothermal-only faults are absent.
        H-UNQ-1 is label-free (no catalogue input except a 2 px collar used
        purely to suppress detector-echo false positives near known faults).
    How it differs from anything in this repo / the focus-9 family:
      * does NOT re-thin the H19-5 ridge skeleton (every focus-9 leader does);
        it is radiometric-primary + fluvial-chi, like GEMSDOE33's THKCOND but
        with fluvial-chi + gravity margin instead of Th/K x conductivity.

Output: single-band float32 GeoTIFF, EPSG:32611, 3730x3292, values in [0,1],
finite everywhere (zeros encoding), ~37,654 binary dots on a CELF-300m
emission thinned to the standard dot budget.

WARNING (no-hallucination): this is built on SYNTHETIC stand-in rasters
because the competition training data (training_features.tif, labels.tif,
sample_submission.tif) require DrivenData login and cannot be downloaded here.
The output is FORMAT-VALID ([0,1], finite, EPSG:32611, 3730x3292) but its
geotransform origin is a documented placeholder — it MUST be re-gridded to the
real sample_submission.tif via scripts/align_to_competition_grid.py and
validated on the holdout before any upload. OK TO SUBMIT = NO until then.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime, timezone

import numpy as np

try:
    import rasterio
    from rasterio.transform import from_origin
    from rasterio.crs import CRS
except Exception as exc:  # pragma: no cover
    rasterio = None
    from_origin = None
    CRS = None

from scipy import ndimage  # distance transforms / gaussian filtering

# Protocol constants
HEIGHT = 3730
WIDTH = 3292
CELLS = HEIGHT * WIDTH  # 12,279,160
PX_M = 100.0  # placeholder pixel size (metres) — placeholder grid
DOT_BUDGET = 37654  # standard GEMS dot budget
CATALOGUE_COLLAR_PX = 2  # suppress within 2 px of known catalogue
CELF_RADIUS_M = 300.0  # CELF emission radius (matches DTI kernel)


def sha256_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Synthetic stand-in feature rasters (label-free, geological proxy)
# ---------------------------------------------------------------------------
def _line_mask(height, width, y0, x0, y1, x1, width_px=3.0):
    """Rasterize a thin line (fault trace) into a boolean mask."""
    rr, cc = _line_rr_cc(y0, x0, y1, x1)
    mask = np.zeros((height, width), dtype=bool)
    valid = (rr >= 0) & (rr < height) & (cc >= 0) & (cc < width)
    mask[rr[valid], cc[valid]] = True
    if width_px > 1:
        mask = ndimage.binary_dilation(mask, iterations=int(width_px))
    return mask


def _line_rr_cc(y0, x0, y1, x1):
    """Bresenham-ish line -> row, col arrays."""
    n = int(max(abs(y1 - y0), abs(x1 - x0)) * 2) + 1
    t = np.linspace(0, 1, n)
    rr = np.round(y0 + t * (y1 - y0)).astype(int)
    cc = np.round(x0 + t * (x1 - x0)).astype(int)
    return rr, cc


def _gaussian_blob(height, width, cy, cx, sigma_px, amp=1.0):
    yy = np.arange(height)[:, None]
    xx = np.arange(width)[None, :]
    d2 = ((yy - cy) / sigma_px) ** 2 + ((xx - cx) / sigma_px) ** 2
    return amp * np.exp(-0.5 * d2)


def synthesize_features(seed: int = 20261027):
    """Build synthetic stand-in feature rasters for H-UNQ-1.

    Returns dict of float32 rasters (height x width) in arbitrary units:
      chi_anom   : fluvial chi anomaly (knickzone/uplift proxy)
      rad_alt    : radiometric hydrothermal alteration proxy (Th/K eU/K)
      grav_edge  : gravity-margin edge proxy
      catalogue  : boolean mask of "known catalogue" faults (for collar only)
    """
    rng = np.random.default_rng(seed)
    h, w = HEIGHT, WIDTH

    # --- Fault traces (blind range-front + transverse), label-free ---------
    traces = [
        # NNE-trending range-front fault (long, deep crustal)
        (h * 0.15, w * 0.10, h * 0.85, w * 0.30, 2.5),
        # NE-trending transverse fault
        (h * 0.20, w * 0.55, h * 0.75, w * 0.85, 2.0),
        # N-trending basement fault (blind, no surface scarp in catalogue)
        (h * 0.10, w * 0.70, h * 0.90, w * 0.68, 1.5),
        # E-W relay zone
        (h * 0.50, w * 0.05, h * 0.55, w * 0.95, 1.0),
    ]
    fault_mask = np.zeros((h, w), dtype=bool)
    for (y0, x0, y1, x1, bw) in traces:
        fault_mask |= _line_mask(h, w, y0, x0, y1, x1, width_px=bw)

    # --- Known catalogue (synthetic, sparse) — used ONLY for the collar ---
    catalogue = np.zeros((h, w), dtype=bool)
    # catalogue covers only a subset of traces (the mapped Quaternary ones)
    cat_traces = [traces[0], traces[2]]  # mapped ones
    for (y0, x0, y1, x1, bw) in cat_traces:
        catalogue |= _line_mask(h, w, y0, x0, y1, x1, width_px=bw)
    catalogue = ndimage.binary_dilation(catalogue, iterations=CATALOGUE_COLLAR_PX)

    # --- Fluvial chi anomaly: high near range-front uplift/knickzones ------
    dist_to_fault = ndimage.distance_transform_edt(~fault_mask)
    # invert: near faults => high chi anomaly (uplift recorded in channel steepness)
    chi_anom = np.exp(-0.5 * (dist_to_fault / 8.0) ** 2)  # sigma 8 px (~800 m)
    chi_anom += 0.15 * rng.standard_normal((h, w))  # noise
    chi_anom = np.clip(chi_anom, 0, None)

    # --- Radiometric alteration: hydrothermal halos around SOME faults -----
    rad_alt = np.zeros((h, w), dtype=np.float32)
    alteration_centers = [
        (h * 0.35, w * 0.22), (h * 0.60, w * 0.72), (h * 0.78, w * 0.40),
    ]
    for (cy, cx) in alteration_centers:
        rad_alt += _gaussian_blob(h, w, cy, cx, sigma_px=12.0, amp=1.0)
    rad_alt = np.clip(rad_alt, 0, None)
    rad_alt = ndimage.gaussian_filter(rad_alt, sigma=4.0)

    # --- Gravity-margin edge: edges of basement blocks ---------------------
    grav_edge = ndimage.distance_transform_edt(~fault_mask)
    grav_edge = np.exp(-0.5 * (grav_edge / 6.0) ** 2)  # sharp edge
    grav_edge += 0.08 * rng.standard_normal((h, w))
    grav_edge = np.clip(grav_edge, 0, None)

    # Normalize each feature to [0,1] for combination
    def norm01(a):
        a = np.nan_to_num(a, nan=0.0, posinf=0.0, neginf=0.0)
        lo, hi = np.percentile(a, 2), np.percentile(a, 98)
        if hi > lo:
            return np.clip((a - lo) / (hi - lo), 0, 1)
        return np.zeros_like(a)

    chi_anom = norm01(chi_anom).astype(np.float32)
    rad_alt = norm01(rad_alt).astype(np.float32)
    grav_edge = norm01(grav_edge).astype(np.float32)

    return {
        "chi_anom": chi_anom,
        "rad_alt": rad_alt,
        "grav_edge": grav_edge,
        "catalogue": catalogue,
        "fault_mask": fault_mask,
    }


def propensity_surface(features: dict, weights=None):
    """Combine features into a propensity surface in [0,1].

    H-UNQ-1 mechanism: hydrothermal fluids ascend along permeable fault zones,
    leaving radiometric (Th/K, eU/K) and geophysical (gravity margin)
    signatures; blind range-front uplift is recorded in fluvial chi anomaly.
    """
    if weights is None:
        weights = {"chi_anom": 0.35, "rad_alt": 0.40, "grav_edge": 0.25}
    p = (weights["chi_anom"] * features["chi_anom"]
         + weights["rad_alt"] * features["rad_alt"]
         + weights["grav_edge"] * features["grav_edge"])
    p = np.clip(p, 0, 1).astype(np.float32)
    return p


def celf_dotted_emission(propensity, features, budget=DOT_BUDGET, radius_m=CELF_RADIUS_M,
                         px_m=PX_M, seed: int = 20261027):
    """CELF (constrained emission local fault) dotted emission.

    Place binary dots preferentially on high-propensity cells, spaced at
    least ~radius apart, and SUPPRESS dots inside the catalogue collar
    (2 px) to avoid detector-echo false positives near known faults.
    """
    rng = np.random.default_rng(seed)
    h, w = propensity.shape
    radius_px = radius_m / px_m

    # Start from propensity; zero out catalogue collar (suppress near known faults)
    p = propensity.copy()
    collar = features["catalogue"]
    p[collar] = 0.0

    # Iterative farthest-point sampling weighted by propensity.
    dots_r = []
    dots_c = []
    occupied = np.zeros((h, w), dtype=bool)

    # Flatten candidate cells with propensity > small threshold
    cand = p > 0.02
    if not np.any(cand):
        return np.zeros((h, w), dtype=np.float32)

    # Repeatedly pick the highest-propensity available cell, then exclude a
    # radius around it (spatial non-max suppression) until budget reached.
    p_work = p.copy()
    n = 0
    while n < budget:
        idx = int(np.argmax(p_work))
        if p_work.flat[idx] <= 0.0:
            break
        r = idx // w
        c = idx % w
        if occupied[r, c]:
            p_work.flat[idx] = 0.0
            continue
        dots_r.append(r)
        dots_c.append(c)
        n += 1
        # exclude radius around this dot
        rr0 = max(0, r - int(radius_px)); rr1 = min(h, r + int(radius_px) + 1)
        cc0 = max(0, c - int(radius_px)); cc1 = min(w, c + int(radius_px) + 1)
        yy = np.arange(rr0, rr1)[:, None]
        xx = np.arange(cc0, cc1)[None, :]
        d2 = ((yy - r) / radius_px) ** 2 + ((xx - c) / radius_px) ** 2
        excl = d2 <= 1.0
        occupied[rr0:rr1, cc0:cc1] |= excl
        p_work[rr0:rr1, cc0:cc1][excl] = 0.0

    out = np.zeros((h, w), dtype=np.float32)
    out[np.array(dots_r), np.array(dots_c)] = 1.0
    return out


def write_geotiff(path, data, profile):
    if rasterio is None:
        raise RuntimeError("rasterio is required")
    prof = profile.copy()
    prof.update(driver="GTiff", dtype="float32", count=1,
                compress="deflate", tiled=True, bigtiff="IF_NEEDED")
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(data.astype(np.float32), 1)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate UNIQUE H-UNQ-1 competition TIF submission (synthetic stand-in).")
    parser.add_argument("--seed", type=int, default=20261027,
                        help="Random seed (deterministic).")
    parser.add_argument("--out", default=None,
                        help="Output TIF path (default submissions/...).")
    parser.add_argument("--dots", action="store_true",
                        help="Also write a binary-dot (CELF) version.")
    args = parser.parse_args(argv)

    if rasterio is None:
        print("ERROR: rasterio is required.", file=sys.stderr)
        return 2

    transform = from_origin(500000.0, 4500000.0, PX_M, PX_M)
    crs = CRS.from_epsg(32611)
    profile = {"driver": "GTiff", "dtype": "float32", "count": 1,
               "height": HEIGHT, "width": WIDTH, "crs": crs,
               "transform": transform, "compress": "deflate",
               "tiled": True, "bigtiff": "IF_NEEDED"}

    features = synthesize_features(seed=args.seed)
    propensity = propensity_surface(features)

    content = hashlib.sha256(propensity.tobytes()).hexdigest()[:12]
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    if args.out is None:
        args.out = f"submissions/gemsdoe-unique-hunq1-{stamp}-{content}-zeros.tif"

    # Continuous propensity surface (valid [0,1] submission)
    write_geotiff(args.out, propensity, profile)
    print(f"Wrote propensity surface: {args.out}")
    print(f"  shape={propensity.shape} dtype={propensity.dtype} "
          f"min={propensity.min():.4f} max={propensity.max():.4f} "
          f"finite={np.all(np.isfinite(propensity))}")

    if args.dots:
        dots = celf_dotted_emission(propensity, features, seed=args.seed)
        dot_path = args.out.replace("-zeros.tif", "-dots.tif")
        write_geotiff(dot_path, dots, profile)
        n_dots = int(np.sum(dots > 0))
        print(f"Wrote dotted emission: {dot_path}  dots={n_dots}")

    # ---- Hash + metadata ----
    sha = sha256_file(args.out)
    meta = {
        "hypothesis": "H-UNQ-1 radiometric-hydrothermal + fluvial-chi + gravity-margin off-catalogue fault detector",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "output": args.out,
        "raster_sha256": sha,
        "shape": [HEIGHT, WIDTH],
        "cells": CELLS,
        "dtype": "float32",
        "crs": "EPSG:32611",
        "transform": [transform.a, transform.b, transform.c, transform.d,
                      transform.e, transform.f],
        "pixel_size_m": PX_M,
        "min": float(propensity.min()),
        "max": float(propensity.max()),
        "nan_count": int(np.sum(~np.isfinite(propensity))),
        "note": ("H-UNQ-1 radiometric-hydrothermal+fluvial-chi+gravity-margin "
                 "off-catalogue fault detector | synthetic stand-in | "
                 "DO NOT SUBMIT until re-gridded to sample_submission.tif "
                 "and holdout-validated"),
        "ok_to_submit": False,
        "reason": ("No DrivenData auth -> cannot re-grid to real sample_submission.tif, "
                   "cannot compute holdout DTI, cannot verify uniqueness vs registry. "
                   "Format-valid only ([0,1], finite, EPSG:32611, 3730x3292)."),
    }
    meta_path = args.out + ".meta.json"
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"\nMetadata: {meta_path}")
    print(f"SHA-256: {sha}")
    print("OK TO SUBMIT: NO — format-valid synthetic stand-in; re-grid to real "
          "sample_submission.tif + holdout + uniqueness gates required.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
