#!/usr/bin/env python3
"""EXP3 — build the H-KP1 candidate submission (TTCA surface).

Hypothesis (preregistered in ``knowledge/kp1-preregistration-20261031.md``)
-------------------------------------------------------------------------
Expert-identified faults that are missing from the USGS+INGENIOUS catalogue are
not concentrated in the 2-15 px collar of the mapped traces (``evidence/
kp1_exp1_forensics.json``: that collar is where the three lowest-scoring focus
files live, and the two highest-scoring files place exactly 0.0 % of their dots
within 2 px of the catalogue).  They are structural boundaries that the
catalogue missed: (i) boundaries seen by several independent potential fields at
once (magnetic horizontal gradient, tilt derivative, upward-continued-to-150 m
magnetic gradient, isostatic-gravity horizontal gradient, basement step),
(ii) geomorphic scarps in the 1 m LiDAR metrics and the detrended DEM,
(iii) hydrothermal fluid conduits (thermal springs / wells), and
(iv) potassium-metasomatism alteration halos (low Th/K and low U/K).

The surface is a **geometric-mean consensus**: a cell scores high only when the
independent terms agree, which is what suppresses the single-field mimics
(single magnetic body, single scarp, single spring).

Emission follows the exact marginal-acceptance algebra of the published metric
(``vendor/gems57/metric.py``), with three empirically forced constraints:
no dot within 2 px of the mapped catalogue, a hard minimum dot separation
(``MIN_SEP_PX``) so that no two dots can spend FP mass on the same truth cell's
credit, and a flat-deep-basin suppression.

This script writes the GeoTIFF, the ZIP and a JSON receipt, then re-reads the
bytes.  It performs **no** submission decision: the release gate and the
selector live in ``scripts/kp1_release_gate.py``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage as ndi

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT))

from gems57 import submission_writer, validate                     # noqa: E402
from gems57.metric import ALPHA, BETA, EPS                         # noqa: E402
from scripts import kp1_data as D                                  # noqa: E402
from scripts import kp1_planes as P                                # noqa: E402

NAME = "karage1-kp1-ttca-springalter-far-conduit-32000-20261031"
NOTE = ("KP1 thermo-tectonic conduit alignment: multi-field edge+scarp+spring+Th/K "
        "consensus, >=2px off catalogue, 4px spacing, 32k dots")

MIN_SEP_PX = 4.0
BUDGET = 32_000
# geometric-mean exponents (sum to 1.0)
WEIGHTS = dict(lineament=0.34, geomorph=0.24, fluid=0.14, alteration=0.12, strain=0.16)


def rank01(plane: np.ndarray, mask: np.ndarray, bins: int = 1024) -> np.ndarray:
    """Monotone percentile map of ``plane`` inside ``mask`` (0 outside)."""
    v = np.asarray(plane, np.float32)[mask]
    v = v[np.isfinite(v)]
    if v.size == 0:
        return np.zeros(plane.shape, np.float32)
    qs = np.quantile(v, np.linspace(0, 1, bins + 1)[1:-1])
    qs = np.unique(qs)
    out = np.zeros(plane.shape, np.float32)
    r = np.searchsorted(qs, np.asarray(plane, np.float32), side="right") / max(len(qs), 1)
    out[mask] = np.clip(r[mask], 0.0, 1.0)
    return out


def geo_mean(terms: dict, weights: dict) -> np.ndarray:
    acc = np.zeros(next(iter(terms.values())).shape, np.float32)
    for key, w in weights.items():
        acc += np.float32(w) * np.log(np.clip(terms[key], 1e-6, 1.0)).astype(np.float32)
    return np.exp(acc).astype(np.float32)


def min_sep_select(score: np.ndarray, allowed: np.ndarray, n: int,
                   min_sep: float = MIN_SEP_PX) -> np.ndarray:
    """Greedy highest-score-first selection with a hard exclusion disc."""
    ys, xs = np.nonzero(allowed)
    v = score[ys, xs]
    order = np.argsort(-v, kind="stable")
    H, W = allowed.shape
    blocked = np.zeros(allowed.shape, bool)
    out = np.zeros(allowed.shape, bool)
    r = int(np.ceil(min_sep))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    disc = (yy * yy + xx * xx) <= min_sep ** 2
    taken = 0
    for k in order:
        y, x = int(ys[k]), int(xs[k])
        if blocked[y, x]:
            continue
        out[y, x] = True
        taken += 1
        y0, y1 = max(0, y - r), min(H, y + r + 1)
        x0, x1 = max(0, x - r), min(W, x + r + 1)
        blocked[y0:y1, x0:x1] |= disc[(y0 - y + r):(y1 - y + r), (x0 - x + r):(x1 - x + r)]
        if taken >= n:
            break
    return out


def build_surface() -> tuple[np.ndarray, dict]:
    fp = D.footprint()
    cat = D.catalogue()
    d_cat = ndi.distance_transform_edt(~cat)

    r = {n: rank01(np.asarray(P.load(n), np.float32), fp) for n in
         ("tmi_hg", "tc", "up150_grad", "iso_grav_anom_hg", "base_edge", "curv2",
          "det_elev_slope", "lidar_step", "lidar_coh", "spring_kde", "spring_hot",
          "ThK", "UK", "geod_2ndinv", "depth_to_base_surf", "det_elev")}

    lineament = geo_mean({k: np.maximum(r[k], 0.02) for k in
                          ("tmi_hg", "tc", "up150_grad", "iso_grav_anom_hg", "base_edge")},
                         {k: 0.2 for k in ("tmi_hg", "tc", "up150_grad",
                                           "iso_grav_anom_hg", "base_edge")})
    geomorph = 0.45 * r["det_elev_slope"] + 0.30 * r["lidar_step"] + 0.25 * r["curv2"]
    fluid = np.maximum(r["spring_kde"], r["spring_hot"])
    # K metasomatism -> high K -> LOW Th/K and LOW U/K: alteration = 1 - rank
    alteration = 0.6 * (1.0 - r["ThK"]) + 0.4 * (1.0 - r["UK"])
    strain = r["geod_2ndinv"]

    terms = dict(lineament=np.clip(lineament, 0, 1), geomorph=np.clip(geomorph, 0, 1),
                 fluid=np.clip(fluid, 0, 1), alteration=np.clip(alteration, 0, 1),
                 strain=np.clip(strain, 0, 1))
    s = geo_mean(terms, WEIGHTS)

    # flat, deep basin fill: low relief over thick basin fill -- the documented
    # false-positive population for both scarps and conductivity.
    flat = (r["det_elev_slope"] < 0.35) & (r["depth_to_base_surf"] > 0.60)
    s = np.where(flat, s * 0.35, s).astype(np.float32)
    s[~fp] = 0.0

    allowed = fp & (d_cat > 2.0)
    diag = dict(
        surface_max=float(s.max()), surface_mean=float(s[fp].mean()),
        flat_deep_basin_fraction_of_footprint=float(flat[fp].mean()),
        term_weight=WEIGHTS,
        allowed_cells=int(allowed.sum()),
        terms_note="each term is a percentile rank inside the footprint; geometric mean "
                   "requires agreement across independent fields",
    )
    return s, allowed, diag


def main(out_dir: Path, name: str = NAME, budget: int = BUDGET,
         min_sep: float = MIN_SEP_PX, weights: dict | None = None) -> dict:
    global WEIGHTS
    if weights:
        WEIGHTS = weights
    pins = D.verify_inputs()
    fp = D.footprint()
    cat = D.catalogue()
    s, allowed, diag = build_surface()
    dots = min_sep_select(s, allowed, budget, min_sep)
    pred = dots.astype(np.float32)

    # exact marginal-acceptance bookkeeping under the published formula,
    # with the *mapped catalogue* standing in as truth: a control, not a score.
    from gems57.metric import kernel
    d = ndi.distance_transform_edt(~cat)
    M = float((1.0 - np.minimum(d[dots] / 3.0, 1.0)).sum())
    n = int(dots.sum())
    control = dict(n_dots=n, self_credit_M=M, catalogue_fp_w=float(n - M),
                   note="catalogue-reference control only; the scored truth is private")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    tif = out_dir / f"{name}.tif"
    receipt = submission_writer.write_submission(
        tif, pred, ROOT / "data" / "official" / "sample_submission.tif", fp,
        note=NOTE, name=name, catalogue=cat,
        metadata=dict(hypothesis="H-KP1 thermo-tectonic conduit alignment (TTCA)",
                      min_sep_px=min_sep, budget=budget))
    val = validate.validate(tif, fp, cat)
    payload = dict(name=name, note=NOTE, note_length=len(NOTE), pins=pins,
                   emission=dict(n_dots=n, budget=budget, min_sep_px=min_sep,
                                 forbidden="within 2 px of the mapped catalogue",
                                 rule="greedy highest-surface-first with exclusion disc"),
                   surface_diagnostics=diag, catalogue_reference_control=control,
                   writer_receipt=receipt, validator=val)
    (out_dir / f"{name}.receipt.json").write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps({k: payload[k] for k in ("emission", "catalogue_reference_control")}, indent=1))
    print(json.dumps(val, indent=1))
    return payload


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "docs" / "downloads"))
    ap.add_argument("--name", default=NAME)
    ap.add_argument("--budget", type=int, default=BUDGET)
    ap.add_argument("--min-sep", type=float, default=MIN_SEP_PX)
    a = ap.parse_args()
    main(Path(a.out), a.name, a.budget, a.min_sep)
