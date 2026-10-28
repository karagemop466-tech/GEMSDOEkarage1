"""Fail-closed adapter for the shared GEMSDOE registry comparison.

The previous local scanner classified lattice and dense rasters as exempt from
proximity checking, sampled rank correlation, and silently skipped unreadable
inputs. None of those exemptions is in the parallel-run protocol. This adapter
delegates to ``gems57.uniqueness`` and requires an explicit, hash-pinned
inventory. A list of locally discovered files is diagnostic only; it cannot
certify a complete registry. A saved pre-placement surface result must be
provided to the final-dot gate.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import re

import numpy as np
import rasterio
from gems57 import uniqueness

FOCUS_9_SITES = tuple(f"GEMSDOE{n}" for n in (24, 25, 27, 28, 30, 31, 32, 33, 36))


def _digest_array(values: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(values, dtype='<f4').tobytes()).hexdigest()


def _inventory(index: dict | list | Path | None) -> tuple[dict | list, str, bool]:
    if index is None:
        index = []  # not evidence of completeness
    if isinstance(index, (str, Path)):
        index = json.loads(Path(index).read_text())
    if not isinstance(index, (list, dict)):
        raise ValueError('registry inventory must be an object or a diagnostic list')
    complete = isinstance(index, dict) and index.get('complete_accessible_scan') is True
    if complete:
        entries = index.get('rasters')
        if not isinstance(entries, list) or not entries or index.get('errors'):
            raise ValueError('complete inventory must contain pinned entries and no source errors')
        if type(index.get('expected_raster_count')) is not int or index['expected_raster_count'] != len(entries):
            raise ValueError('complete inventory requires the independently recorded expected raster count')
        coverage = index.get('source_coverage')
        if not isinstance(coverage, dict) or not isinstance(coverage.get('scope'), str) or not coverage['scope'].strip():
            raise ValueError('complete inventory requires an explicit source-coverage statement')
        sources = coverage.get('immutable_repos')
        if not isinstance(sources, list) or not sources:
            raise ValueError('complete inventory requires immutable source-repository pins')
        if any(not isinstance(x, dict) or not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', str(x.get('repo', '')))
               or not re.fullmatch(r'[0-9a-f]{40}', str(x.get('commit', ''))) for x in sources):
            raise ValueError('source coverage contains an unpinned repository')
        source_repos = {x['repo'] for x in sources}
        seen = set()
        for item in entries:
            if (not isinstance(item, dict) or not re.fullmatch(r'[0-9a-f]{64}', str(item.get('sha256', '')))
                    or not isinstance(item.get('cache_file'), str) or not item['cache_file']
                    or item.get('repo_first') not in source_repos
                    or not isinstance(item.get('sources'), list) or not item['sources']
                    or any(not isinstance(src, str) or not src for src in item['sources'])):
                raise ValueError('registry entry lacks a pinned source, saved file or full SHA-256')
            if item['sha256'] in seen:
                raise ValueError('complete inventory contains repeated raster hashes')
            seen.add(item['sha256'])
    encoded = json.dumps(index, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
    return index, hashlib.sha256(encoded).hexdigest(), bool(complete)



def _digest_footprint(footprint: np.ndarray) -> str:
    return hashlib.sha256(np.ascontiguousarray(footprint, dtype=np.uint8).tobytes()).hexdigest()


def _digest_grid(grid: tuple) -> str:
    shape, crs, transform = grid
    value = {'shape': list(shape), 'crs': str(crs), 'transform': list(transform)[:6]}
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def _rank_coverage(comparison: dict, index: dict | list) -> tuple[bool, float | None]:
    """Require a defined full-footprint correlation for EVERY pinned reference.

    The shared comparator currently regards undefined rows as complete and can
    report just the worst defined row. Reject that ambiguity at this adapter.
    This receipt is tamper-evident against accidental input changes, not a signed
    proof of when a human produced it.
    """
    records, _, _ = uniqueness.records_from_index(index)
    rows = comparison.get('rows')
    if not isinstance(rows, list) or len(rows) != len(records) or not rows:
        return False, None
    expected = {r.get('sha256') for r in records}
    measured = {r.get('sha256') for r in rows if isinstance(r, dict)}
    if None in expected or measured != expected or len(measured) != len(rows):
        return False, None
    values = [r.get('spearman_full_footprint') for r in rows]
    if any(not isinstance(rho, (int, float)) or isinstance(rho, bool) or not math.isfinite(rho)
           or abs(rho) > 1.0 + 1e-12 for rho in values):
        return False, None
    return True, max(abs(float(rho)) for rho in values)

def _verify_registry_pixels(index: dict | list, footprint: np.ndarray, expected_grid: tuple) -> list[str]:
    """Guard the shared comparator, which otherwise converts inside NaNs to zero."""
    records, _, _ = uniqueness.records_from_index(index)
    errors = []
    for rec in records:
        path = Path(rec['file'])
        if not path.is_absolute():
            path = uniqueness.ROOT / path
        try:
            with rasterio.open(path) as src:
                if src.count != 1 or (src.shape, src.crs, src.transform) != expected_grid:
                    raise ValueError('band count or grid mismatch')
                data = src.read(1)
                mask = src.read_masks(1) != 0
            values = data[footprint]
            if not mask[footprint].all() or not np.isfinite(values).all():
                raise ValueError('missing or non-finite registry value inside footprint')
            if np.any((values < 0) | (values > 1)):
                raise ValueError('registry values outside [0,1] inside footprint')
        except (OSError, ValueError, rasterio.errors.RasterioError) as exc:
            errors.append(f'{path}: {exc}')
    return errors


def _grid(path: Path) -> tuple:
    with rasterio.open(path) as ds:
        if ds.count != 1:
            raise ValueError('template/candidate must have one band')
        return (ds.shape, ds.crs, ds.transform)


def check_preplacement_surface(surface: np.ndarray, foot: np.ndarray, template_path: Path,
                               registry_index: dict | list | Path | None) -> dict:
    """Compare the continuous surface before any production dot placement."""
    if template_path is None or registry_index is None:
        raise ValueError('a sample template and complete pinned registry are mandatory')
    surface = np.asarray(surface, dtype=np.float32)
    foot = np.asarray(foot, dtype=bool)
    if surface.shape != foot.shape or not foot.any() or not np.isfinite(surface[foot]).all():
        raise ValueError('surface/footprint mismatch or non-finite surface')
    lo, hi = float(np.min(surface[foot])), float(np.max(surface[foot]))
    if lo == hi:
        raise ValueError('constant surface has undefined rank correlation')
    # A monotone affine transform leaves Spearman ranks invariant; it merely
    # meets the shared comparison API's [0,1] input contract.
    normalized = np.zeros(surface.shape, np.float32)
    normalized[foot] = (surface[foot] - lo) / (hi - lo)
    index, digest, complete = _inventory(registry_index)
    grid = _grid(template_path)
    if grid[0] != foot.shape:
        raise ValueError('surface/footprint grid does not match template')
    errors = _verify_registry_pixels(index, foot, grid)
    if errors:
        return {'phase': 'surface_before_placement', 'passed': False, 'errors': errors,
                'inventory_sha256': digest, 'surface_sha256': _digest_array(surface)}
    comp = uniqueness.compare_array_to_registry(normalized, index, foot, expected_grid=grid)
    ranks_defined, rho = _rank_coverage(comp, index)
    passed = bool(complete and comp['complete_accessible_scan'] and ranks_defined
                  and rho <= uniqueness.RHO_LIMIT and not comp['missing_or_invalid'])
    return {'phase': 'surface_before_placement', 'passed': passed,
            'inventory_sha256': digest, 'surface_sha256': _digest_array(surface),
            'footprint_sha256': _digest_footprint(foot), 'template_grid_sha256': _digest_grid(grid),
            'all_reference_ranks_defined': ranks_defined,
            'surface_max_abs_rho': rho, 'registry_rasters_checked': comp['registry_rasters_checked'],
            'complete_accessible_scan': comp['complete_accessible_scan'],
            'comparison': comp}


def run_full_fleet_uniqueness_gate(continuous_surface: np.ndarray, final_dots_f32: np.ndarray,
                                   final_tif_path: Path, foot: np.ndarray, *,
                                   registry_index: dict | list | Path | None = None,
                                   preplacement_report: dict | None = None, sample: Path | None = None,
                                   **_legacy: object) -> dict:
    """Compare exact saved final bytes against every explicitly indexed raster.

    ``passed`` requires the separately recorded surface gate, a complete pinned
    inventory and the literal directed overlap rule on *all* registry rasters.
    This function never selects a weekly submission slot.
    """
    index, digest, complete = _inventory(registry_index)
    foot = np.asarray(foot, dtype=bool)
    with rasterio.open(final_tif_path) as ds:
        if ds.count != 1 or ds.dtypes[0] != 'float32':
            raise ValueError('candidate must have one float32 band')
        saved = ds.read(1)
        grid = (ds.shape, ds.crs, ds.transform)
    if sample is not None and grid != _grid(sample):
        raise ValueError('saved raster grid differs from the sample')
    if saved.shape != foot.shape or not np.array_equal(saved, np.asarray(final_dots_f32)):
        raise ValueError('candidate array does not match saved GeoTIFF bytes')
    if not np.isfinite(saved).all() or np.any((saved < 0) | (saved > 1)):
        raise ValueError('saved candidate contains non-finite or out-of-range values')
    errors = _verify_registry_pixels(index, foot, grid)
    if errors:
        return {'passed': False, 'errors': errors, 'inventory_sha256': digest}
    result = uniqueness.compare_to_registry(final_tif_path, index, foot, expected_grid=grid)
    surface_comparison = preplacement_report.get('comparison', {}) if isinstance(preplacement_report, dict) else {}
    surface_ranks_defined, surface_rho = _rank_coverage(surface_comparison, index)
    surface_ok = bool(isinstance(preplacement_report, dict)
                      and preplacement_report.get('phase') == 'surface_before_placement'
                      and preplacement_report.get('passed') is True
                      and preplacement_report.get('surface_sha256') == _digest_array(continuous_surface)
                      and preplacement_report.get('footprint_sha256') == _digest_footprint(foot)
                      and preplacement_report.get('template_grid_sha256') == _digest_grid(grid)
                      and preplacement_report.get('inventory_sha256') == digest
                      and surface_comparison.get('complete_accessible_scan') is True
                      and surface_ranks_defined and surface_rho <= uniqueness.RHO_LIMIT)
    ranks_defined, final_rho = _rank_coverage(result, index)
    return {
        'protocol_rule': 'literal-Rule-1-all-registry-rasters',
        'candidate_sha256': uniqueness._sha(final_tif_path),
        'candidate_dots': int(((saved > 0) & foot).sum()),
        'inventory_sha256': digest,
        'surface_preplacement_verified': surface_ok,
        'complete_accessible_scan': bool(complete and result['complete_accessible_scan']),
        'max_directed_overlap_3px_any_registry': result['worst_dot_overlap'],
        'max_overlap_reference': result['worst_overlap_submission'],
        'all_reference_ranks_defined': ranks_defined,
        'max_final_dot_spearman': final_rho,
        'comparison': result,
        'passed': bool(surface_ok and complete and result['unique'] and ranks_defined
                       and final_rho <= uniqueness.RHO_LIMIT),
    }


def run_surface_gate(continuous_surface, footprint, *, sample: Path, registry_index: Path | dict) -> dict:
    """Compatibility alias to the one pre-placement shared-comparison workflow."""
    return check_preplacement_surface(continuous_surface, footprint, sample, registry_index)
