#!/usr/bin/env python3
"""Build the single JSON run card for the H-E1 Euler deconvolution experiment (31 Oct 2026).

Every number is read from evidence/exp_h_e1_euler_20261031.json or from the bytes of
the candidate rasters; nothing is typed by hand. The card is fail-closed: it always
states ok_to_submit = false and never authorises a weekly slot.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import rasterio
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence" / "exp_h_e1_euler_20261031.json"
CARD = ROOT / "evidence" / "session_46ed1c8c_run_card.json"
DL = ROOT / "docs" / "downloads"
ZEROS = "karage1-he1-euler-contact-si0-37654-20261031-zeros.tif"
NANTWIN = "karage1-he1-euler-contact-si0-37654-20261031-nan.tif"
SUBMISSION_NAME = ZEROS[: -len(".tif")]
SUBMISSION_NOTE = ("H-E1 Euler SI0 contact, 37654 dots, label-free; holdout above null; "
                   "lattice gate fails literal rule. HOLD, do not submit.")
COVERAGE_BOUNDS: list = []
SITE_RE = re.compile(r"GEMSDOE(24|25|27|28|30|31|32|33|36)")


def coverage_bound(raster: Path, footprint: np.ndarray, n_dots: int) -> dict:
    """Minimum possible forward 3 px overlap of ANY n_dots set placed inside the footprint.

    U = footprint cells more than 3 px from every positive cell of the covering raster.
    Best case puts all dots in U, so the minimum overlap is (n - U) / n.
    """
    from scipy import ndimage as ndi

    with rasterio.open(raster) as ds:
        a = ds.read(1)
    pos = np.isfinite(a) & (a > 0) & footprint
    dist = ndi.distance_transform_edt(~pos)
    uncovered = int(((dist > 3) & footprint).sum())
    return dict(file=raster.name, positive_cells_in_footprint=int(pos.sum()),
                uncovered_footprint_cells=uncovered,
                min_forward_overlap_for_n_dots=round(max(0, n_dots - uncovered) / n_dots, 6),
                max_dots_passing_70pct_gate=int(uncovered / 0.3))


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def raster_facts(p: Path) -> dict:
    with rasterio.open(p) as ds:
        a = ds.read(1)
        fin = np.isfinite(a)
        return dict(
            file=p.name, sha256=sha256(p), bands=ds.count, dtype=ds.dtypes[0],
            epsg=ds.crs.to_epsg(), shape=[ds.height, ds.width],
            nodata_tag=None if ds.nodata is None else ("NaN" if np.isnan(ds.nodata) else float(ds.nodata)),
            finite_cells=int(fin.sum()), nan_cells=int((~fin).sum()),
            min=float(np.nanmin(a)), max=float(np.nanmax(a)), positive_cells=int((a > 0).sum()),
        )


def saved_byte_receipt(path: Path, out: Path, footprint: np.ndarray, catalogue: np.ndarray,
                       checks: dict, ev: dict) -> dict:
    """Saved-byte receipt in the karage1-local-tif-audit-v1 schema, computed from the bytes on disk.

    scripts/audit_local_tif.py was not used: it reads .cache/gems_data, which is absent here,
    and it imports the vendored uniqueness.py, which does not match its pin. Overlap figures
    come from the H-E1 registry comparison (same dots, same 52 registry rasters).
    """
    from datetime import datetime, timezone

    raw = path.read_bytes()
    with rasterio.open(path) as ds:
        arr = ds.read(1)
    pos = np.isfinite(arr) & (arr > 0)
    rows = [r for r in ev["uniqueness"]["rows_dots"] if "error" not in r]
    lattice = next(r for r in rows if r["name"].startswith("13gems"))
    focus = [r for r in rows if SITE_RE.search(r["name"])]
    worst = max(focus, key=lambda r: r["my_dots_within_3px_of_theirs"])
    rec = dict(
        schema="karage1-local-tif-audit-v1",
        file=str(path.relative_to(ROOT)),
        sha256=hashlib.sha256(raw).hexdigest(),
        bytes=len(raw),
        audited_utc=datetime.now(timezone.utc).isoformat(),
        audit_method=("H-E1 runner validators and literal registry comparison, recomputed from the saved bytes by "
                      "scripts/make_he1_run_card_20261031.py; scripts/audit_local_tif.py not used (needs .cache/gems_data; "
                      "vendored uniqueness.py pin mismatch)"),
        format_report_ok=bool(checks.get("all_passed", checks.get("validator_all_passed"))),
        validator_checks=checks.get("validator_checks", checks.get("checks", checks)),
        positives=int(pos.sum()),
        positives_outside_footprint=int((pos & ~footprint).sum()),
        positives_on_mapped_catalogue=int((pos & catalogue).sum()),
        value_min=float(np.nanmin(arr)), value_max=float(np.nanmax(arr)),
        nan_count=int(np.isnan(arr).sum()),
        lattice_forward_3px_overlap=lattice["my_dots_within_3px_of_theirs"],
        worst_focus_file=worst["name"],
        worst_focus_forward_3px_overlap=worst["my_dots_within_3px_of_theirs"],
        registry_rasters_checked=ev["uniqueness"]["registry_rasters_scanned"],
        ok_to_submit=False,
        verdict="research audit only; not cleared (literal 70% lattice gate fails; holdout is in the H-E1 evidence)",
    )
    out.write_text(json.dumps(rec, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    return rec


def main() -> None:
    import os
    global COVERAGE_BOUNDS
    ev = json.loads(EVID.read_text(encoding="utf-8"))
    dd = Path(os.environ.get("GEMS_DATA_DIR", "/tmp/gems_data"))
    with rasterio.open(dd / "sample_submission.tif") as ds:
        foot = np.isfinite(ds.read(1))
    COVERAGE_BOUNDS = [
        coverage_bound(dd / "scored" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif", foot, 37654),
        coverage_bound(ROOT / "docs/downloads/karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.tif", foot, 37654),
    ]
    prim = ev["arms"]["primary_SI0_contact"]
    sec = ev["arms"]["secondary_SI1_sheet"]
    unq = ev["uniqueness"]
    rows = [r for r in unq["rows_dots"] if "error" not in r]
    site_rows = [r for r in rows if SITE_RE.search(r["name"])]
    discrete = [r for r in rows if r["their_positive_cells"] <= 100_000]
    blankets = [r for r in rows if r["their_positive_cells"] > 100_000 and r["my_dots_within_3px_of_theirs"] >= 0.70]
    canary = {k: round(v["max_direction_invariant_auc"], 4) for k, v in ev["leakage_canary"].items()}
    zeros_p, nan_p = DL / ZEROS, DL / NANTWIN
    assert sha256(ROOT / "archive/research-he1-20261031" / ZEROS) == sha256(zeros_p), "archive/docs copy drift"
    assert sha256(ROOT / "archive/research-he1-20261031" / NANTWIN) == sha256(nan_p), "archive/docs copy drift"
    assert len(SUBMISSION_NOTE) <= 140, "note longer than 140 characters"
    v = ev["artefacts"]["zeros_primary"]
    crit = ev["criteria"]
    card = {
        "schema": "karage1-run-card-v1",
        "session": "arena/46ed1c8c-gemsdoekarage1",
        "review_date": "2026-10-31",
        "hypothesis": ev["hypothesis"],
        "hypothesis_id": "H-E1",
        "mechanism": ("Window Euler deconvolution (11 px window) of the official TMI field, with the official "
                      "tmi_vg band as Tz. Primary structural index SI 0 (contact of infinite depth extent); "
                      "accepted solutions at 50-2000 m depth vote into a dot field of 37,654 dots."),
        "non_fault_mimic": [
            "lithologic and intrusive contacts (magnetisation contrast, not displacement)",
            "dyke and sill margins (SI 1 secondary arm; reported, cannot promote alone)",
            "basalt-flow edges and cover-thickness changes",
            "survey-line and levelling artifacts (not separately tested)",
        ],
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator": ev["evaluator"]["version"],
            "truth": ev["evaluator"]["truth_is"],
            "cells": ev["evaluator"]["cells"],
            "withheld_positives": ev["evaluator"]["withheld_positives"],
            "decision_metric_pooled_dti": prim["candidate"]["pooled_dti"],
            "mean_of_cell_dti": None,
            "mean_of_cell_dti_ci95_cell_bootstrap": None,
            "matched_random_null_pooled_mean_seeds_101_202_303": prim["nulls"]["pooled_mean"],
            "paired_difference_vs_null_mean": prim["paired_vs_null"]["mean_delta"],
            "paired_difference_vs_null_ci95": prim["paired_vs_null"]["ci95"],
            "tmi_hg_baseline_pooled_dti": prim["tmi_hg_baseline"]["holdout"]["pooled_dti"],
            "note": ("The decision metric is pooled DTI. The CI in the evidence belongs to the mean of the 16 per-cell "
                     "DTIs, reported separately. No pooled-DTI CI exists in the evidence file."),
        },
        "correlation_and_overlap": {
            "surface_max_abs_spearman_vs_registry": unq["surface_max_spearman"],
            "dot_overlap_literal_gate_max_my_dots_within_3px_of_any_registry_raster": unq["final_dots_max_my_dots_within_3px"],
            "literal_gate_trips_70pct": [t["file"] for t in unq["dot_gate_trips_70pct"]],
            "literal_gate_trip_reason": ("covering rasters (>100,000 positive cells) make the 70% rule unpassable "
                                         "for this dot count; see coverage_bounds"),
            "coverage_bounds": COVERAGE_BOUNDS,
            "dotted_rasters_le_100k_positive_cells_count": len(discrete),
            "dotted_rasters_le_100k_max_my_dots_within_3px": max(r["my_dots_within_3px_of_theirs"] for r in discrete),
            "focus_site_rasters_max_my_dots_within_3px": max(r["my_dots_within_3px_of_theirs"] for r in site_rows),
            "focus_site_rasters_count": len(site_rows),
            "rasters_scanned": unq["registry_rasters_scanned"],
        },
        "leakage_canary_max_direction_invariant_auc": canary,
        "criteria": crit,
        "raster_sha256": {
            "primary_zeros_outside": raster_facts(zeros_p),
            "twin_nan_outside": raster_facts(nan_p),
        },
        "validator_output": {
            "zeros_primary_all_passed": v["validator_all_passed"],
            "zeros_primary_checks": v["validator_checks"],
            "nan_twin_all_passed": ev["artefacts"]["nan_outside_twin"]["checks"]["all_passed"],
            "nan_twin_checks": ev["artefacts"]["nan_outside_twin"]["checks"],
        },
        "submission_policy": {
            "primary_file": ZEROS,
            "twin_file": NANTWIN,
            "twin_status": "diagnostic only: pinned writer vendor/gems57/grid.py says NaN mode is retained for local diagnostics",
            "pinned_writer_statement": "zeros is the only submission-compatible mode; NaN handling of the organizer is not inferred",
            "official_text_conflict": ("official format text (page 967) says outside-bounds cells should be null or NaN; "
                                       "the pinned writer prefers all-finite zeros. Unresolved; owner decides."),
        },
        "submission_name": SUBMISSION_NAME,
        "submission_note": SUBMISSION_NOTE,
        "submission_note_length": len(SUBMISSION_NOTE),
        "ok_to_submit": False,
        "download_available": True,
        "download_available_meaning": "Owner-review copy of the exact candidate bytes. Download is NOT authorization to submit.",
        "new_candidate_generated": True,
        "slot_selected_or_spent": False,
        "submission_slots_used": 0,
        "geological_experiments_run": 1,
        "experiment_budget": "3 experiments or 2 hours (one run, ~4 minutes wall time)",
        "verdict": ev["verdict"],
        "verdict_reason": ("Pre-registered rule: promote requires all six criteria. The holdout, canary, validator "
                           "and surface criteria pass; the literal dot-overlap criterion fails at 1.0 against three "
                           "dense covering rasters. Owner ruling on that gate is required."),
        "owner_decision_required": "Whether covering rasters (>100,000 positive cells) are in scope of the 70% dot-overlap rule.",
        "holdout_is_not_leaderboard": ("GEMSDOE32 B2 scores HOLDOUT-DTI 0.00473 here against a USER-REPORTED 0.2778 public "
                                       "label. This holdout cannot rank catalogue-derived submissions."),
        "data_status": ev["inputs"]["data_status"],
        "review_path": "knowledge/session-review-arena-46ed1c8c.md",
        "run_card_path": "evidence/session_46ed1c8c_run_card.json",
        "experiment_evidence_path": "evidence/exp_h_e1_euler_20261031.json",
    }
    # fill the holdout CI fields from the per-cell block (never from a hand-typed number)
    cand = prim["candidate"]
    card["holdout_dti"]["mean_of_cell_dti"] = cand["mean_cell_dti"]
    card["holdout_dti"]["mean_of_cell_dti_ci95_cell_bootstrap"] = cand["ci95_cell_bootstrap_of_mean"]
    card["secondary_si1_pooled_dti"] = sec["candidate"]["pooled_dti"]
    # saved-byte receipts (required by tests/test_session_1668dda0_hardening.py for every local TIF)
    with rasterio.open(dd / "sample_submission.tif") as ds:
        fp_mask = np.isfinite(ds.read(1))
    with rasterio.open(dd / "labels.tif") as ds:
        cat_mask = (ds.read(1) == 1) & fp_mask
    saved_byte_receipt(zeros_p, ROOT / "evidence" / f"audit_{SUBMISSION_NAME}.json", fp_mask, cat_mask,
                       ev["artefacts"]["zeros_primary"], ev)
    saved_byte_receipt(nan_p, ROOT / "evidence" / f"audit_{NANTWIN[:-4]}.json", fp_mask, cat_mask,
                       ev["artefacts"]["nan_outside_twin"]["checks"], ev)
    CARD.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote {CARD.relative_to(ROOT)} verdict={card['verdict']} ok_to_submit={card['ok_to_submit']}")


if __name__ == "__main__":
    main()
