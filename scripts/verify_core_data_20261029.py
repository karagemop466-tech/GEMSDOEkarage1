#!/usr/bin/env python3
"""Verify restored core data and local submission rasters; write an evidence JSON.

Read-only. Checks (1) SHA-256 pins from registry/data_manifest.json against the restored
bytes in .cache/gems_data, (2) label/template semantics and the sample-vs-label overlap,
(3) footprint agreement between the feature stack and the label footprint, and (4) the
values/NaN/nodata convention of every local TIF in docs/downloads against the portal's
stated rule (float32, values in [0, 1], NaN or null outside bounds).

Nothing here is a model score. Output is labelled as a data-integrity check only.
Usage: .venv/bin/python scripts/verify_core_data_20261029.py
"""
from __future__ import annotations

import glob
import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / ".cache" / "gems_data"
OUT = ROOT / "evidence" / "core_data_verification_20261029.json"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    manifest = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    pins = []
    for entry in manifest["files"]:
        if entry.get("group") != "core":
            continue
        dest = CACHE / entry["dest"]
        if not dest.exists():
            pins.append({"id": entry["id"], "present": False})
            continue
        got = sha256_file(dest)
        pins.append({"id": entry["id"], "present": True, "sha256_matches_pin": got == entry["sha256"],
                     "sha256": got, "bytes": dest.stat().st_size})

    label_path = CACHE / "labels.tif"
    sample_path = CACHE / "sample_submission.tif"
    feat_path = CACHE / "training_features.tif"
    semantics: dict = {}
    if label_path.exists() and sample_path.exists() and feat_path.exists():
        with rasterio.open(label_path) as ds:
            lab = ds.read(1)
            lab_nodata = ds.nodata
        with rasterio.open(sample_path) as ds:
            smp = ds.read(1)
        with rasterio.open(feat_path) as ds:
            feat_nodata = ds.nodata
            feat0 = ds.read(1)
        footprint_lab = lab != -1
        footprint_feat = feat0 != np.float32(feat_nodata)
        sample_ones = smp == 1
        semantics = {
            "labels_values": {str(int(v)): int((lab == v).sum()) for v in np.unique(lab)},
            "labels_nodata": lab_nodata,
            "labels_outside_minus1_count": int((lab == -1).sum()),
            "sample_nan_count": int(np.isnan(smp).sum()),
            "sample_ones": int(sample_ones.sum()),
            "sample_ones_on_label_fault": int((sample_ones & (lab == 1)).sum()),
            "sample_ones_on_label_background": int((sample_ones & (lab == 0)).sum()),
            "sample_is_label_copy_on_positives": bool(sample_ones.sum() == (lab == 1).sum()
                                                      and (sample_ones & (lab == 1)).sum() == (lab == 1).sum()),
            "training_features_nodata": feat_nodata,
            "footprint_disagreement_label_vs_feature_band1": int((footprint_lab != footprint_feat).sum()),
        }

    local = []
    for f in sorted(glob.glob(str(ROOT / "docs" / "downloads" / "*.tif"))):
        with rasterio.open(f) as ds:
            a = ds.read(1)
            rec = {
                "file": Path(f).name,
                "dtype": ds.dtypes[0],
                "count": ds.count,
                "crs_epsg": ds.crs.to_epsg() if ds.crs else None,
                "shape": list(a.shape),
                "nodata": None if ds.nodata is None else str(ds.nodata),
                "nan_count": int(np.isnan(a).sum()),
                "min_finite": float(np.nanmin(a)),
                "max_finite": float(np.nanmax(a)),
                "values_outside_0_1": int(((a < 0) | (a > 1)).sum()),
                "positives": int((a > 0).sum()),
            }
            local.append(rec)

    any_out_of_range = any(r["values_outside_0_1"] for r in local)
    card = {
        "schema": "karage1-core-data-verification-v1",
        "generated_utc": "2026-10-29",
        "label": "DATA-INTEGRITY CHECK (not a model score; no HOLDOUT-DTI, no ORGANIZER-CONFIRMED value)",
        "restored_core_pins": pins,
        "label_and_template_semantics": semantics,
        "local_tifs": local,
        "any_local_tif_value_outside_0_1": any_out_of_range,
        "portal_range_error_reproduced_locally": False if not any_out_of_range else "partially",
        "notes": [
            "Mirror hashes prove byte consistency with pinned mirrors, not DrivenData authenticity.",
            "The mirrored sample_submission.tif equals the label positives; the DrivenData page calls the sample 'total fault absence'. Treat as an irregularity for owner review; do not use it as a submission.",
        ],
    }
    OUT.write_text(json.dumps(card, indent=2) + "\n")
    print(json.dumps({k: card[k] for k in ("any_local_tif_value_outside_0_1", "portal_range_error_reproduced_locally")}, indent=2))
    print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
