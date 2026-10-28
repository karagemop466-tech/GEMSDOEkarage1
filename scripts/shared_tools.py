"""Bootstrap and invoke pinned shared tools, never copy or fork their implementation."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / '.work/template'


def bootstrap():
    pin = json.loads((ROOT / 'registry/template.json').read_text())
    if not TEMPLATE.exists():
        TEMPLATE.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', '--no-checkout', 'https://github.com/' + pin['repository'] + '.git', str(TEMPLATE)], check=True)
        subprocess.run(['git', '-C', str(TEMPLATE), 'checkout', '--detach', pin['commit']], check=True)
    actual = subprocess.check_output(['git', '-C', str(TEMPLATE), 'rev-parse', 'HEAD'], text=True).strip()
    if actual != pin['commit']:
        raise SystemExit('Template commit mismatch; refusing execution')
    if subprocess.check_output(['git', '-C', str(TEMPLATE), 'status', '--porcelain'], text=True).strip():
        raise SystemExit('Shared template has modifications; no private fork permitted')


def preflight():
    pin = json.loads((ROOT / 'registry/template.json').read_text())
    needed = [ROOT / '.cache/gems_work/feature_stack.npy', ROOT / '.cache/gems_data/existing_faults.tif',
              ROOT / '.cache/gems_data/training_features.tif',
              ROOT / '.cache/gems_data/sample_submission.tif', ROOT / '.cache/gems_data/labels.tif']
    lane = pin.get('method_lane')
    lane_valid = isinstance(lane, str) and bool(lane.strip())
    missing, empty, unreadable = [], [], []
    for path in needed:
        name = str(path.relative_to(ROOT))
        try:
            if not path.is_file():
                missing.append(name)
            else:
                # An interrupted download or touch-created placeholder is not
                # usable input. Do not load the stack here: this remains a
                # lightweight preflight, not format/provenance validation.
                with path.open('rb') as source:
                    if not source.read(1):
                        empty.append(name)
        except OSError:
            unreadable.append(name)
    return {'lane': lane, 'missing': missing, 'empty': empty, 'unreadable': unreadable,
            'template_commit': pin['commit'],
            'ready_for_shared_tools': lane_valid and not (missing or empty or unreadable),
            'ok_to_submit': False,
            'scope': 'Readable nonempty input presence and lane only; not format, provenance, scientific validation or slot selection.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['bootstrap', 'preflight', 'evaluate', 'write'])
    parser.add_argument('args', nargs=argparse.REMAINDER)
    opts = parser.parse_args()
    if opts.command == 'bootstrap':
        bootstrap()
        return
    report = preflight()
    if opts.command == 'preflight':
        print(json.dumps(report, indent=2))
        return 0 if report['ready_for_shared_tools'] else 1
    if not report['ready_for_shared_tools']:
        raise SystemExit('BLOCKED: lane / cached inputs missing, empty or unreadable. ' + json.dumps(report))
    bootstrap()
    target = 'evaluate_holdout.py' if opts.command == 'evaluate' else 'submission_writer.py'
    env = dict(os.environ, GEMS_DATA_DIR=str(ROOT / '.cache/gems_data'), GEMS_WORK_DIR=str(ROOT / '.cache/gems_work'))
    subprocess.run([sys.executable, str(TEMPLATE / 'scripts' / target), *opts.args], env=env, check=True)


if __name__ == '__main__':
    raise SystemExit(main())
