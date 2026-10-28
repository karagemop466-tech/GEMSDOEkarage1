#!/usr/bin/env python3
"""
QUARANTINED historical Conduitcrest generator — DO NOT USE TO CREATE A SUBMISSION.

A prior parallel session generated a 17,415-dot TIFF using a territory mask that
excluded halos around only the nine focus-site rasters. That is not the complete
registry check required by the protocol: an independent saved-byte audit found
99.3454% of its dots within 3 px of the pinned lattice. The archived run card also
omits a pre-placement lattice check, a complete inventory, a per-feature canary,
and a 95% CI for its reported HOLDOUT-DTI claim. `registry/template.json` has no
assigned lane and local template integrity is not authorized.

The executable entry point below fails closed before any output is written. The
remaining implementation is retained for historical code review only. Its former
claims of uniqueness, submission readiness, and automatic resolution of the
`[0,1]` error are superseded and must not be repeated.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57.grid import load_grid, DATA_DIR  # noqa: E402
from gems57 import evaluate_holdout as eh57  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402
from gems57.gates import format_report  # noqa: E402
from gems57.uniqueness import compare_array_to_registry  # noqa: E402
from gems57.holdout import build_holdout, evaluate as holdout_evaluate  # noqa: E402
from gems57.metric import dti_binary  # noqa: E402

# --------------------------------------------------------------------------- #
# Declared single lane
# --------------------------------------------------------------------------- #
LANE_ID = "novel-territory-potential-field-conduit-crest"
SUBMISSION_NAME = (
    "gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4"
)
SUBMISSION_NOTE = (
    "Conduitcrest research artifact; duplicate vs pinned lattice; DO NOT SUBMIT"
)
assert len(SUBMISSION_NAME) <= 140, "submission name must be <= 140 chars"
assert len(SUBMISSION_NOTE) <= 140, "submission note must be <= 140 chars"

FOCUS_SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
               "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")
CACHE = ROOT / ".cache" / "references"
DOWNLOADS = ROOT / "docs" / "downloads"
EVIDENCE = ROOT / "evidence"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

# --------------------------------------------------------------------------- #
# 1. Load grid + training features
# --------------------------------------------------------------------------- #
def load_signature(foot: np.ndarray) -> np.ndarray:
    """Catalogue-independent physical signature in [0,1], zero outside footprint."""
    with rasterio.open(DATA_DIR / "training_features.tif") as src:
        b5 = src.read(5).astype(np.float64)   # iso_grav_anom_slope |∇h g|
        b6 = src.read(6).astype(np.float64)   # radiometric total count
        b18 = src.read(18).astype(np.float64) # iso_grav_anom_hg signed ∂g/∂x
        b12 = src.read(12).astype(np.float64) # det_elev
    # Robust [0,1] normalisation on the footprint (median/MAD, clip at 6 z).
    def robust01(a: np.ndarray) -> np.ndarray:
        sub = a[foot][::4]
        med = float(np.median(sub))
        mad = max(float(np.median(np.abs(sub - med))) * 1.4826, 1e-9)
        z = np.clip((a - med) / mad, -6.0, 6.0)
        out = np.where(foot, np.maximum(z, 0.0) / 6.0, 0.0)
        return np.clip(out, 0.0, 1.0)
    grav_slope = robust01(b5)
    grav_grad = robust01(np.abs(b18))
    rad_tc = robust01(b6)
    dem_relief = robust01(ndi_relief(b12, foot))
    sig = grav_slope * grav_grad * rad_tc * dem_relief
    return np.where(foot & np.isfinite(sig), sig, 0.0).astype(np.float32)


def ndi_relief(dem: np.ndarray, foot: np.ndarray) -> np.ndarray:
    from scipy.ndimage import maximum_filter, minimum_filter
    return np.where(foot,
                    maximum_filter(dem, size=5) - minimum_filter(dem, size=5),
                    0.0).astype(np.float64)


# --------------------------------------------------------------------------- #
# 2. Novel-territory gate (outside every registry raster's 3 px halo)
# --------------------------------------------------------------------------- #
def novel_territory_mask(foot: np.ndarray) -> np.ndarray:
    yy, xx = np.ogrid[-3:4, -3:4]
    struct = yy * yy + xx * xx <= 9
    halo = np.zeros(foot.shape, bool)
    for site in FOCUS_SITES:
        p = CACHE / (site + ".tif")
        with rasterio.open(p) as ds:
            a = ds.read(1)
        supp = np.isfinite(a) & (a > 0) & foot
        halo |= binary_dilation(supp, structure=struct)
    novel = foot & ~halo
    return novel, halo


# --------------------------------------------------------------------------- #
# 3. Dot emission (greedy non-maximum suppression, 3 px min separation)
# --------------------------------------------------------------------------- #
def emit_dots(signature: np.ndarray, novel: np.ndarray, budget: int,
              min_sep_px: float = 3.0) -> np.ndarray:
    """Greedy NMS emission.  Returns bool mask on the full grid."""
    h, w = signature.shape
    order = np.argsort(-signature.ravel(), kind="stable")  # descending, flat
    emitted = np.zeros((h, w), bool)
    # separation kernel
    r = int(np.ceil(min_sep_px))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    sep_struct = (yy * yy + xx * xx) <= min_sep_px * min_sep_px
    suppressed = np.zeros((h, w), bool)
    count = 0
    for flat in order:
        if count >= budget:
            break
        y, x = int(flat // w), int(flat % w)
        y = int(np.asarray(y).item()); x = int(np.asarray(x).item())
        if not novel[y, x] or suppressed[y, x]:
            continue
        if signature[y, x] <= 0:
            continue
        emitted[y, x] = True
        count += 1
        # suppress neighbourhood
        y0, y1 = max(0, y - r), min(h, y + r + 1)
        x0, x1 = max(0, x - r), min(w, x + r + 1)
        sy0, sx0 = r - (y - y0), r - (x - x0)
        sub = suppressed[y0:y1, x0:x1]
        sh = sep_struct[sy0:sy0 + sub.shape[0], sx0:sx0 + sub.shape[1]]
        sub |= sh
    return emitted


# --------------------------------------------------------------------------- #
# main
# --------------------------------------------------------------------------- #
def main() -> int:
    # Quarantine this earlier generator after a post-run audit found that its
    # saved raster has 99.3454% directed overlap with the pinned 13GEMSDOE
    # lattice. Its original run only compared the nine focus-site rasters and
    # did not complete the per-feature canary or provide a 95% holdout CI.
    # Refuse to emit another file until an authorized lane/template and a
    # corrected shared workflow exist; do not evade the lattice with placement.
    print(
        'BLOCKED: historical Conduitcrest generator is superseded by '
        'evidence/conduitcrest_lattice_reaudit_20261028.json (99.3454% lattice overlap within 3 px). '
        'No new candidate or submission was written.',
        file=sys.stderr,
    )
    return 2

    t0 = time.time()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)

    ddir = Path(DATA_DIR)
    g = load_grid(ddir)
    foot, cat = g.footprint, g.catalogue
    print(f"[1/8] grid loaded: footprint={int(foot.sum())} catalogue={int(cat.sum())}")

    # ---- signature ------------------------------------------------------- #
    sig = load_signature(foot)
    print(f"[2/8] signature built: max={float(sig.max()):.4f} novel-eligible px={int((foot & (sig>0)).sum())}")

    # ---- novelty gate ---------------------------------------------------- #
    novel, halo = novel_territory_mask(foot)
    print(f"[3/8] novel territory (outside all 9 registry 3-px halos): {int(novel.sum())} px "
          f"({100*novel.sum()/foot.sum():.2f}% of footprint); catalogue px on novel territory: {int((cat & novel).sum())}")

    # ---- holdout context (hide-and-recover, whole-segment draws) ---------- #
    ctx = build_holdout(g, hide_frac=0.20, seeds=(20, 21), modes=("all", "detached"))
    n_truth = sum(c.n_truth for c in ctx.cells)
    print(f"[4/8] holdout built: {len(ctx.cells)} cells, {n_truth} withheld truth px total")

    # ---- emit dots ------------------------------------------------------- #
    # Budget tuned to the withheld truth mass so FP mass stays bounded.
    budget = min(24000, max(4000, int(0.6 * n_truth)))
    dots = emit_dots(sig, novel, budget, min_sep_px=3.0)
    dots &= foot
    dots &= ~cat  # no mass on mapped catalogue (masked in scoring; writer rejects it)
    ndots = int(dots.sum())
    print(f"[5/8] dots emitted: {ndots} (budget {budget}); on catalogue={int((dots & cat).sum())}; "
          f"on novel territory={int((dots & novel).sum())}")

    # ---- holdout score (shared gems57 evaluator) ------------------------- #
    res = holdout_evaluate(dots, ctx)
    pooled = res["pooled_dti"]
    print(f"[6/8] HOLDOUT-DTI (pooled, all modes) = {pooled:.6f}  "
          f"emit={res['emitted_pixels']} on_cat={res['on_visible_catalogue']}")
    # per-mode breakdown
    for mode in ("all", "detached"):
        rm = holdout_evaluate(dots, ctx, cell_mode=mode)
        print(f"       mode={mode:8s} DTI={rm['pooled_dti']:.6f} "
              f"truth={rm['pooled_n_truth']} emit={rm['emitted_pixels']}")

    # ---- uniqueness vs registry (literal gate) --------------------------- #
    registry_index = [
        dict(repo=f"buffedlizard55-lab/GEMSDOE{s[6:]}", submission=s,
             file=str(CACHE / (s + ".tif")),
             sha256=hashlib.sha256((CACHE / (s + ".tif")).read_bytes()).hexdigest(),
             sources=[s])
        for s in FOCUS_SITES
    ]
    # candidate as float array in [0,1]
    cand = np.where(dots, np.float32(1.0), np.float32(0.0)).astype(np.float32)
    with rasterio.open(ddir / "sample_submission.tif") as ref:
        expected_grid = (ref.shape, ref.crs, ref.transform)
    uniq = compare_array_to_registry(
        cand, registry_index, foot,
        expected_grid=expected_grid,
        progress=lambda i, n, row: None,
    )
    worst_ov = uniq.get("worst_dot_overlap")
    worst_rho = uniq.get("worst_spearman_full_footprint")
    literal_unique = (worst_ov is not None and worst_ov <= 0.70) and (worst_rho is None or worst_rho <= 0.90)
    print(f"[7/8] uniqueness (literal rule): forward_overlap={worst_ov} (<=0.70 PASS) "
          f"spearman={worst_rho} (<=0.90 PASS) unique_by_literal_rule={literal_unique} "
          f"checked={uniq['registry_rasters_checked']}/{uniq['registry_rasters_expected']} "
          f"(complete_accessible_scan={uniq.get('complete_accessible_scan')}: owner-mirror inventory only)")

    # ---- write submission (shared writer, fail-closed format validation) -- #
    out_tif = DOWNLOADS / (SUBMISSION_NAME + "-zeros.tif")
    receipt = write_submission(
        out_tif, cand, ddir / "sample_submission.tif", foot,
        note=SUBMISSION_NOTE, name=SUBMISSION_NAME,
        catalogue=cat,
        metadata={"lane_id": LANE_ID, "generated_utc": STAMP,
                  "budget": budget, "ndots": ndots},
    )
    print(f"[8/8] wrote {out_tif.name} sha256={receipt['sha256'][:16]}... "
          f"validator_ok={receipt['validator'].get('all_checks_passed')}")

    # ---- standalone format re-check (gates.format_report) ---------------- #
    fmt = format_report(out_tif, ddir / "sample_submission.tif", footprint=foot)
    print(f"       format_report: ok={fmt['ok']} problems={fmt['problems']} "
          f"nan={fmt.get('nan_pixels')} in01={fmt.get('min')}..{fmt.get('max')}")

    # ---- run card -------------------------------------------------------- #
    card = {
        "schema": "karage1-run-card-v3",
        "generated_utc": STAMP,
        "session": "arena/6c48ab7e-gemsdoekarage1",
        "lane_id": LANE_ID,
        "hypothesis": (
            "Unmapped geothermal-indicative faults cluster on 'novel territory' far from all nine "
            "prior GEMSDOE site submissions (H19-5 / lattice family).  A catalogue-independent "
            "signature (gravity slope x gravity gradient x radiometric TC x DEM relief) placed there "
            "recovers withheld catalogue faults on novel territory while staying outside every "
            "registry raster's 3 px halo, so it is unique by construction."
        ),
        "mechanism": (
            "Basin-and-Range normal/transtensional fault damage zones localise gravity-gradient and "
            "radiometric alteration crests on piedmonts.  Existing submissions densely cover the "
            "catalogue/lattice corridor; the complementary fault set lies outside their 3 px halos. "
            "Placing dots only there guarantees literal uniqueness (<70% forward overlap vs any "
            "registry raster) while the hide-and-recover holdout measures recovery of withheld "
            "catalogue segments on that same novel territory."
        ),
        "named_non_fault_mimic": (
            "Pluvial Lake Lahontan shoreline berms, TIGER road/rail embankments, and flat conductive "
            "playas can mimic linear gravity/radiometric crests; mitigated by the 100 m DEM relief "
            "factor and by requiring novel-territory placement (shorelines/roads are already dense in "
            "prior submissions and thus excluded by the halo gate)."
        ),
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evidence_class": "HOLDOUT-DTI",
            "evaluator_version": eh57.VERSION,
            "evaluator_implementation_sha256": eh57.implementation_hashes(),
            "alpha": 0.2, "beta": 0.8, "triangular_radius_m": 300.0,
            "pooled_dti_all_modes": round(float(pooled), 6),
            "withheld_positive_pixels_total": int(n_truth),
            "emitted_pixels": int(res["emitted_pixels"]),
            "on_visible_catalogue_pixels": int(res["on_visible_catalogue"]),
            "per_mode": {
                m: dict(dti=round(float(holdout_evaluate(dots, ctx, cell_mode=m)["pooled_dti"]), 6),
                        withheld_positive_pixels=int(holdout_evaluate(dots, ctx, cell_mode=m)["pooled_n_truth"]),
                        emitted_pixels=int(holdout_evaluate(dots, ctx, cell_mode=m)["emitted_pixels"]))
                for m in ("all", "detached")
            },
            "note": "Catalogue-truth hide-and-recover holdout; NOT a leaderboard estimate or projection.",
        },
        "registry_correlation_overlap": {
            "registry_rasters_checked": int(uniq["registry_rasters_checked"]),
            "registry_rasters_expected": int(uniq["registry_rasters_expected"]),
            "complete_accessible_scan": bool(uniq["complete_accessible_scan"]),
            "worst_spearman_full_footprint": uniq.get("worst_spearman_full_footprint"),
            "worst_forward_overlap": uniq.get("worst_dot_overlap"),
            "worst_forward_overlap_submission": uniq.get("worst_overlap_submission"),
            "worst_jaccard": uniq.get("worst_jaccard_dot_sets"),
            "duplicate_count": int(uniq.get("duplicate_count", 0)),
            "unique_by_literal_rule": bool(literal_unique),
            "unique": bool(literal_unique),
            "rho_limit": 0.90, "overlap_limit": 0.70,
            "novel_territory_pixels": int(novel.sum()),
            "dots_on_novel_territory": int((dots & novel).sum()),
            "scope": "Nine pinned focus-site rasters (owner mirrors); not a complete organizer registry.",
        },
        "leakage_canary": {
            "note": "Signature uses only the 19-band training stack (geophysics/DEM), never the catalogue; "
                    "single-feature canary should be run per-channel before any slot is spent.",
        },
        "raster": {
            "tif": out_tif.name,
            "zip": out_tif.with_suffix(".zip").name,
            "receipt": out_tif.with_suffix(".json").name,
            "sha256": receipt["sha256"],
            "bytes": int(receipt["bytes"]),
            "dots": int(ndots),
            "dtype": "float32", "nodata": None,
            "crs": "EPSG:32611", "shape": [3730, 3292],
            "transform": [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0],
        },
        "validator_output": {
            "format_report": fmt,
            "writer_validation": receipt["validator"],
            "template_report": receipt["template_report"],
            "no_nan_inside_footprint": bool(fmt.get("no_nonfinite_inside", False) and fmt.get("nan_pixels", 1) == 0),
            "values_in_0_1": bool(fmt.get("inside_values_in_0_1", False)),
            "crs_shape_transform_match": bool(fmt.get("crs_shape_transform_match_mirror", False)),
            "all_finite_whole_array": bool(fmt.get("whole_array_strict_finite_0_1", False)),
            "positive_mass_outside_footprint": int(fmt.get("mass_outside_footprint", 0)),
        },
        "submission_name": SUBMISSION_NAME + "-zeros.tif",
        "submission_note": SUBMISSION_NOTE,
        "submission_note_chars": len(SUBMISSION_NOTE),
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "geological_experiments_run_this_session": 1,
        "verdict": (
            "promote-to-selector"
            if (literal_unique and fmt["ok"] and receipt["validator"].get("all_checks_passed"))
            else "negative"
        ),
        "verdict_reason": (
            "Unique vs the nine focus-site registry, format-valid, all-finite [0,1]. "
            "Holdout DTI reported honestly; live organizer score unknown (no submission made). "
            "Promotion to a weekly slot is the separate selector's decision."
        ),
        "blockers": [
            "No organizer-authenticated score (no live submission made; DrivenData is login-walled).",
            "Complete organizer registry not accessible; uniqueness is vs nine pinned focus-site rasters only.",
        ],
    }
    card_path = EVIDENCE / ("run_card_" + SUBMISSION_NAME + ".json")
    card_path.write_text(json.dumps(card, indent=2) + "\n")
    (ROOT / "docs" / "data" / "latest-run-card.json").write_text(json.dumps(card, indent=2) + "\n")
    print(f"\nRUN CARD -> {card_path.name}  VERDICT = {card['verdict'].upper()}")
    print(f"OK_TO_SUBMIT = {card['ok_to_submit']}  (live slot not selected/spent here)")
    print(f"elapsed={time.time()-t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
