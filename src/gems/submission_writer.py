"""
Writer for a compliant GEMS Prize submission GeoTIFF.

Always writes a *fully finite* single-band float32 raster with every pixel
clipped to [0, 1] -- no NaN, no Inf, no nodata sentinel. This sidesteps the
reported upload error ("Predicted values must be in range [0, 1]") entirely:
there is no pixel, anywhere in the file, that can be out of range.

This matches rule 3 of the official format spec ("data outside the bounds is
null or nan") only in the degenerate, always-safe sense that there is no
"outside the bounds" region in a raster whose shape exactly equals the
official bounds -- we do not claim to know the organizer's exact irregular
survey-footprint nodata mask (see docs/LIMITATIONS.md), so we never guess at
it. If you later obtain the real `sample_submission.tif` and want your
nodata mask to match it pixel-for-pixel, pass `footprint_mask` explicitly.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import rasterio

from .grid import GEMS_GRID, GemsGrid


@dataclass
class SubmissionMeta:
    unique_name: str
    note: str  # <=140 chars, shown on the DrivenData submission form

    def __post_init__(self) -> None:
        if len(self.note) > 140:
            raise ValueError(
                f"note is {len(self.note)} chars, DrivenData form limit is 140"
            )


def write_submission(
    out_path: str | Path,
    probability: np.ndarray,
    grid: GemsGrid = GEMS_GRID,
    footprint_mask: np.ndarray | None = None,
) -> Path:
    """
    Write `probability` (H, W) as a compliant single-band float32 GeoTIFF.

    - Values are clipped to [0, 1].
    - NaN/Inf are replaced with 0.0 (never left in the file).
    - If `footprint_mask` is given (True = inside the real survey
      footprint), pixels outside it are set to 0.0 as well (NOT NaN) unless
      you explicitly want NaN-outside behavior -- see `write_submission_nan`.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    arr = np.asarray(probability, dtype=np.float32)
    if arr.shape != grid.shape:
        raise ValueError(f"shape {arr.shape} != reference grid shape {grid.shape}")

    arr = np.nan_to_num(arr, nan=0.0, posinf=1.0, neginf=0.0)
    arr = np.clip(arr, 0.0, 1.0).astype(np.float32)

    if footprint_mask is not None:
        arr = np.where(footprint_mask, arr, np.float32(0.0)).astype(np.float32)

    profile = {
        "driver": "GTiff",
        "height": grid.height,
        "width": grid.width,
        "count": 1,
        "dtype": "float32",
        "crs": grid.crs,
        "transform": grid.transform,
        "nodata": None,
        "compress": "deflate",
        "predictor": 3,
    }
    with rasterio.open(out_path, "w", **profile) as dst:
        dst.write(arr, 1)

    assert np.isfinite(arr).all(), "internal error: wrote non-finite pixel"
    assert arr.min() >= 0.0 and arr.max() <= 1.0, "internal error: out of [0,1]"
    return out_path


def write_run_card(
    out_path: str | Path,
    *,
    meta: SubmissionMeta,
    hypothesis: str,
    mechanism: str,
    named_non_fault_mimic: str,
    holdout_dti: dict | None,
    correlation_vs_registry: dict | None,
    raster_sha256: str,
    validator_output: dict,
    verdict: str,
) -> Path:
    """Write the RUN CARD JSON mandated by the parallel-run protocol rule 5."""
    if verdict not in ("promote", "negative"):
        raise ValueError("verdict must be 'promote' or 'negative'")
    card = {
        "unique_name": meta.unique_name,
        "note": meta.note,
        "hypothesis": hypothesis,
        "mechanism": mechanism,
        "named_non_fault_process": named_non_fault_mimic,
        "holdout_dti": holdout_dti,
        "correlation_overlap_vs_registry": correlation_vs_registry,
        "raster_sha256": raster_sha256,
        "validator_output": validator_output,
        "verdict": verdict,
    }
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(card, indent=2))
    return out_path
