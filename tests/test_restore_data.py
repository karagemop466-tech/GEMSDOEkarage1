"""Hermetic tests: no network, no competition data, no writes to the repository."""
import hashlib
import io
import json
import subprocess
from pathlib import Path

import pytest

from scripts import restore_karage1_data as restore

COMMIT = 'a' * 40


def entry(contents=b'abcdef', **overrides):
    base = {'id': 'fixture', 'dest': 'sub/file.tif', 'repo': 'owner/repo', 'ref': COMMIT,
            'path': 'remote/file.tif', 'sha256': hashlib.sha256(contents).hexdigest(),
            'bytes': len(contents)}
    return base | overrides


def test_flat_and_nested_split_restore_atomic(tmp_path, monkeypatch):
    calls = []
    def fake_fetch(repo, ref, path, out):
        calls.append((repo, ref, path))
        out.write({'p1': b'abc', 'p2': b'def'}[path])
    monkeypatch.setattr(restore, 'fetch_blob', fake_fetch)
    obj = entry(source={'kind': 'git_split_blob', 'repo': 'owner/repo', 'ref': COMMIT, 'parts': ['p1', 'p2']})
    rec = restore.restore_entry(obj, tmp_path)
    assert rec['status'] == 'restored' and (tmp_path / obj['dest']).read_bytes() == b'abcdef'
    assert [c[-1] for c in calls] == ['p1', 'p2']
    assert not list(tmp_path.rglob('*.partial'))
    # Exact bytes are reused, without calling the network a second time.
    assert restore.restore_entry(obj, tmp_path)['status'] == 'verified'
    assert len(calls) == 2
    assert restore.normalize_entry(entry(), tmp_path)['paths'] == ['remote/file.tif']


def test_corrupt_download_keeps_previous_file_and_no_predictable_symlink_write(tmp_path, monkeypatch):
    e = entry()
    target = tmp_path / e['dest']; target.parent.mkdir()
    target.write_bytes(b'previous')
    protected = tmp_path / 'protected'; protected.write_bytes(b'do not touch')
    (target.parent / (target.name + '.partial')).symlink_to(protected)
    monkeypatch.setattr(restore, 'fetch_blob', lambda repo, ref, path, out: out.write(b'bad'))
    with pytest.raises(ValueError, match='integrity mismatch'):
        restore.restore_entry(e, tmp_path)
    assert target.read_bytes() == b'previous'
    assert protected.read_bytes() == b'do not touch'
    assert sorted(p.name for p in target.parent.glob('*.partial')) == [target.name + '.partial']
    with pytest.raises(ValueError, match='mismatched'):
        restore.restore_entry(e, tmp_path, verify_only=True)


@pytest.mark.parametrize('change', [
    {'dest': '../escape'}, {'dest': '/absolute'}, {'dest': r'..\\escape'},
    {'sha256': 'x'*64}, {'bytes': 0}, {'bytes': True}, {'repo': '../repo'},
    {'ref': 'main'}, {'path': '../escape'}, {'path': '/absolute'},
    {'source': {'kind': 'git_split_blob', 'repo': 'a/b', 'ref': COMMIT, 'parts': []}},
])
def test_preflight_rejects_unpinned_or_unsafe(change, tmp_path):
    with pytest.raises(ValueError):
        restore.normalize_entry(entry(**change), tmp_path)


def test_existing_symlink_outside_root_is_rejected(tmp_path):
    root = tmp_path / 'data'; root.mkdir()
    external = tmp_path / 'outside'; external.mkdir()
    (root / 'sub').symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError, match='escapes'):
        restore.normalize_entry(entry(), root)


def test_fetch_retry_truncates_failed_partial(monkeypatch):
    calls = []
    def run(cmd, stdout, **kw):
        calls.append(cmd)
        if len(calls) == 1:
            stdout.write(b'broken')
            raise subprocess.CalledProcessError(1, cmd)
        stdout.write(b'valid')
    monkeypatch.setattr(restore.subprocess, 'run', run)
    monkeypatch.setattr(restore.time, 'sleep', lambda seconds: None)
    out = io.BytesIO(b'prefix'); out.seek(6)
    restore.fetch_blob('owner/repo', COMMIT, 'with space/name', out)
    assert out.getvalue() == b'prefixvalid'
    assert 'with%20space/name' in calls[0][2]


def test_cli_unknown_id_and_empty_manifest_fail_before_io(tmp_path, monkeypatch):
    manifest = tmp_path / 'manifest.json'
    manifest.write_text(json.dumps({'files': [entry()]}))
    monkeypatch.setattr('sys.argv', ['restore', '--manifest', str(manifest), '--data-dir', str(tmp_path/'out'), '--id', 'missing'])
    assert restore.main() == 2
    assert not (tmp_path / 'out').exists()
    manifest.write_text('{"files": []}')
    assert restore.main() == 2
