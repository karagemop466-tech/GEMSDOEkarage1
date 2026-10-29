#!/usr/bin/env python3
"""Verify, from SHA-pinned mirror rasters, the binary-mask lineage of the nine focus sites.

Read-only geometry check. It reports set relationships between dot masks, nothing else:
it is not a holdout, not a score, and not a submission authorization. Inputs are the
pinned mirrors cached by ``scripts/audit_references.py --fetch`` in ``.cache/references``.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation, distance_transform_edt

ROOT = Path(__file__).resolve().parents[1]
SITES = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]


def load(path: Path) -> np.ndarray:
    with rasterio.open(path) as s:
        a = s.read(1)
    return a


def disk(r: int) -> np.ndarray:
    g = np.arange(-r, r + 1)
    dx, dy = np.meshgrid(g, g)
    return (dx ** 2 + dy ** 2) <= r ** 2


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cache", type=Path, default=ROOT / ".cache/references")
    ap.add_argument("--out", type=Path, default=ROOT / "evidence/site_lineage_verification_20261029.json")
    args = ap.parse_args()

    tpl = load(args.cache / "template.tif")
    labels = load(args.cache / "labels.tif")
    footprint = np.isfinite(tpl)
    dots = {s: (load(args.cache / f"{s}.tif") == 1) & footprint for s in SITES}
    label_pos = (labels == 1) & footprint
    # Mirror label-mask distance transform (Euclidean px to nearest known-label pixel).
    dist_to_label = distance_transform_edt(~label_pos)

    def removed_within(parent: np.ndarray, child: np.ndarray, r: int) -> dict:
        removed = parent & ~child
        added = child & ~parent
        near = dist_to_label <= r
        return {
            "parent_dots": int(parent.sum()),
            "child_dots": int(child.sum()),
            "removed": int(removed.sum()),
            "added": int(added.sum()),
            "removed_all_within_r_of_known_labels": bool(np.all(near[removed])) if removed.any() else None,
            "removed_within_r_of_known_labels": int(np.count_nonzero(removed & near)),
        }

    p25, p30 = dots["GEMSDOE25"], dots["GEMSDOE30"]
    b2 = dots["GEMSDOE32"]
    checks = {
        "GEMSDOE25_equals_GEMSDOE30": bool(np.array_equal(p25, p30)),
        "GEMSDOE25_dots": int(p25.sum()),
        "GEMSDOE30_dots": int(p30.sum()),
        "GEMSDOE32_vs_GEMSDOE25_remove_within_2px_of_labels": removed_within(p25, b2, 2),
        "GEMSDOE31_vs_GEMSDOE25_remove_within_1px_of_labels": removed_within(p25, dots["GEMSDOE31"], 1),
        "GEMSDOE28_vs_GEMSDOE25_remove_within_1px_of_labels": removed_within(p25, dots["GEMSDOE28"], 1),
        "GEMSDOE36_contains_GEMSDOE32": bool(np.all(dots["GEMSDOE36"][b2])),
        "GEMSDOE36_extra_dots_vs_GEMSDOE32": int(np.count_nonzero(dots["GEMSDOE36"] & ~b2)),
    }
    pairs = {}
    for a in SITES:
        for b in SITES:
            if a >= b:
                continue
            A, B = dots[a], dots[b]
            if not A.any() or not B.any():
                continue
            d_b = distance_transform_edt(~B)
            d_a = distance_transform_edt(~A)
            pairs[f"{a}|{b}"] = {
                "identical_dot_masks": bool(np.array_equal(A, B)),
                "a_dots_within_3px_of_b_fraction": round(float(np.count_nonzero(A & (d_b <= 3)) / A.sum()), 6),
                "b_dots_within_3px_of_a_fraction": round(float(np.count_nonzero(B & (d_a <= 3)) / B.sum()), 6),
            }
    out = {
        "schema": "karage1-site-lineage-verification-v1",
        "scope": "Binary dot-mask geometry on SHA-pinned owner mirrors. Not a holdout, score, or authorization.",
        "label_positive_pixels": int(label_pos.sum()),
        "checks": checks,
        "pairwise_nine_sites": pairs,
        "submit_authorized": False,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(checks, indent=2)[:3000])
    print("wrote", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
