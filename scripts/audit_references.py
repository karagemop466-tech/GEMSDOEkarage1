#!/usr/bin/env python3
"""Reproduce the pinned historical-raster audit; never authorizes a submission.

This is a geometry/format audit, not a model, holdout evaluator, or submission
writer. Input rasters are owner mirrors; checksums prove byte identity, not
that the mirrors are authenticated competition data. The binary-dot analysis
is valid only for exact 0/1 predictions on the audited footprint.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from fractions import Fraction

import numpy as np
import rasterio
import scipy
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
SITES = tuple(f"GEMSDOE{n}" for n in (24, 25, 27, 28, 30, 31, 32, 33, 36))
REQUIRED = {"template", "labels", "lattice", *SITES}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def disk(radius: int) -> np.ndarray:
    """Closed Euclidean disk in pixels, including distance exactly radius."""
    if radius < 0:
        raise ValueError("radius must be non-negative")
    yy, xx = np.ogrid[-radius : radius + 1, -radius : radius + 1]
    return yy * yy + xx * xx <= radius * radius


def minimum_overlap(dots: int, uncovered: int, limit: Fraction = Fraction(7, 10)) -> dict:
    """Pigeonhole lower bound for N distinct dots inside the SAME footprint.

    No optimization around uncovered holes is encouraged or implied. This
    bound says nothing about a different grid or a non-distinct/weighted budget.
    """
    if (not isinstance(dots, int) or isinstance(dots, bool) or
            not isinstance(uncovered, int) or isinstance(uncovered, bool) or dots <= 0 or uncovered < 0):
        raise ValueError("dots must be positive; uncovered must be nonnegative integers")
    if not isinstance(limit, Fraction) or not 0 <= limit <= 1:
        raise ValueError("limit must be a fraction between zero and one")
    num = max(0, dots - uncovered)
    exact = Fraction(num, dots)
    return {
        "dots": dots,
        "uncovered_pixels": uncovered,
        "minimum_overlapping_dots": num,
        "minimum_fraction": float(exact),
        "limit": float(limit),
        "necessarily_exceeds_limit": exact > limit,
        "maximum_dots_not_ruled_out": (uncovered * limit.denominator // (limit.denominator - limit.numerator)) if limit < 1 else None,
    }


def binary_rank_correlation(a: np.ndarray, b: np.ndarray, footprint: np.ndarray) -> float | None:
    """Spearman rho for binary arrays = Pearson correlation of their indicators.

    Two-level average ranks are affine transforms of the indicators. A constant
    input has undefined correlation, reported as null rather than passing it.
    """
    if a.shape != b.shape or a.shape != footprint.shape:
        raise ValueError("shape mismatch")
    n = int(footprint.sum())
    if n == 0:
        return None
    na = int(np.count_nonzero(a & footprint))
    nb = int(np.count_nonzero(b & footprint))
    if na == 0 or nb == 0 or na == n or nb == n:
        return None
    nab = int(np.count_nonzero(a & b & footprint))
    # Exact integer arithmetic first avoids catastrophic cancellation.
    num = n * nab - na * nb
    denom = float((na * (n - na) * nb * (n - nb)) ** 0.5)
    return num / denom


def load_manifest(path: Path) -> list[dict]:
    entries = json.loads(path.read_text())
    if (not isinstance(entries, list) or len(entries) != len(REQUIRED) or
            any(not isinstance(x, dict) or not isinstance(x.get("id"), str) for x in entries) or
            {x["id"] for x in entries} != REQUIRED):
        raise ValueError("manifest must contain each required reference exactly once")
    for x in entries:
        if any(not isinstance(x.get(k), str) for k in ("id", "repo", "ref", "sha256", "path")):
            raise ValueError("manifest entry is missing required string fields")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", x["id"]):
            raise ValueError("unsafe id")
        if not re.fullmatch(r"buffedlizard55-lab/GEMSDOE(?:24|25|27|28|30|31|32|33|36)", x["repo"]):
            raise ValueError("unexpected source repository")
        if not re.fullmatch(r"[0-9a-f]{40}", x["ref"]) or not re.fullmatch(r"[0-9a-f]{64}", x["sha256"]):
            raise ValueError("source must have immutable commit and SHA-256 pins")
        if x["path"].startswith("/") or any(p in ("", ".", "..") for p in x["path"].split("/")):
            raise ValueError("unsafe source path")
        if not isinstance(x.get("bytes"), int) or isinstance(x["bytes"], bool) or x["bytes"] <= 0:
            raise ValueError("invalid source size")
    return entries


def verify_file(path: Path, entry: dict) -> None:
    if not path.is_file():
        raise FileNotFoundError(f"missing {entry['id']}: {path}; rerun with --fetch")
    if path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
        raise ValueError(f"checksum or size mismatch: {path}")


def fetch_files(entries: list[dict], cache: Path) -> None:
    """Fetch only GitHub content API pinned files, atomically, and verify hashes."""
    cache.mkdir(parents=True, exist_ok=True)
    for item in entries:
        dest = cache / (item["id"] + ".tif")
        if dest.exists():
            verify_file(dest, item)
            print(f"verified {item['id']}", file=sys.stderr)
            continue
        endpoint = f"repos/{item['repo']}/contents/{item['path']}?ref={item['ref']}"
        fd, tmpname = tempfile.mkstemp(prefix=".fetch-", dir=cache)
        tmp = Path(tmpname)
        try:
            with os.fdopen(fd, "wb") as stream:
                subprocess.run(["gh", "api", "-H", "Accept: application/vnd.github.raw", endpoint], stdout=stream, check=True)
            verify_file(tmp, item)
            tmp.replace(dest)
        finally:
            tmp.unlink(missing_ok=True)
        print(f"fetched + verified {item['id']}", file=sys.stderr)


def read_grid(path: Path) -> tuple[np.ndarray, dict]:
    with rasterio.open(path) as ds:
        if ds.count != 1:
            raise ValueError(f"expected one band: {path}")
        return ds.read(1), {
            "driver": ds.driver,
            "shape": list(ds.shape),
            "crs": ds.crs.to_string() if ds.crs else None,
            "transform": list(ds.transform)[:6],
            "dtype": ds.dtypes[0],
            "nodata_is_nan": bool(ds.nodata is not None and np.isnan(ds.nodata)),
        }


def same_grid(meta: dict, template: dict) -> bool:
    return all(meta[k] == template[k] for k in ("shape", "crs", "transform"))


def raster_checks(data: np.ndarray, meta: dict, template: dict, footprint: np.ndarray) -> dict:
    """Diagnose exact saved bytes. Format alone is not upload authorization."""
    if data.shape != footprint.shape:
        raise ValueError("footprint shape mismatch")
    inside = data[footprint]
    outside = data[~footprint]
    fin_inside = np.isfinite(inside)
    finite_all = np.isfinite(data)
    valid_inside = fin_inside & (inside >= 0) & (inside <= 1)
    nonfinite_inside = int((~fin_inside).sum())
    out_of_range_inside = int((fin_inside & ((inside < 0) | (inside > 1))).sum())
    # Do not conflate NaN-outside wording with the observed portal error.
    # Full-array strict range explicitly fails if ANY NaN/Inf is present.
    result = {
        "single_band": True,
        "driver_is_geotiff": meta["driver"] == "GTiff",
        "float32": meta["dtype"] == "float32",
        "crs_shape_transform_match_mirror": same_grid(meta, template),
        "no_nonfinite_inside": nonfinite_inside == 0,
        "nonfinite_inside_count": nonfinite_inside,
        "inside_values_in_0_1": bool(valid_inside.all()),
        "out_of_range_inside_count": out_of_range_inside,
        "outside_all_nan": bool(np.isnan(outside).all()) if outside.size else True,
        "outside_nan_count": int(np.isnan(outside).sum()),
        "whole_array_strict_finite_0_1": bool(np.all(finite_all & (data >= 0) & (data <= 1))),
        "minimum_finite": float(np.min(data[finite_all])) if finite_all.any() else None,
        "maximum_finite": float(np.max(data[finite_all])) if finite_all.any() else None,
        "nodata_tag_is_nan": meta["nodata_is_nan"],
        "portal_acceptance": "not tested",
    }
    result["mirror_grid_and_inside_values_pass"] = all(result[k] for k in (
        "single_band", "driver_is_geotiff", "float32", "crs_shape_transform_match_mirror",
        "no_nonfinite_inside", "inside_values_in_0_1"))
    return result


def binary_support(data: np.ndarray, footprint: np.ndarray, label: str) -> np.ndarray:
    v = data[footprint]
    if not np.isfinite(v).all() or not np.isin(v, (0, 1)).all():
        raise ValueError(f"{label} is not a finite binary raster in the footprint")
    return footprint & (data == 1)


def audit(entries: list[dict], cache: Path) -> dict:
    for x in entries:
        verify_file(cache / (x["id"] + ".tif"), x)
    index = {x["id"]: x for x in entries}
    template_arr, template_meta = read_grid(cache / "template.tif")
    if template_meta["driver"] != "GTiff" or template_meta["dtype"] != "float32" or template_meta["crs"] != "EPSG:32611":
        raise ValueError("unexpected mirror template format")
    if template_meta["transform"][:2] != [100.0, 0.0] or template_meta["transform"][3:5] != [0.0, -100.0]:
        raise ValueError("unexpected mirror resolution/rotation")
    fp = np.isfinite(template_arr)
    if not fp.any() or fp.all():
        raise ValueError("mirror footprint is empty or has no outside")
    labels, labels_meta = read_grid(cache / "labels.tif")
    if not same_grid(labels_meta, template_meta):
        raise ValueError("label grid mismatch")
    label_support = fp & (labels == 1)
    sample_positive = fp & (template_arr == 1)
    if not np.isin(template_arr[fp], (0, 1)).all():
        raise ValueError("mirror sample has unexpected values")
    lattice_arr, lattice_meta = read_grid(cache / "lattice.tif")
    if not same_grid(lattice_meta, template_meta):
        raise ValueError("lattice grid mismatch")
    lattice = binary_support(lattice_arr, fp, "lattice")
    covered = binary_dilation(lattice, structure=disk(3))
    uncovered = int(np.count_nonzero(fp & ~covered))
    bound = minimum_overlap(37654, uncovered)

    arrays = {}
    rows = {}
    for name in SITES:
        data, meta = read_grid(cache / (name + ".tif"))
        if not same_grid(meta, template_meta):
            raise ValueError(f"{name}: grid mismatch; no resampling is allowed")
        dots = binary_support(data, fp, name)
        count = int(dots.sum())
        if count == 0:
            raise ValueError(f"{name}: zero dots; directed overlap undefined")
        arrays[name] = dots
        checks = raster_checks(data, meta, template_meta, fp)
        rows[name] = {
            "sha256": index[name]["sha256"],
            "positive_pixels": count,
            "lattice_nearby_count": int(np.count_nonzero(dots & covered)),
            "lattice_directed_overlap": float(np.count_nonzero(dots & covered) / count),
            "literal_lattice_duplicate": (int(np.count_nonzero(dots & covered)) * 10 > count * 7),
            "format_diagnostics": checks,
        }
    pairs = {}
    # Iterate target-by-target so only one full-grid dilation is resident at once.
    for reference in SITES:
        near = binary_dilation(arrays[reference], structure=disk(3))
        for candidate in SITES:
            if candidate == reference:
                continue
            a, b = arrays[candidate], arrays[reference]
            count = rows[candidate]["positive_pixels"]
            hits = int(np.count_nonzero(a & near))
            pairs[f"{candidate}->{reference}"] = {
                "candidate_dots_within_3px": hits,
                "candidate_dots": count,
                "overlap_fraction": hits / count,
                "overlap_exceeds_70_percent": hits * 10 > count * 7,
                "binary_dot_spearman_rho": binary_rank_correlation(a, b, fp),
                "exact_dot_mask_match": bool(np.array_equal(a, b)),
            }
    # H33 B2 forensic check: D2.8 minus label pixels at Euclidean distance <=2 px.
    parent = arrays["GEMSDOE25"]
    h33 = arrays["GEMSDOE32"]
    near_labels = binary_dilation(label_support, structure=disk(2))
    expected = parent & ~near_labels
    result = {
        "schema": "karage1-reference-audit-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "Nine historical pinned rasters, mirror template and one lattice witness. No pre-placement surfaces, complete registry, holdout or portal receipt were checked.",
        "source_authentication": "Owner mirrors pinned by SHA-256; not independently authenticated against DrivenData data files.",
        "software": {"python": sys.version.split()[0], "numpy": np.__version__, "scipy": scipy.__version__, "rasterio": rasterio.__version__},
        "grid": template_meta,
        "footprint_pixels": int(fp.sum()),
        "outside_pixels": int((~fp).sum()),
        "mirror_sample_positive_pixels": int(sample_positive.sum()),
        "label_positive_pixels": int(label_support.sum()),
        "sample_positive_mask_equals_label": bool(np.array_equal(sample_positive, label_support)),
        "lattice": {
            "sha256": index["lattice"]["sha256"],
            "support_pixels": int(lattice.sum()),
            "covered_footprint_pixels": int(np.count_nonzero(fp & covered)),
            "uncovered_footprint_pixels": uncovered,
            "coverage_fraction": float(np.count_nonzero(fp & covered) / fp.sum()),
            "champion_sized_budget_bound": bound,
        },
        "rows": rows,
        "directed_pairs": pairs,
        "all_72_directed_pairs_exceed_70_percent": all(x["overlap_exceeds_70_percent"] for x in pairs.values()),
        "forensics": {
            "GEMSDOE25_vs_GEMSDOE30_exact_dot_masks": bool(np.array_equal(arrays["GEMSDOE25"], arrays["GEMSDOE30"])),
            "GEMSDOE32_equals_GEMSDOE25_minus_visible_catalogue_2px": bool(np.array_equal(expected, h33)),
            "parent_dots": int(parent.sum()),
            "removed_within_2px": int(np.count_nonzero(parent & near_labels)),
            "child_dots": int(h33.sum()),
            "unexpected_child_additions": int(np.count_nonzero(h33 & ~parent)),
            "unexpected_child_deletions": int(np.count_nonzero(expected & ~h33)),
            "interpretation": "Geometry only, not a causal explanation or an organizer-confirmed score.",
        },
        "submit_authorized": False,
    }
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, default=ROOT / "registry/reference_assets.json")
    p.add_argument("--cache", type=Path, default=ROOT / ".cache/references")
    p.add_argument("--fetch", action="store_true", help="Fetch missing pinned reference files via GitHub CLI")
    p.add_argument("--out", type=Path, default=ROOT / "docs/data/reference-audit.json")
    args = p.parse_args()
    try:
        entries = load_manifest(args.manifest)
        if args.fetch:
            fetch_files(entries, args.cache)
        report = audit(entries, args.cache)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.out.with_suffix(args.out.suffix + ".tmp")
        tmp.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        tmp.replace(args.out)
        print(f"Audit written to {args.out}. No submission is authorized.")
        return 0
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"AUDIT BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
