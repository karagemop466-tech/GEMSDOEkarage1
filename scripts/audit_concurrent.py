#!/usr/bin/env python3
"""Independently check one later peer research raster against pinned references.

This does not reproduce the peer's model or holdout, cover the full shared
registry, check a pre-placement surface, or authorize any submission.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.ndimage import binary_dilation

try:
    from scripts.audit_references import ROOT, SITES, binary_rank_correlation, disk, fetch_files, load_manifest, read_grid, same_grid, valid_gdal_mask, verify_file
    from scripts.validate_geotiff import diagnose
except ModuleNotFoundError:
    from audit_references import ROOT, SITES, binary_rank_correlation, disk, fetch_files, load_manifest, read_grid, same_grid, valid_gdal_mask, verify_file
    from validate_geotiff import diagnose


EXPECTED_SOURCE = {
    "id": "GEMSDOE25_H79_research_only", "repo": "buffedlizard55-lab/GEMSDOE25",
    "ref": "19b219f629440b9975b093f459c74e21a42476ca",
    "path": "docs/downloads/gems25-h79-cthm-crustal-sgmc-b2-37654-20261027-e7ad8a4bf3ed-zeros.tif",
    "bytes": 826248, "sha256": "df13471fe77d6eb6dcf24ac4f2d453a36bd0c78e9c51caa34ac032104897a5ef",
}


def validate_source(entry: dict) -> None:
    if not isinstance(entry, dict) or any(entry.get(k) != v for k, v in EXPECTED_SOURCE.items()):
        raise ValueError("unexpected concurrent source; review and update the pin explicitly")
    expected_card = f"https://github.com/{entry['repo']}/blob/{entry['ref']}/registry/run_card_h79_cthm_2026-10-27.json"
    if entry.get("source_run_card") != expected_card:
        raise ValueError("unexpected source card URL")


def compare_binary_support(candidate: np.ndarray, reference: np.ndarray, footprint: np.ndarray) -> dict:
    if candidate.shape != reference.shape or candidate.shape != footprint.shape:
        raise ValueError("candidate, reference and footprint shapes differ")
    candidate = candidate & footprint
    reference = reference & footprint
    count = int(candidate.sum())
    if not count or not reference.any():
        raise ValueError("empty support is not a valid novelty comparison")
    near = binary_dilation(reference, structure=disk(3))
    overlap = int(np.count_nonzero(candidate & near))
    return {
        "candidate_dots": count,
        "within_3px_count": overlap,
        "within_3px_fraction": overlap / count,
        "strictly_exceeds_70_percent": 10 * overlap > 7 * count,
        "binary_support_spearman": binary_rank_correlation(candidate, reference, footprint),
    }


def run(cache: Path, entry: dict) -> dict:
    validate_source(entry)
    refs = {x["id"]: x for x in load_manifest(ROOT / "registry/reference_assets.json")}
    for item in [*refs.values(), entry]:
        verify_file(cache / (item["id"] + ".tif"), item)
    template, tmeta = read_grid(cache / "template.tif")
    footprint = valid_gdal_mask(cache / "template.tif") & np.isfinite(template)
    cpath = cache / (entry["id"] + ".tif")
    candidate, cmeta = read_grid(cpath)
    if (not same_grid(cmeta, tmeta) or not valid_gdal_mask(cpath)[footprint].all()
            or not np.all(np.isin(candidate[footprint], (0, 1)))):
        raise ValueError("candidate must match the pinned grid and be unmasked binary inside")
    cdots = (candidate > 0) & footprint
    comparisons = {}
    for name in (*SITES, "lattice"):
        rpath = cache / (name + ".tif")
        reference, rmeta = read_grid(rpath)
        if (not same_grid(rmeta, tmeta) or not valid_gdal_mask(rpath)[footprint].all()
                or not np.all(np.isin(reference[footprint], (0, 1)))):
            raise ValueError(f"invalid binary reference: {name}")
        comparisons[name] = compare_binary_support(cdots, reference > 0, footprint)
    format_report = diagnose(cpath, cache / "template.tif", refs["template"]["sha256"])
    format_report["candidate"] = cpath.name
    format_report["template"] = "template.tif"
    return {
        "schema": "karage1-concurrent-research-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "scope": "Later peer research artifact, not generated or submitted by this project; no model/holdout replay or full-registry check.",
        "source": entry,
        "owner_status": "Research only; DO NOT SUBMIT (per pinned peer run card).",
        "format_diagnostic": format_report,
        "comparisons_candidate_to_reference": comparisons,
        "surface_correlation_checked": False,
        "holdout_reproduced": False,
        "organizer_score_receipt": None,
        "submission_authorized": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache/references")
    ap.add_argument("--out", type=Path, default=ROOT / "docs/data/concurrent-review.json")
    ap.add_argument("--fetch", action="store_true", help="Fetch the extra pinned peer artifact via gh")
    args = ap.parse_args()
    try:
        entry = json.loads((ROOT / "registry/concurrent_asset.json").read_text())
        # Validate before using any untrusted path in the fetch helper.
        validate_source(entry)
        if args.fetch:
            fetch_files([entry], args.cache)
        result = run(args.cache, entry)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.out.with_suffix(args.out.suffix + ".tmp")
        tmp.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        tmp.replace(args.out)
        print(f"Concurrent audit written to {args.out}; no submission is authorized.")
        return 0
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as exc:
        print(f"CONCURRENT AUDIT FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
