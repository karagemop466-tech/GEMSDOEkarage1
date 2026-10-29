from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_parallel_gse_artifact_is_hash_bound_and_not_submission_cleared():
    card = json.loads((ROOT / "evidence/run_card_gse_exp1.json").read_text())
    saved = json.loads((ROOT / "evidence/gse_saved_byte_audit_20261029.json").read_text())
    filename = card["raster"]["zeros_tif"]
    path = ROOT / "docs/downloads" / filename
    assert hashlib.sha256(path.read_bytes()).hexdigest() == card["raster"]["sha256"]
    assert card["ok_to_submit"] is False
    assert card["verdict"] == "negative"
    assert card["holdout_dti"]["value"] is None
    assert saved["registry_complete"] is False
    assert saved["upload_authorized"] is False
    candidate = next(row for row in saved["candidates"] if row["file"].endswith(Path(filename).name))
    lattice = next(row for row in candidate["comparisons"] if row["reference"] == "lattice")
    assert lattice["candidate_dots_within_3px"] == 23979
    assert lattice["candidate_dots"] == 24000
    assert lattice["overlap_exceeds_70_percent"] is True
    assert candidate["verdict"] == "duplicate"


def test_current_site_keeps_gse_status_explicitly_research_only():
    review = (ROOT / "knowledge/session-review-arena-b2b18800-2026-10-29.md").read_text()
    readme = (ROOT / "README.md").read_text()
    summary = (ROOT / "docs/executive-summary.html").read_text()
    assert "23,979 / 24,000" in review
    assert "DO NOT SUBMIT" in readme and "GSE artifact" in readme
    assert "DO NOT SUBMIT" in summary
    assert "no file is OK to download and submit" in summary or "No file is cleared" in summary


def test_quarantined_gse_builder_fails_closed_without_rewriting_artifacts():
    inputs = [
        ROOT / "docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif",
        ROOT / "docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-nan.tif",
        ROOT / "evidence/run_card_gse_exp1.json",
    ]
    before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs]
    result = subprocess.run(
        [sys.executable, "scripts/build_gse_submission.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    assert [hashlib.sha256(path.read_bytes()).hexdigest() for path in inputs] == before
