#!/usr/bin/env python3
"""Pairwise audit of restored focus-site rasters (dots, forward 3-px overlap, Spearman).

Reads only hash-pinned mirror bytes under data/scored (restore with
scripts/restore_karage1_data.py --group scored). Writes evidence JSON. It does
not select, promote, or score any submission.

Definitions (match the repo's Parallel-Run Protocol, Rule 1):
  dots(X)            = footprint pixels with value > 0
  fwd3(A->B)         = fraction of A's dots lying within 3 px (Chebyshev-free, Euclid <= 3) of a B dot
  rho(A,B)           = Spearman over all finite footprint pixels
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SAMPLE = DATA / "sample_submission.tif"
OUT = ROOT / "evidence" / "focus_sites_audit_20261029.json"

# name -> restored file (sha256 pins live in registry/karage1_data_manifest.json)
FILES = {
    "GEMSDOE24_d1-5": "scored/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif",
    "GEMSDOE25_d2-8": "scored/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
    "GEMSDOE27_tgc-v2": "scored/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif",
    "GEMSDOE28_h27-4-r1": "scored/gems28-h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-allfinite.tif",
    "GEMSDOE30_d28-offcat": "scored/focus/GEMSDOE30.tif",
    "GEMSDOE31_h27-4-solo": "scored/focus/GEMSDOE31.tif",
    "GEMSDOE32_B2": "scored/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
    "GEMSDOE33_h33d-analog": "scored/focus/GEMSDOE33.tif",
    "GEMSDOE36_anderson-pinn": "scored/focus/GEMSDOE36.tif",
    "lattice_13GEMSDOE": "scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif",
}
# Pins for the focus/* files (repo, commit, path, sha256) are in registry/reference_assets.json.
LATTICE = "lattice_13GEMSDOE"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_pinned_focus_files() -> None:
    """Fetch GEMSDOE30/31/33/36 from their pinned commits when absent; verify SHA-256 and byte count."""
    sys.path.insert(0, str(ROOT / "scripts"))
    from restore_karage1_data import fetch_blob  # same gh-api pinned fetcher as the restore tool

    refs = {r["id"]: r for r in json.loads((ROOT / "registry/reference_assets.json").read_text())}
    for name in ("GEMSDOE30", "GEMSDOE31", "GEMSDOE33", "GEMSDOE36"):
        target = DATA / "scored" / "focus" / f"{name}.tif"
        ref = refs[name]
        if target.is_file() and target.stat().st_size == ref["bytes"] and sha256(target) == ref["sha256"]:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as fh:
            fetch_blob(ref["repo"], ref["ref"], ref["path"], fh)
        if target.stat().st_size != ref["bytes"] or sha256(target) != ref["sha256"]:
            raise SystemExit(f"pinned focus file {name} failed size/SHA-256 check")


def main() -> int:
    ensure_pinned_focus_files()
    with rasterio.open(SAMPLE) as s:
        foot = np.isfinite(s.read(1))
        grid = (s.shape, str(s.crs), tuple(s.transform)[:6])
    arrays, rows = {}, []
    for name, rel in FILES.items():
        path = DATA / rel
        with rasterio.open(path) as ds:
            if (ds.shape, str(ds.crs), tuple(ds.transform)[:6]) != grid:
                print(f"GRID MISMATCH {name}", file=sys.stderr)
                return 1
            x = ds.read(1).astype(np.float32)
        inside = x[foot]
        if not np.isfinite(inside).all() or np.any((inside < 0) | (inside > 1)):
            print(f"RANGE FAIL {name}", file=sys.stderr)
            return 1
        dots = foot & (x > 0)
        arrays[name] = dots
        rows.append({
            "name": name, "file": rel, "sha256": sha256(path),
            "footprint_px": int(foot.sum()), "positive_inside_footprint": int(dots.sum()),
            "nonfinite_outside_footprint": int((~np.isfinite(x[~foot])).sum()),
            "unique_values_inside_sample": int(np.unique(inside).size),
        })
    # Lattice coverage bound: which footprint cells lie more than 3 px from every lattice dot.
    lat = arrays[LATTICE]
    lat_dist = distance_transform_edt(~lat)
    uncovered = foot & (lat_dist > 3.0)
    n_unc = int(uncovered.sum())
    bound = {
        "lattice_dots": int(lat.sum()),
        "footprint_px": int(foot.sum()),
        "footprint_uncovered_by_lattice_3px": n_unc,
        "footprint_covered_fraction": float(1 - n_unc / foot.sum()),
        "max_dots_that_can_pass_70pct_rule": int(n_unc / 0.30),
        "note": "Dots inside covered cells always overlap; a pass needs >=30% of dots in uncovered cells.",
    }
    for r in rows:
        dd = arrays[r["name"]]
        r["dots_in_lattice_uncovered_cells"] = int((dd & uncovered).sum())
    pairs = []
    names = list(FILES)
    for a in names:
        for b in names:
            if a == b:
                continue
            da, db = arrays[a], arrays[b]
            dist_b = distance_transform_edt(~db)
            n = int(da.sum())
            fwd = float((dist_b[da] <= 3.0).sum() / n) if n else None
            pairs.append({"A": a, "B": b, "fwd3_A_within_3px_of_B": fwd})
    # Spearman over full footprint (surface), computed once per name pair of interest
    rho = {}
    base = {n: np.asarray(np.array(rasterio.open(DATA / FILES[n]).read(1)[foot], dtype=np.float32)) for n in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            rho[f"{a}|{b}"] = float(spearmanr(base[a], base[b]).statistic)
    # Byte-different files with identical positive masks (packed-bit SHA-256).
    mask_key: dict[str, list[str]] = {}
    for name, m in arrays.items():
        if name.startswith("lattice"):
            continue
        mask_key.setdefault(hashlib.sha256(np.packbits(m).tobytes()).hexdigest()[:12], []).append(name)
    identical = [v for v in mask_key.values() if len(v) > 1]
    # User-reported scores (leaderboard post in the session prompt; UNVERIFIED) vs dot count.
    reported = {"GEMSDOE32_B2": 0.2778, "GEMSDOE36_anderson-pinn": 0.2750, "GEMSDOE28_h27-4-r1": 0.2708,
                "GEMSDOE33_h33d-analog": 0.2632, "GEMSDOE25_d2-8": 0.2600, "GEMSDOE24_d1-5": 0.2477,
                "GEMSDOE27_tgc-v2": 0.2449}
    from scipy import stats
    xs = np.array([int(arrays[k].sum()) for k in reported], float)
    ys = np.array(list(reported.values()), float)
    pr, sr, lr = stats.pearsonr(xs, ys), stats.spearmanr(xs, ys), stats.linregress(xs, ys)
    trend = {
        "label": "USER-REPORTED / UNVERIFIED (session prompt leaderboard post; no organizer receipt)",
        "distinct_masks_n": len(reported),
        "points": [{"name": k, "dots": int(xs[i]), "user_reported": v} for i, (k, v) in enumerate(reported.items())],
        "pearson_r": round(float(pr.statistic), 4), "pearson_p": float(pr.pvalue),
        "spearman_rho": round(float(sr.statistic), 4), "spearman_p": float(sr.pvalue),
        "slope_score_per_1000_dots": round(float(lr.slope) * 1000, 6),
        "caveat": "Descriptive only. Seven points from one family of thinned masks. Not a score, not a mechanism. No extrapolation licensed.",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({
        "schema": "focus-sites-audit-v1", "date_utc": "2026-10-29",
        "label": "MIRROR-BYTES (third-party pinned); not organizer-authenticated",
        "grid": {"shape": list(grid[0]), "crs": grid[1], "transform": list(grid[2])},
        "rasters": rows, "lattice_coverage_bound": bound, "identical_mask_groups": identical,
        "user_reported_score_vs_dot_count": trend,
        "forward_3px_overlap": pairs, "spearman_footprint": rho,
    }, indent=2) + "\n")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
