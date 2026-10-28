#!/usr/bin/env python3
"""Recheck saved candidate bytes against the pinned registry lattice.

This is a format/geometry audit, not a geological experiment, score, or proof
of a complete registry. A known duplicate witness suffices to reject a file;
absence of one does not approve it. Sources are peer mirrors, not authenticated
organizer files. `--fetch` uses immutable GitHub refs and verifies each hash.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.audit_references import (  # noqa: E402
    binary_rank_correlation, binary_support, disk, fetch_files, load_manifest,
    minimum_overlap, read_grid, same_grid, sha256, verify_file,
)
from scripts.validate_geotiff import diagnose  # noqa: E402

CANDIDATES = {
    "hmas": "docs/downloads/karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif",
    "gpcz": "docs/downloads/gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif",
}


def audit(cache: Path) -> dict:
    """Reopen and measure both persisted rasters; raise on invalid inputs."""
    entries = {e['id']: e for e in load_manifest(ROOT / 'registry/reference_assets.json')}
    for key in ('template', 'lattice'):
        verify_file(cache / f'{key}.tif', entries[key])
    with rasterio.open(cache / 'template.tif') as ds:
        template = ds.read(1, masked=True)
        footprint = ~np.ma.getmaskarray(template) & np.isfinite(template.data)
    if not footprint.any() or footprint.all():
        raise ValueError('invalid or unbounded template footprint')
    _, template_meta = read_grid(cache / 'template.tif')
    lattice, lattice_meta = read_grid(cache / 'lattice.tif')
    if not same_grid(lattice_meta, template_meta):
        raise ValueError('lattice grid does not match template')
    lattice_dots = binary_support(lattice, footprint, 'lattice')
    if not lattice_dots.any():
        raise ValueError('empty lattice')
    nearby = binary_dilation(lattice_dots, structure=disk(3))
    uncovered = int(np.count_nonzero(footprint & ~nearby))
    results = {}
    for name, relative in CANDIDATES.items():
        path = ROOT / relative
        values, meta = read_grid(path)
        if not same_grid(meta, template_meta):
            raise ValueError(f'{name}: raster grid mismatch')
        dots = binary_support(values, footprint, name)
        count = int(dots.sum())
        if not count:
            raise ValueError(f'{name}: no prediction dots')
        hit_count = int(np.count_nonzero(dots & nearby))
        fmt = diagnose(path, cache / 'template.tif', entries['template']['sha256'])
        # diagnose records absolute candidate paths when supplied; keep a
        # checkout-independent filename and a mirror label in committed JSON.
        fmt['candidate'] = relative
        fmt['template'] = 'pinned peer mirror: ' + entries['template']['path']
        results[name] = {
            'file': relative,
            'sha256': sha256(path),
            'dots': count,
            'dots_within_closed_3px_disk': hit_count,
            'directed_overlap_fraction': hit_count / count,
            'binary_spearman_vs_lattice': binary_rank_correlation(dots, lattice_dots, footprint),
            'lattice_rule_exceeded': hit_count * 10 > count * 7,
            'pigeonhole_bound': minimum_overlap(count, uncovered),
            'surface_correlation': None,
            'surface_status': 'not replayed; the pre-placement surface is not available in this checkout',
            'format_diagnostic': fmt,
            'verdict': 'negative',
            'ok_to_submit': False,
        }
    return {
        'schema': 'karage1-prior-candidate-audit-v1',
        'created_utc': datetime.now(timezone.utc).isoformat(),
        'scope': 'One pinned registry lattice is a decisive duplicate witness, not a complete registry audit.',
        'source_authenticity': 'Pinned GitHub peer mirrors; not organizer-authenticated.',
        'reference_sources': {k: entries[k] for k in ('template', 'lattice')},
        'footprint_pixels': int(footprint.sum()),
        'lattice_dots': int(lattice_dots.sum()),
        'footprint_pixels_outside_closed_3px_disk': uncovered,
        'overlap_rule': 'candidate dots within Euclidean distance <= 3 pixels; strictly > 70% fails',
        'results': results,
        'geological_experiments_this_session': 0,
        'portal_submissions_this_session': 0,
        'selector_decision_made': False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cache', type=Path, default=ROOT / '.cache' / 'prior-audit')
    ap.add_argument('--fetch', action='store_true', help='Fetch and hash-check the pinned template and lattice')
    ap.add_argument('--out', type=Path, default=ROOT / 'evidence' / 'prior_candidate_audit.json')
    args = ap.parse_args()
    try:
        if args.fetch:
            entries = load_manifest(ROOT / 'registry/reference_assets.json')
            fetch_files([e for e in entries if e['id'] in ('template', 'lattice')], args.cache)
        result = audit(args.cache)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        temp = args.out.with_name(args.out.name + '.tmp')
        temp.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
        temp.replace(args.out)
    except (OSError, ValueError) as exc:
        print(f'AUDIT FAILED (no release): {exc}', file=sys.stderr)
        return 2
    for name, item in result['results'].items():
        print(f"{name}: {item['dots_within_closed_3px_disk']:,}/{item['dots']:,} "
              f"({item['directed_overlap_fraction']:.4%}); verdict={item['verdict']}")
    print(f"Report: {args.out}; no portal submission or slot selection.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
