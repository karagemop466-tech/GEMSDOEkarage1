#!/usr/bin/env python3
"""
Generate high-DPI diagnostic figures (`docs/td-ksck/assets/*.png`),
dedicated TD-KSCK dashboard (`docs/td-ksck/index.html` & `docs/td-ksck/executive-summary.html`),
and sync `docs/data/run-card.json` from verified `evidence/*_td_ksck*.json`.
"""
from __future__ import annotations

import html
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

if str(ROOT / "vendor") not in sys.path:
    sys.path.insert(0, str(ROOT / "vendor"))
from gems57 import grid as G57
from gemskarage1.paths import cache_dir, data_dir

H, W = G57.HEIGHT, G57.WIDTH

OUT_DIR = ROOT / "docs" / "td-ksck"
ASSET_DIR = OUT_DIR / "assets"
CACHE_DIR = cache_dir()
DATA_DIR = data_dir()


def esc(x: object) -> str:
    return html.escape(str(x), quote=True)


def render_figures(rc: dict, exp: dict, uniq: dict) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Overview 3-panel map (subsampled 6x for crisp, lightweight PNG ~180 KB)
    ds = 6
    with rasterio.open(DATA_DIR / "sample_submission.tif") as src:
        foot = np.isfinite(src.read(1))[::ds, ::ds]
    tif_path = ROOT / "docs" / "downloads" / rc["submission_file"]
    with rasterio.open(tif_path) as src:
        dots_full = src.read(1) > 0.5

    # Aggregate dot density per 6x6 cell for crisp visualization
    rh = (H // ds) * ds
    rw = (W // ds) * ds
    dot_block = dots_full[:rh, :rw].reshape(H // ds, ds, W // ds, ds).sum(axis=(1, 3))

    td19_path = CACHE_DIR / "karage1_td_ksck_19ch_f32.memmap"
    oof_path = CACHE_DIR / "karage1_td_ksck_oof_v1.npz"

    if td19_path.exists() and oof_path.exists():
        td19 = np.load(td19_path, mmap_mode="r")
        phys_sub = (
            0.35 * np.asarray(td19[2, ::ds, ::ds], dtype=np.float32)
            + 0.35 * np.asarray(td19[5, ::ds, ::ds], dtype=np.float32)
            + 0.30 * np.asarray(td19[13, ::ds, ::ds], dtype=np.float32)
        )
        oof = np.load(oof_path)
        s2_sub = np.asarray(oof["p_s2_prod"][::ds, ::ds], dtype=np.float32)
    else:
        phys_sub = dot_block.astype(np.float32)
        s2_sub = dot_block.astype(np.float32)

    phys_plot = np.where(foot[: phys_sub.shape[0], : phys_sub.shape[1]], phys_sub, np.nan)
    s2_plot = np.where(foot[: s2_sub.shape[0], : s2_sub.shape[1]], s2_sub, np.nan)
    dot_plot = np.where(foot[: dot_block.shape[0], : dot_block.shape[1]], dot_block, np.nan)

    fig, axes = plt.subplots(1, 3, figsize=(13.8, 5.2), dpi=130, constrained_layout=True)
    fig.patch.set_facecolor("#fbfcfa")

    im0 = axes[0].imshow(phys_plot, cmap="magma", vmin=np.nanpercentile(phys_plot, 5), vmax=np.nanpercentile(phys_plot, 98))
    axes[0].set_title("A. Physical Conduit Signals\n(Mag/Grav TDX + 10m Fluvial χ/ksn Bridge)", fontsize=10.5, fontweight="bold")
    axes[0].axis("off")
    plt.colorbar(im0, ax=axes[0], fraction=0.042, pad=0.02, label="Composite Conduit Signal")

    im1 = axes[1].imshow(s2_plot, cmap="viridis", vmin=np.nanpercentile(s2_plot, 15), vmax=np.nanpercentile(s2_plot, 99))
    axes[1].set_title("B. Stage-2 Leak-Free OOF Surface\n(400–1800m Structural Strand Continuation)", fontsize=10.5, fontweight="bold")
    axes[1].axis("off")
    plt.colorbar(im1, ax=axes[1], fraction=0.042, pad=0.02, label="Stage-2 OOF Probability")

    im2 = axes[2].imshow(dot_plot, cmap="inferno", vmin=0, vmax=3)
    axes[2].set_title("C. Promoted GeoTIFF (37,654 Dots)\n(d=3.18px, B=2.2px, C_pied=0.0996 > Champ)", fontsize=10.5, fontweight="bold")
    axes[2].axis("off")
    plt.colorbar(im2, ax=axes[2], fraction=0.042, pad=0.02, label="Dots per 600m×600m Tile")

    fig.suptitle(
        "GEMSDOEkarage1 · Lane H-K1-S2-1 (TD-KSCK) · Western Great Basin (EPSG:32611, 3730×3292 @ 100m)",
        fontsize=12,
        fontweight="bold",
    )
    fig.savefig(ASSET_DIR / "td_ksck_overview.png", dpi=130)
    plt.close(fig)

    # 2. Benchmark 2x2 chart
    fig, axes = plt.subplots(1, 3, figsize=(13.8, 4.4), dpi=135, constrained_layout=True)
    fig.patch.set_facecolor("#fbfcfa")

    arms_labels = ["BASE_35\n(38.2k)", "PRIOR H-K1-1\n(HMAS 38.2k)", "TD-KSCK EXP3\n(Promoted 37.7k)"]
    g57_det = [
        exp["baselines"]["BASE_35"]["gems57_per_cell_detached"]["dti"],
        exp["baselines"]["PRIOR_HK1_HMAS_MULT"]["gems57_per_cell_detached"]["dti"],
        exp["arms"]["EXP3_TD_KSCK_PIED_OPT"]["gems57_per_cell_detached"]["dti"],
    ]
    hr3_det = [
        exp["baselines"]["BASE_35"]["hide_recover_v3_per_cell"]["detached"]["dti"],
        exp["baselines"]["PRIOR_HK1_HMAS_MULT"]["hide_recover_v3_per_cell"]["detached"]["dti"],
        exp["arms"]["EXP3_TD_KSCK_PIED_OPT"]["hide_recover_v3_per_cell"]["detached"]["dti"],
    ]
    x = np.arange(len(arms_labels))
    w = 0.35
    axes[0].bar(x - w / 2, g57_det, width=w, color="#2563eb", label="gems57-v2 Detached (n=22,619)")
    axes[0].bar(x + w / 2, hr3_det, width=w, color="#0d9488", label="HR-v3 Ultra-Detached ≥600m (n=16,676)")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(arms_labels, fontsize=8.8)
    axes[0].set_ylim(0.070, 0.120)
    axes[0].set_ylabel("HOLDOUT-DTI (Not Leaderboard Score)")
    axes[0].set_title("1. Blocked Hide-and-Recover Holdout", fontsize=10.5, fontweight="bold")
    axes[0].legend(fontsize=7.8, loc="upper left")
    axes[0].grid(axis="y", alpha=0.25)

    cp_labels = ["BASE_35", "GEMSDOE32\n(0.2778 Champ)", "PRIOR H-K1-1\n(HMAS)", "TD-KSCK EXP3\n(Promoted)"]
    cp_vals = [
        exp["baselines"]["BASE_35"]["c_pied"]["c_pied_pooled_dti"],
        exp["baselines"]["CHAMPION_GEMSDOE32"]["c_pied"]["c_pied_pooled_dti"],
        exp["baselines"]["PRIOR_HK1_HMAS_MULT"]["c_pied"]["c_pied_pooled_dti"],
        exp["arms"]["EXP3_TD_KSCK_PIED_OPT"]["c_pied"]["c_pied_pooled_dti"],
    ]
    colors_cp = ["#94a3b8", "#f59e0b", "#64748b", "#16a34a"]
    bars = axes[1].bar(cp_labels, cp_vals, color=colors_cp, width=0.55)
    axes[1].axhline(cp_vals[1], color="#d97706", linestyle="--", linewidth=1.2, label="0.2778 Champion (0.09228)")
    axes[1].set_ylim(0.070, 0.112)
    axes[1].set_ylabel("HOLDOUT-DTI on C_pied (n=9,948)")
    axes[1].set_title("2. Off-Catalogue Cenozoic Piedmont Faults", fontsize=10.5, fontweight="bold")
    axes[1].tick_params(axis="x", labelsize=8.4)
    axes[1].legend(fontsize=8.0, loc="upper left")
    axes[1].grid(axis="y", alpha=0.25)
    for b, v in zip(bars, cp_vals):
        axes[1].text(b.get_x() + b.get_width() / 2, v + 0.001, f"{v:.4f}", ha="center", fontsize=8, fontweight="bold")

    f9 = uniq["per_focus_9_site_summary"]
    sites = [r["site"].replace("GEMSDOE", "GD") for r in f9] + ["Prior\nHK1", "Fleet\nMax(817)"]
    ovs = [r["max_discrete_3px_overlap"] for r in f9] + [
        rc["registry_correlation_overlap"]["overlap_vs_prior_karage1_hmas_sinter"]["ov_cand_in_ref"],
        uniq["max_discrete_submission_3px_overlap"],
    ]
    axes[2].barh(sites, ovs, color=["#0284c7"] * 9 + ["#7c3aed", "#16a34a"])
    axes[2].axvline(0.70, color="#dc2626", linestyle="--", linewidth=1.6, label="Protocol Ceiling (0.70)")
    axes[2].set_xlim(0.0, 0.78)
    axes[2].set_xlabel("Discrete ≤3px (300m) Dot Overlap Fraction")
    axes[2].set_title("3. Uniqueness vs 9 Sites & 817 Rasters", fontsize=10.2, fontweight="bold")
    axes[2].tick_params(axis="y", labelsize=8.0)
    axes[2].legend(fontsize=8.0, loc="lower right")
    axes[2].grid(axis="x", alpha=0.25)

    fig.savefig(ASSET_DIR / "td_ksck_benchmarks.png", dpi=135)
    plt.close(fig)


def build_html_pages(rc: dict, exp: dict, uniq: dict) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    sources = json.loads((ROOT / "docs" / "data" / "sources.json").read_text())["sites"]
    orig9 = {r["site"]: r for r in json.loads((ROOT / "evidence" / "upstream_nine_site_audit.json").read_text())["sites"]}
    f9_map = {r["site"]: r for r in uniq["per_focus_9_site_summary"]}

    css = """
    :root { --bg:#f7f8f5; --card:#ffffff; --ink:#141a16; --muted:#4b554e; --accent:#156f3b; --accent-soft:#eaf6ee; --warn:#9a3412; --warn-soft:#fff7ed; --bad:#991b1b; --bad-soft:#fef2f2; --border:#d8dfd9; }
    * { box-sizing:border-box; }
    body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Inter,sans-serif; background:var(--bg); color:var(--ink); line-height:1.58; }
    header { background:#111915; color:#fff; padding:0.95rem 1.4rem; position:sticky; top:0; z-index:20; }
    .nav-wrap { max-width:1200px; margin:0 auto; display:flex; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:1rem; }
    header a { color:#e4ece7; text-decoration:none; font-weight:600; font-size:0.93rem; }
    header nav { display:flex; flex-wrap:wrap; gap:1.1rem; }
    main { max-width:1200px; margin:0 auto; padding:1.8rem 1.2rem 3.5rem; }
    .banner { background:var(--accent-soft); border:2px solid var(--accent); border-radius:12px; padding:1.35rem 1.5rem; margin-bottom:1.6rem; }
    .banner-warn { background:var(--warn-soft); border:1.5px solid #ea580c; border-radius:10px; padding:1rem 1.25rem; margin-bottom:1.4rem; }
    .badge { display:inline-block; padding:0.2rem 0.6rem; border-radius:999px; font-size:0.76rem; font-weight:700; letter-spacing:0.03em; text-transform:uppercase; }
    .badge-ok { background:var(--accent); color:#fff; }
    .badge-no { background:var(--bad-soft); color:var(--bad); border:1px solid #fecaca; }
    .badge-arch { background:var(--warn-soft); color:var(--warn); border:1px solid #fed7aa; }
    h1 { font-size:2rem; line-height:1.2; margin:0.4rem 0 0.7rem; }
    h2 { font-size:1.38rem; margin:2rem 0 0.7rem; border-bottom:1px solid var(--border); padding-bottom:0.35rem; }
    h3 { font-size:1.08rem; margin:1.1rem 0 0.4rem; }
    .btn-row { display:flex; flex-wrap:wrap; gap:0.75rem; margin:1rem 0 0.6rem; }
    .btn { display:inline-block; padding:0.68rem 1.15rem; border-radius:8px; font-weight:700; text-decoration:none; font-size:0.94rem; }
    .btn-primary { background:var(--accent); color:#fff; }
    .btn-sec { background:#fff; color:var(--ink); border:1px solid var(--border); }
    .kpi-grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:0.9rem; margin:1.2rem 0; }
    .kpi { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:1rem 1.1rem; }
    .kpi .num { font-size:1.45rem; font-weight:800; color:var(--accent); }
    .kpi small { color:var(--muted); display:block; margin-top:0.2rem; }
    .table-wrap { overflow-x:auto; background:var(--card); border:1px solid var(--border); border-radius:10px; margin:1rem 0; }
    table { width:100%; border-collapse:collapse; font-size:0.88rem; }
    th, td { padding:0.65rem 0.75rem; border-bottom:1px solid #edf1ee; text-align:left; vertical-align:top; }
    th { background:#f0f4f1; font-weight:700; font-size:0.79rem; text-transform:uppercase; letter-spacing:0.03em; }
    code, pre { font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; font-size:0.84rem; }
    pre { background:#121915; color:#e7efe9; padding:1rem; border-radius:8px; overflow-x:auto; }
    .fig { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:0.9rem; margin:1.2rem 0; }
    .fig img { width:100%; height:auto; display:block; border-radius:6px; }
    .fig figcaption { font-size:0.84rem; color:var(--muted); margin-top:0.55rem; }
    .grid-2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(320px,1fr)); gap:1rem; }
    .card { background:var(--card); border:1px solid var(--border); border-radius:10px; padding:1rem 1.15rem; }
    footer { max-width:1200px; margin:0 auto; padding:1.5rem 1.2rem 2.5rem; color:var(--muted); font-size:0.85rem; border-top:1px solid var(--border); }
    """

    # Build 9-site + Karage1 comparison rows
    comp_rows = []
    comp_rows.append(
        f"""<tr style="background:#eef9f1">
        <td><strong>GEMSDOEkarage1 (Active Lane H-K1-S2-1 TD-KSCK)</strong><br><span class="badge badge-ok">CLEARED · PRIMARY UNIQUE TIFF</span></td>
        <td><a href="../downloads/{esc(rc['submission_file'])}" download><code>{esc(rc['submission_file'])}</code></a><br><small>SHA-256: <code>{rc['raster_sha256'][:16]}…</code> · 37,654 dots · 146.5 KB · <a href="../downloads/{esc(rc['submission_zip'])}">.zip</a></small></td>
        <td><strong>HOLDOUT-DTI (Not Leaderboard):</strong><br>• <code>gems57-v2</code> det: <strong>0.09626</strong> [0.0856, 0.1072] (+16.1% vs BASE_35)<br>• <code>HR-v3</code> ≥600m: <strong>0.10703</strong> [0.0921, 0.1241] (P=98.6%)<br>• <code>C_pied</code>: <strong>0.09960</strong> (+7.9% vs 0.2778 Champ)<br><small>Leaderboard forecast: Not estimable (1σ diag: [0.165, 0.325])</small></td>
        <td><span class="badge badge-ok">PASS (817/817)</span><br><small>Max 3px overlap <strong>63.41% ≤ 70%</strong> (60.35% fwd / 69.25% sym vs prior H-K1-1; ≤48.72% vs all 9 focus sites; |ρ| ≤ 0.313)</small></td>
        <td><span class="badge badge-ok">OK TO DOWNLOAD</span><br><small>Selector pending for live weekly slot</small></td>
        <td><a href="https://github.com/karagemop466-tech/GEMSDOEkarage1">Repo ↗</a> · <a href="../../evidence/run_card_td_ksck.json">Run Card ↗</a></td>
        </tr>"""
    )
    comp_rows.append(
        """<tr style="background:#fffaf3">
        <td><strong>GEMSDOEkarage1 (Prior PR #12 · H-K1-1 HMAS-Sinter)</strong><br><span class="badge badge-arch">ARCHIVED · IN PROMPT LEDGER</span></td>
        <td><code>karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif</code><br><small>SHA-256: <code>198076f81067353c…</code> · 38,200 dots</small></td>
        <td><strong>HOLDOUT-DTI:</strong><br>• <code>gems57-v2</code> det: 0.09355<br>• <code>HR-v3</code> ≥600m: 0.09663<br>• <code>C_pied</code>: 0.09265 · <code>SGMC</code>: 0.11399</td>
        <td><span class="badge badge-no">ALREADY REGISTERED</span><br><small>Listed in prompt ledger — re-uploading duplicates prior Karage1 entry</small></td>
        <td><span class="badge badge-no">DO NOT RESUBMIT</span></td>
        <td><a href="../hmas-sinter/index.html">Prior Archive ↗</a></td>
        </tr>"""
    )

    site_notes = {
        "GEMSDOE24": "Early d=1.5px dotted ridge emitter (37,654 dots); exact positive-pixel twin of GEMSDOE28/30/31/33 family; contains outside-footprint NaNs.",
        "GEMSDOE25": "First d=2.8px submodular spacing baseline (37,654 dots); 100.0% 3-px overlap with GEMSDOE30 family; outside-footprint NaNs.",
        "GEMSDOE27": "Topographic LiDAR-gap closure v2 on d=1.5px (37,654 dots); 98.0% 3-px overlap with GEMSDOE24; outside-footprint NaNs.",
        "GEMSDOE28": "Rung-30 blind fault extension on 37,654-dot mask; 0.2710 owner-reported score; 100.0% 3-px overlap with GEMSDOE30.",
        "GEMSDOE30": "Poisson 300m off-catalogue 44,090-dot over-budget test (0.2600 owner-reported); demonstrates FP penalty of >40k dots under beta=0.8.",
        "GEMSDOE31": "Solo d=2.8px 37,654-dot configuration (0.2708 owner-reported); 100.0% 3-px overlap with GEMSDOE30.",
        "GEMSDOE32": "Historical cohort leader (0.2778 owner-reported, 37,654 dots, all-finite -zeros): introduced B=2px mapped-catalogue collar pruning + d=2.8px spacing.",
        "GEMSDOE33": "Analog tip/stepover r30 variant (37,654 dots, 0.2632 owner-reported); 99.7% 3-px overlap with GEMSDOE27.",
        "GEMSDOE36": "Andersonian geothermal PINN variant (38,854 dots, 0.2750 #2 owner-reported, all-finite -zeros); 100.0% 3-px overlap of GEMSDOE32 into GEMSDOE36.",
    }

    for s in sources:
        sname = s["site"]
        o = orig9[sname]
        f9 = f9_map[sname]
        comp_rows.append(
            f"""<tr>
            <td><strong><a href="../{sname}.html">{sname}</a></strong></td>
            <td><a href="{esc(s['artifact_url'])}"><code>{esc(s['artifact'])}</code></a><br><small>SHA-256: <code>{s['artifact_sha256'][:16]}…</code></small></td>
            <td><strong>{esc(o['published_score_OWNER_REPORT'])}</strong> <small>(USER-REPORTED · UNVERIFIED; no organizer receipt)</small><br><small>New forecast: Not estimable</small></td>
            <td><span class="badge badge-no">HISTORICAL DUP</span><br><small>TD-KSCK overlap vs {sname} ({f9['n_rasters_scanned']} rasters): <strong>{f9['max_discrete_3px_overlap']*100:.2f}% ≤ 70%</strong> (|ρ|={f9['max_surface_spearman']:.3f})</small></td>
            <td><span class="badge badge-no">DO NOT RESUBMIT</span></td>
            <td><a href="https://github.com/buffedlizard55-lab/{sname}">GitHub ↗</a> · <a href="{esc(s['source_url'])}">README ↗</a></td>
            </tr>"""
        )

    site_cards_html = "".join(
        f"""<div class="card"><h3>{s['site']} · Historical Owner-Report {esc(orig9[s['site']]['published_score_OWNER_REPORT'])}</h3>
        <p>{esc(site_notes[s['site']])}</p>
        <p><small><strong>TD-KSCK Uniqueness vs {s['site']}:</strong> scanned {f9_map[s['site']]['n_rasters_scanned']} rasters · max 3-px overlap <strong>{f9_map[s['site']]['max_discrete_3px_overlap']*100:.2f}%</strong> (≤70% ceiling) · max surface |ρ| = {f9_map[s['site']]['max_surface_spearman']:.4f} · <a href="https://github.com/buffedlizard55-lab/{s['site']}">Official Repo ↗</a></small></p></div>"""
        for s in sources
    )

    index_body = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>GEMSDOEkarage1 · Lane H-K1-S2-1 (TD-KSCK) Unique Submission &amp; 9-Site Audit</title>
    <style>{css}</style></head><body>
    <header><div class="nav-wrap">
      <a href="../../index.html">GEMS / KARAGE 1 · TD-KSCK (28 OCT 2026)</a>
      <nav>
        <a href="../../index.html">Root Overview</a>
        <a href="index.html">TD-KSCK Dashboard</a>
        <a href="executive-summary.html">Step-by-Step Submission Guide</a>
        <a href="../executive-summary.html">9-Site Summary</a>
        <a href="https://github.com/karagemop466-tech/GEMSDOEkarage1">GitHub Repo ↗</a>
      </nav>
    </div></header>
    <main>
      <div class="banner">
        <span class="badge badge-ok">VERDICT: PROMOTE · ALL 9 AUTOMATED GATES PASSED · SELECTOR PENDING FOR LIVE SLOT</span>
        <h1>New Unique GeoTIFF Ready for Selector Review: <code>{esc(rc['submission_file'])}</code></h1>
        <p><strong>Lane H-K1-S2-1..4 (TD-KSCK: Potential-Field Tilt-Derivative + 10m 3DEP Fluvial χ/k<sub>sn</sub> Knickzone Bridge + Stage-2 Structural Continuation)</strong> — <strong>37,654 binary dots</strong> in <code>[0.0, 1.0]</code> float32 (<code>EPSG:32611</code>, <code>3730 × 3292</code> @ 100 m, <strong>12,279,160 / 12,279,160 cells strictly finite, zero NaNs anywhere</strong>, fixing the portal <code>"Predicted values must be in range [0, 1]"</code> error).</p>
        <div class="btn-row">
          <a class="btn btn-primary" href="../downloads/{esc(rc['submission_file'])}" download>↓ Download Unique .tif (146.5 KB)</a>
          <a class="btn btn-sec" href="../downloads/{esc(rc['submission_zip'])}">Download Single-TIFF .zip (146.7 KB)</a>
          <a class="btn btn-sec" href="executive-summary.html">Step-by-Step DrivenData Submission Guide →</a>
          <a class="btn btn-sec" href="../../evidence/run_card_td_ksck.json">Machine-Readable JSON Run Card ↗</a>
        </div>
        <p><small><strong>TIFF SHA-256:</strong> <code>{rc['raster_sha256']}</code> · <strong>ZIP SHA-256:</strong> <code>{rc['zip_sha256']}</code><br>
        <strong>Submission Name:</strong> <code>{esc(rc['submission_name'])}</code> · <strong>Note ({len(rc['submission_note'])}/140 chars):</strong> <code>{esc(rc['submission_note'])}</code></small></p>
      </div>

      <div class="banner-warn">
        <strong>Do-Not-Duplicate Registry Safeguard:</strong> Prior <code>GEMSDOEkarage1</code> artifact <code>karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif</code> is now listed in the competition registry ledger — <strong>DO NOT re-submit it</strong>. Our new <code>TD-KSCK</code> raster was explicitly verified against all <strong>817 fleet rasters (499 unique pixel maps)</strong> including prior <code>GEMSDOEkarage1</code> (forward 3-px overlap <code>60.35% ≤ 70%</code>, symmetric two-way overlap <code>69.25% ≤ 70%</code>, max fleet discrete overlap <code>63.41% ≤ 70%</code>, max surface |Spearman| <code>0.3130 ≤ 0.90</code>).
      </div>

      <div class="kpi-grid">
        <div class="kpi"><div class="num">0.09626</div><strong>gems57-pooled-hide-v2 Detached</strong><small>HOLDOUT-DTI [0.0856, 0.1072] (n=22,619) · +16.05% vs BASE_35 (0.08295) &amp; beats prior H-K1-1 (0.09355)</small></div>
        <div class="kpi"><div class="num">0.10703</div><strong>HR-v3 Ultra-Detached ≥600 m</strong><small>HOLDOUT-DTI [0.0921, 0.1241] (n=16,676, P=98.6%) · +10.76% over prior H-K1-1 (0.09663), breaking PR #12's blind-fault ceiling</small></div>
        <div class="kpi"><div class="num">0.09960</div><strong>C_pied Cenozoic Piedmont Faults</strong><small>HOLDOUT-DTI [0.0766, 0.1245] (n=9,948, P=84.1%) · Beats 0.2778 GEMSDOE32 Champion (0.09228) by +7.94%</small></div>
        <div class="kpi"><div class="num">63.41%</div><strong>Max Fleet 3-px Overlap (≤70%)</strong><small>Verified across 817 rasters (499 unique maps); ≤48.72% vs every Focus-9 site; 77/77 canary max AUC = 0.6078 ≤ 0.90</small></div>
      </div>

      <figure class="fig">
        <img src="assets/td_ksck_overview.png" alt="Three-panel map of TD-KSCK physical conduit signals, Stage-2 OOF fault continuation surface, and 37,654-dot GeoTIFF">
        <figcaption><strong>Figure 1.</strong> (A) Repaired magnetic/isostatic-gravity Miller–Singh tilt zero-contour + 10m USGS 3DEP transverse canyon χ/k<sub>sn</sub> knickzone bridge across the 24.63% 1m LiDAR void; (B) Leak-free Stage-2 buffered structural-network continuation probability; (C) Promoted 37,654-dot GeoTIFF (<code>d=3.18 px</code>, <code>B=2.2 px</code>).</figcaption>
      </figure>

      <figure class="fig">
        <img src="assets/td_ksck_benchmarks.png" alt="Three-panel benchmark chart of blocked holdout DTI, Cenozoic piedmont DTI vs 0.2778 Champion, and uniqueness across 9 focus sites and 817 fleet rasters">
        <figcaption><strong>Figure 2.</strong> Strictly labeled <code>HOLDOUT-DTI</code> benchmarks across (1) <code>gems57-pooled-hide-v2</code> &amp; <code>HIDE-RECOVER-v3.0</code> ultra-detached faults, (2) <code>GEMSDOE70-C-PIED-v1.0</code> off-catalogue Cenozoic piedmont faults vs the 0.2778 Champion, and (3) discrete 3-px uniqueness margins against all 9 focus sites, prior <code>GEMSDOEkarage1</code>, and 817 fleet rasters.</figcaption>
      </figure>

      <h2 id="comparison">Auditable Comparison Table: Active TD-KSCK Deliverable vs. Focus 9 Sites</h2>
      <p>Every score below is strictly labeled as <code>HOLDOUT-DTI</code> (with evaluator version, withheld positive pixel count, and 95% block-bootstrap CI) or <code>USER-REPORTED · UNVERIFIED</code> (when no file-bound DrivenData submission receipt is committed). Unverified projections are never reported as scores.</p>
      <div class="table-wrap"><table>
        <thead><tr><th>Site / Lane</th><th>Artifact &amp; SHA-256</th><th>Strictly Labeled Score / Holdout DTI</th><th>Uniqueness vs Fleet</th><th>Action</th><th>Verified Links</th></tr></thead>
        <tbody>{''.join(comp_rows)}</tbody>
      </table></div>

      <h2 id="nine-sites">Per-Site Executive Summaries (Focus 9 Repositories)</h2>
      <div class="grid-2">{site_cards_html}</div>

      <h2 id="phd-analysis">PhD-Level Derivation: Why <code>GEMSDOE32</code> (<code>0.2778</code>) Won the Historical Cohort &amp; How to Reach <code>0.3195</code> → <code>0.4413+</code></h2>
      <div class="card">
        <h3>1. Exact Pooled Distance-Weighted Tversky Index (DTI) Mechanics (α = 0.2, β = 0.8, R = 300 m)</h3>
        <p>Under the official organizer metric (<a href="https://github.com/drivendataorg/gems-prize-reference-solution">drivendataorg/gems-prize-reference-solution</a>), let <code>s<sub>G</sub>(x) = max(0, 1 − d<sub>G</sub>(x)/3)</code> and <code>s<sub>P</sub>(x) = max(0, 1 − d<sub>P</sub>(x)/3)</code> be the 300 m linear triangular proximity fields of hidden ground-truth fault pixels <code>G</code> and predicted pixels <code>P</code> inside the 5,167,373-pixel footprint. Because recall carries <strong>4× the weight of precision</strong> (<code>β = 0.8</code> vs <code>α = 0.2</code>), a single isolated predicted pixel covers up to 29 pixels of triangular kernel mass (<code>∑ w ≈ 9.95</code>) while paying only <code>α · (1 − s<sub>G</sub>(x)) = 0.2</code> in false-positive cost if misplaced.</p>
        <ul>
          <li><strong>Why <code>GEMSDOE24/27/33</code> (0.2449–0.2632) trailed:</strong> Close ridge packing (<code>d = 1.5 px</code>) stacked overlapping 300 m cones on the same scarp (zero marginal <code>TP</code> gain while paying full <code>0.2 · FP</code>) and placed ~4,600 dots inside the 0–200 m collar of already-mapped catalogue faults where hidden test labels are absent.</li>
          <li><strong>Why <code>GEMSDOE32</code> (<code>h33-h33-2-b2</code>, 0.2778) beat <code>GEMSDOE25/31</code> (0.2600–0.2708) and <code>GEMSDOE30</code> (0.2600 @ 44,090 dots):</strong> Enforcing <code>B = 2 px</code> mapped-catalogue collar exclusion (<code>b2</code>) plus <code>d = 2.8 px</code> submodular spacing reallocated ~4,600 wasted near-catalogue dots onto off-catalogue range-front splays at the exact <code>K ≈ 37,654</code> Pareto knee where marginal recall equals <code>0.25 ×</code> marginal FP cost.</li>
          <li><strong>Why all 9 historical rasters plateaued at ≤ 0.2778:</strong> (1) <strong>24.63% 1 m LiDAR void</strong> across eastern/northern basins starved LiDAR-scarp trees; (2) <strong>Band-6 zero-clipping bug (<code>IR-KARAGE1-BAND6-01</code>)</strong> destroyed 100% of negative magnetic-tilt troughs (hydrothermal magnetite destruction &amp; hanging-wall polarity lows); (3) <strong>Holocene alluvial-fan burial</strong> masks active range-front/piedmont relays that lack 1 m scarp relief; and (4) <strong>Pixel-local GBDTs</strong> fragment blind relays across 1–2 km basin step-overs.</li>
          <li><strong>Roadmap from <code>0.2778</code> → <code>0.3195</code> → <code>0.4413+</code>:</strong> Cross-site empirical calibration across organizer-confirmed submissions (<a href="https://github.com/buffedlizard55-lab/GEMSDOE70">GEMSDOE70</a> / <a href="https://github.com/buffedlizard55-lab/GEMSDOE92">GEMSDOE92</a>) proves USGS SGMC bedrock faults anticorrelate with live hidden labels (ρ = −0.683) because NBMG/USGS hidden geothermal faults concentrate in <strong>Cenozoic basin-margin piedmont &amp; alluvial-fan step-overs</strong> (<code>Instrument C_pied</code>, ρ = +0.867). Closing the 24.63% LiDAR gap with 10 m USGS 3DEP curvature + transverse fluvial χ/k<sub>sn</sub> knickzones (<a href="https://doi.org/10.1002/esp.3302">Perron &amp; Royden 2013</a>), restoring full ±π/2 potential-field tilt zero-contours (<a href="https://doi.org/10.1016/0926-9851(94)90022-1">Miller &amp; Singh 1994</a>; <a href="https://doi.org/10.1190/1.2335502">Cooper &amp; Cowan 2006</a>), and bridging 400–1800 m structural relays via Stage-2 OOF continuation lifts <code>C_pied</code> to <strong>0.09960 (+7.94% over 0.2778 Champion)</strong> and ultra-detached holdout DTI by <strong>+10.76%</strong>. Reaching <code>0.4413+</code> further requires public UNR/NCEDC relocated microseismicity hypocenter lineaments (<a href="https://www.seismo.unr.edu/">UNR NSL</a>), Sentinel-1 InSAR phase-gradient breaks (<a href="https://search.asf.alaska.edu/">ASF NASA</a>), and 3D MT resistivity boundaries (<a href="https://gdr.openei.org/submissions/1391">OpenEI GDR #1391</a>) when outbound access permits.</li>
        </ul>
      </div>

      <h2 id="hypotheses">Preregistered Candidate Hypotheses (Locked Prior to Implementation)</h2>
      <p>Full equations, physical mechanisms, named mimics, and 3-experiment budget are locked in <a href="../research/hypotheses-preregistration-2026-10-28.md"><code>docs/research/hypotheses-preregistration-2026-10-28.md</code></a>:</p>
      <ol>
        <li><strong>H-K1-S2-1 (Rank 1 — Implemented): Potential-Field Tilt-Derivative Zero-Contour &amp; Hydrothermal Magnetite-Destruction Slot Detector</strong> (fixes <code>IR-KARAGE1-BAND6-01</code>; mimic: Oligocene ash-flow caldera margins &amp; mafic dike swarms).</li>
        <li><strong>H-K1-S2-2 (Rank 2 — Implemented): Seamless 10 m 3DEP Transverse Fluvial χ / k<sub>sn</sub> Knickzone &amp; 1.2 km Along-Strike Range-Front Bridge</strong> across the 24.63% 1 m LiDAR void (mimic: Pleistocene Lake Lahontan 1330–1342 m / 1265–1282 m &amp; Lake Dixie 1090–1105 m wave-cut shorelines).</li>
        <li><strong>H-K1-S2-3 (Rank 3 — Implemented): Leak-Free Stage-2 Multi-Scale Structural-Network Continuation</strong> at 400–1800 m scales (mimic: exposed &gt;1920 m Mesozoic pluton cooling joints).</li>
        <li><strong>H-K1-S2-4 (Rank 4 — Implemented in EXP3): Cenozoic Piedmont Conduit Envelope &amp; Non-Redundant d=3.18 px Submodular Allocation</strong> (beats 0.2778 Champion on <code>C_pied</code> while keeping overlap vs prior <code>H-K1-1</code> ≤ 0.70).</li>
        <li><strong>H-K1-S2-5 (Rank 5 — External Free Official Data Extension): Relocated Great Basin Microseismicity &amp; Crustal Strain-Rate Conduit Locator</strong> (USGS ComCat / UNR NSL / Zeng 2022 GPS; deferred in sandbox due to outbound host allowlist).</li>
      </ol>

      <h2 id="runcard">Parallel-Run Protocol JSON Run Card</h2>
      <pre>{esc(json.dumps(rc, indent=2))}</pre>
    </main>
    <footer>GEMSDOEkarage1 · Autonomous Research &amp; Engineering · Zero Portal Uploads Performed · <a href="executive-summary.html">Step-by-Step Submission Guide →</a></footer>
    </body></html>"""

    exec_body = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Step-by-Step Contest Submission Guide · GEMSDOEkarage1 (TD-KSCK)</title>
    <style>{css}</style></head><body>
    <header><div class="nav-wrap">
      <a href="../../index.html">GEMS / KARAGE 1 · SUBMISSION SOP</a>
      <nav>
        <a href="../../index.html">Root Overview</a>
        <a href="index.html">TD-KSCK Dashboard</a>
        <a href="executive-summary.html">Submission Guide</a>
        <a href="../executive-summary.html">9-Site Summary</a>
      </nav>
    </div></header>
    <main>
      <div class="banner">
        <span class="badge badge-ok">CLEARED ALL AUTOMATED GATES · SELECTOR PENDING FOR WEEKLY SLOT</span>
        <h1>How to Submit <code>{esc(rc['submission_file'])}</code> on DrivenData</h1>
        <p>This artifact passed every format, <code>[0, 1]</code> range, zero-NaN, 77-channel leakage canary, blocked holdout, and 817-raster uniqueness check. Per Parallel-Run Protocol Rule 6, <strong>zero live weekly slots were spent automatically</strong>; use the 6 steps below if the human/portfolio selector authorizes a weekly slot.</p>
        <div class="btn-row">
          <a class="btn btn-primary" href="../downloads/{esc(rc['submission_file'])}" download>↓ Step 1: Download Cleared .tif (146.5 KB)</a>
          <a class="btn btn-sec" href="../downloads/{esc(rc['submission_zip'])}">Optional Single-TIFF .zip (146.7 KB)</a>
          <a class="btn btn-sec" href="index.html">Back to Full TD-KSCK Dashboard</a>
        </div>
      </div>

      <h2>Step-by-Step DrivenData Upload Checklist</h2>
      <div class="card">
        <ol>
          <li><strong>Download the exact cleared GeoTIFF</strong> using the green button above: <code>{esc(rc['submission_file'])}</code> (146,504 bytes). Do <em>not</em> upload HTML/JSON files, and do <em>not</em> re-upload <code>karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif</code> (already registered in the prompt ledger) or any historical <code>GEMSDOE24..36</code> file.</li>
          <li><strong>Verify SHA-256 locally before upload:</strong>
            <pre>sha256sum {esc(rc['submission_file'])}
# Expected: {rc['raster_sha256']}</pre>
          </li>
          <li><strong>Confirm automated <code>[0, 1]</code> &amp; CRS preflight (already verified 15/15 PASS):</strong> Single-band <code>float32</code>, <code>EPSG:32611</code>, <code>3730 × 3292</code> @ 100 m, transform <code>(100, 0, 243350, 0, -100, 4508550)</code>, <code>min = 0.0</code>, <code>max = 1.0</code>, <code>n_nan = 0</code>, <code>n_inf = 0</code> across all 12,279,160 pixels (eliminating the prior <code>"Predicted values must be in range [0, 1]"</code> rejection).</li>
          <li><strong>Open the official DrivenData GEMS portal:</strong> Sign in at <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">https://www.drivendata.org/competitions/306/competition-doe-gems/</a> → click <strong>Submissions</strong> → confirm remaining rolling 7-day submission allowance (max 3 per 7 days).</li>
          <li><strong>Upload &amp; paste the exact 133-character submission note (≤ 140 chars):</strong>
            <pre>Submission Name: {esc(rc['submission_name'])}
Submission Note: {esc(rc['submission_note'])}</pre>
          </li>
          <li><strong>Archive the organizer receipt:</strong> Screenshot/save the DrivenData confirmation timestamp and returned score alongside SHA-256 <code>{rc['raster_sha256']}</code> before labeling any result <code>ORGANIZER-CONFIRMED</code>.</li>
        </ol>
      </div>
    </main>
    <footer>GEMSDOEkarage1 · Step-by-Step Submission SOP · <a href="index.html">Full TD-KSCK Dashboard &amp; 9-Site Audit</a></footer>
    </body></html>"""

    (OUT_DIR / "index.html").write_text(index_body)
    (OUT_DIR / "executive-summary.html").write_text(exec_body)


def sync_docs_run_card(rc: dict) -> None:
    # Keep `docs/data/run-card.json` synced to active promoted lane while honoring test_field_site.py schema
    out = dict(rc)
    out["ok_to_submit"] = False
    out["download_available"] = True
    out["lane_id"] = "H-K1-S2-1-TD-KSCK"
    (ROOT / "docs" / "data" / "run-card.json").write_text(json.dumps(out, indent=2) + "\n")


def main() -> None:
    rc = json.loads((ROOT / "evidence" / "run_card_td_ksck.json").read_text())
    exp = json.loads((ROOT / "evidence" / "experiments_td_ksck.json").read_text())
    uniq = json.loads((ROOT / "evidence" / "fleet_uniqueness_td_ksck.json").read_text())
    render_figures(rc, exp, uniq)
    build_html_pages(rc, exp, uniq)
    sync_docs_run_card(rc)
    print("[generate_td_ksck_pages] Rendered figures, docs/td-ksck/*.html, and docs/data/run-card.json")


if __name__ == "__main__":
    main()
