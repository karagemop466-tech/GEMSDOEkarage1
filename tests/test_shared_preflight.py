"""Shared execution requires inputs, a lane and a byte-bound compatible contract."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import shared_tools
from scripts.audit_shared_template import AUDITED_FILES, AUDITED_RUNTIME_ASSETS


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    monkeypatch.setattr(shared_tools, "ROOT", tmp_path)
    (tmp_path / "registry").mkdir()
    return tmp_path


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def configure(root, lane, missing=(), *, compatible=True, stale_contract=False):
    missing = set(missing)
    runtime_assets = {}
    for rel in AUDITED_RUNTIME_ASSETS:
        content = ("runtime asset: " + rel + "\n").encode()
        runtime_assets[rel] = {"bytes": len(content), "sha256": _sha(content)}
        if Path(rel).name not in missing:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

    template = root / ".work/template"
    files = {}
    for rel in AUDITED_FILES:
        content = ("shared tool: " + rel + "\n").encode()
        path = template / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        files[rel] = _sha(content)

    subprocess.run(["git", "init", "-q", str(template)], check=True)
    subprocess.run(["git", "-C", str(template), "config", "user.name", "Fixture"], check=True)
    subprocess.run(["git", "-C", str(template), "config", "user.email", "fixture@example.invalid"], check=True)
    subprocess.run(["git", "-C", str(template), "add", "."], check=True)
    subprocess.run(["git", "-C", str(template), "commit", "-qm", "fixture"], check=True)
    subprocess.run([
        "git", "-C", str(template), "remote", "add", "origin",
        "https://github.com/fixture/template.git",
    ], check=True)
    commit = subprocess.check_output(["git", "-C", str(template), "rev-parse", "HEAD"], text=True).strip()

    (root / "registry/template.json").write_text(json.dumps({
        "repository": "fixture/template",
        "method_lane": lane,
        "commit": commit,
    }))
    if stale_contract:
        files["scripts/evaluate_holdout.py"] = "0" * 64
    (root / "registry/template_contract.json").write_text(json.dumps({
        "schema": "karage1-shared-template-contract-v1",
        "repository": "fixture/template",
        "commit": commit,
        "protocol_compatible": compatible,
        "tool_sha256": files,
        "runtime_assets": runtime_assets,
        "failed_check_ids": [] if compatible else ["synthetic_failure"],
        "dynamic_contract": {
            "run": True,
            "buffer_contract_passed": True,
            "whole_selected_component_scoring_passed": True,
            "static_classification_contract_passed": True,
        },
    }))
    return template


@pytest.mark.parametrize("lane", [None, "", "  ", [], 1, False])
def test_invalid_lane_blocks_even_with_inputs_and_contract(workspace, lane):
    configure(workspace, lane)
    report = shared_tools.preflight()
    assert report["template_contract"]["passed"]
    assert not report["ready_for_shared_tools"]


def test_catalogue_is_required(workspace):
    configure(workspace, "assigned-lane", ("existing_faults.tif",))
    report = shared_tools.preflight()
    assert report["missing"] == [".cache/gems_data/existing_faults.tif"]
    assert not report["ready_for_shared_tools"]


@pytest.mark.parametrize("compatible,stale", [(False, False), (True, True)])
def test_incompatible_or_stale_shared_contract_blocks(workspace, compatible, stale):
    configure(workspace, "assigned-lane", compatible=compatible, stale_contract=stale)
    report = shared_tools.preflight()
    assert not report["template_contract"]["passed"]
    assert not report["ready_for_shared_tools"]
    assert report["template_contract"]["errors"]


def test_symlinked_runtime_asset_blocks_even_when_bytes_match(workspace):
    configure(workspace, "assigned-lane")
    asset = workspace / ".cache/gems_data/labels.tif"
    outside = workspace / "same-label-bytes.tif"
    outside.write_bytes(asset.read_bytes())
    asset.unlink()
    asset.symlink_to(outside)
    report = shared_tools.preflight()
    assert not report["template_contract"]["passed"]
    assert any("non-regular" in error for error in report["template_contract"]["errors"])


def test_dirty_checkout_or_changed_runtime_bytes_block(workspace):
    template = configure(workspace, "assigned-lane")
    (template / "untracked.py").write_text("not audited\n")
    subprocess.run([
        "git", "-C", str(template), "remote", "set-url", "origin",
        "https://evil.invalid/prefix/fixture/template.git",
    ], check=True)
    asset = workspace / ".cache/gems_data/labels.tif"
    asset.write_bytes(b"changed but same length"[:asset.stat().st_size].ljust(asset.stat().st_size, b"!"))
    report = shared_tools.preflight()
    assert not report["template_contract"]["passed"]
    errors = "\n".join(report["template_contract"]["errors"])
    assert "local modifications" in errors
    assert "origin differs" in errors
    assert "runtime asset bytes changed" in errors


@pytest.mark.parametrize("missing,code", [(('feature_stack.npy',), 1), ((), 0)])
def test_cli_exit_status_is_readiness_not_report_success(workspace, monkeypatch, capsys, missing, code):
    configure(workspace, "assigned-lane", missing)
    monkeypatch.setattr(sys, "argv", ["shared_tools.py", "preflight"])
    assert shared_tools.main() == code
    report = json.loads(capsys.readouterr().out)
    assert report["ok_to_submit"] is False
    assert report["ready_for_shared_tools"] == (code == 0)


@pytest.mark.parametrize("command", ["evaluate", "write"])
def test_blocked_execution_never_bootstraps(workspace, monkeypatch, command):
    configure(workspace, "   ")
    monkeypatch.setattr(sys, "argv", ["shared_tools.py", command])
    monkeypatch.setattr(shared_tools, "bootstrap", lambda: pytest.fail("bootstrapped blocked run"))
    with pytest.raises(SystemExit, match="BLOCKED"):
        shared_tools.main()
