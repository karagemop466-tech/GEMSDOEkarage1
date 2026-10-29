#!/usr/bin/env python3
"""Pre-placement check: Spearman rho and 3-px dot overlap of a continuous surface vs. every restored registry raster.

Uses the shared comparison primitives in vendor/gems57/uniqueness.py. Writes evidence/<out>.
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
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
for sub in (".", "src", "vendor"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gemsk import grid  # noqa: E402
from gemskarage1.registry_audit import FOCUS_9_SITES  # noqa: E402  (names only)
from scripts.run_strainphase_experiment import build_strainphase_components, build_signed_offset_components  # noqa: E402

BUDGET = 37654


def read(p: Path) -> np.ndarray:
    with rasterio.open(p) as ds:
        return np.nan_to_num(ds.read(1), nan=0.0).astype(np.float32)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="evidence/surface_registry_overlap_20261029.json")
    ap.add_argument("--sample", type=int, default=400_000)
    args = ap.parse_args()
    foot = grid.footprint()
    registry = sorted((ROOT / "data" / "scored").glob("*.tif"))
    rng = np.random.default_rng(20261029)
    fy, fx = np.nonzero(foot)
    sel = rng.choice(fy.size, size=min(args.sample, fy.size), replace=False)
    sy, sx = fy[sel], fx[sel]
    surfaces = {"strainphase": build_strainphase_components(foot)["strainphase"],
                "signedoffset": build_signed_offset_components(foot)["signedoffset"]}
    rows = []
    for name, surf in surfaces.items():
        s = surf[sy, sx]
        for p in registry:
            a = read(p)
            rho = float(spearmanr(s, a[sy, sx]).statistic)
            rho = 0.0 if not np.isfinite(rho) else rho
            dots_reg = a > 0
            # directed overlap: share of registry dots within 3 px of surface top-N dots
            top = np.zeros(foot.shape, bool)
            thr = np.partition(surf[foot], -BUDGET)[-BUDGET]
            top = (surf >= thr) & foot
            from scipy.ndimage import distance_transform_edt
            d_top = distance_transform_edt(~top)
            reg_n = int(dots_reg.sum())
            overlap_reg_within3 = float(((d_top <= 3) & dots_reg).sum() / max(reg_n, 1))
            rows.append({"surface": name, "registry_file": p.name,
                         "spearman_rho": rho, "abs_rho_gt_0.90": bool(abs(rho) > 0.90),
                         "registry_dots": reg_n,
                         "share_registry_dots_within_3px_of_top_budget": overlap_reg_within3,
                         "over_70pct": bool(overlap_reg_within3 > 0.70)})
            print(f"{name:13s} {p.name[:60]:60s} rho={rho:+.4f} regDots={reg_n} within3px={overlap_reg_within3:.4f}", flush=True)
    worst = {n: max((r for r in rows if r["surface"] == n), key=lambda r: abs(r["spearman_rho"])) for n in surfaces}
    res = {"schema": "karage1-surface-registry-overlap-v1", "created_utc": datetime.now(timezone.utc).isoformat(),
           "registry_source": "data/scored/*.tif (SHA-pinned mirrors in registry/karage1_data_manifest.json; not organizer-authenticated)",
           "registry_files_checked": len(registry), "registry_file_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in registry},
           "sample_pixels": int(sel.size), "budget": BUDGET, "rows": rows,
           "worst_abs_spearman_by_surface": {k: {"registry_file": v["registry_file"], "spearman_rho": v["spearman_rho"]} for k, v in worst.items()},
           "caveat": "Continuous-surface Spearman on a footprint sample; 3-px overlap uses the top-budget surface pixels as a dot proxy, before any final placement.",
           "focus_sites_note": FOCUS_9_SITES}
    Path(args.out).write_text(json.dumps(res, indent=2, allow_nan=False) + "\n")
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
