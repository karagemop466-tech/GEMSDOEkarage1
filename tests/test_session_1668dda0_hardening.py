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


def test_current_local_and_peer_evidence_verifies_all_11_local_tifs():
    data = render_site.local_and_peer_evidence()
    assert data["local_downloads_count"] == 11
    assert data["peer_rasters_count"] == 9
    assert data["submit_authorized"] is False
    assert "All 11 local docs/downloads/*.tif artifacts" in data["scope"]
    actual_tifs = {f"docs/downloads/{p.name}" for p in (ROOT / "docs/downloads").glob("*.tif")}
    audited_tifs = {r["file"] for r in data["local_downloads"]}
    assert audited_tifs == actual_tifs
    assert all(r["ok_to_submit"] is False and r["literal_lattice_duplicate"] is True
               for r in (*data["local_downloads"], *data["peer_rasters"]))
    # The 2026-10-28 receipt is historical and remains byte-for-byte intact.
    import hashlib
    historical_path = ROOT / "evidence/local_downloads_and_peer_audit_20261028.json"
    old = json.loads(historical_path.read_text())
    assert hashlib.sha256(historical_path.read_bytes()).hexdigest() == "8586a93277b85ef5d860e5a5568072e8ecd19491190880f3137dcd2936e50fe0"
    assert old["local_downloads_count"] == 9 and old["peer_rasters_count"] == 9
    assert len(old["local_downloads"]) == 9 and len(old["peer_rasters"]) == 9
    kth = next(r for r in data["local_downloads"] if r["file"].endswith("unique-hyp-kth-therm-mask-20261028-zeros.tif"))
    assert kth["positive_pixels_in_footprint"] == 37654
    assert kth["lattice_dots_within_3px"] == 37617
    assert kth["lattice_directed_overlap_3px"] == pytest.approx(37617 / 37654)


def test_audit_scope_uses_current_row_counts_not_historical_constants():
    assert peer_audit.scope_description(2, 3, 4) == (
        "All 2 local docs/downloads/*.tif artifacts plus 3 SHA-pinned "
        "sibling/peer GeoTIFFs across 4 commit-pinned ecosystem repositories."
    )
    for bad in ((-1, 0, 0), (1.0, 0, 0), (True, 0, 0)):
        with pytest.raises(ValueError, match="non-negative integers"):
            peer_audit.scope_description(*bad)


def test_kth_legacy_holdout_claim_is_quarantined_and_never_promoted():
    summary = json.loads((ROOT / "docs/data/unique-hyp-kth-therm-mask-20261028-zeros.json").read_text())
    card = json.loads((ROOT / "evidence/kth_candidate_audit_20261029.json").read_text())
    legacy = json.loads((ROOT / "evidence/legacy_kth_claim_quarantine_20261029.json").read_text())
    assert summary["verdict"] == "negative" and summary["ok_to_submit"] is False
    assert summary["holdout_DTI"] is None
    assert card["verdict"] == "negative" and card["ok_to_submit"] is False
    assert card["registry_audit"]["preplacement_surface_available"] is False
    assert card["registry_audit"]["lattice_threshold_exceeded"] is True
    assert card["holdout_DTI"]["value"] is None
    fmt = card["validator_output"]
    assert fmt["mirror_grid_match"] is True
    assert fmt["metadata"]["count"] == 1 and fmt["metadata"]["dtype"] == "float32"
    assert fmt["metadata"]["crs"] == "EPSG:32611" and fmt["metadata"]["shape"] == [3730, 3292]
    assert fmt["crs_shape_transform_match"] is True
    assert fmt["metadata"]["transform"] == [100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0]
    assert fmt["no_nan_inside_footprint"] is True and fmt["no_masked_inside_footprint"] is True
    assert fmt["inside_values_in_0_1"] is True
    assert fmt["outside_all_zero"] is True and fmt["portal_acceptance"] == "not tested"
    assert card["legacy_claim_classification"] == "LEGACY-UNVERIFIED CLAIM; not accepted as a HOLDOUT-DTI result"
    assert legacy["classification"] == card["legacy_claim_classification"]
    assert legacy["fields_preserved_from_superseded_card"]["holdout_DTI"] == "0.1713"
    assert legacy["fields_preserved_from_superseded_card"]["verdict"] == "promote"
    for script in ("scripts/my_unique_experiment.py", "scripts/my_unique_experiment2.py"):
        before = (ROOT / "docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.tif").read_bytes()
        result = subprocess.run([sys.executable, script], cwd=ROOT, capture_output=True, text=True)
        assert result.returncode == 2 and "BLOCKED" in result.stderr
        assert (ROOT / "docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.tif").read_bytes() == before


def test_public_site_shows_nine_sites_current_status_and_novelty_screen():
    rows, _ = render_site.build()
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert site in rows
    assert rows.count("<tr>") == 9
    assert "USER-REPORTED / UNVERIFIED" in rows
    assert "No organizer-confirmed score or projection" in rows
    assert "worst focus pair" in rows and "lattice" in rows

    overview = render_site.home(0)
    assert "DO NOT SUBMIT" in overview and "No eligible submission file" in overview
    assert "0.3195" in overview and "0.4413" in overview and "0.4544" in overview
    assert "not authenticated" in overview.lower()
    assert "11 + 9" in overview and "No approved .tif" in overview
    assert "evidence/session_73de02e3_run_card.json" in overview

    guide = render_site.guide(1)
    assert "All 11 local download GeoTIFFs and 9 audited peer GeoTIFFs" in guide
    assert "99.9017%" in guide and "LEGACY-UNVERIFIED" in guide
    assert "No approved .tif" in guide

    research = render_site.research(1)
    for hypothesis in ("Multi-catchment bedrock-incision coherence",
                       "Focal-mechanism-consistent microseismic lineaments",
                       "Persistent InSAR deformation discontinuities"):
        assert hypothesis in research
    assert "None tested" in research and "score projections" in research
