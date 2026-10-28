from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts.restore_karage1_data import normalize_entry, restore_entry


def fixture_entry(payload: bytes, **overrides):
    result = dict(id='test', repo='owner/repo', ref='a' * 40, path='data/file.bin',
                  dest='nested/file.bin', bytes=len(payload), sha256=hashlib.sha256(payload).hexdigest())
    result.update(overrides)
    return result


def test_restore_both_manifest_layouts_and_verify_only(tmp_path):
    data = b'first-second'
    e = fixture_entry(data, parts=['data/one', 'data/two'])
    e.pop('path')
    calls = []
    def fetch(repo, ref, path, out):
        calls.append((repo, ref, path))
        out.write({'data/one': b'first-', 'data/two': b'second'}[path])
    result = restore_entry(e, tmp_path, fetcher=fetch)
    assert result['status'] == 'restored'
    assert (tmp_path/'nested/file.bin').read_bytes() == data
    assert len(calls) == 2
    assert restore_entry(e, tmp_path, verify_only=True)['status'] == 'verified'

    nested = fixture_entry(data)
    nested['source'] = dict(kind='git_blob', repo=nested.pop('repo'), ref=nested.pop('ref'),
                            path=nested.pop('path'))
    assert restore_entry(nested, tmp_path, verify_only=True)['status'] == 'verified'


def test_hash_mismatch_preserves_existing_file_and_removes_partial(tmp_path):
    e = fixture_entry(b'correct')
    target = tmp_path/'nested/file.bin'
    target.parent.mkdir()
    target.write_bytes(b'old')
    def bad(repo, ref, path, out):
        out.write(b'incorrect')
    with pytest.raises(ValueError, match='SHA-256'):
        restore_entry(e, tmp_path, fetcher=bad)
    assert target.read_bytes() == b'old'
    assert not list(target.parent.glob('*.partial'))
    with pytest.raises(ValueError, match='mismatched'):
        restore_entry(e, tmp_path, verify_only=True)


@pytest.mark.parametrize('field,value', [
    ('ref','main'), ('dest','../escape'), ('path','../source'),
    ('sha256','deadbeef'), ('bytes',0), ('repo','owner/../x'),
])
def test_unpinned_or_unsafe_entries_fail(field,value):
    e = fixture_entry(b'data'); e[field] = value
    with pytest.raises(ValueError):
        normalize_entry(e)


def test_actual_manifest_is_fully_normalizable():
    root = Path(__file__).resolve().parents[1]
    data = json.loads((root/'registry/karage1_data_manifest.json').read_text())
    entries = [normalize_entry(e) for e in data['files']]
    assert len(entries) == 31
    assert len({e['dest'] for e in entries}) == len(entries)
    assert all(len(e['source']['ref']) == 40 for e in entries)


def test_concurrent_restore_uses_independent_atomic_staging(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    payload = b'a deterministic synthetic payload'
    entry = fixture_entry(payload)
    barrier = Barrier(2)
    def fetch(repo, ref, path, out):
        barrier.wait(timeout=5)
        out.write(payload)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: restore_entry(entry, tmp_path, fetcher=fetch), range(2)))
    assert [r['status'] for r in results] == ['restored', 'restored']
    assert (tmp_path / entry['dest']).read_bytes() == payload
    assert not list((tmp_path / 'nested').glob('*.partial'))
