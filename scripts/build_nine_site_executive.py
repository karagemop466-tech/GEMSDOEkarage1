#!/usr/bin/env python3
"""Nine-site executive table for the GEMSDOEkarage1 submission site.

For each of the nine owner-reported focus sites (GEMSDOE24/25/27/28/30/31/32/33/36)
this script reads the committed registry raster, measures its dot geometry against
the catalogue and against every other focus site, and records the owner-reported
score with an explicit evidence label.  It writes a machine-readable table that the
site generator consumes.

Evidence labels (never interchangeable):
  * ``USER-REPORTED`` -- a leaderboard value supplied by the owner in the standing
    brief.  No organizer submission receipt tied to the raster SHA-256 exists in
    this repository, so it is NOT an organizer-confirmed score.
  * ``MEASURED``      -- geometry computed here from the restored raster bytes.

No leaderboard estimate is produced: the hidden test labels are not available, so
no defensible projection exists.  See ``knowledge/02_why_gemsdoe32_b2_scored_0.2778.md``.
"""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemskarage1.paths import DOCS_DATA_DIR  # noqa: E402

REGISTRY = ROOT / "registry"
DATA = ROOT / ".cache" / "gems_data"

SITES = (
    "GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28",
    "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36",
)

# Owner-reported leaderboard values from the standing brief (README focus-site table).
USER_REPORTED = {
    "GEMSDOE24": 0.2477,
    "GEMSDOE25": 0.2600,
    "GEMSDOE27": 0.2449,
    "GEMSDOE28": 0.2710,
    "GEMSDOE30": 0.2600,
    "GEMSDOE31": 0.2708,
    "GEMSDOE32": 0.2778,
    "GEMSDOE33": 0.2632,
    "GEMSDOE36": 0.2750,
}

# Preferred raster per site (the owner-reported submission for that site).
PREFERRED = {
    "GEMSDOE24": "GEMSDOE24_gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "GEMSDOE25": "GEMSDOE25_d28.tif",
    "GEMSDOE27": "GEMSDOE27_gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "GEMSDOE28": "GEMSDOE28_gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif",
    "GEMSDOE30": "GEMSDOE30_gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif",
    "GEMSDOE31": "GEMSDOE31_gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif",
    "GEMSDOE32": "GEMSDOE32_B2.tif",
    "GEMSDOE33": "GEMSDOE33_GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
    "GEMSDOE36": "GEMSDOE36_gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif",
}

# The dense 13GEMSDOE lattice calibration probe.  It is a *covering* raster (one dot
# within 3 px of ~99.9 % of the footprint), so the literal forward-overlap gate is
# mathematically unsatisfiable against it.  It is measured and published as a
# diagnostic only; it never decides uniqueness on its own (registry/registry_roles.json).
LATTICE = "13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(path: Path):
    with rasterio.open(path) as src:
        a = src.read(1).astype(np.float64)
        return a, src.profile


def halo(dots: np.ndarray, r: int = 3) -> np.ndarray:
    yy, xx = np.ogrid[-r:r + 1, -r:r + 1]
    struct = (yy * yy + xx * xx) <= r * r
    return ndimage.binary_dilation(dots, structure=struct)


def main() -> int:
    with rasterio.open(DATA / "sample_submission.tif") as src:
        foot = np.isfinite(src.read(1))
    with rasterio.open(DATA / "labels.tif") as src:
        catalogue = src.read(1) > 0

    paths = {site: REGISTRY / PREFERRED[site] for site in SITES}
    missing = [s for s, p in paths.items() if not p.is_file()]
    if missing:
        raise SystemExit(f"missing registry rasters: {missing}")

    grids = {s: load(p)[0] for s, p in paths.items()}

    # ---- per-site geometry ----
    per_site = {}
    for site in SITES:
        a = grids[site]
        dots = (np.isfinite(a) & (a > 0) & foot)
        cat_dist = ndimage.distance_transform_edt(~catalogue)
        d3 = cat_dist <= 3
        d2 = cat_dist <= 2
        d1 = cat_dist <= 1
        per_site[site] = {
            "file": paths[site].name,
            "path": str(paths[site].relative_to(ROOT)),
            "sha256": sha256_file(paths[site]),
            "dots": int(dots.sum()),
            "positive_values": sorted({float(v) for v in a[dots].tolist()})[:8],
            "on_catalogue": int((dots & catalogue).sum()),
            "within_1px_of_catalogue": int((dots & d1).sum()),
            "within_2px_of_catalogue": int((dots & d2).sum()),
            "within_3px_of_catalogue": int((dots & d3).sum()),
            "user_reported_score": USER_REPORTED[site],
            "score_label": "USER-REPORTED / UNVERIFIED",
        }

    # ---- pairwise like-for-like duplicate test (dotted vs dotted) ----
    dot_masks = {s: (np.isfinite(grids[s]) & (grids[s] > 0) & foot) for s in SITES}
    pairwise = {}
    for a_site in SITES:
        for b_site in SITES:
            if a_site >= b_site:
                continue
            A, B = dot_masks[a_site], dot_masks[b_site]
            nA, nB = int(A.sum()), int(B.sum())
            fwd = float((A & halo(B)).sum() / nA) if nA else 0.0
            rev = float((B & halo(A)).sum() / nB) if nB else 0.0
            inter = int((A & B).sum())
            union = int((A | B).sum())
            jac = inter / union if union else 0.0
            # Spearman on the common footprint (monotone rank correlation)
            both = foot & np.isfinite(grids[a_site]) & np.isfinite(grids[b_site])
            x = grids[a_site][both]
            y = grids[b_site][both]
            # rank via stable argsort (deterministic, no scipy rank dependency)
            def rank(v):
                order = np.argsort(v, kind="mergesort")
                r = np.empty_like(order, dtype=np.float64)
                r[order] = np.arange(len(v), dtype=np.float64)
                return r
            rx, ry = rank(x), rank(y)
            rxy = float(np.corrcoef(rx, ry)[0, 1]) if len(x) > 1 else 0.0
            pairwise[f"{a_site}|{b_site}"] = {
                "forward_overlap_a_in_b": round(fwd, 6),
                "reverse_overlap_b_in_a": round(rev, 6),
                "jaccard": round(jac, 6),
                "shared_dots": inter,
                "spearman": round(rxy, 6),
                "literal_70pct_gate_fails": bool(fwd > 0.70 or rev > 0.70),
            }

    # ---- lattice diagnostic ----
    lat_path = DATA / LATTICE
    lattice = None
    if lat_path.is_file():
        lat_arr = load(lat_path)[0]
        lattice = (np.isfinite(lat_arr) & (lat_arr > 0) & foot)
    lattice_diag = {}
    if lattice is not None:
        for site in SITES:
            dots = dot_masks[site]
            lattice_diag[site] = round(float((dots & halo(lattice)).sum() / max(int(dots.sum()), 1)), 6)

    def cand_overlap(site: str, other: str) -> float:
        """Fraction of ``site``'s dots within 3 px of ``other``'s dots."""
        key = f"{min(site, other)}|{max(site, other)}"
        pw = pairwise[key]
        if site < other:
            return pw["forward_overlap_a_in_b"]
        return pw["reverse_overlap_b_in_a"]

    # ---- best submission per site + unique verdict ----
    best = max(SITES, key=lambda s: USER_REPORTED[s])
    for site in SITES:
        others = [o for o in SITES if o != site]
        worst = max(others, key=lambda o: cand_overlap(site, o))
        fwd = cand_overlap(site, worst)
        per_site[site]["worst_peer"] = worst
        per_site[site]["worst_forward_overlap"] = fwd
        per_site[site]["unique_vs_other_eight"] = bool(fwd <= 0.70)
        per_site[site]["literal_70pct_gate_fails_vs_peer"] = bool(fwd > 0.70)

    out = {
        "schema": "karage1-nine-site-executive-v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "grid": {"shape": [int(foot.shape[0]), int(foot.shape[1])],
                 "footprint_px": int(foot.sum()), "catalogue_px": int(catalogue.sum())},
        "best_reported_site": best,
        "evidence_policy": {
            "USER-REPORTED": "owner-supplied leaderboard value; no organizer receipt in this repo",
            "MEASURED": "geometry computed from restored raster bytes in this run",
            "note": "No leaderboard estimate is produced; hidden test labels are unavailable.",
        },
        "sites": per_site,
        "pairwise": pairwise,
        "lattice_forward_overlap_diagnostic": lattice_diag,
    }
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DOCS_DATA_DIR / "nine_site_executive_20261031.json"
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"best_reported_site": best,
                      "out": str(out_path.relative_to(ROOT)),
                      "lattice_diag": lattice_diag}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
