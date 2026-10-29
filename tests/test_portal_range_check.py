"""Regression tests for scripts/portal_range_check.py (diagnostic only)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import portal_range_check as prc  # noqa: E402


def _write(path: Path, arr: np.ndarray, nodata=None) -> Path:
    h, w = arr.shape[-2:]
    count = 1 if arr.ndim == 2 else arr.shape[0]
    data = arr if arr.ndim == 3 else arr[None]
    with rasterio.open(
        path, "w", driver="GTiff", height=h, width=w, count=count, dtype="float32",
        crs="EPSG:32611", transform=from_origin(0, 0, 100, 100), nodata=nodata,
    ) as dst:
        dst.write(data.astype("float32"))
    return path


def test_nan_outside_fails_naive_check_but_passes_nan_aware(tmp_path):
    a = np.full((4, 5), np.nan, np.float32)
    a[1:3, 1:4] = 0.5
    r = prc.check(_write(tmp_path / "nan.tif", a))
    assert r["ok_format"] is True
    assert r["naive_whole_array_pass"] is False
    assert r["nan_aware_pass"] is True
    assert r["nan_count"] == 20 - 6
    assert r["positive_count"] == 6


def test_zeros_outside_passes_both_checks(tmp_path):
    a = np.zeros((4, 5), np.float32)
    a[1:3, 1:4] = 1.0
    r = prc.check(_write(tmp_path / "zeros.tif", a))
    assert r["naive_whole_array_pass"] is True
    assert r["nan_aware_pass"] is True
    assert r["finite_min"] == 0.0 and r["finite_max"] == 1.0


def test_out_of_range_values_fail_both_checks(tmp_path):
    a = np.zeros((3, 3), np.float32)
    a[0, 0] = -3.4028234663852886e38  # the feature-stack nodata sentinel, if written as a value
    a[1, 1] = 1.5
    r = prc.check(_write(tmp_path / "bad.tif", a))
    assert r["naive_whole_array_pass"] is False
    assert r["nan_aware_pass"] is False
    assert r["finite_outside_01_count"] == 2


def test_two_band_file_is_rejected_fail_closed(tmp_path):
    a = np.zeros((2, 3, 3), np.float32)
    r = prc.check(_write(tmp_path / "two.tif", a))
    assert r["ok_format"] is False
    assert "exactly one band" in r["error"]


def test_report_is_strict_json_and_cli_exit_code(tmp_path):
    a = np.full((3, 3), np.nan, np.float32)
    a[0, 0] = 0.2
    p = _write(tmp_path / "one.tif", a)
    out = tmp_path / "report.json"
    code = prc.main([str(p), "--out", str(out)])
    assert code == 0
    data = json.loads(out.read_text(), parse_constant=lambda c: (_ for _ in ()).throw(ValueError(c)))
    assert data["schema"] == "portal-range-check-v1"
    assert data["not_established"].startswith("Portal acceptance is not established")
    assert len(data["file_sha256"]) == 64


def test_non_tif_is_refused(tmp_path):
    p = tmp_path / "x.zip"
    p.write_bytes(b"not a tif")
    r = prc.check(p)
    assert r["ok_format"] is False


def test_missing_file_fails_closed(tmp_path):
    r = prc.check(tmp_path / "absent.tif")
    assert r["ok_format"] is False
    assert r["error"] == "file not found"
    assert "file_sha256" not in r


def test_corrupt_tif_fails_closed(tmp_path):
    p = tmp_path / "corrupt.tif"
    p.write_bytes(b"II*\x00 not really a tiff")
    r = prc.check(p)
    assert r["ok_format"] is False
    assert r["error"].startswith("unreadable GeoTIFF")
