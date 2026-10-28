from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio import Affine
from scipy.stats import spearmanr

from scripts import audit_references as audit
from scripts import preflight


def test_disk_is_closed_and_euclidean():
    d = audit.disk(3)
    assert d.shape == (7, 7)
    assert d[3, 6] and d[6, 3]  # exactly 3 pixels is included
    assert d[5, 5]  # sqrt(8) <= 3
    assert not d[6, 4] and not d[6, 6]  # sqrt(10) and sqrt(18) > 3
    assert d.sum() == 29
    with pytest.raises(ValueError):
        audit.disk(-1)


def test_feasibility_is_exact_at_the_strict_boundary():
    assert audit.minimum_overlap(10, 3)["minimum_fraction"] == 0.7
    assert not audit.minimum_overlap(10, 3)["necessarily_exceeds_limit"]
    assert audit.minimum_overlap(11, 3)["necessarily_exceeds_limit"]
    assert audit.minimum_overlap(2, 3)["minimum_fraction"] == 0
    assert audit.minimum_overlap(37654, 6649)["maximum_dots_not_ruled_out"] == 22163
    assert audit.minimum_overlap(1, 0, Fraction(1))["maximum_dots_not_ruled_out"] is None
    for bad_dots, bad_uncovered in [(0, 0), (-1, 1), (1, -1), (1.2, 1)]:
        with pytest.raises(ValueError):
            audit.minimum_overlap(bad_dots, bad_uncovered)
    with pytest.raises(ValueError):
        audit.minimum_overlap(1, 0, Fraction(3, 2))


def test_binary_rank_correlation_matches_scipy_with_ties_and_mask():
    rng = np.random.default_rng(123)
    a = rng.random((10, 12)) < .2
    b = rng.random((10, 12)) < .4
    mask = rng.random((10, 12)) < .8
    got = audit.binary_rank_correlation(a, b, mask)
    assert got == pytest.approx(spearmanr(a[mask], b[mask]).statistic)
    assert audit.binary_rank_correlation(a, a, mask) == pytest.approx(1)
    assert audit.binary_rank_correlation(a, ~a, mask) == pytest.approx(-1)
    assert audit.binary_rank_correlation(np.zeros_like(a), b, mask) is None
    with pytest.raises(ValueError):
        audit.binary_rank_correlation(a, b[:2], mask)


def test_format_reports_nan_outside_and_strict_range_separately():
    arr = np.array([[0., 1., np.nan], [0.1, 0.5, np.nan]], dtype=np.float32)
    fp = np.isfinite(arr)
    meta = {"driver": "GTiff", "dtype": "float32", "shape": [2, 3], "crs": "EPSG:32611", "transform": [100., 0., 0., 0., -100., 0.], "nodata_is_nan": True}
    x = audit.raster_checks(arr, meta, meta, fp)
    assert x["mirror_grid_and_inside_values_pass"]
    assert x["outside_all_nan"]
    assert not x["whole_array_strict_finite_0_1"]
    arr[0, 0] = np.nan
    x = audit.raster_checks(arr, meta, meta, fp)
    assert not x["no_nonfinite_inside"] and not x["inside_values_in_0_1"]
    arr[0, 0] = -0.01
    x = audit.raster_checks(arr, meta, meta, fp)
    assert x["out_of_range_inside_count"] == 1
    assert not x["mirror_grid_and_inside_values_pass"]
    arr[0, 0] = 0
    arr[~fp] = 0
    x = audit.raster_checks(arr, meta, meta, fp)
    assert x["whole_array_strict_finite_0_1"] and not x["outside_all_nan"]
    assert x["portal_acceptance"] == "not tested"


def test_binary_support_fails_on_nonbinary_nonfinite_and_shape():
    mask = np.ones((2, 2), bool)
    for data in (np.array([[0, 1], [.5, 1]]), np.array([[0, 1], [np.nan, 1]])):
        with pytest.raises(ValueError):
            audit.binary_support(data, mask, "x")


def test_manifest_requires_distinct_pinned_safe_entries(tmp_path):
    original = json.loads((audit.ROOT / "registry/reference_assets.json").read_text())
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(original))
    assert len(audit.load_manifest(path)) == 12
    for mutate in (
        lambda x: x.append(x[0]),
        lambda x: x[0].update(ref="main"),
        lambda x: x[0].update(path="../secret"),
        lambda x: x[0].update(sha256="bad"),
        lambda x: x[0].update(repo="evil/example"),
    ):
        data = json.loads(json.dumps(original))
        mutate(data)
        path.write_text(json.dumps(data))
        with pytest.raises(ValueError):
            audit.load_manifest(path)


def _write(path: Path, a: np.ndarray, dtype: str, nodata):
    with rasterio.open(path, "w", driver="GTiff", height=a.shape[0], width=a.shape[1], count=1,
                       dtype=dtype, crs="EPSG:32611", transform=Affine(100, 0, 0, 0, -100, 800), nodata=nodata) as ds:
        ds.write(a.astype(dtype), 1)


def test_audit_small_end_to_end_and_tamper_detection(tmp_path):
    fp = np.ones((8, 8), bool)
    fp[0] = False
    labels = np.zeros((8, 8), np.int8)
    labels[3, 3] = 1
    labels[~fp] = -1
    sample = np.where(fp, (labels == 1).astype(np.float32), np.nan)
    grid = np.where(fp, 0., np.nan).astype(np.float32)
    grid[3, 3] = 1
    entries = []
    for key in sorted(audit.REQUIRED):
        arr = labels if key == "labels" else sample if key == "template" else grid
        path = tmp_path / f"{key}.tif"
        _write(path, arr, "int8" if key == "labels" else "float32", -1 if key == "labels" else np.nan)
        entries.append({"id": key, "bytes": path.stat().st_size, "sha256": audit.sha256(path)})
    out = audit.audit(entries, tmp_path)
    assert out["sample_positive_mask_equals_label"]
    assert out["all_72_directed_pairs_exceed_70_percent"]
    assert len(out["directed_pairs"]) == 72
    assert out["submit_authorized"] is False
    assert out["rows"]["GEMSDOE24"]["format_diagnostics"]["outside_all_nan"]
    (tmp_path / "GEMSDOE24.tif").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="checksum or size mismatch"):
        audit.audit(entries, tmp_path)


def test_preflight_is_negative_with_missing_or_malformed_inputs():
    for value in (None, {}, {"lattice": "bad"}, {"lattice": {"coverage_fraction": float("nan")}},
                  {"lattice": {"champion_sized_budget_bound": {"minimum_fraction": .2, "necessarily_exceeds_limit": True}}}):
        card = preflight.run_card(value)
        assert card["verdict"] == "negative"
        assert not card["ok_to_submit"] and not card["download_available"]
        assert card["raster_sha256"] is None and card["holdout_dti"]["ci95"] is None
        json.dumps(card, allow_nan=False)
        assert any("unavailable or invalid" in r for r in card["blockers"])


def test_preflight_cli_fails_closed_when_audit_missing(tmp_path):
    import subprocess
    import sys
    out = tmp_path / "blocked.json"
    run = subprocess.run([sys.executable, str(audit.ROOT / "scripts/preflight.py"),
                          "--audit", str(tmp_path / "not-present.json"), "--out", str(out)],
                         capture_output=True, text=True)
    assert run.returncode == 1
    card = json.loads(out.read_text())
    assert card["verdict"] == "negative" and card["ok_to_submit"] is False
    assert card["correlation_overlap_vs_registry"]["lattice_coverage_fraction"] is None


def test_manifest_malformed_entry_fails_cleanly(tmp_path):
    x = json.loads((audit.ROOT / "registry/reference_assets.json").read_text())
    x[0]["id"] = ["unhashable"]
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(x))
    with pytest.raises(ValueError):
        audit.load_manifest(path)
    with pytest.raises(ValueError):
        audit.minimum_overlap(True, 1)


def test_candidate_format_diagnostic_separates_outside_policies(tmp_path):
    from scripts.validate_geotiff import diagnose
    fp = np.ones((8, 8), bool); fp[0] = False
    template = np.where(fp, 0., np.nan).astype(np.float32)
    nan_candidate = template.copy(); nan_candidate[3, 3] = 1
    zero_candidate = np.nan_to_num(nan_candidate, nan=0)
    template_path, nan_path, zero_path = (tmp_path / x for x in ("sample.tif", "nan.tif", "zero.tif"))
    _write(template_path, template, "float32", np.nan)
    _write(nan_path, nan_candidate, "float32", np.nan)
    _write(zero_path, zero_candidate, "float32", None)
    nan_result = diagnose(nan_path, template_path, audit.sha256(template_path))
    assert nan_result["diagnostics"]["nan_outside_variant_pass"]
    assert not nan_result["diagnostics"]["strict_whole_array_variant_pass"]
    zero_result = diagnose(zero_path, template_path)
    assert zero_result["diagnostics"]["strict_whole_array_variant_pass"]
    assert not zero_result["diagnostics"]["nan_outside_variant_pass"]
    assert not zero_result["submission_authorized"]
    assert not zero_result["template_hash_matched_requested_pin"]
    with pytest.raises(ValueError, match="template SHA-256 mismatch"):
        diagnose(zero_path, template_path, "0" * 64)
    zero_candidate[2, 2] = 1.1
    _write(zero_path, zero_candidate, "float32", None)
    assert not diagnose(zero_path, template_path)["diagnostics"]["grid_and_inside_pass"]


def test_candidate_diagnostic_masks_finite_nodata_and_rejects_masked_inside(tmp_path):
    from scripts.validate_geotiff import diagnose
    template = np.ones((8, 8), np.float32); template[0] = -9999
    candidate = np.zeros((8, 8), np.float32); candidate[0] = -9999
    template_path, candidate_path = tmp_path / "sample.tif", tmp_path / "candidate.tif"
    _write(template_path, template, "float32", -9999)
    _write(candidate_path, candidate, "float32", -9999)
    result = diagnose(candidate_path, template_path)
    assert result["diagnostics"]["null_or_nan_outside_variant_pass"]
    assert not result["diagnostics"]["nan_outside_variant_pass"]
    assert not result["diagnostics"]["strict_whole_array_variant_pass"]
    candidate[3, 3] = -9999
    _write(candidate_path, candidate, "float32", -9999)
    result = diagnose(candidate_path, template_path)
    assert result["checks"]["masked_inside_count"] == 1
    assert not result["diagnostics"]["grid_and_inside_pass"]


def test_candidate_diagnostic_forbids_unmasked_positive_outside_in_strict_variant(tmp_path):
    from scripts.validate_geotiff import diagnose
    template = np.zeros((8, 8), np.float32); template[0] = np.nan
    prediction = np.zeros((8, 8), np.float32); prediction[0, 3] = .2
    template_path, prediction_path = tmp_path / "sample.tif", tmp_path / "prediction.tif"
    _write(template_path, template, "float32", np.nan)
    _write(prediction_path, prediction, "float32", None)
    result = diagnose(prediction_path, template_path)
    assert result["checks"]["outside_unmasked_positive_count"] == 1
    assert not result["diagnostics"]["strict_whole_array_variant_pass"]


def test_concurrent_comparison_strict_threshold_and_shape():
    from scripts.audit_concurrent import compare_binary_support
    fp = np.ones((1, 21), bool)
    candidate = np.zeros_like(fp); candidate[0, [0, 2, 4, 6, 8, 10, 12, 14, 16, 20]] = True
    reference = np.zeros_like(fp); reference[0, [0, 6, 12]] = True
    result = compare_binary_support(candidate, reference, fp)
    assert result["within_3px_count"] == 8
    assert result["strictly_exceeds_70_percent"]
    assert -1 <= result["binary_support_spearman"] <= 1
    with pytest.raises(ValueError):
        compare_binary_support(candidate, reference[:, :-1], fp)


def test_concurrent_source_is_pinned_before_fetch():
    from scripts.audit_concurrent import validate_source
    source = json.loads((audit.ROOT / "registry/concurrent_asset.json").read_text())
    validate_source(source)
    source["ref"] = "0" * 40
    with pytest.raises(ValueError):
        validate_source(source)


def test_format_diagnostic_cli_rejects_invalid_range(tmp_path):
    import subprocess
    import sys
    template = np.zeros((8, 8), np.float32); template[0] = np.nan
    candidate = np.zeros((8, 8), np.float32); candidate[3, 3] = 1.1
    sample, tif, output = (tmp_path / x for x in ("sample.tif", "bad.tif", "result.json"))
    _write(sample, template, "float32", np.nan)
    _write(tif, candidate, "float32", None)
    run = subprocess.run([sys.executable, str(audit.ROOT / "scripts/validate_geotiff.py"),
                          str(tif), "--template", str(sample), "--out", str(output)],
                         capture_output=True, text=True)
    assert run.returncode == 1
    result = json.loads(output.read_text())
    assert not result["diagnostics"]["grid_and_inside_pass"]
    assert not result["submission_authorized"]


@pytest.mark.parametrize('alias', ['candidate', 'template', 'candidate_symlink', 'template_hardlink'])
def test_format_diagnostic_cannot_replace_input(tmp_path, alias):
    import os
    import subprocess
    import sys
    template = np.zeros((8, 8), np.float32); template[0] = np.nan
    candidate = np.zeros((8, 8), np.float32)
    sample, tif = tmp_path / 'sample.tif', tmp_path / 'candidate.tif'
    _write(sample, template, 'float32', np.nan)
    _write(tif, candidate, 'float32', None)
    inputs = {p: p.read_bytes() for p in (sample, tif)}
    if alias == 'candidate':
        output = tif
    elif alias == 'template':
        output = sample
    elif alias == 'candidate_symlink':
        output = tmp_path / 'alias.tif'
        output.symlink_to(tif)
    else:
        output = tmp_path / 'hardlink.tif'
        os.link(sample, output)
    run = subprocess.run([sys.executable, str(audit.ROOT / 'scripts/validate_geotiff.py'),
                          str(tif), '--template', str(sample), '--out', str(output)],
                         capture_output=True, text=True)
    assert run.returncode == 2
    assert 'must not overwrite candidate or template' in run.stderr
    assert all(p.read_bytes() == b for p, b in inputs.items())


def test_format_cli_defaults_to_strict_and_inside_only_is_explicit(tmp_path):
    import subprocess
    import sys
    template = np.zeros((8, 8), np.float32); template[0] = np.nan
    sample, candidate = tmp_path / 'sample.tif', tmp_path / 'candidate.tif'
    _write(sample, template, 'float32', np.nan)
    _write(candidate, template, 'float32', np.nan)
    command = [sys.executable, str(audit.ROOT / 'scripts/validate_geotiff.py'),
               str(candidate), '--template', str(sample)]
    strict = subprocess.run(command, capture_output=True, text=True)
    assert strict.returncode == 1
    report = json.loads(strict.stdout)
    assert report['diagnostics']['grid_and_inside_pass']
    assert report['cli_exit_check'] == 'strict_whole_array_variant_pass'
    assert not report['cli_exit_check_passed'] and not report['submission_authorized']
    weak = subprocess.run(command + ['--require-inside-only'], capture_output=True, text=True)
    assert weak.returncode == 0
    report = json.loads(weak.stdout)
    assert report['cli_exit_check'] == 'grid_and_inside_pass'
    assert report['cli_exit_check_passed'] and not report['submission_authorized']
    _write(candidate, np.nan_to_num(template), 'float32', None)
    strict = subprocess.run(command, capture_output=True, text=True)
    assert strict.returncode == 0
    assert not json.loads(strict.stdout)['submission_authorized']
