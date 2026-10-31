#!/usr/bin/env python3
"""Re-derive the format and footprint receipt for the nine focus-site rasters.

Read-only. Uses the repository's shared validator (`scripts/validate_geotiff.py`,
`diagnose`) against the mirrored sample grid, then checks three facts that the
review depends on:

1. footprint: every focus raster has the same NaN-or-finite footprint as the
   sample (no NaN inside the footprint; outside cells are NaN or 0);
2. subset: GEMSDOE32 positives are a strict subset of GEMSDOE25 positives;
3. sample-vs-label: the mirrored sample's positives equal the label raster's
   positives (the official sample is described as "total fault absence").

This script never authorises a submission. The sample and labels come from
third-party mirrors (`scripts/restore_karage1_data.py`), so the receipt proves
mirror consistency only.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from validate_geotiff import diagnose  # noqa: E402

REGISTRY = ROOT / "registry"
SAMPLE = ROOT / "data" / "sample_submission.tif"
LABELS = ROOT / "data" / "labels.tif"
SUBSET_PAIR = ("GEMSDOE32", "GEMSDOE25")
KEY_CHECKS = (
    "single_band",
    "float32",
    "crs_shape_transform_match_mirror",
    "no_nonfinite_inside",
    "inside_values_in_0_1",
    "outside_all_nan",
    "outside_nan_count",
    "whole_array_strict_finite_0_1",
    "nodata_tag_is_nan",
)


def focus_rasters(registry: Path = REGISTRY) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for path in sorted(registry.glob("GEMSDOE*.tif")):
        site = path.name.split("_", 1)[0]
        if site in out:
            raise ValueError(f"two registry rasters claim site {site}")
        out[site] = path
    return out


def build_receipt(sample: Path = SAMPLE, labels: Path = LABELS, registry: Path = REGISTRY) -> dict:
    if not sample.exists():
        raise FileNotFoundError(f"{sample} missing; run scripts/restore_karage1_data.py --group core")
    rasters = focus_rasters(registry)
    with rasterio.open(sample) as src:
        sample_grid = src.read(1)
    footprint = np.isfinite(sample_grid)

    sites = []
    arrays: dict[str, np.ndarray] = {}
    for site, path in rasters.items():
        diag = diagnose(path, sample)
        with rasterio.open(path) as src:
            arr = src.read(1)
        arrays[site] = arr
        outside = arr[~footprint]
        inside = arr[footprint]
        sites.append(
            {
                "site": site,
                "file": path.name,
                "candidate_sha256": diag["candidate_sha256"],
                "checks": {k: diag["checks"].get(k) for k in KEY_CHECKS},
                "nan_inside_footprint": int((~np.isfinite(inside)).sum()),
                "outside_encoding": (
                    "nan" if np.isnan(outside).all() else ("zero" if np.isfinite(outside).all() and (outside == 0).all() else "mixed")
                ),
                "nonzero_outside_footprint": int(np.nansum(np.nan_to_num(outside) != 0)),
                "positive_cells": int(np.nansum(arr > 0)),
                "submission_authorized": False,
            }
        )

    sub_site, parent_site = SUBSET_PAIR
    subset = None
    if sub_site in arrays and parent_site in arrays:
        child = arrays[sub_site] > 0
        parent = arrays[parent_site] > 0
        subset = {
            "child": sub_site,
            "parent": parent_site,
            "child_positives": int(child.sum()),
            "parent_positives": int(parent.sum()),
            "child_is_strict_subset_of_parent": bool(not (child & ~parent).any()),
            "parent_only_positives": int((parent & ~child).sum()),
        }

    with rasterio.open(labels) as src:
        lab = src.read(1)
    sample_pos = np.nan_to_num(sample_grid) > 0
    label_pos = lab > 0
    sample_vs_labels = {
        "sample_positives": int(sample_pos.sum()),
        "label_positives": int(label_pos.sum()),
        "positives_identical": bool(np.array_equal(sample_pos, label_pos)),
        "label_unique_values": sorted(int(v) for v in np.unique(lab)),
        "official_description": "A sample submission that predicts total fault absence (problem page, section 'Submission format').",
        "irregular": bool(sample_pos.sum() > 0),
    }

    return {
        "schema": "karage1-nine-site-format-receipt-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sample": str(sample.relative_to(ROOT)),
        "sample_footprint_cells": int(footprint.sum()),
        "labels": str(labels.relative_to(ROOT)),
        "source_authentication": "Mirror consistency only (hash-pinned third-party mirror). Organizer authenticity NOT established.",
        "official_rules_verified_against": [
            "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/",
            "https://docs.nlr.gov/docs/fy26osti/96647.pdf",
        ],
        "sites": sites,
        "subset_check": subset,
        "sample_vs_labels": sample_vs_labels,
        "submission_authorized": False,
        "portal_acceptance": "not tested by this receipt",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=None, help="write JSON receipt here")
    args = ap.parse_args(argv)
    receipt = build_receipt()
    text = json.dumps(receipt, indent=2, sort_keys=True)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
