"""Small synthetic checks for stop rules; no geological experiment is run."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from gemskarage1.holdout_eval import score_canary_feature
from gemskarage1.registry_audit import check_preplacement_surface, run_full_fleet_uniqueness_gate
from scripts import restore_karage1_data as restore


def write_tif(path, data, transform=None, nodata=None):
    data = np.asarray(data, dtype=np.float32)
    with rasterio.open(path, 'w', driver='GTiff', count=1, dtype='float32',
                       width=data.shape[1], height=data.shape[0], crs='EPSG:32611',
                       transform=transform or from_origin(0, 2000, 100, 100), nodata=nodata) as dst:
        dst.write(data, 1)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def complete_index(*paths):
    repo = 'fixture/test'
    commit = 'a' * 40
    return {'complete_accessible_scan': True, 'errors': [], 'expected_raster_count': len(paths),
            'source_coverage': {'scope': 'synthetic test fixture, not a real registry',
                                'immutable_repos': [{'repo': repo, 'commit': commit}]},
            'rasters': [{'cache_file': str(p), 'sha256': sha(p), 'repo_first': repo,
                         'sources': [f'{repo}@{commit}/{p.name}']} for p in paths]}


@pytest.fixture
def geometry(tmp_path):
    shape = (20, 20)
    foot = np.ones(shape, dtype=bool)
    surface = np.random.default_rng(3).random(shape, dtype=np.float32)
    ref = np.zeros(shape, dtype=np.float32)
    ref[2, 2] = 1
    dots = np.zeros(shape, dtype=np.float32)
    dots[17, 17] = 1
    template, ref_file, final = (tmp_path / n for n in ('template.tif', 'reference.tif', 'final.tif'))
    write_tif(template, np.zeros(shape))
    write_tif(ref_file, ref)
    write_tif(final, dots)
    index = complete_index(ref_file)
    return dict(foot=foot, surface=surface, dots=dots, template=template, final=final,
                ref=ref_file, index=index)


def before(g):
    return check_preplacement_surface(g['surface'], g['foot'], g['template'], g['index'])


def final(g, report):
    return run_full_fleet_uniqueness_gate(g['surface'], g['dots'], g['final'], g['foot'],
                                          registry_index=g['index'], preplacement_report=report)


def test_tiny_complete_fixture_passes_both_checks_without_selecting_slot(geometry):
    r = before(geometry)
    assert r['passed'] and r['all_reference_ranks_defined']
    result = final(geometry, r)
    assert result['passed'] and result['surface_preplacement_verified']
    assert result['max_directed_overlap_3px_any_registry'] == 0.0
    assert 'slot_selected' not in result


def test_registered_lattice_is_never_exempt_and_three_pixel_boundary_is_inclusive(geometry):
    g = geometry
    # (2,2) is precisely three pixels away from (2,5).
    g['dots'][:] = 0
    g['dots'][2, 5] = 1
    write_tif(g['final'], g['dots'])
    result = final(g, before(g))
    assert result['surface_preplacement_verified']
    assert result['max_directed_overlap_3px_any_registry'] == 1.0
    assert not result['passed']
    # Dense witnesses are not excluded, either.
    dense = np.zeros(g['foot'].shape, dtype=np.float32)
    dense[::4, ::4] = 1
    extra = g['ref'].with_name('calibration-lattice.tif')
    write_tif(extra, dense)
    g['index'] = complete_index(g['ref'], extra)
    result = final(g, before(g))
    assert result['max_directed_overlap_3px_any_registry'] == 1.0
    assert not result['passed']


def test_missing_complete_inventory_fails_closed(geometry):
    g = geometry
    index = copy.deepcopy(g['index'])
    index['complete_accessible_scan'] = False
    g['index'] = index
    assert not before(g)['passed']
    index['complete_accessible_scan'] = True
    index['expected_raster_count'] += 1
    with pytest.raises(ValueError, match='expected raster count'):
        before(g)


def test_missing_or_nonfinite_registry_input_is_not_sanitized_to_a_pass(geometry):
    g = geometry
    with rasterio.open(g['ref']) as ds:
        a = ds.read(1)
    a[4, 4] = np.nan
    write_tif(g['ref'], a)
    g['index'] = complete_index(g['ref'])
    result = before(g)
    assert not result['passed']
    assert any('non-finite' in e for e in result['errors'])
    g['ref'].unlink()
    result = before(g)
    assert not result['passed'] and result['errors']


def test_every_reference_rank_must_be_defined_not_just_the_maximum(geometry):
    g = geometry
    constant = g['ref'].with_name('constant.tif')
    write_tif(constant, np.zeros(g['foot'].shape))
    g['index'] = complete_index(g['ref'], constant)
    result = before(g)
    assert result['comparison']['worst_spearman_full_footprint'] is not None
    assert any(r['spearman_full_footprint'] is None for r in result['comparison']['rows'])
    assert not result['all_reference_ranks_defined'] and not result['passed']
    # Even a mutated high-level flag cannot make an incomplete rank receipt valid.
    result['passed'] = True
    gfinal = final(g, result)
    assert not gfinal['surface_preplacement_verified'] and not gfinal['passed']


def test_preplacement_receipt_binds_surface_inventory_and_footprint(geometry):
    g = geometry
    report = before(g)
    assert final(g, report)['passed']
    assert not final(g, None)['passed']
    g['surface'][0, 0] += .01
    assert not final(g, report)['surface_preplacement_verified']
    g['surface'][0, 0] -= .01
    # A different valid footprint cannot reuse the receipt.
    g['foot'][0, 0] = False
    result = final(g, report)
    assert not result['surface_preplacement_verified'] and not result['passed']
    g['foot'][0, 0] = True
    g['index']['source_coverage']['scope'] += ' changed'
    assert not final(g, report)['surface_preplacement_verified']


def test_saved_file_must_equal_the_in_memory_array_and_current_grid(geometry):
    g = geometry
    report = before(g)
    altered = g['dots'].copy()
    altered[10, 10] = 1
    write_tif(g['final'], altered)
    with pytest.raises(ValueError, match='does not match saved'):
        final(g, report)
    write_tif(g['final'], g['dots'], transform=from_origin(1, 2000, 100, 100))
    result = final(g, report)
    assert not result['passed']  # grid mismatch is detected, not skipped


@pytest.mark.parametrize('values,labels,status', [
    ([1, 1, 1, 1], [0, 0, 1, 1], 'constant_no_variation'),
    ([0, float('nan'), 2, 3], [0, 0, 1, 1], 'nonfinite'),
    ([0, 1, 2, 3], [1, 1, 1, 1], 'missing_class'),
    ([0, 0, 1, 1], [0, 0, 1, 1], 'leakage_alarm'),
    ([1, 1, 0, 0], [0, 0, 1, 1], 'leakage_alarm'),
])
def test_canary_never_converts_bad_or_high_auc_inputs_into_a_pass(values, labels, status):
    result = score_canary_feature(np.array(values), np.array(labels))
    assert not result['passed'] and result['status'] == status


def test_canary_accepts_a_really_testable_nonleaking_feature():
    result = score_canary_feature(np.array([0, 1, 1, 0]), np.array([0, 0, 1, 1]))
    assert result['passed'] and result['status'] == 'tested'
    assert result['direction_invariant_auc'] == .5


def test_restore_both_manifest_schemas_without_real_network(tmp_path, monkeypatch):
    chunks = {'one': b'abc', 'part1': b'def', 'part2': b'ghi'}
    common = {'repo': 'fixture/test', 'ref': 'a'*40}
    manifest = {'files': [
        {'id': 'top', 'dest': 'a.bin', 'sha256': hashlib.sha256(chunks['one']).hexdigest(),
         **common, 'path': 'one'},
        {'id': 'nested', 'dest': 'b.bin', 'sha256': hashlib.sha256(b'defghi').hexdigest(),
         'source': {**common, 'kind': 'git_split_blob', 'parts': ['part1', 'part2']}},
    ]}
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(manifest))
    class FakeFetcher:
        def __init__(self, _cache): pass
        def write_blob(self, repo, ref, path, fh):
            assert repo == common['repo'] and ref == common['ref']
            fh.write(chunks[path])
    monkeypatch.setattr(restore, 'GitBlobFetcher', FakeFetcher)
    monkeypatch.setattr('sys.argv', ['restore', '--manifest', str(path), '--data-dir', str(tmp_path / 'data')])
    assert restore.main() == 0
    assert (tmp_path / 'data/a.bin').read_bytes() == b'abc'
    assert (tmp_path / 'data/b.bin').read_bytes() == b'defghi'
    (tmp_path / 'data/b.bin').write_bytes(b'corrupt')
    monkeypatch.setattr('sys.argv', ['restore', '--manifest', str(path), '--data-dir', str(tmp_path / 'data'), '--verify-only'])
    assert restore.main() == 1


def test_restore_rejects_paths_that_escape_or_are_symlinks(tmp_path, monkeypatch):
    dest = tmp_path / 'dest'
    dest.mkdir()
    (dest / 'out').symlink_to(tmp_path, target_is_directory=True)
    entry = {'id': 'bad', 'dest': 'out/elsewhere', 'sha256': '0'*64,
             'repo': 'fixture/test', 'ref': 'a'*40, 'path': 'one'}
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps({'files': [entry]}))
    monkeypatch.setattr('sys.argv', ['restore', '--manifest', str(path), '--data-dir', str(dest)])
    with pytest.raises(ValueError, match='escapes'):
        restore.main()
