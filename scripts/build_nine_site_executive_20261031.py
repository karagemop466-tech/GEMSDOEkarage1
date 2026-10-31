#!/usr/bin/env python3
"""Build evidence/nine_site_executive_20261031.json: the per-site executive table and the candidate row.

Reads only committed evidence and registry files (plus the restored audit inputs for the
uniqueness numbers, which are already summarised in evidence/focus_nine_audit_20261031.json).
Writes no raster and makes no score claim. Every number is labelled by its evidence class.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "evidence" / "focus_nine_audit_20261031.json"
FINAL = ROOT / "evidence" / "h31_final_20261031.json"
HOLD = ROOT / "evidence" / "h31_holdout_20261031.json"
HOLD_B20 = ROOT / "evidence" / "h31_holdout_20261031_buffer20_posthoc.json"
LEDGER = ROOT / "registry" / "score_ledger.csv"
LEADER = ROOT / "registry" / "leaderboard_snapshot_20261030.json"
OUT = ROOT / "evidence" / "nine_site_executive_20261031.json"

SITES = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]
FWD_LIMIT = 0.70
PHI_LIMIT = 0.90


def main() -> int:
    audit = json.loads(AUDIT.read_text())
    final = json.loads(FINAL.read_text())
    hold = json.loads(HOLD.read_text())
    hold20 = json.loads(HOLD_B20.read_text())
    ledger = {}
    with LEDGER.open() as fh:
        for row in csv.DictReader(fh):
            ledger[row["site"]] = row
    leader = json.loads(LEADER.read_text())

    pair = audit["pairwise_nine_plus_lattice"]
    rows = []
    for site in SITES:
        meta = audit["files"][site]
        worst = None
        exact_partners = []
        fails = []
        for other in SITES:
            if other == site:
                continue
            fwd_out = pair[site][other]["fwd3_a_dots_within_3px_of_b"]
            fwd_in = pair[other][site]["fwd3_a_dots_within_3px_of_b"]
            phi = pair[site][other]["phi_spearman_footprint"]
            exact = pair[site][other]["exact_positive_mask_equal"]
            if exact:
                exact_partners.append(other)
            f = max(fwd_out, fwd_in)
            if worst is None or f > worst[1]:
                worst = (other, f, phi)
            if fwd_out > FWD_LIMIT or fwd_in > FWD_LIMIT or abs(phi) >= PHI_LIMIT or exact:
                fails.append(other)
        lattice = audit["lattice_probe_fwd3_site_dots_within_3px_of_lattice"][site]
        rows.append({
            "site": site,
            "file_to_download": meta["file"],
            "file_sha256": meta["sha256"],
            "dots": meta["dots"],
            "reported_score": float(ledger[site]["score"]),
            "score_label": "USER-REPORTED / UNVERIFIED (score_ledger.csv; no organizer receipt)",
            "estimated_leaderboard_score": "NOT ESTIMABLE",
            "estimate_reason": ("No organizer receipt and no calibrated mapping from our catalogue holdout "
                                "to the hidden labels. Holdout random-placement control is 0.0773 HOLDOUT-DTI."),
            "unique_vs_other_focus_sites": not fails,
            "duplicate_flags_vs": fails,
            "exact_mask_duplicates_of": exact_partners,
            "worst_pair_3px_overlap_either_direction": {"sibling": worst[0], "fraction": round(worst[1], 6),
                                                       "phi": round(worst[2], 6)},
            "lattice_forward3px_overlap": round(lattice, 6),
            "lattice_gate_passes": lattice <= FWD_LIMIT,
            "ok_to_download_and_submit": False,
            "action": "DO NOT RESUBMIT (already listed; a re-upload is not a new candidate)",
        })

    cand = {
        "file_to_download": final["file"],
        "zip_to_download": final["zip"],
        "sha256_tif": final["sha256_tif"],
        "dots": final["dots_written"],
        "name": "karage1-h31-visgrad-nms3px-40k-20261031-zeros",
        "holdout_dti": {
            "label": "HOLDOUT-DTI",
            "evaluator_version": hold["evaluator_version"],
            "value": round(hold["pooled"]["scores"]["candidate_H_V31"]["dti"], 6),
            "ci95": [round(x, 6) for x in hold["pooled"]["scores"]["candidate_H_V31"]["ci95"]],
            "withheld_positive_pixels": hold["pooled"]["scores"]["candidate_H_V31"]["withheld_positive_pixels"],
            "paired_vs_random": {"delta": round(hold["pooled"]["paired_differences"]["C1_random"]["delta"], 6),
                                 "ci95": [round(x, 6) for x in hold["pooled"]["paired_differences"]["C1_random"]["ci95"]]},
            "buffer20_posthoc_value": round(hold20["pooled"]["scores"]["candidate_H_V31"]["dti"], 6),
            "buffer20_posthoc_ci95": [round(x, 6) for x in hold20["pooled"]["scores"]["candidate_H_V31"]["ci95"]],
            "buffer20_posthoc_paired_vs_random_delta": round(hold20["pooled"]["paired_differences"]["C1_random"]["delta"], 6),
            "buffer20_posthoc_paired_vs_random_ci95": [round(x, 6) for x in hold20["pooled"]["paired_differences"]["C1_random"]["ci95"]],
            "random_control_value": round(hold["pooled"]["scores"]["C1_random"]["dti"], 6),
            "canary_max_symmetric_auc": max(hold["leakage_canary"]["max_symmetric_auc_per_channel"].values()),
        },
        "estimated_leaderboard_score": "NOT ESTIMABLE",
        "unique_vs_nine_focus": final["unique_vs_nine_focus_passes"],
        "lattice_gate_passes": final["lattice_gate_passes"],
        "surface_gate_passes": final["surface_gate_passes_all_registry"],
        "validator_pass": final["validator"]["pass"],
        "independent_saved_byte_audit": {
            "receipt": "evidence/audit_h31_candidate_saved_bytes_20261031.json",
            "method": "re-read saved bytes; overlap by 3 px disk dilation (independent of the runner)",
            "all_format_and_focus_checks_pass": bool(json.loads((ROOT / "evidence/audit_h31_candidate_saved_bytes_20261031.json").read_text())["uniqueness_vs_focus_passes"]),
            "lattice_gate_passes": bool(json.loads((ROOT / "evidence/audit_h31_candidate_saved_bytes_20261031.json").read_text())["lattice_gate_passes"]),
        },
        "gate_status": final["gate_status"],
        "ok_to_download_and_submit": False,
        "submission_status": final["submission_status"],
    }

    report = {
        "schema": "karage1-nine-site-executive-20261031-v1",
        "date_utc": "2026-10-31",
        "leaderboard_context": {
            "label": leader["status_label"],
            "captured_utc_date": leader["captured_utc_date"],
            "top_score": leader["top_score"],
            "rank_48_score": leader["rank_48_score"],
            "note": "Snapshot from 30 Oct 2026; not re-fetched this session (drivendata.org not reachable from the sandbox).",
        },
        "rows": rows,
        "candidate": cand,
        "b2_mechanism": audit["b2_vs_d28"],
        "decision": ("NO FILE IS OK TO DOWNLOAD AND SUBMIT. The candidate is unique and format-valid, "
                     "but fails the registry lattice gate (forward overlap 99.75%, inherent to any dotted "
                     "raster on this grid). Owner decision required before any selector step."),
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
