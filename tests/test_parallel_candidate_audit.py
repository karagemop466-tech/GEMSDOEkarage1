"""Synthetic regressions; these do not establish real-data release readiness."""
import json

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

from scripts import audit_parallel_candidates as audit
from scripts.audit_references import sha256


def write_tif(path, values, origin=0):
    with rasterio.open(path, 'w', driver='GTiff', width=values.shape[1], height=values.shape[0],
                       count=1, dtype='float32', crs='EPSG:32611',
                       transform=from_origin(origin, 1000, 100, 100), nodata=np.nan) as ds:
        ds.write(values.astype('float32'), 1)


@pytest.fixture
def synthetic(tmp_path, monkeypatch):
    monkeypatch.setattr(audit, 'ROOT', tmp_path)
    (tmp_path / 'registry').mkdir()
    samples = tmp_path / 'rasters'
    samples.mkdir()
    template = np.zeros((12, 12)); template[0, :] = np.nan
    lattice = np.zeros((12, 12)); lattice[5, 5] = 1; lattice[0, :] = np.nan
    dots = np.zeros((12, 12)); dots[5, 8] = 1; dots[11, 11] = 1
    for name, array in [('template', template), ('lattice', lattice), ('td', dots), ('ctws', dots)]:
        write_tif(samples / f'{name}.tif', array)
    refs = [{'id': n, 'sha256': sha256(samples / f'{n}.tif')} for n in ('template', 'lattice')]
    (tmp_path / 'registry/reference_assets.json').write_text(json.dumps(refs))
    monkeypatch.setattr(audit, 'PARALLEL_ASSETS', {
        n: {'pr': i, 'commit': 'c'*40, 'path': n+'.tif', 'sha256': sha256(samples / f'{n}.tif')}
        for i, n in enumerate(('td', 'ctws'))})
    return samples


def test_overlap_uses_closed_disk_and_candidate_denominator(synthetic):
    result = audit.audit(synthetic)
    assert result['candidates']['td']['candidate_dots_in_footprint'] == 2
    assert result['candidates']['td']['dots_within_3px'] == 1
    assert result['candidates']['td']['directed_overlap'] == .5
    assert result['candidates']['td']['ok_to_submit'] is False
    assert result['candidates']['td']['preplacement_surface_checked'] is False


def test_changed_bytes_are_rejected(synthetic):
    with (synthetic/'td.tif').open('ab') as f:
        f.write(b'changed')
    with pytest.raises(ValueError, match='SHA-256 mismatch'):
        audit.audit(synthetic)


@pytest.mark.parametrize('case', ['grid', 'nonbinary', 'nodata', 'empty', 'all_ones', 'uint8'])
def test_invalid_candidate_fails_closed(synthetic, case):
    a = np.zeros((12, 12)); a[5, 5] = 1
    if case == 'nonbinary': a[5, 5] = 1.1
    if case == 'nodata': a[5, 5] = np.nan
    if case == 'empty': a[:] = 0
    if case == 'all_ones': a[:] = 1
    path = synthetic / 'td.tif'
    if case == 'uint8':
        with rasterio.open(path, 'w', driver='GTiff', width=a.shape[1], height=a.shape[0],
                           count=1, dtype='uint8', crs='EPSG:32611',
                           transform=from_origin(0, 1000, 100, 100)) as ds:
            ds.write(a.astype('uint8'), 1)
    else:
        write_tif(path, a, origin=100 if case == 'grid' else 0)
    audit.PARALLEL_ASSETS['td']['sha256'] = sha256(path)
    with pytest.raises(ValueError):
        audit.audit(synthetic)


def test_parallel_audit_cli_refuses_to_overwrite_input(synthetic, monkeypatch):
    import sys
    target = synthetic / 'td.tif'
    before = target.read_bytes()
    monkeypatch.setattr(sys, 'argv', ['audit_parallel_candidates.py', str(synthetic), '--out', str(target)])
    assert audit.main() == 2
    assert target.read_bytes() == before


def test_saved_evidence_records_negative_not_approval():
    root = audit.Path(__file__).resolve().parents[1]
    report = json.loads((root / 'evidence/parallel_candidates_audit_20261028.json').read_text())
    for row in report['candidates'].values():
        assert row['dots_within_3px'] * 10 > row['candidate_dots_in_footprint'] * 7
        assert row['duplicate_over_70_percent'] and row['ok_to_submit'] is False


def test_cli_refuses_to_overwrite_input_rasters(synthetic, monkeypatch):
    import sys
    before = (synthetic / 'td.tif').read_bytes()
    monkeypatch.setattr(sys, 'argv', ['audit_parallel_candidates.py', str(synthetic), '--out', str(synthetic / 'td.tif')])
    assert audit.main() == 2
    assert (synthetic / 'td.tif').read_bytes() == before
    out = synthetic / 'nested/out.json'
    monkeypatch.setattr(sys, 'argv', ['audit_parallel_candidates.py', str(synthetic), '--out', str(out)])
    assert audit.main() == 0
    assert json.loads(out.read_text())['candidates']['td']['ok_to_submit'] is False
