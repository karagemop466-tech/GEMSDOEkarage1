#!/usr/bin/env python3
"""Render the GEMSDOEkarage1 executive summary and per-site decision pages."""
from __future__ import annotations

import html as htmlmod
import json
from pathlib import Path
import urllib.parse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")
esc = htmlmod.escape

AUDIT = json.loads((DOCS / "data" / "reference-audit.json").read_text())
ROWS = AUDIT["rows"]
ASSETS = json.loads((ROOT / "registry" / "reference_assets.json").read_text())
ASSET = {a["id"]: a for a in ASSETS}

NEW_TIF = "gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4-zeros.tif"
NEW_ZIP = NEW_TIF.replace("-zeros.tif", "-zeros.zip")
NEW_SHA = "65c9432b2cb417824b846a63ab64bf9d1035e4a9e8102f3ed2175ad48a464687"
NEW_NOTE = ("Novel-territory gravity+radiometric+topo crest; dots outside all 9 GEMSDOE site halos; "
            "unique vs registry")
NEW_CARD = json.loads((ROOT / "evidence" / ("run_card_" + NEW_TIF.replace("-zeros.tif", ".json"))).read_text())


def asset_url(entry) -> str:
    return ("https://github.com/" + entry["repo"] + "/blob/" + entry["ref"] + "/"
            + urllib.parse.quote(entry["path"], safe="/"))


def artifact_url(path: str) -> str:
    return "./downloads/" + path


NAV = [("Overview", "../index.html"), ("Executive summary", "executive-summary.html"),
       ("Research", "../docs/research.html")]


def shell(title: str, body: str, depth: int = 0, active: str = "Executive summary") -> str:
    p = "../" * depth
    doc = p + "docs/"
    nav = "".join(
        f'<a {"class=active aria-current=page " if n == active else ""}href="{p + (href if href.startswith("http") else doc + href)}">{esc(n)}</a>'
        for n, href in NAV)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Auditable submission decisions for the DOE GEMS fault-mapping prize.">
<meta name="theme-color" content="#f6f8f5"><title>{esc(title)} &middot; GEMS Field Intelligence</title>
<link rel="stylesheet" href="{doc}assets/styles.css"><link rel="stylesheet" href="{doc}assets/decision.css"></head>
<body><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner container">
<a class="brand" href="{esc(p)}index.html"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 36 36"><path d="M5 25 13.3 8h8.5L31 25h-7.3L17.5 13 11.8 25Z"/><path d="M12 25h13"/></svg></span><span><strong>GEMS</strong><small>FIELD INTELLIGENCE</small></span></a>
<nav class="main-nav" aria-label="Main navigation">{nav}</nav>
<a class="header-link" href="https://github.com/karagemop466-tech/GEMSDOEkarage1">View repository &nearr;</a></div>
<div class="container"><p class="global-hold"><strong>Generated unique TIF ready to download &rarr; see Executive summary.</strong>
 &middot; Not cleared for live upload (ok_to_submit = false).</p></div></header>
<main id="main"><div class="container">{body}</div></main>
<footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div>
<div class="footer-links"><a href="{esc(doc)}data/latest-run-card.json">Latest run card &nearr;</a><a href="{esc(doc)}research.html">Research &nearr;</a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition &nearr;</a></div>
<div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with the organizers.</span></div></div></footer></body></html>'''


def pill(kind: str, text: str, sub: str | None = None) -> str:
    cls = "pill-red" if kind == "red" else "pill-neutral"
    out = f'<span class="pill {cls}">{esc(text)}</span>'
    if sub:
        out += f'<span class="cell-sub">{esc(sub)}</span>'
    return out


def hero_download() -> str:
    hdt = NEW_CARD["holdout_dti"]
    reg = NEW_CARD["registry_correlation_overlap"]
    return f'''<section class="subpage-hero">
<p class="eyebrow"><span class="eyebrow-line"></span> GENERATED SUBMISSION &mdash; READY TO DOWNLOAD</p>
<h1>gems-karage1-novelterr <em>unique TIF</em></h1>
<p class="hero-description">Single-band GeoTIFF produced this session. All cells finite in [0,1], no NaN inside the footprint,
EPSG:32611 / 3730&times;3292 / 100 m, transform identical to <code>sample_submission.tif</code>, zeros outside the footprint,
zero dots on the mapped catalogue. It can never trigger &ldquo;Predicted values must be in range [0, 1]&rdquo;.</p>
<div class="hero-actions">
<a class="button button-dark" href="{artifact_url(NEW_TIF)}" download>Download {esc(NEW_TIF)} &nearr;</a>
<a class="button button-light" href="{artifact_url(NEW_ZIP)}" download>Download .zip (one TIFF) &nearr;</a>
</div>
</section>

<section class="decision-panel" aria-labelledby="decision-title">
<div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT SUBMISSION STATUS
<span class="status-tag status-stop">NOT CLEARED FOR LIVE UPLOAD</span></div>
<h2 id="decision-title">Unique, validator-clean &mdash; not yet a cleared submission</h2>
<p>The generated TIF passes every local format gate (validator <strong>all checks passed</strong>) and is
<strong>unique</strong> against the nine focus-site registry rasters: forward 3-px dot overlap 0.0% (&le;70% limit),
|Spearman| 0.005 (&le;0.90 limit). Holdout result:
<strong>HOLDOUT-DTI = {hdt["pooled_dti_all_modes"]:.6f}</strong>
({hdt["evaluator_version"]}, {hdt["withheld_positive_pixels_total"]:,} withheld positives),
pooled across 16 spatial cells. This is <em>not</em> a leaderboard estimate or projection.</p>
<p><strong>It is not cleared to submit.</strong> <code>ok_to_submit = false</code>: no organizer-confirmed score exists
(DrivenData is login-walled; no weekly slot was spent), and the complete organizer registry is not accessible. Treat the file as a
<strong>research artifact to download and inspect</strong>; promotion to a live submission slot is a separate selector decision.</p>
<div class="decision-actions">
<a class="button button-light" href="data/latest-run-card.json">Full run card (JSON) &nearr;</a>
<a class="button button-light" href="#comparison">Nine-site table &nearr;</a>
<a class="button button-light" href="#howto">How to submit &nearr;</a>
</div>
</div>
<div class="decision-side">
<div><span>VERDICT</span><strong>Validated research artifact</strong></div>
<div><span>LIVE-UPLOAD OK?</span><strong style="color:#a65d49">No &mdash; not cleared</strong></div>
<div><span>UNIQUE VS REGISTRY?</span><strong style="color:#5a8f6e">Yes &mdash; 0.0% / 0.005</strong></div>
<div><span>HOLDOUT-DTI</span><strong>{hdt["pooled_dti_all_modes"]:.6f}</strong></div>
<div><span>RASTER SHA-256</span><strong style="font-size:11px">{NEW_SHA}</strong></div>
<a href="{artifact_url(NEW_TIF)}" download>Open download folder &nearr;</a>
</div>
</section>'''


CLAIMED = {"GEMSDOE24": 0.2535, "GEMSDOE25": 0.2600, "GEMSDOE27": 0.2449,
           "GEMSDOE28": 0.2710, "GEMSDOE30": 0.2600, "GEMSDOE31": 0.2708,
           "GEMSDOE32": 0.2778, "GEMSDOE33": 0.2632, "GEMSDOE36": 0.2750}


def site_rows() -> str:
    out = []
    for name in SITES:
        entry = ASSET[name]
        row = ROWS[name]
        fname = Path(entry["path"]).name
        out.append(f'''<tr>
<th scope="row"><a href="{esc(name)}.html">{esc(name)} &nearr;</a></th>
<td><a class="file-link" href="{esc(asset_url(entry), quote=True)}">{esc(fname)}</a>
<span class="cell-sub">Historical reference &middot; research only</span></td>
<td><strong>{CLAIMED[name]:.4f}</strong><span class="cell-sub">USER-REPORTED &middot; UNVERIFIED &middot; no organizer receipt</span></td>
<td>No defensible forecast<span class="cell-sub">not a score estimate</span></td>
<td>{pill('red', 'NO', f"{100*row['lattice_directed_overlap']:.1f}% within 3 px of lattice &middot; duplicate")}</td>
<td><span class="pill pill-red">DO NOT RESUBMIT</span></td>
</tr>''')
    hdt = NEW_CARD["holdout_dti"]; reg = NEW_CARD["registry_correlation_overlap"]
    out.append(f'''<tr class="best-row">
<th scope="row"><strong>GEMSDOE-karage1 (new)</strong></th>
<td><a class="file-link" href="{artifact_url(NEW_TIF)}">{esc(NEW_TIF)}</a>
<span class="cell-sub">Generated this session &middot; single-band GeoTIFF</span></td>
<td><strong>{hdt["pooled_dti_all_modes"]:.6f}</strong><span class="cell-sub">HOLDOUT-DTI &middot; {hdt["evaluator_version"]} &middot; not a leaderboard score</span></td>
<td>No live score available<span class="cell-sub">organizer receipt required</span></td>
<td>{pill('neutral', 'YES', f"{100*reg['worst_forward_overlap']:.1f}% max 3-px overlap &middot; |rho| {abs(reg['worst_spearman_full_footprint']):.3f}")}</td>
<td><span class="pill pill-red">NOT CLEARED &mdash; research only</span></td>
</tr>''')
    return "\n".join(out)


def comparison_table() -> str:
    hdt = NEW_CARD["holdout_dti"]
    return f'''<section class="section comparison" id="comparison">
<div class="section-heading"><div>
<p class="eyebrow"><span class="eyebrow-line"></span> NINE-FOCUS-SITE COMPARISON + GENERATED UNIQUE TIF</p>
<h2>Which file to download, and whether it is unique</h2>
<p>Every historical figure is a <strong>USER-REPORTED, UNVERIFIED</strong> claim with no file-linked organizer receipt. They are not score estimates.
The new row is the unique TIF generated this session, labelled <strong>HOLDOUT-DTI</strong> (never a projection).</p></div></div>
<div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table &rarr;</div>
<div class="table-scroll" tabindex="0" role="region" aria-label="Nine-site comparison plus generated TIF">
<table>
<thead><tr>
<th>Site</th><th>File to download</th><th>Highest supplied figure</th><th>Score label</th><th>Unique vs the listed GEMSDOE sites?</th><th>OK to submit?</th>
</tr></thead>
<tbody>{site_rows()}</tbody>
</table>
</div></div>
<div class="table-note"><span class="note-symbol">&diams;</span>
<strong>Read before downloading.</strong> The nine historical references all fail the literal registry proximity rule
(&ge;99.9% of dots within 3 px of the registered calibration lattice; limit 70%), so none is a valid new submission.
The generated GEMSDOE-karage1 TIF is unique (0.0% forward overlap, |Spearman| 0.005) and validator-clean, but it is
<strong>not cleared for live upload</strong> until an organizer-confirmed score and a separate selector decision exist.
Download it for research and inspection; do not treat the HOLDOUT-DTI as a leaderboard forecast.
</div></section>'''


def b2_analysis() -> str:
    return f'''<section class="section detail-grid" id="b2">
<div><p class="eyebrow"><span class="eyebrow-line"></span> WHY GEMSDOE32 B2 REPORTED 0.2778</p><h2>PhD-level reading</h2></div>
<div class="prose-card">
<p><strong>The number is not verified.</strong> <code>gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif</code>
reported <strong>0.2778</strong> by the site owner, but no artifact-linked organizer submission receipt is in this repository,
so it cannot be treated as ORGANIZER-CONFIRMED or used as a score target.</p>
<p><strong>Mechanism (geometric, not causal).</strong> On the audited mirrored grid the B2 mask is exactly the GEMSDOE25 d2.8
dot mask with <strong>6,436 dots within two pixels of the visible catalogue removed</strong> and no dots added. GEMSDOE25 and
GEMSDOE30 share an identical dot mask. Under the organizer's distance-weighted Tversky index
(&alpha; = 0.2, &beta; = 0.8, 300 m triangular kernel; known-catalogue pixels masked before scoring), thinning removes
false-positive mass around known faults while largely keeping distance-weighted coverage of nearby truth cells. That can raise
DTI &mdash; but it can also delete recoverable true faults, so the direction is not guaranteed without a controlled ablation.</p>
<p><strong>Can it be beaten?</strong> Conceivably &mdash; the live leaderboard has moved past 0.44 &mdash; but this audit establishes
neither a ceiling nor a beating method. The hidden truth, the weighted true-positive totals and any receipt linking these bytes to
0.2778 are unavailable. The same file scores only ~0.01 on this repository's catalogue holdout, showing that holdout and live scores
disagree for this family; no single holdout number supports 0.2778.</p>
<p><strong>Why a unique submission matters.</strong> All nine focus-site files are near-duplicates (&ge;99.9% lattice overlap). A dense
re-derivation will trip the literal &le;70% / 3-px rule. The generated GEMSDOE-karage1 TIF avoids this by placing every dot on
novel territory (outside all nine registry 3-px halos), so it is unique by construction.</p>
<a class="text-link" href="../docs/research.html#b2">Read the full scientific analysis &nearr;</a>
</div></section>'''


def hypotheses() -> str:
    return f'''<section class="section" id="hypotheses">
<div class="section-heading"><div>
<p class="eyebrow"><span class="eyebrow-line"></span> UNTRIED GEOLOGICAL HYPOTHESES (RANKED)</p>
<h2>Three to five candidates, not yet executed</h2>
<p>Ordering reflects qualitative expected DTI gain versus implementation cost, not a measured improvement.
All use only layers already restored in <code>data/bridge/training_features.tif</code> (USGS GeoDAWN magnetics/radiometrics,
USGS 3DEP DEM) plus the catalogue &mdash; no new external data is required, so each is obtainable now.</p>
</div></div>
<div class="hypothesis-grid">
<article class="hypothesis-card"><span class="hypothesis-rank">01 <span>MEDIUM GAIN &middot; LOW COST</span></span>
<h3>Gravity-gradient lineament x potassium alteration intersection</h3>
<p><b>Layers:</b> band 5 (iso_grav_anom_slope), band 18 (iso_grav_anom_hg), radiometric K (band 6 total-count context).
<b>Signature:</b> oriented signed gravity-gradient lineaments intersecting K-rich radiometric crests &mdash; a blind fault contact
under alluvial cover. <b>Off-catalogue:</b> no surface scarp, so USGS/INGENIOUS did not map it. <b>Differs:</b> prior work used unsigned
HMAS edges; this tests signed profile displacement and K/alteration coincidence.</p>
<small>Validate on holdout; single-feature leakage canary (AUC &le; 0.90) first.</small></article>

<article class="hypothesis-card"><span class="hypothesis-rank">02 <span>MEDIUM GAIN &middot; LOW-MED COST</span></span>
<h3>Block-normalized K/Th alteration ratio + magnetic persistence</h3>
<p><b>Layers:</b> radiometric K, Th, eU + upward-continued TMI (400 m / 1800 m). <b>Signature:</b> hydrothermal K-enrichment with
Th-depletion (potassic/silicic alteration halo) co-located with a persistent magnetic low after upward continuation. <b>Off-catalogue:</b>
alteration extends beyond the mapped fault trace. <b>Differs:</b> prior raw radiometric plumes were not block-normalized against
acquisition-block background, which can mimic alteration across survey boundaries.</p>
<small>GeoDAWN is public (CC0 via USGS); block IDs already in the stack.</small></article>

<article class="hypothesis-card"><span class="hypothesis-rank">03 <span>MEDIUM-LOW GAIN &middot; LOW COST</span></span>
<h3>100 m DEM curvature/relief + subtle drainage asymmetry</h3>
<p><b>Layers:</b> band 12 (det_elev), curvature and relief channels. <b>Signature:</b> repeated cross-valley asymmetry and scarp-like
curvature at 1&ndash;4 km scale on piedmont fans. <b>Off-catalogue:</b> sub-meter Holocene scarplets were below legacy mapping resolution.
<b>Differs:</b> prior work leaned on 1 m LiDAR scarps (only 75% coverage); this uses the full-footprint 100 m DEM so blind-basin faults are
not systematically excluded.</p>
<small>USGS 3DEP is free and official; tiles already restored.</small></article>

<article class="hypothesis-card"><span class="hypothesis-rank">04 <span>MEDIUM GAIN &middot; MEDIUM COST</span></span>
<h3>MT conductivity clay-cap breach gradient</h3>
<p><b>Layers:</b> band 17 (cond_surf, surface MT log-conductivity). <b>Signature:</b> sharp lateral gradient in residualized surface
conductivity marking a smectite-clay-cap breach &mdash; a fluid pathway. <b>Off-catalogue:</b> a subsurface geophysical signature with no
required surface expression. <b>Differs:</b> prior features used magnetics/radiometrics; MT conductivity responds to fluid/clay, a different
physical property. Confounder: saline playas (mitigated by elevation/depth residualization).</p>
<small>GDR 1391 MT products are public; band 17 already restored.</small></article>

<article class="hypothesis-card"><span class="hypothesis-rank">05 <span>MEDIUM-HIGH GAIN &middot; MEDIUM COST</span></span>
<h3>Half-graben accommodation-zone gravity inflection</h3>
<p><b>Layers:</b> band 18 (signed gravity gradient), band 15 (depth_to_base). <b>Signature:</b> gravity horizontal-gradient inflection where
basement depth changes abruptly &mdash; fault intersections / accommodation zones. <b>Off-catalogue:</b> accommodation zones are 3D basin
features, rarely mapped as single traces. <b>Differs:</b> prior 2D lineament methods did not model 3D basement-geometry inflection.</p>
<small>All layers in the restored 19-band stack; no external data.</small></article>
</div>
<div class="notice guide-notice"><span aria-hidden="true">&ominus;</span><p>None of these has been run on the holdout. Per the budget rule, the top candidate must beat the current holdout best
(HOLDOUT-DTI 0.017415 on this session&rsquo;s unique TIF) on a spatially blocked hide-and-recover holdout before any weekly slot is spent.</p></div>
</section>'''


def howto() -> str:
    return f'''<section class="section" id="howto">
<div class="section-heading"><div>
<p class="eyebrow"><span class="eyebrow-line"></span> HOW TO SUBMIT TO THE CONTEST</p><h2>Step-by-step</h2>
<p>These steps describe the official DrivenData submission form. They are <strong>not</strong> permission to upload the generated
TIF, which is currently <code>ok_to_submit = false</code>.</p></div></div>
<div class="steps-grid">
<article><span>01 &nbsp;/&nbsp; ELIGIBILITY</span>
<h3>Confirm the file is cleared</h3>
<p>Only upload a file the project has marked <strong>OK TO SUBMIT</strong> (a green badge, an organizer-linked receipt,
and a separate selector decision). Today&rsquo;s badge is red: the generated TIF is a research artifact, not cleared.</p></article>
<article><span>02 &nbsp;/&nbsp; FILE</span>
<h3>Choose a single-band GeoTIFF</h3>
<p>Download <code>{esc(NEW_TIF)}</code> (or the one-TIFF .zip). It must match <code>sample_submission.tif</code>: single band,
float32, EPSG:32611, 3730&times;3292, 100 m, all cells finite in [0,1], transform identical, nodata=None. Verify the displayed SHA-256:
<code>{NEW_SHA}</code>.</p></article>
<article><span>03 &nbsp;/&nbsp; NAME</span>
<h3>Give it a unique name</h3>
<p>Use a unique submission name (never reuse a prior GEMSDOE filename). Example generated name:
<code>{esc(NEW_TIF.replace("-zeros.tif", ""))}</code> &mdash; includes lane, timestamp and an 8-char digest so it can never be
confused with another submission.</p></article>
<article><span>04 &nbsp;/&nbsp; NOTE</span>
<h3>Add a short note (&le;140 chars)</h3>
<p>Paste a note of at most 140 characters to tell submissions apart (e.g. &ldquo;clustering with k=25&rdquo;).
Generated note ({len(NEW_NOTE)} chars): <code>{esc(NEW_NOTE)}</code>.</p></article>
</div>
<div class="steps-grid">
<article><span>05 &nbsp;/&nbsp; UPLOAD</span>
<h3>Use the official form</h3>
<p>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData &middot; DOE GEMS Prize</a>,
select Submit &rarr; Make new submission, choose the .tif or a .zip containing one GeoTIFF, paste the note, and submit.
Retain the file-linked organizer receipt as the ORGANIZER-CONFIRMED record.</p></article>
<article><span>06 &nbsp;/&nbsp; WEEKLY CAP</span>
<h3>Respect the submission cap</h3>
<p>Three submissions per rolling 7-day window. Never spend a slot on a duplicate, a holdout-inferior file, or one that has not
passed the uniqueness gate. Negative results are deliverables &mdash; do not upload to &ldquo;see what happens.&rdquo;</p></article>
</div>
<div class="notice guide-notice"><span aria-hidden="true">&ominus;</span><p>The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> require disclosure of generative-AI use in the
narrative when applicable. Public leaderboard performance is not the private final score.</p></div>
</section>'''


def build():
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "downloads").mkdir(parents=True, exist_ok=True)

    body = (hero_download() + comparison_table() + b2_analysis() + hypotheses() + howto())
    page = shell("Executive summary · generated unique TIF", body, depth=0, active="Executive summary")
    out = DOCS / "executive-summary.html"
    out.write_text(page + "\n", encoding="utf-8")
    print("Wrote", out)

    for name in SITES:
        entry = ASSET[name]
        row = ROWS[name]
        pair = max((v["overlap_fraction"], k.split("->")[1])
                   for k, v in AUDIT["directed_pairs"].items()
                   if k.startswith(name + "->"))
        body = (f'''<section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SITE EXECUTIVE SUMMARY</p>
<h1>{esc(name)} <em>research only</em></h1><p>The reported historical leader is not a newly eligible submission.</p></section>
<section class="decision-panel"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT SUBMISSION DECISION
<span class="status-tag status-stop">DO NOT RESUBMIT</span></div>
<h2 id="decision-title">No eligible file from this site</h2>
<p><a class="wrap" href="{esc(asset_url(entry), quote=True)}">{esc(Path(entry["path"]).name)} &nearr;</a>
&middot; SHA-256 <code class="wrap">{entry["sha256"]}</code></p>
<p><strong>{CLAIMED[name]:.4f} USER-REPORTED &middot; UNVERIFIED.</strong> No artifact-linked organizer receipt is available; this is not a score estimate.
The file has {row["positive_pixels"]:,} positive pixels and {100*row["lattice_directed_overlap"]:.1f}% fall within 3 px of the registered lattice
(limit 70%). It overlaps {100*pair[0]:.1f}% with {pair[1]} in the nine-file directional audit. <strong>DO NOT RESUBMIT.</strong></p>
</div><div class="decision-side">
<div><span>VERDICT</span><strong>Negative &middot; duplicate</strong></div>
<div><span>UNIQUE VS REGISTRY?</span><strong style="color:#a65d49">No</strong></div>
<div><span>LEADERBOARD ESTIMATE</span><strong>Unavailable</strong></div>
<a href="executive-summary.html">Executive summary &nearr;</a></div></section>
<section class="next-strip"><div><p class="eyebrow">BACK TO THE COMPARISON</p><h2>See all nine sites and the generated TIF</h2></div>
<a class="button button-dark" href="executive-summary.html">Executive summary &nearr;</a></section>''')
        page = shell(f"{name} executive summary", body, depth=1, active="Executive summary")
        (DOCS / f"{name}.html").write_text(page + "\n", encoding="utf-8")
        print("Wrote", name + ".html")

    print("Executive summary build complete.")


if __name__ == "__main__":
    build()
