#!/usr/bin/env python3
"""Audit local downloads and pinned sibling/peer GeoTIFFs, reconciling all tracked TIFFs.

This read-only audit checks saved GeoTIFF bytes against the SHA-256-pinned
reference template, catalogue labels, 13GEMSDOE lattice, and nine focus-site
leaders. Git-tracked archive TIFF paths are reconciled against exact current bytes
or the quarantined archive audit. It never selects a weekly slot or authorizes an upload.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from urllib.parse import quote

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_references import disk, load_manifest, sha256, verify_file
from scripts.validate_geotiff import diagnose


def _safe_rel(value: str) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    p = PurePosixPath(value)
    return not p.is_absolute() and all(part not in ("", ".", "..") for part in value.split("/"))


def _unique_object(pairs):
    out = {}
    for k, v in pairs:
        if k in out:
            raise ValueError(f"duplicate JSON key: {k}")
        out[k] = v
    return out


def _reject_constant(val: str):
    raise ValueError(f"non-standard JSON constant: {val}")


def load_peer_pins(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant, object_pairs_hook=_unique_object)
    if not isinstance(raw, dict) or raw.get("schema") != "karage1-peer-ecosystem-pins-v1":
        raise ValueError("unexpected peer-pins schema")
    repos = raw.get("immutable_repos")
    rasters = raw.get("rasters")
    if not isinstance(repos, list) or not repos or not isinstance(rasters, list) or not rasters:
        raise ValueError("peer pins must include non-empty immutable_repos and rasters")
    repo_commits: dict[str, str] = {}
    for row in repos:
        repo = row.get("repo") if isinstance(row, dict) else None
        commit = row.get("commit") if isinstance(row, dict) else None
        if (not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
                or any(part in (".", "..") for part in repo.split("/"))
                or repo in repo_commits
                or not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit)):
            raise ValueError(f"invalid repo pin: {row!r}")
        repo_commits[repo] = commit
    seen_ids: set[str] = set()
    seen_hashes: set[str] = set()
    for item in rasters:
        if not isinstance(item, dict):
            raise ValueError("malformed peer raster entry")
        pid = item.get("id")
        repo = item.get("repo")
        ref = item.get("ref")
        rel = item.get("path")
        digest = item.get("sha256")
        size = item.get("bytes")
        rep_score = item.get("user_reported_score")
        score_ok = rep_score is None or (
            type(rep_score) in (int, float) and math.isfinite(rep_score) and 0.0 <= rep_score <= 1.0
        )
        if (not isinstance(pid, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", pid) or pid in seen_ids
                or repo not in repo_commits or ref != repo_commits[repo]
                or not _safe_rel(rel) or not rel.endswith(".tif")
                or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)
                or digest in seen_hashes or type(size) is not int or size <= 0
                or not score_ok):
            raise ValueError(f"invalid peer raster pin: {item!r}")
        seen_ids.add(pid)
        seen_hashes.add(digest)
    lb = raw.get("user_reported_leaderboard_context")
    if not isinstance(lb, list) or not lb:
        raise ValueError("peer pins must record user_reported_leaderboard_context")
    for entry in lb:
        sc = entry.get("user_reported_score") if isinstance(entry, dict) else None
        if (not isinstance(entry, dict)
                or entry.get("evidence_class") != "USER-REPORTED / UNVERIFIED"
                or entry.get("artifact_available") is not False
                or type(sc) not in (int, float) or not math.isfinite(sc) or not (0.0 <= sc <= 1.0)):
            raise ValueError(f"invalid leaderboard context entry: {entry!r}")
    return raw


def fetch_peer_rasters(pins: dict, peer_cache: Path) -> None:
    peer_cache.mkdir(parents=True, exist_ok=True)
    for item in pins["rasters"]:
        target = peer_cache / f"{item['id']}.tif"
        if target.is_file() and target.stat().st_size == item["bytes"] and sha256(target) == item["sha256"]:
            continue
        endpoint = f"repos/{item['repo']}/contents/{quote(item['path'], safe='/')}?ref={item['ref']}"
        fd, tmp_name = tempfile.mkstemp(prefix="." + target.name + ".", suffix=".part", dir=peer_cache)
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "wb") as fh:
                subprocess.run(
                    ["gh", "api", "-H", "Accept: application/vnd.github.raw", endpoint],
                    check=True, stdout=fh, timeout=300,
                )
            verify_file(tmp, item)
            os.chmod(tmp, 0o644)
            tmp.replace(target)
        finally:
            tmp.unlink(missing_ok=True)


def inspect_candidate(
    tif_path: Path,
    template_path: Path,
    template_sha: str,
    footprint: np.ndarray,
    lattice_near: np.ndarray,
    focus_nears: dict[str, np.ndarray],
) -> dict:
    fmt = diagnose(tif_path, template_path, template_sha)
    with rasterio.open(tif_path) as ds:
        arr = ds.read(1)
        valid_mask = ds.read_masks(1) != 0
    pos_in = footprint & valid_mask & np.isfinite(arr) & (arr > 0)
    pos_out = (~footprint) & valid_mask & np.isfinite(arr) & (arr > 0)
    n_in = int(pos_in.sum())
    n_out = int(pos_out.sum())
    in_vals = arr[footprint]
    is_binary_inside = bool(
        valid_mask[footprint].all() and np.isfinite(in_vals).all() and np.isin(in_vals, (0.0, 1.0)).all()
    )
    lat_hits = int(np.count_nonzero(pos_in & lattice_near))
    lat_frac = float(lat_hits / n_in) if n_in > 0 else None
    worst_site = None
    worst_site_frac = -1.0
    for site_id, near_mask in sorted(focus_nears.items()):
        hits = int(np.count_nonzero(pos_in & near_mask))
        frac = float(hits / n_in) if n_in > 0 else 0.0
        if frac > worst_site_frac:
            worst_site_frac = frac
            worst_site = site_id
    diag = fmt["diagnostics"]
    return {
        "bytes": tif_path.stat().st_size,
        "sha256": fmt["candidate_sha256"],
        "is_binary_inside": is_binary_inside,
        "positive_pixels_in_footprint": n_in,
        "outside_unmasked_positive_pixels": fmt["checks"]["outside_unmasked_positive_count"],
        "outside_any_positive_pixels": n_out,
        "grid_and_inside_pass": diag["grid_and_inside_pass"],
        "nan_outside_variant_pass": diag["nan_outside_variant_pass"],
        "strict_whole_array_variant_pass": diag["strict_whole_array_variant_pass"],
        "outside_encoding_accepted": diag["outside_encoding_accepted"],
        "lattice_dots_within_3px": lat_hits,
        "lattice_directed_overlap_3px": lat_frac,
        "literal_lattice_duplicate": bool(lat_frac is not None and lat_hits * 10 > n_in * 7),
        "worst_focus_site_3px": worst_site if n_in > 0 else None,
        "worst_focus_site_overlap_3px": worst_site_frac if n_in > 0 else None,
        "ok_to_submit": False,
    }


def tracked_tiff_inventory(local_rows: list[dict]) -> dict:
    """Reconcile every Git-tracked TIFF path with current or quarantined audits."""
    listed = subprocess.run(
        ["git", "ls-files", "--", "*.tif", "*.tiff"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    ).stdout.splitlines()
    paths = sorted(set(listed))
    if not paths:
        raise ValueError("Git reports no tracked TIFF paths")

    current_by_path = {row["file"]: row["sha256"] for row in local_rows}
    current_hashes = set(current_by_path.values())
    archive_path = ROOT / "docs/data/archive-review.json"
    archive_report = json.loads(archive_path.read_text(encoding="utf-8"))
    if archive_report.get("schema") != "karage1-quarantined-archive-audit-v1" or archive_report.get("submission_authorized") is not False:
        raise ValueError("quarantined archive audit is missing or not fail-closed")
    archived_hashes: set[str] = set()
    verified_archive_assets = []
    for asset in archive_report.get("assets", {}).values():
        diag = asset.get("format_diagnostic", {})
        rel = diag.get("candidate")
        digest = asset.get("sha256")
        if not _safe_rel(rel) or not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("malformed quarantined archive asset reference")
        tif_path = ROOT / rel
        if not tif_path.is_file() or sha256(tif_path) != digest or diag.get("candidate_sha256") != digest:
            raise ValueError(f"quarantined archive asset hash mismatch: {rel}")
        archived_hashes.add(digest)
        verified_archive_assets.append({"file": rel, "sha256": digest})

    rows = []
    unique_hashes = set()
    for rel in paths:
        if not _safe_rel(rel):
            raise ValueError(f"unsafe tracked TIFF path: {rel}")
        p = ROOT / rel
        if not p.is_file():
            raise ValueError(f"tracked TIFF missing from workspace: {rel}")
        digest = sha256(p)
        unique_hashes.add(digest)
        if rel in current_by_path:
            if current_by_path[rel] != digest:
                raise ValueError(f"current audit hash mismatch: {rel}")
            coverage = "current-download-audit"
        elif digest in current_hashes:
            coverage = "same-bytes-as-current-download-audit"
        elif digest in archived_hashes:
            coverage = "verified-quarantined-archive-audit"
        else:
            coverage = "UNACCOUNTED"
        rows.append({"file": rel, "sha256": digest, "audit_coverage": coverage})
    unaccounted = [r["file"] for r in rows if r["audit_coverage"] == "UNACCOUNTED"]
    archive_bytes = sha256(archive_path)
    return {
        "tracked_tiff_paths_count": len(paths),
        "unique_tracked_tiff_sha256_count": len(unique_hashes),
        "tracked_download_directory_paths_count": sum(p.startswith("docs/downloads/") for p in paths),
        "tracked_quarantined_archive_paths_count": sum(p.startswith("archive/") for p in paths),
        "quarantined_archive_audit": {
            "file": "docs/data/archive-review.json",
            "sha256": archive_bytes,
            "schema": archive_report["schema"],
            "submission_authorized": False,
            "verified_asset_count": len(verified_archive_assets),
            "verified_assets": verified_archive_assets,
        },
        "all_tracked_tiff_bytes_accounted": not unaccounted,
        "unaccounted_paths": unaccounted,
        "tracked_tiffs": rows,
    }


def run_audit(
    ref_manifest_path: Path,
    ref_cache: Path,
    peer_pins_path: Path,
    peer_cache: Path,
    downloads_dir: Path,
) -> dict:
    ref_entries = load_manifest(ref_manifest_path)
    for entry in ref_entries:
        verify_file(ref_cache / f"{entry['id']}.tif", entry)
    ref_index = {x["id"]: x for x in ref_entries}
    template_path = ref_cache / "template.tif"
    template_sha = ref_index["template"]["sha256"]

    with rasterio.open(template_path) as ts:
        tdata = ts.read(1, masked=True)
        footprint = ~np.ma.getmaskarray(tdata) & np.isfinite(tdata.data)
    if not footprint.any() or footprint.all():
        raise ValueError("reference template footprint invalid")

    struct3 = disk(3)
    with rasterio.open(ref_cache / "lattice.tif") as ls:
        lat_arr = ls.read(1)
        lattice_mask = footprint & np.isfinite(lat_arr) & (lat_arr > 0)
    lattice_near = binary_dilation(lattice_mask, structure=struct3)

    focus_nears: dict[str, np.ndarray] = {}
    for entry in ref_entries:
        if entry["id"].startswith("GEMSDOE"):
            with rasterio.open(ref_cache / f"{entry['id']}.tif") as fs:
                farr = fs.read(1)
                fmask = footprint & np.isfinite(farr) & (farr > 0)
            focus_nears[entry["id"]] = binary_dilation(fmask, structure=struct3)

    local_tifs = sorted(downloads_dir.glob("*.tif"))
    if not local_tifs:
        raise ValueError(f"no .tif files found in {downloads_dir}")
    local_rows = []
    for tif in local_tifs:
        info = inspect_candidate(tif, template_path, template_sha, footprint, lattice_near, focus_nears)
        local_rows.append({"file": f"docs/downloads/{tif.name}", **info})

    pins = load_peer_pins(peer_pins_path)
    peer_rows = []
    for item in pins["rasters"]:
        ptif = peer_cache / f"{item['id']}.tif"
        verify_file(ptif, item)
        info = inspect_candidate(ptif, template_path, template_sha, footprint, lattice_near, focus_nears)
        peer_rows.append({
            "id": item["id"],
            "repo": item["repo"],
            "ref": item["ref"],
            "path": item["path"],
            "user_reported_score": item.get("user_reported_score"),
            "score_evidence_class": "USER-REPORTED / UNVERIFIED" if item.get("user_reported_score") is not None else "NO_SCORE_REPORTED",
            **info,
        })

    tracked_inventory = tracked_tiff_inventory(local_rows)
    return {
        "schema": "karage1-local-and-peer-audit-v1",
        "scope": (f"All {len(local_rows)} local docs/downloads/*.tif files present at audit time, "
                  f"plus {len(peer_rows)} SHA-pinned sibling/peer GeoTIFFs across "
                  f"{len(pins['immutable_repos'])} commit-pinned ecosystem repositories; "
                  f"all {tracked_inventory['tracked_tiff_paths_count']} Git-tracked TIFF paths also "
                  "reconciled by exact SHA-256 against the current or quarantined-archive audits."),
        "source_authentication": "GitHub mirror pins verified by full SHA-256; NOT authenticated organizer files or a complete competition registry.",
        "template_sha256": template_sha,
        "lattice_sha256": ref_index["lattice"]["sha256"],
        "footprint_pixels": int(footprint.sum()),
        "outside_pixels": int((~footprint).sum()),
        "user_reported_leaderboard_context": pins["user_reported_leaderboard_context"],
        "immutable_ecosystem_repos": pins["immutable_repos"],
        "local_downloads_count": len(local_rows),
        "all_local_downloads_blocked": all((not r["ok_to_submit"]) and r["literal_lattice_duplicate"] for r in local_rows),
        "local_downloads": local_rows,
        "tracked_tiff_inventory": tracked_inventory,
        "peer_rasters_count": len(peer_rows),
        "all_audited_peer_rasters_exceed_70pct_lattice": all(r["literal_lattice_duplicate"] for r in peer_rows),
        "peer_rasters": peer_rows,
        "submit_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref-manifest", type=Path, default=ROOT / "registry/reference_assets.json")
    ap.add_argument("--ref-cache", type=Path, default=ROOT / ".cache/references")
    ap.add_argument("--peer-pins", type=Path, default=ROOT / "registry/peer_ecosystem_pins.json")
    ap.add_argument("--peer-cache", type=Path, default=ROOT / ".cache/peer_audit")
    ap.add_argument("--downloads-dir", type=Path, default=ROOT / "docs/downloads")
    ap.add_argument("--fetch-peers", action="store_true", help="Fetch missing pinned peer GeoTIFFs via gh api")
    dated_default = ROOT / f"evidence/local_downloads_and_peer_audit_{datetime.now(timezone.utc):%Y%m%d}.json"
    ap.add_argument("--out", type=Path, default=dated_default)
    args = ap.parse_args(argv)
    try:
        if args.out.suffix.lower() in (".tif", ".tiff"):
            raise ValueError("audit output must be a JSON path, never a GeoTIFF")
        protected = [args.ref_manifest, args.peer_pins, *args.downloads_dir.glob("*.tif")]
        for src in protected:
            if args.out.resolve() == src.resolve() or (
                args.out.exists() and src.exists() and os.path.samefile(args.out, src)
            ):
                raise ValueError("audit output must not overwrite input manifest or GeoTIFF")
        pins = load_peer_pins(args.peer_pins)
        if args.fetch_peers:
            fetch_peer_rasters(pins, args.peer_cache)
        report = run_audit(args.ref_manifest, args.ref_cache, args.peer_pins, args.peer_cache, args.downloads_dir)
        text = json.dumps(report, indent=2, allow_nan=False) + "\n"
        args.out.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix="." + args.out.name + ".", suffix=".tmp", dir=args.out.parent)
        tmp = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
            os.chmod(tmp, 0o644)
            tmp.replace(args.out)
        finally:
            tmp.unlink(missing_ok=True)
        print(f"Wrote {args.out} ({report['local_downloads_count']} local + {report['peer_rasters_count']} peer rasters). submit_authorized=False")
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"LOCAL/PEER AUDIT BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
