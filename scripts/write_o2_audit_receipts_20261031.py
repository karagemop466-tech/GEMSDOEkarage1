#!/usr/bin/env python3
"""Saved-byte audit receipts for the E1 (H-O2) candidate TIFs, session arena/9cf124bb, 2026-10-31.

Why this exists: scripts/audit_local_tif.py needs a 13GEMSDOE lattice raster under
registry/, and that raster is not in this checkout (only its summary numbers are in
evidence/). The receipt is therefore written with the lattice comparison set to null and
the reason stated. Everything else comes from the repo's shared validators, applied to the
exact committed bytes:

- vendor/gems57/gates.py      format_report
- vendor/gems57/validate.py   validate (range, NaN, footprint, catalogue zero)
- vendor/gems57/uniqueness.py dot_overlap against every registry raster (same grid)

Each receipt is ok_to_submit=false. Nothing is cleared and no submission state changes.

Inputs: data/sample_submission.tif, data/labels.tif (restored, hash-verified, ignored by git),
registry/*.tif (committed). Usage: .venv/bin/python scripts/write_o2_audit_receipts_20261031.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "vendor")]
from gems57 import gates, uniqueness as UQ, validate as VAL  # noqa: E402

DATA = ROOT / "data"
REG = ROOT / "registry"
DL = ROOT / "docs/downloads"
STEM = "DO-NOT-SUBMIT_karage1-o2-lidar-scarp-halo-prune-37654-20261031"
TARGETS = {
    f"{STEM}-zeros.tif": "evidence/audit_o2_candidate_zeros_20261031.json",
    f"{STEM}-nan.tif": "evidence/audit_o2_candidate_nan_20261031.json",
}
LATTICE_NOTE = ("13GEMSDOE lattice raster is not present in this checkout (registry/ holds the nine focus rasters only); "
                "lattice comparison not run. Its summary numbers are in evidence/lattice_saturation_null_20261029.json.")


def main() -> int:
    sample = DATA / "sample_submission.tif"
    with rasterio.open(sample) as s:
        fp = np.isfinite(s.read(1))
    with rasterio.open(DATA / "labels.tif") as s:
        cat = (s.read(1) == 1) & fp
    registry = {}
    for p in sorted(REG.glob("*.tif")):
        with rasterio.open(p) as s:
            registry[p.name] = s.read(1)
    for name, out in TARGETS.items():
        path = DL / name
        raw = path.read_bytes()
        report = gates.format_report(path, sample, footprint=fp)
        local = VAL.validate(path, fp, cat)
        with rasterio.open(path) as s:
            arr = s.read(1)
        clean = np.nan_to_num(arr, nan=0.0)
        dots = UQ._dots(clean)
        comparisons = {}
        for k, t in registry.items():
            comparisons[k] = dict(
                forward_3px_overlap=round(float(UQ.dot_overlap(clean, t)), 6),
                reverse_3px_overlap=round(float(UQ.dot_overlap(t, clean)), 6),
                their_dots=int(UQ._dots(np.nan_to_num(t, nan=0.0)).sum()),
            )
        focus = {k: v for k, v in comparisons.items() if k.startswith("GEMSDOE")}
        worst = max(focus.items(), key=lambda kv: kv[1]["forward_3px_overlap"])
        worst_any = max(comparisons.items(), key=lambda kv: kv[1]["forward_3px_overlap"])
        receipt = dict(
            schema="karage1-local-tif-audit-v1",
            file=path.relative_to(ROOT).as_posix(),
            sha256=hashlib.sha256(raw).hexdigest(),
            bytes=len(raw),
            audited_utc=datetime.now(timezone.utc).isoformat(),
            method="repo shared validators (gates.format_report, validate.validate, uniqueness.dot_overlap) on the committed bytes; lattice not run",
            format_report_ok=bool(report["ok"]),
            format_report_problems=report.get("problems", []),
            validator_checks=local.get("checks"),
            positives=int(dots.sum()),
            positives_outside_footprint=int(((clean > 0) & ~fp).sum()),
            positives_on_mapped_catalogue=int(((clean > 0) & cat).sum()),
            value_min=float(np.nanmin(arr)),
            value_max=float(np.nanmax(arr)),
            nan_count=int(np.isnan(arr).sum()),
            lattice_forward_3px_overlap=None,
            lattice_status=LATTICE_NOTE,
            worst_focus_file=worst[0],
            worst_focus_forward_3px_overlap=worst[1]["forward_3px_overlap"],
            worst_any_registry_file=worst_any[0],
            worst_any_registry_forward_3px_overlap=worst_any[1]["forward_3px_overlap"],
            registry_rasters_checked=len(comparisons),
            ok_to_submit=False,
            verdict="research audit only; not cleared (literal dot-overlap gate fails against a local probability blanket; holdout negative)",
            comparisons=comparisons,
        )
        (ROOT / out).write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
        print(f"{out}: sha256={receipt['sha256'][:16]} positives={receipt['positives']} "
              f"worst_focus={worst[1]['forward_3px_overlap']:.4f} worst_any={worst_any[0]} {worst_any[1]['forward_3px_overlap']:.4f} "
              f"format_ok={receipt['format_report_ok']} validator_ok={local.get('all_checks_passed')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
