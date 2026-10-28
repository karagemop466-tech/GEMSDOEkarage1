"""Synthetic tests only: local formatting is never a slot or uniqueness gate."""
import json
import zipfile

import numpy as np
import pytest
import rasterio
from affine import Affine
from gems57 import gates, grid, submission_writer, validate


@pytest.fixture
def synthetic_grid(tmp_path, monkeypatch):
    shape = (8, 8)
    transform = Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0)
    for name, value in {'HEIGHT': 8, 'WIDTH': 8, 'SHAPE': shape, 'TRANSFORM': transform}.items():
        monkeypatch.setattr(grid, name, value)
    for name, value in {'HEIGHT': 8, 'WIDTH': 8, 'TRANSFORM': transform}.items():
        monkeypatch.setattr(validate, name, value)
    monkeypatch.setattr(gates, 'SHAPE', shape)
    monkeypatch.setattr(gates, 'TRANSFORM', transform)
    foot = np.ones(shape, dtype=bool)
    foot[0, :] = False
    catalogue = np.zeros(shape, dtype=bool)
    catalogue[2, 2] = True
    sample = tmp_path / 'sample.tif'
    sample_array = np.where(foot, 0.0, np.nan).astype('float32')
    with rasterio.open(sample, 'w', driver='GTiff', height=8, width=8, count=1,
                       dtype='float32', crs='EPSG:32611', transform=transform, nodata=np.nan) as dst:
        dst.write(sample_array, 1)
    return sample, foot, catalogue


def test_shared_local_writer_round_trip_does_not_select_a_slot(tmp_path, synthetic_grid):
    sample, foot, cat = synthetic_grid
    p = np.zeros(foot.shape, dtype='float32')
    p[4, 4] = 1
    path = tmp_path / 'synthetic.tif'
    rec = submission_writer.write_submission(path, p, sample, foot, catalogue=cat,
                                              name='synthetic test', note='synthetic test only')
    assert rec['promoted'] is False and rec['approved_for_weekly_slot'] is False
    assert rec['validator']['all_checks_passed'] is True  # local policy, not organizer acceptance
    with rasterio.open(path) as src:
        saved = src.read(1)
        assert src.count == 1 and src.dtypes[0] == 'float32'
        assert np.array_equal(saved, p)
        assert np.all(saved[~foot] == 0)  # separate from official null/NaN wording
    with zipfile.ZipFile(path.with_suffix('.zip')) as archive:
        assert archive.namelist() == [path.name]
        assert archive.read(path.name) == path.read_bytes()
    assert json.loads(path.with_suffix('.json').read_text())['approved_for_weekly_slot'] is False


@pytest.mark.parametrize('invalid', [float('nan'), float('inf'), -0.01, 1.01])
def test_shared_local_writer_rejects_bad_values_without_outputs(tmp_path, synthetic_grid, invalid):
    sample, foot, cat = synthetic_grid
    p = np.zeros(foot.shape, dtype='float32')
    p[3, 3] = invalid
    path = tmp_path / 'bad.tif'
    with pytest.raises(ValueError):
        submission_writer.write_submission(path, p, sample, foot, catalogue=cat, name='test', note='test')
    assert not path.exists() and not path.with_suffix('.zip').exists()


def test_shared_local_writer_rejects_catalogue_or_outside_positive(tmp_path, synthetic_grid):
    sample, foot, cat = synthetic_grid
    for y, x in ((2, 2), (0, 1)):
        p = np.zeros(foot.shape, dtype='float32')
        p[y, x] = 1
        with pytest.raises(ValueError):
            submission_writer.write_submission(tmp_path / 'bad.tif', p, sample, foot,
                                               catalogue=cat, name='test', note='test')
    assert not (tmp_path / 'bad.tif').exists()


def test_historical_pipeline_cannot_rebuild_or_ship_before_gate(tmp_path):
    from gemsk import pipeline
    with pytest.raises(RuntimeError, match='literal lattice'):
        pipeline.build(10)
    with pytest.raises(RuntimeError, match='incomplete registry'):
        pipeline.ship(np.zeros((1, 1)), np.zeros((1, 1)), 'test', 'test', tmp_path)
    assert list(tmp_path.iterdir()) == []
