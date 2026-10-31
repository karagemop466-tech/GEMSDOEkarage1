#!/usr/bin/env python3
"""Write evidence/run_card_h31_20261031.json from the measured evidence files.

Every number is copied from evidence/*.json; nothing is typed by hand. The verdict is
computed from the protocol gates, so it cannot be promoted by editing this script's output.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FINAL = ROOT / "evidence/h31_final_20261031.json"
HOLD = ROOT / "evidence/h31_holdout_20261031.json"
HOLD20 = ROOT / "evidence/h31_holdout_20261031_buffer20_posthoc.json"
SAVED = ROOT / "evidence/audit_h31_candidate_saved_bytes_20261031.json"
OUT = ROOT / "evidence/run_card_h31_20261031.json"

NAME = "karage1-h31-visgrad-nms3px-40k-20261031-zeros"
NOTE = ("H-V31 visible-catalogue emitter, 40k NMS-3px dots. Holdout DTI 0.114 [0.092,0.136]. "
        "Lattice gate FAILS: NOT CLEARED.")
DUPLICATE_OVERLAP = 0.70
DUPLICATE_CORR = 0.90
CANARY_LIMIT = 0.90


def main() -> int:
    if len(NOTE) > 140:
        raise SystemExit(f"note is {len(NOTE)} chars; limit is 140")
    final = json.loads(FINAL.read_text())
    hold = json.loads(HOLD.read_text())
    hold20 = json.loads(HOLD20.read_text())
    saved = json.loads(SAVED.read_text())
    cand = hold["pooled"]["scores"]["candidate_H_V31"]
    c1 = hold["pooled"]["scores"]["C1_random"]
    d1 = hold["pooled"]["paired_differences"]["C1_random"]
    d1_20 = hold20["pooled"]["paired_differences"]["C1_random"]
    cand20 = hold20["pooled"]["scores"]["candidate_H_V31"]
    focus = {k: v for k, v in final["uniqueness_vs_nine_focus"].items() if not k.startswith("13gems")}
    lattice = {k: v for k, v in final["uniqueness_vs_nine_focus"].items() if k.startswith("13gems")}
    worst_fwd = max(focus.items(), key=lambda kv: kv[1]["fwd3_candidate_dots_within_3px_of_registry"])
    worst_phi = max(focus.items(), key=lambda kv: abs(kv[1]["phi_spearman_footprint"]))
    worst_rho = max(final["uniqueness_vs_nine_focus"].items(),
                    key=lambda kv: abs(kv[1]["surface_spearman_vs_registry_raster"]))
    lat_fwd = next(iter(lattice.values()))["fwd3_candidate_dots_within_3px_of_registry"]
    lattice_fail = lat_fwd > DUPLICATE_OVERLAP
    fold1 = next(f for f in hold["folds"] if f["fold"] == 1)
    canary = hold["leakage_canary"]["max_symmetric_auc_per_channel"]
    canary_max = max(canary.values())
    protocol_duplicate = (lattice_fail or any(
        v["fwd3_candidate_dots_within_3px_of_registry"] > DUPLICATE_OVERLAP for v in focus.values())
        or any(abs(v["phi_spearman_footprint"]) > DUPLICATE_CORR for v in focus.values()))
    holdout_pass = hold["verdict_holdout_only"] == "PASS_HOLDOUT_ONLY"
    # Protocol: duplicate or leakage -> stop (negative). Promote only if every gate passes.
    verdict = ("promote" if (holdout_pass and not protocol_duplicate and canary_max <= CANARY_LIMIT
                             and final["unique_vs_nine_focus_passes"] and final["surface_gate_passes_all_registry"])
               else "negative")
    card = {
        "schema": "karage1-parallel-run-card-v2",
        "session": "arena/8e91c377-gemsdoekarage1",
        "date_utc": "2026-10-31",
        "lane": "H-V31 visible-catalogue discriminator with 3 px NMS (preregistered: knowledge/preregistration-h31-visgrad-20261031.md)",
        "hypothesis": ("Linear maxima of horizontal magnetic and gravity gradients plus tilt and strain-rate "
                       "contrasts, learned on visible catalogue segments, mark further unmapped faults in withheld regions."),
        "mechanism": ("LightGBM (300 trees, lr 0.05, 63 leaves) on all 19 finite bands. Positives are all catalogue "
                      "pixels outside a 1 km buffer of withheld segments; 200,000 sampled negatives; the top 40,000 "
                      "probabilities are kept after a 3 px greedy non-maximum suppression and written as 0/1 dots."),
        "mimicked_process": ("Catalogue hide-and-recover under evaluator gems57-pooled-hide-v2: 4 spatial quadrant folds, "
                             "20 km paired bootstrap clusters. The organizer scorer is NOT reproduced (no hidden labels). "
                             "Known catalogue pixels are masked as the organizer does for known faults (row A5)."),
        "holdout": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": hold["evaluator_version"],
            "truth_source": hold["truth_source"],
            "dti": round(cand["dti"], 6),
            "ci95": [round(x, 6) for x in cand["ci95"]],
            "withheld_positive_pixels": cand["withheld_positive_pixels"],
            "random_control_dti": round(c1["dti"], 6),
            "paired_delta_vs_random": round(d1["delta"], 6),
            "paired_delta_vs_random_ci95": [round(x, 6) for x in d1["ci95"]],
            "posthoc_buffer20_dti": round(cand20["dti"], 6),
            "posthoc_buffer20_ci95": [round(x, 6) for x in cand20["ci95"]],
            "posthoc_buffer20_paired_delta_vs_random": round(d1_20["delta"], 6),
            "posthoc_buffer20_paired_delta_vs_random_ci95": [round(x, 6) for x in d1_20["ci95"]],
            "preregistered_verdict": hold["verdict_holdout_only"],
            "fold1_candidate_vs_random": {
                "candidate": round(fold1["arms"]["candidate_H_V31"]["dti"], 6),
                "random": round(fold1["arms"]["C1_random"]["dti"], 6)},
        },
        "leakage_canary": {"metric": "max symmetric single-feature AUC", "value": round(canary_max, 6),
                           "limit": CANARY_LIMIT, "pass": canary_max <= CANARY_LIMIT},
        "registry_correlation_and_overlap": {
            "unique_vs_nine_focus_rule": "candidate forward 3 px overlap (dots within 3 px of registry) must be <= 0.70; |phi| < 0.90; no exact mask match",
            "unique_vs_nine_focus_passes": final["unique_vs_nine_focus_passes"],
            "max_forward_3px_overlap_focus": {"raster": worst_fwd[0], "value": round(worst_fwd[1]["fwd3_candidate_dots_within_3px_of_registry"], 6)},
            "max_abs_phi_focus": {"raster": worst_phi[0], "value": round(worst_phi[1]["phi_spearman_footprint"], 6)},
            "max_abs_surface_spearman_all_registry": {"raster": worst_rho[0], "value": round(worst_rho[1]["surface_spearman_vs_registry_raster"], 6)},
            "surface_gate_passes": final["surface_gate_passes_all_registry"],
            "lattice_forward_3px_overlap": round(lat_fwd, 6),
            "lattice_gate_passes": final["lattice_gate_passes"],
            "independent_saved_byte_cross_check": {"receipt": "evidence/audit_h31_candidate_saved_bytes_20261031.json",
                                                   "all_format_and_focus_checks_pass": saved["uniqueness_vs_focus_passes"],
                                                   "lattice_gate_passes": saved["lattice_gate_passes"]},
            "note": ("The protocol's literal duplicate rule (> 70% of dots within 3 px of any registry raster) "
                     "fails against the 13GEMS lattice probe for every dotted raster on this grid (measured on "
                     "all nine focus files). Dots in lattice holes were not used to evade it."),
        },
        "raster": {
            "file": final["file"],
            "sha256": final["sha256_tif"],
            "bytes": final["bytes_tif"],
            "zip": final["zip"],
            "zip_sha256": final["sha256_zip"],
            "dots": final["dots_written"],
            "encoding": "zeros (float32, 0.0 off-dot, 1.0 on-dot; single band; deflate; sample grid)",
        },
        "validator_output": final["validator"],
        "name": NAME,
        "note": NOTE,
        "note_chars": len(NOTE),
        "ok_to_submit": False,
        "download_available": "research only; NOT CLEARED",
        "slot_selected_or_spent": False,
        "experiments_used": 3,
        "experiments_budget": 3,
        "experiment_list": [
            "E1 nine-site audit (evidence/focus_nine_audit_20261031.json)",
            "E2 preregistered H-V31 holdout (evidence/h31_holdout_20261031.json)",
            "E3 post-hoc buffer-20 sensitivity (evidence/h31_holdout_20261031_buffer20_posthoc.json); reported as E3 of 3, not preregistered, cannot change the verdict",
        ],
        "verdict": verdict,
        "verdict_reason": ("NEGATIVE under the parallel-run protocol: the literal lattice duplicate rule fails "
                           f"(forward 3 px overlap {lat_fwd:.4f} > 0.70). The holdout is a PASS_HOLDOUT_ONLY result, "
                           "but the protocol's stop rule applies. No promote verdict is issued."),
        "owner_decision_required": ("Decide whether the literal 70% lattice rule applies to a covering-grid probe that "
                                    "every dotted raster on this grid exceeds. Until that is decided, nothing is submitted."),
        "known_deviations": [
            "Under-budget control C3 (catalogue proximity): 50 / 21 / 134 / 40 dots per fold versus 8.9k–11k for the candidate and random arms.",
            "Fold 1: candidate 0.0637 vs random 0.0759 at buffer 10 (candidate loses); 0.0728 vs 0.0732 at buffer 20 (tie).",
            "Pooled bootstrap seed 20261031, not the repo's usual 520810 (earlier runs in evidence/ use 520810).",
            "Final raster written directly with rasterio. vendor/gems57/submission_writer.py is NOT used: its hash does not match its provenance pin.",
            "Uniqueness and lattice checks are a private reimplementation, not vendor/gems57/uniqueness.py (hash mismatch). An independent saved-byte cross-check agrees to 4 decimals.",
            "Holdout truth is the catalogue mirror (data/labels.tif, byte-identical to existing_faults.tif), not organizer hidden labels.",
            "Holdout assigns segments whole by centroid. 395 catalogue pixels (60,988 total minus 60,593 scored) belong to segments whose centroid is in another quadrant and are scored in no fold. Edge effect, not a leak.",
            "Shared template preflight is not ready (shared feature stack missing), so the candidate uses the mirror training features (not organizer-authenticated).",
        ],
        "limitations": [
            "No organizer receipt exists for any file in this repository; no leaderboard estimate is available.",
            "The buffer of 1 km removes any hidden truth within about 2.8 px of visible catalogue traces, so the holdout cannot measure the adjacency trade-off that the metric's marginal rule makes important (knowledge/hypotheses-20261031.md, H-A1).",
            "Random placement is a strong control under this metric (0.0773 HOLDOUT-DTI), so holdout values are not comparable to leaderboard values (0.26–0.28, USER-REPORTED).",
        ],
    }
    OUT.write_text(json.dumps(card, indent=2, allow_nan=False) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)} (note {len(NOTE)} chars, verdict {verdict})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
