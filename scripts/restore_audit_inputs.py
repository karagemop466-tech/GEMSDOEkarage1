"""Restore only pinned historical-audit inputs; does not build a feature stack."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

from shared_tools import bootstrap, TEMPLATE, ROOT


def main():
    bootstrap()
    spec = importlib.util.spec_from_file_location('shared_restore', TEMPLATE / 'scripts/restore_data.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manifest = json.loads((TEMPLATE / 'registry/data_manifest.json').read_text())
    receipts = []
    for entry in manifest['files']:
        if entry['id'] in ('sample_submission', 'labels'):
            receipts.append(module.restore_entry(entry, ROOT / '.cache/gems_data'))
    path = ROOT / '.cache/registry/lattice.tif'
    path.parent.mkdir(parents=True, exist_ok=True)
    expected = 'b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2'
    if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        result = subprocess.run(['gh','api', 'repos/buffedlizard55-lab/13GEMSDOE/contents/docs/downloads/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif?ref=92ee6f074323f161eed837b80ec3ee5b662e26f5', '-H', 'Accept: application/vnd.github.raw'], capture_output=True, check=True, timeout=120)
        if hashlib.sha256(result.stdout).hexdigest() != expected:
            raise SystemExit('Lattice bytes do not match pinned hash')
        path.write_bytes(result.stdout)
    print(json.dumps(receipts, indent=2))


if __name__ == '__main__':
    main()
