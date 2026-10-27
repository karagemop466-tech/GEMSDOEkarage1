"""
Submission format validator.

Implements, literally, the five official requirements from
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format
(fetched live 2026-10-27, no login required):

    1. Same projected CRS as training data: EPSG:32611 (UTM zone 11N).
    2. Same resolution as training data: 100 m.
    3. Same bounds as training data; data outside the bounds is null/NaN.
    4. Single band, dtype float32, values in [0, 1] (confidence of fault
       presence; higher = more confident).
    5. (implicit, from the DrivenData upload form) must open as a valid
       single-band GeoTIFF, or a .zip containing exactly one GeoTIFF.

This module is the single source of truth other scripts call; do not
re-implement these checks elsewhere (PARALLEL-RUN PROTOCOL rule #2:
"fix it once in the template").

Root cause of the reported upload error, "Predicted values must be in range
[0, 1]": the two most common causes, both of which this validator catches
*before* upload:
    (a) leftover nodata sentinel values (e.g. -3.4e38, the GDAL float32
        default nodata) written into pixels instead of a real prediction or
        NaN, which are wildly outside [0, 1]; or
    (b) un-squashed model logits (a raw U-Net head without a final sigmoid)
        written directly to disk, which can be negative or > 1.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import rasterio

from .grid import GEMS_GRID, GemsGrid


@dataclass
class ValidationReport:
    path: str
    sha256: str
    size_bytes: int
    checks: dict
    all_checks_passed: bool
    n_bands: int
    dtype: str
    shape: tuple
    crs: str | None
    transform: tuple
    min_value: float | None
    max_value: float | None
    n_nan: int
    n_inf: int
    n_finite: int

    def to_json(self) -> str:
        d = asdict(self)
        return json.dumps(d, indent=2, default=str)


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def validate_submission(
    path: str | Path,
    expected_grid: GemsGrid = GEMS_GRID,
    *,
    require_all_finite: bool = True,
) -> ValidationReport:
    """
    Validate a candidate submission GeoTIFF against the official format
    rules. Raises no exceptions for failed *content* checks (they are
    recorded in the report); raises only if the file cannot be opened at
    all as a raster.

    If `require_all_finite` is True (default, and the safest option), the
    file must contain ZERO NaN/Inf pixels anywhere -- this sidesteps any
    ambiguity about which interior pixels belong to the organizer's
    "footprint" vs. outside the study-area bounds, and is the pattern this
    repo's own generator uses (see scripts/generate_baseline_submission.py).
    """
    path = Path(path)
    size_bytes = path.stat().st_size
    sha = _sha256(path)

    with rasterio.open(path) as src:
        n_bands = src.count
        dtype = src.dtypes[0]
        shape = (src.height, src.width)
        crs = src.crs.to_string() if src.crs else None
        transform = tuple(src.transform)[:6]
        arr = src.read(1).astype(np.float64)

    n_nan = int(np.isnan(arr).sum())
    n_inf = int(np.isinf(arr).sum())
    n_finite = int(np.isfinite(arr).sum())
    finite_vals = arr[np.isfinite(arr)]
    min_value = float(finite_vals.min()) if finite_vals.size else None
    max_value = float(finite_vals.max()) if finite_vals.size else None

    checks = {
        "opens_as_geotiff": True,
        "single_band": n_bands == 1,
        "dtype_float32": dtype == "float32",
        "shape_matches_reference": shape == expected_grid.shape,
        "crs_matches_reference_epsg32611": crs is not None
        and "32611" in crs,
        "transform_matches_reference": _transform_close(
            transform, tuple(expected_grid.transform)[:6]
        ),
        "no_inf_anywhere": n_inf == 0,
        "no_sentinel_nodata_leak": (min_value is None)
        or (min_value > -1e6),
        "finite_values_in_0_1": (min_value is None)
        or (0.0 - 1e-6 <= min_value and max_value <= 1.0 + 1e-6),
        "all_pixels_finite": (n_nan == 0) if require_all_finite else True,
    }
    checks["all_checks_passed"] = all(checks.values())

    return ValidationReport(
        path=str(path),
        sha256=sha,
        size_bytes=size_bytes,
        checks=checks,
        all_checks_passed=checks["all_checks_passed"],
        n_bands=n_bands,
        dtype=dtype,
        shape=shape,
        crs=crs,
        transform=transform,
        min_value=min_value,
        max_value=max_value,
        n_nan=n_nan,
        n_inf=n_inf,
        n_finite=n_finite,
    )


def _transform_close(a: tuple, b: tuple, tol: float = 1e-3) -> bool:
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Validate a GEMS submission GeoTIFF")
    parser.add_argument("tif_path")
    parser.add_argument(
        "--allow-nan",
        action="store_true",
        help="Allow NaN pixels (e.g. an explicit outside-footprint NaN mask).",
    )
    args = parser.parse_args()

    report = validate_submission(args.tif_path, require_all_finite=not args.allow_nan)
    print(report.to_json())
    if not report.all_checks_passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
