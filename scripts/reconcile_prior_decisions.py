#!/usr/bin/env python3
"""Compatibility entrypoint: reconcile the two independent negative audits.

The active decision is generated once by sync_review_status, rather than letting
parallel snapshot formats compete as separate current run cards.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.sync_review_status import main as sync_review_status


def main():
    prior = json.loads((ROOT/'evidence/prior_candidate_audit.json').read_text())
    current = json.loads((ROOT/'evidence/release_reassessment_20261028.json').read_text())
    for name in ('hmas', 'gpcz'):
        first, second = prior['results'][name], current['candidates'][name]
        if (first['sha256'] != second['sha256'] or first['dots'] != second['dots_in_footprint']
                or first['dots_within_closed_3px_disk'] != second['lattice_dots_within_3px_count']
                or first['directed_overlap_fraction'] != second['lattice_directed_overlap']):
            raise ValueError(f'independent audits disagree for {name}; stop and investigate')
    sync_review_status()


if __name__ == '__main__':
    main()
