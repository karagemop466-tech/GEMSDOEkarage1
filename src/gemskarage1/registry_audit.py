"""Use the pinned shared literal uniqueness gate; no private raster exemptions.

A positive clearance needs a complete, hash-pinned indexed public inventory, an
actual grid template, and both pre-placement surface and saved-dot checks. A
single duplicate witness is sufficient to stop. Public inventory completeness
is not the same as proof about private or inaccessible submissions.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import rasterio
from gems57.gates import lane_uniqueness_report


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def run_phase(candidate, footprint, *, sample: Path, registry_index: Path | dict, phase: str) -> dict:
    """Run the same literal shared gate on a surface or on final saved dots."""
    if sample is None or registry_index is None:
        raise ValueError("both a sample grid and a complete pinned registry index are required")
    report = lane_uniqueness_report(candidate, footprint, sample=sample, phase=phase,
                                    registry_index=registry_index)
    # An undefined rank correlation cannot establish the required rank check.
    undefined = [r.get("submission", "unknown") for r in report["rows"]
                 if "error" not in r and r.get("spearman_full_footprint") is None]
    if undefined:
        report["ok"] = False
        report["unique"] = False
        report["stop_required"] = True
        report["undefined_rank_references"] = undefined
    return report


def run_surface_gate(continuous_surface, footprint, *, sample: Path, registry_index: Path | dict) -> dict:
    """Run before any production dot-placement and stop on an incomplete scan."""
    return run_phase(continuous_surface, footprint, sample=sample, registry_index=registry_index, phase="surface")


def run_full_fleet_uniqueness_gate(
    continuous_surface, final_dots_f32, final_tif_path: Path, foot, *,
    sample: Path | None = None, registry_index: Path | dict | None = None,
) -> dict:
    """Audit both phases for an already-existing file; never certify from a partial scan.

    New pipelines must additionally call ``run_surface_gate`` before placement.
    The on-disk candidate must be exactly the array tested in the final phase.
    """
    if sample is None or registry_index is None:
        raise ValueError("complete pinned registry index and sample are mandatory; legacy fleet globs are not clearance")
    surface = run_surface_gate(continuous_surface, foot, sample=sample, registry_index=registry_index)
    with rasterio.open(final_tif_path) as ds, rasterio.open(sample) as ref:
        if ds.count != 1 or ds.dtypes[0] != "float32" or (ds.shape, ds.crs, ds.transform) != (ref.shape, ref.crs, ref.transform):
            raise ValueError("saved raster grid differs from the reference")
        saved = ds.read(1)
    if not np.array_equal(saved, np.asarray(final_dots_f32), equal_nan=True):
        raise ValueError("tested dots do not match the exact saved raster")
    dots = run_phase(saved, foot, sample=sample, registry_index=registry_index, phase="dots")
    return {"schema": "shared-literal-two-phase-v1", "candidate_sha256": _sha(Path(final_tif_path)),
            "surface": surface, "dots": dots,
            "comparisons_passed": bool(surface["ok"] and dots["ok"]),
            # A retrospective function cannot prove the surface was checked
            # before any placement took place. The future orchestrator must
            # enforce and record that ordering; this is not a release receipt.
            "surface_checked_before_placement": False, "passed": False,
            "complete_indexed_public_scope_only": True,
            "note": "Retrospective comparison cannot prove placement order; public indexes cannot certify private or inaccessible rasters."}
