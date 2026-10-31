#!/usr/bin/env python3
"""Catalogue hide-and-recover holdout screen for the 2026-10-31 candidate.

Uses the shared evaluator ``src/gemsk/holdout.py`` (whole-segment withholding,
200 px spatial blocks, 3 px buffer, pooled DTI with a paired block bootstrap).
The truth is the mapped USGS/INGENIOUS catalogue withheld whole, so this rewards
re-finding mapped traces and penalises off-catalogue placement by construction.

It is a SCREEN, never a leaderboard estimate.  The champion GEMSDOE32 B2 is run as
a control so the two numbers are comparable on identical folds.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from gemsk import holdout  # noqa: E402
from gemskarage1.paths import DOCS_DATA_DIR, EVIDENCE_DIR  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"


def dots_from(path: Path, foot: np.ndarray) -> np.ndarray:
    with rasterio.open(path) as src:
        a = src.read(1)
    return (np.isfinite(a) & (a > 0) & foot)


def main() -> int:
    with rasterio.open(DATA / "sample_submission.tif") as src:
        foot = np.isfinite(src.read(1))
    with rasterio.open(DATA / "labels.tif") as src:
        catalogue = src.read(1) > 0

    folds = holdout.make_folds(catalogue, foot, k=4, block_px=200, buffer_px=3,
                               scheme="blocked", seed=20261027)
    print(f"folds: {[(f['fold'], f['n_withheld'], f['n_segments_withheld']) for f in folds]}")

    arms = {}
    cand_glob = sorted((ROOT / "docs/downloads").glob("karage1-seisprox-*-zeros.tif"))
    if not cand_glob:
        raise SystemExit("candidate tif not found")
    for p in cand_glob:
        tag = p.stem.replace("karage1-seisprox-", "").replace("-zeros", "")
        arms[f"candidate_{tag}"] = dots_from(p, foot)
    cand = cand_glob[-1]
    arms["control_gemsdoe32_b2"] = dots_from(ROOT / "registry/GEMSDOE32_B2.tif", foot)
    rng_arm = np.zeros(foot.shape, bool)
    rng = np.random.default_rng(7)
    ys, xs = np.nonzero(foot)
    pick = rng.choice(ys.size, size=min(37654, ys.size), replace=False)
    rng_arm[ys[pick], xs[pick]] = True
    arms["control_uniform_random"] = rng_arm

    terms = {name: [] for name in arms}
    for fold in folds:
        for name, d in arms.items():
            _, t = holdout.evaluate_dots(d, fold, block_px=200)
            terms[name].append(t)

    pooled = {name: holdout.pooled(v) for name, v in terms.items()}
    ci = holdout.bootstrap_ci(terms, draws=1000, seed=20261027)

    out = {
        "schema": "karage1-holdout-screen-v1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "evaluator": holdout.VERSION,
        "evaluator_source": "src/gemsk/holdout.py",
        "truth": "mapped USGS/INGENIOUS catalogue segments withheld whole (local mirror)",
        "caveat": "Catalogue-truth holdout cannot rank off-catalogue candidates; not a leaderboard estimate.",
        "pooled": pooled,
        "ci95": ci,
        "candidate_file": str(cand.relative_to(ROOT)),
    }
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    path = EVIDENCE_DIR / "holdout_screen_seisprox_20261031.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"pooled": {k: round(v["dti"], 5) for k, v in pooled.items()},
                      "out": str(path.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
