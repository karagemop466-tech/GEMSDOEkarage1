"""Regression checks for the 2026-10-29 fail-closed review."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_historical_kth_candidate_is_quarantined_and_never_promoted():
    stem = "unique-hyp-kth-therm-mask-20261028-zeros"
    record = json.loads((ROOT / f"docs/data/{stem}.json").read_text())
    artifact_dir = ROOT / "archive/negative-candidates/unique-hyp-kth-therm-mask-20261028"
    raster = artifact_dir / f"{stem}.tif"
    zip_path = artifact_dir / f"{stem}.zip"
    assert record["verdict"] == "negative"
    assert record["ok_to_submit"] is False
    assert record["historical_holdout_claim"]["value"] is None
    assert record["registry_comparison"]["status"].startswith("unknown")
    assert hashlib.sha256(raster.read_bytes()).hexdigest() == record["raster_sha256"]
    assert hashlib.sha256(zip_path.read_bytes()).hexdigest() == record["zip_sha256"]
    assert not (ROOT / f"docs/downloads/{stem}.tif").exists()
    assert not (ROOT / f"docs/downloads/{stem}.zip").exists()


def test_generated_executive_summary_has_no_false_green_light():
    page = (ROOT / "docs/executive-summary.html").read_text().lower()
    assert "do not submit" in page
    assert "unique-hyp-kth-therm-mask-20261028-zeros.tif" in page
    assert "quarantined for audit only" in page
    assert "cleared for submission" not in page
    assert "submit this file" not in page


def test_quarantined_runner_has_valid_python_and_protocol_error():
    import ast
    source = (ROOT / "scripts/run_karage1_experiments.py").read_text()
    ast.parse(source)
    assert "raise RuntimeError(" in source
    assert "pre-placement literal registry gate" in source
