#!/usr/bin/env python3
"""Independently reassess prior saved TIFFs using the shared literal registry gate.

This is a negative-witness audit, not a complete-registry certification or a
new model experiment. It downloads nothing and never changes raster bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "src", ROOT / "vendor"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from gems57.uniqueness import dot_overlap, saturation_certificate  # shared implementation
from scripts.validate_geotiff import diagnose

SAMPLE_HASH = "2176d08e485aa2cd2860ce8df539db4faf4d76163b38a4dd8c30a40454d35cbc"
LABEL_HASH = "7ba308ccdc4418b31a178f4f1ef21aaa6e152e4028f2f6f64b01f7eb25ae4093"
LATTICE_HASH = "b4570b406efec198eb2f4d142ad8d0d6184b14b66f2f52b5c4d697f0647dc9b2"
PARENT_HASH = "91eae1ca42ec845eaa8c2ba32da49806e24751743459b8a10017c479bbe639b8"
CHAMPION_HASH = "c55bafc470054e8271dcb89347a17e07fefe50de6af6e6ba6c4b169ef7ab6fa9"
FILES = {
    "hmas": ROOT / "docs/downloads/karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif",
    "gpcz": ROOT / "docs/downloads/gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif",
}


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def checked(path: Path, digest: str) -> None:
    actual = sha(path)
    if actual != digest:
        raise ValueError(f"unexpected bytes for {path}: {actual} != {digest}")


def read_same_grid(path: Path, grid, footprint: np.ndarray | None = None, *, require_float32: bool = False) -> np.ndarray:
    with rasterio.open(path) as ds:
        if (ds.driver != "GTiff" or ds.count != 1 or (ds.shape, ds.crs, ds.transform) != grid
                or (require_float32 and ds.dtypes[0] != "float32")):
            raise ValueError(f"single-band CRS/shape/transform mismatch: {path}")
        arr = ds.read(1)
        if footprint is not None and not (ds.read_masks(1)[footprint] != 0).all():
            raise ValueError(f"masked pixels inside footprint: {path}")
        return arr


def audit(data: Path, champion: Path) -> dict:
    sample = data / "sample_submission.tif"
    labels = data / "labels.tif"
    lattice = data / "scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif"
    parent = data / "scored/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif"
    for p, digest in ((sample, SAMPLE_HASH), (labels, LABEL_HASH), (lattice, LATTICE_HASH),
                      (parent, PARENT_HASH), (champion, CHAMPION_HASH)):
        checked(p, digest)
    with rasterio.open(sample) as src:
        sample_values = src.read(1, masked=True)
        fp = ~np.ma.getmaskarray(sample_values) & np.isfinite(sample_values.data)
        grid = (src.shape, src.crs, src.transform)
    if not fp.any():
        raise ValueError("empty sample footprint")
    lab_arr = read_same_grid(labels, grid, fp)
    cat = fp & np.isfinite(lab_arr) & (lab_arr > 0)
    lat = read_same_grid(lattice, grid, fp)
    lat_dots = fp & np.isfinite(lat) & (lat > 0)
    if not lat_dots.any():
        raise ValueError("empty lattice witness")
    certificate = saturation_certificate(lattice, fp, expected_grid=grid)
    candidates = {}
    for key, tif in FILES.items():
        arr = read_same_grid(tif, grid, fp, require_float32=True)
        if not np.isfinite(arr).all() or not np.all((arr == 0) | (arr == 1)):
            raise ValueError(f"candidate is not finite binary: {tif}")
        dots = fp & (arr > 0)
        n = int(dots.sum())
        if not n:
            raise ValueError("empty candidate")
        fraction = dot_overlap(dots, lat_dots)
        matched = int(round(fraction * n))
        lower_bound = max(0, n - certificate["uncovered_allowed_pixels"]) / n
        check = diagnose(tif, sample, SAMPLE_HASH)
        candidates[key] = {
            "file": str(tif.relative_to(ROOT)), "sha256": sha(tif), "dots_in_footprint": n,
            "on_catalogue_pixels": int((dots & cat).sum()),
            "lattice_dots_within_3px_count": matched, "lattice_directed_overlap": fraction,
            "minimum_possible_lattice_overlap_at_this_budget": lower_bound,
            "literal_duplicate": fraction > 0.70,
            "surface_before_placement": "unavailable; not independently replayed",
            "format_diagnostics": check["diagnostics"], "saved_byte_checks": check["checks"],
            "submit_authorized": False,
        }
    ref = read_same_grid(parent, grid, fp)
    champion_arr = read_same_grid(champion, grid, fp)
    p = fp & np.isfinite(ref) & (ref > 0)
    c = fp & np.isfinite(champion_arr) & (champion_arr > 0)
    disk2 = np.fromfunction(lambda y, x: (y - 2) ** 2 + (x - 2) ** 2 <= 4, (5, 5))
    near2 = binary_dilation(cat, structure=disk2)
    expected_b2 = p & ~near2
    prior = json.loads((ROOT / "evidence/run_card_hmas_sinter.json").read_text())
    inherited = prior["holdout_dti"]["gems57_pooled_hide_v2_detached"]
    return {
        "schema": "karage1-literal-release-reassessment-v1",
        "reviewed_utc_date": "2026-10-28",
        "scope": "One immutable lattice witness is sufficient for a negative verdict. This is not a complete registry scan.",
        "provenance": {
            "sample_sha256": SAMPLE_HASH, "labels_sha256": LABEL_HASH, "lattice_sha256": LATTICE_HASH,
            "parent_sha256": PARENT_HASH, "champion_sha256": CHAMPION_HASH,
            "source": "Owner-supplied commit-pinned GitHub mirrors; hashes do not establish organizer authenticity.",
            "lattice_source": "https://github.com/buffedlizard55-lab/GEMSDOE24/blob/07345ea0604953d7efb858d9cfbc21e20c7aca0b/inputs/calibration/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif",
        },
        "lattice_certificate": {
            **certificate,
            "witness_file": "data/scored/13gems_20261001_r13-lattice-s5_v2_nan-outside.tif",
            "support_definition": "finite value > 0 inside the mirrored footprint",
            "geometry_only_maximum_dots_at_70_percent_overlap": int(certificate["uncovered_allowed_pixels"] / 0.30),
            "caveat": "Geometry bound only; a smaller candidate is not necessarily unique, valid, or competitive.",
        },
        "candidates": candidates,
        "b2_family_audit": {
            "parent_dots": int(p.sum()), "champion_dots": int(c.sum()),
            "parent_dots_removed": int((p & ~c).sum()), "champion_dots_added": int((c & ~p).sum()),
            "champion_exactly_parent_minus_catalogue_2px": bool(np.array_equal(c, expected_b2)),
            "causal_explanation": "Not established: hidden test labels and artifact-linked organizer receipts unavailable.",
        },
        "inherited_hmas_holdout": {
            **inherited,
            "verification_status": "Prior-session measurement; not independently rerun in this review. The original split cut some branches into short chunks and did not establish the requested buffered whole-component holdout.",
        },
        "verdict": "negative", "new_experiments": 0, "new_rasters": 0,
        "submission_slots_spent_by_this_review": 0,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=ROOT / "data")
    ap.add_argument("--champion", type=Path, default=ROOT / ".cache/audit-inputs/champion.tif")
    ap.add_argument("--out", type=Path, help="Write a JSON audit instead of stdout")
    args = ap.parse_args()
    try:
        report = audit(args.data_dir, args.champion)
        text = json.dumps(report, indent=2, allow_nan=False) + "\n"
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix='.' + args.out.name + '.', suffix='.partial', dir=args.out.parent)
            tmp = Path(name)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as fh:
                    fh.write(text)
                os.chmod(tmp, 0o644)
                tmp.replace(args.out)
            finally:
                tmp.unlink(missing_ok=True)
            print(f"Wrote {args.out}. Negative witness; this does not approve a submission.")
        else:
            print(text, end="")
    except (OSError, ValueError, KeyError) as exc:
        print(f"Audit blocked: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
