"""Read-only provenance checks, including corrupt manifests and unsafe paths."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.audit_template_integrity import audit

ROOT = Path(__file__).resolve().parents[1]


def fixture(root):
    (root / 'vendor').mkdir()
    (root / 'registry').mkdir()
    payload = root / 'vendor/tool.py'
    payload.write_bytes(b'# fixture only\n')
    pin = {'repository': 'fixture/repo', 'commit': 'a' * 40, 'method_lane': 'fixture'}
    provenance = {'source_repo': pin['repository'], 'source_commit': pin['commit'],
                  'files': {'vendor/tool.py': hashlib.sha256(payload.read_bytes()).hexdigest()}}
    (root / 'registry/template.json').write_text(json.dumps(pin))
    (root / 'vendor/PROVENANCE.json').write_text(json.dumps(provenance))
    return payload, provenance


def test_matching_pins_are_not_authorization(tmp_path):
    fixture(tmp_path)
    report = audit(tmp_path)
    assert report['file_pins_match'] and not report['execution_authorized']


def test_changed_or_missing_bytes_do_not_repin(tmp_path):
    payload, _ = fixture(tmp_path)
    manifest = tmp_path / 'vendor/PROVENANCE.json'
    before = manifest.read_bytes()
    payload.write_bytes(b'changed')
    assert not audit(tmp_path)['file_pins_match']
    assert manifest.read_bytes() == before
    payload.unlink()
    assert audit(tmp_path)['files'][0]['actual_sha256'] is None


@pytest.mark.parametrize('path', ['vendor/../outside', '/absolute', 'vendor/../../outside'])
def test_unsafe_paths_fail_closed(tmp_path, path):
    _, provenance = fixture(tmp_path)
    provenance['files'] = {path: 'a' * 64}
    (tmp_path / 'vendor/PROVENANCE.json').write_text(json.dumps(provenance))
    result = audit(tmp_path)
    assert not result['execution_authorized'] and not result['file_pins_match']


def test_missing_manifest_fails_closed(tmp_path):
    assert not audit(tmp_path)['execution_authorized']


def test_current_receipt_replays_and_tools_cannot_run():
    saved = json.loads((ROOT / 'evidence/template_integrity_20261028.json').read_text())
    assert audit(ROOT) == saved
    assert {r['path'] for r in saved['files'] if not r['matches']} == {
        'vendor/gems57/uniqueness.py', 'vendor/gems57/submission_writer.py'}
    for stage in ('evaluate', 'write'):
        result = subprocess.run([sys.executable, 'scripts/shared_tools.py', stage],
                                cwd=ROOT, text=True, capture_output=True)
        assert result.returncode != 0 and 'BLOCKED' in result.stderr
        assert 'shared-template provenance' in result.stderr


def test_partial_manifest_cannot_report_all_pins_match(tmp_path):
    _, provenance = fixture(tmp_path)
    provenance['files']['vendor/zzz/../../escape'] = 'a' * 64
    (tmp_path / 'vendor/PROVENANCE.json').write_text(json.dumps(provenance))
    result = audit(tmp_path)
    assert result['files'][0]['matches']  # earlier valid row does not clear the manifest
    assert not result['file_pins_match'] and not result['execution_authorized']


def test_superseded_conduitcrest_generator_stops_before_writes():
    candidate = ROOT / 'docs/downloads/gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4-zeros.tif'
    latest = ROOT / 'docs/data/latest-run-card.json'
    before_candidate = hashlib.sha256(candidate.read_bytes()).hexdigest()
    before_latest = latest.read_bytes()
    result = subprocess.run([sys.executable, 'scripts/build_unique_submission.py'],
                            cwd=ROOT, text=True, capture_output=True)
    assert result.returncode == 2
    assert '99.3454% lattice overlap' in result.stderr
    assert hashlib.sha256(candidate.read_bytes()).hexdigest() == before_candidate
    assert latest.read_bytes() == before_latest
