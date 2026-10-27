"""prepare_data.py — build the cached feature stack from competition data.

Reads the competition rasters placed in data/ (requires DrivenData login to
obtain) and produces a cached feature stack plus a sample_submission grid
reference used by evaluate_holdout.py and submission_writer.py.

Expected inputs in data/:
    training_features.tif, labels.tif, sample_submission.tif, 1m_DEM_links.csv

Outputs in data/prepared/:
    feature_stack.npz  (named feature bands)
    labels.npy         (boolean fault mask)
    grid.json          (CRS/shape/transform from sample_submission.tif)

Runs on CPU. If data are absent, prints the documented placement instructions.
"""

from __future__ import annotations

import json
import os
import sys

import numpy as np

try:
    import rasterio
except Exception:  # pragma: no cover
    rasterio = None

DATA_DIR = "data"
PREPARED_DIR = os.path.join(DATA_DIR, "prepared")


def load_raster_band(path):
    if rasterio is None:
        raise RuntimeError("rasterio is required")
    with rasterio.open(path) as src:
        return src.read(1).astype(np.float32), src.profile


def main() -> int:
    required = ["training_features.tif", "labels.tif", "sample_submission.tif"]
    missing = [f for f in required if not os.path.exists(os.path.join(DATA_DIR, f))]
    if missing:
        print("Competition data not found in data/:", missing)
        print("Run on an authenticated machine:")
        print("  bash scripts/download_competition_data.sh   (place files into data/)")
        print("  python scripts/prepare_data.py              (then build the stack)")
        return 2

    os.makedirs(PREPARED_DIR, exist_ok=True)

    features, feat_profile = load_raster_band(os.path.join(DATA_DIR, "training_features.tif"))
    labels, label_profile = load_raster_band(os.path.join(DATA_DIR, "labels.tif"))
    _, sub_profile = load_raster_band(os.path.join(DATA_DIR, "sample_submission.tif"))

    # Save feature stack + labels.
    np.savez_compressed(os.path.join(PREPARED_DIR, "feature_stack.npz"),
                        features=features)
    np.save(os.path.join(PREPARED_DIR, "labels.npy"), (labels > 0).astype(np.uint8))

    # Grid reference (CRS/shape/transform) for submission writing.
    import rasterio as _rio
    grid = {
        "crs": str(sub_profile.get("crs")),
        "height": int(sub_profile["height"]),
        "width": int(sub_profile["width"]),
        "transform": [sub_profile["transform"].a, sub_profile["transform"].b,
                      sub_profile["transform"].c, sub_profile["transform"].d,
                      sub_profile["transform"].e, sub_profile["transform"].f],
        "dtype": str(sub_profile["dtype"]),
        "count": int(sub_profile["count"]),
    }
    with open(os.path.join(PREPARED_DIR, "grid.json"), "w") as f:
        json.dump(grid, f, indent=2)

    print(f"Prepared feature stack: {features.shape} labels: {labels.shape}")
    print(f"Grid: {grid['height']}x{grid['width']} crs={grid['crs']}")
    print(f"Outputs in {PREPARED_DIR}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
