"""Session 1668dda0 regressions: vacuous-outside validator closure, PR #42 retraction, and peer/local audit gates."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio import Affine

from scripts import audit_local_and_peer_rasters as peer_audit
from scripts import audit_references as ref_audit
from scripts import render_site
from scripts.validate_geotiff import diagnose

ROOT = Path(__file__).resolve().parents[1]


def _write_tif(path: Path, arr: np.ndarray, nodata=None) -> None:
    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        height=arr.shape[0],
        width=arr.shape[1],
        count=1,
        dtype="float32",
        crs="EPSG:32611",
        transform=Affine(100.0, 0.0, 0.0, 0.0, -100.0, 800.0),
        nodata=nodata,
    ) as ds:
        ds.write(arr.astype("float32"), 1)


def test_raster_checks_never_marks_empty_outside_as_all_nan():
    arr = np.zeros((4, 4), dtype=np.float32)
    fp = np.ones((4, 4), dtype=bool)
    meta = {
        "driver": "GTiff",
        "dtype": "float32",
        "shape": [4, 4],
        "crs": "EPSG:32611",
        "transform": [100.0, 0.0, 0.0, 0.0, -100.0, 400.0],
        "nodata_is_nan": False,
    }
    checks = ref_audit.raster_checks(arr, meta, meta, fp)
    assert checks["outside_all_nan"] is False


def test_validate_geotiff_rejects_all_finite_bogus_template(tmp_path):
    bogus_template = tmp_path / "all_finite_zeros.tif"
    candidate = tmp_path / "candidate.tif"
    _write_tif(bogus_template, np.zeros((6, 6), dtype=np.float32), nodata=None)
    cand = np.zeros((6, 6), dtype=np.float32)
    cand[0, 0] = 1.0
    _write_tif(candidate, cand, nodata=None)
    with pytest.raises(ValueError, match="empty or has no outside"):
        diagnose(candidate, bogus_template)
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts/validate_geotiff.py"), str(candidate), "--template", str(bogus_template)],
        capture_output=True,
        text=True,
    )
    assert run.returncode == 2
    assert "empty or has no outside" in run.stderr


def test_validate_geotiff_cli_exits_1_when_outside_has_unmasked_positives(tmp_path):
    template_arr = np.zeros((6, 6), dtype=np.float32)
    template_arr[0, :] = np.nan
    cand_arr = np.zeros((6, 6), dtype=np.float32)
    cand_arr[0, 2] = 0.75  # outside footprint positive!
    cand_arr[3, 3] = 1.0   # inside footprint positive
    template_path = tmp_path / "template.tif"
    cand_path = tmp_path / "cand.tif"
    out_path = tmp_path / "diag.json"
    _write_tif(template_path, template_arr, nodata=np.nan)
    _write_tif(cand_path, cand_arr, nodata=None)
    run = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/validate_geotiff.py"),
            str(cand_path),
            "--template",
            str(template_path),
            "--out",
            str(out_path),
        ],
        capture_output=True,
        text=True,
    )
    assert run.returncode == 1
    report = json.loads(out_path.read_text())
    assert report["checks"]["outside_unmasked_positive_count"] == 1
    assert report["diagnostics"]["grid_and_inside_pass"] is True
    assert report["diagnostics"]["outside_encoding_accepted"] is False
    assert report["submission_authorized"] is False


@pytest.mark.parametrize("script_rel,flag", [
    ("scripts/audit_references.py", "--manifest"),
    ("scripts/audit_local_and_peer_rasters.py", "--peer-pins"),
])
@pytest.mark.parametrize("alias_kind", ["same", "symlink", "hardlink"])
def test_audit_clis_refuse_to_overwrite_manifests(tmp_path, script_rel, flag, alias_kind):
    manifest = tmp_path / "manifest.json"
    original = (
        (ROOT / "registry/reference_assets.json").read_bytes()
        if flag == "--manifest"
        else (ROOT / "registry/peer_ecosystem_pins.json").read_bytes()
    )
    manifest.write_bytes(original)
    if alias_kind == "same":
        out = manifest
    elif alias_kind == "symlink":
        out = tmp_path / "link.json"
        out.symlink_to(manifest)
    else:
        out = tmp_path / "hard.json"
        os.link(manifest, out)
    run = subprocess.run(
        [sys.executable, str(ROOT / script_rel), flag, str(manifest), "--out", str(out)],
        capture_output=True,
        text=True,
    )
    assert run.returncode == 2
    assert "must not overwrite" in run.stderr
    assert manifest.read_bytes() == original


def test_peer_pins_validation_rejects_bad_scores_and_duplicates(tmp_path):
    base = json.loads((ROOT / "registry/peer_ecosystem_pins.json").read_text())
    p = tmp_path / "pins.json"
    p.write_text(json.dumps(base))
    assert len(peer_audit.load_peer_pins(p)["rasters"]) == 9

    for mut in (
        lambda d: d["rasters"][0].update(user_reported_score=True),
        lambda d: d["rasters"][0].update(user_reported_score=1.2),
        lambda d: d["rasters"][0].update(ref="main"),
        lambda d: d["rasters"][0].update(path="../escape.tif"),
        lambda d: d["user_reported_leaderboard_context"][0].update(evidence_class="ORGANIZER-CONFIRMED"),
        lambda d: d["user_reported_leaderboard_context"][0].update(artifact_available=True),
    ):
        copy = json.loads(json.dumps(base))
        mut(copy)
        p.write_text(json.dumps(copy))
        with pytest.raises(ValueError):
            peer_audit.load_peer_pins(p)

    p.write_text('{"schema":"karage1-peer-ecosystem-pins-v1","schema":"dup"}')
    with pytest.raises(ValueError, match="duplicate JSON key"):
        peer_audit.load_peer_pins(p)


def test_pr42_sidecars_and_all_repo_jsons_remain_fail_closed():
    sidecar = json.loads((ROOT / "docs/downloads/karage1-unique-alteration-dots-20261028-zeros.json").read_text())
    val = json.loads((ROOT / "docs/downloads/karage1-unique-alteration-dots-20261028-zeros.validate.json").read_text())
    card = json.loads((ROOT / "evidence/run_card_unique_tif_20261028.json").read_text())
    session_card = json.loads((ROOT / "evidence/session_1668dda0_run_card.json").read_text())

    assert sidecar["ok_to_submit"] is False and sidecar["verdict"] == "negative" and sidecar["superseded"] is True
    assert sidecar["outside_unmasked_positive_pixels"] == 2113
    assert val["checks"]["outside_unmasked_positive_count"] == 2113
    assert val["diagnostics"]["outside_encoding_accepted"] is False
    assert val["submission_authorized"] is False
    assert card["ok_to_submit"] is False and card["verdict"] == "negative" and card["superseded"] is True
    assert session_card["ok_to_submit"] is False and session_card["verdict"] == "negative"
    assert len(session_card["submission_note"]) <= 140

    # Zero JSON files anywhere in docs/, evidence/, or registry/ may assert authorization.
    def _find_true_flags(obj, prefix=""):
        found = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                cur = f"{prefix}.{k}" if prefix else k
                if k in ("ok_to_submit", "submit_authorized", "submission_authorized", "submission_ready") and v is True:
                    found.append(cur)
                found.extend(_find_true_flags(v, cur))
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                found.extend(_find_true_flags(item, f"{prefix}[{idx}]"))
        return found

    for folder in ("docs", "evidence", "registry"):
        for json_path in sorted((ROOT / folder).rglob("*.json")):
            hits = _find_true_flags(json.loads(json_path.read_text()))
            assert not hits, f"{json_path} contains true authorization flags: {hits}"


def test_local_and_peer_evidence_verifies_all_current_local_tifs():
    data = render_site.local_and_peer_evidence()
    actual_tifs = {f"docs/downloads/{p.name}" for p in (ROOT / "docs/downloads").glob("*.tif")}
    audited_tifs = {r["file"] for r in data["local_downloads"]}
    assert data["local_downloads_count"] == len(actual_tifs) == 11
    assert data["peer_rasters_count"] == 9
    assert audited_tifs == actual_tifs
    assert data["all_local_downloads_blocked"] is True
    assert all(r["literal_lattice_duplicate"] and not r["ok_to_submit"] for r in data["local_downloads"])
    tracked = data["tracked_tiff_inventory"]
    assert tracked["tracked_tiff_paths_count"] == 15
    assert tracked["unique_tracked_tiff_sha256_count"] == 13
    assert tracked["tracked_download_directory_paths_count"] == 11
    assert tracked["tracked_quarantined_archive_paths_count"] == 4
    assert tracked["all_tracked_tiff_bytes_accounted"] is True
    assert tracked["unaccounted_paths"] == []
    assert all(row["audit_coverage"] != "UNACCOUNTED" for row in tracked["tracked_tiffs"])

    # Keep the earlier nine-local audit immutable and explicitly historical.
    old = json.loads((ROOT / "evidence/local_downloads_and_peer_audit_20261028.json").read_text())
    assert old["local_downloads_count"] == 9 and old["peer_rasters_count"] == 9
    assert len(render_site.secondary_evidence()['rows']) == 12


def test_unique_hyp_legacy_promotion_and_score_claim_are_superseded():
    card = render_site.unique_hyp_evidence()
    assert card['verdict'] == 'negative' and card['ok_to_submit'] is False
    assert card['holdout_dti']['label'] == 'HOLDOUT-DTI'
    assert card['holdout_dti']['dti'] is None and card['holdout_dti']['ci95'] is None
    assert card['holdout_dti']['evaluator_version'] is None
    assert card['holdout_dti']['withheld_positive_count'] is None
    assert card['legacy_claim_retraction']['reportable_holdout_result'] is None
    assert card['validator_output']['inside_values_finite_and_in_0_1'] is True
    assert card['validator_output']['organizer_acceptance'] == 'not tested'
    assert len(card['submission_note']) <= 140 and card['submission_note_chars'] == len(card['submission_note'])
    assert card['registry_correlation_overlap']['lattice']['directed_overlap'] > .70
    assert card['registry_correlation_overlap']['nine_focus_sites']['distinct_from_each_under_audited_thresholds'] is True
    assert card['registry_correlation_overlap']['complete_registry_checked'] is False
    assert card['slot_selected_or_spent'] is False
    assert card['leakage_canary']['status'] == 'NOT RUN'
    assert card['leakage_canary']['single_feature_auc_leakage_threshold'] == 0.90
    assert card['protocol_holdout_spec']['status'] == 'NOT RUN'
    assert card['protocol_holdout_spec']['alpha'] == 0.2 and card['protocol_holdout_spec']['beta'] == 0.8
    assert card['protocol_holdout_spec']['triangular_kernel_radius_m'] == 300
    assert card['experiment_budget']['geological_experiments_this_session'] == 0
    assert card['tracked_tiff_inventory']['tracked_tiff_paths_count'] == 15
    assert card['tracked_tiff_inventory']['unique_tracked_tiff_sha256_count'] == 13
    assert card['tracked_tiff_inventory']['all_tracked_tiff_bytes_accounted'] is True
    assert card['tracked_tiff_inventory']['unaccounted_paths'] == []
