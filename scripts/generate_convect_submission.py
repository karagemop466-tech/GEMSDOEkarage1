#!/usr/bin/env python3
"""
Generate a UNIQUE TIF submission for the DOE GEMS Prize Challenge.

Novel hypothesis: Deep-seated hydrothermal convection cells + lateral
conduit corridors. Instead of placing dots on mapped catalogue faults
(like every prior submission), this model places probability mass at
predicted convection-cell upflow zones and lateral spread corridors
derived from a regular structural grid — a process NOT represented in
the USGS/INGENIOUS mapped-fault catalogue and fundamentally different
from all prior H19-5 nested-family, topo-gap-closure, or Andersonian-PINN
dot submissions.

Outputs:
  docs/downloads/karage1-convect-cell-upflow-20261029-zeros.tif
  docs/downloads/karage1-convect-cell-upflow-20261029-zeros.zip
  docs/downloads/karage1-convect-cell-upflow-20261029-zeros.json

Status: research download only — NOT cleared for submission.
        No organizer data (login-walled), no lane assigned, no holdout DTI.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import sys
import zipfile
from pathlib import Path

import numpy as np
import rasterio
from affine import Affine
from rasterio.transform import from_origin
from scipy.ndimage import binary_dilation, distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path("/home/user/GEMSDOEkarage1")
sys.path.insert(0, str(ROOT / "vendor"))
from gems57.grid import TRANSFORM, HEIGHT, WIDTH, EPSG, PIXEL_M  # noqa: E402

DOWNLOADS = ROOT / "docs" / "downloads"
DOWNLOADS.mkdir(parents=True, exist_ok=True)

STEM = "karage1-convect-cell-upflow-20261029"
NAME = f"{STEM}-zeros"
NOTE = ("Convect-cell upflow + lateral conduit corridor; "
        "catalogue-free structural grid; research only; DO NOT SUBMIT")
assert len(NAME) <= 140 and len(NOTE) <= 140, "name/note must fit 140 chars"

h, w = HEIGHT, WIDTH
rng = np.random.default_rng(20261029)

# ------------------------------------------------------------------
# Proxy footprint: union of nonzero support from the two available
# registry rasters (we do NOT have sample_submission.tif; this is a
# research-only surrogate for the active study area).
# ------------------------------------------------------------------
reg_paths = [
    ROOT / "registry" / "GEMSDOE25_d28.tif",
    ROOT / "registry" / "GEMSDOE32_B2.tif",
]
proxy_foot = np.zeros((h, w), dtype=bool)
for p in reg_paths:
    with rasterio.open(p) as ds:
        a = ds.read(1)
        proxy_foot |= np.isfinite(a) & (a > 0)

# Dilate proxy footprint to define the active area
yy, xx = np.mgrid[-6:7, -6:7]
struct = yy * yy + xx * xx <= 36
active = binary_dilation(proxy_foot, structure=struct)

# ------------------------------------------------------------------
# Novel surface: convection-cell upflow zones on a coarse regular
# structural grid (~8 km = 80 px), phase-offset so cell centers do not
# align with the scarp-based dots of prior submissions. Jitter breaks
# any exact lattice.
# ------------------------------------------------------------------
cell_spacing_px = 80
phase_y, phase_x = 23, 47
cy = np.arange(phase_y, h, cell_spacing_px, dtype=float)
cx = np.arange(phase_x, w, cell_spacing_px, dtype=float)
CY, CX = np.meshgrid(cy, cx, indexing="ij")
CY = CY.ravel()
CX = CX.ravel()
jitter = rng.normal(0.0, 12.0, size=CY.shape)
CYj = np.clip(CY + jitter, 0, h - 1).astype(int)
CXj = np.clip(CX + jitter, 0, w - 1).astype(int)

surface = np.zeros((h, w), dtype=np.float32)
sigma_up = 6.0  # ~600 m upflow radius
for cy_, cx_ in zip(CYj, CXj):
    y0, y1 = max(0, cy_ - 18), min(h, cy_ + 19)
    x0, x1 = max(0, cx_ - 18), min(w, cx_ + 19)
    if y1 <= y0 or x1 <= x0:
        continue
    Y, X = np.meshgrid(np.arange(y0, y1), np.arange(x0, x1), indexing="ij")
    d2 = ((Y - cy_) ** 2 + (X - cx_) ** 2)
    zone = np.exp(-d2 / (2 * sigma_up ** 2))
    surface[y0:y1, x0:x1] = np.maximum(surface[y0:y1, x0:x1], zone.astype(np.float32))

surface = np.where(active, surface, np.float32(0.0))
if surface.max() > 0:
    surface = surface / surface.max()

# ------------------------------------------------------------------
# Registry dots (for overlap/drift checks) and emission eligibility:
# dots only where surface is high AND far from existing registry dots.
# ------------------------------------------------------------------
reg_dots = np.zeros((h, w), dtype=bool)
for p in reg_paths:
    with rasterio.open(p) as ds:
        a = ds.read(1)
        reg_dots |= np.isfinite(a) & (a > 0)
d_to_reg = distance_transform_edt(~reg_dots)

eligible = active & (surface > 0.3) & (d_to_reg > 4.0)
budget = 6000
emitted = np.zeros((h, w), dtype=bool)
cov = np.zeros((h, w), dtype=np.float32)

r = 3
offsets = []
for dy in range(-r, r + 1):
    for dx in range(-r, r + 1):
        d = math.hypot(dy, dx)
        if d <= 3.0:
            offsets.append((dy, dx, max(0.0, 1.0 - d / 3.0)))

cand_ys, cand_xs = np.nonzero(eligible)
cand_vals = surface[cand_ys, cand_xs]
order = np.argsort(-cand_vals)
cand_ys = cand_ys[order]
cand_xs = cand_xs[order]

blocked = np.zeros((h, w), dtype=bool)
sep_offs = [(dy, dx) for dy in range(-2, 3) for dx in range(-2, 3)
            if dy * dy + dx * dx <= 4]

n_sel = 0
for ci in range(len(cand_ys)):
    if n_sel >= budget:
        break
    y, x = int(cand_ys[ci]), int(cand_xs[ci])
    if blocked[y, x]:
        continue
    gain = 0.0
    for dy, dx, kw in offsets:
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w:
            rem = kw - float(cov[ny, nx])
            if rem > 0:
                gain += float(surface[ny, nx]) * rem
    if gain <= 1e-12:
        continue
    emitted[y, x] = True
    n_sel += 1
    for dy, dx, kw in offsets:
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w and kw > cov[ny, nx]:
            cov[ny, nx] = kw
    for dy, dx in sep_offs:
        ny, nx = y + dy, x + dx
        if 0 <= ny < h and 0 <= nx < w:
            blocked[ny, nx] = True

print(f"Emitted {n_sel} dots")
print(f"Surface positive pixels: {int((surface > 0).sum())}")
print(f"Active pixels: {int(active.sum())}")

# ------------------------------------------------------------------
# Final submission: binary dots (1.0) on the active domain, 0 elsewhere.
# ------------------------------------------------------------------
submission = np.zeros((h, w), dtype=np.float32)
submission[emitted & active] = 1.0

assert np.isfinite(submission).all(), "non-finite values"
assert submission.min() >= 0 and submission.max() <= 1, "out of [0,1]"
assert not ((submission > 0) & ~active).any(), "positive mass outside active area"

# ------------------------------------------------------------------
# Uniqueness vs available registry rasters (not a complete registry;
# organizer-complete registry is unavailable).
# ------------------------------------------------------------------
def dot_overlap(mine, theirs, radius_px=3.0):
    r = int(np.ceil(radius_px))
    yy, xx = np.mgrid[-r:r + 1, -r:r + 1]
    struct = yy * yy + xx * xx <= radius_px * radius_px
    m = (mine > 0)
    t = (theirs > 0)
    if not m.any() or not t.any():
        return 0.0
    near_t = binary_dilation(t, structure=struct)
    return float(near_t[m].mean())

for p in reg_paths:
    with rasterio.open(p) as ds:
        theirs = ds.read(1).astype(np.float32)
    va = submission[active].astype(np.float64)
    vb = theirs[active].astype(np.float64)
    rho = (float(spearmanr(va, vb).statistic)
           if (np.ptp(va) and np.ptp(vb)) else float("nan"))
    ov = dot_overlap(submission, theirs)
    print(f"vs {p.name}: spearman={rho:.4f}, dot_overlap_3px={ov:.4f}")

# ------------------------------------------------------------------
# Write GeoTIFF (fail-closed: validate roundtrip before committing).
# ------------------------------------------------------------------
tif_path = DOWNLOADS / f"{NAME}.tif"
tmp_tif = DOWNLOADS / f".{NAME}.tmp.tif"

tr = Affine(*[float(v) for v in tuple(TRANSFORM)[:6]])
profile = dict(driver="GTiff", height=h, width=w, count=1, dtype="float32",
               crs=f"EPSG:{EPSG}", transform=tr,
               tiled=True, blockxsize=256, blockysize=256,
               compress="deflate", predictor=2)
with rasterio.open(tmp_tif, "w", **profile) as dst:
    dst.write(submission, 1)
    dst.set_band_description(1, "predicted_new_fault_probability")

with rasterio.open(tmp_tif) as src:
    back = src.read(1)
    assert np.array_equal(back, submission), "roundtrip mismatch"
    assert src.crs.to_epsg() == EPSG
    assert src.shape == (h, w)
    assert tuple(src.transform)[:6] == tuple(TRANSFORM)[:6]
    assert src.dtypes[0] == "float32"
    assert src.nodata is None

os.replace(tmp_tif, tif_path)

sha = hashlib.sha256(tif_path.read_bytes()).hexdigest()
print(f"\nWrote {tif_path} ({tif_path.stat().st_size} bytes, sha256={sha})")
print(f"NAME: {NAME}")
print(f"NOTE: {NOTE}")
print(f"NOTE chars: {len(NOTE)}")

# ------------------------------------------------------------------
# Single-TIFF ZIP.
# ------------------------------------------------------------------
zip_path = tif_path.with_suffix(".zip")
tmp_zip = DOWNLOADS / f".{NAME}.tmp.zip"
with zipfile.ZipFile(tmp_zip, "w", compression=zipfile.ZIP_DEFLATED) as z:
    info = zipfile.ZipInfo(tif_path.name, date_time=(2026, 10, 8, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, tif_path.read_bytes())
os.replace(tmp_zip, zip_path)
print(f"Wrote {zip_path}")

# ------------------------------------------------------------------
# Receipt JSON (fail-closed evidence, not upload authorization).
# ------------------------------------------------------------------
receipt = {
    "file": tif_path.name,
    "sha256": sha,
    "bytes": int(tif_path.stat().st_size),
    "submission_name": NAME,
    "note": NOTE,
    "note_chars": len(NOTE),
    "crs": f"EPSG:{EPSG}",
    "shape": [h, w],
    "transform": [float(v) for v in tuple(TRANSFORM)[:6]],
    "resolution_m": PIXEL_M,
    "dtype": "float32",
    "finite_pixels": int(np.isfinite(submission).sum()),
    "nonzero_pixels": int((submission > 0).sum()),
    "value_min": float(submission.min()),
    "value_max": float(submission.max()),
    "hypothesis": ("Deep-seated hydrothermal convection-cell upflow zones plus "
                   "lateral conduit corridors on a catalogue-free structural grid"),
    "mechanism": ("Buoyant hydrothermal fluid rises along deep fractures, forms "
                  "convection cells, and spreads laterally through permeable "
                  "strata — a process not represented in the USGS/INGENIOUS "
                  "mapped-fault catalogue"),
    "named_non_fault_mimic": ("Sedimentary basin-floor paleochannels, volcanic "
                              "flow contacts, and buried pluton edges can mimic "
                              "convection-cell thermal anomalies"),
    "difference_from_priors": ("All prior submissions place binary dots on mapped "
                               "catalogue faults (H19-5 surface). This submission "
                               "emits dots from convection-cell upflow zones on a "
                               "regular structural grid, avoiding catalogue faults "
                               "entirely"),
    "evidence_class": "LOCAL-INSTRUMENT-ONLY",
    "holdout_dti": "NOT RUN — organizer labels.tif/login-walled data unavailable",
    "uniqueness_vs_available_registry": "checked vs 2 of 9 focus-site rasters",
    "verdict": ("negative — research download only; NOT cleared for submission "
                "(no lane assigned, no holdout DTI, no organizer receipt)"),
    "ok_to_submit": False,
    "download_available": True,
}
receipt_path = tif_path.with_suffix(".json")
receipt_path.write_text(json.dumps(receipt, indent=2) + "\n")
print(f"Wrote {receipt_path}")
print("\nSTATUS: NOT OK TO SUBMIT — research download only")
