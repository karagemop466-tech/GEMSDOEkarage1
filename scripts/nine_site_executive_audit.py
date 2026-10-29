#!/usr/bin/env python3
"""Nine-site executive audit: pinned bytes, dot counts, lattice overlap and cross-site uniqueness.

Inputs
------
* ``registry/user_reported_nine_sites_20261029.json`` -- the user's listed files and
  scores (USER-REPORTED / UNVERIFIED), with the registry id where bytes are pinned.
* ``registry/data_manifest.json`` -- SHA-256 pins for every ``reg_*`` raster.
* ``.cache/gems_data/registry/*.tif`` -- restored by ``scripts/restore_data.py --group registry``.

Output
------
``evidence/nine_site_executive_20261029.json``.  Every overlap is directional and uses the
shared template definition (``gems57.uniqueness.dot_overlap``: fraction of ``mine``'s dots within
3 px of ``theirs``' dots).  Nothing here is an organizer score or a leaderboard estimate.
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
from gems57 import uniqueness as UQ  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"
OUT = ROOT / "evidence" / "nine_site_executive_20261029.json"
LATTICE_ID = "lattice"
OVERLAP_LIMIT = 0.70


def _load_manifest() -> dict[str, dict]:
    m = json.loads((ROOT / "registry" / "data_manifest.json").read_text())
    return {f["id"]: f for f in m["files"]}


def _sha256(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    user = json.loads((ROOT / "registry" / "user_reported_nine_sites_20261029.json").read_text())
    manifest = _load_manifest()
    # Flatten the listed files; each pinned file is audited once even if listed twice.
    listed = []
    for site in user["sites"]:
        for f in site["files"]:
            listed.append(dict(site=site["site"], label=f["label"],
                               user_reported_score=f["user_reported_score"],
                               registry_id=f["registry_id"]))
    pinned_ids = sorted({r["registry_id"] for r in listed if r["registry_id"]})
    if LATTICE_ID not in pinned_ids:
        pinned_ids.append("reg_lattice_s5_calibration")  # 13GEMSDOE calibration probe (covering grid)
    raster = {}
    for rid in pinned_ids:
        entry = manifest[rid]
        path = ROOT / ".cache" / "gems_data" / entry["dest"]
        if not path.is_file():
            raise FileNotFoundError(f"restore the registry group first: {path}")
        if _sha256(path) != entry["sha256"]:
            raise ValueError(f"pinned SHA-256 drift for {rid}")
        with rasterio.open(path) as s:
            a = s.read(1)
        raster[rid] = dict(path=path, arr=a, entry=entry, dots=int(UQ._dots(a).sum()))

    focus_ids = [r for r in pinned_ids if r != "reg_lattice_s5_calibration"]
    site_of = {}
    for r in listed:
        if r["registry_id"]:
            site_of[r["registry_id"]] = r["site"]

    fwd: dict[str, dict[str, float]] = {}
    for i in focus_ids + ["reg_lattice_s5_calibration"]:
        fwd[i] = {}
        for j in focus_ids + ["reg_lattice_s5_calibration"]:
            if i == j:
                continue
            fwd[i][j] = UQ.dot_overlap(raster[i]["arr"], raster[j]["arr"])

    rows = []
    for r in listed:
        rid = r["registry_id"]
        row = dict(site=r["site"], label=r["label"], user_reported_score=r["user_reported_score"],
                   user_reported_label="USER-REPORTED / UNVERIFIED",
                   estimated_leaderboard_score="UNAVAILABLE",
                   registry_id=rid)
        if rid is None:
            row.update(pinned=False, unique_vs_other_focus_sites=None,
                       note="No pinned bytes in this checkout; not audited here.")
        else:
            e = raster[rid]["entry"]
            cross = {j: v for j, v in fwd[rid].items()
                     if j in focus_ids and site_of.get(j) != r["site"]}
            worst_cross_id = max(cross, key=cross.get) if cross else None
            same_site = {j: v for j, v in fwd[rid].items()
                         if j in focus_ids and site_of.get(j) == r["site"]}
            url = None
            if e.get("repo") and e.get("ref") and e.get("path"):
                url = f"https://github.com/{e['repo']}/blob/{e['ref']}/{e['path']}"
            row.update(
                pinned=True,
                download_url=url,
                pinned_file=e["dest"],
                pinned_sha256=e["sha256"],
                pinned_bytes=e["bytes"],
                dots=raster[rid]["dots"],
                lattice_forward_3px_overlap=fwd[rid]["reg_lattice_s5_calibration"],
                worst_cross_site_forward_3px_overlap=cross[worst_cross_id] if cross else None,
                worst_cross_site_file=worst_cross_id,
                max_same_site_other_file_overlap=max(same_site.values()) if same_site else None,
                unique_vs_other_focus_sites=bool(cross and cross[worst_cross_id] <= OVERLAP_LIMIT),
                lattice_literal_stop=bool(fwd[rid]["reg_lattice_s5_calibration"] > OVERLAP_LIMIT),
            )
        rows.append(row)

    best = {}
    for row in rows:
        if row["site"] not in best or row["user_reported_score"] > best[row["site"]]["user_reported_score"]:
            best[row["site"]] = row
    summary = dict(
        best_pinned_or_listed_by_site={
            site: dict(label=b["label"], user_reported_score=b["user_reported_score"],
                       registry_id=b["registry_id"], pinned=b["pinned"],
                       unique_vs_other_focus_sites=b.get("unique_vs_other_focus_sites"))
            for site, b in sorted(best.items())
        },
        overall_best_user_reported=max(rows, key=lambda x: x["user_reported_score"])["label"],
        organizer_confirmed_scores=0,
        submit_authorized=False,
    )
    out = dict(
        schema="karage1-nine-site-executive-v1",
        created_utc=datetime.now(timezone.utc).isoformat(),
        overlap_definition="directional: fraction of row file's dots within 3 px of column file's dots (gems57.uniqueness.dot_overlap)",
        overlap_limit=OVERLAP_LIMIT,
        scope_limitation=("Only the pinned registry files are compared. The wider set of listed "
                          "GEMSDOE submissions is not pinned in this checkout, so 'unique' here means "
                          "'unique versus the pinned focus-site rasters and the lattice'."),
        rows=rows,
        summary=summary,
        pairwise_forward_3px=fwd,
        dots={k: v["dots"] for k, v in raster.items()},
    )
    OUT.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(rows)} listed rows, {len(pinned_ids)} pinned rasters")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
