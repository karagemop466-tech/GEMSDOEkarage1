"""Independent historical raster audit, NOT a holdout evaluator or submission writer."""
import hashlib
import json
from pathlib import Path
import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]


def overlap(candidate, reference, footprint):
    """Directional fraction of candidate dots within Euclidean 3 px of reference."""
    a, b = candidate & footprint, reference & footprint
    if not a.any():
        return None
    if not b.any():
        return 0.0
    return float(np.count_nonzero(a & (distance_transform_edt(~b) <= 3)) / a.sum())


def binary_spearman(a, b, footprint):
    # Pearson on binary values equals Spearman on their two sets of midranks.
    x, y = a[footprint], b[footprint]
    n = len(x)
    nx, ny = int(x.sum()), int(y.sum())
    den = float(nx * ny * (n-nx) * (n-ny)) ** .5
    return (n * int((x & y).sum()) - nx * ny) / den if den else None


def main():
    manifest = json.loads((ROOT/'docs/data/sources.json').read_text())
    masks, footprints, grids, reports = [], [], [], []
    for row in manifest['sites']:
        path = ROOT/'.research/rasters'/row['artifact']
        if hashlib.sha256(path.read_bytes()).hexdigest() != row['artifact_sha256']:
            raise ValueError('Artifact integrity failure')
        with rasterio.open(path) as ds:
            a = ds.read(1)
            unmasked = ds.read_masks(1) != 0
            finite = unmasked & np.isfinite(a)
            # Shared footprint established below from NaN-outside artifacts.
            grids.append((str(ds.crs), ds.shape, tuple(ds.transform)))
            masks.append(finite & (a > 0))
            footprints.append(finite)
            reports.append({'site': row['site'], 'sha256': row['artifact_sha256'],
                            'bands': ds.count, 'crs': str(ds.crs), 'shape': list(ds.shape),
                            'transform': list(ds.transform), 'nan_count': int(np.isnan(a).sum()),
                            'all_finite': bool(np.isfinite(a).all() and unmasked.all()),
                            'finite_range_valid': bool(((a[finite] >= 0) & (a[finite] <= 1)).all()),
                            'binary': bool(np.isin(a[finite], [0, 1]).all())})
    if not all(r['binary'] and r['bands'] == 1 for r in reports):
        raise ValueError('Historical binary-mask audit cannot process nonbinary/multiband rasters')
    if len(set(grids)) != 1:
        raise ValueError('Grid mismatch: cannot compare masks')
    # A peer-derived domain is adequate for historical comparison, not official validation.
    footprint = np.logical_and.reduce(footprints)
    for i, r in enumerate(reports):
        r['dots'] = int(masks[i].sum())
        r['comparisons'] = []
        for j, other in enumerate(reports):
            if i == j:
                continue
            r['comparisons'].append({'site': other['site'],
                'same_dot_mask': bool(np.array_equal(masks[i], masks[j])),
                'spearman': binary_spearman(masks[i], masks[j], footprint),
                'within_3px_fraction': overlap(masks[i], masks[j], footprint)})
        if any(c['within_3px_fraction'] is None or c['spearman'] is None for c in r['comparisons']):
            raise ValueError(f"Undefined comparison metric in historical raster audit: {r['site']}")
        r['literal_duplicate'] = any(c['within_3px_fraction'] > .70 or
                                     abs(c['spearman']) > .90 for c in r['comparisons'])
    out = {'version': 'historical-mask-audit-v1',
           'domain': 'intersection of finite peer pixels; NOT organizer-authenticated footprint',
           'footprint_pixels': int(footprint.sum()), 'surface_check': 'unavailable: source surfaces absent',
           'score_estimation': 'not estimable', 'rasters': reports}
    (ROOT/'docs/data/raster_audit.json').write_text(json.dumps(out, indent=2, allow_nan=False)+'\n')
    by_site = dict(zip((r['site'] for r in reports), masks))
    b, d, c = (by_site[s] for s in ('GEMSDOE32', 'GEMSDOE25', 'GEMSDOE36'))
    forensic = {'measurement_type': 'binary-mask set comparison, not a performance score',
                'b2_subset_of_gems25': bool(np.all(~b | d)),
                'gems25_dots_removed_for_b2': int((d & ~b).sum()),
                'b2_subset_of_gems36': bool(np.all(~b | c)),
                'gems36_additional_dots': int((c & ~b).sum())}
    (ROOT/'docs/data/b2_forensics.json').write_text(json.dumps(forensic, indent=2)+'\n')



if __name__ == '__main__':
    main()
