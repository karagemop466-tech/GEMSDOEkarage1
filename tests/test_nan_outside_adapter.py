"""NaN-outside adapter (scripts/nan_outside_adapter.py). Synthetic grid only; local format checks."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest
import rasterio
from affine import Affine

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import nan_outside_adapter as adapter  # noqa: E402

T = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)


@pytest.fixture
def sample(tmp_path):
    foot = np.ones((8, 8), bool)
    foot[0, :] = False
    foot[:, 0] = False
    s = tmp_path / "sample.tif"
    with rasterio.open(s, "w", driver="GTiff", height=8, width=8, count=1, dtype="float32",
                       crs="EPSG:32611", transform=T, nodata=float("nan")) as dst:
        dst.write(np.where(foot, 0.0, np.nan).astype("float32"), 1)
    return s, foot


def test_round_trip_nan_outside_passes_all_checks(tmp_path, sample):
    s, foot = sample
    pred = np.zeros((8, 8))
    pred[3, 3] = 1.0
    pred[5, 2] = 0.25
    rec = adapter.write_nan_outside(tmp_path / "x.tif", pred, s, foot, name="t", note="n")
    assert rec["validator"]["all_checks_passed"]
    assert rec["outside_encoding"] == "nan"
    with rasterio.open(tmp_path / "x.tif") as ds:
        a = ds.read(1)
    assert np.isnan(a[~foot]).all() and np.isfinite(a[foot]).all()
    assert a[3, 3] == 1.0 and a[5, 2] == 0.25
    assert json.loads((tmp_path / "x.json").read_text())["approved_for_weekly_slot"] is False
    assert sorted(z for z in __import__("zipfile").ZipFile(tmp_path / "x.zip").namelist()) == ["x.tif"]


def test_refuses_overwrite_and_out_of_range(tmp_path, sample):
    s, foot = sample
    pred = np.zeros((8, 8))
    pred[2, 2] = 1.2
    with pytest.raises(ValueError):
        adapter.write_nan_outside(tmp_path / "bad.tif", pred, s, foot, name="t", note="n")
    assert not (tmp_path / "bad.tif").exists()
    ok = np.zeros((8, 8))
    adapter.write_nan_outside(tmp_path / "ok.tif", ok, s, foot, name="t", note="n")
    with pytest.raises(FileExistsError):
        adapter.write_nan_outside(tmp_path / "ok.tif", ok, s, foot, name="t", note="n")


def test_rejects_long_note_and_catalogue_hit(tmp_path, sample):
    s, foot = sample
    pred = np.zeros((8, 8))
    pred[4, 4] = 1.0
    with pytest.raises(ValueError):
        adapter.write_nan_outside(tmp_path / "a.tif", pred, s, foot, name="t", note="x" * 141)
    cat = np.zeros((8, 8), bool)
    cat[4, 4] = True
    with pytest.raises(ValueError):
        adapter.write_nan_outside(tmp_path / "b.tif", pred, s, foot, name="t", note="n", catalogue=cat)


def test_zeros_outside_file_fails_nan_validator(tmp_path, sample):
    s, foot = sample
    p = tmp_path / "zeros.tif"
    with rasterio.open(p, "w", driver="GTiff", height=8, width=8, count=1, dtype="float32",
                       crs="EPSG:32611", transform=T) as dst:
        dst.write(np.zeros((8, 8), "float32"), 1)
    v = adapter.validate_nan_outside(p, s, foot)
    assert not v["all_checks_passed"]
    assert v["checks"]["outside_footprint_all_nan"] is False
