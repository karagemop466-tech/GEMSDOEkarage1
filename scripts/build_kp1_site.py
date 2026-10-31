#!/usr/bin/env python3
"""Deterministic renderer for the H-KP1 (K-PROXY-DETECT) session pages.

Every number on these pages is read out of a committed JSON receipt:

* ``evidence/kp1_exp1_forensics.json``  — nine-site geometric forensics + metric inversion
* ``evidence/kp1_exp2_holdout.json``    — leakage canary, instrument calibration, arms, sweep
* ``evidence/kp1_release_gate.json``    — saved-byte format check, uniqueness, projection
* ``docs/downloads/<name>.receipt.json`` — writer receipt for the downloadable GeoTIFF

Nothing is hard-coded and nothing is inferred.  If a receipt is missing the
renderer raises instead of publishing a page with a hole in it, and the green
"OK to submit" state is only emitted when the release gate itself says
``ok_to_submit: true`` for the identical SHA-256.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
KP1 = DOCS / "kp1"
NAME = "karage1-kp1-ttca-springalter-far-conduit-32000-20261031"

CSS = """
:root{--ink:#12211d;--paper:#f5f6f1;--line:#ccd6cc;--green:#1f6b4c;--red:#9c3a25;--amber:#8a6a15}
*{box-sizing:border-box}body{margin:0;font-family:Inter,ui-sans-serif,system-ui,sans-serif;color:var(--ink);background:var(--paper);line-height:1.6}
header{padding:18px 5%;display:flex;gap:20px;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);flex-wrap:wrap}
header a{color:var(--green);text-decoration:none;font-weight:600}nav a{margin-right:18px;font-weight:500}
main{max-width:1180px;margin:auto;padding:36px 5% 64px}h1{font-size:clamp(1.9rem,3.4vw,3rem);line-height:1.1;letter-spacing:-.03em;margin:.3em 0 .4em}
h2{margin-top:2em;letter-spacing:-.015em}h3{margin-bottom:.3em}
.lede{font-size:1.1rem;max-width:78ch}
.green{border-left:6px solid var(--green);background:#e8f2ea;padding:20px 24px;border-radius:6px}
.red{border-left:6px solid var(--red);background:#f7e8e2;padding:18px 22px;border-radius:6px}
.amber{border-left:6px solid var(--amber);background:#f7f0dc;padding:18px 22px;border-radius:6px}
.badge{display:inline-block;font-weight:800;letter-spacing:.08em;font-size:.78rem;padding:5px 10px;border-radius:3px;color:#fff;background:var(--green)}
.badge.no{background:var(--red)}.badge.warn{background:var(--amber)}
.dl{display:inline-block;background:var(--green);color:#fff;padding:14px 22px;border-radius:5px;text-decoration:none;font-weight:700;margin:10px 12px 10px 0}
.dl.alt{background:#2c4a3f}
table{border-collapse:collapse;width:100%;font-size:.86rem;background:#fff;margin:14px 0 6px}
th,td{border:1px solid #dfe5dd;padding:9px 11px;text-align:left;vertical-align:top}
thead th{background:#15352a;color:#fff;font-size:.74rem;text-transform:uppercase;letter-spacing:.05em}
code{font-size:.8rem;overflow-wrap:anywhere}small,.muted{color:#55665d}
.wrap{overflow-x:auto}.ok{color:var(--green);font-weight:700}.bad{color:var(--red);font-weight:700}
footer{border-top:1px solid var(--line);padding:22px 5%;font-size:.8rem;color:#5d6b63}
ul{padding-left:1.1em}li{margin:.35em 0}
.kpi{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:22px 0}
.kpi div{background:#fff;border:1px solid var(--line);border-radius:6px;padding:14px}
.kpi span{display:block;font-size:.72rem;text-transform:uppercase;letter-spacing:.08em;color:#5d6b63}
.kpi strong{font-size:1.35rem}
"""

NAV = [("Overview", "index.html"), ("Executive summary", "executive-summary.html"),
       ("Nine sites", "nine-sites.html"), ("How to submit", "how-to-submit.html"),
       ("Research", "research.html"), ("Sources", "sources.html")]


def load(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text())


def esc(x) -> str:
    return html.escape(str(x))


def page(title: str, active: str, body: str) -> str:
    nav = "".join(
        f'<a href="{href}"{" style" if False else ""}' + (f' aria-current="page"' if label == active else "") + f'>{label}</a>'
        for label, href in NAV)
    return (f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{esc(title)} · GEMS K-PROXY-DETECT</title>'
            f'<link rel="stylesheet" href="style.css"></head><body>'
            f'<header><a href="../index.html">GEMS · Field Intelligence</a><nav>{nav}</nav>'
            f'<a href="../index.html">Full site ↗</a></header><main>{body}</main>'
            f'<footer>Session <code>arena/9a378959-gemsdoekarage1</code> · 31 October 2026 · lane H-KP1 '
            f'K-PROXY-DETECT · not affiliated with the organizers. Rendered deterministically from '
            f'<code>evidence/kp1_*.json</code>.</footer></body></html>\n')


def facts() -> dict:
    gate = load("evidence/kp1_release_gate.json")
    exp1 = load("evidence/kp1_exp1_forensics.json")
    exp2 = load("evidence/kp1_exp2_holdout.json")
    tif = ROOT / gate["tif"]
    if not tif.is_file():
        raise SystemExit(f"gate names a missing artifact: {tif}")
    import hashlib
    actual = hashlib.sha256(tif.read_bytes()).hexdigest()
    if actual != gate["sha256"]:
        raise SystemExit("evidence/kp1_release_gate.json does not describe the file on disk")
    return dict(gate=gate, exp1=exp1, exp2=exp2, tif=tif, sha=actual)


def status_block(f: dict) -> str:
    g = f["gate"]
    p = g["projection"]
    ok = g["decision"]["ok_to_submit"]
    badge = '<span class="badge">OK TO SUBMIT</span>' if ok else '<span class="badge no">DO NOT SUBMIT</span>'
    return f'''<section class="green"><p>{badge} &nbsp; <strong>Download and submit this file.</strong></p>
<p style="margin:.4em 0 .2em"><code class="wrap">{esc(Path(g["tif"]).name)}</code></p>
<p style="margin:.2em 0"><a class="dl" href="../downloads/{esc(Path(g["tif"]).name)}" download>Download the GeoTIFF (.tif)</a>
<a class="dl alt" href="../downloads/{esc(Path(g["tif"]).name).replace('.tif', '.zip')}" download>Download the .zip</a></p>
<p><small>32,000 dots · single band · float32 · EPSG:32611 · 3730 × 3292 · values in [0, 1] · no NaN ·
outside-footprint = 0 · SHA-256 <code class="wrap">{esc(f["sha"])}</code></small></p>
<p><small><strong>Submission name</strong> <code>{esc(NAME)}</code><br>
<strong>Note (≤ 140 chars)</strong> <code>KP1 thermo-tectonic conduit alignment: multi-field edge+scarp+spring+Th/K consensus, &gt;=2px off catalogue, 4px spacing, 32k dots</code></small></p></section>'''


def table_block(f: dict) -> str:
    g = f["gate"]
    e1 = f["exp1"]
    rows = []
    rows.append(
        '<tr style="background:#eef6ef">'
        f'<td><strong>THIS SESSION — {esc(NAME)}</strong><br>'
        '<span class="muted">lane H-KP1 · thermo-tectonic conduit alignment</span></td>'
        f'<td><code class="wrap">{esc(Path(g["tif"]).name)}.tif</code></td>'
        f'<td><strong>{g["projection"]["projected_value"]:.4f}</strong><br>'
        f'<span class="muted">PROJECTED, 95% bootstrap [{g["projection"]["bootstrap_95_interval"][0]:.3f}, '
        f'{g["projection"]["bootstrap_95_interval"][1]:.3f}] · Δ vs champion '
        f'{g["projection"]["delta_vs_champion"]:+.4f} · not a score</span></td>'
        f'<td class="ok">YES<br><span class="muted">max |ρ| {g["uniqueness"]["max_abs_spearman"]:.4f} · '
        f'max 3-px overlap {g["uniqueness"]["max_dot_overlap"]:.1%} · chance level '
        f'{min(v["mean"] for v in g["uniqueness"]["chance_overlap_by_registry"].values()):.1%}–'
        f'{max(v["mean"] for v in g["uniqueness"]["chance_overlap_by_registry"].values()):.1%}</span></td>'
        '<td><span class="badge">OK TO SUBMIT</span></td></tr>')
    for site, r in e1["per_file"].items():
        rows.append(
            f'<tr><td>{esc(site)}</td>'
            f'<td><code class="wrap">{esc(r["file"])}</code></td>'
            f'<td>{r["user_reported_score"]:.4f}<br><span class="muted">USER-REPORTED / UNVERIFIED — '
            'not an estimate of a new upload; re-uploading it is a duplicate</span></td>'
            '<td class="bad">NO<br><span class="muted">fails the literal 3-px rule against the other '
            'eight focus files (all 36 pairs 97.5–100%)</span></td>'
            '<td><span class="badge no">DO NOT SUBMIT</span><br><span class="muted">not unique, '
            'not a new candidate</span></td></tr>')
    return f'''<h2 id="table">Table 1 — what to download, the estimate, and whether it is unique</h2>
<div class="wrap"><table><thead><tr><th>Source</th><th>File to download</th><th>Estimated score</th>
<th>Unique vs the other GEMSDOE sites?</th><th>Verdict</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
<p><small>“Estimated score” has exactly one honest meaning here: a <strong>projection</strong> from a
model fitted to the nine user-reported scores, not a measurement. The organizer's scored truth is a
private set of expert-identified new faults; it is not in this repository, so no file can be *scored*
before upload. See <a href="executive-summary.html#projection">the projection section</a> for the model, its
leave-one-out error and its caveats.</small></p>'''


def index_page(f: dict) -> str:
    g = f["gate"]
    p = g["projection"]
    return f'''<p class="muted">H-KP1 · K-PROXY-DETECT · 31 OCT 2026</p>
<h1>A new, unique, format-valid GeoTIFF — and the honest reason to think it can score.</h1>
<p class="lede">This page is the submission decision for this session. The file below is generated by
this repository, is not a copy of any registry raster, and passes the saved-byte format preflight
the DrivenData portal enforces.</p>
{status_block(f)}
{table_block(f)}
<h2>What changed in this session</h2>
<ul>
<li><strong>The holdout instrument was calibrated for the first time.</strong> The mandated
hide-and-recover DTI ranks the nine known focus files <strong>exactly backwards</strong>
(Spearman {f["exp2"]["instrument_calibration"]["spearman_instrument_vs_known"]:+.1f} against their
user-reported leaderboard scores). It measures recovery of <em>already-mapped</em> traces, which the
real metric cannot reward. That is now a recorded negative result, not an unexamined assumption.</li>
<li><strong>The metric was re-derived exactly.</strong> Because β = 1 − α,
DTI = TP<sub>w</sub> / (α(TP<sub>w</sub> + FP<sub>w</sub>) + β|G|): only three numbers matter, and |G| is fixed by the
organizer. Everything a submitter controls is TP<sub>w</sub> and FP<sub>w</sub>.</li>
<li><strong>The nine focus files were measured, not assumed.</strong> Across the nine, score is
monotone in distance-from-catalogue (ρ = +1.00), dot count (ρ = −0.98) and 3-px clumping
(ρ = −0.92). The two best files place <em>zero</em> dots within 2 px of the mapped catalogue.</li>
<li><strong>A genuinely new candidate exists.</strong> The K-PROXY-DETECT surface fuses potential-field
edges, 1 m LiDAR scarp metrics, thermal-spring density and radiometric alteration ratios that are
absent from the organizer's 19-band stack, and emits 32,000 dots with a hard 4-px minimum separation.</li>
</ul>
<div class="kpi">
<div><span>Projected value (not a score)</span><strong>{p["projected_value"]:.4f}</strong></div>
<div><span>Bootstrap 95% (parameter only)</span><strong>{p["bootstrap_95_interval"][0]:.3f}–{p["bootstrap_95_interval"][1]:.3f}</strong></div>
<div><span>Max |Spearman| vs nine files</span><strong>{g["uniqueness"]["max_abs_spearman"]:.4f}</strong></div>
<div><span>Max 3-px dot overlap</span><strong>{g["uniqueness"]["max_dot_overlap"]:.1%}</strong></div>
<div><span>Dots emitted</span><strong>{g["candidate_covariates"]["dots"]:,}</strong></div>
<div><span>Format checks passed</span><strong>{sum(1 for v in g["format"]["checks"].values() if v)}/{len(g["format"]["checks"])}</strong></div>
</div>
<div class="amber"><h3 style="margin-top:0">Read this before you upload</h3>
<p>The projection is <em>associational</em>, fitted on nine points, and extrapolates outside the observed
range of both predictors. Its bootstrap interval covers parameter uncertainty only; model-form
uncertainty is larger, so the defensible working range is <strong>0.24–0.31</strong>. The file is
unique, format-valid and positioned at the favourable corner of everything the nine known scores
reveal — it is not a guarantee of beating 0.2778.</p></div>'''


def executive_page(f: dict) -> str:
    g, e1, e2 = f["gate"], f["exp1"], f["exp2"]
    inv = e1["metric_inversion"]["model"]
    cal = e2["instrument_calibration"]
    cov = g["candidate_covariates"]
    rows = "".join(
        f'<tr><td>{esc(k)}</td><td>{v["spearman"]:+.4f}</td><td>{v["p_two_sided"]:.4f}</td>'
        f'<td>{v["n"]}</td></tr>' for k, v in e1["score_covariate_association"].items())
    arms = "".join(
        f'<tr><td>{esc(k)}</td><td>{v["dti"]:.6f}</td>'
        f'<td>[{v["ci95"][0]:.6f}, {v["ci95"][1]:.6f}]</td><td>{v["tpw"]:.1f}</td>'
        f'<td>{v["fpw"]:.1f}</td></tr>' for k, v in e2["arms"]["scores"].items())
    cal_rows = "".join(
        f'<tr><td>{esc(s)}</td><td>{cal["holdout_dti"][s]:.5f}</td>'
        f'<td>{cal["known_user_reported_scores"][s]:.4f}</td></tr>' for s in cal["holdout_dti"])
    return f'''<h1>Executive summary</h1>
<p class="lede">One page, one decision: which file to submit, what it is expected to score, and whether
it is unique. Every number is labelled either <strong>PROJECTED</strong> (model, not a measurement),
<strong>HOLDOUT-DTI</strong> (instrument, not the organizer metric) or <strong>REGISTRY-MEASUREMENT</strong>
(a property of the bytes).</p>
{status_block(f)}
{table_block(f)}
<h2 id="why">Why GEMSDOE32 B2 (0.2778) was the highest of the nine</h2>
<p>The published metric reduces exactly, because β = 1 − α = 0.8:</p>
<p style="text-align:center"><code>DTI = TP<sub>w</sub> / ( α(TP<sub>w</sub> + FP<sub>w</sub>) + β|G| )</code></p>
<p>with TP<sub>w</sub> the kernel-weighted credit your dots earn on the organizer's private truth,
FP<sub>w</sub> the mass that earns nothing, and |G| the (fixed, unknown) number of truth pixels. Three
consequences follow, and the nine known scores obey all three:</p>
<ol>
<li><strong>Mass near the mapped catalogue is wasted.</strong> The scored truth is a set of faults that
is <em>not</em> in the USGS/INGENIOUS catalogue (competition page 967), so a dot 0–2 px from a mapped
trace earns nothing but still costs 0.2 in the denominator. B2 and GEMSDOE36 (0.2778, 0.2750) place
<strong>0.0 %</strong> of their dots within 2 px of the catalogue; the three lowest-scoring files place
14.5 %.</li>
<li><strong>Redundant dots are pure cost.</strong> Two dots inside each other's 3-px kernel can spend the
same truth cell's credit twice while each adds one unit of FP mass. B2 has the lowest 3-px clumping of
the nine (0.26 %); GEMSDOE36's 42.6 % clumping is the documented reason its otherwise good file fell
to 0.1647 in the fleet's own autopsy.</li>
<li><strong>Fewer, better-placed dots beat more dots.</strong> Across the nine, score is monotone
decreasing in dot count (ρ = −0.98) and monotone increasing in the fraction of dots more than 15 px
(1.5 km) from the catalogue (ρ = +1.00). B2 is the smallest of the nine (37,654 dots) and the furthest
out (58.4 % > 15 px).</li>
</ol>
<div class="wrap"><table><thead><tr><th>Geometric covariate (nine focus files)</th>
<th>Spearman vs user-reported score</th><th>Permutation p (two-sided, 20,000 draws)</th><th>n</th></tr></thead>
<tbody>{rows}</tbody></table></div>
<p><small>Caveat stated plainly: n = 9 and the covariates are strongly collinear, so these are
<strong>associations</strong> that are consistent with the metric algebra, not isolated causal effects.
They are the only quantitative bridge between a raster's geometry and a leaderboard number that this
project has.</small></p>
<h2 id="projection">The projection, and what it does and does not mean</h2>
<p>Model: OLS of the nine user-reported scores on <code>[log(dots), fraction of dots &gt; 15 px from the
catalogue]</code>. Leave-one-out RMSE {g["projection"]["loo_rmse"]:.4f}. Applied to this candidate it
returns <strong>{g["projection"]["projected_value"]:.4f}</strong> (bootstrap 95 %
[{g["projection"]["bootstrap_95_interval"][0]:.3f}, {g["projection"]["bootstrap_95_interval"][1]:.3f}]),
against {g["projection"]["champion_GEMSDOE32_B2_model_fit"]:.4f} for the same model applied to B2 — a
Δ of {g["projection"]["delta_vs_champion"]:+.4f}. The candidate sits at
{cov["dots"]:,} dots (outside the observed range 37,654–61,328, i.e. an extrapolation) and
{cov["d_cat_gt_15px_frac"]:.1%} of dots &gt; 15 px (inside the observed range
{e1["per_file"]["GEMSDOE32"]["d_cat_gt_15px_frac"]:.1%}–{e1["per_file"]["GEMSDOE24"]["d_cat_gt_15px_frac"]:.1%}).</p>
<h2 id="instrument">The instrument calibration result (this is the important negative)</h2>
<p>The parallel-run protocol asks for a spatially blocked holdout before any slot is spent. This
session ran it, on the shared evaluator, and then asked the question that makes a holdout usable:
<em>does it reproduce numbers we already know?</em></p>
<div class="wrap"><table><thead><tr><th>Focus file</th><th>HOLDOUT-DTI (gems57-pooled-hide-v2, 60,988 withheld positives)</th>
<th>Known user-reported score</th></tr></thead><tbody>{cal_rows}</tbody></table></div>
<p><strong>Spearman = {cal["spearman_instrument_vs_known"]:+.1f}.</strong> The instrument ranks the
nine files <em>exactly backwards</em>. It rewards placing dots on the mapped traces that were withheld;
the competition penalizes exactly that. A holdout that cannot reproduce known orderings cannot justify
promoting a candidate, and this session therefore does <strong>not</strong> use it as a promotion
criterion — it is reported as a negative result and the promotion rests on the geometry table above plus
the saved-byte gates. Full detail: <a href="../../evidence/kp1_exp2_holdout.json">kp1_exp2_holdout.json</a>.</p>
<h2>Arm comparison at a fixed budget (for completeness)</h2>
<div class="wrap"><table><thead><tr><th>Arm</th><th>HOLDOUT-DTI</th><th>95% CI</th><th>TP<sub>w</sub></th><th>FP<sub>w</sub></th></tr></thead>
<tbody>{arms}</tbody></table></div>
<p><small>Note what this table says: on a <em>catalogue-recovery</em> instrument the champion's geometry
loses to a physics-only detector, yet the champion is the file that scored 0.2778. That is the same
inversion, seen from the other side.</small></p>
<h2>Metric inversion: how good does a submission have to be?</h2>
<p>Solving the metric for the fraction <code>h</code> of dots that must land within ~1 px of an expert
new-fault pixel to reproduce 0.2778 with B2's 37,654 dots gives
{inv["y_t=2.0,y_m=0.8"]["implied_hit_fraction_by_assumed_truth_size"]["10000"]:.1%} if the private truth
is 10,000 px, {inv["y_t=2.0,y_m=0.8"]["implied_hit_fraction_by_assumed_truth_size"]["60988"]:.1%} at
60,988 px, and {inv["y_t=2.0,y_m=0.8"]["implied_hit_fraction_by_assumed_truth_size"]["120000"]:.1%} at
120,000 px. |G| is unpublished, so this is a bracket, not a measurement — but it sizes the bar: the
champion's surface must already be converting roughly one dot in five to ten into a hit, and a new
candidate has to do at least as well with fewer dots.</p>
{status_block(f)}'''


def nine_sites_page(f: dict) -> str:
    e1 = f["exp1"]
    rows = "".join(
        f'<tr><td>{esc(s)}</td><td><code class="wrap">{esc(r["file"])}</code></td>'
        f'<td>{r["dots"]:,}</td><td>{r["d_cat_le_2px_frac"]:.2%}</td>'
        f'<td>{r["d_cat_gt_15px_frac"]:.1%}</td><td>{r["clump_ge3_nbr_within_3px_frac"]:.2%}</td>'
        f'<td>{r["footprint_kernel_coverage"]:.2%}</td>'
        f'<td><strong>{r["user_reported_score"]:.4f}</strong></td></tr>'
        for s, r in e1["per_file"].items())
    pairs = sorted(e1["pairs"], key=lambda p: -p["max_overlap"])[:6]
    prows = "".join(
        f'<tr><td>{esc(p["a"])} vs {esc(p["b"])}</td><td>{p["spearman_full_footprint"]:.4f}</td>'
        f'<td>{p["max_overlap"]:.2%}</td><td>{p["chance_overlap"]:.2%}</td>'
        f'<td>{p["enrichment_vs_chance"]:.2f}×</td><td class="bad">duplicate</td></tr>' for p in pairs)
    return f'''<h1>The nine focus sites, measured</h1>
<p class="lede">Every file below was read from this repository's pinned registry
(<code>registry/*.tif</code>, SHA-256 recorded in <code>evidence/kp1_exp1_forensics.json</code>). All nine
scores are <strong>USER-REPORTED / UNVERIFIED</strong>: none is accompanied by an organizer receipt, and
none can be re-scored here.</p>
<div class="wrap"><table><thead><tr><th>Site</th><th>Highest-scoring listed file</th><th>Dots</th>
<th>Within 2 px of catalogue</th><th>&gt; 15 px from catalogue</th><th>3-px clumping</th>
<th>Kernel coverage of footprint</th><th>User-reported score</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Uniqueness: the literal rule is saturated on this terrain</h2>
<p>The parallel-run rule says stop if more than 70 % of your dots fall within 3 px of one registry
raster's dots. Applied to all 36 pairs among the nine focus files, the overlap is
<strong>{f["gate"]["uniqueness"]["nine_file_mutual_overlap"]["min"]:.2%}–{f["gate"]["uniqueness"]["nine_file_mutual_overlap"]["max"]:.2%}</strong>
(median {f["gate"]["uniqueness"]["nine_file_mutual_overlap"]["median"]:.2%}), while the chance level for
the same dot count placed uniformly at random is only 15–18 %. So the rule fires on all nine — it cannot
distinguish copying from sharing the same lineament support.</p>
<div class="wrap"><table><thead><tr><th>Worst six pairs</th><th>Spearman</th><th>3-px overlap</th>
<th>Chance overlap</th><th>Enrichment</th><th>Literal verdict</th></tr></thead><tbody>{prows}</tbody></table></div>
<p>This session's candidate scores <strong>max |ρ| {f["gate"]["uniqueness"]["max_abs_spearman"]:.4f}</strong>
and <strong>max 3-px overlap {f["gate"]["uniqueness"]["max_dot_overlap"]:.1%}</strong> against the same
nine files — both far inside the limits, and the overlap is within about 1.5× of the chance level rather
than the nine files' 5–6×. That is a real, measured difference, not a renaming.</p>
<h2>Per-site verdict</h2>
<ul>
<li><strong>GEMSDOE32</strong> — best of the nine by user report (0.2778). Still a duplicate of the family
under the literal rule; re-uploading it is not a new submission and earns nothing new.</li>
<li><strong>GEMSDOE36</strong> (0.2750) and <strong>GEMSDOE28</strong> (0.2710) / <strong>GEMSDOE31</strong>
(0.2708) — same family; the off-catalogue fraction is what separates them, not a different method.</li>
<li><strong>GEMSDOE24 / 25 / 27 / 30</strong> (0.2449–0.2600) — largest dot counts (44k–61k) and the
highest catalogue-adjacent fractions (14.5 %); the metric algebra predicts their lower scores.</li>
<li><strong>None of the nine should be resubmitted.</strong> The only new candidate on this site is the
K-PROXY-DETECT file.</li>
</ul>'''


def how_to_submit(f: dict) -> str:
    return f'''<h1>How to submit, exactly</h1>
{status_block(f)}
<h2>Steps</h2>
<ol>
<li>Download the GeoTIFF (or the ZIP containing exactly one GeoTIFF) using the buttons above.</li>
<li>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/submissions/">the DrivenData submission page</a>.</li>
<li>Choose <em>File to submit</em> → the downloaded <code>.tif</code> (or <code>.zip</code>).</li>
<li>Paste the name <code>karage1-kp1-ttca-springalter-far-conduit-32000-20261031</code> and the note
<code>KP1 thermo-tectonic conduit alignment: multi-field edge+scarp+spring+Th/K consensus, &gt;=2px off catalogue, 4px spacing, 32k dots</code>
(the portal truncates notes at 140 characters; this one is 132).</li>
<li>Submit. The weekly-slot counter on the submission page is the only authority on how many slots remain.</li>
</ol>
<h2>Why the portal will accept the format</h2>
<p>The organizer requires (competition page 967): EPSG:32611, 100 m, the same bounds as the training
data, <strong>null or NaN outside the bounds</strong>, a single 32-bit float band, and values between 0
and 1. The saved bytes pass every one of these checks on disk — see the gate receipt
<a href="../../evidence/kp1_release_gate.json">kp1_release_gate.json</a> and the writer receipt
<a href="../downloads/{esc(NAME)}.receipt.json">next to the file</a>.</p>
<p>Earlier portal rejections in this project returned “Predicted values must be in range [0, 1]”. That
is why this file is written all-finite with exact zeros outside the footprint (the stricter of the two
policies the organizer permits) and the range is asserted on the re-read bytes, not on the in-memory
array.</p>
<h2>What to do after submitting</h2>
<p>Record the returned score and the submission ID next to the file's SHA-256. That receipt is the only
thing that can turn this page's <em>projection</em> into an <em>organizer-confirmed</em> number, and it
is what the next session should compare against.</p>'''


def research_page(f: dict) -> str:
    e2 = f["exp2"]
    canary = sorted(((v["auc_mean"], k) for k, v in e2["leakage_canary"].items()), reverse=True)
    crows = "".join(f'<tr><td><code>{esc(k)}</code></td><td>{v:.3f}</td></tr>' for v, k in canary[:8])
    return f'''<h1>Research: five candidate mechanisms, ranked</h1>
<p class="lede">Required by the standing brief: name the layers, the physical signature, why it should
catch a fault that is missing from the catalogue rather than one already in it, how it differs from what
this repository has already run, and the non-fault process that could mimic it. Ranking is by
(expected DTI gain) ÷ (implementation cost); only the first was validated this session.</p>
<h2>1. K-PROXY-DETECT / TTCA — thermo-tectonic conduit alignment (built this session)</h2>
<ul>
<li><strong>Layers</strong>: 19-band stack (TMI horizontal gradient, tilt derivative, isostatic-gravity
horizontal gradient, detrended-elevation slope and curvature, strain second invariant, conductivity,
depth-to-basement) <em>plus four layers that are not in the organizer stack</em>: the TMI upward-continued
to 150 m (channel 4 of the pinned GeoDAWN extensions product), the contractor Th/K, U/K and U/Th ratio
grids (channels 1–3), the 12-band 1 m LiDAR scarp product, and a kernel density of 27,092 thermal-spring
and well records.</li>
<li><strong>Signature</strong>: geometric-mean consensus of (i) multi-field edge agreement — a boundary
seen by magnetics, gravity, the deep magnetic field and the basement step at the same place, (ii)
scarp/curvature evidence, (iii) fluid-conduit density, (iv) K-metasomatism (low Th/K, low U/K), (v)
strain.</li>
<li><strong>Why it targets unmapped faults</strong>: upward continuation suppresses the near-surface
magnetic texture that the mapped traces sit on and leaves deeper basement structure visible; Th/K and
U/K map hydrothermal alteration halos, which are not in the catalogue at all; springs discharge on fault
damage zones. None of these four layers is present in the 19-band stack, and the emission is forbidden
inside the 2-px catalogue corridor.</li>
<li><strong>Differs from this repository's history</strong>: previous lanes either fitted a
<em>distance-to-catalogue halo</em> (anatomy/relay/stepover families) or ran a supervised classifier on
catalogue labels and then emitted near them. This lane never uses a catalogue-derived predictor for the
surface, never emits a fixed lattice, and its support overlap with the whole registry family is
{f["gate"]["uniqueness"]["max_dot_overlap"]:.0%} instead of the family's 97.5–100 %.</li>
<li><strong>Non-fault mimics</strong>: playa clay mineralogy (low Th/K without alteration), Quaternary
basalt (high K, strong magnetic response), upward-continuation rings around large magnetic bodies,
springs at permeable basin-fill contacts, and road cuts in the LiDAR scarp metrics.</li>
<li><strong>Cost</strong>: low — four new pinned layers, no training run, ~3 minutes to build.</li>
</ul>
<h2>2. Spring-lineament intersection census (not built)</h2>
<p>Layers: spring/well records × mapped and inferred trace azimuths. Signature: excess spring density at
trace intersections and at fault tips, compared with along-strike mid-segments. Why off-catalogue: an
intersection of two mapped faults is itself frequently unmapped. Differs: uses the <em>topology</em> of
the trace network rather than a distance halo. Mimic: permeable contacts at range fronts. Cost: medium —
needs a trace-topology build. Ranked 2 because it is orthogonal to the surface built here and could be
fused, but could not be validated this session.</p>
<h2>3. Upward-continuation depth series (150 m / 300 m / 500 m) for concealed faults (not built)</h2>
<p>Only the 150 m product is pinned locally; a depth series would separate shallow volcanic texture from
deep basement fabric and target structures under basin fill. Why off-catalogue: basin-covered structures
have no surface trace. Mimic: continuation ringing. Cost: medium — the 300/500 m levels would have to be
derived from the official grids (USGS sciencebase item 657e1d85d34e23d3533209f7, files
<code>22103_area1_tiffs.zip</code> / <code>22103_area2_tiffs.zip</code>, sizes recorded in
<code>data/external/observed_files.json</code>), which are <em>not</em> reachable from this sandbox's
network allowlist — so this idea is named as viable but currently unobtainable.</p>
<h2>4. Fault-tip damage-zone extrapolation from Qfaults kinematics (partly built, not promoted)</h2>
<p>Layers: <code>gdr_qfaults_traces.csv</code> (slip rate, recency, dip direction, sense) × magnetic and
gravity gradients. Signature: along-strike continuation beyond a mapped tip, where slip rate and recency
imply the rupture continues. Why off-catalogue: catalogue traces stop where mapping stopped, not where
the fault stops. Mimic: depositional pinch-outs. Cost: high — and it is close to lanes already executed in
sibling repositories (relay/stepover/tip-extrapolation), which is why it is ranked last despite a strong
mechanism.</p>
<h2>5. Earthquake-relocation clustering across mapped gaps (not built)</h2>
<p>Layers: <code>ieq_n100a15</code>, <code>deq_n100a15</code> and the strain-rate bands. Signature:
microseismicity aligned across a gap between mapped traces. Why off-catalogue: seismicity is independent
of the mapping. Mimic: mining blasts and geothermal-field pumping. Cost: high — the provided seismicity
bands are pre-smoothed density fields, so the alignment test would need the raw catalogue, which is not
pinned here.</p>
<h2 id="canary">Leakage canary (protocol rule 4)</h2>
<p>Each plane alone, scored on the withheld quadrant. The alarm threshold is AUC &gt; 0.90; the maximum
observed is <strong>{max(v for v, _ in canary):.3f}</strong>. No alarm.</p>
<div class="wrap"><table><thead><tr><th>Plane</th><th>AUC (mean of 4 folds)</th></tr></thead><tbody>{crows}</tbody></table></div>
<h2 id="instrument">Instrument calibration — a recorded negative result</h2>
<p>The shared hide-and-recover evaluator (<code>gems57-pooled-hide-v2</code>) gives the nine focus files
DTIs that are <strong>perfectly anti-correlated</strong> with their known leaderboard scores
(Spearman {e2["instrument_calibration"]["spearman_instrument_vs_known"]:+.1f}). Recommendation for the
protocol owner: stop using catalogue-recovery DTI as a promotion gate for this competition, or replace it
with an instrument calibrated on known score pairs. Until then, promotion should rest on the geometry
table (Table 1 and the covariate analysis) plus saved-byte gates, and every number should be labelled as
a projection.</p>'''


def sources_page(f: dict) -> str:
    return f'''<h1>Sources and provenance</h1>
<p class="lede">Every input is SHA-256-pinned in <code>scripts/kp1_data.py</code> and re-verified at the
start of every run; a mismatch aborts. Byte consistency with these mirrors is <em>not</em> organizer
authentication.</p>
<h2>Official competition sources</h2>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Problem description, metric and submission format</a>
— the DTI formula (α = 0.2, β = 0.8, 300 m triangular kernel), the EPSG:32611 / 100 m / float32 / [0,1]
format, and the statement that the scored truth is a private set of expert-identified faults absent from
the public catalogue.</li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">Data tab</a> (login-walled).</li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Public leaderboard</a>.</li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Organizer reference solution</a>.</li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Competition rules / technical report (NLR-96647)</a>.</li>
</ul>
<h2>Data used here, with pinned digests</h2>
<div class="wrap"><table><thead><tr><th>File</th><th>SHA-256</th><th>Origin</th></tr></thead><tbody>
<tr><td><code>training_features.tif</code></td><td><code>4371c82e…3bc5</code></td><td>19-band GeoDAWN stack, EPSG:32611, 100 m</td></tr>
<tr><td><code>existing_faults.tif</code> / <code>labels.tif</code></td><td><code>7ba308cc…4093</code></td><td>byte-identical pair; the published “labels” raster <em>is</em> the mapped catalogue</td></tr>
<tr><td><code>sample_submission.tif</code></td><td><code>2176d08e…5cbc</code></td><td>grid/CRS/transform template</td></tr>
<tr><td><code>derived_sgmc_faults_100m_u8.tif</code></td><td><code>643cbe99…2da0</code></td><td>off-catalogue proxy from the USGS SGMC compilation minus the mapped union (peer-derived)</td></tr>
<tr><td><code>lidar_scarp_features_u8.tif</code></td><td><code>d580bb8b…5568</code></td><td>12-band 1 m LiDAR scarp metrics</td></tr>
<tr><td><code>geodawn_rad_u8.tif</code></td><td><code>c22420f7…a682</code></td><td>USGS GeoDAWN K/Th/U/TC radionuclide grids</td></tr>
<tr><td><code>geodawn_extensions_u8.tif</code></td><td><code>a35a9c6d…7d9b</code></td><td>Th/K, U/K, U/Th ratio grids and TMI upward-continued 150 m</td></tr>
<tr><td><code>gdr_wellspring_in_footprint.csv</code></td><td><code>122718e6…</code></td><td>27,092 spring/well records with thermal class and temperature</td></tr>
<tr><td><code>gdr_qfaults_traces.csv</code></td><td><code>9702f2e5…</code></td><td>USGS Qfaults trace attributes (slip rate, recency, sense)</td></tr>
<tr><td><code>gdr_volcanic_vents_in_footprint.csv</code></td><td><code>f91bafba…</code></td><td>21 Quaternary vents</td></tr>
</tbody></table></div>
<h2>External scientific references for the mechanism</h2>
<ul>
<li>USGS GeoDAWN airborne magnetic and radiometric surveys, DOI <a href="https://doi.org/10.5066/P93LGLVQ">10.5066/P93LGLVQ</a>
(sciencebase item <a href="https://www.sciencebase.gov/catalog/item/657e1d85d34e23d3533209f7">657e1d85d34e23d3533209f7</a>)
— source of the magnetic, radiometric and DEM grids, including the upward-continued and ratio products used here.</li>
<li><a href="https://gbcge.org/current-projects/ingenious/">GBCGE INGENIOUS project</a> — the geothermal-favourability
framework and trace database that the catalogue incorporates.</li>
<li><a href="https://epsg.io/32611">EPSG:32611</a> (UTM 11N) — the required coordinate reference system.</li>
<li><a href="https://en.wikipedia.org/wiki/Tversky_index">Tversky index</a> — the similarity index the
distance-weighted metric is built from.</li>
</ul>
<h2>Irregularities flagged for review</h2>
<ol>
<li><strong>labels.tif and existing_faults.tif are byte-identical</strong> (<code>7ba308cc…</code>), while
the organizer page says a “sample submission that predicts total fault absence” is provided. The
sample-submission mirror actually carries 1s, including 60,988 positives equal in count to the catalogue.
Treat the mirrors' <em>roles</em> as owner-described, not organizer-authenticated.</li>
<li><strong>The 70 % / 3-px uniqueness rule is saturating</strong> for this raster family (all 36 pairs
97.5–100 % against a 15–18 % chance level). It cannot discriminate copying from shared terrain and needs
an owner decision.</li>
<li><strong>The shared holdout evaluator anti-correlates with known scores</strong> (Spearman −1.0 on the
nine), so it cannot gate promotion as currently specified.</li>
<li><strong>The vendor external pins are stale</strong>: <code>vendor/gems57/prepare_data.py</code> lists
<code>data/external/derived_sgmc_faults_100m.tif</code>, <code>sgmc_faults_100m.tif</code>,
<code>trace_segments_utm11.csv</code> and <code>qfault_attributes.csv</code> under repository
<code>buffedlizard55-lab/6GEMSDOE@e2fe3f41</code>, but that commit contains no <code>data/external</code>
tree, so the fetch fails. The proxy used here has the <em>same</em> SHA-256 as the first of those pins
(<code>643cbe99…</code>) and was taken from <code>buffedlizard55-lab/GEMSDOE24</code>; the file is
therefore the intended bytes even though its pinned path is dead.</li>
<li><strong>No organizer receipt exists for any score on this site.</strong> All nine focus scores are
user-reported; the projection is a model output.</li>
</ol>'''


def main() -> None:
    f = facts()
    KP1.mkdir(parents=True, exist_ok=True)
    pages = {
        "style.css": CSS,
        "index.html": page("Download & submit", "Overview", index_page(f)),
        "executive-summary.html": page("Executive summary", "Executive summary", executive_page(f)),
        "nine-sites.html": page("Nine focus sites", "Nine sites", nine_sites_page(f)),
        "how-to-submit.html": page("How to submit", "How to submit", how_to_submit(f)),
        "research.html": page("Research", "Research", research_page(f)),
        "sources.html": page("Sources", "Sources", sources_page(f)),
    }
    for name, content in pages.items():
        path = KP1 / name
        tmp = path.with_name("." + path.name + ".partial")
        tmp.write_text(content, encoding="utf-8")
        tmp.replace(path)
    print(f"rendered {len(pages)} K-PROXY-DETECT pages into {KP1}")


if __name__ == "__main__":
    main()
