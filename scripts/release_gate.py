"""Fail-closed evidence policy; neither selects a weekly slot nor uploads.

Rows, not a self-declared maximum, drive the literal registry gate. The pinned
lattice witness must be present; there is no density or calibration exemption.
A registry report is still only as complete as its authenticated inventory.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def valid_sha256(value):
    return (isinstance(value, str) and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _lattice_pin():
    try:
        entries = json.loads((ROOT / "registry/reference_assets.json").read_text())
        matches = [x["sha256"] for x in entries if x.get("id") == "lattice"]
        return matches[0] if len(matches) == 1 else None
    except (OSError, ValueError, TypeError, KeyError):
        return None


def assess(card):
    reasons = []
    if not isinstance(card, dict):
        return {"verdict": "negative", "ok_to_submit": False, "selector_required": True,
                "reasons": ["Missing run card"]}
    for key in ("hypothesis", "mechanism", "named_non_fault_mimic"):
        if not isinstance(card.get(key), str) or not card[key].strip():
            reasons.append("Missing scientific run-card field: " + key)
    if not isinstance(card.get("lane"), str) or not card["lane"].strip():
        reasons.append("Named assigned method lane missing")
    if type(card.get("experiments")) is not int or not 1 <= card["experiments"] <= 3:
        reasons.append("No completed experiment within budget")
    elapsed = card.get("elapsed_seconds")
    if not finite_number(elapsed) or not 0 < elapsed <= 7200:
        reasons.append("Elapsed-time budget not evidenced")
    h = card.get("holdout") if isinstance(card.get("holdout"), dict) else {}
    if (h.get("label") != "HOLDOUT-DTI" or not isinstance(h.get("evaluator_version"), str)
            or not h["evaluator_version"].strip()
            or type(h.get("withheld_positives")) is not int or h["withheld_positives"] <= 0):
        reasons.append("Incomplete HOLDOUT-DTI provenance")
    score, ci = h.get("dti"), h.get("ci95")
    if (not finite_number(score) or not 0 <= score <= 1 or not isinstance(ci, list)
            or len(ci) != 2 or not all(finite_number(x) for x in ci)
            or not 0 <= ci[0] <= score <= ci[1] <= 1):
        reasons.append("Invalid holdout measurement or CI")
    # Conservative policy, not a theorem about confidence intervals: require
    # the reported paired interval to contain the observed point difference.
    # Some valid bootstrap intervals need not; they require manual policy review.
    baseline, delta = h.get("baseline_dti"), h.get("paired_delta_ci95")
    if (h.get("same_evaluator_as_best") is not True
            or h.get("baseline_evaluator_version") != h.get("evaluator_version")
            or not finite_number(baseline)
            or not 0 <= baseline <= 1 or not finite_number(score) or score <= baseline
            or not isinstance(delta, list) or len(delta) != 2
            or not all(finite_number(x) for x in delta)
            or not 0 < delta[0] <= score - baseline <= delta[1] <= 1):
        reasons.append("No measured same-evaluator improvement with positive paired CI")
    if (h.get("visible_only_features") is not True or h.get("whole_segment_buffered") is not True
            or h.get("pixel_exact_visible_mask") is not True
            or h.get("alpha") != .2 or h.get("beta") != .8 or h.get("kernel_radius_m") != 300):
        reasons.append("Hide-and-recover controls or metric parameters missing")
    canary = card.get("canary") if isinstance(card.get("canary"), dict) else {}
    aucs = canary.get("feature_aucs")
    statuses = canary.get("feature_status")
    expected_features = canary.get("expected_features")
    if (not isinstance(aucs, dict) or not aucs or canary.get("passed") is not True
            or canary.get("all_features_tested") is not True
            or canary.get("nonconstant_features_verified") is not True
            or canary.get("all_features_have_variation") is not True or canary.get("invalid_features") != []
            or type(canary.get("n_features")) is not int or canary["n_features"] != len(aucs)
            or any(not isinstance(k, str) or not k.strip() for k in aucs)
            or not isinstance(statuses, dict) or set(statuses) != set(aucs)
            or any(v != "tested" for v in statuses.values())
            or not isinstance(expected_features, list)
            or any(not isinstance(k, str) or not k.strip() for k in expected_features)
            or len(expected_features) != len(set(expected_features)) or set(expected_features) != set(aucs)
            # Inputs are direction-invariant AUCs: max(raw_auc, 1 - raw_auc).
            or any(not finite_number(v) or not .50 <= v <= .90 for v in aucs.values())):
        reasons.append("Single-feature leakage canary missing or failed")

    reg = card.get("registry") if isinstance(card.get("registry"), dict) else {}
    rows = reg.get("comparisons")
    expected = reg.get("expected_rasters")
    if (reg.get("complete") is not True or reg.get("saved_bytes_checked") is not True
            or reg.get("all_registry_rasters_included") is not True or reg.get("exact_ranks") is not True
            or reg.get("literal_all_rasters") is not True or reg.get("excluded_registry_rasters") != []
            or reg.get("duplicate_witnesses") != [] or reg.get("surface_checked_before_placement") is not True
            or type(expected) is not int or expected <= 0 or not isinstance(rows, list)
            or len(rows) != expected):
        reasons.append("Complete registry inventory / pre-placement and saved-byte comparisons missing")
        rows = rows if isinstance(rows, list) else []
    inventory = reg.get("inventory_sha256")
    surface = reg.get("preplacement_surface_sha256")
    if (not valid_sha256(inventory) or not valid_sha256(surface)
            or reg.get("preplacement_inventory_sha256") != inventory
            or reg.get("candidate_sha256") != card.get("raster_sha256")):
        reasons.append("Registry receipt is not bound to a pinned inventory, surface and candidate")
    ids = set()
    dot_counts = set()
    lattice_ok = False
    for row in rows:
        if not isinstance(row, dict):
            reasons.append("Malformed registry comparison")
            continue
        ref_id, digest = row.get("id"), row.get("sha256")
        if not isinstance(ref_id, str) or not ref_id or ref_id in ids:
            reasons.append("Missing or duplicate registry identity")
        else:
            ids.add(ref_id)
        if not valid_sha256(digest):
            reasons.append("Registry raster hash missing or invalid")
        # A self-reported identity flag cannot contradict the actual digests in
        # the card. This checks internal consistency, not the bytes themselves.
        if valid_sha256(digest) and digest == card.get("raster_sha256"):
            reasons.append("Candidate hash matches registry raster: " + str(ref_id))
        if ref_id == "lattice" and digest == _lattice_pin() and digest is not None:
            lattice_ok = True
        for key in ("surface_spearman", "dot_spearman"):
            value = row.get(key)
            if not finite_number(value) or not -1 <= value <= 1:
                reasons.append("Registry rank correlation missing: " + str(ref_id))
            elif abs(value) > .90:
                reasons.append("Registry rank correlation exceeds limit: " + str(ref_id))
        hits, dots = row.get("dots_within_3px"), row.get("candidate_dots")
        if type(hits) is not int or type(dots) is not int or dots <= 0 or hits < 0 or hits > dots:
            reasons.append("Registry dot counts missing or invalid: " + str(ref_id))
        else:
            dot_counts.add(dots)
            if hits * 10 > dots * 7:
                reasons.append("Registry dot overlap exceeds 70%: " + str(ref_id))
        if row.get("identical_bytes") is not False or row.get("identical_pixels") is not False:
            reasons.append("Registry exact-identity check missing or failed: " + str(ref_id))
    if not lattice_ok:
        reasons.append("Pinned lattice witness missing from registry comparisons")
    if len(dot_counts) != 1:
        reasons.append("Candidate dot counts disagree across registry comparisons")

    validator = card.get("validator") if isinstance(card.get("validator"), dict) else {}
    for key in ("single_band", "float32", "all_finite_inside", "range_0_1_inside",
                "crs_match", "shape_match", "transform_match", "outside_encoding_accepted",
                "template_official_authenticated"):
        if validator.get(key) is not True:
            reasons.append("Saved TIFF validation missing or failed: " + key)
    digest = card.get("raster_sha256")
    if not valid_sha256(digest):
        reasons.append("Saved raster SHA-256 missing")
    note = card.get("submission_note")
    name = card.get("submission_name")
    if not isinstance(note, str) or not note.strip() or len(note) > 140 or not isinstance(name, str) or not name.strip():
        reasons.append("Submission name / short note missing")
    # Scientific promotion is NOT a weekly slot selection or upload authorization.
    return {"verdict": "negative" if reasons else "promote", "ok_to_submit": False,
            "selector_required": True, "reasons": reasons}
