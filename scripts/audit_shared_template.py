#!/usr/bin/env python3
"""Audit the immutable shared-template pin without creating a private fork.

The audit separates four questions that older reports conflated:

* Is the checkout exactly the commit named in ``registry/template.json``?
* Are the cached feature bytes bound to source inputs and builder code?
* Does the shared holdout implement the requested whole-segment buffered split?
* Can the shared CLI classify a catalogue-leaking static raster as valid holdout evidence?

A negative report is expected while any contract fails.  The script never writes
predictions, estimates a leaderboard score, selects a weekly slot, or modifies
the shared checkout.  ``--report-only`` makes a completed negative audit exit 0;
without it, protocol incompatibility exits 1 so automation fails closed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np
from scipy.ndimage import distance_transform_edt, label

ROOT = Path(__file__).resolve().parents[1]
# This session artifact is content-addressed and reproducible. Runtime wall-clock
# time is deliberately excluded so identical audited bytes yield identical JSON.
AUDIT_LOGICAL_TIME = "2026-10-28T00:00:00+00:00"
DEFAULT_TEMPLATE = ROOT / ".work" / "template"
DEFAULT_DATA = ROOT / ".cache" / "gems_data"
DEFAULT_STACK = ROOT / ".cache" / "gems_work" / "feature_stack.npy"
AUDITED_FILES = (
    "scripts/evaluate_holdout.py",
    "scripts/submission_writer.py",
    "scripts/build_features.py",
    "src/gems32/holdout.py",
    "src/gems32/submission.py",
    "src/gems32/features.py",
    "registry/feature_receipt.json",
)
AUDITED_RUNTIME_ASSETS = (
    ".cache/gems_work/feature_stack.npy",
    ".cache/gems_data/training_features.tif",
    ".cache/gems_data/sample_submission.tif",
    ".cache/gems_data/labels.tif",
    ".cache/gems_data/existing_faults.tif",
    ".cache/gems_data/external/derived_sgmc_faults_100m_u8.tif",
)
UPSTREAM_ISSUES = {
    "feature_filter": "https://github.com/buffedlizard55-lab/GEMSDOE32/issues/49",
    "cache_provenance": "https://github.com/buffedlizard55-lab/GEMSDOE32/issues/53",
    "holdout_buffer": "https://github.com/buffedlizard55-lab/GEMSDOE32/issues/60",
    "static_evidence_class": "https://github.com/buffedlizard55-lab/GEMSDOE32/issues/61",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_pin(path: Path) -> dict[str, Any]:
    pin = json.loads(path.read_text())
    repo, commit = pin.get("repository"), pin.get("commit")
    if (not isinstance(repo, str)
            or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
            or any(part in (".", "..") for part in repo.split("/"))):
        raise ValueError("template repository must be a safe owner/name slug")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("template commit must be a full immutable SHA")
    return pin


def git_text(template: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(template), *args], text=True).strip()


def checkout_receipt(template: Path, pin: dict[str, Any]) -> dict[str, Any]:
    if not (template / ".git").is_dir():
        return {
            "present": False,
            "actual_commit": None,
            "commit_matches_pin": False,
            "clean": False,
            "remote_matches_pin": False,
            "errors": ["shared checkout is absent"],
        }
    errors: list[str] = []
    try:
        actual = git_text(template, "rev-parse", "HEAD")
        status = git_text(template, "status", "--porcelain")
        remote = git_text(template, "remote", "get-url", "origin")
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "present": True,
            "actual_commit": None,
            "commit_matches_pin": False,
            "clean": False,
            "remote_matches_pin": False,
            "errors": [f"git inspection failed: {exc}"],
        }
    repo = pin["repository"]
    normalized_remote = remote.rstrip("/")
    remote_ok = normalized_remote in {
        f"https://github.com/{repo}",
        f"https://github.com/{repo}.git",
        f"git@github.com:{repo}",
        f"git@github.com:{repo}.git",
        f"ssh://git@github.com/{repo}",
        f"ssh://git@github.com/{repo}.git",
    }
    if actual != pin["commit"]:
        errors.append("checkout commit differs from immutable pin")
    if status:
        errors.append("shared checkout has local modifications")
    if not remote_ok:
        errors.append("checkout origin differs from pinned repository")
    return {
        "present": True,
        "actual_commit": actual,
        "commit_matches_pin": actual == pin["commit"],
        "clean": not bool(status),
        "remote": remote,
        "remote_matches_pin": remote_ok,
        "errors": errors,
    }


def tool_receipt(template: Path) -> tuple[dict[str, str | None], list[str]]:
    hashes: dict[str, str | None] = {}
    errors: list[str] = []
    for rel in AUDITED_FILES:
        path = template / rel
        if not path.is_file() or path.is_symlink():
            hashes[rel] = None
            errors.append(f"missing or non-regular shared file: {rel}")
        else:
            hashes[rel] = sha256_file(path)
    return hashes, errors


def static_contract(template: Path, pin: dict[str, Any]) -> dict[str, Any]:
    """Record source-level contract probes; dynamic checks remain authoritative."""
    def text(rel: str) -> str:
        path = template / rel
        return path.read_text() if path.is_file() else ""

    holdout = text("src/gems32/holdout.py")
    evaluator = text("scripts/evaluate_holdout.py")
    writer = text("scripts/submission_writer.py")
    writer_core = text("src/gems32/submission.py")
    features = text("src/gems32/features.py")
    try:
        feature_receipt = json.loads(text("registry/feature_receipt.json") or "{}")
    except ValueError:
        feature_receipt = {}

    lane = pin.get("method_lane")
    lane_assigned = isinstance(lane, str) and bool(lane.strip())
    connected_components = bool(re.search(r"\blabel\(labels,\s*structure=", holdout))
    truth_clipped = "truth_sub = (hidden_full[sl] & domain[sl])" in holdout
    quadrant_collar = "collars[fold] = binary_dilation(q" in holdout
    static_diagnostic = '"mode": "static_binary_diagnostic"' in evaluator
    static_invokes_holdout = "evaluate_hide_and_recover(mask, ctx" in evaluator
    writer_binary_guard = "require_binary_mask" in writer and "require_binary_mask" in writer_core
    post_format_note_guard = "exceeds 140 characters after expansion" in writer_core
    feature_known_expression = "return -small * (big < 0)" in features
    cache_has_digest = isinstance(feature_receipt.get("sha256"), str) and bool(
        re.fullmatch(r"[0-9a-f]{64}", feature_receipt.get("sha256", ""))
    )

    checks = {
        "assigned_method_lane": {
            "passed": lane_assigned,
            "observed": lane,
            "requirement": "A non-empty single method paragraph must be assigned before a parallel run.",
        },
        "whole_segment_buffer_contract": {
            "passed": False,
            "observed": {
                "uses_8_connected_components": connected_components,
                "truth_clipped_to_eroded_domain": truth_clipped,
                "collar_is_built_from_quadrant": quadrant_collar,
            },
            "requirement": "Withhold whole fault segments with a measured buffer from visible catalogue context.",
            "upstream_issue": UPSTREAM_ISSUES["holdout_buffer"],
            "status": "Dynamic replay required; current pinned implementation is known to fail it.",
        },
        "static_input_evidence_class": {
            "passed": False,
            "observed": {
                "outer_mode_is_static_diagnostic": static_diagnostic,
                "static_mask_still_invokes_holdout": static_invokes_holdout,
            },
            "requirement": "A static full-catalogue diagnostic must not be emitted as valid HOLDOUT-DTI evidence.",
            "upstream_issue": UPSTREAM_ISSUES["static_evidence_class"],
        },
        "writer_rejects_implicit_probability_conversion": {
            "passed": writer_binary_guard,
            "observed": "require_binary_mask present" if writer_binary_guard else "binary guard absent",
            "requirement": "Reject rather than silently threshold or clip model output.",
        },
        "writer_checks_rendered_note_length": {
            "passed": post_format_note_guard,
            "observed": "post-format guard present" if post_format_note_guard else "only raw note length checked",
            "requirement": "The final rendered portal note must be <=140 characters.",
        },
        "feature_builder_known_hessian_issue_resolved": {
            "passed": not feature_known_expression,
            "observed": "known smaller-eigenvalue expression present" if feature_known_expression else "known expression absent",
            "requirement": "Resolve the shared ridge-response defect and invalidate affected cache bytes.",
            "upstream_issue": UPSTREAM_ISSUES["feature_filter"],
        },
        "canonical_cache_is_content_addressed": {
            "passed": cache_has_digest,
            "observed": {
                "receipt_path": "registry/feature_receipt.json",
                "sha256_present": cache_has_digest,
                "receipt_channels": feature_receipt.get("n_channels"),
                "receipt_shape": feature_receipt.get("shape"),
            },
            "requirement": "Publish canonical cache bytes, digest, inputs, channel order and builder commit.",
            "upstream_issue": UPSTREAM_ISSUES["cache_provenance"],
        },
    }
    return {"checks": checks, "all_passed": all(x["passed"] for x in checks.values())}


def verify_inputs(data_dir: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text())
    wanted = {
        "training_features",
        "labels",
        "existing_faults",
        "sample_submission",
        "ext_derived_sgmc_faults_100m_u8",
    }
    rows: dict[str, Any] = {}
    for entry in manifest.get("files", []):
        if entry.get("id") not in wanted:
            continue
        path = data_dir / entry["dest"]
        exists = path.is_file() and not path.is_symlink()
        size = path.stat().st_size if exists else None
        digest = sha256_file(path) if exists and size == entry.get("bytes") else None
        rows[entry["id"]] = {
            "path": entry["dest"],
            "exists": exists,
            "bytes": size,
            "expected_bytes": entry.get("bytes"),
            "sha256": digest,
            "expected_sha256": entry.get("sha256"),
            "verified": exists and size == entry.get("bytes") and digest == entry.get("sha256"),
            "organizer_authenticated": False,
        }
    missing_ids = sorted(wanted - set(rows))
    return {
        "rows": rows,
        "missing_manifest_ids": missing_ids,
        "all_verified_to_third_party_manifest": not missing_ids and all(row["verified"] for row in rows.values()),
        "organizer_authenticated": False,
        "scope": "Hash agreement proves mirror consistency only; it does not authenticate organizer origin.",
    }


def stack_receipt(stack_path: Path, template: Path, input_receipt: dict[str, Any]) -> dict[str, Any]:
    if not stack_path.is_file() or stack_path.is_symlink():
        return {"present": False, "verified": False, "path": str(stack_path), "errors": ["shared feature stack is absent or non-regular"]}
    errors: list[str] = []
    try:
        mm = np.load(stack_path, mmap_mode="r")
        shape, dtype = list(mm.shape), str(mm.dtype)
    except (OSError, ValueError) as exc:
        return {"present": True, "verified": False, "path": str(stack_path), "errors": [f"cannot read NPY: {exc}"]}
    try:
        declared = json.loads((template / "registry/feature_receipt.json").read_text())
    except (OSError, ValueError):
        declared = {}
    expected_shape = [*declared.get("shape", []), declared.get("n_channels")]
    if shape != expected_shape:
        errors.append(f"shape {shape} differs from declared {expected_shape}")
    if dtype != "float32":
        errors.append(f"dtype is {dtype}, expected float32")
    if not input_receipt.get("all_verified_to_third_party_manifest"):
        errors.append("source inputs are absent or differ from the third-party manifest")
    try:
        display_path = str(stack_path.resolve().relative_to(ROOT))
    except ValueError:
        display_path = str(stack_path)
    return {
        "present": True,
        "verified": not errors,
        "path": display_path,
        "bytes": stack_path.stat().st_size,
        "sha256": sha256_file(stack_path),
        "shape": shape,
        "dtype": dtype,
        "ordered_channels": declared.get("channels"),
        "builder_files": {
            rel: sha256_file(template / rel)
            for rel in ("scripts/build_features.py", "src/gems32/features.py")
            if (template / rel).is_file()
        },
        "source_input_sha256": {
            key: row["sha256"] for key, row in input_receipt.get("rows", {}).items() if row.get("sha256")
        },
        "organizer_authenticated": False,
        "errors": errors,
        "caveat": "A reproducible local cache does not resolve the open shared feature-filter defect or make these official organizer bytes.",
    }


def _load_shared_holdout(template: Path):
    """Import the pinned shared module in this process; callers run in a clean CLI."""
    source = str(template / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
    # Refuse accidental reuse of another template implementation.
    prior = sys.modules.get("gems32.holdout")
    if prior is not None and not Path(prior.__file__).resolve().is_relative_to(template.resolve()):
        raise RuntimeError("gems32.holdout was already imported from another checkout")
    return importlib.import_module("gems32.holdout")


def dynamic_holdout_probe(template: Path, data_dir: Path) -> dict[str, Any]:
    holdout = _load_shared_holdout(template)
    ctx = holdout.load_holdout_context(data_dir)
    components, n_components = label(ctx.labels, structure=np.ones((3, 3), dtype=int))
    rows: list[dict[str, Any]] = []
    for cell in ctx.cells:
        truth = np.zeros_like(ctx.labels, dtype=bool)
        sy, sx = cell.bbox
        yy, xx = cell.truth_coords
        truth[yy + int(sy.start), xx + int(sx.start)] = True
        ids = np.unique(components[truth])
        ids = ids[ids > 0]
        source_pixels = np.isin(components, ids) & ctx.labels
        d_visible = distance_transform_edt(~cell.visible_full)
        partial = 0
        for component_id in ids:
            component_mask = (components == component_id) & ctx.labels
            if not np.array_equal(truth & component_mask, component_mask):
                partial += 1
        rows.append(
            {
                "cell": cell.key,
                "withheld_positive_pixels": int(truth.sum()),
                "selected_8_connected_components": int(ids.size),
                "selected_component_pixels": int(source_pixels.sum()),
                "scored_fraction_of_selected_components": float(truth.sum() / source_pixels.sum()),
                "minimum_truth_to_visible_distance_px": float(d_visible[truth].min()),
                "truth_pixels_within_claimed_buffer": int((truth & (d_visible <= holdout.COLLAR_PX)).sum()),
                "partially_scored_component_instances": int(partial),
            }
        )

    truth_total = sum(row["withheld_positive_pixels"] for row in rows)
    near_total = sum(row["truth_pixels_within_claimed_buffer"] for row in rows)
    partial_total = sum(row["partially_scored_component_instances"] for row in rows)
    minimum = min(row["minimum_truth_to_visible_distance_px"] for row in rows)

    # This deliberately leaking input is a software canary, never a scientific result.
    leak = holdout.evaluate_hide_and_recover(
        ctx.labels,
        ctx,
        b_visible_px=0.0,
        n_boot=1000,
        seed=20261026,
        name="invalid-full-catalogue-canary",
    )
    return {
        "split_geometry": {
            "catalogue_8_connected_components": int(n_components),
            "claimed_buffer_px": int(holdout.COLLAR_PX),
            "minimum_truth_to_visible_distance_px": minimum,
            "withheld_positive_pixel_instances": truth_total,
            "truth_pixel_instances_within_claimed_buffer": near_total,
            "fraction_within_claimed_buffer": near_total / truth_total,
            "partially_scored_component_instances": partial_total,
            "buffer_contract_passed": minimum > holdout.COLLAR_PX,
            "whole_selected_component_scoring_passed": partial_total == 0,
            "cells": rows,
        },
        "full_catalogue_leakage_canary": {
            "evidence_class": "INVALID-HOLDOUT / LEAKAGE-CANARY",
            "valid_holdout": False,
            "input": "the complete mirrored labels.tif catalogue",
            "tool_emitted_score_label": leak.get("score_label"),
            "tool_evaluator_version": leak.get("evaluator_version"),
            "tool_withheld_positive_pixels": leak.get("n_withheld_positives"),
            "tool_numeric_output_not_a_score": leak.get("pooled_dti"),
            "tool_ci95_not_valid_holdout_evidence": leak.get("ci95_cluster_bootstrap"),
            "classification_contract_passed": (
                leak.get("score_label") != "HOLDOUT-DTI"
                and leak.get("pooled_dti") is None
                and leak.get("ci95_cluster_bootstrap") is None
            ),
            "reason": "The static input contains every hidden catalogue pixel and has no fold-local provenance; it must emit no holdout score or CI.",
        },
    }


def contract_summary(report: dict[str, Any]) -> dict[str, Any]:
    """Reduce the full audit to the bytes required for execution preflight."""
    runtime_assets: dict[str, dict[str, Any]] = {}
    for row in (report.get("input_receipt") or {}).get("rows", {}).values():
        if isinstance(row.get("sha256"), str):
            runtime_assets[f".cache/gems_data/{row['path']}"] = {
                "bytes": row.get("bytes"),
                "sha256": row["sha256"],
            }
    cache = report.get("shared_cache_receipt") or {}
    if isinstance(cache.get("sha256"), str) and isinstance(cache.get("path"), str):
        runtime_assets[cache["path"]] = {
            "bytes": cache.get("bytes"),
            "sha256": cache["sha256"],
            "shape": cache.get("shape"),
            "dtype": cache.get("dtype"),
        }
    return {
        "schema": "karage1-shared-template-contract-v1",
        "repository": report["template_pin"]["repository"],
        "commit": report["template_pin"]["commit"],
        "audited_utc": report["created_utc"],
        "protocol_compatible": report["protocol_compatible"],
        "tool_sha256": report["tool_sha256"],
        "runtime_assets": runtime_assets,
        "failed_check_ids": [
            key for key, value in report["static_contract"]["checks"].items() if not value["passed"]
        ],
        "dynamic_contract": {
            "run": report.get("dynamic_holdout_probe") is not None,
            "buffer_contract_passed": (report.get("dynamic_holdout_probe") or {}).get("split_geometry", {}).get("buffer_contract_passed"),
            "whole_selected_component_scoring_passed": (report.get("dynamic_holdout_probe") or {}).get("split_geometry", {}).get("whole_selected_component_scoring_passed"),
            "static_classification_contract_passed": (report.get("dynamic_holdout_probe") or {}).get("full_catalogue_leakage_canary", {}).get("classification_contract_passed"),
        },
        "upstream_issues": UPSTREAM_ISSUES,
        "ok_to_submit": False,
        "scope": "Shared-tool compatibility only; never scientific promotion, uniqueness clearance, portal acceptance, or slot selection.",
    }


def verify_contract_for_preflight(
    root: Path,
    template: Path,
    pin: dict[str, Any],
    contract_path: Path | None = None,
) -> dict[str, Any]:
    """Verify that a committed contract is current and bound to local tool bytes."""
    contract_path = contract_path or root / "registry" / "template_contract.json"
    errors: list[str] = []
    try:
        contract = json.loads(contract_path.read_text())
    except (OSError, ValueError) as exc:
        return {"passed": False, "errors": [f"template contract unavailable: {exc}"], "protocol_compatible": False}
    if contract.get("schema") != "karage1-shared-template-contract-v1":
        errors.append("template contract schema is unsupported")
    if contract.get("repository") != pin.get("repository") or contract.get("commit") != pin.get("commit"):
        errors.append("template contract does not bind the current repository/commit pin")

    checkout = checkout_receipt(template, pin)
    errors.extend(checkout["errors"])

    hashes = contract.get("tool_sha256")
    if not isinstance(hashes, dict):
        errors.append("template contract has no tool hashes")
        hashes = {}
    if set(hashes) != set(AUDITED_FILES):
        errors.append("template contract tool set is incomplete or unexpected")
    for rel in AUDITED_FILES:
        expected = hashes.get(rel)
        path = template / rel
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            errors.append(f"invalid contract hash for {rel}")
        elif not path.is_file() or path.is_symlink():
            errors.append(f"audited template file is absent or non-regular: {rel}")
        elif sha256_file(path) != expected:
            errors.append(f"audited template file changed: {rel}")

    assets = contract.get("runtime_assets")
    if not isinstance(assets, dict):
        errors.append("template contract has no content-bound runtime assets")
        assets = {}
    if set(assets) != set(AUDITED_RUNTIME_ASSETS):
        errors.append("template contract runtime asset set is incomplete or unexpected")
    for rel, expected in assets.items():
        parts = Path(rel).parts if isinstance(rel, str) else ()
        if not parts or Path(rel).is_absolute() or ".." in parts or parts[0] != ".cache":
            errors.append(f"unsafe runtime asset path: {rel!r}")
            continue
        if not isinstance(expected, dict):
            errors.append(f"invalid runtime asset receipt: {rel}")
            continue
        expected_hash, expected_bytes = expected.get("sha256"), expected.get("bytes")
        path = root / rel
        if not isinstance(expected_hash, str) or not re.fullmatch(r"[0-9a-f]{64}", expected_hash):
            errors.append(f"invalid runtime asset hash: {rel}")
        elif not isinstance(expected_bytes, int) or expected_bytes < 0:
            errors.append(f"invalid runtime asset size: {rel}")
        elif not path.is_file() or path.is_symlink():
            errors.append(f"content-bound runtime asset is absent or non-regular: {rel}")
        elif path.stat().st_size != expected_bytes:
            errors.append(f"runtime asset size changed: {rel}")
        elif sha256_file(path) != expected_hash:
            errors.append(f"runtime asset bytes changed: {rel}")

    compatible = contract.get("protocol_compatible") is True
    failed_ids = contract.get("failed_check_ids")
    dynamic = contract.get("dynamic_contract")
    if compatible and failed_ids != []:
        errors.append("compatible contract still contains failed checks")
    if compatible and (not isinstance(dynamic, dict) or not dynamic.get("run")
                       or dynamic.get("buffer_contract_passed") is not True
                       or dynamic.get("whole_selected_component_scoring_passed") is not True
                       or dynamic.get("static_classification_contract_passed") is not True):
        errors.append("compatible contract lacks passing dynamic probes")
    if not compatible:
        errors.append("shared template is not protocol-compatible")
    return {
        "passed": not errors and compatible,
        "errors": errors,
        "protocol_compatible": compatible,
        "failed_check_ids": failed_ids if isinstance(failed_ids, list) else [],
        "checkout": checkout,
        "runtime_asset_count": len(assets),
        "contract": str(contract_path),
    }


def run_audit(template: Path, data_dir: Path, stack_path: Path, *, dynamic: bool = True) -> dict[str, Any]:
    pin = load_pin(ROOT / "registry" / "template.json")
    checkout = checkout_receipt(template, pin)
    hashes, tool_errors = tool_receipt(template)
    static = static_contract(template, pin)
    input_receipt: dict[str, Any] | None = None
    cache: dict[str, Any] | None = None
    probe: dict[str, Any] | None = None
    runtime_errors: list[str] = []
    if dynamic:
        try:
            input_receipt = verify_inputs(data_dir, ROOT / "registry" / "karage1_data_manifest.json")
            cache = stack_receipt(stack_path, template, input_receipt)
            if input_receipt["all_verified_to_third_party_manifest"] and checkout["commit_matches_pin"] and checkout["clean"]:
                probe = dynamic_holdout_probe(template, data_dir)
            else:
                runtime_errors.append("dynamic holdout probe skipped because checkout or inputs did not verify")
        except (OSError, ValueError, RuntimeError, KeyError, ImportError) as exc:
            runtime_errors.append(f"dynamic audit failed: {exc}")
    dynamic_pass = bool(
        probe
        and probe["split_geometry"]["buffer_contract_passed"]
        and probe["split_geometry"]["whole_selected_component_scoring_passed"]
        and probe["full_catalogue_leakage_canary"]["classification_contract_passed"]
    )
    protocol_compatible = bool(
        checkout["commit_matches_pin"]
        and checkout["clean"]
        and checkout["remote_matches_pin"]
        and not tool_errors
        and static["all_passed"]
        and input_receipt
        and input_receipt["all_verified_to_third_party_manifest"]
        and cache
        and cache["verified"]
        and (dynamic_pass if dynamic else False)
    )
    return {
        "schema": "karage1-shared-template-audit-v1",
        "created_utc": AUDIT_LOGICAL_TIME,
        "template_pin": pin,
        "checkout": checkout,
        "tool_sha256": hashes,
        "tool_errors": tool_errors,
        "static_contract": static,
        "input_receipt": input_receipt,
        "shared_cache_receipt": cache,
        "dynamic_holdout_probe": probe,
        "runtime_errors": runtime_errors,
        "upstream_issues": UPSTREAM_ISSUES,
        "protocol_compatible": protocol_compatible,
        "geological_experiments_run": 0,
        "candidate_rasters_generated": 0,
        "submission_slots_selected_or_spent": 0,
        "ok_to_submit": False,
        "verdict": "negative",
        "scope": "Tool/cache/split audit only. No scientific candidate, leaderboard estimate, uniqueness pass, portal test, or slot decision.",
    }


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    temp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument("--data-dir", type=Path, default=DEFAULT_DATA)
    ap.add_argument("--stack", type=Path, default=DEFAULT_STACK)
    ap.add_argument("--out", type=Path, default=ROOT / "evidence" / "shared_template_audit_20261028.json")
    ap.add_argument("--contract-out", type=Path, default=ROOT / "registry" / "template_contract.json")
    ap.add_argument("--skip-dynamic", action="store_true")
    ap.add_argument("--report-only", action="store_true", help="Return zero after writing a negative report")
    args = ap.parse_args()
    try:
        report = run_audit(args.template, args.data_dir, args.stack, dynamic=not args.skip_dynamic)
        atomic_json(args.out, report)
        atomic_json(args.contract_out, contract_summary(report))
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as exc:
        print(f"SHARED TEMPLATE AUDIT FAILED: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({
        "report": str(args.out),
        "contract": str(args.contract_out),
        "protocol_compatible": report["protocol_compatible"],
        "verdict": report["verdict"],
        "ok_to_submit": False,
    }, indent=2))
    return 0 if report["protocol_compatible"] or args.report_only else 1


if __name__ == "__main__":
    raise SystemExit(main())
