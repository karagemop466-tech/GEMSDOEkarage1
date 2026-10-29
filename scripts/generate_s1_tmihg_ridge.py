#!/usr/bin/env python3
"""Session arena/5ee7ef4b (2026-10-29): candidate H-S1, magnetic horizontal-gradient ridge dots.

Method (plain-language):
  1. Read the official training-feature band `tmi_hg` (horizontal gradient of total
     magnetic intensity) from the restored competition feature stack.
  2. Light Gaussian smoothing (sigma 1 px) to suppress 100 m pixel noise.
  3. Keep local maxima of the smoothed gradient (3x3 neighbourhood) inside the scored
     footprint. Maxima are the Blakely-Simpson-style crest of a magnetic contact.
  4. Off-catalogue rule: discard any maximum within 2 px of the MAPPED catalogue, so
     the output never sits on a known trace (the competition asks for unmapped faults).
  5. Strongest first, Poisson-style spacing of at least 2.8 px between kept dots.
  6. Keep the top 37,654 dots (same budget as the 0.2778 champion, for a like-for-like
     comparison).

Writes through the shared writer `vendor/gems57/submission_writer.write_submission`
(all-finite float32 in [0,1], zeros outside footprint, single band, EPSG:32611,
transform and shape copied from the sample grid, no catalogue overlap).

Named non-fault mimics: lithologic contacts (intrusive/volcanic boundaries), magnetite-rich
units, and cultural/infrastructure magnetic noise. Not validated for the leaderboard.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))

from gems57 import grid as G57  # noqa: E402
from gems57.submission_writer import write_submission  # noqa: E402

DATA = Path(os.environ.get("GEMS_DATA_DIR", "/tmp/gems_data"))
BUDGET = 37654
APRON_PX = 2.0
SPACING_PX = 2.8
NAME = "karage1-s1-tmihg-ridge-offcat-20261029"
OUT_DIR = ROOT / "archive" / "research-s1-20261029"  # negative research artifact: not in docs/downloads
OUT_TIF = OUT_DIR / f"{NAME}-zeros.tif"
NOTE = "H-S1 tmi_hg crest dots, off-catalogue, 2.8px spacing; all-finite zeros; format-valid"


def read_band(path: Path, description_prefix: str) -> np.ndarray:
    with rasterio.open(path) as ds:
        names = list(ds.descriptions)
        idx = [i for i, n in enumerate(names) if n and n.startswith(description_prefix)]
        if len(idx) != 1:
            raise ValueError(f"expected one band starting with {description_prefix!r}, got {idx}")
        return ds.read(idx[0] + 1).astype(np.float64)


def select_dots(score: np.ndarray, footprint: np.ndarray, catalogue: np.ndarray) -> tuple[np.ndarray, dict]:
    valid = footprint & np.isfinite(score)
    s = np.where(valid, score, 0.0)
    s = ndi.gaussian_filter(s, sigma=1.0)
    is_max = (s == ndi.maximum_filter(s, size=3)) & valid & (s > 0)
    dist_cat = ndi.distance_transform_edt(~catalogue)
    off_cat = dist_cat > APRON_PX
    cand = np.argwhere(is_max & off_cat)
    vals = s[cand[:, 0], cand[:, 1]]
    order = np.argsort(-vals, kind="stable")
    cand = cand[order]

    r = int(np.ceil(SPACING_PX))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disk = (yy * yy + xx * xx) < SPACING_PX * SPACING_PX
    dy, dx = yy[disk], xx[disk]
    blocked = np.zeros(score.shape, bool)
    h, w = score.shape
    chosen = []
    for y, x in cand:
        if blocked[y, x]:
            continue
        chosen.append((y, x))
        ty, tx = y + dy, x + dx
        ok = (ty >= 0) & (ty < h) & (tx >= 0) & (tx < w)
        blocked[ty[ok], tx[ok]] = True
        if len(chosen) >= BUDGET:
            break
    dots = np.zeros(score.shape, bool)
    if chosen:
        arr = np.asarray(chosen)
        dots[arr[:, 0], arr[:, 1]] = True
    info = dict(local_maxima_off_catalogue=int(cand.shape[0]), dots_kept=int(dots.sum()),
                budget=BUDGET, budget_met=bool(dots.sum() == BUDGET), budget_shortfall=int(BUDGET - dots.sum()),
                smoothing_sigma_px=1.0,
                apron_px=APRON_PX, spacing_px=SPACING_PX)
    return dots, info


def main() -> None:
    g = G57.load_grid(DATA)
    tmi_hg = read_band(DATA / "training_features.tif", "tmi_hg")
    dots, info = select_dots(tmi_hg, g.footprint, g.catalogue)
    if info["dots_kept"] == 0:
        raise SystemExit("BLOCKED: no off-catalogue crest dots survive the spacing rule")
    pred = dots.astype(np.float32)
    pred[~g.footprint] = 0.0
    receipt = write_submission(
        OUT_TIF, pred, DATA / "sample_submission.tif", g.footprint,
        note=NOTE, name=NAME, catalogue=g.catalogue,
        metadata=dict(hypothesis="H-S1 magnetic tmi_hg crest, off-catalogue", selection=info,
                      session="arena/5ee7ef4b-gemsdoekarage1", date_utc="2026-10-29",
                      approved_for_weekly_slot=False, promoted=False),
    )
    OUT_TIF.with_suffix(".selection.json").write_text(json.dumps(info, indent=2) + "\n")
    print(json.dumps({k: receipt[k] for k in ("file", "sha256", "bytes", "note_chars", "zip_file", "zip_sha256")}, indent=2))
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
