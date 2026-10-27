#!/usr/bin/env python
"""
Lane-discipline / duplicate check (parallel-run protocol rule 1): compare a
candidate submission GeoTIFF against one or more "registry" GeoTIFFs (other
known candidates, sibling-site downloads kept for research only, etc.).

Usage:
    python scripts/check_uniqueness.py candidate.tif registry1.tif [registry2.tif ...]

Flags a duplicate if, against ANY registry raster:
  - |Spearman rank correlation| > 0.90 on the full surface, or
  - more than 70% of the candidate's positive pixels fall within 3 px of
    that registry raster's positive pixels.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import rasterio

from gems.uniqueness import check_against_registry_raster


def _read(path: str):
    with rasterio.open(path) as src:
        return src.read(1)


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        raise SystemExit(2)
    candidate_path, registry_paths = sys.argv[1], sys.argv[2:]
    candidate = _read(candidate_path)

    worst = None
    for reg_path in registry_paths:
        registry = _read(reg_path)
        if registry.shape != candidate.shape:
            print(f"SKIP {reg_path}: shape mismatch {registry.shape} vs {candidate.shape}")
            continue
        result = check_against_registry_raster(candidate, registry)
        flag = "DUPLICATE -- STOP" if result.is_duplicate else "ok"
        print(
            f"{reg_path}: spearman={result.spearman_rho:.4f} "
            f"within_3px_fraction={result.fraction_within_radius:.4f} -> {flag}"
        )
        if worst is None or result.is_duplicate:
            worst = result

    if worst is not None and worst.is_duplicate:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
