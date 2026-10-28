#!/usr/bin/env python3
"""Generate SHA-256-verified 9-Focus-Site comparison JSON and scientific diagnostic maps."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio
from scipy.ndimage import distance_transform_edt
from scipy.stats import spearmanr

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gemskarage1.emitter import compute_spatial_forensics
from gemskarage1.holdout_eval import evaluate_sgmc_off_catalogue, load_reference_masks
from gemskarage1.paths import DOCS_DATA_DIR, DOCS_DIR, DOWNLOADS_DIR, EVIDENCE_DIR, cache_dir, data_dir
from numpy.lib.format import open_memmap

NINE_SITES_SPEC = [
    {
        "site": "GEMSDOE32",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE32",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE32/",
        "tif_path": "/tmp/research/clones/GEMSDOE32/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        "display_file": "gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE32/main/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif",
        "owner_reported_dti": 0.2778,
        "owner_score_label": "0.2778 (OWNER-REPORT — Registry High)",
        "family": "H19-5 Nested Family (B=2.0px Collar)",
        "method_short": "H33-2 B=2.0px Catalogue-Halo-Stripped H27-4/H19-5 Poisson-Disk d=2.8px",
        "exec_summary": (
            "Registry leader (0.2778 OWNER-REPORT). Achieved a +0.0070 gain over GEMSDOE28's 0.2708 baseline "
            "(h27-4-r1-solo-d2-8, 40,199 dots) via a single surgical geometric operation: expanding the Euclidean "
            "exclusion collar around mapped catalogue faults (labels.tif) from B=1.0 px to B=2.0 px (min d_cat = 2.24 px). "
            "That stripped exactly 2,545 near-catalogue halo dots (leaving 37,654 binary 1.0 dots, 0 NaNs, -zeros convention) "
            "whose 300 m kernels overlapped already-saturated public fault traces and added pure 0.2*FP denominator drag. "
            "Also resolved an earlier portal range rejection caused by raw -3.4e38 Float32 sentinels in training_features.tif. "
            "Limitation: still inherits the scarp-dominated H19-5 surface (SGMC off-catalogue raw DTI = 0.093694)."
        ),
    },
    {
        "site": "GEMSDOE36",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE36",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE36/",
        "tif_path": "/tmp/research/clones/GEMSDOE36/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-nan.tif",
        "display_file": "gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-nan.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE36/main/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-nan.tif",
        "owner_reported_dti": 0.2750,
        "owner_score_label": "0.2750 (OWNER-REPORT; KPL36-EXP3: 0.1647)",
        "family": "H19-5 Nested Family (97.4% <=3px w/ GEMSDOE32)",
        "method_short": "H33-2 Core (37,654 dots) + 1,200 Andersonian Geothermal PINN Extension Dots",
        "exec_summary": (
            "Second-highest owner-reported score (0.2750 OWNER-REPORT, 38,854 dots, -nan outside footprint). "
            "Retains 100% of GEMSDOE32's 37,654 H33-2 dots (97.40% <=3 px overlap — near-duplicate of GEMSDOE32) "
            "and appends 1,200 Andersonian stress / geothermal PINN dots. Because those 1,200 extra dots achieved lower "
            "marginal precision than the 0.0556 DTI breakeven threshold at 0.2778, adding them diluted DTI by -0.0028 "
            "(0.2778 -> 0.2750). A separate non-H19-5 experiment in GEMSDOE36 (kpl36-exp3, 44,500 dots) scored 0.1647 "
            "due to over-concentrating 81% of dots near existing fault tips (only 19.3% far-field >1.5 km)."
        ),
    },
    {
        "site": "GEMSDOE28",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE28",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE28/",
        "tif_path": "/tmp/research/clones/GEMSDOE28/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif",
        "display_file": "gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE28/main/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-allfinite.tif",
        "owner_reported_dti": 0.2710,
        "owner_score_label": "0.2710 (OWNER-REPORT; h27-4-solo: 0.2708)",
        "family": "H19-5 Nested Family (95.5% <=3px w/ GEMSDOE32)",
        "method_short": "H27-4 Ridge-Centered Sub-Selection (40,199 dots) + H36-1 Relay Rungs (41,622 dots)",
        "exec_summary": (
            "Breakthrough intermediate stepping-stone (0.2708 on h27-4-r1-solo-d2-8 with 40,199 dots; 0.2710 with "
            "+1,423 H36-1 step-over relay rungs = 41,622 dots, 0 NaNs). Improved +0.0108 over GEMSDOE25's 0.2600 "
            "d2.8 baseline by re-centering Poisson-disk dots directly onto multi-scale Hessian ridge crests rather than "
            "off-axis flank pixels, maximizing the 1 - d/300m triangular kernel height. Still used only a B=1.0 px "
            "catalogue buffer, leaving 2,545 redundant halo dots that GEMSDOE32 later removed to reach 0.2778."
        ),
    },
    {
        "site": "GEMSDOE33",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE33",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE33/",
        "tif_path": "/tmp/research/clones/GEMSDOE33/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
        "display_file": "GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE33/main/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif",
        "owner_reported_dti": 0.2632,
        "owner_score_label": "0.2632 (OWNER-REPORT; S33-1: 0.0963)",
        "family": "H19-5 Nested Family (92.6% <=3px w/ GEMSDOE32)",
        "method_short": "H33d r=3.0px Analog-Tip Stepover Variant (37,068 dots); S33-1 Independent Playas (0.0963)",
        "exec_summary": (
            "Contrasts two extremes: its H19-5 thinned variant h33d-r30 (37,068 dots, 92.64% <=3 px overlap with "
            "GEMSDOE32) scored 0.2632 (OWNER-REPORT), whereas its independent S33-1 geophysical/radiometric model "
            "(37,654 dots) collapsed to 0.0963 because un-vetoed shallow conductivity and uranium anomalies spilled "
            "18.8% of all emitted dots onto flat deep evaporite playas (slope < 2 deg, depth_to_base_surf > 300 m) "
            "and packed 14.3% of dots into redundant >=3-neighbor clumps."
        ),
    },
    {
        "site": "GEMSDOE25",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE25",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE25/",
        "tif_path": "/tmp/research/clones/GEMSDOE25/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
        "display_file": "gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE25/main/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif",
        "owner_reported_dti": 0.2600,
        "owner_score_label": "0.2600 (OWNER-REPORT; H66: 0.0742)",
        "family": "H19-5 Nested Family (88.2% <=3px w/ GEMSDOE32)",
        "method_short": "Poisson-Disk d=2.8px Thinning of H19-5 Surface (44,090 dots); H66 Basin Tracker (0.0742)",
        "exec_summary": (
            "Demonstrated the non-additive max-cover spacing law: increasing Poisson-disk inter-dot spacing on the "
            "H19-5 surface from d=1.5 px (60,069 dots, 0.2477 in GEMSDOE24) to d=2.8 px (44,090 dots) raised live DTI "
            "by +0.0123 to 0.2600 by cutting 15,979 redundant neighbor FP dots inside the 300 m kernel radius. "
            "Conversely, its independent H66 lineament model scored 0.0742 due to 16.4% flat-playa false-positive spill. "
            "Byte-identical d2.8 copies were also mirrored into GEMSDOE30 and GEMSDOE31."
        ),
    },
    {
        "site": "GEMSDOE30",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE30",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE30/",
        "tif_path": "/tmp/research/clones/GEMSDOE30/docs/downloads/gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif",
        "display_file": "gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE30/main/docs/downloads/gems30-MSDB1-edge44090-20261025-e7856ec3f14a.tif",
        "owner_reported_dti": 0.1462,
        "owner_score_label": "0.1462 on MSDB1 (OWNER-REPORT; mirrors 0.2600 d2.8)",
        "family": "Independent Multi-Scale Discontinuity (39.2% <=3px w/ GEMSDOE32)",
        "method_short": "MSDB1 Multi-Scale Discontinuity Bridge (44,090 dots; also mirrors d2.8 0.2600)",
        "exec_summary": (
            "Hosts both a byte-exact mirror of the 0.2600 d2.8 raster (sha256: 91eae1ca...) and a genuinely independent "
            "architecture, MSDB1 (44,090 dots, 0.1462 OWNER-REPORT, 39.18% <=3 px overlap with GEMSDOE32). MSDB1 "
            "underperformed on live DTI because >10% of its dots clustered into >=3-neighbor clumps inside the "
            "non-additive max kernel and lacked 1 m LiDAR gap calibration or Lahontan shoreline vetoing."
        ),
    },
    {
        "site": "GEMSDOE31",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE31",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE31/",
        "tif_path": "/tmp/research/clones/GEMSDOE31/docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif",
        "display_file": "gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE31/main/docs/downloads/gemsdoe31-reference-d28-offcat-44090-20261004-nan.tif",
        "owner_reported_dti": 0.2600,
        "owner_score_label": "0.2600 d2.8 mirror (OWNER-REPORT; union-b unreceipted)",
        "family": "H19-5 Ensemble / Union Family (88.2% <=3px w/ GEMSDOE32)",
        "method_short": "Mirrors d2.8 Baseline (44,090 dots) + Multi-Regime / Union Sweeps",
        "exec_summary": (
            "Explored set-union and regime-split variants across H19-5/H27-4 members (e.g., union-b-p060, 50,023 dots; "
            "pgr31 / h31aa-slfs-flexure, 37,654 dots) above the mirrored 0.2600 d2.8 baseline (sha256: 91eae1ca...). "
            "Audit finding: taking pixel unions of nested H19-5 rasters inflates dot count (>50k) and re-introduces "
            "sub-300 m neighbor collisions between shifted ridge discretizations."
        ),
    },
    {
        "site": "GEMSDOE24",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE24",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE24/",
        "tif_path": "/tmp/research/clones/GEMSDOE24/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-allfinite.tif",
        "display_file": "gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-allfinite.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE24/main/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-allfinite.tif",
        "owner_reported_dti": 0.2477,
        "owner_score_label": "0.2477 on d1.5 (OWNER-REPORT; GVC1: 0.0859)",
        "family": "H19-5 Early Dense Family (88.5% <=3px w/ GEMSDOE32)",
        "method_short": "Dense d=1.5px Dotted H19-5 (60,069 dots, +0.0563 over continuous H19-5 0.1914)",
        "exec_summary": (
            "First proof of the discrete dotting jump: converting continuous H19-5 probabilities (0.1914 live) into "
            "60,069 discrete 1.0 dots at d=1.5 px spacing jumped live DTI by +0.0563 to 0.2477 (OWNER-REPORT) because "
            "DTI's TP uses max_{d<=300m} p*k(d) while FP sums p across all positive pixels. However, d=1.5 px still "
            "packed 2–3 dots inside every 300 m disk (60,069 vs optimal ~38,000). A later GVC1 gravity-volcanic model "
            "scored 0.0859 due to un-thinned cluster clumping and deep-basin spill."
        ),
    },
    {
        "site": "GEMSDOE27",
        "repo_url": "https://github.com/buffedlizard55-lab/GEMSDOE27",
        "pages_url": "https://buffedlizard55-lab.github.io/GEMSDOE27/",
        "tif_path": "/tmp/research/clones/GEMSDOE27/docs/downloads/gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif",
        "display_file": "gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif",
        "download_url": "https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE27/main/docs/downloads/gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite.tif",
        "owner_reported_dti": 0.2250,
        "owner_score_label": "0.2250 on H31-DRCG-WL (OWNER-REPORT; t-v2-d1.5: 0.2449)",
        "family": "Strongest Prior Non-H19-5 Architecture (50.2% <=3px w/ GEMSDOE32)",
        "method_short": "H31 Dual-Regime Cover-Gated GBDT + Walker Lane + CELF d=2.8px (37,654 dots)",
        "exec_summary": (
            "The strongest genuinely independent (non-H19-5) scored model in the prior registry (0.2250 OWNER-REPORT, "
            "37,654 dots, 0 NaNs, only 50.23% <=3 px overlap with GEMSDOE32; earlier H19-5 gap-fill t-v2-d1.5 scored "
            "0.2449). Pioneered cover-gated GBDT + CELF kernel thinning, but used raw 19-band features without "
            "1 m LiDAR gap parity (M_Full vs LiDAR-free M_Sub), without hydrothermal magnetite-destruction troughs, "
            "without Poisson pseudo-gravity volcanic de-confounding, and without INGENIOUS F2mDAB / sinter plumes."
        ),
    },
]


def _overlap_3px(dots_a: np.ndarray, dots_b: np.ndarray) -> float:
    na = int(dots_a.sum())
    if na == 0 or not np.any(dots_b):
        return 0.0
    ya, xa = np.nonzero(dots_a)
    h, w = dots_a.shape
    hit = np.zeros(na, dtype=bool)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            if dy * dy + dx * dx > 9:
                continue
            ny = np.clip(ya + dy, 0, h - 1)
            nx = np.clip(xa + dx, 0, w - 1)
            hit |= dots_b[ny, nx]
    return float(hit.mean())


def main() -> int:
    print("BLOCKED: historical dashboard figures contain superseded uniqueness and causal claims; use scripts/render_site.py instead.", file=sys.stderr)
    return 2
    ddir = data_dir()
    cdir = cache_dir()
    assets_dir = DOCS_DIR / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    refs = load_reference_masks(ddir)
    foot = refs["footprint"]
    labels = refs["labels"]
    sgmc_off_cat = refs["sgmc_off_cat"]
    lidar_valid = refs["lidar_valid"]

    mm = open_memmap(cdir / "karage1_stack_58ch_f32.memmap", mode="r")
    dem = mm[11].astype(np.float32, copy=True)
    depth_base = mm[14].astype(np.float32, copy=True)
    slope_deg = mm[18].astype(np.float32, copy=True)
    del mm

    rc = json.loads((EVIDENCE_DIR / "run_card_hmas_sinter.json").read_text())
    led = json.loads((EVIDENCE_DIR / "experiments_summary.json").read_text())
    uniq = json.loads((EVIDENCE_DIR / "fleet_uniqueness_593.json").read_text())
    canary = json.loads((EVIDENCE_DIR / "leakage_canary_58ch.json").read_text())

    our_tif = DOWNLOADS_DIR / rc["submission_file"]
    with rasterio.open(our_tif) as ds_our:
        our_arr = ds_our.read(1).astype(np.float32)
    our_dots = (our_arr >= 0.5) & foot

    champ_tif = Path(NINE_SITES_SPEC[0]["tif_path"])
    with rasterio.open(champ_tif) as ds_ch:
        ch_raw = ds_ch.read(1)
        champ_arr = np.where(foot & np.isfinite(ch_raw), ch_raw.astype(np.float32), np.float32(0.0))
    champ_dots = (champ_arr >= 0.5) & foot
    _, champ_sgmc_blks = evaluate_sgmc_off_catalogue(champ_arr, foot, labels, sgmc_off_cat)

    fp_sub = np.flatnonzero(foot)[::13]
    sy, sx = fp_sub // foot.shape[1], fp_sub % foot.shape[1]
    our_sub = our_arr[sy, sx].astype(np.float64)
    champ_sub = champ_arr[sy, sx].astype(np.float64)

    site_rows = []
    # Add OUR submission as Row 0 for side-by-side comparison
    our_foren = led["arms"][led["winning_arm"]]["forensics"]
    our_sgmc = led["arms"][led["winning_arm"]]["sgmc"]
    ov_our_champ = _overlap_3px(our_dots, champ_dots)
    rho_our_champ = abs(float(spearmanr(our_sub, champ_sub).statistic))

    site_rows.append(
        {
            "rank_group": "NEW_CANDIDATE",
            "site": "GEMSDOEkarage1 (Ours)",
            "repo_url": "https://github.com/karagemop466-tech/GEMSDOEkarage1",
            "pages_url": "https://karagemop466-tech.github.io/GEMSDOEkarage1/",
            "display_file": rc["submission_file"],
            "download_url": f"downloads/{rc['submission_file']}",
            "zip_download_url": f"downloads/{rc['submission_zip']}",
            "sha256": rc["raster_sha256"],
            "owner_reported_dti": None,
            "owner_score_label": "UNSUBMITTED — READY FOR PORTAL (0/3 weekly slots spent)",
            "gems57_detached_dti": rc["holdout_dti"]["gems57_pooled_hide_v2_detached"]["dti"],
            "gems57_detached_ci95": rc["holdout_dti"]["gems57_pooled_hide_v2_detached"]["ci95"],
            "sgmc_raw_dti": our_sgmc["sgmc_raw_pooled_dti"],
            "sgmc_raw_ci95": our_sgmc["sgmc_raw_ci95"],
            "dots": our_foren["dots"],
            "nan_count": 0,
            "val_min": 0.0,
            "val_max": 1.0,
            "far_field_frac": our_foren["far_field_gt_1p5km_frac"],
            "lidar_gap_frac": our_foren["lidar_gap_frac"],
            "flat_basin_frac": our_foren["flat_deep_basin_frac"],
            "clump3_frac": our_foren["clump_ge3_in_3px_frac"],
            "overlap_3px_with_gemsdoe32": round(ov_our_champ, 4),
            "spearman_with_gemsdoe32": round(rho_our_champ, 5),
            "overlap_3px_with_karage1": 1.0,
            "uniqueness_badge": "UNIQUE PASS (max 60.4% fleet / 58.0% 9-site <= 70%)",
            "family": "H-K1-1 HMAS-SINTER Dual-Cover (Independent Lane)",
            "method_short": "58-ch HMAS Mag-Trough + PPGR + F2mDAB/Sinter Dual-Cover GBDT + d=2.9px Submodular",
            "exec_summary": (
                "Dedicated H-K1-1 (HMAS-SINTER-ENV) architecture built from scratch on the leak-checked 58-channel "
                "stack. Combines negative magnetic tilt-curvature / 3-D analytic-signal magnetite-destruction troughs, "
                "2-D FFT 1/|k| Poisson pseudo-gravity orthogonal basement residuals, 4-block standardized GeoDAWN 214Bi "
                "radon & K/Th alteration crests, and strike-projected INGENIOUS F2mDAB (2,782 probes), Quaternary sinter/breccia "
                "(281 sites), and quartz-geothermometer plumes via Dual-Cover cross-fitting (M_Full inside 75.37% 1m LiDAR + "
                "quantile-matched LiDAR-free M_Sub inside the 24.63% gap) and d=2.9px 300m submodular kernel emission. "
                "Beats BASE_35 on gems57 detached (+0.0106, 95% CI [+0.0056, +0.0158]) and beats the 0.2778 Champion on "
                "off-catalogue USGS SGMC bedrock faults (+0.0184, 95% CI [+0.0016, +0.0355]) with only 46.44% 3-px overlap "
                "with GEMSDOE32 (20,461 of 38,200 dots = 53.56% genuinely novel fault placements >300 m away)."
            ),
        }
    )

    for spec in NINE_SITES_SPEC:
        p = Path(spec["tif_path"])
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        with rasterio.open(p) as ds:
            raw = ds.read(1)
        nan_cnt = int(np.isnan(raw).sum())
        fin_fp = raw[foot & np.isfinite(raw)]
        vmin = float(fin_fp.min()) if fin_fp.size else 0.0
        vmax = float(fin_fp.max()) if fin_fp.size else 0.0
        clean = np.where(foot & np.isfinite(raw), raw.astype(np.float32), np.float32(0.0))
        dots_b = (clean > 0.0) & foot

        sgmc_r, _ = evaluate_sgmc_off_catalogue(clean, foot, labels, sgmc_off_cat, ref_blocks=champ_sgmc_blks)
        foren = compute_spatial_forensics(dots_b, foot, labels, lidar_valid, slope_deg, depth_base)

        ov_ch = 1.0 if spec["site"] == "GEMSDOE32" else _overlap_3px(dots_b, champ_dots)
        ov_k1 = _overlap_3px(our_dots, dots_b)
        sub_v = clean[sy, sx].astype(np.float64)
        rho_ch = 1.0 if spec["site"] == "GEMSDOE32" else abs(float(spearmanr(sub_v, champ_sub).statistic))

        if spec["site"] == "GEMSDOE32":
            ubadge = "REGISTRY REF (0.2778 Champion)"
        elif ov_ch > 0.70:
            ubadge = f"NESTED H19-5 DUPLICATE ({ov_ch*100:.1f}% > 70% w/ GEMSDOE32)"
        else:
            ubadge = f"DISTINCT PRIOR LANE ({ov_ch*100:.1f}% w/ GEMSDOE32)"

        site_rows.append(
            {
                "rank_group": "FOCUS_9",
                "site": spec["site"],
                "repo_url": spec["repo_url"],
                "pages_url": spec["pages_url"],
                "display_file": spec["display_file"],
                "download_url": spec["download_url"],
                "zip_download_url": None,
                "sha256": sha,
                "owner_reported_dti": spec["owner_reported_dti"],
                "owner_score_label": spec["owner_score_label"],
                "gems57_detached_dti": None,
                "gems57_detached_ci95": None,
                "sgmc_raw_dti": sgmc_r["sgmc_raw_pooled_dti"],
                "sgmc_raw_ci95": sgmc_r["sgmc_raw_ci95"],
                "dots": foren["dots"],
                "nan_count": nan_cnt,
                "val_min": round(vmin, 4),
                "val_max": round(vmax, 4),
                "far_field_frac": foren["far_field_gt_1p5km_frac"],
                "lidar_gap_frac": foren["lidar_gap_frac"],
                "flat_basin_frac": foren["flat_deep_basin_frac"],
                "clump3_frac": foren["clump_ge3_in_3px_frac"],
                "overlap_3px_with_gemsdoe32": round(ov_ch, 4),
                "spearman_with_gemsdoe32": round(rho_ch, 5),
                "overlap_3px_with_karage1": round(ov_k1, 4),
                "uniqueness_badge": ubadge,
                "family": spec["family"],
                "method_short": spec["method_short"],
                "exec_summary": spec["exec_summary"],
            }
        )
        print(
            f"[9-site] {spec['site']:10s} | live={spec['owner_reported_dti']} | "
            f"SGMC_raw={sgmc_r['sgmc_raw_pooled_dti']:.6f} | ov_vs_32={ov_ch:.4f} | ov_k1_in_site={ov_k1:.4f}"
        )

    bundle = {
        "generated_at_utc": "2026-10-27T22:05:00Z",
        "competition": {
            "name": "DOE Geospatial Geothermal Exploration Machine Learning (GEMS) Prize",
            "portal_url": "https://www.drivendata.org/competitions/306/competition-doe-gems/",
            "leaderboard_url": "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/",
            "rules_pdf_url": "https://docs.nlr.gov/docs/fy26osti/96647.pdf",
            "openei_gdr_url": "https://gdr.openei.org/submissions/1391",
            "geodawn_doi_url": "https://doi.org/10.5066/P93LGLVQ",
            "live_leaderboard_top1": {"user": "xiaofanhu", "dti": 0.4544, "as_of": "2026-10-27"},
            "live_leaderboard_top5_cutoff": {"user": "No Fault of Our Own", "dti": 0.3566, "as_of": "2026-10-27"},
            "prompt_cited_high": 0.4413,
            "prompt_secondary_benchmark": 0.3195,
            "registry_high": {"site": "GEMSDOE32", "dti": 0.2778, "label": "OWNER-REPORT"},
        },
        "run_card": rc,
        "experiments_summary": led,
        "leakage_canary_top15": sorted(
            canary["channels"], key=lambda x: x["direction_invariant_auc"], reverse=True
        )[:15],
        "uniqueness_summary": {
            "total_fleet_rasters_scanned": uniq["total_fleet_rasters_scanned"],
            "unique_pixel_rasters_scanned": uniq["unique_pixel_rasters_scanned"],
            "max_pre_placement_surface_spearman": uniq["max_pre_placement_surface_spearman"],
            "max_final_dot_spearman": uniq["max_final_dot_spearman"],
            "max_discrete_submission_3px_overlap": uniq["max_discrete_submission_3px_overlap"],
            "max_discrete_submission_ref": uniq["max_discrete_submission_ref"],
            "per_focus_9_site_summary": uniq["per_focus_9_site_summary"],
            "passed": uniq["passed"],
        },
        "comparison_rows": site_rows,
    }
    (DOCS_DATA_DIR / "dashboard_data.json").write_text(json.dumps(bundle, indent=2) + "\n")
    (EVIDENCE_DIR / "nine_site_audit.json").write_text(json.dumps(site_rows, indent=2) + "\n")

    # --- Render Figure 1: Spatial Discovery Map + Dixie Valley / Carson Sink Hydrothermal Zoom ---
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.2), dpi=160, facecolor="#0b1120")
    for ax in axes:
        ax.set_facecolor("#0f172a")

    # Downsample 4x for crisp full-footprint overview
    ds_step = 4
    bg = np.where(foot[::ds_step, ::ds_step], dem[::ds_step, ::ds_step], np.nan)
    axes[0].imshow(bg, cmap="Greys_r", alpha=0.42, vmin=np.nanpercentile(bg, 5), vmax=np.nanpercentile(bg, 95))
    # Highlight 1m LiDAR gap boundary
    gap_m = foot[::ds_step, ::ds_step] & (~lidar_valid[::ds_step, ::ds_step])
    axes[0].contourf(gap_m.astype(float), levels=[0.5, 1.5], colors=["#38bdf8"], alpha=0.10)

    ly, lx = np.nonzero(labels)
    axes[0].scatter(lx[::6] / ds_step, ly[::6] / ds_step, s=0.35, c="#94a3b8", alpha=0.55, label="Mapped Catalogue (labels.tif)")

    d_from_ch = distance_transform_edt(~champ_dots)
    novel_our = our_dots & (d_from_ch > 3.0)
    shared_our = our_dots & (d_from_ch <= 3.0)

    sy_sh, sx_sh = np.nonzero(shared_our)
    sy_nv, sx_nv = np.nonzero(novel_our)
    nov_pct = float(novel_our.sum()) / max(float(our_dots.sum()), 1.0) * 100.0
    axes[0].scatter(sx_sh[::3] / ds_step, sy_sh[::3] / ds_step, s=0.55, c="#38bdf8", alpha=0.65, label=f"Shared w/ GEMSDOE32 <=300m ({int(shared_our.sum()):,} dots, {100.0-nov_pct:.1f}%)")
    axes[0].scatter(sx_nv[::3] / ds_step, sy_nv[::3] / ds_step, s=0.75, c="#f97316", alpha=0.88, label=f"Novel H-K1-1 Blind/Gap Discoveries ({int(novel_our.sum()):,} dots, {nov_pct:.1f}%)")
    axes[0].set_title("Full GeoDAWN Footprint (EPSG:32611, 3,730x3,292 @ 100m)\nBlue Tint = 24.63% 1m-LiDAR Blind Gap Covered by M_Sub-52", color="#f8fafc", fontsize=11, fontweight="bold")
    axes[0].legend(loc="lower left", fontsize=8, facecolor="#0f172a", edgecolor="#334155", labelcolor="#e2e8f0", markerscale=4)
    axes[0].set_xticks([]); axes[0].set_yticks([])

    # Right panel: Zoom on Central Great Basin / Dixie Valley - Carson Sink - Humboldt Salt Marsh (rows 1350..2150, cols 1150..1950)
    r0, r1, c0, c1 = 1350, 2150, 1150, 1950
    bg_z = np.where(foot[r0:r1, c0:c1], dem[r0:r1, c0:c1], np.nan)
    axes[1].imshow(bg_z, cmap="Greys_r", alpha=0.48, vmin=np.nanpercentile(bg_z, 5), vmax=np.nanpercentile(bg_z, 95))
    sg_y, sg_x = np.nonzero(sgmc_off_cat[r0:r1, c0:c1])
    axes[1].scatter(sg_x, sg_y, s=1.4, c="#22c55e", alpha=0.60, label="Off-Catalogue USGS SGMC Bedrock Faults (>300m)")
    ch_y, ch_x = np.nonzero(champ_dots[r0:r1, c0:c1])
    axes[1].scatter(ch_x, ch_y, s=2.2, c="#a855f7", alpha=0.65, label="GEMSDOE32 Champion (0.2778)")
    nv_zy, nv_zx = np.nonzero(novel_our[r0:r1, c0:c1])
    axes[1].scatter(nv_zx, nv_zy, s=3.2, c="#f97316", alpha=0.92, label="Novel H-K1-1 HMAS-SINTER Conduit Dots")
    axes[1].set_title("Central Great Basin / Dixie-Carson Geothermal Corridor (80x80 km Zoom)\nRecovering Off-Catalogue SGMC Bedrock & Blind Basin Faults", color="#f8fafc", fontsize=11, fontweight="bold")
    axes[1].legend(loc="lower right", fontsize=8, facecolor="#0f172a", edgecolor="#334155", labelcolor="#e2e8f0", markerscale=3)
    axes[1].set_xticks([]); axes[1].set_yticks([])

    plt.tight_layout()
    fig.savefig(assets_dir / "karage1_vs_champion_spatial.png", dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)

    # --- Render Figure 2: 3-Experiment Ablation + 9-Focus-Site SGMC vs Uniqueness ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.0, 5.8), dpi=160, facecolor="#0b1120")
    for ax in (ax1, ax2):
        ax.set_facecolor("#0f172a")
        ax.tick_params(colors="#cbd5e1")
        for sp in ax.spines.values():
            sp.set_color("#334155")

    arms_order = ["BASE_35", "EXP2_HMAS_MAXENV_RAW", "EXP3_HMAS_MAXENV_AXIAL29", "EXP1_HMAS_MULT"]
    labels_short = ["BASE-35\n(Template)", "EXP2: MaxEnv\n(d=0 Raw)", "EXP3: MaxEnv\n(d=2.9 Axial)", "EXP1: HMAS-Mult\n(d=2.9 PROMOTED)"]
    x = np.arange(len(arms_order))
    w_bar = 0.26
    v_all = [led["arms"][a]["gems57_per_cell_all"]["dti"] for a in arms_order]
    v_det = [led["arms"][a]["gems57_per_cell_detached"]["dti"] for a in arms_order]
    v_sgm = [led["arms"][a]["sgmc"]["sgmc_raw_pooled_dti"] for a in arms_order]

    ax1.bar(x - w_bar, v_all, width=w_bar, color="#38bdf8", label="gems57-pooled-hide-v2 (all, n=22,641)")
    ax1.bar(x, v_det, width=w_bar, color="#f97316", label="gems57-pooled-hide-v2 (detached, n=22,619)")
    ax1.bar(x + w_bar, v_sgm, width=w_bar, color="#22c55e", label="SGMC Off-Catalogue Raw DTI (n=62,703)")
    ax1.axhline(led["arms"]["CHAMPION_GEMSDOE32_02778"]["sgmc"]["sgmc_raw_pooled_dti"], color="#a855f7", linestyle="--", linewidth=1.6, label="GEMSDOE32 Champion SGMC Raw (0.0937)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels_short, color="#e2e8f0", fontsize=8.5)
    ax1.set_ylabel("Pooled DTI (alpha=0.2, beta=0.8, R=300m)", color="#e2e8f0")
    ax1.set_ylim(0.06, 0.132)
    ax1.set_title("H-K1-1 Pre-Registered 3-Experiment Ablation vs Shared Template & Champion", color="#f8fafc", fontsize=10.5, fontweight="bold")
    ax1.legend(fontsize=7.8, facecolor="#0f172a", edgecolor="#334155", labelcolor="#e2e8f0")

    # Right: Scatter of 9 Focus Sites + Ours: Novelty vs GEMSDOE32 (1 - overlap) vs Off-Catalogue SGMC Raw DTI
    offsets_map = {
        "GEMSDOEkarage1 (Ours)": (-82, -14),
        "GEMSDOE25": (6, 5),
        "GEMSDOE31": (6, -10),
        "GEMSDOE32": (5, -10),
        "GEMSDOE36": (5, 4),
        "GEMSDOE30": (-28, 7),
    }
    for r in site_rows:
        nov = (1.0 - r["overlap_3px_with_gemsdoe32"]) * 100.0
        sg = r["sgmc_raw_dti"]
        is_ours = r["rank_group"] == "NEW_CANDIDATE"
        col = "#22c55e" if is_ours else ("#a855f7" if r["site"] == "GEMSDOE32" else ("#ef4444" if nov < 30.0 else "#38bdf8"))
        sz = 155 if is_ours else 85
        ax2.scatter([nov], [sg], s=sz, c=col, edgecolors="#f8fafc", linewidths=1.2, zorder=4)
        lbl_txt = "GEMSDOEkarage1 (Ours)" if is_ours else r["site"].replace("GEMSDOE", "G")
        ox, oy = offsets_map.get(r["site"], (5, 4))
        ax2.annotate(
            lbl_txt,
            (nov, sg),
            xytext=(ox, oy),
            textcoords="offset points",
            color="#4ade80" if is_ours else "#cbd5e1",
            fontsize=8.3,
            fontweight="bold" if is_ours else "normal",
        )
    ax2.set_xlim(-3, 66)
    ax2.set_ylim(0.067, 0.116)
    ax2.axvline(30.0, color="#ef4444", linestyle=":", linewidth=1.4, label="Protocol Rule 1 Duplication Boundary (>=30% Novelty / <=70% Overlap)")
    ax2.set_xlabel("Spatial Novelty vs GEMSDOE32 Champion (% Dots > 300 m Away)", color="#e2e8f0")
    ax2.set_ylabel("Off-Catalogue USGS SGMC Raw DTI (n=62,703)", color="#e2e8f0")
    ax2.set_title("9 Focus Sites + GEMSDOEkarage1: Off-Catalogue Fault Recovery vs Fleet Novelty", color="#f8fafc", fontsize=10.5, fontweight="bold")
    ax2.legend(loc="upper center", fontsize=7.8, facecolor="#0f172a", edgecolor="#334155", labelcolor="#e2e8f0")

    plt.tight_layout()
    fig.savefig(assets_dir / "ablation_and_nine_sites.png", dpi=160, facecolor=fig.get_facecolor())
    plt.close(fig)
    print("[figures] Saved docs/assets/karage1_vs_champion_spatial.png and docs/assets/ablation_and_nine_sites.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
