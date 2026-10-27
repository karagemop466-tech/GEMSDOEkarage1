"""
Canonical output grid for a GEMS Prize submission GeoTIFF.

SOURCE A (OFFICIAL, verified live 2026-10-27 from
https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#provided-features
and #submission-format):
    - CRS: projected UTM zone 11N, EPSG:32611
    - Resolution: 100 m
    - dtype: float32
    - Values: single band, in [0, 1]
    - Same bounds as training_features.tif; data outside those bounds is
      null/NaN.

SOURCE B (CROSS-REPLICATED, UNVERIFIED-BY-US): the exact pixel grid
(height, width, affine transform) below was read back identically from the
`audit.json` / `run_card.json` receipts published by multiple independent
GEMSDOE-prefixed research sites (e.g. GEMSDOE25, GEMSDOE31, GEMSDOE32,
GEMSDOE33, GEMSDOE36), each of which states it derived the numbers from a
locally cached `.cache/gems_data/sample_submission.tif`. Example citation:
    https://buffedlizard55-lab.github.io/GEMSDOE32/docs/downloads/
        gemsdoe32-h44-spcp-sarpu-curvconduit-37654-20261026T053000Z-38f7995a-audit.json
    -> "crs": "EPSG:32611", "transform": [100.0, 0.0, 243350.0, 0.0, -100.0,
       4508550.0], "shape": [3730, 3292], "dtype": "float32"

We did NOT independently open the organizer's original sample_submission.tif
in this environment (no DrivenData login is configured here -- see
docs/LIMITATIONS.md). Treat GRID below as "best available, cross-replicated
across >=5 independent sources, geographically plausible for the GeoDAWN
study area in NW Nevada" -- NOT as an organizer-confirmed fact. Before a real
competition upload, re-derive these numbers yourself from the actual
`sample_submission.tif` you download from the authenticated data tab and
assert they match exactly (see scripts/prepare_data.py::assert_matches_grid).
"""

from __future__ import annotations

from dataclasses import dataclass

from rasterio.crs import CRS
from rasterio.transform import Affine


@dataclass(frozen=True)
class GemsGrid:
    height: int
    width: int
    transform: Affine
    crs: CRS
    dtype: str = "float32"
    pixel_size_m: float = 100.0

    @property
    def shape(self) -> tuple[int, int]:
        return (self.height, self.width)

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        """(left, bottom, right, top) in the grid's CRS units (meters)."""
        left = self.transform.c
        top = self.transform.f
        right = left + self.width * self.transform.a
        bottom = top + self.height * self.transform.e  # e is negative
        return (left, bottom, right, top)

    @property
    def n_pixels(self) -> int:
        return self.height * self.width


# Cross-replicated reference grid (see module docstring for provenance).
# transform = (a, b, c, d, e, f) = (pixel_w, 0, origin_x, 0, -pixel_h, origin_y)
GEMS_GRID = GemsGrid(
    height=3730,
    width=3292,
    transform=Affine(100.0, 0.0, 243350.0, 0.0, -100.0, 4508550.0),
    crs=CRS.from_epsg(32611),
    dtype="float32",
)

# Sanity bound check: UTM 11N covers the NW Great Basin / northern Nevada
# GeoDAWN survey area referenced on the official data page. This is a
# plausibility check, not proof.
_LEFT, _BOTTOM, _RIGHT, _TOP = GEMS_GRID.bounds
assert 150_000 < _LEFT < 700_000, "easting out of UTM11N plausible range"
assert 150_000 < _RIGHT < 700_000, "easting out of UTM11N plausible range"
assert 3_500_000 < _BOTTOM < 4_700_000, "northing out of plausible NV range"
assert 3_500_000 < _TOP < 4_700_000, "northing out of plausible NV range"
assert GEMS_GRID.n_pixels == 3730 * 3292 == 12_279_160
