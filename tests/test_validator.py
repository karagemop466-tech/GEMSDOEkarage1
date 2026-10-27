import numpy as np
import pytest
import rasterio

from gems.grid import GEMS_GRID
from gems.submission_writer import write_submission
from gems.validator import validate_submission


def test_generated_baseline_passes_all_gates(tmp_path):
    path = tmp_path / "baseline.tif"
    arr = np.zeros(GEMS_GRID.shape, dtype=np.float32)
    write_submission(path, arr)
    report = validate_submission(path)
    assert report.all_checks_passed, report.checks
    assert report.n_nan == 0
    assert report.min_value == 0.0
    assert report.max_value == 0.0


def test_sentinel_nodata_leak_is_caught(tmp_path):
    """
    Reproduces the class of bug behind the reported DrivenData error:
    'Predicted values must be in range [0, 1]' -- a raw GDAL float32 nodata
    sentinel (-3.4e38) written into real pixels instead of being handled.
    """
    path = tmp_path / "bad_sentinel.tif"
    h, w = GEMS_GRID.shape
    arr = np.zeros((h, w), dtype=np.float32)
    arr[10, 10] = np.float32(-3.4e38)
    profile = {
        "driver": "GTiff",
        "height": h,
        "width": w,
        "count": 1,
        "dtype": "float32",
        "crs": GEMS_GRID.crs,
        "transform": GEMS_GRID.transform,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr, 1)

    report = validate_submission(path)
    assert report.all_checks_passed is False
    assert report.checks["no_sentinel_nodata_leak"] is False
    assert report.checks["finite_values_in_0_1"] is False


def test_wrong_shape_is_caught(tmp_path):
    path = tmp_path / "wrong_shape.tif"
    profile = {
        "driver": "GTiff",
        "height": 10,
        "width": 10,
        "count": 1,
        "dtype": "float32",
        "crs": GEMS_GRID.crs,
        "transform": GEMS_GRID.transform,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(np.zeros((10, 10), dtype=np.float32), 1)
    report = validate_submission(path)
    assert report.checks["shape_matches_reference"] is False
    assert report.all_checks_passed is False


def test_logits_out_of_range_are_caught(tmp_path):
    """Un-squashed model logits (no final sigmoid) written directly."""
    path = tmp_path / "logits.tif"
    h, w = GEMS_GRID.shape
    arr = np.random.default_rng(0).normal(0, 3, size=(h, w)).astype(np.float32)
    profile = {
        "driver": "GTiff",
        "height": h,
        "width": w,
        "count": 1,
        "dtype": "float32",
        "crs": GEMS_GRID.crs,
        "transform": GEMS_GRID.transform,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr, 1)
    report = validate_submission(path)
    assert report.checks["finite_values_in_0_1"] is False
    assert report.all_checks_passed is False


def test_writer_rejects_wrong_shape_input():
    with pytest.raises(ValueError):
        write_submission("/tmp/should_not_be_written.tif", np.zeros((5, 5)))
