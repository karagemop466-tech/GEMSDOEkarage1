import numpy as np

from gems.uniqueness import check_against_registry_raster

DUPLICATE_SPEARMAN_RHO_SANITY = 0.99


def test_identical_rasters_are_flagged_duplicate():
    rng = np.random.default_rng(1)
    a = rng.random((100, 100)).astype(np.float32)
    result = check_against_registry_raster(a, a.copy())
    assert result.is_duplicate is True
    assert result.spearman_rho > DUPLICATE_SPEARMAN_RHO_SANITY


def test_unrelated_sparse_rasters_are_not_duplicates():
    rng = np.random.default_rng(2)
    a = np.zeros((200, 200), dtype=np.float32)
    b = np.zeros((200, 200), dtype=np.float32)
    a_idx = rng.choice(200 * 200, size=50, replace=False)
    b_idx = rng.choice(200 * 200, size=50, replace=False)
    a.flat[a_idx] = 1.0
    b.flat[b_idx] = 1.0
    result = check_against_registry_raster(a, b)
    assert result.is_duplicate is False


def test_all_zero_candidate_is_never_a_duplicate():
    zeros = np.zeros((50, 50), dtype=np.float32)
    registry = np.zeros((50, 50), dtype=np.float32)
    registry[10:40, 25] = 1.0  # a registry raster with real content
    result = check_against_registry_raster(zeros, registry)
    assert result.is_duplicate is False
    assert result.fraction_within_radius == 0.0


def test_overlap_fraction_matches_manual_count():
    a = np.zeros((20, 20), dtype=np.float32)
    b = np.zeros((20, 20), dtype=np.float32)
    a[5, 5] = 1.0
    a[5, 19] = 1.0  # far from anything in b
    b[5, 6] = 1.0  # 1 px away from a[5,5] -> within 3px
    result = check_against_registry_raster(a, b)
    assert result.fraction_within_radius == 0.5  # 1 of 2 candidate dots is near b
