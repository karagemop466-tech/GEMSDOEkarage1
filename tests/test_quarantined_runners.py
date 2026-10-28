"""A duplicate STOP cannot be bypassed by an old lane entry point."""
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('command', [
    ['scripts/prepare_data.py'],
    ['scripts/run_karage1_experiments.py', '--stage', 'fit'],
    ['scripts/run_karage1_experiments.py', '--stage', 'eval'],
    ['scripts/run_experiment1_screen.py'],
    ['scripts/run_experiment2_gpcz.py'],
    ['scripts/run_experiment3_build.py'],
])
def test_old_experiment_entrypoints_fail_closed(command):
    result = subprocess.run([sys.executable, *command], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode != 0
    assert 'BLOCKED' in result.stderr


def test_old_registry_scanner_cannot_certify_incomplete_inventory(tmp_path):
    from gemskarage1.registry_audit import run_full_fleet_uniqueness_gate
    a = np.zeros((2, 2), dtype='float32')
    with pytest.raises(RuntimeError, match='disabled'):
        run_full_fleet_uniqueness_gate(a, a, tmp_path / 'missing.tif', np.ones((2, 2), bool))


def test_old_gpcz_registry_scan_cannot_exempt_lattice():
    from gemsk.uniqueness import check
    with pytest.raises(RuntimeError, match='exempted the lattice'):
        check(np.zeros((2, 2), dtype=bool))
