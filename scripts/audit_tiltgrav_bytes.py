#!/usr/bin/env python3
"""Saved-byte audit for the H-TILTGRAV final TIF (2026-10-29).

Recomputes hashes from the bytes on disk and copies measured overlap values
from evidence/site_overlap_matrix_20261029.json. Writes
evidence/local_candidates_tiltgrav_audit_20261029.json. Never sets approval.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TIF = ROOT / "docs/downloads/karage1-tiltgrav-ridge-sp6-37654-20261029.tif"
ZIP = TIF.with_suffix(".zip")
OUT = ROOT / "evidence/local_candidates_tiltgrav_audit_20261029.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    final = json.loads((ROOT / "evidence/tiltgrav_final_20261029.json").read_text())
    rec = final["final_receipt"]
    matrix = json.loads((ROOT / "evidence/site_overlap_matrix_20261029.json").read_text())
    labels = [item["label"] for item in matrix["items"]]
    cand = labels.index("NEW candidate (H-TILTGRAV)")
    lattice = labels.index("13GEMSDOE lattice (calibration)")
    row = matrix["matrix"][cand]
    focus = [row[i] for i in range(9)]
    assert rec["sha256"] == sha256(TIF), "receipt sha256 does not match bytes on disk"
    assert rec["zip_sha256"] == sha256(ZIP), "zip sha256 does not match bytes on disk"
    v = rec["validator"]
    out = {
        "schema": "local-candidate-saved-byte-audit/v1",
        "date": "2026-10-29",
        "instrument": "H-TILTGRAV final candidate; hashes recomputed from disk; overlaps from site_overlap_matrix_20261029.json",
        "candidates": [{
            "file": TIF.name,
            "sha256": sha256(TIF),
            "bytes": TIF.stat().st_size,
            "zip_file": ZIP.name,
            "zip_sha256": sha256(ZIP),
            "dots": rec["metadata"]["n_dots"],
            "verdict": rec["metadata"]["verdict"],
            "format_all_checks_passed": bool(v["all_checks_passed"]),
            "outside_nan_cells": v["outside_nan_cells"],
            "in_footprint_positive": v["in_footprint_positive"],
            "catalogue_positive_hits": v["catalogue_positive_hits"],
            "lattice_forward_overlap": row[lattice],
            "lattice_forward_overlap_literal_gate": 0.70,
            "worst_nine_forward_overlap": {"site": labels[focus.index(max(focus))].split(" ")[0], "frac": max(focus)},
            "focus_forward_overlap_range": [min(focus), max(focus)],
            "uniqueness_cleared": False,
            "approved_for_weekly_slot": False,
            "submit_authorized": False,
        }],
    }
    OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out["candidates"][0], indent=1)[:600])


if __name__ == "__main__":
    main()
