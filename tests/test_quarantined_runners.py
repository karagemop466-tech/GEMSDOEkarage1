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


def test_incomplete_registry_cannot_certify_preplacement(tmp_path):
    import rasterio
    from rasterio.transform import from_origin
    from gemskarage1.registry_audit import check_preplacement_surface
    a = np.arange(9, dtype='float32').reshape(3, 3)
    sample = tmp_path / 'synthetic.tif'
    with rasterio.open(sample, 'w', driver='GTiff', count=1, dtype='float32', width=3, height=3,
                       crs='EPSG:32611', transform=from_origin(0, 300, 100, 100)) as dst:
        dst.write(a, 1)
    report = check_preplacement_surface(a, np.ones((3, 3), bool), sample, registry_index=None)
    assert report['passed'] is False


def test_old_gpcz_registry_scan_cannot_exempt_lattice():
    from gemsk.uniqueness import check
    with pytest.raises(RuntimeError, match='exempted the lattice'):
        check(np.zeros((2, 2), dtype=bool))
