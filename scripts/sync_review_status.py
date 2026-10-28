#!/usr/bin/env python3
"""Apply the independently measured 2026-10-28 negative witness to release metadata.

Prior numerical measurements remain intact and are explicitly marked historical;
this script does not fabricate a new experiment or grant a submission slot.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text())


def save(path, value):
    (ROOT / path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def main():
    from scripts.release_gate import assess
    audit = load("evidence/release_reassessment_20261028.json")
    if audit["schema"] != "karage1-literal-release-reassessment-v1":
        raise ValueError("unrecognized reassessment")
    h, g = audit["candidates"]["hmas"], audit["candidates"]["gpcz"]
    if not h["literal_duplicate"] or not g["literal_duplicate"]:
        raise ValueError("expected independent duplicate witnesses")
    old = load("evidence/run_card_hmas_sinter.json")
    old.setdefault("previously_reported_verdict", old["verdict"])
    old["verdict"] = "negative"
    old["status_update"] = "Superseded 2026-10-28 by independent literal-overlap witness; historical holdout not replayed."
    old["registry_correlation_overlap"]["passed"] = False
    old["registry_correlation_overlap"]["literal_witness"] = {
        "source_sha256": audit["provenance"]["lattice_sha256"],
        "candidate_dots_within_3px": h["lattice_dots_within_3px_count"],
        "candidate_dots": h["dots_in_footprint"],
        "directed_overlap": h["lattice_directed_overlap"],
    }
    save("evidence/run_card_hmas_sinter.json", old)

    for key, path in (("hmas", "evidence/release_gate_hmas_sinter.json"),
                      ("gpcz", "evidence/release_gate_gpcz.json")):
        obj = load(path)
        obj.setdefault("original_result", obj["result"])
        c = audit["candidates"][key]
        obj["input"]["registry"].update({
            "complete": False, "literal_all_rasters": False,
            "surface_checked_before_placement": False,
            "excluded_registry_rasters": ["13GEMSDOE r13-lattice-s5"],
            "duplicate_witnesses": [{"sha256": audit["provenance"]["lattice_sha256"],
                                     "directed_overlap": c["lattice_directed_overlap"]}],
            "max_directed_overlap_3px": None,
        })
        obj["result"] = assess(obj["input"])
        obj["reassessment"] = "evidence/release_reassessment_20261028.json"
        save(path, obj)

    uniqueness = load("evidence/fleet_uniqueness_593.json")
    uniqueness.setdefault("previously_reported_nonliteral_pass", uniqueness["passed"])
    uniqueness["passed"] = False
    uniqueness["superseded_by"] = "evidence/release_reassessment_20261028.json"
    uniqueness["reassessment_note"] = "Previous discrete-only maximum excluded a registered lattice; it does not implement the literal gate."
    uniqueness["literal_lattice_overlap"] = h["lattice_directed_overlap"]
    save("evidence/fleet_uniqueness_593.json", uniqueness)

    ledger = load("evidence/experiments_summary.json")
    ledger.setdefault("previously_reported_verdict", ledger["verdict"])
    ledger["verdict"] = "negative"
    ledger["gates"]["uniqueness_gate_passed"] = False
    ledger["gates"]["leakage_canary_passed"] = False
    ledger["superseded_by"] = "evidence/release_reassessment_20261028.json"
    save("evidence/experiments_summary.json", ledger)

    canary_path = "evidence/leakage_canary_58ch.json"
    canary = load(canary_path)
    canary.setdefault("previously_reported_all_passed", canary["all_passed"])
    canary["all_passed"] = False
    canary["reassessment_note"] = ("Not independently replayed; the historical implementation assigned AUC 0.5 to constant features "
                                   "without recording variation, and used a split that does not establish the requested buffered holdout.")
    save(canary_path, canary)

    rec_path = "docs/downloads/karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.json"
    rec = load(rec_path)
    rec.update(promoted=False, approved_for_weekly_slot=False, uniqueness_gate_passed=False,
               verdict="negative", submission_slots_used=None,
               status="DO NOT SUBMIT: independently measured literal registry duplicate; format checks are not slot approval.",
               reassessment="evidence/release_reassessment_20261028.json")
    save(rec_path, rec)

    for path in ("evidence/run_card_gpcz.json", "docs/data/latest-run-card.json"):
        obj = load(path)
        obj.setdefault("previously_reported_verdict", obj["verdict"])
        obj.update(verdict="negative", verdict_reason="Literal lattice overlap exceeds 70%; stop. The prior non-probe clearance is superseded.",
                   reassessment="evidence/release_reassessment_20261028.json")
        if isinstance(obj.get("uniqueness"), dict):
            obj["uniqueness"]["unique"] = False
            obj["uniqueness"]["literal_lattice_overlap"] = g["lattice_directed_overlap"]
        save(path, obj)
    gpcz = load("docs/data/run-card-gpcz.json")
    gpcz.update(verdict="negative", ok_to_submit=False,
                ok_to_submit_meaning="DO NOT SUBMIT: literal lattice witness exceeds the 70% threshold.",
                reassessment="evidence/release_reassessment_20261028.json")
    overlap = gpcz["correlation_overlap_vs_registry"]
    overlap.setdefault("previous_nonprobe_final_dot_overlap", overlap["final_dot_overlap"])
    overlap["final_dot_overlap"] = g["lattice_directed_overlap"]
    overlap["registry_coverage"] = "Historical 15-raster scan excluded lattice from clearance; the literal lattice witness now fails. Not a complete scan."
    gpcz["holdout_dti"]["status"] = "Historical HOLDOUT-DTI on catalogue truth; not independently replayed in this review and not a leaderboard estimate."
    gpcz["blockers"] = [
        "Literal lattice overlap 35,959 / 36,000 exceeds 70%; no exemption.",
        "IR-K1-SGMC-01: historical off-catalogue calibration favored the champion; not independently replayed.",
        "Owner mirrors are hash-pinned, not organizer-authenticated; portal encoding untested.",
        "The designated lane/template and buffered matched-fold validation remain unresolved.",
        "No artifact-linked organizer receipt or live score is available for this file.",
    ]
    save("docs/data/run-card-gpcz.json", gpcz)
    hedge_path = "evidence/hedge_sqrt_receipt_REJECTED_89pct_same_as_primary.json"
    hedge = load(hedge_path)
    hedge_u = hedge["uniqueness"]
    hedge_u.setdefault("previously_reported_nonprobe_unique", hedge_u["unique"])
    hedge_u["unique"] = False
    hedge_u["rule_overlap_le_0.70"] = False
    hedge_u["reassessment_note"] = "Prior receipt's own lattice row is 99.8972%; it was excluded from clearance. Hedge bytes were not independently replayed in this review."
    hedge["submission_authorized"] = False
    save(hedge_path, hedge)
    gpcrec = load("docs/downloads/gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-receipt.json")
    gpcrec.update(release_verdict="negative", submission_authorized=False,
                  reassessment="evidence/release_reassessment_20261028.json")
    save("docs/downloads/gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-receipt.json", gpcrec)

    holdout = dict(audit["inherited_hmas_holdout"])
    card = {
        "schema": "karage1-active-run-card-v2", "reviewed_utc_date": audit["reviewed_utc_date"],
        "hypothesis": "Prior H-K1-1: hydrothermal alteration and shallow thermal signatures may identify faults missing from mapped catalogues. No new method lane was assigned in this request.",
        "mechanism": "Potential-field, radiometric and thermal anomaly coincidence was used as a proxy for a concealed fault; it does not prove a vent or fault.",
        "non_fault_process_that_could_mimic_it": "Volcanic lithologic contacts and Lake Lahontan shoreline benches.",
        "holdout_dti": {**holdout, "independently_replayed_this_review": False},
        "correlation_overlap_vs_registry": {
            "surface_rank_correlation": None,
            "surface_status": "Prior surface unavailable for independent pre-placement replay.",
            "witness": "registered 13GEMSDOE r13-lattice-s5",
            "witness_sha256": audit["provenance"]["lattice_sha256"],
            "candidate_dots": h["dots_in_footprint"],
            "dots_within_3px": h["lattice_dots_within_3px_count"],
            "directed_overlap": h["lattice_directed_overlap"],
            "literal_threshold": 0.70, "duplicate": True,
            "complete_registry_replayed": False,
        },
        "raster_sha256": h["sha256"],
        "raster_status": "Previously generated research raster only; not a new submission.",
        "validator_output": {
            "no_nan_inside_footprint": h["saved_byte_checks"]["no_nonfinite_inside"],
            "values_in_0_1": h["saved_byte_checks"]["inside_values_in_0_1"],
            "crs_shape_transform_match_mirror": h["saved_byte_checks"]["crs_shape_transform_match_mirror"],
            "single_band": h["saved_byte_checks"]["single_band"],
            "all_finite_range": h["saved_byte_checks"]["whole_array_strict_finite_0_1"],
            "outside_null_or_nan": h["saved_byte_checks"]["outside_all_null_or_nan"],
            "sample_organizer_authenticated": False, "portal_acceptance_tested": False,
        },
        "submission_file": Path(h["file"]).name,
        "submission_name": "karage1-hmas-sinter-dualcover-sep29-zeros",
        "submission_note": "H-K1-1 historical raster; duplicate witness failed; research only, do not submit.",
        "download_available": True, "download_purpose": "research only",
        "estimated_leaderboard_score": None, "ok_to_submit": False, "selector_approved": False,
        "experiments_this_review": 0, "slots_spent_this_review": 0, "account_quota_known": False,
        "verdict": "negative", "audit": "evidence/release_reassessment_20261028.json",
    }
    assert len(card["submission_note"]) <= 140
    save("docs/data/run-card.json", card)
    save("evidence/active_run_card_20261028.json", card)

    # Make the old generated dashboard data unambiguous if directly inspected.
    dash = load("docs/data/dashboard_data.json")
    dash["release_status"] = "SUPERSEDED: DO NOT SUBMIT; see evidence/release_reassessment_20261028.json"
    dash["run_card"] = card
    dash["experiments_summary"] = ledger
    dash["uniqueness_summary"] = uniqueness
    dash["leakage_canary_status"] = "HISTORICAL; not independently replayed and variation not evidenced."
    dash["competition"]["leaderboard_freshness"] = "Historical snapshot only; consult the official live leaderboard."
    for row in dash["comparison_rows"]:
        if row.get("rank_group") == "NEW_CANDIDATE":
            row["owner_score_label"] = "NO ORGANIZER SCORE — DO NOT SUBMIT"
            row["uniqueness_badge"] = "FAIL: literal lattice witness"
            row["exec_summary"] = "Historical research raster; local format checks passed, but the literal lattice overlap gate failed. Prior holdout was not replayed in the reassessment."
    save("docs/data/dashboard_data.json", dash)
    rows = load("evidence/nine_site_audit.json")
    for row in rows:
        if row.get("rank_group") == "NEW_CANDIDATE":
            row["owner_score_label"] = "NO ORGANIZER SCORE — DO NOT SUBMIT"
            row["uniqueness_badge"] = "FAIL: literal lattice witness"
            row["exec_summary"] = "Historical research raster; literal lattice overlap exceeds the threshold. Not a submission recommendation."
            row["superseded_by"] = "evidence/release_reassessment_20261028.json"
    save("evidence/nine_site_audit.json", rows)
    print("Updated active run card and retired misleading prior release decisions.")


if __name__ == "__main__":
    main()
