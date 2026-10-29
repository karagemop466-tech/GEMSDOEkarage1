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
    ap.add_argument("--append-fleet", default=None,
                    help="append a row in the fleet-audit schema (evidence/local_downloads_audit_*.json) if absent")
    a = ap.parse_args()
    out_path = (ROOT / a.out).resolve()
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
    if a.append_fleet:
        fleet_path = ROOT / a.append_fleet
        fleet = json.loads(fleet_path.read_text(encoding="utf-8"))
        rel = str(path.relative_to(ROOT))
        if not any(r["file"] == rel for r in fleet["local_downloads"]):
            with rasterio.open(REG / next(k for k in uq if k.startswith("13GEMSDOE"))) as s_:
                lat_arr = s_.read(1)
            near = UQ._near(UQ._dots(lat_arr))
            lat_dots = int((near & dots).sum())
            focus_rows = {k: v for k, v in focus.items() if k.startswith("GEMSDOE")}
            wk = max(focus_rows.items(), key=lambda kv: kv[1]["forward_3px_overlap"])
            fleet["local_downloads"].append(dict(
                file=rel, bytes=len(raw), sha256=receipt["sha256"], is_binary_inside=bool(np.isin(arr[fp], [0, 1]).all()),
                positive_pixels_in_footprint=int(dots.sum()),
                outside_unmasked_positive_pixels=receipt["positives_outside_footprint"],
                outside_any_positive_pixels=receipt["positives_outside_footprint"],
                grid_and_inside_pass=bool(receipt["format_report_ok"]),
                nan_outside_variant_pass=False,
                strict_whole_array_variant_pass=bool(receipt["format_report_ok"]),
                outside_encoding_accepted=bool(receipt["format_report_ok"]),
                lattice_dots_within_3px=lat_dots,
                lattice_directed_overlap_3px=receipt["lattice_forward_3px_overlap"],
                literal_lattice_duplicate=bool(receipt["lattice_forward_3px_overlap"] > 0.70),
                worst_focus_site_3px=wk[0].split("_")[0],
                worst_focus_site_overlap_3px=wk[1]["forward_3px_overlap"],
                ok_to_submit=False,
                audit_receipt=str(out_path.relative_to(ROOT)),
                note="Row appended by scripts/audit_local_tif.py (session 1d15747e). Research audit only; not cleared.",
            ))
            fleet["local_downloads_count"] = len(fleet["local_downloads"])
            fleet_path.write_text(json.dumps(fleet, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    out_path.write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({k: receipt[k] for k in ("sha256", "positives", "positives_outside_footprint",
                                              "lattice_forward_3px_overlap", "worst_focus_forward_3px_overlap",
                                              "format_report_ok")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
