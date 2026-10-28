#!/usr/bin/env python3
"""Audit already-published candidate bytes against pinned reference rasters.

This is a *disqualifying* audit, not a way to certify uniqueness. The small,
explicitly pinned reference set is not the complete registry and pre-placement
surfaces are not available. A registered lattice is never exempted from the
literal directional-overlap rule. No geological model is run or TIFF written.

    python scripts/audit_references.py --fetch --out .cache/reference-audit.json
    python scripts/audit_existing_candidates.py
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

try:
    from scripts import audit_references as refs
    from scripts.validate_geotiff import diagnose
except ModuleNotFoundError:  # direct execution from scripts/
    import audit_references as refs
    from validate_geotiff import diagnose

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = (
    "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif",
    "gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif",
)


def is_overlap_duplicate(hits: int, dots: int) -> bool:
    """Strictly greater than 70%, evaluated in integer arithmetic."""
    if (type(hits) is not int or type(dots) is not int or dots <= 0
            or hits < 0 or hits > dots):
        raise ValueError("invalid candidate dot/overlap counts")
    return hits * 10 > dots * 7


def audit(cache: Path, candidate_paths: list[Path], entries: list[dict]) -> dict:
    # Verify *every* required reference before doing any comparisons. A missing
    # or modified witness is an error, never evidence that a candidate passes.
    for entry in entries:
        refs.verify_file(cache / (entry["id"] + ".tif"), entry)
    by_id = {entry["id"]: entry for entry in entries}
    if set(by_id) != refs.REQUIRED or len(entries) != len(refs.REQUIRED):
        raise ValueError("reference inventory is incomplete or duplicated")
    template = cache / "template.tif"
    with rasterio.open(template) as ds:
        sample = ds.read(1, masked=True)
        footprint = ~np.ma.getmaskarray(sample) & np.isfinite(sample.data)
    if not footprint.any():
        raise ValueError("empty reference footprint")
    _, template_meta = refs.read_grid(template)

    candidates = []
    supports = []
    for path in candidate_paths:
        fmt = diagnose(path, template, by_id["template"]["sha256"])
        if fmt["checks"]["masked_inside_count"] != 0:
            raise ValueError(f"candidate has masked pixels inside footprint: {path}")
        data, meta = refs.read_grid(path)
        if not refs.same_grid(meta, template_meta):
            raise ValueError(f"candidate grid mismatch: {path}")
        dots = refs.binary_support(data, footprint, path.name)
        n = int(dots.sum())
        if n == 0:
            raise ValueError(f"candidate has no positive dots: {path}")
        candidates.append({
            "file": path.name,
            "sha256": refs.sha256(path),
            "positive_pixels_in_footprint": n,
            "format_diagnostics": fmt["diagnostics"],
            "format_checks": {
                key: fmt["checks"][key] for key in (
                    "single_band", "float32", "crs_shape_transform_match_mirror",
                    "no_nonfinite_inside", "nonfinite_inside_count",
                    "inside_values_in_0_1", "out_of_range_inside_count",
                    "masked_inside_count", "outside_all_null_or_nan",
                    "whole_array_strict_finite_0_1", "minimum_finite", "maximum_finite",
                )
            },
            "preplacement_surface": "unavailable in checkout; not checked",
            "comparisons": [],
        })
        supports.append(dots)

    for ref_id in ("lattice", *refs.SITES):
        data, meta = refs.read_grid(cache / (ref_id + ".tif"))
        if not refs.same_grid(meta, template_meta):
            raise ValueError(f"reference grid mismatch: {ref_id}")
        target = refs.binary_support(data, footprint, ref_id)
        if not target.any():
            raise ValueError(f"empty reference support: {ref_id}")
        near = binary_dilation(target, structure=refs.disk(3))
        for result, ours in zip(candidates, supports):
            n = result["positive_pixels_in_footprint"]
            hits = int(np.count_nonzero(ours & near))
            rho = refs.binary_rank_correlation(ours, target, footprint)
            if rho is None:
                raise ValueError(f"undefined binary rank correlation: {ref_id}")
            result["comparisons"].append({
                "reference": ref_id,
                "reference_sha256": by_id[ref_id]["sha256"],
                "candidate_dots_within_3px": hits,
                "candidate_dots": n,
                "directed_overlap": hits / n,
                "binary_dot_spearman": rho,
                "overlap_exceeds_70_percent": is_overlap_duplicate(hits, n),
                "rank_abs_exceeds_0_90": abs(rho) > 0.90,
                "exact_dot_mask_match": bool(np.array_equal(ours, target)),
            })

    for result in candidates:
        result["duplicate_references"] = [
            row["reference"] for row in result["comparisons"]
            if row["overlap_exceeds_70_percent"] or row["rank_abs_exceeds_0_90"]
        ]
        # Even without a duplicate, this partial comparison cannot clear a file.
        result["verdict"] = "duplicate" if result["duplicate_references"] else "incomplete"
        result["ok_to_submit"] = False

    return {
        "schema": "karage1-existing-candidate-audit-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "method": "Exact saved binary supports; closed Euclidean 3-pixel disk; Spearman on all mirror-footprint pixels.",
        "reference_scope": "Nine pinned historical site files plus the pinned 13GEMSDOE lattice. This is not a complete registry.",
        "template_authenticity": "Owner mirror with verified SHA-256; not independently authenticated against DrivenData.",
        "footprint_pixels": int(footprint.sum()),
        "lattice_sha256": by_id["lattice"]["sha256"],
        "thresholds": {"directed_overlap_strictly_greater_than": 0.70, "absolute_spearman_strictly_greater_than": 0.90},
        "preplacement_surfaces_checked": False,
        "registry_complete": False,
        "candidates": candidates,
        "upload_authorized": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache/references")
    ap.add_argument("--manifest", type=Path, default=ROOT / "registry/reference_assets.json")
    ap.add_argument("--out", type=Path, default=ROOT / "evidence/candidate_audit_20261028.json")
    args = ap.parse_args()
    try:
        entries = refs.load_manifest(args.manifest)
        paths = [ROOT / "docs/downloads" / name for name in CANDIDATES]
        report = audit(args.cache, paths, entries)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.out.with_suffix(args.out.suffix + ".tmp")
        tmp.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        tmp.replace(args.out)
    except (OSError, ValueError) as exc:
        print(f"AUDIT BLOCKED: {exc}", file=sys.stderr)
        return 2
    print(f"Audit written to {args.out}; no upload is authorized.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
