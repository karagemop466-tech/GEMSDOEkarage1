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


def test_local_and_peer_evidence_verifies_original_receipt_and_later_tif_cards():
    data = render_site.local_and_peer_evidence()
    assert data["local_downloads_count"] == 9
    assert data["peer_rasters_count"] == 9
    actual_tifs = {f"docs/downloads/{p.name}" for p in (ROOT / "docs/downloads").glob("*.tif")}
    audited_tifs = {r["file"] for r in data["local_downloads"]}
    # Session 1668dda0's receipt is historical and must not be rewritten.
    # Any TIF added afterwards must be covered by a later session audit:
    # 147b0f11's SGMC re-audit covers the new DIPDUAL raster (run card
    # evidence/run_card_dipdual_20261028.json, verdict negative).
    later = json.loads((ROOT / "evidence/local_candidates_sgmc_audit_20261028.json").read_text())
    later_tifs = {f"docs/downloads/{r['file']}" for r in later["candidates"]}
    # Session 1d15747e's K1-HGRID-STRAIN build receipts cover its own TIF (validator, reread,
    # uniqueness and run card are all written by the same stage; see evidence/hgridge_e3_build_*.json).
    for receipt in sorted((ROOT / "evidence").glob("hgridge_e3_build_*.json")):
        later_tifs.add(json.loads(receipt.read_text())["file"])
    # Saved-byte receipts written by scripts/audit_local_tif.py (session 1d15747e) cover
    # TIFs that predate any audit, e.g. docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.tif.
    for receipt in sorted((ROOT / "evidence").glob("audit_*.json")):
        data = json.loads(receipt.read_text())
        if data.get("schema") == "karage1-local-tif-audit-v1":
            later_tifs.add(data["file"])
    # Session 2026-10-29 re-audited every local TIF (including unique-hyp-kth-therm-mask)
    # with the shared audit script; see evidence/local_downloads_audit_20261029.json.
    fleet = json.loads((ROOT / "evidence/local_downloads_audit_20261029.json").read_text())
    later_tifs |= {r["file"] for r in fleet["local_downloads"]}
    # Two additional mainline files were committed after the fleet receipt. Their
    # own negative run cards bind the saved TIFF bytes; neither is a clearance.
    import hashlib
    separate_cards = {
        "docs/downloads/gems-karage1-unique-novelterritory-20261029T120000Z-5a6b7c8d-zeros.tif":
            "evidence/run_card_gems-karage1-unique-novelterritory-20261029T120000Z-5a6b7c8d.json",
        "docs/downloads/karage1-convect-cell-upflow-20261029-zeros.tif":
            "evidence/session_convect_20261029_run_card.json",
    }
    for tif, card_path in separate_cards.items():
        card = json.loads((ROOT / card_path).read_text())
        expected = card.get("raster_sha256") or card["raster"]["sha256"]
        assert hashlib.sha256((ROOT / tif).read_bytes()).hexdigest() == expected
        assert card["ok_to_submit"] is False and "negative" in card["verdict"].lower()
        later_tifs.add(tif)
    uncovered = actual_tifs - audited_tifs - later_tifs
    assert not uncovered, f"local TIFs with no saved-byte audit: {sorted(uncovered)}"
    assert audited_tifs <= actual_tifs
