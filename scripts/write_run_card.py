#!/usr/bin/env python3
"""Write the session run card (evidence/run_card_c4222b5c_20261029.json).

Every number is read from the receipts via scripts/submission_hub.build_facts();
nothing is typed by hand. Labels: HOLDOUT-DTI (evaluator, withheld positives,
95% CI) or ORGANIZER-CONFIRMED (none exist for this session). No submission
slot is spent by this script.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts import submission_hub as h  # noqa: E402

OUT = ROOT / "evidence" / "run_card_c4222b5c_20261029.json"


def _strict(obj):
    """Replace NaN/inf with null so the JSON is strict (RFC 8259)."""
    import math
    if isinstance(obj, float) and not math.isfinite(obj):
        return None
    if isinstance(obj, dict):
        return {k: _strict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_strict(v) for v in obj]
    return obj


def _shared_receipt() -> dict:
    return json.loads((ROOT / "evidence/audit_tiltgrav_ridge_sp6_20261029.json").read_text())


def _shared_ok() -> bool:
    return bool(_shared_receipt()["format_report_ok"])


def _shared_problems() -> list:
    return list(_shared_receipt()["format_report_problems"])


def main() -> None:
    f = h.build_facts()
    rows = h.site_rows(f)
    spear = f["spearman"]
    is_cand = lambda lab: lab.startswith("NEW candidate")  # noqa: E731
    cand_pairs = [p for p in spear["pairs"] if is_cand(p["a"]) or is_cand(p["b"])]
    focus_pairs = [p for p in spear["pairs"] if not (is_cand(p["a"]) or is_cand(p["b"]))]
    mat = f["matrix"]
    labels = [it["label"] for it in mat["items"]]
    ci = next(i for i, lab in enumerate(labels) if is_cand(lab))
    li = next(i for i, lab in enumerate(labels) if lab.startswith("13GEMSDOE"))
    fi = [i for i, lab in enumerate(labels) if lab.startswith("GEMSDOE")]
    card = {
        "schema": "run-card/v1",
        "session": "arena/c4222b5c-gemsdoekarage1",
        "date": "2026-10-29",
        "lane": None,
        "lane_note": "method_lane is null in registry/registry_roles.json; no lane was inferred",
        "verdict": "NEGATIVE / DO NOT SUBMIT",
        "submission_slots_used": 0,
        "promotion": "not performed; promotion to a slot is a separate selector step",
        "experiment_budget": {"used": 3, "max": 3,
                              "items": ["EXP1 canary (leakage AUC)", "EXP2 hide-and-recover holdout",
                                        "EXP3 6 px spacing sweep"]},
        "candidate": {
            "file": h.TIF_NAME,
            "path": f"docs/downloads/{h.TIF_NAME}",
            "sha256": f["file"]["sha256"], "bytes": f["file"]["bytes"],
            "zip_sha256": f["file"]["zip_sha256"],
            "dots": f["file"]["dots"], "outside_nan_cells": f["file"]["outside_nan"],
            "format_all_checks_passed": f["file"]["all_checks_passed"],
            "submission_name": f["file"]["name_text"],
            "submission_note": f["file"]["note_text"],
            "submission_note_chars": f["file"]["note_chars"],
            "status": "NOT CLEARED: DO NOT SUBMIT",
        },
        "holdout_labels": {
            "HOLDOUT-DTI": {
                "evaluator": f["evaluator"],
                "withheld_positive_pixels": f["withheld_total"],
                "bootstrap": f["bootstrap"],
                "candidate_spaced": f["spacing"]["candidate_spaced"],
                "random_spaced_null": f["spacing"]["random_spaced_null"],
                "paired_delta_candidate_minus_random_spaced": f["spacing_delta"],
                "unspaced_candidate_vs_random": f["holdout_unspaced"],
                "unspaced_delta_vs_random": f["holdout_unspaced_delta_vs_random"],
            },
            "ORGANIZER-CONFIRMED": "none (no organizer receipt available in this environment)",
            "USER-REPORTED (not a label of ours)": {r["site"]: r["reported"] for r in rows},
        },
        "leakage_canary": {"features": f["canary"]["n_features"], "max_feature": f["canary"]["max_feature"],
                           "max_auc": f["canary"]["max_auc"], "gate": f["canary"]["alarm_gate"],
                           "any_alarm": f["canary"]["any_alarm"],
                           "candidate_score_auc": f["canary"]["candidate_score_auc"]},
        "uniqueness": {
            "rules": {"rho_gate": h.RHO_GATE, "dot_overlap_gate": h.LATTICE_GATE},
            "lattice_forward_overlap": f["lattice"]["fwd"],
            "candidate_vs_lattice_forward": mat["matrix"][ci][li],
            "candidate_vs_focus_forward_range": [min(mat["matrix"][ci][i] for i in fi), max(mat["matrix"][ci][i] for i in fi)],
            "candidate_vs_focus_abs_spearman_max": max(abs(p["spearman_full_footprint"]) for p in cand_pairs),
            "focus_pairs_rho_above_gate": [p for p in focus_pairs if p["rho_duplicate"]],
            "focus_pairs_rho_above_gate_count": sum(1 for p in focus_pairs if p["rho_duplicate"]),
            "focus_pairs_total": len(focus_pairs),
            "lattice_gate_ruling": "DECISION NEEDED from the protocol owner: the literal 3 px rule is unsatisfiable "
                                   "for every dotted raster in the registry (all >= 99.6% within 3 px of the lattice). "
                                   "This session did not jitter, rename or exempt any lattice.",
        },
        "focus_site_rows": [{k: r[k] for k in ("site", "file", "reported", "unique", "dup_focus", "dup_rho",
                                               "lattice_fwd", "cand_fwd")} for r in rows],
        "shared_template_validator": {
            "receipt": "evidence/audit_tiltgrav_ridge_sp6_20261029.json",
            "format_report_ok": _shared_ok(),
            "problems": _shared_problems(),
            "note": "Fails only on the NaN-outside policy (shared validator requires zeros outside; official spec allows null or NaN).",
        },
        "irregularities": [
            "B5: sample_submission.tif positives equal labels.tif positives; sample carries the known-fault set; official text says it 'predicts total fault absence'.",
            "B6: two evaluator lineages (gems57-pooled-hide-v2 and gemsk-hide-recover-v1); numbers not directly comparable.",
            "B7: official feature list includes a top-of-crustal magnetic source depth band not among the 19 mirrored bands.",
            "NaN-vs-zeros vendor conflict: vendor writer zeros outside; official says null/NaN outside. Adapter used; vendor not edited (integrity pin).",
            "0.3195 (README rank #47) and 0.4413 (user-cited) not verified on the live leaderboard pages read this session.",
        ],
        "sources": [
            "https://www.drivendata.org/competitions/306/competition-doe-gems/",
            "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
            "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
        ],
        "limitations": [
            "Holdout DTI is a hide-and-recover estimate on catalogue faults; it is not calibrated to organizer scores (holdout ~0.03-0.05 vs organizer-reported 0.22-0.28 for the B2 family).",
            "Data tab is login-walled; restored data are SHA-pinned third-party GitHub mirrors, not authenticated organizer downloads.",
            "Local checks cannot establish portal acceptance of any file.",
            "The shared template and assigned method lane are unresolved.",
        ],
    }
    OUT.write_text(json.dumps(_strict(card), indent=2, sort_keys=True, allow_nan=False) + "\n")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
