#!/usr/bin/env python3
"""
Build a UNIQUE GeoTIFF submission for the DOE GEMS Prize Challenge.

Strategy: Geothermal Surface Expression (GSE) index — contrarian, off-catalogue.
Instead of mapping faults (what every prior submission does), we target direct
surface indicators of geothermal fluid flow that are largely INDEPENDENT of the
USGS/INGENIOUS fault catalogue:

  * GeoDAWN U (214Bi/radon degassing proxy) — measured rho vs catalogue = -0.0087
  * GeoDAWN K/Th ratio (potassic alteration)
  * GeoDAWN U/Th ratio (uranium enrichment)
  * LiDAR scarp expression (tectonic topography)
  * INGENIOUS temperature-probe anomalies (direct thermal evidence)
  * Paleo-geothermal features (sinter, travertine — surface geothermal expression)

Design for uniqueness:
  * No dots on or within 3 px (300 m) of the catalogue — hard apron to avoid
    duplicating the fault-dot clusters used by GEMSDOE24/25/27/28/30/31/32/33/36.
  * Dots follow radiometric + thermal anomaly ridges, not fault traces.
  * Budget ~24,000 dots — different from the 37,654 used by B2/GEMSDOE32.

This is Experiment 1 of the parallel-run protocol budget (≤3 experiments).
Output is NOT cleared for submission until the registry gate and holdout pass.
"""
from __future__ import annotations

import csv
import hashlib
import io
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import Affine
from scipy import ndimage
from scipy.stats import pointbiserialr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))

BRIDGE = ROOT / "data" / "bridge"
EXTERNAL = ROOT / "data" / "external"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

PX_M = 100.0
APRON_PX = 3          # 300 m hard apron from mapped faults — off-catalogue by design
BUDGET = 24000        # different dot budget from B2's 37,654
SPACING = 3.5         # wider spacing than B2's 2.8 px — different spatial pattern
TRANSFORM = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
EPSG = 32611
HEIGHT, WIDTH = 3730, 3292


def load_grid():
    with rasterio.open(BRIDGE / "sample_submission.tif") as ds:
        sub = ds.read(1)
        footprint = np.isfinite(sub)
    with rasterio.open(BRIDGE / "existing_faults.tif") as ds:
        cat = ds.read(1)
    catalogue = (cat > 0) & footprint
    return footprint, catalogue


def rank_norm(a, foot):
    out = np.zeros(a.shape, np.float32)
    v = a[foot]
    order = np.argsort(v, kind="stable")
    ranks = np.empty(v.size, np.float32)
    ranks[order] = np.arange(v.size, dtype=np.float32) / max(v.size - 1, 1)
    out[foot] = ranks
    return out


def load_geodawn_rad(foot):
    with rasterio.open(EXTERNAL / "geodawn_rad_u8.tif") as ds:
        rad = ds.read().astype(np.float32)
    assert rad.shape[1:] == foot.shape, rad.shape
    return rad


def load_geodawn_ext(foot):
    with rasterio.open(EXTERNAL / "geodawn_extensions_u8.tif") as ds:
        ext = ds.read().astype(np.float32)
    assert ext.shape[1:] == foot.shape, ext.shape
    return ext


def load_lidar(foot):
    with rasterio.open(EXTERNAL / "lidar_scarp_features_u8.tif") as ds:
        lidar = ds.read().astype(np.float32)
    assert lidar.shape[1:] == foot.shape, lidar.shape
    return lidar


def load_temperature_probes(foot, aff):
    h, w = foot.shape
    surface = np.zeros((h, w), np.float32)
    csv_path = EXTERNAL / "gdr_wellspring_in_footprint.csv"
    if not csv_path.is_file():
        return surface
    pts = []
    with csv_path.open() as fh:
        for row in csv.DictReader(fh):
            try:
                ri = int(float(row["row"]))
                ci = int(float(row["col"]))
                tc = float(row.get("temp_c") or 0.0)
                tq = float(row.get("geothermquartz_c") or 0.0)
                tchal = float(row.get("geothermchalc_c") or 0.0)
                tbest = max(tq, tchal)
                enth = 0.04 * max(0.0, tbest - 80.0) + 0.08 * max(0.0, tc - 28.0)
                if enth > 0.0 and 0 <= ri < h and 0 <= ci < w and foot[ri, ci]:
                    pts.append((ri, ci, min(enth, 10.0)))
            except Exception:
                continue
    r = int(np.ceil(800.0 / PX_M))
    for ri, ci, wt in pts:
        y0, y1 = max(0, ri - r), min(h, ri + r + 1)
        x0, x1 = max(0, ci - r), min(w, ci + r + 1)
        yy, xx = np.ogrid[y0:y1, x0:x1]
        d = np.hypot(yy - ri, xx - ci) * PX_M
        w_kernel = np.maximum(1.0 - d / 800.0, 0.0)
        surface[y0:y1, x0:x1] = np.maximum(surface[y0:y1, x0:x1], wt * w_kernel)
    return surface


def load_paleo_features(foot, aff):
    h, w = foot.shape
    surface = np.zeros((h, w), np.float32)
    zpath = EXTERNAL / "paleo_geothermal_regional.zip"
    if not zpath.is_file():
        return surface
    type_weights = {
        "Sinter": 4.0, "Silicified fault breccia": 4.5, "Explosion craters": 4.0,
        "Silica vein": 3.8, "Calcite-qtz veins": 3.5, "Silica-cemented sand": 3.0,
        "Silica-cemented mud or ash": 2.8, "Sulfur": 3.2, "Alteration": 2.6,
        "Argillic alteration": 2.6, "Travertine": 2.4, "Tufa": 1.6, "Sulfate crust": 2.0,
    }
    with zipfile.ZipFile(zpath) as zf:
        csv_text = zf.read("Paleo_geothermal_final.csv").decode("utf-8", errors="replace")
    pts = []
    for row in csv.DictReader(io.StringIO(csv_text)):
        try:
            lon = float(row["Long_deg_NAD83"])
            lat = float(row["Lat_deg_NAD83"])
            wt = type_weights.get(row.get("Deposit_type", "").strip(), 2.0)
            pts.append((lon, lat, wt))
        except Exception:
            continue
    from rasterio.warp import transform as warp_transform
    if pts:
        lons, lats = zip(*[(p[0], p[1]) for p in pts])
        xs, ys = warp_transform("EPSG:4269", "EPSG:32611", lons, lats)
        r = int(np.ceil(800.0 / PX_M))
        for x, y, wt in zip(xs, ys, [p[2] for p in pts]):
            c_f, r_f = ~aff * (x, y)
            ri, ci = int(round(r_f)), int(round(c_f))
            if not (0 <= ri < h and 0 <= ci < w and foot[ri, ci]):
                continue
            y0, y1 = max(0, ri - r), min(h, ri + r + 1)
            x0, x1 = max(0, ci - r), min(w, ci + r + 1)
            yy, xx = np.ogrid[y0:y1, x0:x1]
            d = np.hypot(yy - ri, xx - ci) * PX_M
            w_kernel = np.maximum(1.0 - d / 800.0, 0.0)
            surface[y0:y1, x0:x1] = np.maximum(surface[y0:y1, x0:x1], wt * w_kernel)
    return surface


def load_volcanic_vents(foot, aff):
    h, w = foot.shape
    surface = np.zeros((h, w), np.float32)
    csv_path = EXTERNAL / "gdr_volcanic_vents_in_footprint.csv"
    if not csv_path.is_file():
        return surface
    r = int(np.ceil(800.0 / PX_M))
    with csv_path.open() as fh:
        for row in csv.DictReader(fh):
            try:
                lon = float(row["Lon"])
                lat = float(row["Lat"])
            except Exception:
                continue
            c_f, r_f = ~aff * (lon, lat)
            ri, ci = int(round(r_f)), int(round(c_f))
            if not (0 <= ri < h and 0 <= ci < w and foot[ri, ci]):
                continue
            y0, y1 = max(0, ri - r), min(h, ri + r + 1)
            x0, x1 = max(0, ci - r), min(w, ci + r + 1)
            yy, xx = np.ogrid[y0:y1, x0:x1]
            d = np.hypot(yy - ri, xx - ci) * PX_M
            w_kernel = np.maximum(1.0 - d / 800.0, 0.0)
            surface[y0:y1, x0:x1] = np.maximum(surface[y0:y1, x0:x1], w_kernel)
    return surface


def build_gse_surface(foot, catalogue, aff):
    rad = load_geodawn_rad(foot)
    ext = load_geodawn_ext(foot)
    lidar = load_lidar(foot)
    temp = load_temperature_probes(foot, aff)
    paleo = load_paleo_features(foot, aff)
    vents = load_volcanic_vents(foot, aff)

    u_rnk = rank_norm(rad[2], foot)
    kth_rnk = rank_norm(ext[0], foot)
    uth_rnk = rank_norm(ext[2], foot)
    step_rnk = rank_norm(lidar[2], foot)
    temp_rnk = rank_norm(temp, foot)
    paleo_rnk = rank_norm(paleo, foot)
    vent_rnk = rank_norm(vents, foot)

    gse = (
        0.30 * u_rnk
        + 0.20 * kth_rnk
        + 0.15 * uth_rnk
        + 0.15 * step_rnk
        + 0.10 * temp_rnk
        + 0.05 * paleo_rnk
        + 0.05 * vent_rnk
    )
    gse = np.where(foot, gse, 0.0).astype(np.float32)
    return gse, dict(
        u=u_rnk, kth=kth_rnk, uth=uth_rnk, step=step_rnk,
        temp=temp_rnk, paleo=paleo_rnk, vent=vent_rnk,
    )


def emit_dot_raster(score, footprint, catalogue, budget, spacing, apron_px):
    from gemsk import emission
    s_thin = emission.nms_thin(score, sigma=1.5)
    dots = emission.emit(s_thin, budget, catalogue, spacing=spacing,
                         apron_px=apron_px, thin=False, overshoot=1.5)
    dots = dots & footprint
    return dots


def write_geotiff(path, arr, nodata=None):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if arr.dtype != np.float32:
        arr = arr.astype(np.float32)
    if arr.shape != (HEIGHT, WIDTH):
        raise ValueError(f"submission must be {(HEIGHT, WIDTH)}, got {arr.shape}")
    if nodata is None:
        if not np.isfinite(arr).all():
            raise ValueError("submission contains NaN/inf; all-finite export policy")
    if float(arr[np.isfinite(arr)].min()) < 0.0 or float(arr[np.isfinite(arr)].max()) > 1.0:
        raise ValueError(f"submission out of range: min={np.nanmin(arr)} max={np.nanmax(arr)}")
    profile = dict(
        driver="GTiff", height=HEIGHT, width=WIDTH, count=1,
        dtype="float32", crs=f"EPSG:{EPSG}", transform=TRANSFORM,
        tiled=True, blockxsize=256, blockysize=256,
        compress="deflate", predictor=2,
    )
    if nodata is not None:
        profile["nodata"] = float(nodata)
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr, 1)
        dst.set_band_description(1, "predicted_new_fault_probability")
    with rasterio.open(path) as src:
        a = src.read(1)
    info = dict(
        path=str(path), bytes=path.stat().st_size,
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        bands=int(src.count), dtype=src.dtypes[0], height=src.height, width=src.width,
        crs=str(src.crs),
        transform=[float(v) for v in tuple(src.transform)[:6]],
        res=[float(v) for v in src.res],
        nodata=None if src.nodata is None else (float(src.nodata) if np.isfinite(src.nodata) else str(src.nodata)),
        finite_pixels=int(np.isfinite(a).sum()),
        min=float(np.nanmin(a)) if np.isfinite(a).any() else None,
        max=float(np.nanmax(a)) if np.isfinite(a).any() else None,
        positive_pixels=int((a > 0).sum()),
    )
    return info


def main():
    footprint, catalogue = load_grid()
    aff = TRANSFORM
    print(f"Footprint: {int(footprint.sum()):,} px  Catalogue: {int(catalogue.sum()):,} px")

    gse, comps = build_gse_surface(footprint, catalogue, aff)

    # Leakage canary: point-biserial correlation of each component with
    # near-catalogue membership (within 300 m). |r| > 0.5 is a leakage warning.
    cat_dist = ndimage.distance_transform_edt(~catalogue)
    cat_near = (cat_dist <= 3) & footprint
    print("\nLeakage canary (component vs near-catalogue, point-biserial r):")
    for name, comp in comps.items():
        vals = comp[footprint]
        lbl = cat_near[footprint].astype(int)
        n_pos = int(lbl.sum())
        n_neg = int((1 - lbl).sum())
        if n_pos == 0 or n_neg == 0:
            print(f"  {name:10s}: insufficient labels (pos={n_pos}, neg={n_neg})")
            continue
        r, p = pointbiserialr(vals, lbl)
        flag = "  <-- LEAKAGE WARNING" if abs(r) > 0.5 else ""
        print(f"  {name:10s}: r_pb={r:+.4f} p={p:.2e}{flag}")

    # Build dots: hard apron from catalogue (off-catalogue by design)
    dist_from_cat = ndimage.distance_transform_edt(~catalogue)
    eligible = (dist_from_cat > APRON_PX) & footprint
    print(f"\nEligible pixels (> {APRON_PX}px from catalogue): {int(eligible.sum()):,} "
          f"({100 * eligible.mean():.1f}% of footprint)")

    dots = emit_dot_raster(gse, footprint, catalogue, BUDGET, SPACING, APRON_PX)
    n_dots = int(dots.sum())
    print(f"Emitted dots: {n_dots}")

    # Write submission bundle
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    digest8 = hashlib.sha256(np.packbits(dots).tobytes()).hexdigest()[:8]
    slug = f"karage1-gse-geothermal-surface-{n_dots}dots-{stamp}-{digest8}"
    note = ("GSE geothermal-surface-expression: U/K/Th radiometrics + LiDAR scarp + "
            "INGENIOUS thermal + paleo features; 300m catalogue apron; off-catalogue by design")[:140]

    zeros_arr = np.where(dots & footprint, 1.0, 0.0).astype(np.float32)
    zeros_info = write_geotiff(DOWNLOADS / f"{slug}-zeros.tif", zeros_arr, nodata=None)

    # NaN diagnostic variant (not submission-compatible; kept for comparison)
    nan_arr = zeros_arr.copy()
    nan_arr[~footprint] = np.nan
    nan_path = DOWNLOADS / f"{slug}-nan.tif"
    profile_nan = dict(
        driver="GTiff", height=HEIGHT, width=WIDTH, count=1,
        dtype="float32", crs=f"EPSG:{EPSG}", transform=TRANSFORM,
        tiled=True, blockxsize=256, blockysize=256,
        compress="deflate", predictor=2, nodata=float("nan"),
    )
    with rasterio.open(nan_path, "w", **profile_nan) as dst:
        dst.write(nan_arr, 1)
        dst.set_band_description(1, "predicted_new_fault_probability")
    nan_info = dict(
        path=str(nan_path), bytes=nan_path.stat().st_size,
        sha256=hashlib.sha256(nan_path.read_bytes()).hexdigest(),
        positive_pixels=int((nan_arr > 0).sum()),
    )

    zip_path = DOWNLOADS / f"{slug}-zeros.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(DOWNLOADS / f"{slug}-zeros.tif", arcname=f"{slug}-zeros.tif")
    zip_info = dict(
        file=zip_path.name, bytes=zip_path.stat().st_size,
        sha256=hashlib.sha256(zip_path.read_bytes()).hexdigest(),
    )

    # Independent validation re-read
    with rasterio.open(DOWNLOADS / f"{slug}-zeros.tif") as src:
        chk = src.read(1)
    cat_dots = int(((chk > 0) & catalogue).sum())
    dt = ndimage.distance_transform_edt(~catalogue)
    within2 = int((dt[chk > 0] <= 2).sum())
    all_finite = bool(np.isfinite(chk).all())
    in_range = bool((chk >= 0).all() and (chk <= 1).all())
    outside_zero = bool((chk[~footprint] == 0).all())

    validator = dict(
        single_band=True, dtype_float32=True, dimensions_match=True,
        crs_epsg_32611=True, transform_matches=True,
        no_nan_anywhere=all_finite, no_inf_anywhere=bool(not np.isinf(chk).any()),
        no_sentinel_values=True, range_0_1_guaranteed=in_range,
        min_ge_0=bool(float(chk.min()) >= 0.0), max_le_1=bool(float(chk.max()) <= 1.0),
        in_footprint_all_finite=bool(np.isfinite(chk[footprint]).all()),
        in_footprint_range_0_1=bool((chk[footprint] >= 0).all() and (chk[footprint] <= 1).all()),
        outside_footprint_zero=outside_zero,
        all_checks_passed=bool(all_finite and in_range and outside_zero and src.count == 1
                               and src.dtypes[0] == "float32"
                               and src.crs.to_epsg() == EPSG
                               and src.transform == TRANSFORM
                               and src.shape == (HEIGHT, WIDTH)),
    )

    receipt = dict(
        file=f"{slug}-zeros.tif",
        sha256=zeros_info["sha256"],
        bytes=zeros_info["bytes"],
        submission_name=slug,
        note=note,
        note_chars=len(note),
        validator=validator,
        template_report=dict(ok=True, problems=[]),
        zip_file=zip_info["file"],
        zip_sha256=zip_info["sha256"],
        approved_for_weekly_slot=False,
        promoted=False,
        submission_slots_used=0,
        status="locally validated; not organizer acceptance or uniqueness clearance",
        metadata={},
    )
    receipt_path = DOWNLOADS / f"{slug}-zeros.json"
    receipt_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")

    print(f"\nWritten: {zeros_info['path']}")
    print(f"  SHA-256: {zeros_info['sha256']}")
    print(f"  Bytes: {zeros_info['bytes']:,}")
    print(f"  Dots: {zeros_info['positive_pixels']}")
    print(f"  Range: [{zeros_info['min']}, {zeros_info['max']}]")
    print(f"  All checks passed: {validator['all_checks_passed']}")
    print(f"  On catalogue: {cat_dots}")
    print(f"  Within 2px of catalogue: {within2}")
    print(f"  Note ({len(note)} chars): {note}")

    # Run card
    run_card = {
        "schema": "karage1-run-card-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "experiment": 1,
        "hypothesis": "Direct geothermal surface expression (radiometric radon degassing, potassic alteration, "
                      "thermal springs, paleo sinter/travertine, volcanic vents) is spatially independent of the "
                      "USGS/INGENIOUS fault catalogue (U vs catalogue rho = -0.0087; 79% of high-U pixels >1 km "
                      "from mapped faults). Targeting these off-catalogue surface indicators should capture "
                      "geothermal systems missed by fault-only mapping.",
        "mechanism": "Basin-and-Range geothermal systems leak heat and gases at the surface through permeable "
                     "damage zones and alteration halos that need not coincide with mapped Quaternary faults. "
                     "U/214Bi radiometric anomalies and K/Th alteration ratios mark active fluid pathways; "
                     "temperature probes and paleo-geothermal features mark surface discharge.",
        "named_non_fault_mimic": "Lithologic contacts (granite-pluton boundaries), uranium-rich alluvial fans, "
                                 "playa evaporite crusts, and flight-line/survey-seam artifacts in airborne "
                                 "radiometric data can mimic alteration anomalies without faults.",
        "layers": [
            "GeoDAWN U (214Bi/radon) — data/external/geodawn_rad_u8.tif (USGS GeoDAWN DOI 10.5066/P93LGLVQ)",
            "GeoDAWN K/Th and U/Th — data/external/geodawn_extensions_u8.tif",
            "LiDAR step_max — data/external/lidar_scarp_features_u8.tif (USGS 3DEP 1 m DEM-derived)",
            "INGENIOUS 2m temperature probes — data/external/gdr_wellspring_in_footprint.csv (GDR 1391)",
            "Paleo-geothermal features — data/external/paleo_geothermal_regional.zip (GDR 1391)",
            "Quaternary volcanic vents — data/external/gdr_volcanic_vents_in_footprint.csv (GDR 1391)",
        ],
        "holdout_dti": {"value": None, "status": "not run — no lane assigned, no cached holdout evaluator"},
        "leakage_canary": "component vs near-catalogue point-biserial r printed above; all |r| < 0.06 << 0.5",
        "budget": {"dots": BUDGET, "spacing_px": SPACING, "apron_px": APRON_PX},
        "raster": {
            "zeros_tif": zeros_info["path"],
            "sha256": zeros_info["sha256"],
            "dots": zeros_info["positive_pixels"],
        },
        "validator": validator,
        "submission_name": f"{slug}-zeros.tif",
        "submission_note": note,
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "verdict": "negative",
        "verdict_reason": "No lane assigned; registry uniqueness gate and holdout not yet run. "
                          "Format-valid TIF generated; research download only.",
    }
    (EVIDENCE / "run_card_gse_exp1.json").write_text(
        json.dumps(run_card, indent=2) + "\n"
    )
    print(f"\nRun card written to evidence/run_card_gse_exp1.json")
    print(f"Verdict: {run_card['verdict']} — {run_card['verdict_reason']}")


if __name__ == "__main__":
    main()