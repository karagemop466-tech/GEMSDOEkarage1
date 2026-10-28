"""Regression tests for the shared literal all-raster gate and saved bytes."""
import hashlib
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gemskarage1 import registry_audit
from gemskarage1.registry_audit import run_full_fleet_uniqueness_gate, run_surface_gate
from gems57.uniqueness import compare_array_to_registry

TRANSFORM = from_origin(100, 1000, 100, 100)
REPO, COMMIT = 'fixture/test', 'a' * 40


@pytest.fixture(autouse=True)
def use_fixture_as_lattice_witness(tmp_path, monkeypatch):
    """Only synthetic tests may replace the real registered lattice pin."""
    last = [None]
    def fixture_pin():
        path = tmp_path / 'prior.tif'
        if path.exists():
            last[0] = hashlib.sha256(path.read_bytes()).hexdigest()
        return last[0]
    monkeypatch.setattr(registry_audit, '_lattice_pin', fixture_pin)


def write(path, arr, *, transform=TRANSFORM, dtype='float32'):
    arr = np.asarray(arr, dtype=dtype)
    with rasterio.open(path, 'w', driver='GTiff', width=arr.shape[1], height=arr.shape[0],
                       count=1, dtype=dtype, crs='EPSG:32611', transform=transform) as dst:
        dst.write(arr, 1)
    return path


def index(path, **overrides):
    row = {'repo_first': REPO, 'sources': [f'{REPO}@{COMMIT}/{path.name}'], 'cache_file': str(path),
           'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    return {'rasters': [row], 'expected_raster_count': 1, 'complete_accessible_scan': True,
            'source_coverage': {'scope': 'synthetic tests only',
                                'immutable_repos': [{'repo': REPO, 'commit': COMMIT}]},
            'errors': []} | overrides


def fixture(tmp_path):
    foot = np.ones((24, 24), dtype=bool)
    sample = write(tmp_path/'sample.tif', np.zeros(foot.shape))
    a = np.zeros(foot.shape, np.float32); a[1, 1] = 1; a[22, 22] = 1
    b = np.zeros(foot.shape, np.float32); b[1, 6] = 1; b[22, 17] = 1
    prior = write(tmp_path/'prior.tif', b)
    candidate = write(tmp_path/'candidate.tif', a)
    return foot, sample, a, prior, candidate


def test_both_phases_require_bound_preplacement_receipt(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    receipt = run_surface_gate(a, foot, sample=sample, registry_index=index(prior))
    assert receipt['passed']
    report = run_full_fleet_uniqueness_gate(a, a, candidate, foot, sample=sample,
                 registry_index=index(prior), preplacement_report=receipt)
    assert report['passed'] and report['surface_preplacement_verified']
    assert report['candidate_sha256'] == hashlib.sha256(candidate.read_bytes()).hexdigest()
    late = run_full_fleet_uniqueness_gate(a, a, candidate, foot, sample=sample, registry_index=index(prior))
    assert not late['passed'] and not late['surface_preplacement_verified']


def test_saturated_prior_and_undefined_ranks_are_never_exempt(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    write(prior, np.ones(foot.shape))
    report = compare_array_to_registry(a, index(prior), foot,
                expected_grid=(foot.shape, rasterio.crs.CRS.from_epsg(32611), TRANSFORM))
    assert not report['unique'] and report['duplicate_count'] == 1
    assert report['rows'][0]['my_dots_within_3px_of_theirs'] == 1
    surface = run_surface_gate(a, foot, sample=sample, registry_index=index(prior))
    assert not surface['passed'] and not surface['all_reference_ranks_defined']
    write(prior, np.zeros(foot.shape))
    assert not run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['passed']


def test_missing_empty_incomplete_bad_hash_and_wrong_grid(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    with pytest.raises(ValueError):
        run_surface_gate(a, foot, sample=None, registry_index=index(prior))
    with pytest.raises(ValueError):
        run_surface_gate(a, foot, sample=sample, registry_index=None)
    empty = index(prior, rasters=[], expected_raster_count=0)
    with pytest.raises(ValueError):
        run_surface_gate(a, foot, sample=sample, registry_index=empty)
    for idx in (index(prior, complete_accessible_scan=False), index(prior, complete_accessible_scan='true')):
        assert not run_surface_gate(a, foot, sample=sample, registry_index=idx)['passed']
    with pytest.raises(ValueError):
        run_surface_gate(a, foot, sample=sample, registry_index=index(prior, expected_raster_count=2))
    with pytest.raises(ValueError):
        run_surface_gate(a, foot, sample=sample, registry_index=index(prior, errors=['incomplete source']))
    bad = index(prior); bad['rasters'][0]['sha256'] = 'f'*64
    with pytest.raises(ValueError, match='lattice witness'):
        run_surface_gate(a, foot, sample=sample, registry_index=bad)
    missing = index(prior); prior.unlink()
    assert not run_surface_gate(a, foot, sample=sample, registry_index=missing)['passed']
    write(prior, a, transform=from_origin(200, 1000, 100, 100))
    assert not run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['passed']
    unpinned = index(prior); unpinned['rasters'][0]['sha256'] = None
    with pytest.raises(ValueError, match='pinned'):
        run_surface_gate(a, foot, sample=sample, registry_index=unpinned)


def test_saved_bytes_must_equal_final_array(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    altered = a.copy(); altered[2, 2] = 1
    with pytest.raises(ValueError, match='does not match saved'):
        run_full_fleet_uniqueness_gate(a, altered, candidate, foot, sample=sample, registry_index=index(prior))
    write(candidate, a, dtype='float64')
    with pytest.raises(ValueError, match='float32'):
        run_full_fleet_uniqueness_gate(a, a, candidate, foot, sample=sample, registry_index=index(prior))
    with rasterio.open(candidate, 'w', driver='GTiff', width=a.shape[1], height=a.shape[0],
                       count=1, dtype='float32', crs='EPSG:32611', transform=TRANSFORM, nodata=1.0) as dst:
        dst.write(a, 1)
    with pytest.raises(ValueError, match='masked or nodata pixels inside footprint'):
        run_full_fleet_uniqueness_gate(a, a, candidate, foot, sample=sample, registry_index=index(prior))


def test_exact_70_percent_does_not_trigger_but_eight_tenths_does(tmp_path):
    foot = np.ones((12, 110), dtype=bool)
    sample = write(tmp_path/'sample.tif', np.zeros(foot.shape))
    a = np.zeros(foot.shape, np.float32)
    for x in range(5, 105, 10): a[5, x] = 1
    prior = tmp_path/'prior.tif'
    b = a.copy(); b[5, 75:] = 0
    write(prior, b)
    row = run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['comparison']['rows'][0]
    assert row['my_dots_within_3px_of_theirs'] == .7 and not row['duplicate_by_overlap']
    b[5, 75] = 1; write(prior, b)
    row = run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['comparison']['rows'][0]
    assert row['my_dots_within_3px_of_theirs'] == .8 and row['duplicate_by_overlap']


def test_shared_comparator_never_sanitizes_nonfinite_inside_footprint(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    b = np.zeros(foot.shape, np.float32); b[2, 2] = 1; b[4, 4] = np.nan
    write(prior, b)
    report = compare_array_to_registry(a, index(prior), foot,
                expected_grid=(foot.shape, rasterio.crs.CRS.from_epsg(32611), TRANSFORM))
    assert not report['unique'] and not report['complete_accessible_scan']
    assert 'non-finite' in report['rows'][0]['error']
    # NaN outside the footprint remains acceptable: the protocol concerns the
    # valid competition footprint, and official outside encoding is unresolved.
    foot[4, 4] = False
    report = compare_array_to_registry(a, index(prior), foot,
                expected_grid=(foot.shape, rasterio.crs.CRS.from_epsg(32611), TRANSFORM))
    assert report['complete_accessible_scan'] and 'error' not in report['rows'][0]
