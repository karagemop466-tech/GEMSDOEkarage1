"""Fail-closed evidence policy; neither selects a weekly slot nor uploads.

Rows, not a self-declared maximum, drive the literal registry gate. The pinned
lattice witness must be present; there is no density or calibration exemption.
A registry report is still only as complete as its authenticated inventory.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def finite_number(value):
    if type(value) not in (int, float):
        return False
    try:
        return math.isfinite(value)
    except OverflowError:
        return False


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
            or type(h.get("withheld_positives")) is not int or h["withheld_positives"] <= 0
            or ("baseline_withheld_positives" in h
                and h.get("baseline_withheld_positives") != h.get("withheld_positives"))):
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
    # Matching evaluator names do not establish that the two measurements used
    # the same withheld segments. Require an immutable split-assignment digest
    # for both arms. A digest is a consistency check, not proof of honest folds.
    split = h.get("fold_assignment_sha256")
    if (h.get("same_evaluator_as_best") is not True
            or h.get("baseline_evaluator_version") != h.get("evaluator_version")
            or not valid_sha256(split) or h.get("baseline_fold_assignment_sha256") != split
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
            or not valid_sha256(reg.get("candidate_sha256"))
            or reg.get("preplacement_inventory_sha256") != inventory
            or reg.get("candidate_sha256") != card.get("raster_sha256")):
        reasons.append("Registry receipt is not bound to a pinned inventory, surface and candidate")
    ids = set()
    digests = set()
    dot_counts = set()
    lattice_ok = False
    for row in rows:
        if not isinstance(row, dict):
            reasons.append("Malformed registry comparison")
            continue
        ref_id, digest = row.get("id"), row.get("sha256")
        if not isinstance(ref_id, str) or not ref_id.strip() or ref_id in ids:
            reasons.append("Missing or duplicate registry identity")
        else:
            ids.add(ref_id)
        if not valid_sha256(digest):
            reasons.append("Registry raster hash missing or invalid")
        elif digest in digests:
            reasons.append("Duplicate registry raster hash: " + str(ref_id))
        else:
            digests.add(digest)
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
    for key in ("geotiff", "single_band", "float32", "all_finite_inside", "range_0_1_inside",
                "crs_match", "shape_match", "transform_match", "outside_encoding_accepted",
                "template_official_authenticated"):
        if validator.get(key) is not True:
            reasons.append("Saved TIFF validation missing or failed: " + key)
    if ("unmasked_inside" in validator and validator.get("unmasked_inside") is not True) or validator.get("masked_inside_count", 0) != 0:
        reasons.append("Saved TIFF validation missing or failed: unmasked_inside / masked in-footprint pixels")
    digest = card.get("raster_sha256")
    if not valid_sha256(digest):
        reasons.append("Saved raster SHA-256 missing")
    # Diagnostic booleans from an unrelated TIFF must never clear this card.
    # The template hash binds the reported grid checks to one particular sample;
    # matching hashes alone do not establish that sample is organizer-authentic.
    if (not valid_sha256(validator.get("candidate_sha256"))
            or validator.get("candidate_sha256") != digest
            or not valid_sha256(validator.get("template_sha256"))
            or validator.get("template_sha256") == digest):
        reasons.append("Saved TIFF validation not bound to candidate and template hashes")
    note = card.get("submission_note")
    name = card.get("submission_name")
    if (not isinstance(note, str) or not note.strip() or len(note) > 140
            or not isinstance(name, str) or not name.strip() or len(name) > 140):
        reasons.append("Submission name / short note missing")
    # Scientific promotion is NOT a weekly slot selection or upload authorization.
    return {"verdict": "negative" if reasons else "promote", "ok_to_submit": False,
            "selector_required": True, "reasons": reasons}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", type=Path, help="Path to JSON run-card / release-gate input")
    parser.add_argument("--out", type=Path, help="Optional output JSON path")
    args = parser.parse_args(argv)
    if args.out is not None:
        # Preserve the source evidence even when the output is spelled through
        # a symlink or hard link. Never turn the input into its own verdict.
        same_path = args.out.resolve() == args.card.resolve()
        try:
            same_path = same_path or os.path.samefile(args.out, args.card)
        except FileNotFoundError:
            pass
        if same_path:
            print("Output must not overwrite the input run card", file=sys.stderr)
            return 1
    try:
        def _reject_constant(value: str):
            raise ValueError(f"non-standard JSON constant: {value}")
        payload = json.loads(args.card.read_text(), parse_constant=_reject_constant,
                             object_pairs_hook=_unique_object)
        if isinstance(payload, dict) and isinstance(payload.get("input"), dict) and "holdout" not in payload:
            payload = payload["input"]
        result = assess(payload)
    except (OSError, ValueError) as exc:
        result = {"verdict": "negative", "ok_to_submit": False, "selector_required": True,
                  "reasons": [f"Unreadable or malformed run card: {exc}"]}
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix="." + args.out.name + ".", suffix=".tmp", dir=args.out.parent)
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.chmod(tmp, 0o644)
            tmp.replace(args.out)
        finally:
            tmp.unlink(missing_ok=True)
    else:
        sys.stdout.write(text)
    return 0 if result["verdict"] == "promote" else 1


if __name__ == "__main__":
    raise SystemExit(main())
