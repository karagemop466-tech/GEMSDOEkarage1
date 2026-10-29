#!/usr/bin/env python3
"""Saved-byte audit of one local GeoTIFF using the shared template validators.

Usage: python scripts/audit_local_tif.py docs/downloads/<file>.tif --out evidence/<receipt>.json

Reads only the restored inputs in .cache/gems_data (run scripts/restore_data.py first).
Writes a JSON receipt; it never changes the TIF, the registry or any submission state.
"""
from __future__ import annotations

import argparse
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

DATA = ROOT / ".cache" / "gems_data"
REG = DATA / "registry"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("tif")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    path = (ROOT / a.tif).resolve()
    sample = DATA / "sample_submission.tif"
    with rasterio.open(sample) as s:
        fp = np.isfinite(s.read(1))
    with rasterio.open(DATA / "labels.tif") as s:
        cat = (s.read(1) == 1) & fp
    raw = path.read_bytes()
    report = gates.format_report(path, sample, footprint=fp)
    local = VAL.validate(path, fp, cat)
    with rasterio.open(path) as s:
        arr = s.read(1)
    dots = UQ._dots(arr)
    uq = {}
    for p in sorted(REG.glob("*.tif")):
        with rasterio.open(p) as s:
            t = s.read(1)
        uq[p.name] = dict(forward_3px_overlap=UQ.dot_overlap(arr, t),
                          reverse_3px_overlap=UQ.dot_overlap(t, arr),
                          their_dots=int(UQ._dots(t).sum()))
    lattice = next(v for k, v in uq.items() if k.startswith("13GEMSDOE"))
    focus = {k: v for k, v in uq.items() if not k.startswith(("13GEMSDOE", "GEMS19"))}
    worst = max(focus.items(), key=lambda kv: kv[1]["forward_3px_overlap"])
    receipt = dict(
        schema="karage1-local-tif-audit-v1",
        file=str(path.relative_to(ROOT)),
        sha256=hashlib.sha256(raw).hexdigest(),
        bytes=len(raw),
        audited_utc=datetime.now(timezone.utc).isoformat(),
        format_report_ok=bool(report["ok"]),
        format_report_problems=report.get("problems", []),
        validator_checks=local.get("checks"),
        positives=int(dots.sum()),
        positives_outside_footprint=int(((arr > 0) & ~fp).sum()),
        positives_on_mapped_catalogue=int(((arr > 0) & cat).sum()),
        value_min=float(np.nanmin(arr)), value_max=float(np.nanmax(arr)),
        nan_count=int(np.isnan(arr).sum()),
        lattice_forward_3px_overlap=lattice["forward_3px_overlap"],
        worst_focus_file=worst[0],
        worst_focus_forward_3px_overlap=worst[1]["forward_3px_overlap"],
        registry_rasters_checked=len(uq),
        ok_to_submit=False,
        verdict="research audit only; not cleared (literal lattice gate and holdout not run)",
        comparisons=uq,
    )
    Path(a.out).write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("sha256", "positives", "positives_outside_footprint",
                                              "lattice_forward_3px_overlap", "worst_focus_forward_3px_overlap",
                                              "format_report_ok")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
