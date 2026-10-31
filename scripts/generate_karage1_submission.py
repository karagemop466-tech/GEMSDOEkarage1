#!/usr/bin/env python3
"""Generate a UNIQUE single-band GeoTIFF submission candidate for GEMSDOEkarage1.

Lane H-K1-SEISMIC-PROX
---------------------
Novel ingredient: official training band 10 ``deq_n100a15`` (distance to the
nearest earthquake within a 100 km, 15-degree-azimuth window).  A grep of
``src/gemskarage1/features.py`` shows the repo's 58-channel stack never uses
band 10 (only band 16 ``ieq_n100a15`` enters channel 48).  Seismic proximity is
therefore an unused official layer.

Physical mechanism
------------------
In the Great Basin, currently-active faults are seismogenic and are the structures
most likely to host geothermal systems; many of them are blind or only partly
mapped, so they are under-represented in the USGS/INGENIOUS catalogue.  A magnetic
horizontal-gradient crest supplies the structural position of a contact; a
seismic-proximity weight supplies the "this structure is active" prior.  Their
product is highest where an active structure is most likely to be missing from the
catalogue.

Metric reasoning (why dots, why a collar)
----------------------------------------
DTI = T / (T + 0.2 F + 0.8 (G - T)).  Known catalogue faults are masked from the
scored truth, so a dot within the 300 m kernel of a *known* fault but farther than
300 m from every *hidden* fault earns no TP and a full unit of FP.  Removing such
dots is therefore a mechanistically-motivated, not curve-fitted, improvement.  The
nine owner-reported sites used collars of at most 2 px; this lane uses the full
3 px kernel radius.

Dots (binary, p = 1) are near-optimal for this asymmetric objective: TP is linear
in p at the argmax location while FP is only weighted 0.2, so concentrating
probability into a sparse set beats spreading it.

Output
------
``docs/downloads/karage1-<name>-zeros.tif`` plus a .zip and a JSON run card.  The
file is format-valid and unique by construction, but it is NOT cleared for upload:
the hidden test labels are unavailable, so no organizer score exists and no
leaderboard estimate is produced.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

DATA = ROOT / ".cache" / "gems_data"
REGISTRY = ROOT / "registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"

FOCUS_SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
               "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")
LATTICE = "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"

KERNEL_PX = 3.0
NODATA = -3.4028234663852886e+38


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def disk(r: int) -> np.ndarray:
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    return (yy * yy + xx * xx) <= r * r


def triangular(radius: float) -> np.ndarray:
    r = int(np.ceil(radius))
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    d = np.hypot(yy, xx)
    return np.maximum(1.0 - d / radius, 0.0).astype(np.float64)


def robust_norm(x: np.ndarray, foot: np.ndarray) -> np.ndarray:
    v = x[foot]
    v = v[np.isfinite(v)]
    if v.size == 0:
        return np.zeros_like(x, dtype=np.float32)
    lo, hi = np.quantile(v, [0.02, 0.98])
    if not np.isfinite(hi) or hi <= lo:
        return np.zeros_like(x, dtype=np.float32)
    z = np.where(np.isfinite(x), (x - lo) / (hi - lo), 0.0)
    return np.clip(z, 0.0, 1.0).astype(np.float32)


def load_bands() -> dict:
    with rasterio.open(DATA / "sample_submission.tif") as src:
        ss = src.read(1)
        profile = src.profile
    foot = np.isfinite(ss)
    with rasterio.open(DATA / "labels.tif") as src:
        catalogue = src.read(1) > 0
    with rasterio.open(DATA / "training_features.tif") as src:
        nd = src.nodata
        arr = src.read()
    bands = {}
    for idx, name in ((2, "rtp"), (3, "tmi_hg"), (10, "deq"), (13, "iso_grav_anom"),
                      (18, "iso_grav_anom_hg")):
        b = arr[idx - 1].astype(np.float32)
        b = np.where(np.isfinite(b) & (b > nd), b, np.float32(np.nan))
        bands[name] = b
    return foot, catalogue, profile, bands


def build_field(bands, foot, catalogue, seis_weight: float, collar_px: int):
    rtp = bands["rtp"]
    deq = bands["deq"]
    g_hg = bands["iso_grav_anom_hg"]

    with np.errstate(invalid="ignore"):
        dx = ndimage.sobel(rtp, axis=1)
        dy = ndimage.sobel(rtp, axis=0)
    mag_edge = np.hypot(dx, dy)
    mag_edge = ndimage.gaussian_filter(mag_edge.astype(np.float32), 1.0, mode="nearest")
    mag_edge = robust_norm(mag_edge, foot)

    grav_edge = robust_norm(g_hg, foot)

    with np.errstate(invalid="ignore"):
        seis = np.exp(-np.nan_to_num(deq, nan=1e9) / 2500.0)
    seis = ndimage.gaussian_filter(seis.astype(np.float32), 1.5, mode="nearest")
    seis = robust_norm(seis, foot)

    structural = (0.55 * mag_edge + 0.25 * grav_edge + 0.20 * seis).astype(np.float32)
    # Foreground the novel seismic-proximity term.
    field = structural * (1.0 - seis_weight + seis_weight * seis)

    collar = ndimage.binary_dilation(catalogue, structure=disk(collar_px))
    gate = foot & ~collar
    field = np.where(gate, field, 0.0)
    field = np.nan_to_num(field, nan=0.0, posinf=0.0, neginf=0.0)
    return field.astype(np.float32), gate


def emit_dots(field, gate, budget: int, kernel_px: float = KERNEL_PX):
    """Exact greedy max-coverage dot selection with the official metric kernel.

    ``W(x) = sum_g F(g) k(d(x,g))`` is the expected true-positive coverage of a dot
    at ``x`` under the published triangular kernel (radius 3 px = 300 m).  After a dot
    is placed at ``x`` the truth mass it covers is removed from the residual field, so
    only ``W`` within ``2 r`` of ``x`` changes; that window is recomputed exactly from
    the residual field over a ``3 r`` window.  This maximises the metric numerator
    directly and naturally spaces dots at roughly the kernel radius instead of packing
    them around one peak.
    """
    r = int(np.ceil(kernel_px))
    k = triangular(kernel_px)
    h, w = field.shape
    wcov = ndimage.convolve(field, k, mode="constant", cval=0.0).astype(np.float32)
    wcov = np.where(gate, wcov, 0.0)
    f_rem = field.astype(np.float64).copy()
    emitted = np.zeros(field.shape, bool)
    n = 0
    for _ in range(budget):
        idx = int(np.argmax(wcov))
        if wcov.flat[idx] <= 0:
            break
        y, x = np.unravel_index(idx, wcov.shape)
        emitted[y, x] = True
        n += 1
        # remove the truth mass this dot covers (within r of x)
        cy0, cy1 = max(0, y - r), min(h, y + r + 1)
        cx0, cx1 = max(0, x - r), min(w, x + r + 1)
        kw_y0 = r - (y - cy0)
        kw_x0 = r - (x - cx0)
        kw = k[kw_y0:kw_y0 + (cy1 - cy0), kw_x0:kw_x0 + (cx1 - cx0)]
        covered = f_rem[cy0:cy1, cx0:cx1] * kw
        f_rem[cy0:cy1, cx0:cx1] -= covered
        # recompute W exactly over the 2r window from the 3r residual window
        wy0, wy1 = max(0, y - 2 * r), min(h, y + 2 * r + 1)
        wx0, wx1 = max(0, x - 2 * r), min(w, x + 2 * r + 1)
        fy0, fy1 = max(0, y - 3 * r), min(h, y + 3 * r + 1)
        fx0, fx1 = max(0, x - 3 * r), min(w, x + 3 * r + 1)
        sub = ndimage.convolve(f_rem[fy0:fy1, fx0:fx1], k, mode="constant", cval=0.0)
        wcov[wy0:wy1, wx0:wx1] = sub[wy0 - fy0:wy1 - fy0, wx0 - fx0:wx1 - fx0]
        wcov[~gate] = 0.0
    return emitted, int(n)


def write_geotiff(arr: np.ndarray, path: Path, profile: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    prof = dict(profile)
    prof.update(driver="GTiff", height=arr.shape[0], width=arr.shape[1],
                count=1, dtype="float32", compress="deflate",
                predictor=2, tiled=True, blockxsize=256, blockysize=256, nodata=None)
    with rasterio.open(path, "w", **prof) as dst:
        dst.write(arr.astype(np.float32), 1)


def validate(tif: Path, footprint: np.ndarray) -> dict:
    with rasterio.open(tif) as src:
        a = src.read(1)
        checks = {
            "single_band": src.count == 1,
            "dtype_float32": src.dtypes[0] == "float32",
            "crs_matches_template": str(src.crs) == "EPSG:32611",
            "shape_matches_template": (src.width, src.height) == (footprint.shape[1], footprint.shape[0]),
        }
    inside = a[footprint]
    outside = a[~footprint]
    checks.update({
        "in_footprint_all_finite": bool(np.isfinite(inside).all()),
        "in_footprint_range_0_1": bool(inside.min() >= 0.0 and inside.max() <= 1.0),
        "outside_all_zero": bool((outside == 0).all()),
        "no_inf_anywhere": bool(not np.isinf(a).any()),
        "no_nan_anywhere": bool(not np.isnan(a).any()),
    })
    checks["all_checks_passed"] = all(checks.values())
    return checks


def uniqueness_vs_registry(dots: np.ndarray, footprint: np.ndarray) -> dict:
    results = []
    for site in FOCUS_SITES:
        for path in sorted(REGISTRY.glob(f"{site}*.tif")):
            with rasterio.open(path) as src:
                a = src.read(1)
            ref = (np.isfinite(a) & (a > 0) & footprint)
            halo = ndimage.binary_dilation(ref, structure=disk(3))
            within = int((dots & halo).sum())
            total = int(dots.sum())
            frac = within / total if total else 0.0
            results.append({"reference": path.name, "candidate_dots": total,
                            "within_3px": within, "directed_overlap": float(frac),
                            "exceeds_70pct": bool(frac > 0.70)})
    lat = DATA / LATTICE
    if lat.is_file():
        with rasterio.open(lat) as src:
            a = src.read(1)
        ref = (np.isfinite(a) & (a > 0) & footprint)
        halo = ndimage.binary_dilation(ref, structure=disk(3))
        within = int((dots & halo).sum())
        total = int(dots.sum())
        results.append({"reference": "13GEMSDOE_lattice_calibration_probe",
                        "candidate_dots": total, "within_3px": within,
                        "directed_overlap": float(within / total if total else 0.0),
                        "exceeds_70pct": bool(within / total > 0.70 if total else False),
                        "role": "calibration_probe_diagnostic_only"})
    worst = max(results, key=lambda r: r["directed_overlap"])
    peers = [r for r in results if "lattice" not in r["reference"]]
    worst_peer = max(peers, key=lambda r: r["directed_overlap"])
    return {
        "registry_rasters_checked": len(results),
        "worst_forward_overlap": worst["directed_overlap"],
        "worst_forward_overlap_reference": worst["reference"],
        "worst_peer_forward_overlap": worst_peer["directed_overlap"],
        "worst_peer_reference": worst_peer["reference"],
        "unique_by_literal_rule_vs_peers": bool(worst_peer["directed_overlap"] <= 0.70),
        "pairwise": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--name", default=None)
    ap.add_argument("--seis-weight", type=float, default=0.55)
    ap.add_argument("--collar-px", type=int, default=3)
    ap.add_argument("--budget", type=int, default=37654)
    ap.add_argument("--kernel-px", type=float, default=3.0)
    ap.add_argument("--tag", default=None)
    args = ap.parse_args()

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    tag = args.tag or f"{stamp}"
    name = args.name or f"karage1-seisprox-c{args.collar_px}-w{args.seis_weight:.2f}-{tag}"

    foot, catalogue, profile, bands = load_bands()
    print(f"Grid {foot.shape[0]}x{foot.shape[1]}, footprint={int(foot.sum())}, "
          f"catalogue={int(catalogue.sum())}")

    field, gate = build_field(bands, foot, catalogue, args.seis_weight, args.collar_px)
    print(f"Collar {args.collar_px} px: gated pixels={int(gate.sum())} "
          f"({100*gate.sum()/foot.sum():.2f}% of footprint)")

    dots, n = emit_dots(field, gate, args.budget, args.kernel_px)
    dots &= gate
    n = int(dots.sum())
    print(f"Dots emitted: {n} (budget {args.budget}), all in gate: {bool((dots & ~gate).sum() == 0)}")

    cand = np.where(dots, np.float32(1.0), np.float32(0.0)).astype(np.float32)
    cand[~foot] = 0.0

    tif_path = DOWNLOADS / (name + "-zeros.tif")
    write_geotiff(cand, tif_path, profile)
    zip_path = tif_path.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(tif_path, arcname=tif_path.name)

    checks = validate(tif_path, foot)
    print("Validation:", checks)

    uniq = uniqueness_vs_registry(dots, foot)
    print(f"Uniqueness: worst peer overlap={uniq['worst_peer_forward_overlap']:.4f} "
          f"({uniq['worst_peer_reference']}), "
          f"unique_vs_peers={uniq['unique_by_literal_rule_vs_peers']}")
    print(f"Lattice diagnostic overlap={uniq['worst_forward_overlap']:.4f} "
          f"({uniq['worst_forward_overlap_reference']})")

    sha = sha256_file(tif_path)

    note = (f"Seismic-proximity (band10) x magnetic/gravity edge, {args.collar_px}px "
            f"catalogue collar, {n} dots; research candidate")
    assert len(note) <= 140, len(note)

    card = {
        "schema": "karage1-run-card-v4",
        "generated_utc": stamp,
        "lane_id": "H-K1-SEISMIC-PROX",
        "hypothesis": (
            "Official band 10 deq_n100a15 (distance to nearest earthquake) is unused by "
            "the repo 58-channel stack.  Weighting a magnetic/gravity structural edge by "
            "seismic proximity marks active, commonly blind, Great Basin faults that are "
            "under-mapped in the USGS/INGENIOUS catalogue."
        ),
        "mechanism": (
            "Magnetic horizontal-gradient crest = structural contact position; "
            "exp(-deq/2500 m) = seismogenic-activity prior.  Product is high where an "
            "active structure is most likely absent from the catalogue.  Dots are placed "
            "only outside a 3 px (300 m) catalogue collar, so no submitted dot can earn "
            "FP from a masked known fault, and only at kernel-spaced peaks of the "
            "expected-coverage convolution."
        ),
        "named_non_fault_mimic": (
            "Earthquake clouds on non-fault structures (volcanic collapse, regional "
            "stress), lithologic magnetic contacts, and the smooth 100 km seismicity "
            "window itself."
        ),
        "holdout_dti": {"label": "HOLDOUT-DTI", "status": "NOT_COMPUTED_AS_LEADERBOARD",
                        "note": "Catalogue hide-and-recover holdout rewards re-finding mapped "
                                "traces and penalises off-catalogue placement by construction; "
                                "it cannot rank this candidate.  No leaderboard estimate is produced."},
        "registry_correlation_overlap": uniq,
        "raster": {"tif": tif_path.name, "zip": zip_path.name, "sha256": sha,
                   "bytes": int(tif_path.stat().st_size), "dots": n,
                   "dtype": "float32", "crs": "EPSG:32611",
                   "shape": [int(foot.shape[0]), int(foot.shape[1])]},
        "validator_output": checks,
        "submission_name": tif_path.name,
        "submission_note": note,
        "submission_note_chars": len(note),
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "verdict": "negative",
        "verdict_reason": (
            "Unique, format-valid GeoTIFF generated for research/audit.  Hidden test labels "
            "are unavailable, so no organizer score exists; no method lane was assigned by the "
            "owner; no weekly slot was selected.  NOT cleared for DrivenData upload."
        ),
        "variant": {"seis_weight": args.seis_weight, "collar_px": args.collar_px,
                    "budget": args.budget},
    }
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    card_path = EVIDENCE / f"run_card_{name}.json"
    card_path.write_text(json.dumps(card, indent=2) + "\n")
    print(f"\nRun card: {card_path}")
    print(f"SHA-256: {sha}")
    print(f"Download (research only): {tif_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
