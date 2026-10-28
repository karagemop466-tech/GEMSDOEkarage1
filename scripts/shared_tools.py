"""Bootstrap and invoke pinned shared tools, never copy or fork their implementation."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
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
    needed = [ROOT / '.cache/gems_work/feature_stack.npy', ROOT / '.cache/gems_data/training_features.tif',
              ROOT / '.cache/gems_data/sample_submission.tif', ROOT / '.cache/gems_data/labels.tif']
    # The vendored evaluator and the execution pin came from different peer
    # lineages. Never choose one silently or repair its provenance by repinning.
    from scripts.audit_template_integrity import audit
    integrity = audit(ROOT)
    return {'lane': pin.get('method_lane'), 'missing': [str(p.relative_to(ROOT)) for p in needed if not p.is_file()],
            'template_commit': pin['commit'], 'template_integrity': integrity}


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
        return
    if not report['lane'] or report['missing'] or not report['template_integrity']['execution_authorized']:
        raise SystemExit('BLOCKED: lane, cached inputs or authoritative shared-template provenance unresolved. ' + json.dumps(report))
    bootstrap()
    target = 'evaluate_holdout.py' if opts.command == 'evaluate' else 'submission_writer.py'
    env = dict(os.environ, GEMS_DATA_DIR=str(ROOT / '.cache/gems_data'), GEMS_WORK_DIR=str(ROOT / '.cache/gems_work'))
    subprocess.run([sys.executable, str(TEMPLATE / 'scripts' / target), *opts.args], env=env, check=True)


if __name__ == '__main__':
    main()
