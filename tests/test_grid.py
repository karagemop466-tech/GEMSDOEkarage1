from gems.grid import GEMS_GRID


def test_grid_pixel_count():
    assert GEMS_GRID.n_pixels == 3730 * 3292 == 12_279_160


def test_grid_resolution_is_100m():
    assert GEMS_GRID.transform.a == 100.0
    assert GEMS_GRID.transform.e == -100.0


def test_grid_crs_is_utm11n():
    assert GEMS_GRID.crs.to_epsg() == 32611


def test_grid_bounds_are_geographically_plausible_for_nw_nevada():
    left, bottom, right, top = GEMS_GRID.bounds
    # UTM 11N easting for northern Nevada is roughly 230,000-650,000 m.
    assert 150_000 < left < right < 700_000
    # Northing for ~39-41 deg N is roughly 4,300,000-4,550,000 m.
    assert 3_900_000 < bottom < top < 4_700_000
