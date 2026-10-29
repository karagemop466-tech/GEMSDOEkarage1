"""Regression guards added 2026-10-29 after a false 'CLEARED FOR SUBMISSION' page
(and its unaudited 'promote' raster card) was found committed on main.

These tests never grant clearance. They only ensure that no published page
claims a file is OK to submit, and that private-fork experiment scripts stay
fail-closed.
"""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_CLEARANCE_PHRASES = (
    "CLEARED FOR SUBMISSION",
    "IT IS OK TO DOWNLOAD AND SUBMIT",
)


def _published_pages():
    pages = [ROOT / "index.html", ROOT / "executive-summary.html", ROOT / "legacy-overview.html"]
    pages += sorted((ROOT / "docs").glob("**/*.html"))
    return [p for p in pages if p.is_file()]


@pytest.mark.parametrize("phrase", FORBIDDEN_CLEARANCE_PHRASES)
def test_no_published_page_claims_clearance(phrase):
    offenders = [str(p.relative_to(ROOT)) for p in _published_pages()
                 if phrase in p.read_text(encoding="utf-8", errors="replace")]
    assert not offenders, f"published pages claim clearance: {offenders}"


def test_unaudited_unique_hyp_raster_is_not_in_public_downloads():
    public = list((ROOT / "docs" / "downloads").glob("unique-hyp-kth-therm-mask-*"))
    assert public == [], "quarantined raster must not be publicly downloadable"
    quarantine = ROOT / "archive" / "quarantine" / "unique-hyp-kth-therm-mask-20261028"
    assert (quarantine / "QUARANTINE.md").is_file()


@pytest.mark.parametrize("command", [
    ["scripts/my_unique_experiment.py"],
    ["scripts/my_unique_experiment2.py"],
])
def test_private_fork_experiments_fail_closed(command):
    before = sorted(p.as_posix() for p in (ROOT / "docs" / "downloads").glob("*"))
    result = subprocess.run([sys.executable, *command], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 2
    assert "BLOCKED" in result.stderr
    after = sorted(p.as_posix() for p in (ROOT / "docs" / "downloads").glob("*"))
    assert before == after
