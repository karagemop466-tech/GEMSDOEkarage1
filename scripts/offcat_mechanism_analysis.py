#!/usr/bin/env python3
"""Off-catalogue mechanism audit for the nine focus-site rasters (session arena/510af7c7).

Pure measurement on the committed registry rasters and the restored training
catalogue. It does NOT generate predictions, run a holdout, or authorize a
submission. Every score it touches is USER-REPORTED (copied from the request
text) and is labelled as such in the output.

Reads:
  registry/GEMSDOE*.tif                         local copies of focus-site rasters
  <GEMS_DATA_DIR>/existing_faults.tif           INGENIOUS/USGS catalogue (binary 1 = fault)
  <GEMS_DATA_DIR>/sample_submission.tif         grid + footprint (finite = scored area)

Writes:
  evidence/offcat_mechanism_510af7c7_20261031.json

Usage:
  GEMS_DATA_DIR=$PWD/data .venv/bin/python scripts/offcat_mechanism_analysis.py
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
DATA = Path(os.environ.get("GEMS_DATA_DIR", ROOT / "data"))
OUT = ROOT / "evidence" / "offcat_mechanism_510af7c7_20261031.json"

# USER-REPORTED values, copied from the request text for the registry file named.
USER_REPORTED = {
    "GEMSDOE24": ("gems24-h25-1-dotted-h19-5-d1-5", 0.2477),
    "GEMSDOE25": ("GEMSDOE25_d28", 0.2600),
    "GEMSDOE27": ("gems27-topo-gap-closure-t-v2-on-d1-5", 0.2449),
    "GEMSDOE28": ("gems28-h36-1-rung30-blind-r1", 0.2710),
    "GEMSDOE30": ("gemsdoe30-d28-poisson300m-offcat-44090", 0.2600),
    "GEMSDOE31": ("gemsdoe31-h27-4-solo-d28", 0.2708),
    "GEMSDOE32": ("GEMSDOE32_B2", 0.2778),
    "GEMSDOE33": ("GEMSDOE33-h33d-analog-tip-stepover-r30", 0.2632),
    "GEMSDOE36": ("gemsdoe36-anderson-geothermal-pinn-38854", 0.2750),
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    with rasterio.open(DATA / "sample_submission.tif") as s:
        foot = np.isfinite(s.read(1))
        grid = dict(crs=str(s.crs), shape=list(s.shape), transform=list(s.transform)[:6])
    with rasterio.open(DATA / "existing_faults.tif") as s:
        cat = s.read(1) == 1
    dist_cat = distance_transform_edt(~cat)  # px to nearest catalogue cell

    rasters: dict[str, dict] = {}
    dots: dict[str, np.ndarray] = {}
    for key, (stem, score) in USER_REPORTED.items():
        matches = sorted((ROOT / "registry").glob(f"{key}*.tif"))
        if len(matches) != 1:
            raise SystemExit(f"expected exactly one registry raster for {key}, found {len(matches)}")
        path = matches[0]
        with rasterio.open(path) as s:
            arr = s.read(1)
        d = (arr > 0) & foot
        dots[key] = d
        n = int(d.sum())
        rasters[key] = dict(
            file=str(path.relative_to(ROOT)),
            sha256=sha256(path),
            dots_in_footprint=n,
            pct_within_2px_of_catalogue=round(100 * float((dist_cat[d] <= 2).mean()), 4),
            pct_within_3px_of_catalogue=round(100 * float((dist_cat[d] <= 3).mean()), 4),
            median_dist_to_catalogue_px=float(np.median(dist_cat[d])),
            user_reported_score=score,
            user_reported_score_label="USER-REPORTED / UNVERIFIED",
            registry_stem=stem,
        )

    rho, p = spearmanr([rasters[k]["user_reported_score"] for k in USER_REPORTED],
                       [-rasters[k]["pct_within_3px_of_catalogue"] for k in USER_REPORTED])

    # Exact dot-set relations (values > 0 within footprint).
    b2, p25, p30 = dots["GEMSDOE32"], dots["GEMSDOE25"], dots["GEMSDOE30"]
    removed = p25 & ~b2
    jac_25_30 = float((p25 & p30).sum() / (p25 | p30).sum())
    keys = list(USER_REPORTED)
    jac = {a: {} for a in keys}
    for a in keys:
        for b in keys:
            if a != b:
                jac[a][b] = round(float((dots[a] & dots[b]).sum() / (dots[a] | dots[b]).sum()), 4)
    max_partner = {a: max(jac[a], key=jac[a].get) for a in keys}
    for a in keys:
        rasters[a]["max_jaccard_to_other_focus_site"] = jac[a][max_partner[a]]
        rasters[a]["max_jaccard_partner"] = max_partner[a]

    # Protocol-style 3-px overlap: share of dots of A within 3 px of any dot of B.
    dist_dots = {a: distance_transform_edt(~dots[a]) for a in keys}
    overlap3 = {a: {b: round(100 * float((dist_dots[b][dots[a]] <= 3).mean()), 2)
                    for b in keys if b != a} for a in keys}
    # Random-placement baseline for the same test (200 draws, matched counts, vs GEMSDOE25 dots).
    foot_idx = np.flatnonzero(foot.ravel())
    null = {}
    for n in sorted({int(dots["GEMSDOE25"].sum()), int(dots["GEMSDOE32"].sum())}):
        vals = []
        for seed in range(200):
            pick = np.random.default_rng(seed).choice(foot_idx, size=n, replace=False)
            vals.append(float((dist_dots["GEMSDOE25"].ravel()[pick] <= 3).mean()))
        null[str(n)] = dict(draws=200, mean_pct=round(100 * float(np.mean(vals)), 2),
                            min_pct=round(100 * float(np.min(vals)), 2), max_pct=round(100 * float(np.max(vals)), 2))

    report = dict(
        schema="karage1-offcat-mechanism-v1",
        protocol_3px_overlap_pct_A_to_B=overlap3,
        protocol_3px_random_null_vs_gemsdoe25=null,
        protocol_gate_note="Literal 70%/3-px gate (internal protocol, not an official rule). Random null vs focus-site dots is ~17%; observed 100% is real co-location. The gate saturates only against the dense 13GEMS lattice.",
        jaccard_dot_sets=jac,
        session="arena/510af7c7-gemsdoekarage1",
        date_utc="2026-10-31",
        scope="Measurement only. No prediction, holdout, or submission. Scores are USER-REPORTED.",
        grid=grid,
        footprint_pixels=int(foot.sum()),
        catalogue_pixels_in_footprint=int((cat & foot).sum()),
        rasters=rasters,
        spearman_score_vs_neg_offcat_pct=dict(rho=round(float(rho), 4), p_value=float(p), n=len(USER_REPORTED),
                                              label="ASSOCIATION across 9 USER-REPORTED scores; not causal"),
        b2_is_subset_of_gemsdoe25=bool((b2 & ~p25).sum() == 0),
        b2_extra_dots_not_in_gemsdoe25=int((b2 & ~p25).sum()),
        removed_from_gemsdoe25_to_make_b2=int(removed.sum()),
        removed_within_2px_of_catalogue=int((dist_cat[removed] <= 2).sum()),
        removed_median_dist_to_catalogue_px=float(np.median(dist_cat[removed])),
        gemsdoe25_and_gemsdoe30_dot_jaccard=jac_25_30,
        gemsdoe25_and_gemsdoe30_identical_dot_sets=bool(np.array_equal(p25, p30)),
        note_identical_sets="Identical dot sets, possibly different bytes; treat GEMSDOE30 as a duplicate of GEMSDOE25 for uniqueness.",
    )
    OUT.write_text(json.dumps(report, indent=2, sort_keys=True, default=float) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    print(f"spearman={rho:.3f} n=9; B2 subset of 25: {report['b2_is_subset_of_gemsdoe25']}; "
          f"removed={report['removed_from_gemsdoe25_to_make_b2']} "
          f"(within 2px: {report['removed_within_2px_of_catalogue']}); "
          f"25==30: {report['gemsdoe25_and_gemsdoe30_identical_dot_sets']}")


if __name__ == "__main__":
    main()
