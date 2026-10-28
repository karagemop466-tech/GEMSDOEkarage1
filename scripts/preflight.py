#!/usr/bin/env python3
"""Write this session's honest negative run card; never selects a weekly slot.

Historical predictions and holdout reports exist, but none is cleared for
submission. This command checks no new candidate. An available format check or
a self-reported score cannot change this negative session result. If the audit is missing or malformed, the outcome remains negative.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_card(audit: dict | None) -> dict:
    # Treat malformed or non-finite source fields as missing, never as a pass.
    audit = audit if isinstance(audit, dict) else {}
    lattice = audit.get("lattice")
    lattice = lattice if isinstance(lattice, dict) else {}
    bound = lattice.get("champion_sized_budget_bound")
    bound = bound if isinstance(bound, dict) else {}

    def fraction(value):
        return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) and 0 <= value <= 1 else None

    coverage = fraction(lattice.get("coverage_fraction"))
    minimum = fraction(bound.get("minimum_fraction"))
    confirmed_bound = minimum is not None and minimum > 0.7 and bound.get("necessarily_exceeds_limit") is True
    reasons = [
        "The prompt refers to a single assigned method lane but supplies no lane paragraph.",
        "The complete current shared registry, a cached feature stack, and a frozen comparable holdout best are not present in this checkout.",
        "No new candidate surface, leakage-canary results, held-out experiment, independent confirmation, or selector decision is produced by this preflight.",
        "The mirrored template is not organizer-authenticated and outside-footprint encoding versus the reported portal range error remains unresolved.",
    ]
    if confirmed_bound:
        reasons.insert(1, "The pinned calibration lattice makes the literal overlap gate impossible at the historical 37,654-dot budget.")
    else:
        reasons.insert(1, "The pinned lattice audit is unavailable or invalid; novelty cannot be certified.")
    return {
        "schema": "karage1-run-card-v1",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "Unassigned; the ranked signed multiscale magnetic-gravity asymmetry hypothesis is a proposal only, not an active lane.",
        "mechanism": "Untested polarity and scale persistence of magnetic and gravity margin gradients, with topographic context and fold-local catalogue handling.",
        "named_non_fault_mimic": "Lithologic contacts or volcanic flow margins can produce similar gradients without fault displacement.",
        "holdout_dti": {"value": None, "evaluator_version": None, "withheld_positives": None, "ci95": None, "status": "not run"},
        "correlation_overlap_vs_registry": {
            "preplacement_surface_spearman": None,
            "final_dot_overlap": None,
            "registry_coverage": "One lattice witness and nine historical rasters audited; not the full registry.",
            "lattice_coverage_fraction": coverage,
            "champion_sized_minimum_overlap_fraction": minimum,
        },
        "raster_sha256": None,
        "validator_output": {
            "no_nan_inside_footprint": None,
            "values_in_0_1": None,
            "crs_shape_transform_match": None,
            "status": "not run; this preflight generates no candidate raster",
        },
        "submission_name": None,
        "submission_note": None,
        "download_available": False,
        "ok_to_submit": False,
        "slot_selected_or_spent": False,
        "geological_experiments_run": 0,
        "blockers": reasons,
        "verdict": "negative",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, default=ROOT / "docs/data/reference-audit.json")
    parser.add_argument("--out", type=Path, default=ROOT / ".cache/preflight/run-card.json")
    args = parser.parse_args()
    if args.out.resolve() == args.audit.resolve() or (
        args.out.exists() and args.audit.exists() and args.out.samefile(args.audit)
    ):
        parser.error("--out must not overwrite the input audit")
    try:
        def reject_constant(value):
            raise ValueError(f"non-standard JSON constant: {value}")
        audit = json.loads(args.audit.read_text(), parse_constant=reject_constant)
        if audit.get("schema") != "karage1-reference-audit-v1":
            audit = None
    except (OSError, ValueError, AttributeError):
        audit = None
    result = run_card(audit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="." + args.out.name + ".", suffix=".tmp", dir=args.out.parent)
    temp = Path(name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
        temp.replace(args.out)
    finally:
        temp.unlink(missing_ok=True)
    print(json.dumps({"verdict": result["verdict"], "ok_to_submit": False, "run_card": str(args.out)}, indent=2))
    # A blocked/negative decision is a nonzero exit so automation cannot treat
    # a successfully written report as permission to upload.
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
