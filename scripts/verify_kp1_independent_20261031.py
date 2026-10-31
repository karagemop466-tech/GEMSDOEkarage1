#!/usr/bin/env python3
"""Independent, data-free verification of the K-PROXY-DETECT GeoTIFF (31 Oct 2026).

This script does NOT import the candidate builder, the release gate or the vendored
validator. It re-reads the saved bytes with rasterio and recomputes, from scratch:

* file identity (SHA-256, byte count) against the release gate receipt;
* format against the official DrivenData submission-format rules (EPSG:32611,
  100 m, float32, single band, values in [0, 1], nodata null/NaN or finite zeros);
* uniqueness against every nine-focus registry raster (|Spearman| on the full
  footprint, and the fraction of this file's dots within 3 px of that raster's dots);
* the same overlap against every other same-grid local GeoTIFF, so a reader can see
  which files drive the maximum and which overlaps are density artifacts.

It makes no submission decision. It writes ``evidence/kp1_independent_verification_20261031.json``.
Only the repository's own committed rasters are read (no competition data needed).
"""
from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
TIF = ROOT / "docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif"
GATE = ROOT / "evidence/kp1_release_gate.json"
OUT = ROOT / "evidence/kp1_independent_verification_20261031.json"

RHO_LIMIT = 0.90
OVERLAP_LIMIT = 0.70
DOT_RADIUS_PX = 3.0
DENSE_CUTOFF = 1_000_000  # positives; above this a raster covers so much of the grid that dot overlap is meaningless
OFFICIAL_RULES = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read(path: Path):
    with rasterio.open(path) as ds:
        arr = ds.read(1).astype(np.float64)
        meta = dict(
            count=ds.count, dtype=ds.dtypes[0], shape=list(ds.shape),
            crs=ds.crs.to_string() if ds.crs else None,
            transform=[float(v) for v in tuple(ds.transform)[:6]], nodata=ds.nodata,
        )
        masked_pixels = int(np.count_nonzero(ds.read_masks(1) == 0))
    return arr, meta, masked_pixels


def dot_overlap(a_dots: np.ndarray, b_dots: np.ndarray) -> float:
    """Fraction of ``a_dots`` lying within DOT_RADIUS_PX of any ``b_dots``."""
    if b_dots.size == 0:
        return 0.0
    dist, _ = cKDTree(b_dots).query(a_dots, k=1)
    return float((dist <= DOT_RADIUS_PX).mean())


def main() -> dict:
    gate = json.loads(GATE.read_text())
    arr, meta, masked = read(TIF)
    digest = sha256(TIF)

    # ---- identity against the gate receipt
    identity = {
        "file": str(TIF.relative_to(ROOT)),
        "sha256": digest,
        "bytes": TIF.stat().st_size,
        "sha256_matches_gate_receipt": digest == gate["sha256"],
        "bytes_match_gate_receipt": TIF.stat().st_size == gate["bytes"],
    }

    # ---- official format (rules page 967, "Submission format")
    finite = np.isfinite(arr)
    positives = arr > 0
    fmt = {
        "single_band": meta["count"] == 1,
        "dtype_float32": meta["dtype"] == "float32",
        "crs_epsg_32611": meta["crs"] == "EPSG:32611",
        "resolution_100m": abs(meta["transform"][0]) == 100.0 and abs(meta["transform"][4]) == 100.0,
        "unrotated": meta["transform"][1] == 0.0 and meta["transform"][3] == 0.0,
        "all_pixels_finite": bool(finite.all()),
        "values_in_0_1": bool(((arr >= 0) & (arr <= 1)).all()),
        "no_masked_pixels": masked == 0,
        "shape_matches_registry": None,  # filled below
    }
    registry = sorted((ROOT / "registry").glob("GEMSDOE*.tif"))
    reg_data = {p.name: read(p) for p in registry}
    # Scored study-area footprint = finite cells. Derive it from the registry's NaN-outside
    # files and require them to agree; the organizer sample has the same mask (checked by the
    # repo's gate on restored bytes). Zeros-outside files are finite everywhere and carry no mask.
    nan_outside = [n for n, v in reg_data.items() if not np.isfinite(v[0]).all()]
    if not nan_outside:
        raise SystemExit("no NaN-outside registry file; footprint cannot be derived")
    fp = np.isfinite(reg_data[nan_outside[0]][0])
    footprint_consistent = all(np.array_equal(fp, np.isfinite(reg_data[n][0])) for n in nan_outside)
    if not footprint_consistent:
        raise SystemExit("NaN-outside registry masks disagree; refusing to guess the footprint")
    shapes = {tuple(v[1]["shape"]) for v in reg_data.values()}
    transforms = {tuple(v[1]["transform"]) for v in reg_data.values()}
    crs = {v[1]["crs"] for v in reg_data.values()}
    fmt["shape_matches_registry"] = bool(shapes == {tuple(meta["shape"])})
    fmt["transform_matches_registry"] = bool(transforms == {tuple(meta["transform"])})
    fmt["crs_matches_registry"] = bool(crs == {meta["crs"]})
    fmt["all_checks_pass"] = all(v for v in fmt.values() if v is not None)

    # ---- uniqueness
    kdots = np.argwhere(positives & fp)
    flat = arr[fp]

    def compare(name: str, data: np.ndarray, meta_b: dict, masked_b: int) -> dict:
        # Correlate on the other raster's finite footprint only. Filling its NaN with 0 would
        # invent a tie block of "no fault" pixels and change the ranks.
        rho = float(spearmanr(flat, data[fp]).statistic)
        bdots = np.argwhere(fp & np.isfinite(data) & (data > 0))
        return {
            "file": name,
            "abs_spearman": round(abs(rho), 6),
            "kp1_dots_within_3px_of_it": round(dot_overlap(kdots, bdots), 6),
            "its_positives": int(bdots.shape[0]),
            "dense_artifact": bool(bdots.shape[0] > DENSE_CUTOFF),
        }

    focus = [compare(n, v[0], v[1], v[2]) for n, v in reg_data.items()]
    focus_max_rho = max(r["abs_spearman"] for r in focus)
    focus_max_overlap = max(r["kp1_dots_within_3px_of_it"] for r in focus)

    other = []
    for p in sorted(set(glob.glob(str(ROOT / "docs/**/*.tif"), recursive=True)
                        + glob.glob(str(ROOT / "archive/**/*.tif"), recursive=True)
                        + glob.glob(str(ROOT / "docs/candidates/*.tif"), recursive=True))):
        path = Path(p)
        if path.resolve() == TIF.resolve():
            continue
        data, m, mk = read(path)
        if m["shape"] != meta["shape"] or m["crs"] != meta["crs"]:
            continue
        other.append(dict(compare(str(path.relative_to(ROOT)), data, m, mk)))
    sparse = [r for r in other if not r["dense_artifact"]]
    dense = [r for r in other if r["dense_artifact"]]
    other_sparse_max = max((r["kp1_dots_within_3px_of_it"] for r in sparse), default=0.0)
    other_sparse_max_rho = max((r["abs_spearman"] for r in sparse), default=0.0)

    uniqueness = {
        "registry_rule": {
            "rho_limit": RHO_LIMIT, "overlap_limit": OVERLAP_LIMIT,
            "registry_files": len(registry),
            "max_abs_spearman": round(focus_max_rho, 6),
            "max_kp1_dots_within_3px": round(focus_max_overlap, 6),
            "passes_rho": focus_max_rho <= RHO_LIMIT,
            "passes_overlap": focus_max_overlap <= OVERLAP_LIMIT,
        },
        "registry_detail": focus,
        "other_local_same_grid_sparse_files": {
            "count": len(sparse),
            "max_kp1_dots_within_3px": round(other_sparse_max, 6),
            "max_abs_spearman": round(other_sparse_max_rho, 6),
            "passes_overlap": other_sparse_max <= OVERLAP_LIMIT,
        },
        "dense_research_rasters_excluded_from_rule": {
            "count": len(dense),
            "note": ("Each has more than %d positives, so almost any dot falls within 3 px of "
                     "them. Their 100 %% overlap is a density artifact, not duplication. "
                     "They are not registry members and not organizer-scored files." % DENSE_CUTOFF),
            "files": dense,
        },
        "sparse_other_files": sorted(sparse, key=lambda r: -r["kp1_dots_within_3px_of_it"])[:8],
    }

    # ---- content
    content = {
        "positives": int(positives.sum()),
        "unique_values": sorted(float(v) for v in np.unique(arr)),
        "mean": float(arr.mean()),
    }

    footprint_info = {
        "definition": "finite cells of the NaN-outside registry rasters (= organizer sample footprint)",
        "cells": int(fp.sum()),
        "nan_outside_files": nan_outside,
        "masks_identical": footprint_consistent,
        "kp1_positives_inside_footprint": int((positives & fp).sum()),
        "kp1_positives_outside_footprint": int((positives & ~fp).sum()),
        "kp1_values_outside_footprint_all_zero": bool((arr[~fp] == 0).all()),
    }
    report = {
        "schema": "karage1-kp1-independent-verification-v1",
        "footprint": footprint_info,
        "date": "2026-10-31",
        "purpose": "Data-free re-check of the K-PROXY-DETECT GeoTIFF from the saved bytes.",
        "official_rules_source": OFFICIAL_RULES,
        "identity": identity,
        "format": fmt,
        "uniqueness": uniqueness,
        "content": content,
        "verdict_scope": ("format and uniqueness only. Not an organizer receipt, not a score, "
                          "not a leaderboard estimate. Score projection lives in the gate receipt and is "
                          "labelled PROJECTED."),
    }
    report["all_gates_pass"] = bool(
        identity["sha256_matches_gate_receipt"] and fmt["all_checks_pass"]
        and uniqueness["registry_rule"]["passes_rho"] and uniqueness["registry_rule"]["passes_overlap"]
        and uniqueness["other_local_same_grid_sparse_files"]["passes_overlap"]
    )
    OUT.write_text(json.dumps(report, indent=1) + "\n")
    return report


if __name__ == "__main__":
    r = main()
    print(json.dumps({"all_gates_pass": r["all_gates_pass"],
                      "sha256": r["identity"]["sha256"],
                      "format_all_pass": r["format"]["all_checks_pass"],
                      "registry_max_rho": r["uniqueness"]["registry_rule"]["max_abs_spearman"],
                      "registry_max_overlap": r["uniqueness"]["registry_rule"]["max_kp1_dots_within_3px"],
                      "other_sparse_max_overlap": r["uniqueness"]["other_local_same_grid_sparse_files"]["max_kp1_dots_within_3px"],
                      "dense_excluded": r["uniqueness"]["dense_research_rasters_excluded_from_rule"]["count"]},
                     indent=1))
