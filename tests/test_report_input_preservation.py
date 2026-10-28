"""Reporting commands must not destroy the evidence they assess."""
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def command(script, source, out):
    args = ['--audit', str(source)] if script == 'preflight.py' else [str(source)]
    return [sys.executable, str(ROOT / 'scripts' / script), *args, '--out', str(out)]


@pytest.mark.parametrize('script', ['preflight.py', 'release_gate.py'])
@pytest.mark.parametrize('alias', ['same', 'symlink', 'hardlink'])
def test_output_cannot_overwrite_input(tmp_path, script, alias):
    source = tmp_path / 'evidence.json'
    original = b'{"schema":"original-evidence"}\n'
    source.write_bytes(original)
    out = tmp_path / 'output.json'
    if alias == 'same':
        out = source
    elif alias == 'symlink':
        out.symlink_to(source)
    else:
        out.hardlink_to(source)
    result = subprocess.run(command(script, source, out), capture_output=True, text=True)
    assert result.returncode == (2 if script == 'preflight.py' else 1)
    assert 'must not overwrite' in result.stderr
    assert source.read_bytes() == original


@pytest.mark.parametrize('constant', ['NaN', 'Infinity', '-Infinity'])
def test_preflight_rejects_nonstandard_json_entirely(tmp_path, constant):
    source, out = tmp_path / 'audit.json', tmp_path / 'result.json'
    source.write_text('{"schema":"karage1-reference-audit-v1","extra":' + constant +
                      ',"lattice":{"coverage_fraction":0.9}}')
    result = subprocess.run(command('preflight.py', source, out), capture_output=True, text=True)
    assert result.returncode == 1
    card = json.loads(out.read_text())
    assert card['verdict'] == 'negative'
    assert card['correlation_overlap_vs_registry']['lattice_coverage_fraction'] is None
    assert not list(tmp_path.glob('*.tmp'))
