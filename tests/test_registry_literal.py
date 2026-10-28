"""Regression tests for the shared literal all-raster gate and saved bytes."""
import hashlib
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gemskarage1.registry_audit import run_full_fleet_uniqueness_gate, run_surface_gate
from gems57.uniqueness import compare_array_to_registry

TRANSFORM = from_origin(100, 1000, 100, 100)


def write(path, arr, *, transform=TRANSFORM, dtype='float32'):
    arr = np.asarray(arr, dtype=dtype)
    with rasterio.open(path, 'w', driver='GTiff', width=arr.shape[1], height=arr.shape[0],
                       count=1, dtype=dtype, crs='EPSG:32611', transform=transform) as dst:
        dst.write(arr, 1)
    return path


def index(path, **overrides):
    row = {'repo_first': 'owner/repo', 'sources': ['prior'], 'cache_file': str(path),
           'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    return {'rasters': [row], 'registry_rasters_expected': 1, 'complete_accessible_scan': True,
            'errors': []} | overrides


def fixture(tmp_path):
    foot = np.ones((24, 24), dtype=bool)
    sample = write(tmp_path/'sample.tif', np.zeros(foot.shape))
    a = np.zeros(foot.shape, np.float32); a[1, 1] = 1; a[22, 22] = 1
    b = np.zeros(foot.shape, np.float32); b[1, 6] = 1; b[22, 17] = 1
    prior = write(tmp_path/'prior.tif', b)
    candidate = write(tmp_path/'candidate.tif', a)
    return foot, sample, a, prior, candidate


def test_both_phases_and_retrospective_order_fail_closed(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    assert run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['ok']
    report = run_full_fleet_uniqueness_gate(a, a, candidate, foot, sample=sample, registry_index=index(prior))
    assert report['surface']['ok'] and report['dots']['ok'] and report['comparisons_passed']
    assert report['surface_checked_before_placement'] is False and report['passed'] is False
    assert report['candidate_sha256'] == hashlib.sha256(candidate.read_bytes()).hexdigest()


def test_saturated_prior_and_undefined_ranks_are_never_exempt(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    write(prior, np.ones(foot.shape))
    for phase in ('surface', 'dots'):
        report = compare_array_to_registry(a, index(prior), foot,
                    expected_grid=(foot.shape, rasterio.crs.CRS.from_epsg(32611), TRANSFORM))
        assert not report['unique'] and report['duplicate_count'] == 1
        assert report['rows'][0]['my_dots_within_3px_of_theirs'] == 1
    surface = run_surface_gate(a, foot, sample=sample, registry_index=index(prior))
    assert not surface['ok'] and surface['undefined_rank_references'] == ['prior']
    assert surface['policy_exemptions'] == []
    write(prior, np.zeros(foot.shape))
    assert not run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['ok']


def test_missing_empty_incomplete_bad_hash_and_wrong_grid(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    with pytest.raises(ValueError):
        run_surface_gate(a, foot, sample=None, registry_index=index(prior))
    with pytest.raises(ValueError):
        run_surface_gate(a, foot, sample=sample, registry_index=None)
    empty = {'rasters': [], 'registry_rasters_expected': 0, 'complete_accessible_scan': True, 'errors': []}
    assert not run_surface_gate(a, foot, sample=sample, registry_index=empty)['ok']
    for idx in (index(prior, complete_accessible_scan=False),
                index(prior, complete_accessible_scan='true'),
                index(prior, registry_rasters_expected=2),
                index(prior, errors=['incomplete source'])):
        assert not run_surface_gate(a, foot, sample=sample, registry_index=idx)['ok']
    bad = index(prior); bad['rasters'][0]['sha256'] = 'f'*64
    assert not run_surface_gate(a, foot, sample=sample, registry_index=bad)['ok']
    missing = index(prior); prior.unlink()
    assert not run_surface_gate(a, foot, sample=sample, registry_index=missing)['ok']
    write(prior, a, transform=from_origin(200, 1000, 100, 100))
    assert not run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['ok']
    unpinned = index(prior); unpinned['rasters'][0]['sha256'] = None
    with pytest.raises(ValueError, match='SHA256'):
        run_surface_gate(a, foot, sample=sample, registry_index=unpinned)


def test_saved_bytes_must_equal_final_array(tmp_path):
    foot, sample, a, prior, candidate = fixture(tmp_path)
    altered = a.copy(); altered[2, 2] = 1
    with pytest.raises(ValueError, match='exact saved raster'):
        run_full_fleet_uniqueness_gate(a, altered, candidate, foot, sample=sample, registry_index=index(prior))
    write(candidate, a, dtype='float64')
    with pytest.raises(ValueError, match='grid differs'):
        run_full_fleet_uniqueness_gate(a, a, candidate, foot, sample=sample, registry_index=index(prior))


def test_exact_70_percent_does_not_trigger_but_eight_tenths_does(tmp_path):
    foot = np.ones((12, 110), dtype=bool)
    sample = write(tmp_path/'sample.tif', np.zeros(foot.shape))
    a = np.zeros(foot.shape, np.float32)
    for x in range(5, 105, 10): a[5, x] = 1
    prior = tmp_path/'prior.tif'
    b = a.copy(); b[5, 75:] = 0  # seven of ten, separated by >3 pixels
    write(prior, b)
    row = run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['rows'][0]
    assert row['my_dots_within_3px_of_theirs'] == .7 and not row['duplicate_by_overlap']
    b[5, 75] = 1; write(prior, b)
    row = run_surface_gate(a, foot, sample=sample, registry_index=index(prior))['rows'][0]
    assert row['my_dots_within_3px_of_theirs'] == .8 and row['duplicate_by_overlap']
