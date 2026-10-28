#!/usr/bin/env python3
"""Read-only audit of inherited template pins; never updates pins to fit bytes.

Matching these hashes establishes consistency with a local manifest, not that
an organizer or the parallel-run owner authorized this template.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def audit(root: Path = ROOT) -> dict:
    root = root.resolve()
    problems, rows = [], []
    try:
        provenance = json.loads((root / 'vendor/PROVENANCE.json').read_text())
        template = json.loads((root / 'registry/template.json').read_text())
        pins = provenance['files']
        if not isinstance(pins, dict) or not pins:
            raise ValueError('empty or malformed file pins')
        for relative, expected in sorted(pins.items()):
            if (not isinstance(relative, str) or not relative.startswith('vendor/')
                    or Path(relative).is_absolute() or '..' in Path(relative).parts
                    or not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected)):
                raise ValueError('unsafe path or invalid SHA-256 in provenance')
            path = root / relative
            if not path.resolve().is_relative_to(root / 'vendor'):
                raise ValueError('provenance path escapes vendor directory')
            actual = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
            rows.append({'path': relative, 'expected_sha256': expected,
                         'actual_sha256': actual, 'matches': actual == expected})
        if any(not row['matches'] for row in rows):
            problems.append('Vendored bytes differ from recorded immutable provenance; do not repin without upstream review.')
        if (provenance.get('source_repo'), provenance.get('source_commit')) != (
                template.get('repository'), template.get('commit')):
            problems.append('Vendored source and execution-template pin identify different repositories or commits.')
        if not template.get('method_lane'):
            problems.append('Assigned method lane is absent.')
        # No authorization is inferred from a successful file-hash comparison.
        problems.append('Authoritative shared-template assignment and upstream repair approval are not established by this audit.')
    except (OSError, ValueError, TypeError, KeyError) as exc:
        problems.append(f'Template provenance unavailable or invalid: {exc}')
    return {'schema': 'karage1-template-integrity-v1', 'files': rows,
            'file_pins_match': bool(rows) and all(row['matches'] for row in rows),
            'problems': problems, 'execution_authorized': False,
            'scope': 'Local provenance consistency only; no organizer authentication or upstream changes.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = audit()
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text)
    print(text, end='')
    return 0 if result['execution_authorized'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
