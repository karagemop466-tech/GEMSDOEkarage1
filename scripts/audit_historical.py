"""Re-read pinned historical bytes; no models or predictions are generated."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr


def load(path):
    with rasterio.open(path) as ds:
        return ds.read(1), (ds.crs, ds.shape, ds.transform, ds.count)


def main():
    audit = json.loads(Path('evidence/upstream_nine_site_audit.json').read_text())
    template, geometry = load('.cache/gems_data/sample_submission.tif')
    foot = np.isfinite(template)
    def fetch(row):
        path = Path('.cache/registry') / (row['site'] + '.tif')
        repo = 'buffedlizard55-lab/' + row['site']
        if not path.exists():
            result = subprocess.run(['gh', 'api', f"repos/{repo}/contents/{row['file']}?ref={row['github_ref']}", '-H', 'Accept: application/vnd.github.raw'], capture_output=True, check=True, timeout=120)
            path.write_bytes(result.stdout)
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row['sha256']:
            raise ValueError('Hash mismatch: ' + row['site'])
        arr, grid = load(path)
        values = arr[foot]
        return dict(site=row['site'], file=row['file'], ref=row['github_ref'], sha256=digest,
                    geometry_matches=grid == geometry, nan_inside=int(np.isnan(values).sum()),
                    finite_range_pass=bool(np.isfinite(values).all() and (values >= 0).all() and (values <= 1).all()),
                    all_cells_finite=bool(np.isfinite(arr).all()), dots=int(((arr > 0) & foot).sum())), ((arr > 0) & foot)
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        entries = list(pool.map(fetch, audit['sites']))
    masks = {row['site']: mask for row, mask in entries}
    pairs = []
    lattice, lattice_grid = load('.cache/registry/lattice.tif')
    if lattice_grid != geometry:
        raise ValueError('Lattice grid mismatch')
    within = distance_transform_edt(~((lattice > 0) & foot)) <= 3
    outside = int((foot & ~within).sum())
    lattice_results = {name: float(within[mask].mean()) for name, mask in masks.items()}
    for target, b in masks.items():
        near = distance_transform_edt(~b) <= 3
        for name, a in masks.items():
            if name == target:
                continue
            # Spearman on binary fields equals Pearson/phi; use scipy to retain tie semantics.
            rho = float(spearmanr(a[foot], b[foot]).statistic) if name < target else None
            overlap = float(near[a].mean())
            pairs.append(dict(candidate=name, registry=target, rank_correlation=rho,
                              directed_overlap_3px=overlap, duplicate=overlap > .70 or (rho is not None and abs(rho) > .90)))
    output = dict(classification='MEASURED GEOMETRY/UNIQUENESS AUDIT; not a score', footprint_pixels=int(foot.sum()),
                  template_sha256=hashlib.sha256(Path('.cache/gems_data/sample_submission.tif').read_bytes()).hexdigest(),
                  files=[row for row, _ in entries], comparisons=pairs,
                  lattice=dict(source='https://github.com/buffedlizard55-lab/13GEMSDOE/blob/92ee6f074323f161eed837b80ec3ee5b662e26f5/docs/downloads/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif',
                               sha256=hashlib.sha256(Path('.cache/registry/lattice.tif').read_bytes()).hexdigest(),
                               footprint_pixels_outside_3px=outside, fraction_covered=float(within[foot].mean()),
                               necessary_max_dot_count_for_70pct_overlap=outside / .30,
                               historical_directed_overlaps=lattice_results),
                  limitations=['Historical final binary dots only; pre-placement surfaces unavailable.',
                               'Pinned mirrors are not organizer-authenticated competition files.',
                               'Nine historical best files plus lattice, not the complete live registry.'])
    Path('evidence/historical_byte_audit.json').write_text(json.dumps(output, indent=2, allow_nan=False)+'\n')
    print(json.dumps(output['lattice'], indent=2))


if __name__ == '__main__':
    main()
