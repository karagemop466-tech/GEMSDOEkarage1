#!/usr/bin/env python3
"""Null-model audit of the literal 70% / 3-px registry-overlap gate.

Question: does the gate in ``gems57.uniqueness`` distinguish a candidate from
noise? It is measured against the 13GEMS lattice raster (the registry raster
whose coverage of the footprint is largest). Random dot sets drawn uniformly
from the scored footprint are used as the null.

Also records two raster facts used elsewhere in the review: the count of
``-3.4028235e+38`` sentinel pixels inside the footprint of ``training_features``
(an earlier session reported 3,073), and the byte identity of ``labels.tif``
and ``existing_faults.tif``.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57.metric import RADIUS_PX  # noqa: E402

DATA = ROOT / "data"
LATTICE = DATA / "scored" / "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
OUT = ROOT / "evidence" / "lattice_gate_null_check_20261029.json"
SENTINEL = -3.4028234663852886e38


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    with rasterio.open(DATA / "sample_submission.tif") as ds:
        fp = np.isfinite(ds.read(1))
    with rasterio.open(LATTICE) as ds:
        lat = ds.read(1)
    support = np.isfinite(lat) & (lat > 0) & fp
    dist = distance_transform_edt(~support)
    covered = (dist <= RADIUS_PX) & fp
    rng = np.random.default_rng(20261029)
    idx = np.flatnonzero(fp)
    null = {}
    for n in (1_000, 37_654, 60_988):
        draws = []
        for _ in range(200):
            s = rng.choice(idx, size=n, replace=False)
            draws.append(float((dist.flat[s] <= RADIUS_PX).mean()))
        null[str(n)] = dict(mean=float(np.mean(draws)), min=float(np.min(draws)), max=float(np.max(draws)),
                            draws=200, rule_threshold=0.70, fails_gate_in_all_draws=bool(min(draws) > 0.70))

    with rasterio.open(DATA / "training_features.tif") as ds:
        feat = ds.read(1)
    sentinel_in_fp = int(((feat <= SENTINEL * 0.999) & fp).sum())
    # Distinct footprint pixels with the sentinel in ANY band (union), plus per-band sums.
    any_sentinel = np.zeros(fp.shape, bool)
    per_band_sum = 0
    with rasterio.open(DATA / "training_features.tif") as ds:
        for b in range(1, ds.count + 1):
            hit = (ds.read(b) <= SENTINEL * 0.999) & fp
            per_band_sum += int(hit.sum())
            any_sentinel |= hit

    result = dict(
        check="lattice_gate_null_model",
        status="DIAGNOSTIC — the literal gate is non-informative: uniform random dots also fail it",
        lattice_file=str(LATTICE.relative_to(ROOT)),
        lattice_sha256=sha256(LATTICE),
        footprint_pixels=int(fp.sum()),
        lattice_support_pixels_in_footprint=int(support.sum()),
        footprint_fraction_within_3px_of_lattice=float(covered.sum() / fp.sum()),
        footprint_pixels_beyond_3px=int((fp & ~covered).sum()),
        random_dot_null=null,
        training_features_sentinel_pixels_in_footprint_band1=sentinel_in_fp,
        training_features_sentinel_distinct_pixels_in_footprint_any_band=int(any_sentinel.sum()),
        training_features_sentinel_sum_over_bands_in_footprint=per_band_sum,
        labels_sha256=sha256(DATA / "labels.tif"),
        existing_faults_sha256=sha256(DATA / "existing_faults.tif"),
        labels_and_existing_faults_byte_identical=sha256(DATA / "labels.tif") == sha256(DATA / "existing_faults.tif"),
        organizer_authenticated=False,
    )
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "random_dot_null"}, indent=2))
    print(json.dumps(result["random_dot_null"], indent=2))


if __name__ == "__main__":
    main()
