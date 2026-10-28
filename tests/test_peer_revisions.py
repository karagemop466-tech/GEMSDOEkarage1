"""Revision monitoring never implies a score, registry pass or slot approval."""
import copy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts import check_peer_revisions as monitor

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_has_nine_exact_immutable_pins():
    pins = monitor.load_pins(ROOT / 'registry/reference_assets.json')
    assert [row['site'] for row in pins] == list(monitor.SITES)
    assert all(monitor.SHA.fullmatch(row['audit_commit']) for row in pins)
    assert len({row['repo'] for row in pins}) == 9


@pytest.mark.parametrize('mutation', ['missing', 'duplicate', 'branch', 'wrong_repo', 'not_list'])
def test_bad_manifest_fails_closed(tmp_path, mutation):
    rows = json.loads((ROOT / 'registry/reference_assets.json').read_text())
    if mutation == 'missing':
        rows = [r for r in rows if r.get('id') != 'GEMSDOE24']
    elif mutation == 'duplicate':
        rows.append(next(r for r in rows if r.get('id') == 'GEMSDOE24'))
    elif mutation == 'branch':
        next(r for r in rows if r.get('id') == 'GEMSDOE24')['ref'] = 'main'
    elif mutation == 'wrong_repo':
        next(r for r in rows if r.get('id') == 'GEMSDOE24')['repo'] = 'attacker/repo'
    else:
        rows = {'not': 'a list'}
    path = tmp_path / 'manifest.json'
    path.write_text(json.dumps(rows))
    with pytest.raises(ValueError):
        monitor.load_pins(path)


def test_success_changed_and_failure_are_distinct():
    pins = monitor.load_pins(ROOT / 'registry/reference_assets.json')
    def lookup(repo):
        if repo.endswith('24'):
            return pins[0]['audit_commit']
        if repo.endswith('25'):
            return 'f' * 40
        if repo.endswith('27'):
            raise subprocess.TimeoutExpired('gh', 30)
        if repo.endswith('28'):
            return 'not a sha'
        raise OSError('unavailable')
    report = monitor.check(pins, lookup)
    assert [r['status'] for r in report['sites'][:4]] == [
        'at_audit_pin', 'changed', 'unavailable', 'unavailable']
    assert report['counts'] == {'at_audit_pin': 1, 'changed': 1, 'unavailable': 7}
    assert report['sites'][2]['head'] is None
    assert report['ok_to_submit'] is False and report['slot_selected'] is False
    assert 'score' in report['scope'] and 'not a raster' in report['scope']
    json.dumps(report, allow_nan=False)


def test_cli_writes_a_negative_receipt_even_if_sources_are_unavailable(tmp_path, monkeypatch, capsys):
    out = tmp_path / 'receipt.json'
    monkeypatch.setattr(monitor, 'github_head', lambda repo: (_ for _ in ()).throw(OSError('offline')))
    monkeypatch.setattr(sys, 'argv', ['check_peer_revisions.py', '--out', str(out)])
    assert monitor.main() == 1
    receipt = json.loads(out.read_text())
    assert receipt['counts']['unavailable'] == 9
    assert not receipt['ok_to_submit'] and not receipt['slot_selected']
    assert json.loads(capsys.readouterr().out)['unavailable'] == 9
    assert not list(tmp_path.glob('*.partial'))


def test_cli_changed_revision_is_nonzero_but_all_at_pin_is_only_freshness(tmp_path, monkeypatch):
    pins = monitor.load_pins(ROOT / 'registry/reference_assets.json')
    by_repo = {row['repo']: row['audit_commit'] for row in pins}
    out = tmp_path / 'receipt.json'
    monkeypatch.setattr(sys, 'argv', ['check_peer_revisions.py', '--out', str(out)])
    monkeypatch.setattr(monitor, 'github_head', lambda repo: by_repo[repo])
    assert monitor.main() == 0
    assert json.loads(out.read_text())['ok_to_submit'] is False
    # A real changed HEAD is not an unavailable lookup, but must still mark the
    # audit comparison as stale and leave the receipt available for review.
    monkeypatch.setattr(monitor, 'github_head', lambda repo: 'f' * 40 if repo.endswith('24') else by_repo[repo])
    assert monitor.main() == 1
    receipt = json.loads(out.read_text())
    assert receipt['counts'] == {'at_audit_pin': 8, 'changed': 1, 'unavailable': 0}
    assert receipt['ok_to_submit'] is False


def test_evidence_snapshot_is_explicitly_not_current_permission():
    receipt = json.loads((ROOT / 'evidence/peer_revisions_20261028.json').read_text())
    expected = monitor.load_pins(ROOT / 'registry/reference_assets.json')
    assert len(receipt['sites']) == len(expected)
    for actual, pin in zip(receipt['sites'], expected):
        assert all(actual[key] == pin[key] for key in pin)
        assert actual['status'] in ('at_audit_pin', 'changed', 'unavailable')
    assert receipt['counts']['changed'] == 9
    assert receipt['counts']['unavailable'] == 0
    assert receipt['ok_to_submit'] is False and receipt['slot_selected'] is False
    later = json.loads((ROOT / 'evidence/peer_revisions_20261028_1640.json').read_text())
    assert later['counts'] == {'at_audit_pin': 0, 'changed': 9, 'unavailable': 0}
    assert later['checked_utc'] > receipt['checked_utc']
    assert {a['site'] for a, b in zip(receipt['sites'], later['sites']) if a['head'] != b['head']} == {
        'GEMSDOE25', 'GEMSDOE32', 'GEMSDOE33', 'GEMSDOE36'}
    assert later['ok_to_submit'] is False and later['slot_selected'] is False
