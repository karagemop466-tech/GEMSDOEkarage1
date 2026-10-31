#!/usr/bin/env python3
"""Check the K-PROXY-DETECT GeoTIFF against every GeoTIFF fetched from the listed GEMSDOE repos.

Input : evidence/listed_sites_tif_inventory_20261031.json (scripts/fetch_listed_site_tifs.py) with the
        bytes under data/peers/ (git-ignored), plus this repository's own GeoTIFFs.
Output: evidence/kp1_uniqueness_vs_listed_sites_20261031.json

Measures, matching the release gate's literal rule where it applies:
* exact byte duplicate (SHA-256) of the candidate;
* |Spearman| over the scored footprint (finite cells of the NaN-outside registry masks). For a
  binary raster Spearman equals Pearson exactly (average ranks are affine in a 0/1 variable), so it
  is computed exactly for binary files; non-binary files are flagged and get no rho;
* fraction of the candidate's dots within 3 px of the peer's dots. A peer on a different grid is
  mapped by world coordinates (EPSG:32611, no rotation), so it is compared rather than skipped.

Dense rasters (more than DENSE_CUTOFF positives) are recorded and excluded from the rule, because
almost any dot falls within 3 px of a dense field. They are listed, never hidden.
"""
from __future__ import annotations

import glob
import hashlib
import json
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import rasterio
from scipy.spatial import cKDTree

ROOT = Path(__file__).resolve().parents[1]
TIF = ROOT / "docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif"
INV = ROOT / "evidence/listed_sites_tif_inventory_20261031.json"
OUT = ROOT / "evidence/kp1_uniqueness_vs_listed_sites_20261031.json"
DOT_PX = 3.0
RHO_LIMIT, OVERLAP_LIMIT = 0.90, 0.70
DENSE_CUTOFF = 1_000_000

# Filled in main() and inherited by the worker processes (fork).
G: dict = {}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def footprint() -> np.ndarray:
    masks = []
    for p in sorted((ROOT / "registry").glob("GEMSDOE*.tif")):
        with rasterio.open(p) as ds:
            a = ds.read(1)
        if not np.isfinite(a).all():
            masks.append(np.isfinite(a))
    if not masks or not all(np.array_equal(masks[0], m) for m in masks):
        raise SystemExit("cannot derive a consistent footprint from registry NaN masks")
    return masks[0]


def _work(peer: dict) -> dict:
    path = Path(peer["path"])
    try:
        with rasterio.open(path) as ds:
            if ds.count != 1:
                return dict(peer, error=f"{ds.count} bands; not a single-layer submission")
            data = ds.read(1)
            transform, crs, shape, dtype = ds.transform, (ds.crs.to_string() if ds.crs else None), ds.shape, ds.dtypes[0]
        finite = np.isfinite(data)
        vals = np.where(finite, data, 0).astype(np.float64)
        pos = finite & (vals > 0)
        row = dict(origin=peer["origin"], file=peer["rel"], sha256=peer["sha256"], dtype=dtype, crs=crs,
                   shape=list(shape), positives_all_cells=int(pos.sum()),
                   values_outside_01=int(((vals < 0) | (vals > 1))[finite].sum()))
        binary = bool(np.isin(vals[finite], (0.0, 1.0)).all())
        row["binary"] = binary
        same_grid = bool(shape == G["k_shape"] and crs == G["k_crs"]
                         and tuple(transform)[:6] == tuple(G["k_transform"])[:6])
        row["same_grid"] = same_grid
        if same_grid and binary:
            fv = vals[G["fp"]]
            kv = G["kp_flat"]
            row["abs_spearman_footprint"] = round(abs(float(np.corrcoef(kv, fv)[0, 1])), 6) \
                if fv.std() > 0 else 0.0
        dense = row["positives_all_cells"] > DENSE_CUTOFF
        row["dense_artifact"] = dense
        if row["positives_all_cells"] == 0 or dense:
            row["kp1_dots_within_3px"] = None
            return row
        if transform.b != 0 or transform.d != 0:
            return dict(peer, error="rotated geotransform; mapping not implemented")
        pr, pc = np.nonzero(pos)
        x = transform.a * (pc + 0.5) + transform.c
        y = transform.e * (pr + 0.5) + transform.f
        kt = G["k_transform"]
        kcol = (x - kt.c) / kt.a - 0.5
        krow = (y - kt.f) / kt.e - 0.5
        dist, _ = cKDTree(np.column_stack([krow, kcol])).query(G["kp_pos"], k=1)
        row["kp1_dots_within_3px"] = round(float((dist <= DOT_PX).mean()), 6)
        return row
    except Exception as exc:  # noqa: BLE001 - record and continue
        return dict(peer, error=str(exc)[:200])


def _init() -> None:
    """Build the candidate's state once per worker (fork inherits G, but make it explicit)."""
    pass


def main() -> dict:
    inv = json.loads(INV.read_text())
    fp = footprint()
    with rasterio.open(TIF) as ds:
        kp = ds.read(1)
        k_transform, k_crs, k_shape = ds.transform, ds.crs.to_string(), ds.shape
    kp_pos_mask = (kp > 0) & fp
    kp_pos = np.argwhere(kp_pos_mask).astype(float)
    kp_flat = kp[fp].astype(np.float64)
    kp_sha = sha256(TIF)
    G.update(fp=fp, kp_flat=kp_flat, kp_pos=kp_pos, k_transform=k_transform, k_crs=k_crs, k_shape=k_shape)

    peers = []
    for entry in inv["sites"]:
        for t in entry.get("tifs", []):
            if "local" in t:
                peers.append(dict(origin=f'{entry["owner"]}/{entry["repo"]}', path=str(ROOT / t["local"]),
                                  rel=t["local"], sha256=t.get("sha256")))
    for p in sorted({*glob.glob(str(ROOT / "docs/**/*.tif"), recursive=True),
                     *glob.glob(str(ROOT / "archive/**/*.tif"), recursive=True),
                     *glob.glob(str(ROOT / "registry/*.tif"))}):
        peers.append(dict(origin="this repository", path=p, rel=str(Path(p).relative_to(ROOT)), sha256=None))

    results, errors, dup_of = [], [], []
    seen: dict[str, str] = {}
    todo = []
    for peer in peers:
        path = Path(peer["path"])
        if not path.exists():
            errors.append({"file": peer["rel"], "error": "missing local copy"})
            continue
        if path.resolve() == TIF.resolve():
            continue
        digest = peer["sha256"] or sha256(path)
        if digest in seen:
            dup_of.append({"file": peer["rel"], "same_bytes_as": seen[digest], "sha256": digest})
            continue
        seen[digest] = peer["rel"]
        todo.append(dict(peer, sha256=digest))

    with Pool(2) as pool:
        for out in pool.imap_unordered(_work, todo, chunksize=4):
            (errors if "error" in out else results).append(out)

    def is_own_copy(r: dict) -> bool:
        return r.get("sha256") == kp_sha and r.get("origin") == "karagemop466-tech/GEMSDOEkarage1"

    rule = [r for r in results if not r.get("dense_artifact") and r.get("kp1_dots_within_3px") is not None
            and not is_own_copy(r)]
    dense_rows = [r for r in results if r.get("dense_artifact")]
    worst = max(rule, key=lambda r: r["kp1_dots_within_3px"]) if rule else None
    spear = [r for r in rule if r.get("abs_spearman_footprint") is not None]
    worst_rho = max(spear, key=lambda r: r["abs_spearman_footprint"]) if spear else None
    max_overlap = worst["kp1_dots_within_3px"] if worst else 0.0
    max_rho = worst_rho["abs_spearman_footprint"] if worst_rho else 0.0
    # The candidate's own bytes in this repository's main branch are not a competitor; record, do not count.
    own_copies = [r["file"] for r in results + dup_of
                  if r.get("sha256") == kp_sha and r.get("origin") == "karagemop466-tech/GEMSDOEkarage1"]
    exact_dups = [r["file"] for r in results + dup_of
                  if r.get("sha256") == kp_sha and r["file"] not in own_copies]
    # Multi-band inputs (19-band training stacks, feature packs) are not single-layer submissions:
    # they are recorded as excluded, not as failures.
    not_submissions = [e for e in errors if "not a single-layer submission" in e.get("error", "")]
    other_errors = [e for e in errors if e not in not_submissions]
    over_limit = sorted({(r["origin"], r["file"], r["kp1_dots_within_3px"]) for r in rule
                         if r["kp1_dots_within_3px"] > OVERLAP_LIMIT}, key=lambda t: -t[2])

    report = {
        "schema": "kp1-uniqueness-vs-listed-sites-v1",
        "date": "2026-10-31",
        "candidate": {"file": str(TIF.relative_to(ROOT)), "sha256": kp_sha, "dots_in_footprint": int(kp_pos.shape[0])},
        "footprint_cells": int(fp.sum()),
        "rule": {"rho_limit": RHO_LIMIT, "overlap_limit": OVERLAP_LIMIT, "dot_radius_px": DOT_PX},
        "listed_sites_in_inventory": len(inv["sites"]),
        "listed_sites_with_tif_in_repo_tree": sum(1 for s in inv["sites"] if s.get("status") == "fetched"),
        "listed_sites_without_tif_in_repo_tree": [f'{s["owner"]}/{s["repo"]}' for s in inv["sites"]
                                                  if s.get("status") != "fetched"],
        "files_checked": len(results),
        "duplicate_bytes_skipped": len(dup_of),
        "same_grid_files": sum(1 for r in results if r.get("same_grid")),
        "other_grid_files": sum(1 for r in results if not r.get("same_grid")),
        "non_binary_files": sorted(r["file"] for r in results if not r.get("binary")),
        "errors": other_errors,
        "not_single_layer_submissions_excluded": [e["rel"] for e in not_submissions],
        "candidate_own_copies_in_repo_main": own_copies,
        "exact_byte_duplicates_of_candidate": exact_dups,
        "files_over_overlap_limit": [{"origin": o, "file": f, "kp1_dots_within_3px": v} for o, f, v in over_limit],
        "origins_over_overlap_limit": sorted({o for o, _, _ in over_limit}),
        "max_kp1_dots_within_3px_rule_set": {"value": round(max_overlap, 6),
                                              "file": worst["file"] if worst else None,
                                              "origin": worst["origin"] if worst else None,
                                              "passes": max_overlap <= OVERLAP_LIMIT},
        "max_abs_spearman_rule_set": {"value": round(max_rho, 6),
                                       "file": worst_rho["file"] if worst_rho else None,
                                       "passes": max_rho <= RHO_LIMIT},
        "dense_research_rasters_excluded": [dict(file=r["file"], origin=r["origin"], positives=r["positives_all_cells"])
                                            for r in dense_rows],
        "results": sorted(results, key=lambda r: -(r.get("kp1_dots_within_3px") or -1)),
        "duplicate_bytes": dup_of,
    }
    report["passes_literal_rule_on_checked_files"] = bool(
        report["max_kp1_dots_within_3px_rule_set"]["passes"]
        and report["max_abs_spearman_rule_set"]["passes"]
        and not exact_dups and not other_errors)
    OUT.write_text(json.dumps(report, indent=1) + "\n")
    return report


if __name__ == "__main__":
    r = main()
    keys = ("listed_sites_in_inventory", "listed_sites_with_tif_in_repo_tree", "files_checked",
            "duplicate_bytes_skipped", "same_grid_files", "other_grid_files",
            "max_kp1_dots_within_3px_rule_set", "max_abs_spearman_rule_set", "exact_byte_duplicates_of_candidate",
            "passes_literal_rule_on_checked_files")
    out = {k: r[k] for k in keys}
    out["dense_excluded"] = len(r["dense_research_rasters_excluded"])
    out["errors"] = len(r["errors"])
    out["files_over_overlap_limit"] = len(r["files_over_overlap_limit"])
    out["origins_over_overlap_limit"] = r["origins_over_overlap_limit"]
    out["non_binary_files"] = len(r["non_binary_files"])
    print(json.dumps(out, indent=1))
