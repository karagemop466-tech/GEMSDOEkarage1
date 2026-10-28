"""Full-Fleet 593-Raster Duplication & Registry Uniqueness Gate (`Protocol Rule 1`).

Audits BOTH:
1. Pre-placement continuous belief surface (`|Spearman| <= 0.90` against EVERY raster in the fleet), AND
2. Final binary dot submission (`|Spearman| <= 0.90` against EVERY raster in the fleet, `SHA-256` byte &
   pixel uniqueness, and `3-px dot overlap <= 70.0%` against all discrete competing fault submissions,
   with transparent classification of uniform lattice diagnostics `r13-lattice-s5` and continuous un-thinned
   research surfaces).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

FOCUS_9_SITES: tuple[str, ...] = (
    "GEMSDOE24",
    "GEMSDOE25",
    "GEMSDOE27",
    "GEMSDOE28",
    "GEMSDOE30",
    "GEMSDOE31",
    "GEMSDOE32",
    "GEMSDOE33",
    "GEMSDOE36",
)


def _classify_raster(vals_fp: np.ndarray, rel_key: str) -> str:
    kl = rel_key.lower()
    if "lattice" in kl or "grid-s5" in kl or "pindrop" in kl:
        return "uniform_lattice_diagnostic"
    pos = vals_fp[vals_fp > 0.0]
    n_pos = int(pos.size)
    if n_pos == 0:
        return "empty"
    frac_unit = float((pos >= 0.999).mean())
    if n_pos > 200_000 and frac_unit < 0.50:
        return "continuous_unthinned_surface"
    if n_pos > 100_000:
        return "overdense_exploratory_mask"
    return "discrete_fault_submission"


def discover_fleet_tifs(
    clones_dir: Path,
    extra_scored_dir: Path,
    ddir: Path,
    *,
    prior_local_dir: Path | None = None,
    exclude_paths: set[Path] | None = None,
) -> list[tuple[str, str, Path]]:
    """Return `(site, rel_path, full_path)` for all unique `.tif` rasters across the entire GEMSDOE fleet."""
    skip_names = {
        "training_features.tif",
        "labels.tif",
        "existing_faults.tif",
        "sample_submission.tif",
        "example_submission.tif",
        "geodawn_extensions_u8.tif",
        "geodawn_rad_u8.tif",
        "lidar_scarp_features_u8.tif",
        "derived_sgmc_faults_100m_u8.tif",
        "acquisition_block_id_100m.tif",
        "tiger_road_distance_m.tif",
        "blm_closed_claim_distance_m.tif",
        "topo_10m_derived_100m_u8.tif",
        "dem10_chi_100m_i16.tif",
        "dem10_chi_100m_u8.tif",
        "dem10_chi_100m_sig_i32.tif",
    }
    excl_resolved = {p.resolve() for p in (exclude_paths or set()) if p.exists()}
    found: list[tuple[str, str, Path]] = []
    seen_real: set[str] = set()

    if clones_dir.is_dir():
        for repo_dir in sorted(clones_dir.iterdir()):
            if not repo_dir.is_dir():
                continue
            site = repo_dir.name
            for p in sorted(repo_dir.rglob("*.tif")):
                if ".git" in p.parts or p.name in skip_names or p.stat().st_size < 10_000:
                    continue
                if p.resolve() in excl_resolved:
                    continue
                rk = f"{site}/{p.relative_to(repo_dir)}"
                if rk not in seen_real:
                    seen_real.add(rk)
                    found.append((site, str(p.relative_to(repo_dir)), p))

    if extra_scored_dir.is_dir():
        for item in sorted(extra_scored_dir.iterdir()):
            if item.is_dir():
                site = item.name
                for p in sorted(item.rglob("*.tif")):
                    if p.name in skip_names or p.stat().st_size < 10_000 or p.resolve() in excl_resolved:
                        continue
                    rk = f"{site}/{p.relative_to(item)}"
                    if rk not in seen_real:
                        seen_real.add(rk)
                        found.append((site, str(p.relative_to(item)), p))
            elif item.is_file() and item.suffix == ".tif":
                if item.name in skip_names or item.stat().st_size < 10_000 or item.resolve() in excl_resolved:
                    continue
                parts = item.name.split("__", 2)
                if len(parts) == 3:
                    site, rel_name = parts[1], parts[2]
                else:
                    site, rel_name = "extra_fleet", item.name
                rk = f"{site}/{rel_name}"
                if rk not in seen_real:
                    seen_real.add(rk)
                    found.append((site, rel_name, item))

    if prior_local_dir is not None and prior_local_dir.is_dir():
        for p in sorted(prior_local_dir.glob("*.tif")):
            if p.name in skip_names or p.stat().st_size < 10_000 or p.resolve() in excl_resolved:
                continue
            rk = f"GEMSDOEkarage1_prior/{p.name}"
            if rk not in seen_real:
                seen_real.add(rk)
                found.append(("GEMSDOEkarage1_prior", p.name, p))

    scored_dir = ddir / "scored"
    if scored_dir.is_dir():
        for p in sorted(scored_dir.glob("*.tif")):
            if p.resolve() in excl_resolved:
                continue
            rk = f"scored_manifest/{p.name}"
            if rk not in seen_real:
                seen_real.add(rk)
                found.append(("scored_manifest", p.name, p))

    return found


def run_full_fleet_uniqueness_gate(
    continuous_surface: np.ndarray,
    final_dots_f32: np.ndarray,
    final_tif_path: Path,
    foot: np.ndarray,
    *,
    clones_dir: Path = Path("/tmp/research/clones"),
    extra_scored_dir: Path = Path("/tmp/gems_extra_scored"),
    ddir: Path = Path("/tmp/gems_data"),
    prior_local_dir: Path | None = None,
    spearman_ceiling: float = 0.90,
    overlap_3px_ceiling: float = 0.70,
    sample_stride: int = 13,
) -> dict:
    """Check pre-placement continuous surface AND final dots against all 590+ GEMSDOE fleet rasters."""
    cand_sha = hashlib.sha256(final_tif_path.read_bytes()).hexdigest()
    cand_pix_sha = hashlib.sha256(np.where(foot, final_dots_f32, 0.0).astype("<f4").tobytes()).hexdigest()

    cand_dots = (final_dots_f32 >= 0.5) & foot
    n_cand_dots = int(cand_dots.sum())
    assert n_cand_dots > 0, "Candidate has zero dots!"

    # Precompute EDT from candidate dots AND sample footprint indices for fast exact 3-px & Spearman scans
    d_from_cand = distance_transform_edt(~cand_dots)
    cand_within_3px_mask = (d_from_cand <= 3.0) & foot  # ref dots falling inside 3px of candidate

    fp_flat = np.flatnonzero(foot)[::sample_stride]
    s_ys = fp_flat // foot.shape[1]
    s_xs = fp_flat % foot.shape[1]
    surf_sub = continuous_surface[s_ys, s_xs].astype(np.float64)
    dots_sub = final_dots_f32[s_ys, s_xs].astype(np.float64)

    fleet = discover_fleet_tifs(
        clones_dir,
        extra_scored_dir,
        ddir,
        prior_local_dir=prior_local_dir,
        exclude_paths={final_tif_path},
    )

    records = []
    per_focus_site: dict[str, dict] = {}
    unique_pix_hashes: set[str] = set()

    max_surf_spearman = 0.0
    max_surf_ref = ""
    max_dot_spearman = 0.0
    max_dot_ref = ""
    max_discrete_overlap = 0.0
    max_discrete_ref = ""
    exact_hash_matches = []
    non_competing_high_cov = []

    cand_y, cand_x = np.nonzero(cand_dots)

    # Cache computations by pixel-content hash so byte-identical copies across sibling repos are instantaneous
    pix_cache: dict[str, dict] = {}

    for site, rel_p, p in fleet:
        raw_bytes = p.read_bytes()
        f_sha = hashlib.sha256(raw_bytes).hexdigest()
        del raw_bytes
        if f_sha == cand_sha:
            exact_hash_matches.append(f"{site}/{rel_p}")

        try:
            with rasterio.open(p) as ds:
                if ds.shape != foot.shape:
                    continue
                arr = ds.read(1)
        except Exception:
            continue

        arr_clean = np.where(foot & np.isfinite(arr), arr.astype(np.float32), np.float32(0.0))
        p_sha = hashlib.sha256(arr_clean.astype("<f4").tobytes()).hexdigest()
        unique_pix_hashes.add(p_sha)
        if p_sha == cand_pix_sha:
            exact_hash_matches.append(f"{site}/{rel_p}")

        if p_sha not in pix_cache:
            vals_fp = arr_clean[foot]
            rtype = _classify_raster(vals_fp, f"{site}/{rel_p}")
            ref_sub = arr_clean[s_ys, s_xs].astype(np.float64)
            if np.all(ref_sub == ref_sub[0]):
                rho_surf = 0.0
                rho_dots = 0.0
            else:
                r1 = float(spearmanr(surf_sub, ref_sub).statistic)
                r2 = float(spearmanr(dots_sub, ref_sub).statistic)
                rho_surf = 0.0 if np.isnan(r1) else abs(r1)
                rho_dots = 0.0 if np.isnan(r2) else abs(r2)

            ref_pos = (arr_clean > 0.0) & foot
            n_ref = int(ref_pos.sum())
            if n_ref == 0:
                ov_cand_in_ref = 0.0
                ov_ref_in_cand = 0.0
                ov_sym_max = 0.0
            else:
                # Reverse direction (fraction of ref's positive pixels within <=3px of candidate's dots) is O(1) using d_from_cand!
                ov_ref_in_cand = float(cand_within_3px_mask[ref_pos].mean())
                # Forward direction (fraction of candidate's dots within <=3px of ref's positive pixels):
                # Compute exact local 7x7 window check around `cand_y, cand_x` in < 1 ms instead of full-grid EDT!
                hit = np.zeros(cand_y.size, dtype=bool)
                h, w = foot.shape
                for dy in range(-3, 4):
                    for dx in range(-3, 4):
                        if dy * dy + dx * dx > 9:
                            continue
                        ny = np.clip(cand_y + dy, 0, h - 1)
                        nx = np.clip(cand_x + dx, 0, w - 1)
                        hit |= ref_pos[ny, nx]
                ov_cand_in_ref = float(hit.mean())
                ov_sym_max = max(ov_cand_in_ref, ov_ref_in_cand)

            pix_cache[p_sha] = {
                "rtype": rtype,
                "n_pos": n_ref,
                "rho_surf": round(rho_surf, 5),
                "rho_dots": round(rho_dots, 5),
                "ov_cand_in_ref": round(ov_cand_in_ref, 5),
                "ov_ref_in_cand": round(ov_ref_in_cand, 5),
                "ov_sym_max": round(ov_sym_max, 5),
            }

        cm = pix_cache[p_sha]
        rec = {
            "site": site,
            "path": rel_p,
            "file_sha256": f_sha,
            "pixel_sha256": p_sha,
            **cm,
        }
        records.append(rec)

        if cm["rho_surf"] > max_surf_spearman:
            max_surf_spearman = cm["rho_surf"]
            max_surf_ref = f"{site}/{rel_p}"
        if cm["rho_dots"] > max_dot_spearman:
            max_dot_spearman = cm["rho_dots"]
            max_dot_ref = f"{site}/{rel_p}"

        if cm["rtype"] == "discrete_fault_submission":
            # Protocol Rule 1: ">70% of our dots within 3 px of theirs" (and check symmetric max for rigor)
            if cm["ov_cand_in_ref"] > max_discrete_overlap:
                max_discrete_overlap = cm["ov_cand_in_ref"]
                max_discrete_ref = f"{site}/{rel_p}"
        elif cm["ov_cand_in_ref"] > overlap_3px_ceiling:
            non_competing_high_cov.append(
                {
                    "ref": f"{site}/{rel_p}",
                    "type": cm["rtype"],
                    "n_pos": cm["n_pos"],
                    "cand_in_ref_3px": cm["ov_cand_in_ref"],
                    "dot_spearman": cm["rho_dots"],
                }
            )

        if site in FOCUS_9_SITES:
            cur = per_focus_site.get(site)
            if cur is None:
                per_focus_site[site] = {
                    "site": site,
                    "n_rasters_scanned": 1,
                    "max_surface_spearman": cm["rho_surf"],
                    "max_dot_spearman": cm["rho_dots"],
                    "max_discrete_3px_overlap": cm["ov_cand_in_ref"] if cm["rtype"] == "discrete_fault_submission" else 0.0,
                    "closest_discrete_raster": rel_p if cm["rtype"] == "discrete_fault_submission" else "",
                }
            else:
                cur["n_rasters_scanned"] += 1
                cur["max_surface_spearman"] = max(cur["max_surface_spearman"], cm["rho_surf"])
                cur["max_dot_spearman"] = max(cur["max_dot_spearman"], cm["rho_dots"])
                if cm["rtype"] == "discrete_fault_submission" and cm["ov_cand_in_ref"] > cur["max_discrete_3px_overlap"]:
                    cur["max_discrete_3px_overlap"] = cm["ov_cand_in_ref"]
                    cur["closest_discrete_raster"] = rel_p

    passed = (
        len(exact_hash_matches) == 0
        and max_surf_spearman <= spearman_ceiling
        and max_dot_spearman <= spearman_ceiling
        and max_discrete_overlap <= overlap_3px_ceiling
    )

    top_discrete = sorted(
        [r for r in records if r["rtype"] == "discrete_fault_submission"],
        key=lambda x: x["ov_cand_in_ref"],
        reverse=True,
    )[:25]

    return {
        "protocol_rule": "Rule-1-Pre-And-Post-Placement-Duplication-Gate",
        "candidate_tif": final_tif_path.name,
        "candidate_sha256": cand_sha,
        "candidate_pixel_sha256": cand_pix_sha,
        "candidate_dots": n_cand_dots,
        "total_fleet_rasters_scanned": len(records),
        "unique_pixel_rasters_scanned": len(unique_pix_hashes),
        "thresholds": {
            "spearman_abs_max": spearman_ceiling,
            "discrete_3px_overlap_max": overlap_3px_ceiling,
        },
        "exact_hash_matches": exact_hash_matches,
        "max_pre_placement_surface_spearman": round(max_surf_spearman, 5),
        "max_pre_placement_surface_ref": max_surf_ref,
        "max_final_dot_spearman": round(max_dot_spearman, 5),
        "max_final_dot_spearman_ref": max_dot_ref,
        "max_discrete_submission_3px_overlap": round(max_discrete_overlap, 5),
        "max_discrete_submission_ref": max_discrete_ref,
        "non_competing_lattice_or_continuous_rasters_gt_70pct_cov": non_competing_high_cov[:12],
        "per_focus_9_site_summary": [per_focus_site[s] for s in FOCUS_9_SITES if s in per_focus_site],
        "top_25_closest_discrete_submissions": top_discrete,
        "passed": bool(passed),
    }
