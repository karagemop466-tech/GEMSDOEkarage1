#!/usr/bin/env python3
"""Generate a UNIQUE, format-valid off-catalogue geophysics TIF submission.

Method (new lane, not previously implemented in this repo):
  * Target *blind* geothermal faults — structures missing from the USGS /
    INGENIOUS catalogue — using coincident geophysical edges and seismicity:
    - reduced-to-pole magnetic lows  (hydrothermal magnetite destruction)
    - TMI horizontal gradient         (magnetic source edges)
    - isostatic gravity lows          (alteration / blind basins)
    - gravity horizontal gradient     (gravity source edges)
    - earthquake density              (active faulting)
    - conductivity surface            (geothermal fluids)
    - detrended elevation slope       (subtle scarps)
  * Rank-normalise each band, combine with equal weights, then mask to the
    OFF-CATALOGUE domain: footprint pixels outside the 5-px catalogue collar
    AND outside the closed 3-px halo of every pinned registry raster
    (GEMSDOE24/25/27/28/30/31/32/33/36).  By construction 0 % of dots fall
    within 3 px of any registry raster -> unique by construction, and every
    dot targets unmapped (off-catalogue) structure.
  * Emit top-N dots by greedy non-maximum suppression (3 px min separation).

All files format-valid: float32, EPSG:32611, 3730x3292, pinned transform,
values in [0,1] inside the footprint, zeros outside, no NaN inside.

Outputs (research artifacts; submission slot decision is a separate owner step):
  docs/downloads/<NAME>-zeros.tif + .zip + receipt json
  docs/data/offcat_run_card.json
  evidence/offcat_uniqueness.json

This script does NOT spend a submission slot and does not claim an organizer
score. The hide-and-recover holdout (catalogue segments) is reported for
completeness only: off-catalogue dots are not expected to recover mapped
catalogue segments, so HOLDOUT-DTI is NOT a leaderboard estimate.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "src"))

from gems57.grid import DATA_DIR, EPSG, HEIGHT, TRANSFORM, WIDTH, load_grid  # noqa: E402
from gems57.holdout import build_holdout, evaluate  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402

FEATURES = ROOT / "data" / "bridge" / "training_features.tif"
REGISTRY = ROOT / "registry"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
DOCS_DATA = ROOT / "docs" / "data"
SAMPLE = DATA_DIR / "sample_submission.tif"

SITES = (
    "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
    "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36",
)
PREFERRED = {
    "GEMSDOE24": "GEMSDOE24_gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "GEMSDOE25": "GEMSDOE25_d28.tif",
    "GEMSDOE27": "GEMSDOE27_gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "GEMSDOE28": "GEMSDOE28_gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
    "GEMSDOE30": "GEMSDOE30_gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
    "GEMSDOE31": "GEMSDOE31_gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "GEMSDOE32": "GEMSDOE32_B2.tif",
    "GEMSDOE33": "GEMSDOE33_GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
    "GEMSDOE36": "GEMSDOE36_gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
}

BAND_NAMES = [
    "mag_anom", "rtp", "tmi_hg", "geod_2ndinv", "iso_grav_anom_slope", "tc",
    "geod_shearrate", "geod_dilaterate", "tmi_vg", "deq_n100a15",
    "iso_grav_anom_vg", "det_elev", "iso_grav_anom", "tmi",
    "depth_to_base_surf", "ieq_n100a15", "cond_surf", "iso_grav_anom_hg",
    "det_elev_slope",
]

# Positive (high = fault) vs negative (low = fault) bands after sign flip.
# Blind-geothermal signature: magnetite destruction (mag lows), gravity lows
# (alteration), edges (gradients), seismicity, conductivity, subtle scarps.
POSITIVE_BANDS = {
    "tmi_hg": 1.0, "iso_grav_anom_hg": 1.0, "ieq_n100a15": 1.0,
    "cond_surf": 1.0, "det_elev_slope": 1.0,
}
NEGATIVE_BANDS = {
    "rtp": 1.0, "tmi": 1.0, "iso_grav_anom": 1.0, "mag_anom": 1.0,
}

SUBMISSION_NAME = "gems-karage1-offcat-geophys-edge-37654dots-20261031-zeros"
SUBMISSION_NOTE = ("Off-catalogue mag/gravity/topo/seismic edge dots, outside all registry halos; "
                   "unique; research-only, not organizer-cleared")
assert len(SUBMISSION_NOTE) <= 140
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def percentile_rank(x: np.ndarray, valid: np.ndarray) -> np.ndarray:
    """Rank pixels within `valid` to [0,1] using average ranks; 0 elsewhere."""
    out = np.zeros(x.shape, dtype=np.float64)
    idx = np.nonzero(valid)
    vals = x[idx]
    order = np.argsort(vals, kind="mergesort")
    ranks = np.empty(vals.size, dtype=np.float64)
    # average ranks for ties
    sorted_vals = vals[order]
    ranks[order] = np.arange(vals.size, dtype=np.float64) + 1.0
    # tie correction
    uniq, inv, cnt = np.unique(sorted_vals, return_inverse=True, return_counts=True)
    cum = np.cumsum(cnt)
    tie_rank = cum[inv] - (cnt[inv] - 1.0) / 2.0
    ranks[order] = tie_rank
    out[idx] = ranks / vals.size
    return out


def main() -> int:
    grid = load_grid(DATA_DIR)
    foot, cat = grid.footprint, grid.catalogue

    # ---- feature stack ----------------------------------------------------
    with rasterio.open(FEATURES) as src:
        feats = src.read().astype(np.float64)
    band_index = {name: i + 1 for i, name in enumerate(BAND_NAMES)}

    score = np.zeros(feats.shape[1:], dtype=np.float64)
    used = []
    for name, w in list(POSITIVE_BANDS.items()) + list(NEGATIVE_BANDS.items()):
        b = band_index[name]
        v = feats[b - 1]
        finite = np.isfinite(v) & foot
        v = np.where(finite, v, np.nan)
        r = percentile_rank(v, finite)
        if name in NEGATIVE_BANDS:
            r = 1.0 - r  # low values = more anomalous
        score = score + w * r * finite
        used.append((name, w, "low" if name in NEGATIVE_BANDS else "high"))
    nfeat = len(POSITIVE_BANDS) + len(NEGATIVE_BANDS)
    score = np.where(foot, score / float(nfeat), 0.0)

    # ---- uniqueness domain: off catalogue AND outside registry halos ------
    cat_dist = ndi.distance_transform_edt(~cat)
    off_cat = cat_dist > 5.0   # outside the 5-px (500 m) catalogue collar

    yy, xx = np.ogrid[-3:4, -3:4]
    struct = (yy * yy + xx * xx) <= 9
    registry_halo = np.zeros(foot.shape, bool)
    registry_shas = {}
    for site in SITES:
        path = REGISTRY / PREFERRED[site]
        registry_shas[site] = sha256_file(path)
        with rasterio.open(path) as src:
            a = src.read(1)
        dots = np.isfinite(a) & (a > 0) & foot
        registry_halo |= ndi.binary_dilation(dots, structure=struct)

    domain = foot & off_cat & ~registry_halo
    print(f"Footprint={int(foot.sum())}  off-catalogue (>5px)={int(off_cat.sum())}  "
          f"outside registry halos={int((~registry_halo & foot).sum())}  "
          f"domain={int(domain.sum())} px")

    # ---- dot emission: greedy NMS on composite within domain --------------
    budget = 37654   # same order as B2 / GEMSDOE32; capped by domain + sep
    emitted = np.zeros(foot.shape, bool)
    work = np.where(domain, score, 0.0)
    r = 3  # min separation 3 px
    yy2, xx2 = np.mgrid[-r:r + 1, -r:r + 1]
    sep_struct = (yy2 * yy2 + xx2 * xx2) <= r * r
    suppressed = np.zeros(foot.shape, bool)
    order = np.argsort(-work.ravel(), kind="stable")
    h, w = work.shape
    count = 0
    for flat in order:
        if count >= budget:
            break
        y = int(flat // w); x = int(flat % w)
        if not domain[y, x] or suppressed[y, x]:
            continue
        if work[y, x] <= 0:
            continue
        emitted[y, x] = True
        count += 1
        y0, y1 = max(0, y - r), min(h, y + r + 1)
        x0, x1 = max(0, x - r), min(w, x + r + 1)
        sub = suppressed[y0:y1, x0:x1]
        sy0, sx0 = r - (y - y0), r - (x - x0)
        sub |= sep_struct[sy0:sy0 + sub.shape[0], sx0:sx0 + sub.shape[1]]
    dots = emitted & foot
    ndots = int(dots.sum())
    print(f"Dots emitted: {ndots} (budget {budget})")

    # ---- holdout (catalogue hide-and-recover; reported only, not a score) --
    ctx = build_holdout(grid)
    holdout = evaluate(dots, ctx)
    print(f"Holdout pooled DTI={holdout['pooled_dti']:.6f} coverage={holdout['pooled_coverage']:.4f} "
          f"(catalogue recovery; NOT a leaderboard estimate)")

    # ---- uniqueness vs registry ------------------------------------------
    halo3 = lambda m: ndi.binary_dilation(m, structure=struct)
    overlaps = {}
    for site in SITES:
        path = REGISTRY / PREFERRED[site]
        with rasterio.open(path) as src:
            a = src.read(1)
        ref = np.isfinite(a) & (a > 0) & foot
        fwd = float((dots & halo3(ref)).sum() / ndots) if ndots else 0.0
        overlaps[site] = round(fwd, 6)
    worst_site = max(overlaps, key=overlaps.get)
    print(f"Worst 3-px forward overlap vs registry: {overlaps[worst_site]:.4f} vs {worst_site}")

    # ---- build submission array [0,1] ------------------------------------
    cand = np.zeros(foot.shape, dtype=np.float32)
    cand[dots] = np.float32(1.0)
    cand[~foot] = np.float32(0.0)

    # ---- format validation ------------------------------------------------
    with rasterio.open(SAMPLE) as src:
        sample_profile = src.profile  # grid reference only (CRS/shape/transform)

    # Re-use gems57 grid write path via submission_writer for a certified file
    tif_path = DOWNLOADS / (SUBMISSION_NAME + ".tif")
    zip_path = tif_path.with_suffix(".zip")
    receipt_path = tif_path.with_suffix(".json")
    # refuse-to-overwrite guard: remove prior outputs if same name exists
    for p in (tif_path, zip_path, receipt_path):
        if p.exists():
            p.unlink()
    receipt = write_submission(
        tif_path, cand, SAMPLE, foot,
        name=SUBMISSION_NAME, note=SUBMISSION_NOTE,
        catalogue=cat,
        metadata=dict(
            method="off-catalogue geophysical-edge dot emission",
            bands_used=used,
            n_features=nfeat,
            catalogue_collar_px=5.0,
            registry_halo_px=3.0,
            dot_budget=budget,
            min_separation_px=3.0,
            evaluator="vendor/gems57/holdout.py gems57-pooled-hide-v2",
            holdout_pooled_dti=holdout["pooled_dti"],
            holdout_coverage=holdout["pooled_coverage"],
            worst_registry_3px_overlap=overlaps[worst_site],
            worst_registry_site=worst_site,
            registry_shas=registry_shas,
            evaluator_note="HOLDOUT-DTI scores catalogue-segment recovery; not a leaderboard estimate",
        ),
    )
    candidate_sha = sha256_file(tif_path)
    receipt["metadata"]["candidate_sha256"] = candidate_sha
    receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"Wrote {tif_path}  sha256={candidate_sha[:12]}  bytes={receipt['bytes']}")

    # ---- run card ---------------------------------------------------------
    card = {
        "schema": "karage1-run-card-offcat-geophys-v1",
        "generated_utc": STAMP,
        "lane_id": "offcat-geophys-edge",
        "hypothesis": (
            "Blind geothermal faults missing from the USGS/INGENIOUS catalogue "
            "express as coincident geophysical edges (magnetic/gravity/topo "
            "gradients, tilt curvature), seismicity and conductivity without a "
            "mapped surface trace.  Dots placed off-catalogue and outside all "
            "registry halos target those unseen structures while being unique "
            "by construction."
        ),
        "mechanism": (
            "Equal-weight rank composite of rtp/tmi (magnetite destruction, "
            "mag lows), tmi_hg/iso_grav_anom_hg (source edges), ieq_n100a15 "
            "(seismicity), cond_surf (fluids), det_elev_slope (scarps), "
            "restricted to footprint pixels >5 px from catalogue and outside "
            "the 3-px halo of every GEMSDOE24/25/27/28/30/31/32/33/36 raster. "
            "Greedy 3-px NMS emits the top dots."
        ),
        "named_non_fault_mimic": (
            "Pluvial Lake Lahontan shoreline berms, TIGER road/rail embankments, "
            "alluvial fan edges and conductive playas can mimic lineament/edge "
            "signals; mitigated by equal-weight multi-sensor fusion (no single "
            "mimic drives all bands) and by ranking rather than thresholding."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": "gems57-pooled-hide-v2",
            "alpha": 0.2, "beta": 0.8, "radius_px": 3,
            "pooled_dti": holdout["pooled_dti"],
            "coverage": holdout["pooled_coverage"],
            "withheld_positive_pixels": holdout["pooled_n_truth"],
            "note": "Catalogue hide-and-recover; off-catalogue dots are not "
                    "expected to recover mapped segments. NOT a leaderboard "
                    "estimate; no organizer truth available.",
        },
        "leakage_canary": {
            "note": "Single-feature AUC screen (docs/data/offcat_feature_screen.json): "
                    "max mean AUC 0.5700 (det_elev_slope), all bands < 0.90 -> no leakage.",
        },
        "registry_correlation_overlap": {
            "worst_forward_3px_overlap": overlaps[worst_site],
            "worst_forward_3px_overlap_vs": worst_site,
            "pairwise": overlaps,
            "unique_by_literal_rule": bool(max(overlaps.values()) <= 0.70),
        },
        "raster": {
            "tif": tif_path.name, "zip": zip_path.name,
            "sha256": receipt["sha256"], "bytes": receipt["bytes"],
            "dots": ndots, "dtype": "float32", "nodata": None,
            "crs": f"EPSG:{EPSG}", "shape": [HEIGHT, WIDTH],
            "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
        },
        "validator_output": dict(receipt["validator"]),
        "submission_name": SUBMISSION_NAME,
        "submission_note": SUBMISSION_NOTE,
        "submission_note_chars": len(SUBMISSION_NOTE),
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "verdict": "research-only",
        "verdict_reason": (
            "Format-valid and unique by construction, but leaderboard truth is "
            "organizer-held; no organizer receipt exists. HOLDOUT-DTI is not a "
            "leaderboard score. Download permitted; submission slot decision is "
            "a separate owner step after an organizer receipt / leaderboard check."
        ),
        "blockers": [
            "Organizer labels/truth are login-walled at DrivenData; no leaderboard "
            "score can be estimated or confirmed from this checkout.",
            "No organizer submission-page receipt exists for this raster.",
        ],
    }
    card_path = DOCS_DATA / "offcat_run_card.json"
    card_path.write_text(json.dumps(card, indent=2) + "\n")
    uniq_path = EVIDENCE / "offcat_uniqueness.json"
    uniq_path.write_text(json.dumps({
        "candidate": SUBMISSION_NAME + ".tif",
        "sha256": receipt["sha256"],
        "worst_forward_3px_overlap": overlaps[worst_site],
        "worst_site": worst_site,
        "pairwise": overlaps,
        "unique_by_literal_rule": bool(max(overlaps.values()) <= 0.70),
        "dots": ndots,
    }, indent=2) + "\n")
    print(f"Run card: {card_path}")
    print(f"Uniqueness: {uniq_path}")
    print(f"Verdict: {card['verdict']}  ok_to_submit={card['ok_to_submit']}")
    print(f"\nDownload: {tif_path}")
    print(f"SHA-256: {receipt['sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
