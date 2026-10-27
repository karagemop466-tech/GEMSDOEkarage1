import numpy as np
import pytest
from pathlib import Path
from gemsk import grid

pytestmark = pytest.mark.skipif(not (grid.DATA / "sample_submission.tif").exists(), reason="competition data not restored")


def test_zeros_mode_is_whole_array_finite_and_matches_template(tmp_path):
    from gemsk import submission
    foot = grid.footprint()
    dots = np.zeros(foot.shape, bool)
    yy, xx = np.nonzero(foot)
    dots[yy[::50000], xx[::50000]] = True
    p = submission.write(dots, tmp_path / "t-zeros.tif", "zeros")
    v = submission.validate(p)
    assert v["all_checks_passed"] and v["whole_array_finite"] and v["emitted_positive_pixels"] == int(dots.sum())
    assert v["unique_values_in_footprint"] == [0.0, 1.0]


def test_shipped_file_in_docs_downloads_validates():
    from gemsk import submission
    files = sorted((grid.ROOT / "docs" / "downloads").glob("gemsk1-*-zeros.tif"))
    assert files, "no shipped zeros file"
    v = submission.validate(files[-1])
    assert v["all_checks_passed"] and v["on_catalogue_dots"] == 0 and v["dots_within_2px_of_catalogue"] == 0
