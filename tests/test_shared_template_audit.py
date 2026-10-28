"""Regression tests for the shared-template compatibility audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import pytest

from scripts.audit_shared_template import (
    AUDITED_FILES,
    AUDITED_RUNTIME_ASSETS,
    load_pin,
    verify_contract_for_preflight,
)

ROOT = Path(__file__).resolve().parents[1]


def test_current_shared_audit_is_negative_for_measured_reasons():
    report = json.loads((ROOT / "evidence/shared_template_audit_20261028.json").read_text())
    contract = json.loads((ROOT / "registry/template_contract.json").read_text())
    assert report == json.loads((ROOT / "docs/data/shared-template-audit.json").read_text())
    session = json.loads((ROOT / "evidence/run_card_arena_a2fe7ce0_20261028.json").read_text())
    assert session == json.loads((ROOT / "docs/data/latest-session-run-card.json").read_text())
    assert session["verdict"] == "negative" and session["ok_to_submit"] is False
    assert session["candidate_rasters_generated"] == 0 and session["raster_sha256"] is None
    assert report["schema"] == "karage1-shared-template-audit-v1"
    assert report["verdict"] == "negative" and report["ok_to_submit"] is False
    assert report["geological_experiments_run"] == 0
    assert report["candidate_rasters_generated"] == 0
    assert report["submission_slots_selected_or_spent"] == 0
    assert report["checkout"]["commit_matches_pin"] and report["checkout"]["clean"]
    assert report["input_receipt"]["all_verified_to_third_party_manifest"]
    assert report["input_receipt"]["organizer_authenticated"] is False

    split = report["dynamic_holdout_probe"]["split_geometry"]
    assert split["claimed_buffer_px"] == 15
    assert split["minimum_truth_to_visible_distance_px"] == 2.0
    assert split["withheld_positive_pixel_instances"] == 22232
    assert split["truth_pixel_instances_within_claimed_buffer"] == 15705
    assert not split["buffer_contract_passed"]
    assert split["partially_scored_component_instances"] == 76
    assert not split["whole_selected_component_scoring_passed"]

    canary = report["dynamic_holdout_probe"]["full_catalogue_leakage_canary"]
    assert canary["evidence_class"] == "INVALID-HOLDOUT / LEAKAGE-CANARY"
    assert canary["valid_holdout"] is False
    assert canary["tool_emitted_score_label"] == "HOLDOUT-DTI"
    assert canary["tool_numeric_output_not_a_score"] == 1.0
    assert not canary["classification_contract_passed"]

    assert contract["commit"] == report["template_pin"]["commit"]
    assert contract["tool_sha256"] == report["tool_sha256"]
    assert contract["protocol_compatible"] is False
    assert {"whole_segment_buffer_contract", "static_input_evidence_class"}.issubset(contract["failed_check_ids"])


def test_shared_cache_receipt_is_content_addressed_but_not_promoted():
    report = json.loads((ROOT / "evidence/shared_template_audit_20261028.json").read_text())
    cache = report["shared_cache_receipt"]
    assert cache["verified"] and cache["dtype"] == "float32"
    assert cache["shape"] == [3730, 3292, 35]
    assert cache["bytes"] == 1719082528
    assert len(cache["sha256"]) == 64
    assert len(cache["ordered_channels"]) == 35
    assert cache["organizer_authenticated"] is False
    assert report["protocol_compatible"] is False


def test_load_pin_rejects_mutable_or_malformed_refs(tmp_path):
    path = tmp_path / "pin.json"
    for value in (
        {"repository": "owner/repo", "commit": "main"},
        {"repository": "../repo", "commit": "a" * 40},
        {"repository": "owner/repo", "commit": "A" * 40},
    ):
        path.write_text(json.dumps(value))
        with pytest.raises(ValueError):
            load_pin(path)


def test_preflight_contract_binds_exact_tool_and_runtime_bytes(tmp_path):
    root = tmp_path
    template = root / ".work/template"
    tool_hashes = {}
    for rel in AUDITED_FILES:
        path = template / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture {rel}\n")
        tool_hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    runtime_assets = {}
    for rel in AUDITED_RUNTIME_ASSETS:
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"fixture {rel}\n")
        runtime_assets[rel] = {
            "bytes": path.stat().st_size,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    subprocess.run(["git", "init", "-q", str(template)], check=True)
    subprocess.run(["git", "-C", str(template), "config", "user.name", "Fixture"], check=True)
    subprocess.run(["git", "-C", str(template), "config", "user.email", "fixture@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(template), "add", "."], check=True)
    subprocess.run(["git", "-C", str(template), "commit", "-qm", "fixture"], check=True)
    subprocess.run([
        "git", "-C", str(template), "remote", "add", "origin", "https://github.com/owner/repo.git",
    ], check=True)
    commit = subprocess.check_output(["git", "-C", str(template), "rev-parse", "HEAD"], text=True).strip()
    pin = {"repository": "owner/repo", "commit": commit}
    contract_path = root / "contract.json"
    contract_path.write_text(json.dumps({
        "schema": "karage1-shared-template-contract-v1",
        "repository": pin["repository"],
        "commit": pin["commit"],
        "protocol_compatible": True,
        "tool_sha256": tool_hashes,
        "runtime_assets": runtime_assets,
        "failed_check_ids": [],
        "dynamic_contract": {
            "run": True,
            "buffer_contract_passed": True,
            "whole_selected_component_scoring_passed": True,
            "static_classification_contract_passed": True,
        },
    }))
    assert verify_contract_for_preflight(root, template, pin, contract_path)["passed"]
    (template / "scripts/evaluate_holdout.py").write_text("changed\n")
    result = verify_contract_for_preflight(root, template, pin, contract_path)
    assert not result["passed"]
    assert any("changed" in error for error in result["errors"])
