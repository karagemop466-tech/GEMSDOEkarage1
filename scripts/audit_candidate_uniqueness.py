#!/usr/bin/env python3
"""Independent read-back audit of a candidate GeoTIFF + uniqueness check.

Re-reads the file from disk (not the in-memory array), then checks:
* format: single band, float32, EPSG:32611, shape 3730 x 3292, transform, all-finite,
  values in [0, 1]; footprint cells (sample_submission finite) and outside-footprint.
* catalogue collar: count of positives on / within 1, 2, 3 px of mapped catalogue.
* uniqueness vs (a) the 15 SHA-pinned registry rasters restored from github.com
  (data/restore_receipt.json) and (b) the 9 earlier TIFs committed in docs/downloads/,
  using the shared comparator vendor/gems57/uniqueness.compare_array_to_registry
  (3-px lattice overlap in both directions, rank correlation, exact digest).
* the literal protocol gates: |rho| > 0.90 -> duplicate; > 70% dots within 3 px -> duplicate.

Writes evidence/candidate_uniqueness_<tag>_20261029.json. The index is PARTIAL
(15 restored + 9 committed), so the result is a bounded scope, not a full registry scan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57.grid import DATA_DIR, EPSG, HEIGHT, TRANSFORM, WIDTH, load_grid  # noqa: E402
from gems57.uniqueness import compare_array_to_registry  # noqa: E402


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build_index() -> dict:
    rec = json.loads((ROOT / "data" / "restore_receipt.json").read_text())
    rasters = []
    for f in rec["files"]:
        if f.get("group") != "registry":
            continue
        p = ROOT / ".cache" / "gems_data" / f["dest"]
        rasters.append(dict(repo_first=f["id"], sources=[f["dest"]], cache_file=str(p), sha256=f["sha256"]))
    for p in sorted((ROOT / "docs" / "downloads").glob("*.tif")):
        rasters.append(dict(repo_first="karage1-own-earlier", sources=[p.name], cache_file=str(p),
                            sha256=sha256(p)))
    return dict(
        expected_raster_count=len(rasters), registry_rasters_expected=len(rasters),
        complete_accessible_scan=False,
        errors=["PARTIAL index: 15 SHA-pinned registry rasters + 9 committed karage1 TIFs. "
                "The full DrivenData/peer registry was not scanned; no complete-inventory claim is made."],
        rasters=rasters,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("candidate", type=Path)
    ap.add_argument("--tag", required=True)
    args = ap.parse_args()
    cand = args.candidate.resolve()

    grid = load_grid(DATA_DIR)
    fp = grid.footprint
    with rasterio.open(cand) as src:
        fmt = dict(
            driver=src.driver, count=src.count, dtype=src.dtypes[0], crs=str(src.crs),
            shape=[src.height, src.width], transform=list(tuple(src.transform)[:6]),
            nodata=src.nodata, descriptions=list(src.descriptions),
        )
        arr = src.read(1)
    fmt["crs_ok"] = fmt["crs"] == f"EPSG:{EPSG}"
    fmt["shape_ok"] = fmt["shape"] == [HEIGHT, WIDTH]
    fmt["transform_ok"] = fmt["transform"] == list(tuple(TRANSFORM)[:6])
    fmt["single_band_float32"] = fmt["count"] == 1 and fmt["dtype"] == "float32"
    fmt["all_finite"] = bool(np.isfinite(arr).all())
    fmt["min"] = float(np.nanmin(arr))
    fmt["max"] = float(np.nanmax(arr))
    fmt["values_in_0_1"] = bool(fmt["min"] >= 0.0 and fmt["max"] <= 1.0)
    fmt["unique_values"] = [float(x) for x in np.unique(arr)[:5]]
    fmt["outside_footprint_positive"] = int(((arr > 0) & ~fp).sum())
    fmt["inside_footprint_cells"] = int(fp.sum())

    pos = (arr > 0) & fp
    n = int(pos.sum())
    dist = ndi.distance_transform_edt(~grid.catalogue)
    d = dist[pos]
    collar = dict(
        dots=n,
        on_catalogue=int((d == 0).sum()),
        within_1px=int((d <= 1.0).sum()),
        within_2px=int((d <= 2.0).sum()),
        within_3px=int((d <= 3.0).sum()),
        min_distance_px=float(d.min()) if n else None,
    )

    comparison = compare_array_to_registry(arr, build_index(), fp, file_sha256=sha256(cand))
    rows = comparison["rows"]
    checked = [r for r in rows if "error" not in r]
    errors = [r for r in rows if "error" in r]
    worst_my_overlap = max(checked, key=lambda r: r["my_dots_within_3px_of_theirs"]) if checked else None
    rank_rows = [r for r in checked if r.get("spearman_full_footprint") is not None]
    worst_rho = max(rank_rows, key=lambda r: abs(r["spearman_full_footprint"])) if rank_rows else None
    lattice = next((r for r in checked if "13GEMS" in str(r.get("file", ""))), None)
    out = dict(
        schema="karage1-candidate-uniqueness-v1",
        candidate=str(cand.relative_to(ROOT)),
        candidate_sha256=sha256(cand),
        format=fmt,
        catalogue_collar=collar,
        registry_scope="PARTIAL: 15 pinned registry + 9 committed karage1 TIFs (see index errors)",
        comparator=dict(module="vendor/gems57/uniqueness.py", thresholds=dict(
            rank_correlation_abs=0.90, my_dots_within_3px=0.70, jaccard=0.50)),
        gates=dict(
            worst_my_dots_within_3px=(worst_my_overlap or {}).get("my_dots_within_3px_of_theirs"),
            worst_my_overlap_file=(worst_my_overlap or {}).get("file"),
            max_abs_spearman=(abs(worst_rho["spearman_full_footprint"]) if worst_rho else None),
            max_abs_spearman_file=(worst_rho or {}).get("file"),
            identical_bytes_matches=sum(1 for r in checked if r.get("identical_bytes")),
            identical_decoded_matches=sum(1 for r in checked if r.get("identical_decoded_predictions")),
            rows_with_errors=len(errors),
            duplicate_count_by_comparator=comparison.get("duplicate_count"),
            lattice_row=lattice,
        ),
        comparator_unique_flag=comparison.get("unique"),
        comparison_rows=rows,
        software=dict(numpy=np.__version__, rasterio=rasterio.__version__),
    )
    dst = ROOT / "evidence" / f"candidate_uniqueness_{args.tag}_20261029.json"
    text = json.dumps(out, indent=2, default=float, allow_nan=False) + "\n"
    dst.write_text(text.replace(str(ROOT) + "/", ""))
    print(json.dumps({k: out[k] for k in ("candidate_sha256", "catalogue_collar", "comparator_unique_flag")}, indent=2))
    print("gates:", json.dumps({k: v for k, v in out["gates"].items() if k != "lattice_row"}, default=float))
    print("lattice:", json.dumps(lattice, default=float)[:600])
    print("format:", json.dumps({k: fmt[k] for k in ("crs_ok", "shape_ok", "transform_ok", "single_band_float32", "all_finite", "values_in_0_1", "outside_footprint_positive")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
