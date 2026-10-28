#!/usr/bin/env python3
"""Audit two pinned parallel-PR TIFFs against one lattice witness, not a full registry.

Inputs must be fetched from the immutable links in PARALLEL_ASSETS and the
reference-assets manifest. This read-only audit never authorizes an upload.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import tempfile

import numpy as np
import rasterio
from scipy.ndimage import binary_dilation

try:
    from scripts.audit_references import binary_rank_correlation, disk, sha256
except ModuleNotFoundError:
    from audit_references import binary_rank_correlation, disk, sha256

ROOT = Path(__file__).resolve().parents[1]
PARALLEL_ASSETS = {
    "td": {
        "pr": 20, "commit": "722d7f1ef1d051e835dc00974a2dfbf04df1d600",
        "path": "docs/downloads/karage1-td-ksck-chi10m-stage2-37654d-20261028T061500Z-zeros.tif",
        "sha256": "20be4c631571ffb62b27f4c36ce518bf240a478f349e97242c147b763b5250ee",
    },
    "ctws": {
        "pr": 19, "commit": "cd981a202ffe0a4bda10218f14e54348499f67e2",
        "path": "docs/downloads/karage1-ctws2d-tiltworm-ptcf-relay-sep29-20261028T073640Z-zeros.tif",
        "sha256": "f33bc5cfccc917c3d241932253706a9b685db1dced0a95ed4b915d8c2fa5263f",
    },
}


def read_pinned(path, pin):
    if sha256(path) != pin:
        raise ValueError(f"SHA-256 mismatch: {path}")
    with rasterio.open(path) as ds:
        if ds.count != 1 or ds.driver != "GTiff" or ds.crs is None:
            raise ValueError(f"Invalid single-band georeferenced TIFF: {path}")
        return ds.read(1, masked=True), (ds.shape, ds.crs, ds.transform)


def audit(directory: Path) -> dict:
    assets = json.loads((ROOT / "registry/reference_assets.json").read_text())
    pins = {x["id"]: x["sha256"] for x in assets if x["id"] in ("template", "lattice")}
    if set(pins) != {"template", "lattice"}:
        raise ValueError("Missing reference pins")
    sample, grid = read_pinned(directory / "template.tif", pins["template"])
    footprint = ~np.ma.getmaskarray(sample) & np.isfinite(sample.data)
    if not footprint.any():
        raise ValueError("Empty footprint")
    reference, rgrid = read_pinned(directory / "lattice.tif", pins["lattice"])
    if rgrid != grid:
        raise ValueError("Lattice grid mismatch")
    if np.any(np.ma.getmaskarray(reference)[footprint]) or not np.isfinite(reference.data[footprint]).all():
        raise ValueError("Invalid lattice in footprint")
    lattice = footprint & (reference.data > 0)
    if not lattice.any():
        raise ValueError("Empty lattice")
    covered = binary_dilation(lattice, structure=disk(3))
    candidates = {}
    for label, item in PARALLEL_ASSETS.items():
        candidate, cgrid = read_pinned(directory / (label + ".tif"), item["sha256"])
        if cgrid != grid:
            raise ValueError(f"Candidate grid mismatch: {label}")
        vals = candidate.data[footprint]
        if np.any(np.ma.getmaskarray(candidate)[footprint]) or not np.isfinite(vals).all() or not np.isin(vals, [0, 1]).all():
            raise ValueError(f"Candidate is not finite, unmasked and binary inside footprint: {label}")
        dots = footprint & (candidate.data == 1)
        count = int(dots.sum())
        if count == 0:
            raise ValueError(f"Candidate has no dots: {label}")
        hits = int(np.count_nonzero(dots & covered))
        candidates[label] = {
            **item,
            "source_url": f"https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/{item['commit']}/{item['path']}",
            "candidate_dots_in_footprint": count,
            "dots_within_3px": hits,
            "directed_overlap": hits / count,
            "dot_spearman_in_footprint": binary_rank_correlation(dots, lattice, footprint),
            "duplicate_over_70_percent": hits * 10 > count * 7,
            "preplacement_surface_checked": False,
            "ok_to_submit": False,
        }
    return {
        "schema": "parallel-candidate-lattice-audit-v1",
        "scope": "One pinned witness only; not a complete registry or holdout audit. Peer mirror authenticity is not established.",
        "distance": "Closed Euclidean disk of radius 3 pixels on the matched mirror grid, within the template footprint.",
        "footprint_pixels": int(footprint.sum()),
        "uncovered_footprint_pixels": int(np.count_nonzero(footprint & ~covered)),
        "template_sha256": pins["template"], "lattice_sha256": pins["lattice"],
        "candidates": candidates,
    }


def fetch_inputs(directory: Path) -> None:
    """Fetch pinned GitHub blobs atomically; pins establish identity, not provenance."""
    entries = json.loads((ROOT / "registry/reference_assets.json").read_text())
    refs = {x['id']: x for x in entries if x['id'] in ('template', 'lattice')}
    items = {name: {'repo': item['repo'], 'ref': item['ref'], 'path': item['path'], 'sha256': item['sha256']}
             for name, item in refs.items()}
    items.update({name: {'repo': 'karagemop466-tech/GEMSDOEkarage1', 'ref': item['commit'],
                         'path': item['path'], 'sha256': item['sha256']}
                  for name, item in PARALLEL_ASSETS.items()})
    if set(items) != {'template', 'lattice', 'td', 'ctws'}:
        raise ValueError('Missing pinned inputs')
    directory.mkdir(parents=True, exist_ok=True)
    for name, item in items.items():
        destination = directory / (name + '.tif')
        if destination.exists():
            if sha256(destination) != item['sha256']:
                raise ValueError(f'SHA-256 mismatch: {destination}')
            continue
        endpoint = f"repos/{item['repo']}/contents/{item['path']}?ref={item['ref']}"
        with tempfile.NamedTemporaryFile(dir=directory, prefix='.fetch-', delete=False) as handle:
            tmp = Path(handle.name)
            try:
                subprocess.run(['gh', 'api', '-H', 'Accept: application/vnd.github.raw', endpoint], stdout=handle, check=True)
            except BaseException:
                tmp.unlink(missing_ok=True)
                raise
        try:
            if sha256(tmp) != item['sha256']:
                raise ValueError(f'SHA-256 mismatch: {name}')
            tmp.replace(destination)
        finally:
            tmp.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path, help="Directory containing template.tif, lattice.tif, td.tif, ctws.tif")
    parser.add_argument("--fetch", action='store_true', help='Fetch missing pinned inputs from GitHub')
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if args.fetch:
        fetch_inputs(args.directory)
    result = audit(args.directory)
    text = json.dumps(result, indent=2, allow_nan=False) + "\n"
    if args.out:
        args.out.write_text(text)
    else:
        print(text, end="")
    # This script produces an audit, never a release approval.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
