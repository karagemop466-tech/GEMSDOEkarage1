from __future__ import annotations

from scripts.render_site import gse_research_evidence, home, guide


def test_parallel_gse_artifact_is_hash_bound_and_not_submission_cleared():
    card, raster, original_receipt, saved_audit, saved_row = gse_research_evidence()
    assert raster.name == card["submission_name"]
    assert card["ok_to_submit"] is False
    assert card["verdict"] == "negative"
    assert card["holdout_dti"]["value"] is None
    assert original_receipt["candidate_sha256"] == card["raster"]["sha256"]
    assert len(original_receipt["results"]) == 11
    assert saved_audit["registry_complete"] is False
    assert len(saved_row["comparisons"]) == 10
    lattice = next(row for row in saved_row["comparisons"] if row["reference"] == "lattice")
    assert lattice["candidate_dots_within_3px"] == 23979
    assert lattice["candidate_dots"] == 24000
    assert lattice["overlap_exceeds_70_percent"] is True
    assert saved_row["verdict"] == "duplicate"


def test_pages_show_gse_as_research_only_and_report_saved_byte_gate():
    overview = home(1)
    submission_guide = guide(1)
    filename = "karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif"

    assert filename in overview
    assert "DO NOT SUBMIT" in overview
    assert "99.9125%" in overview
    assert "HOLDOUT-DTI not run" in overview
    assert "DO NOT SUBMIT" in submission_guide
    assert filename in submission_guide
    assert "Download research raster only" in submission_guide
    assert "OK TO DOWNLOAD AND SUBMIT" not in overview
    assert "OK TO DOWNLOAD AND SUBMIT" not in submission_guide


def test_quarantined_gse_builder_fails_closed_without_rewriting_artifacts():
    import hashlib
    import subprocess
    import sys
    from pathlib import Path

    root = Path(__file__).resolve().parents[1]
    inputs = [
        root / "docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif",
        root / "docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-nan.tif",
        root / "evidence/run_card_gse_exp1.json",
    ]
    before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs]
    result = subprocess.run(
        [sys.executable, "scripts/build_gse_submission.py"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs] == before
