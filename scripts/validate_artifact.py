"""Read-only, strict saved-byte format check. Does not certify scientific readiness."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import rasterio


def validate(candidate, template, footprint):
    with rasterio.open(template) as t, rasterio.open(candidate) as c, rasterio.open(footprint) as f:
        grid = lambda d: (d.crs, d.shape, d.transform)
        checks = {'geotiff': c.driver == 'GTiff', 'single_band': c.count == 1,
                  'float32': c.dtypes[0] == 'float32',
                  'crs_match': c.crs == t.crs and t.crs is not None,
                  'shape_match': c.shape == t.shape, 'transform_match': c.transform == t.transform,
                  'footprint_grid_match': grid(f) == grid(t) and f.count == 1}
        a = c.read(1)
        checks['all_values_finite'] = bool(np.isfinite(a).all())
        checks['all_values_in_range'] = bool((np.isfinite(a) & (a >= 0) & (a <= 1)).all())
        if checks['footprint_grid_match'] and checks['shape_match']:
            raw = f.read(1)
            # This validator expects an explicit 0/1 footprint covering the
            # whole grid. A nodata/mask on either 0 or 1 makes that ambiguous.
            checks['footprint_unmasked'] = bool((f.read_masks(1) != 0).all())
            valid = np.isfinite(raw) & (raw == 1)
            checks['footprint_binary'] = bool(np.isin(raw, [0, 1]).all())
            checks['footprint_nonempty'] = bool(valid.any())
            checks['no_nan_inside_footprint'] = bool(np.isfinite(a[valid]).all())
            # Raw values may be in range while GDAL's nodata or internal mask
            # hides them. A masked in-footprint prediction is not a valid value.
            checks['unmasked_inside_footprint'] = bool((c.read_masks(1)[valid] != 0).all())
        else:
            checks['no_nan_inside_footprint'] = False
            checks['unmasked_inside_footprint'] = False
        return {'sha256': hashlib.sha256(Path(candidate).read_bytes()).hexdigest(),
                'checks': checks, 'format_pass': all(checks.values()),
                'submission_ready': False,
                'note': 'Format only. Requires separate provenance, holdout, leakage, full-registry and selector gates.'}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('candidate'); p.add_argument('template'); p.add_argument('footprint')
    args = p.parse_args()
    result = validate(args.candidate, args.template, args.footprint)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['format_pass'] else 1)
