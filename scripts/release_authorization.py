"""Fail-closed authorization for any artifact advertised as submit-ready.

A historical lane receipt is not sufficient: only an explicit active decision
bound to the exact raster SHA-256 and all current protocol gates can authorize
an upload. This module deliberately makes missing evidence equivalent to denial.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "evidence" / "active_submission_status.json"
REQUIRED_GATES = (
    "assigned_lane",
    "canonical_template",
    "organizer_authenticated_inputs",
    "preplacement_surface_registry_check",
    "leakage_canary",
    "spatial_holdout_beats_frozen_best",
    "final_dot_registry_check",
    "saved_byte_format_validation",
)


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def load_active_status(path: Path = STATUS_PATH) -> dict[str, Any]:
    """Read status strictly; malformed, absent, or non-finite records fail closed."""
    try:
        status = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)
    except (OSError, ValueError, TypeError):
        return {"ok_to_submit": False, "reason": "active authorization record missing or invalid"}
    if not isinstance(status, dict) or status.get("schema") != "gems-active-submission-status-v1":
        return {"ok_to_submit": False, "reason": "active authorization schema missing or invalid"}
    return status


def authorization_for(gate: dict[str, Any], status: dict[str, Any] | None = None) -> tuple[bool, str]:
    """Return true only for explicit, current, exact-byte authorization.

    The selector/weekly-slot decision remains separate. This checks only whether
    a candidate has passed the scientific and file-integrity promotion gates.
    """
    status = load_active_status() if status is None else status
    if not isinstance(status, dict) or status.get("schema") != "gems-active-submission-status-v1":
        return False, "active authorization record missing or invalid"
    if status.get("verdict") != "promote" or status.get("ok_to_submit") is not True:
        return False, str(status.get("reason", "no active candidate is cleared"))
    expected_sha = gate.get("sha256")
    if not isinstance(expected_sha, str) or len(expected_sha) != 64:
        return False, "candidate has no valid SHA-256 binding"
    if status.get("candidate_sha256") != expected_sha:
        return False, "active authorization is not bound to this exact raster"
    gates = status.get("gates")
    if not isinstance(gates, dict) or any(gates.get(name) is not True for name in REQUIRED_GATES):
        return False, "one or more required protocol gates are absent or failed"
    surface = status.get("preplacement_surface_registry")
    if not isinstance(surface, dict) or surface.get("complete_registry_checked") is not True:
        return False, "complete pre-placement registry comparison is missing"
    surface_rho = surface.get("max_abs_spearman")
    if (isinstance(surface_rho, bool) or not isinstance(surface_rho, (int, float))
            or not math.isfinite(surface_rho) or abs(surface_rho) > 0.90):
        return False, "pre-placement surface correlation gate is absent or failed"
    final = status.get("final_dot_registry")
    if not isinstance(final, dict) or final.get("complete_registry_checked") is not True:
        return False, "complete final-dot registry comparison is missing"
    overlap = final.get("max_forward_overlap_within_3px")
    if (isinstance(overlap, bool) or not isinstance(overlap, (int, float))
            or not math.isfinite(overlap) or not 0 <= overlap <= 0.70):
        return False, "final-dot overlap gate is absent or failed"
    canary = status.get("leakage_canary_auc_max")
    if (isinstance(canary, bool) or not isinstance(canary, (int, float))
            or not math.isfinite(canary) or not 0 <= canary <= 0.90):
        return False, "single-feature leakage canary is missing or failed"
    validator = status.get("validator_output")
    if not isinstance(validator, dict) or any(validator.get(key) is not True for key in (
            "no_nan_inside_footprint", "values_in_0_1", "crs_shape_transform_match", "saved_bytes_verified")):
        return False, "saved-byte format validation is incomplete or failed"
    holdout = status.get("holdout_dti")
    if not isinstance(holdout, dict) or holdout.get("label") != "HOLDOUT-DTI":
        return False, "no protocol-labelled holdout result"
    if not isinstance(holdout.get("evaluator_version"), str) or not holdout["evaluator_version"]:
        return False, "holdout evaluator version is missing"
    positives = holdout.get("withheld_positive_pixels")
    if isinstance(positives, bool) or not isinstance(positives, int) or positives <= 0:
        return False, "holdout withheld-positive count is missing"
    for field in ("value", "ci95_low", "ci95_high", "paired_ci95_low_vs_frozen_best"):
        value = holdout.get(field)
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
            return False, "holdout result, paired comparison, or 95% CI is incomplete"
    if (not 0 <= holdout["value"] <= 1 or holdout["ci95_low"] > holdout["ci95_high"]
            or holdout["paired_ci95_low_vs_frozen_best"] <= 0):
        return False, "holdout fails its range, interval, or frozen-best comparison gate"
    tif_rel = gate.get("tif")
    if not isinstance(tif_rel, str) or Path(tif_rel).is_absolute() or ".." in Path(tif_rel).parts:
        return False, "candidate path is invalid"
    tif_path = ROOT / tif_rel
    try:
        digest = hashlib.sha256(tif_path.read_bytes()).hexdigest()
    except OSError:
        return False, "candidate file is missing"
    if digest != expected_sha:
        return False, "candidate file bytes do not match the gate receipt"
    return True, "active gates pass; weekly slot selection remains separate"
