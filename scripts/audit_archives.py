#!/usr/bin/env python3
"""Check inherited synthetic demonstrators; never authorize a submission."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import numpy as np

try:
    from scripts.audit_references import ROOT, load_manifest, read_grid, sha256, valid_gdal_mask, verify_file
    from scripts.audit_concurrent import compare_binary_support
    from scripts.validate_geotiff import diagnose
except ModuleNotFoundError:
    from audit_references import ROOT, load_manifest, read_grid, sha256, valid_gdal_mask, verify_file
    from audit_concurrent import compare_binary_support
    from validate_geotiff import diagnose

ASSETS = {
    "CDA1_zero": {
        "path": "archive/cda1-demonstrator/docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif",
        "sha256": "753b8d47f951894240a80826e8100216c5e84613caf3d2596272d26a1b85c120",
    },
    "HUNQ1_dots": {
        "path": "archive/prototype/docs/downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-dots.tif",
        "sha256": "8fc2f9e1f17f57bf09432433446550a8d02aa2c8ddad35e6db4dd5cf925dd23c",
    },
    "HUNQ1_zero": {
        "path": "archive/prototype/docs/downloads/gemsdoe-unique-hunq1-20261027T210333Z-d880eae3246b-zeros.tif",
        "sha256": "642a6369a3a7e9a5c5761983e110c60a6abbc196abd339985e11da351d3e5c4b",
    },
}


def review(cache: Path) -> dict:
    refs = {x["id"]: x for x in load_manifest(ROOT / "registry/reference_assets.json")}
    for key in ("template", "lattice"):
        verify_file(cache / f"{key}.tif", refs[key])
    template, _ = read_grid(cache / "template.tif")
    lattice, _ = read_grid(cache / "lattice.tif")
    footprint = valid_gdal_mask(cache / "template.tif") & np.isfinite(template)
    if not valid_gdal_mask(cache / "lattice.tif")[footprint].all():
        raise ValueError("lattice has masked or nodata pixels inside footprint")
    outputs = {}
    for name, info in ASSETS.items():
        p = ROOT / info["path"]
        if sha256(p) != info["sha256"]:
            raise ValueError(f"quarantined asset changed: {name}")
        diagnostic = diagnose(p, cache / "template.tif", refs["template"]["sha256"])
        diagnostic["candidate"] = info["path"]
        diagnostic["template"] = "template.tif"
        record = {
            "sha256": info["sha256"],
            "origin": "Synthetic demonstrator from a parallel session; not a competition prediction.",
            "format_diagnostic": diagnostic,
        }
        if name == "CDA1_zero":
            data, _ = read_grid(p)
            if not valid_gdal_mask(p)[footprint].all() or not np.all(np.isin(data[footprint], (0, 1))):
                raise ValueError("CDA1 support is not unmasked binary inside footprint")
            record["vs_lattice"] = compare_binary_support(data > 0, lattice > 0, footprint)
            record["purported_holdout_status"] = (
                "Invalid: archived spatially_blocked_holdout returns hard-coded numbers independent of input; no measured HOLDOUT-DTI."
            )
            record["archived_lattice_fraction_claim"] = 0.9999
        outputs[name] = record
    return {
        "schema": "karage1-quarantined-archive-audit-v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "scope": "Inherited synthetic artifacts; format and lattice checks only, not holdout scoring or a full-registry clearance.",
        "assets": outputs,
        "submission_authorized": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache/references")
    ap.add_argument("--out", type=Path, default=ROOT / "docs/data/archive-review.json")
    args = ap.parse_args()
    try:
        result = review(args.cache)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        tmp = args.out.with_suffix(args.out.suffix + ".tmp")
        tmp.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
        tmp.replace(args.out)
        print(f"Archive audit written to {args.out}; no submission is authorized.")
        return 0
    except (OSError, ValueError) as exc:
        print(f"ARCHIVE AUDIT BLOCKED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
