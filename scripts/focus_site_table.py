#!/usr/bin/env python3
"""Nine focus-site audit table (GEMSDOE24/25/27/28/30/31/32/33/36) + lattice chance test.

For each site it re-reads the SHA-256-pinned registry raster (restored from github.com,
see data/restore_receipt.json) and records measurable facts only:
  * positive count, value set, outside-footprint encoding, finite/[0,1] checks;
  * catalogue collar profile (dots on / within 1, 2, 3 px of the mapped catalogue);
  * observed 3-px lattice overlap (share of the site's dots within 3 px of a lattice dot)
    AND the chance overlap for uniformly random dots in the same footprint
    (the share of footprint cells covered by the lattice). If observed ~ chance, the
    lattice gate measures lattice coverage, not similarity;
  * pairwise among the nine: identical positive sets, 3-px overlap, |Spearman|.
Scores are the owner-reported values recorded in README.md and labelled OWNER-REPORTED / UNVERIFIED.

Writes evidence/focus_site_table_20261029.json. No holdout number is produced here.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.spatial import cKDTree
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gems57.grid import DATA_DIR, load_grid  # noqa: E402

REG = ROOT / ".cache" / "gems_data" / "registry"
SITES = [
    # site, registry file (verified present, SHA pinned in data/restore_receipt.json),
    # user-reported score (as recorded in README.md focus-site table, OWNER-REPORT)
    ("GEMSDOE24", "GEMSDOE24_h25-1-dotted-h19-5-d1-5_allfinite.tif", 0.2477),
    ("GEMSDOE25", "GEMSDOE25_dotted-h19-5-d2-8_zeros.tif", 0.2600),
    ("GEMSDOE27", "GEMSDOE27_topo-gap-closure-t-v2-on-d1-5_allfinite.tif", 0.2449),
    ("GEMSDOE28", "GEMSDOE28_h36-1-rung30-blind-r1_allfinite.tif", 0.2710),
    ("GEMSDOE30", "GEMSDOE30_d28-poisson300m-offcat-44090.tif", 0.2600),
    ("GEMSDOE31", "GEMSDOE31_h27-4-solo-d28_allfinite.tif", 0.2708),
    ("GEMSDOE32", "GEMSDOE32_h33-h33-2-b2_e5eb6e7e_zeros.tif", 0.2778),
    ("GEMSDOE33", "GEMSDOE33_h33d-analog-tip-stepover-r30.tif", 0.2632),
    ("GEMSDOE36", "GEMSDOE36_anderson-geothermal-pinn-38854_zeros.tif", 0.2750),
]
LATTICE = "13GEMSDOE_r13-lattice-s5_v2_nan-outside.tif"


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def dots_xy(mask: np.ndarray) -> np.ndarray:
    return np.argwhere(mask).astype(np.float64)


def within3_share(a_xy: np.ndarray, b_xy: np.ndarray) -> float:
    if len(a_xy) == 0 or len(b_xy) == 0:
        return 0.0
    d, _ = cKDTree(b_xy).query(a_xy, k=1)
    return float((d <= 3.0).mean())


def main() -> int:
    grid = load_grid(DATA_DIR)
    fp = grid.footprint
    dist = ndi.distance_transform_edt(~grid.catalogue)
    rec = {}
    pos = {}
    values = {}
    for site, fname, score in SITES:
        p = REG / fname
        with rasterio.open(p) as src:
            a = src.read(1).astype(np.float64)
            nodata = src.nodata
        inside = a[fp]
        pm = (a > 0) & fp
        pos[site] = pm
        values[site] = a
        d = dist[pm]
        rec[site] = dict(
            file=f"registry/{fname}", sha256=sha256(p),
            inside_finite=bool(np.isfinite(inside).all()),
            inside_min=float(inside.min()), inside_max=float(inside.max()),
            inside_in_0_1=bool(inside.min() >= 0 and inside.max() <= 1),
            outside_finite_cells=int(np.isfinite(a[~fp]).sum()),
            nodata_tag=(None if nodata is None or nodata != nodata else float(nodata)),
            positives=int(pm.sum()),
            positive_values=sorted({float(x) for x in np.unique(inside[inside > 0])})[:3],
            on_catalogue=int((d == 0).sum()), within_1px=int((d <= 1).sum()),
            within_2px=int((d <= 2).sum()), within_3px=int((d <= 3).sum()),
            user_reported_score=score, user_reported_source="README.md focus-site table (repo record)",
            score_status="OWNER-REPORTED / UNVERIFIED (no organiser receipt tied to this hash)",
        )

    # lattice: observed vs chance
    lat = rasterio.open(REG / LATTICE).read(1).astype(np.float64)
    lat_mask = (lat > 0) & fp
    lat_xy = dots_xy(lat_mask)
    lat_cover = ndi.binary_dilation(lat_mask, structure=_disk(3)) & fp
    chance_all = float(lat_cover[fp].mean())
    for site in pos:
        obs = within3_share(dots_xy(pos[site]), lat_xy)
        rec[site]["lattice_observed_3px_overlap"] = obs
        rec[site]["lattice_chance_3px_overlap_uniform_random"] = chance_all
        rec[site]["lattice_literal_gate_70pct"] = "FAILS" if obs > 0.70 else "passes"

    # pairwise among the nine
    keys = list(pos)
    pair = {}
    for a, b in itertools.combinations(keys, 2):
        same = bool((pos[a] == pos[b]).all())
        ov = within3_share(dots_xy(pos[a]), dots_xy(pos[b]))
        va = values[a][fp].ravel(); vb = values[b][fp].ravel()
        ra = rankdata(va); ra -= ra.mean()
        rb = rankdata(vb); rb -= rb.mean()
        den = np.linalg.norm(ra) * np.linalg.norm(rb)
        rho = float(np.dot(ra, rb) / den) if den > 0 else None
        ov_ba = within3_share(dots_xy(pos[b]), dots_xy(pos[a]))
        pair[f"{a}|{b}"] = dict(identical_positive_sets=same,
                                first_dots_within_3px_of_second=ov,
                                second_dots_within_3px_of_first=ov_ba,
                                spearman_full_footprint=rho)
    dup_groups = [[a, b] for k, v in pair.items() for a, b in [k.split("|")] if v["identical_positive_sets"]]

    # subset / superset checks used in the GEMSDOE32 analysis (pixel-set arithmetic on pinned rasters)
    extra = {}
    with rasterio.open(REG / "GEMSDOE28_h27-4-r1-solo-d2-8_allfinite.tif") as src:
        h27r1_pos = (src.read(1) > 0) & fp
    extra["GEMSDOE28_h27-4-r1 positives equal GEMSDOE31 positives"] = bool((h27r1_pos == pos["GEMSDOE31"]).all())
    extra["GEMSDOE32 positives subset of GEMSDOE30"] = bool((pos["GEMSDOE32"] & ~pos["GEMSDOE30"]).sum() == 0)
    extra["GEMSDOE30 minus GEMSDOE32 (dots)"] = int((pos["GEMSDOE30"] & ~pos["GEMSDOE32"]).sum())
    extra["GEMSDOE32 positives subset of GEMSDOE36"] = bool((pos["GEMSDOE32"] & ~pos["GEMSDOE36"]).sum() == 0)
    extra["GEMSDOE36 minus GEMSDOE32 (dots)"] = int((pos["GEMSDOE36"] & ~pos["GEMSDOE32"]).sum())
    extra["GEMSDOE25 positives equal GEMSDOE30 positives"] = bool((pos["GEMSDOE25"] == pos["GEMSDOE30"]).all())

    out = dict(
        schema="karage1-focus-site-table-v1",
        created_utc="2026-10-29",
        scope="Nine focus sites: the owner-reported raster per site (as recorded in README.md). Other files per site are listed in the request, not audited here.",
        grid=dict(shape=list(grid.shape), footprint_cells=int(fp.sum()), catalogue_cells=int(grid.catalogue.sum())),
        sites=rec,
        lattice=dict(file=f"registry/{LATTICE}", footprint_cover_within_3px=chance_all,
                     note="Chance overlap = share of footprint cells within 3 px of a lattice dot. Uniform random dots in the footprint would score about this value."),
        pairwise=pair,
        identical_positive_set_groups=dup_groups,
        subset_checks=extra,
        software=dict(numpy=np.__version__, rasterio=rasterio.__version__),
    )
    dst = ROOT / "evidence" / "focus_site_table_20261029.json"
    dst.write_text(json.dumps(out, indent=2, allow_nan=False) + "\n")
    for s in keys:
        r = rec[s]
        print(f"{s} dots={r['positives']:6d} c1={r['within_1px']:5d} c2={r['within_2px']:5d} c3={r['within_3px']:5d} "
              f"lattice_obs={r['lattice_observed_3px_overlap']:.4f} chance={chance_all:.4f} score={r['user_reported_score']}")
    print("identical groups:", dup_groups)
    return 0


def _disk(r: int) -> np.ndarray:
    y, x = np.mgrid[-r:r + 1, -r:r + 1]
    return (x * x + y * y) <= r * r


if __name__ == "__main__":
    raise SystemExit(main())
