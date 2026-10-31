"""Regression for scripts/nine_site_format_receipt.py (skips without restored core data)."""
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample_submission.tif"
LABELS = ROOT / "data" / "labels.tif"

pytestmark = pytest.mark.skipif(
    not (SAMPLE.exists() and LABELS.exists()),
    reason="core data not restored (scripts/restore_karage1_data.py --group core)",
)


def test_receipt_invariants():
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from nine_site_format_receipt import build_receipt

    r = build_receipt()
    assert r["submission_authorized"] is False
    sites = {s["site"]: s for s in r["sites"]}
    assert set(sites) == {f"GEMSDOE{n}" for n in (24, 25, 27, 28, 30, 31, 32, 33, 36)}
    for s in sites.values():
        assert s["nan_inside_footprint"] == 0
        assert s["nonzero_outside_footprint"] == 0
        assert s["checks"]["crs_shape_transform_match_mirror"] is True
        assert s["checks"]["no_nonfinite_inside"] is True
        assert s["checks"]["inside_values_in_0_1"] is True
        assert s["submission_authorized"] is False
        assert s["outside_encoding"] in {"nan", "zero"}
    # Two encodings are present, and the mirror sample uses NaN outside.
    assert {s["outside_encoding"] for s in sites.values()} == {"nan", "zero"}
    assert r["subset_check"]["child_is_strict_subset_of_parent"] is True
    assert r["subset_check"]["parent_only_positives"] == 6436
    # Irregularity under review: the mirrored sample is not "total fault absence".
    assert r["sample_vs_labels"]["positives_identical"] is True
    assert r["sample_vs_labels"]["sample_positives"] > 0
