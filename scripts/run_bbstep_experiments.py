#!/usr/bin/env python3
"""H-K1-BBSTEP three-experiment budget. Label-free surface; fold-local catalogue apron.

EXP1  leakage canary on each component (AUC > 0.90 is an alarm until proven
      label-free).
EXP2  buried basement-step surface + dotted emission vs GEMSDOE32 B2 control
      on the same hide-and-recover folds.
EXP3  slope-gate / budget sweep of the same lane (no new mechanism).

Does not spend a weekly submission slot.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT))

from gemsk import emission, grid, holdout, metric, submission  # noqa: E402
from gemskarage1.bbstep import LANE, build_components, combine, rank01  # noqa: E402

EVIDENCE = ROOT / "evidence"
DOCS_DL = ROOT / "docs" / "downloads"
REG = ROOT / ".cache" / "gems_data" / "registry"
EVALUATOR = holdout.VERSION  # gemsk-hide-recover-v1
SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")


def _dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n")


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _read_dots(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as src:
        a = src.read(1)
    return np.isfinite(a) & (a > 0) & foot


def uniqueness(dots: np.ndarray, surface: np.ndarray, foot: np.ndarray) -> dict:
    """Directed 3-px overlap and Spearman vs nine focus sites + lattice."""
    ny, nx = np.nonzero(dots & foot)
    fy, fx = np.nonzero(foot)
    rng = np.random.default_rng(20261028)
    sel = rng.choice(fy.size, size=min(400_000, fy.size), replace=False)
    sy, sx = fy[sel], fx[sel]
    rows = []
    for name in (*SITES, "lattice"):
        p = REG / f"{name}.tif"
        with rasterio.open(p) as src:
            ref = np.nan_to_num(src.read(1), nan=0.0).astype(np.float32)
        ref_dots = (ref > 0) & foot
        d = ndimage.distance_transform_edt(~ref_dots)
        overlap = float((d[ny, nx] <= 3).mean()) if ny.size else 0.0
        rho_dots = float(spearmanr(dots.astype(np.float32)[sy, sx], ref[sy, sx]).statistic)
        rho_surf = float(spearmanr(surface[sy, sx], ref[sy, sx]).statistic)
        if not np.isfinite(rho_dots):
            rho_dots = 0.0
        if not np.isfinite(rho_surf):
            rho_surf = 0.0
        rows.append({
            "id": name,
            "their_dots": int(ref_dots.sum()),
            "frac_our_dots_within_3px": overlap,
            "spearman_dots": rho_dots,
            "spearman_surface": rho_surf,
            "duplicate_by_overlap": overlap > 0.70,
            "duplicate_by_rho": max(abs(rho_dots), abs(rho_surf)) > 0.90,
        })
    focus = [r for r in rows if r["id"] != "lattice"]
    lattice = next(r for r in rows if r["id"] == "lattice")
    worst_focus = max(focus, key=lambda r: r["frac_our_dots_within_3px"])
    worst_rho = max(focus, key=lambda r: max(abs(r["spearman_dots"]), abs(r["spearman_surface"])))
    unique_vs_nine = (not any(r["duplicate_by_overlap"] or r["duplicate_by_rho"] for r in focus))
    return {
        "n_our_dots": int(ny.size),
        "rows": rows,
        "unique_vs_nine_focus_sites": unique_vs_nine,
        "worst_focus_overlap": worst_focus,
        "worst_focus_rho": {
            "id": worst_rho["id"],
            "abs_spearman": max(abs(worst_rho["spearman_dots"]), abs(worst_rho["spearman_surface"])),
        },
        "lattice_overlap": lattice["frac_our_dots_within_3px"],
        "lattice_duplicate_literal": lattice["duplicate_by_overlap"] or lattice["duplicate_by_rho"],
        "registry_complete": False,
        "registry_coverage": "Nine focus-site historic rasters plus the pinned 13GEMSDOE lattice. Not a complete fleet registry.",
    }


def score_arm(dots: np.ndarray, folds: list[dict]) -> tuple[dict, list[np.ndarray]]:
    terms = []
    n_withheld = 0
    for f in folds:
        _, t = holdout.evaluate_dots(dots, f)
        terms.append(t)
        n_withheld += int(f["n_withheld"])
    pooled = holdout.pooled(terms)
    return {**pooled, "withheld_positives": n_withheld, "evaluator_version": EVALUATOR}, terms


def emit_from(surface: np.ndarray, visible: np.ndarray, budget: int, spacing: float, apron: float) -> np.ndarray:
    """Peak-local-max candidates, then the shared Euclidean Poisson selector."""
    from skimage.feature import peak_local_max

    dcat = ndimage.distance_transform_edt(~visible)
    eligible = (surface > 0) & (dcat > apron)
    if not eligible.any():
        return np.zeros(surface.shape, bool)
    masked = np.where(eligible, surface, 0.0)
    min_d = max(1, int(np.floor(spacing)))
    coords = peak_local_max(
        masked, min_distance=min_d,
        threshold_abs=float(np.quantile(masked[eligible], 0.85)),
        num_peaks=max(budget * 3, 8000), exclude_border=False,
    )
    peaks = np.zeros_like(surface)
    if coords.size:
        peaks[coords[:, 0], coords[:, 1]] = masked[coords[:, 0], coords[:, 1]]
    dots = emission.poisson_select(peaks, budget, spacing, candidates=peaks > 0)
    return emission.apron_prune(dots, visible, apron_px=apron)


QUARANTINED_REASON = (
    "QUARANTINED: scripts/run_bbstep_experiments.py cannot run while "
    "registry/template.json has method_lane=null and canonical_template_assignment=null; "
    "its historical candidate overlaps 98.5253% within 3 px of the 13GEMSDOE lattice, "
    "uses private src/gemsk/holdout.py (which dilates visible faults by 3 px and "
    "compares against a static full-catalogue-pruned B2 mask), and would overwrite "
    "committed run-card receipts (docs/data/run-card.json and docs/data/latest-run-card.json)."
)


def main() -> int:
    print(QUARANTINED_REASON, file=sys.stderr)
    return 2


def _legacy_unquarantined_main() -> int:
    started = datetime.now(timezone.utc).isoformat()
    foot = grid.footprint()
    cat = grid.catalogue()
    print(f"grid footprint={int(foot.sum())} catalogue={int(cat.sum())}", flush=True)

    print("building label-free components", flush=True)
    comp = build_components(foot)
    folds_b = holdout.make_folds(cat, foot, scheme="blocked")
    n_withheld = sum(f["n_withheld"] for f in folds_b)
    print(f"blocked folds withheld positives={n_withheld}", flush=True)

    # ----- EXP1 leakage canary -----
    print("EXP1 leakage canary", flush=True)
    canary_feats = {
        "iso_grav_anom_hg": np.abs(comp["grav_hg"]),
        "grav_ridge": comp["grav_ridge"],
        "dtb_ridge": comp["dtb_ridge"],
        "align": comp["align"],
        "low_slope": comp["low_slope"],
        "mag_ridge": comp["mag_ridge"],
        "bbstep_surface_gate50": combine(comp, foot, slope_gate=0.50, use_magnetic=False),
    }
    canary_rows = []
    alarm = False
    rng = np.random.default_rng(20261028)
    for name, feat in canary_feats.items():
        aucs = [holdout.auc_on_fold(feat, f, rng=rng) for f in folds_b]
        mean_auc = float(np.mean(aucs))
        constant = float(np.nanstd(feat[foot])) == 0.0
        finite = bool(np.isfinite(feat[foot]).all())
        leak = (mean_auc > 0.90) or constant or (not finite)
        # Gravity/basement ridges are constructed without labels. An AUC > 0.90
        # would still be an alarm; we record the construction proof separately.
        canary_rows.append({
            "feature": name,
            "mean_auc": mean_auc,
            "fold_aucs": [float(a) for a in aucs],
            "constant": constant,
            "finite_in_footprint": finite,
            "reads_labels": False,
            "alarm": leak,
        })
        print(f"  {name:24s} AUC={mean_auc:.4f} alarm={leak}", flush=True)
        alarm = alarm or leak
    # Protocol: AUC>0.90 is leakage until proven otherwise. These features do
    # not read labels; an alarm still blocks promotion even if construction is
    # label-free, because a near-perfect rank of catalogue pixels usually means
    # the feature is a dressed-up distance-to-fault proxy.
    exp1 = {
        "experiment": 1,
        "lane": LANE,
        "evaluator_version": EVALUATOR,
        "withheld_positives": int(n_withheld),
        "rows": canary_rows,
        "any_alarm": alarm,
        "note": "Features are constructed without labels. AUC>0.90 still blocks promotion.",
    }
    _dump(EVIDENCE / "exp1_bbstep_canary.json", exp1)

    # ----- EXP2 primary holdout -----
    print("EXP2 primary BB-STEP holdout", flush=True)
    surface = canary_feats["bbstep_surface_gate50"]
    # Fold-local emission (visible-only apron) for holdout; full-catalogue apron for the saved raster.
    hold_terms = []
    n_emitted_folds = []
    for f in folds_b:
        d = emit_from(surface, f["visible"], budget=25000, spacing=2.8, apron=2.0)
        n_emitted_folds.append(int(d.sum()))
        _, t = holdout.evaluate_dots(d, f)
        hold_terms.append(t)
    bb_hold = holdout.pooled(hold_terms)
    print(f"  BB-STEP fold-local DTI={bb_hold['dti']:.6f} emitted/fold={n_emitted_folds}", flush=True)

    b2_path = REG / "GEMSDOE32.tif"
    b2_dots = _read_dots(b2_path, foot)
    b2_score, b2_terms = score_arm(b2_dots, folds_b)
    print(f"  B2 control DTI={b2_score['dti']:.6f} dots={int(b2_dots.sum())}", flush=True)

    ci = holdout.bootstrap_ci({"b2": b2_terms, "bbstep": hold_terms})
    exp2 = {
        "experiment": 2,
        "lane": LANE,
        "evaluator_version": EVALUATOR,
        "scheme": "blocked",
        "withheld_positives": int(n_withheld),
        "bbstep": {**bb_hold, "emitted_per_fold": n_emitted_folds,
                   "ci95": ci["bbstep"]["ci95"]},
        "b2_control": {**b2_score, "ci95": ci["b2"]["ci95"]},
        "paired_delta_vs_b2": ci["bbstep"].get("paired_delta_vs_b2"),
        "beats_b2_holdout": bool(bb_hold["dti"] > b2_score["dti"]
                                 and ci["bbstep"].get("paired_delta_vs_b2", {}).get("ci95", [0, 0])[0] > 0),
    }
    _dump(EVIDENCE / "exp2_bbstep_holdout.json", exp2)

    # ----- EXP3 slope-gate / budget sweep -----
    print("EXP3 slope-gate and budget sweep", flush=True)
    sweep = []
    best = None
    for gate, budget, spacing, mag in (
        (0.50, 18000, 2.8, False),
        (0.60, 18000, 2.8, False),
        (0.50, 25000, 3.2, False),
        (0.55, 22000, 2.8, True),
    ):
        surf = combine(comp, foot, slope_gate=gate, use_magnetic=mag)
        terms = []
        emitted = []
        for f in folds_b:
            d = emit_from(surf, f["visible"], budget=budget, spacing=spacing, apron=2.0)
            emitted.append(int(d.sum()))
            _, t = holdout.evaluate_dots(d, f)
            terms.append(t)
        pooled = holdout.pooled(terms)
        row = {
            "slope_gate": gate, "budget": budget, "spacing": spacing, "use_magnetic": mag,
            "dti": pooled["dti"], "tp": pooled["tp"], "fp": pooled["fp"], "fn": pooled["fn"],
            "emitted_per_fold": emitted,
        }
        sweep.append(row)
        print(f"  gate={gate} budget={budget} mag={mag} DTI={pooled['dti']:.6f}", flush=True)
        if best is None or pooled["dti"] > best["dti"]:
            best = {**row, "surface_key": (gate, mag)}
    # Cap at 3 experiments: the four rows are one sweep experiment, not four lanes.
    exp3 = {
        "experiment": 3,
        "lane": LANE,
        "evaluator_version": EVALUATOR,
        "withheld_positives": int(n_withheld),
        "sweep": sweep,
        "best": best,
    }
    _dump(EVIDENCE / "exp3_bbstep_sweep.json", exp3)

    # Final raster: full-catalogue apron, best holdout settings from EXP2/EXP3.
    gate, mag = best["surface_key"]
    final_surface = combine(comp, foot, slope_gate=gate, use_magnetic=mag)
    final_dots = emit_from(final_surface, cat, budget=int(best["budget"]),
                           spacing=float(best["spacing"]), apron=2.0)
    print(f"final dots={int(final_dots.sum())} gate={gate} mag={mag}", flush=True)

    uniq = uniqueness(final_dots, final_surface, foot)
    print(f"unique vs 9 sites={uniq['unique_vs_nine_focus_sites']} "
          f"lattice_overlap={uniq['lattice_overlap']:.4f}", flush=True)
    _dump(EVIDENCE / "bbstep_uniqueness.json", uniq)

    # Score the SAVED (full-catalogue-apron) dots on the same holdout for the run card.
    saved_score, saved_terms = score_arm(final_dots, folds_b)
    saved_ci = holdout.bootstrap_ci({"saved": saved_terms})["saved"]["ci95"]
    print(f"saved-raster HOLDOUT-DTI={saved_score['dti']:.6f} CI={saved_ci}", flush=True)

    slug = "karage1-bbstep-buried-basement-20261028T180000Z"
    note = "BB-STEP buried grav/dtb ridge; research only; DO NOT SUBMIT"
    assert len(note) <= 140
    rec = submission.write_bundle(final_dots, DOCS_DL, slug, note)
    zeros = rec["files"]["zeros"]
    print(f"wrote {slug}-zeros.tif sha={zeros['sha256'][:12]} dots={zeros['emitted_positive_pixels']}", flush=True)

    # Literal protocol: lattice overlap > 70% => duplicate, stop, do not promote.
    lattice_block = bool(uniq["lattice_duplicate_literal"])
    nine_ok = bool(uniq["unique_vs_nine_focus_sites"])
    format_ok = bool(zeros["all_checks_passed"])
    canary_ok = not alarm
    beats = bool(saved_score["dti"] > b2_score["dti"])
    verdict = "negative"
    if canary_ok and format_ok and nine_ok and beats and not lattice_block:
        verdict = "promote"  # to selector only; still not a spent slot
    ok_to_submit = False  # selector step is separate; weekly cap unknown

    card = {
        "schema": "karage1-run-card-v3",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "session": "arena/9d2bc03d-gemsdoekarage1",
        "started_utc": started,
        "hypothesis": (
            "Buried intra-basin normal faults produce aligned isostatic-gravity and "
            "depth-to-basement gradient ridges where topographic slope is low."
        ),
        "mechanism": (
            "Multiscale NMS ridges of iso_grav_anom and depth_to_base_surf, sign-invariant "
            "gradient alignment, low-slope veto, 2 px catalogue apron, Poisson 300 m packing."
        ),
        "named_non_fault_mimic": (
            "Lithologic contacts, volcanic-flow density edges, and basin-fill compaction steps."
        ),
        "lane": LANE,
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "value": saved_score["dti"],
            "evaluator_version": EVALUATOR,
            "withheld_positives": int(n_withheld),
            "ci95": saved_ci,
            "status": "Measured this session on blocked whole-segment hide-and-recover.",
        },
        "b2_control_holdout_dti": {
            "label": "HOLDOUT-DTI",
            "value": b2_score["dti"],
            "evaluator_version": EVALUATOR,
            "withheld_positives": int(n_withheld),
            "ci95": ci["b2"]["ci95"],
            "file": "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
            "owner_report_organizer_score": "0.2778 USER-REPORTED / UNVERIFIED",
        },
        "correlation_overlap_vs_registry": {
            "preplacement_surface_spearman_worst_nine": uniq["worst_focus_rho"],
            "final_dot_overlap_worst_nine": uniq["worst_focus_overlap"],
            "unique_vs_nine_focus_sites": nine_ok,
            "lattice_overlap": uniq["lattice_overlap"],
            "lattice_duplicate_literal": lattice_block,
            "registry_coverage": uniq["registry_coverage"],
            "registry_complete": False,
        },
        "raster_sha256": zeros["sha256"],
        "raster_status": "Generated this session from label-free BB-STEP surface.",
        "validator_output": {
            "no_nan_inside_footprint": zeros["checks"]["in_footprint_all_finite"],
            "values_in_0_1": zeros["checks"]["in_footprint_range_0_1"],
            "crs_shape_transform_match": zeros["checks"]["crs_matches_template"]
            and zeros["checks"]["shape_matches_template"]
            and zeros["checks"]["transform_matches_template"],
            "all_finite_whole_array": zeros["whole_array_finite"],
            "outside_null_or_nan": rec["files"]["nan"]["checks"]["outside_footprint_zero_or_nan"],
            "all_checks_passed_zeros": format_ok,
            "reference": "Hash-pinned owner mirror of sample_submission.tif; organizer authenticity not established.",
            "portal_acceptance": "not tested",
        },
        "submission_name": f"{slug}-zeros.tif",
        "submission_note": note,
        "download_available": True,
        "download_available_meaning": (
            "Research download of a newly generated GeoTIFF. Not authorization to upload. "
            "OK-TO-SUBMIT is false."
        ),
        "ok_to_submit": ok_to_submit,
        "slot_selected_or_spent": False,
        "geological_experiments_run_this_session": 3,
        "exp1_canary_alarm": alarm,
        "beats_b2_on_holdout": beats,
        "blockers": [b for b in [
            "Literal lattice overlap exceeds 70%; protocol says log duplicate and stop." if lattice_block else "",
            "Leakage-canary alarm on at least one feature." if alarm else "",
            "Duplicate vs a nine-site historic raster." if not nine_ok else "",
            "HOLDOUT-DTI does not beat B2 control on the same evaluator." if not beats else "",
            "Weekly-slot selector has not run; ok_to_submit remains false.",
            "Registry is not complete; uniqueness vs the full fleet is unproven.",
            "Mirrored sample is not organizer-authenticated.",
        ] if b],
        "verdict": verdict,
        "audit": "evidence/bbstep_uniqueness.json",
    }
    _dump(EVIDENCE / "run_card.json", card)
    _dump(EVIDENCE / "current_run_card.json", card)
    _dump(ROOT / "docs" / "data" / "run-card.json", card)
    _dump(ROOT / "docs" / "data" / "latest-run-card.json", card)
    _dump(EVIDENCE / "bbstep_receipt.json", rec)
    _dump(EVIDENCE / "experiments_summary.json", {
        "lane": LANE,
        "n_experiments": 3,
        "exp1": "evidence/exp1_bbstep_canary.json",
        "exp2": "evidence/exp2_bbstep_holdout.json",
        "exp3": "evidence/exp3_bbstep_sweep.json",
        "uniqueness": "evidence/bbstep_uniqueness.json",
        "verdict": verdict,
        "ok_to_submit": ok_to_submit,
    })
    print(json.dumps({"verdict": verdict, "ok_to_submit": ok_to_submit,
                      "holdout_dti": saved_score["dti"], "lattice_overlap": uniq["lattice_overlap"],
                      "unique_vs_nine": nine_ok, "file": f"{slug}-zeros.tif"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
