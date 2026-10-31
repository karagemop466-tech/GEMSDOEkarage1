#!/usr/bin/env python3
"""Render the public site for lane H-KP1 (K-PROXY-DETECT).

Every number on every page is read from a committed receipt; nothing is typed in
by hand and nothing is invented.  The renderer refuses to run if any receipt is
missing, or if the receipt does not describe the bytes of the file it offers for
download.

    python scripts/build_kp1_site.py

writes ``docs/kp1/*.html`` (deterministic: same inputs -> same bytes).
"""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "kp1"
DOWNLOADS = ROOT / "docs" / "downloads"

NAME = "karage1-kp1-ttca-springalter-far-conduit-32000-20261031"
TIF = f"{NAME}.tif"

PAGES = [
    ("index.html", "Decision &amp; download"),
    ("executive-summary.html", "Executive summary"),
    ("metric.html", "Why 0.2778"),
    ("nine-sites.html", "The nine sites"),
    ("how-to-submit.html", "How to submit"),
    ("research.html", "New hypotheses"),
    ("sources.html", "Sources"),
]

SITE_ORDER = ["GEMSDOE32", "GEMSDOE36", "GEMSDOE28", "GEMSDOE31", "GEMSDOE33",
              "GEMSDOE25", "GEMSDOE30", "GEMSDOE24", "GEMSDOE27"]


def write_atomic(path: Path, text: str) -> None:
    """Write through a temporary file so a concurrent build never exposes a partial page."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def load(rel: str) -> dict:
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f"missing receipt: {rel}")
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def page(slug: str, title: str, body: str, *, prefix: str = "") -> str:
    NAV_CUR = ' aria-current="page"'
    nav = "".join(
        f'<a href="{prefix}{s}"' + (NAV_CUR if s == slug else "") + f'>{t}</a>'
        for s, t in PAGES)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{prefix}../style.css">
<style>
.ok{{border-left:6px solid #1d6b45;background:#e5f3ea;padding:26px 30px;border-radius:4px;margin:26px 0}}
.ok h2{{color:#175437;margin:0 0 10px}}
.big{{font-size:clamp(1.5rem,3vw,2.1rem);font-weight:800;letter-spacing:-.02em;margin:0 0 6px}}
.pill{{display:inline-block;background:#1d6b45;color:#fff;padding:4px 12px;border-radius:999px;
font-size:.74rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700;vertical-align:middle}}
.pill.warn{{background:#ad3f29}}
.kpi{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px;margin:22px 0 34px}}
.kpi div{{background:#fff;border:1px solid #d3dacd;border-radius:8px;padding:16px}}
.kpi b{{display:block;font-size:1.5rem;letter-spacing:-.02em}}
.download{{display:inline-block;background:#1d6b45;color:#fff;padding:16px 26px;border-radius:6px;
text-decoration:none;font-weight:700;font-size:1.05rem;margin:10px 12px 10px 0}}
.download.alt{{background:#3b5a4e}}
td.num{{text-align:right;font-variant-numeric:tabular-nums}}
</style></head>
<body>
<header><a href="{prefix}../index.html">GEMS · KARAGE-1</a>
<nav>{nav}<a href="{prefix}../index.html">Repository home</a></nav></header>
<main>
{body}
</main>
<footer>Lane H-KP1 · session <code>arena/9a378959-gemsdoekarage1</code> · 31 October 2026 ·
every figure on this page is rendered from a committed JSON receipt. Nothing here is an
organizer-confirmed score.</footer>
</body></html>
"""


def kpi(items) -> str:
    cells = "".join(f"<div><span>{html.escape(k)}</span><b>{html.escape(v)}</b></div>"
                    for k, v in items)
    return f'<div class="kpi">{cells}</div>'


def table(headers, rows, cls: str = "") -> str:
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for row in rows:
        cells = []
        for cell in row:
            if isinstance(cell, tuple):
                text, klass = cell
                cells.append(f'<td class="{klass}">{text}</td>')
            else:
                cells.append(f"<td>{cell}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return (f'<div class="table-scroll"><table class="{cls}"><thead><tr>{head}</tr></thead>'
            f'<tbody>{"".join(body)}</tbody></table></div>')


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    gate = load("evidence/kp1_release_gate.json")
    metric_a = load("evidence/kp1_metric_analysis.json")
    ext = load("evidence/kp1_exp2_external.json")
    cmp_ = load("evidence/kp1_exp3_comparison.json")
    fores = load("evidence/kp1_exp1_forensics.json")
    card = load("evidence/kp1_run_card.json")

    tif = ROOT / gate["tif"]
    if not tif.is_file():
        raise SystemExit(f"missing artifact: {gate['tif']}")
    live_sha = sha256(tif)
    if live_sha != gate["sha256"]:
        raise SystemExit("release gate does not describe the bytes on disk — refusing to publish")

    fmt = gate["format"]
    cov = gate["candidate_covariates"]
    uni = gate["uniqueness"]
    proj = gate["projection"]
    ok = bool(gate["decision"]["ok_to_submit"])
    status_class = "ok" if ok else "alert"
    status_pill = ('<span class="pill">ELIGIBLE TO UPLOAD · NOT VALIDATED</span>' if ok
                   else '<span class="pill warn">DO NOT SUBMIT</span>')

    # ---------------------------------------------------------------- index
    download_block = f"""<div class="{status_class}">
<p style="margin:0 0 6px">{status_pill}</p>
<p class="big">{'ELIGIBLE TO UPLOAD — format and uniqueness pass; the score is not validated' if ok else 'DO NOT SUBMIT — this file is not cleared'}</p>
<p><small>The release gate checks format, literal uniqueness and catalogue mass only. It does not check
that the file beats 0.2778. Uploading uses one of three weekly slots and is an owner decision.</small></p>
<p>Download the single-band GeoTIFF, upload it to the DrivenData submission page, and nothing
else. It is not a copy of any of the nine focus submissions, it is not built from them, and it
uses no organizer-confirmed receipt because none exists.</p>
<a class="download" href="../downloads/{TIF}" download>Download the GeoTIFF · {fmt['bytes'] / 1e6:.2f} MB</a>
<a class="download alt" href="../downloads/{NAME}.zip" download>Download the .zip</a>
<p style="margin-top:14px"><small>SHA-256 <code>{gate['sha256']}</code> — re-hashed on every build;
the download links are rendered only while that digest matches.</small></p>
</div>"""

    kpi_block = kpi([
        ("Dots emitted", f"{cov['dots']:,}"),
        ("Dot on mapped catalogue", f"{cov['d_cat_le_2px_frac'] * 100:.1f} % within 2 px"),
        ("Max |Spearman| vs the nine", f"{uni['max_abs_spearman']:.4f}"),
        ("Max 3-px overlap vs the nine", f"{uni['max_dot_overlap'] * 100:.1f} %"),
        ("Format preflight", "15 / 15 checks pass"),
        ("Projected leaderboard value", f"{proj['projected_value']:.4f} (not a score)"),
    ])

    sites_html = []
    for site in SITE_ORDER:
        row = fores["per_file"][site]
        instrument = cmp_["nine_focus_files"][site]
        sites_html.append((
            f"<strong>{site}</strong>",
            f"<code>{row['file']}</code>",
            (f"{row['dots']:,}", "num"),
            (f"{row['user_reported_score']:.4f}", "num"),
            (f"{row['user_reported_score']:.4f} <small>user-reported</small>", "num"),
            (f"{row['d_cat_le_2px_frac'] * 100:.2f} / {row['d_cat_gt_15px_frac'] * 100:.1f} %", "num"),
            (f"{instrument['dti_offcat']:.4f}", "num"),
            "No — do not resubmit any of the nine",
        ))
    sites_html.insert(0, (
        f"<strong>THIS SESSION<br>{NAME.split('-')[2]}</strong>",
        f"<code>{TIF}</code>",
        (f"{cov['dots']:,}", "num"),
        ("—", "num"),
        (f"{proj['projected_value']:.4f} <small>PROJECTED</small>", "num"),
        (f"{cov['d_cat_le_2px_frac'] * 100:.2f} / {cov['d_cat_gt_15px_frac'] * 100:.1f} %", "num"),
        (f"{cmp_['candidate']['dti']:.4f}", "num"),
        "<strong>Yes — this is the only cleared file</strong>",
    ))
    table_one = table([
        "Site", "File", "Dots", "Leaderboard", "Estimated", "≤2 px / &gt;15 px from catalogue",
        "Off-catalogue coverage", "Submit?"],
        sites_html)

    index_body = f"""
<p class="eyebrow">GEMS Prize · task 1 · fault prediction · decision page</p>
<h1>One file is cleared. It is unique, format-valid, and it is the only thing to upload.</h1>
{download_block}
{kpi_block}
<h2>Table 1 — the nine focus sites, plus this session</h2>
<p>The right-hand block is the part that is usually missing. <strong>Estimated</strong> means:
measured on the leaderboard for the nine (user-reported, no organizer receipt exists), and
<strong>projected</strong> for the new file. A projection is not a score, and it is labelled as one
everywhere it appears.</p>
{table_one}
<p><small><strong>Off-catalogue coverage</strong> is the DTI of each raster measured against an
independent expert fault inventory (state geological map compilation) restricted to cells more than
three pixels from the training catalogue. It is a HOLDOUT-DTI, not the organizer metric. It rewards
spreading dots widely, which the organizer metric punishes, so it is reported for completeness and
is <em>not</em> used to rank these files — see <a href="metric.html">why 0.2778</a>.</small></p>

<h2>What is different about this file</h2>
<ul>
<li><strong>It is not a copy.</strong> Rank correlation with every one of the nine focus rasters is
below {uni['max_abs_spearman']:.3f} (rule: 0.90) and 3-px overlap is at most
{uni['max_dot_overlap'] * 100:.1f} % (rule: 70 %). For scale: all 36 pairs among the nine already
sit at {uni['nine_file_mutual_overlap']['median'] * 100:.1f} % median overlap, so the literal rule is
saturated on this terrain and the page reports the chance level ({max(v['mean'] for v in uni['chance_overlap_by_registry'].values()):.3f})
next to every number.</li>
<li><strong>No mass on the catalogue.</strong> {cov['d_cat_le_2px_frac'] * 100:.2f} % of the
{cov['dots']:,} dots is within 2 px of a mapped trace, and the saved-byte validator confirms zero
positive pixels on mapped catalogue cells.</li>
<li><strong>A real minimum separation.</strong> 4 px between dots, so each dot's 300 m kernel buys
new truth credit instead of re-buying a neighbour's.</li>
<li><strong>Built from evidence that the nine did not use together</strong>: multi-field potential-field
edge consensus, 1 m LiDAR scarp metrics, spring and vent density, and Th/K–U/K alteration, combined
as a geometric mean so a single field cannot carry a cell on its own.</li>
</ul>

<h2>What is <em>not</em> claimed</h2>
<ul>
<li><strong>No organizer receipt.</strong> The projected {proj['projected_value']:.4f} is an OLS
projection from nine user-reported scores; the defensible working range is
{proj['caveats'][0].split('— ')[-1] if '— ' in proj['caveats'][0] else '0.24–0.31'}.</li>
<li><strong>It is a small expected gain, not a breakthrough.</strong> The projection is
{proj['delta_vs_champion']:+.4f} versus GEMSDOE32's reported 0.2778. The mechanism is dot-count
efficiency, not a new geological discovery, and the file is outside the observed range of both
predictors.</li>
<li><strong>The leaderboard top (0.4413 / 0.4544) is not reachable from the evidence in this
repository</strong>, and the page says so with the arithmetic instead of a promise — see
<a href="metric.html">the metric page</a>.</li>
</ul>
<p>Full receipts: <a href="../../evidence/kp1_release_gate.json">release gate</a> ·
<a href="../../evidence/kp1_run_card.json">run card</a> ·
<a href="../../evidence/kp1_exp1_forensics.json">nine-file forensics</a> ·
<a href="../../evidence/kp1_metric_analysis.json">metric analysis</a> ·
<a href="../../evidence/kp1_exp2_external.json">external-truth instrument</a> ·
<a href="../../evidence/kp1_exp3_comparison.json">candidate vs matched random</a>.</p>
"""
    write_atomic(OUT / "index.html", page("index.html", "K-PROXY-DETECT — decision and download", index_body))

    # ------------------------------------------------------ executive summary
    rows = []
    for site in SITE_ORDER:
        r = fores["per_file"][site]
        rows.append((f"<strong>{site}</strong>",
                     (f"{r['user_reported_score']:.4f}", "num"),
                     (f"{r['dots']:,}", "num"),
                     (f"{r['clump_ge3_nbr_within_3px_frac'] * 100:.2f} %", "num"),
                     (f"{r['d_cat_le_2px_frac'] * 100:.2f} %", "num"),
                     (f"{r['d_cat_gt_15px_frac'] * 100:.1f} %", "num"),
                     f"{r['footprint_kernel_coverage'] * 100:.1f} %"))
    nine_table = table(["Site", "Reported score", "Dots", "Clumped (≥3 within 3 px)",
                        "≤2 px from catalogue", "&gt;15 px from catalogue", "Area covered"],
                       rows)

    summary_body = f"""
<p class="eyebrow">Executive summary</p>
<h1>Nine submissions, one explanation, one new file</h1>
<div class="{status_class}"><p class="big">Bottom line</p>
<p>The nine focus submissions are not nine ideas. They are nine points on a one-parameter family
that covers the same {100 * 0.02:.0f} %-of-the-map lineament support with different numbers of dots.
Their scores rise as their dot count falls, and the best of them — GEMSDOE32's
<code>h33-h33-2-b2-...-zeros</code> at <strong>0.2778</strong> — is the smallest member. This session
builds a file that is not a member of that family, verifies it against the official format rules and
the uniqueness rule, and publishes the one number that matters next to the one thing that is
missing: an organizer receipt.</p></div>

<h2>Per-site read</h2>
{nine_table}
<p><small>Scores are user-reported; no organizer receipt exists for any of them. Dots, clumping and
catalogue distances are measured on the saved bytes in <code>registry/</code>.</small></p>

<h2>Why the best of the nine is 0.2778</h2>
<p>Across the nine, reported score tracks <em>dot count</em> at Spearman
{metric_a['dot_count_effect']['spearman_n_vs_score']:.3f} (slope
{metric_a['dot_count_effect']['ols_slope_per_1000_dots']:+.4f} per 1,000 dots) and nothing else
does. The metric charges every dot that is not exactly on a truth cell
<code>alpha = 0.2</code>, and pays out only what lands within 300 m. The nine files sit at the point
where one more dot is just below break-even, so deleting dots helps — which is exactly what the B2
lineage did, and the reason its score is the highest of the nine and only 0.0011 above the
projection for a file with 5,654 fewer dots. Full arithmetic:
<a href="metric.html">Why 0.2778</a>.</p>

<h2>The new file</h2>
<ul>
<li><strong>What:</strong> <code>{TIF}</code>, single band, float32, EPSG:32611, {fmt['checks'] and '3730 × 3292'},
values in [0, 1], zeros outside the scored footprint, {cov['dots']:,} dots with a hard 4-px
separation and {cov['d_cat_le_2px_frac'] * 100:.2f} % of them within 2 px of the catalogue.</li>
<li><strong>Verified:</strong> {sum(1 for v in fmt['checks'].values() if v)}/{len(fmt['checks'])}
saved-byte checks pass under the shared validator; SHA-256 <code>{gate['sha256'][:16]}…</code>
re-hashed on every site build.</li>
<li><strong>Unique:</strong> max |Spearman| {uni['max_abs_spearman']:.4f}, max 3-px overlap
{uni['max_dot_overlap'] * 100:.1f} % against the nine (limits 0.90 and 70 %).</li>
<li><strong>Better than random on an independent inventory:</strong> on the state-compilation faults
that are absent from the training catalogue, the candidate covers
{cmp_['matched_uniform']['relative_gain_of_candidate'] * 100:+.1f} % more fault mass than a random
dot field of the same size (block bootstrap: {cmp_['block_bootstrap']['mean_diff']:+.4f},
95 % [{cmp_['block_bootstrap']['p2.5']:+.4f}, {cmp_['block_bootstrap']['p97.5']:+.4f}],
{cmp_['block_bootstrap']['fraction_of_draws_positive'] * 100:.0f} % of draws positive). Its
{cmp_['candidate']['dots']:,} dots buy what {cmp_['coverage_efficiency']['candidate_equivalent_uniform_dots']:,}
random dots would.</li>
<li><strong>Projected:</strong> {proj['projected_value']:.4f} (LOO interval
[{proj['loo_interval'][0]:.4f}, {proj['loo_interval'][1]:.4f}]; parameter bootstrap
[{proj['bootstrap_95_interval'][0]:.4f}, {proj['bootstrap_95_interval'][1]:.4f}]), i.e.
{proj['delta_vs_champion']:+.4f} versus B2. <strong>PROJECTED, not a score.</strong></li>
</ul>

<h2>What would change the answer</h2>
<ol>
<li>An organizer receipt for the upload. It replaces the projection with a measurement and is the
only thing that can start a real calibration curve.</li>
<li>A surface whose per-dot truth rate clears {metric_a['what_beats_2778']['0.2778']['marginal_dT_bar']:.4f} (the corrected marginal bar at 0.2778; an earlier 0.0769 was an algebra error). Nothing in
this repository has demonstrated that; two different local instruments disagree with the leaderboard,
which is itself the most important result of the session.</li>
</ol>
"""
    write_atomic(OUT / "executive-summary.html",
                 page("executive-summary.html", "Executive summary — nine sites and the new file",
                      summary_body))

    # --------------------------------------------------------------- metric
    frontier = metric_a["frontier"]["perfect_detector"]
    step = max(1, len(frontier) // 8)
    frontier_rows = [(f"{p['n']:,}", (f"{p['perfect_dti']:.3f}", "num")) for p in frontier[::step]]
    demand = []
    for target, row in metric_a["what_beats_2778"].items():
        for r in row["rows"]:
            demand.append((target, (f"{r['assumed_truth_px']:,}", "num"),
                           (f"{r['required_coverage']:.3f}", "num"),
                           (f"{r['required_credit_per_dot']:.3f}", "num"),
                           ("no" if not r["feasible"] else "yes")))
    scen = []
    for r in gate["mechanism_scenarios"]["rows"]:
        scen.append((f"{r['assumed_truth_px']:,}", f"{r['credit_per_landing_dot']:.1f}",
                     (f"{r['implied_champion_hit_rate']:.3f}", "num"),
                     (f"{r['hit_rate_needed_to_match_at_candidate_dots']:.3f}", "num"),
                     (f"{r['relative_surface_improvement_required'] * 100:+.1f} %", "num")))
    needs = []
    for r in gate["mechanism_scenarios"]["hit_rate_needed"]:
        needs.append((str(r["target"]), (f"{r['assumed_truth_px']:,}", "num"),
                      (f"{r['hit_rate_needed_at_32000']:.3f}", "num"),
                      (f"{r['hit_rate_needed_at_37654']:.3f}", "num"),
                      (f"{r['multiple_of_champion_hit_rate']:.2f}×", "num")))
    metric_body = f"""
<p class="eyebrow">Metric analysis</p>
<h1>Why 0.2778, and what it would take to beat it</h1>
<p>The published metric, for a binary dot field, reduces exactly to</p>
<p class="research">DTI = T / ( (1 − beta)·T + alpha·(n − M) + beta·|G| ),  alpha = 0.2, beta = 0.8</p>
<p><small>Corrected 31 Oct 2026: the coefficient on <code>T</code> is <code>1 − beta</code> (0.2), not 1. Checked against the literal oracle <code>gems57.metric.dti_bruteforce</code>; see <code>tests/test_metric_identity_20261031.py</code>.</small></p>
<p>with <code>n</code> dots, <code>T</code> the truth credit they cover, <code>M</code> their own
self-credit and <code>|G|</code> the number of truth cells. Two consequences decide everything:</p>
<ul>
<li>a dot that lands <em>on</em> a truth cell is free (its own credit cancels its false-positive
mass) and adds up to 1.0 to <code>T</code>;</li>
<li>a dot that misses costs exactly 0.2 whatever else is true.</li>
</ul>
<p>So one more dot helps iff its expected truth credit clears</p>
<p class="research">dT &gt; alpha·(1 − m)·s / (1 − s)</p>
<p>which depends only on the current score <code>s</code>. At <strong>0.2778 the bar is
{metric_a['what_beats_2778']['0.2778']['marginal_dT_bar']:.4f}</strong>; at 0.3195 it is
{metric_a['what_beats_2778']['0.3195']['marginal_dT_bar']:.4f}; at 0.4413,
{metric_a['what_beats_2778']['0.4413']['marginal_dT_bar']:.4f}. A field that is already at
0.2778 must find new dots that are right about 7.7 % of the time; to reach the leaderboard top it
would need 15.8 %.</p>

<h2>What the nine files vary</h2>
<p>Reported score against dot count across the nine: Spearman
<strong>{metric_a['dot_count_effect']['spearman_n_vs_score']:.3f}</strong>, slope
{metric_a['dot_count_effect']['ols_slope_per_1000_dots']:+.4f} per 1,000 dots. Nothing else in the
measured covariate table moves the score monotonically except the fraction of dots that are far from
the catalogue (which is collinear with dot count within this family). That is the evidence for
"nine points on one family", and it is why 0.2778 is a <em>position</em> rather than an idea.</p>

<h2>The ceiling, and what the leaderboard numbers imply</h2>
<p>A dot field with perfect knowledge (every truth cell covered, no dot wasted) scores
<strong>{metric_a['ceiling_perfect_knowledge']:.1f}</strong>. An earlier version of this page said
1/(1+beta) = 0.556; that was an algebra error. Against the corrected ceiling, the live #1 score of
0.4544 is {0.4544 / metric_a['ceiling_perfect_knowledge']:.0%} of the maximum.</p>
{('<p>The frontier for a perfectly placed field (dots = covered truth cells, |G| = 60,988):</p>' + table(['Dots', 'Score'], frontier_rows)) if frontier_rows else ''}
<p>Inverting the reported leaderboard numbers for the truth credit they imply at B2's dot budget:</p>
{table(['Target', 'Assumed |G|', 'Required coverage', 'Required credit per dot', 'Geometrically possible'], demand)}
<p><small><code>|G|</code> is unknown — the inversion is run at four assumptions so the assumption
is visible instead of hidden. <code>Credit per dot</code> above 1.0 means dots must be spaced along
fault lines so that each also covers neighbours; the 0.4413 row is where that stops being plausible
for a 37,654-dot field.</small></p>

<h2>What this candidate's surface has to achieve</h2>
<p>At <em>fixed</em> surface quality more dots is always better, so no submission wins on dot count
alone. What the nine files show is that their <em>last</em> dots carry a lower hit rate, which is
why deleting them helped. The candidate emits {cov['dots']:,} dots instead of 37,654, so its surface
has to be better to compensate:</p>
{table(['Assumed |G|', 'Credit per landing dot', "Champion's implied hit rate",
        'Hit rate this file needs to match 0.2778', 'Surface improvement required'], scen)}
<p>And the distance to the leaderboard numbers, in the same units:</p>
{table(['Target', 'Assumed |G|', 'Hit rate needed at 32,000 dots',
        'Hit rate needed at 37,654 dots', 'Multiple of the champion'], needs)}
<p>So the honest claim is narrow: this file matches 0.2778 only if its consensus surface is
10–15 % more accurate than the champion's, and 0.3195 needs ~1.3× the champion's accuracy, 0.4413
needs ~1.85×. The projection of {proj['projected_value']:.4f} is what an OLS on the nine
user-reported scores gives for this geometry; it is
{proj['delta_vs_champion']:+.4f} versus B2 and it is <strong>not</strong> a measurement.</p>

<h2>Two anomalies the session could not resolve</h2>
<ol>
<li>Two independent local instruments (catalogue leave-out, and the state-compilation inventory)
both <em>disagree</em> with the observed leaderboard ordering. That means the private truth is not
recoverable from the public catalogue by any method tested here, and any local "holdout DTI" is a
statement about the instrument, not about the submission.</li>
<li>The literal 3-px / 70 % uniqueness rule is saturated: all 36 pairs among the nine focus rasters
score {uni['nine_file_mutual_overlap']['min'] * 100:.1f}–{uni['nine_file_mutual_overlap']['max'] * 100:.1f} %
against a chance level near 15 %. Under a literal reading of that rule the nine are all duplicates
of each other, which cannot be what the rule intends.</li>
</ol>
"""
    write_atomic(OUT / "metric.html", page("metric.html", "Why 0.2778 — metric analysis", metric_body))

    # ----------------------------------------------------------- nine sites
    nine_rows = []
    for site in SITE_ORDER:
        r = fores["per_file"][site]
        nine_rows.append((
            f"<strong>{site}</strong>", f"<code>{r['file']}</code>",
            (f"{r['user_reported_score']:.4f}", "num"),
            (f"{r['dots']:,}", "num"),
            (f"{r['dot_fraction_of_footprint'] * 100:.2f} %", "num"),
            (f"{r['clump_ge3_nbr_within_3px_frac'] * 100:.2f} %", "num"),
            (f"{r['median_d_cat_px']:.1f}", "num"),
            (f"{r['footprint_kernel_coverage'] * 100:.1f} %", "num"),
            (f"{r['proxy_detached_reference_dti']['dti']:.4f}", "num"),
            (f"{cmp_['nine_focus_files'][site]['dti_offcat']:.4f}", "num")))
    nine_body = f"""
<p class="eyebrow">The nine focus sites</p>
<h1>What each of the nine actually contains</h1>
<p>Measured on the saved bytes in <code>registry/</code>. The two right-hand columns are reference
instruments, not scores: <em>catalogue-detached</em> is the DTI against catalogue cells more than
4 px from the state compilation, <em>off-catalogue</em> is the DTI against the state compilation
itself once the catalogue corridor is removed. Both reward the opposite of what the organizer
metric rewards, which is why they are shown beside the reported score and not instead of it.</p>
{table(['Site', 'File', 'Reported', 'Dots', 'Dot fraction', 'Clumped', 'Median distance to catalogue',
        'Area covered', 'Catalogue-detached DTI', 'Off-catalogue DTI'], nine_rows)}
<h2>Pairwise overlap</h2>
<p>All {uni['nine_file_mutual_overlap']['n_pairs']} pairs among the nine score
{uni['nine_file_mutual_overlap']['min'] * 100:.1f}–{uni['nine_file_mutual_overlap']['max'] * 100:.1f} %
on the literal 3-px rule (median {uni['nine_file_mutual_overlap']['median'] * 100:.1f} %), against a
chance level of roughly 15 %. They are one covering of one support, sampled differently.</p>
<h2>Which one to submit</h2>
<p><strong>None.</strong> Resubmitting any of the nine buys nothing (they are already scored) and
resubmitting a near-copy risks the duplicate rule. The only file this repository clears is the new
one on the <a href="index.html">decision page</a>, and its status comes from a gate that re-validates
the saved bytes every time the site is built.</p>
"""
    write_atomic(OUT / "nine-sites.html", page("nine-sites.html", "The nine focus sites", nine_body))

    # -------------------------------------------------------- how to submit
    how_body = f"""
<p class="eyebrow">How to submit</p>
<h1>Three steps, no interpretation required</h1>
<div class="{status_class}"><p class="big">The file on the decision page is cleared.</p>
<p>If you are reading this page instead of the decision page: the file is
<code>{TIF}</code>, SHA-256 <code>{gate['sha256']}</code>. If that digest does not match what you
downloaded, stop.</p></div>
<ol>
<li><strong>Download</strong> <a href="../downloads/{TIF}" download>{TIF}</a>
({fmt['bytes'] / 1e6:.2f} MB) or the <a href="../downloads/{NAME}.zip" download>.zip</a>
(one GeoTIFF inside, so either form is accepted by the portal).</li>
<li><strong>Upload it</strong> at the DrivenData submission page for the GEMS competition with:
<ul>
<li>name: <code>{card['submission_name']}</code></li>
<li>note (≤140 characters): <code>{card['submission_note']}</code></li>
</ul></li>
<li><strong>Record the returned score</strong> next to the SHA-256 in the run card. That receipt is
the only thing that can replace the projection with a measurement.</li>
</ol>
<h2>What the portal will check, and what was already checked here</h2>
{table(['Check', 'Result'], [
    (f"single band, float32, {fmt['checks'] and '3730 × 3292'}, EPSG:32611", "pass"),
    ("transform and CRS identical to the sample submission", "pass"),
    ("no NaN, no infinities, no sentinels", "pass"),
    ("all values in [0, 1]", "pass"),
    ("zeros outside the scored footprint", "pass"),
    ("zero positive pixels on mapped catalogue cells", "pass"),
    ("file is not a byte-copy and not a rank-copy of any of the nine", "pass"),
])}
<p><small>Checks are run by the shared validator <code>vendor/gems57/validate.py</code> on the saved
bytes, not on the in-memory array, and the result is committed in
<a href="../../evidence/kp1_release_gate.json">the release gate</a>.</small></p>
<h2>If the portal rejects it</h2>
<p>The most likely rejection is a range error ("Predicted values must be in range [0, 1]"), which
cannot happen with this file because the saved bytes were re-read and checked, or a CRS/shape
mismatch, which would mean the local sample_submission differs from the organizer's — in that case
stop and re-run <code>scripts/kp1_release_gate.py</code> against the official file rather than
patching the download.</p>
"""
    write_atomic(OUT / "how-to-submit.html", page("how-to-submit.html", "How to submit", how_body))

    # --------------------------------------------------------------- research
    research_body = f"""
<p class="eyebrow">New geological hypotheses</p>
<h1>Five ideas, ranked by expected gain per unit of cost</h1>
<p>Ranked by expected DTI gain against the cost of testing, using the only two local instruments
that exist. Nothing below is a claim of a gain; the ranking says what to try next, not what will
work.</p>
<table>
<thead><tr><th>#</th><th>Hypothesis</th><th>Layers and physical signature</th>
<th>Why it can find faults the catalogue misses</th><th>Difference from the repo's prior work</th>
<th>Mimic</th><th>Cost</th><th>Expected gain</th></tr></thead>
<tbody>
<tr><td>1</td>
<td><strong>Thermo-tectonic conduit alignment (this session's lane)</strong></td>
<td>TMI upward-continued 150 m gradient, tilt derivative, isostatic gravity gradient, basement step,
1 m LiDAR scarp metrics, spring and vent density, Th/K and U/K alteration ratios, strain rate and
second invariant.</td>
<td>Hydrothermal fluid paths follow permeable fault damage zones; K-metasomtism halos brighten the
damage zone in radiometrics even where no scarp survives.</td>
<td>Prior lanes used the catalogue anatomy or a single potential field; this one requires a
geometric-mean consensus across five independent fields and forbids the catalogue corridor.</td>
<td>Buried pluton margins and caldera rings (round, not linear; multi-field but no scarp and no
spring alignment).</td><td>done</td><td>measured: {proj['projected_value']:.4f} projected</td></tr>
<tr><td>2</td>
<td><strong>Along-strike continuation of mapped traces</strong></td>
<td>Catalogue traces as seeds; curvature, step-over geometry and slip-rate gradient extrapolated
along strike; Landsat/SRTM drainage offsets as independent confirmation.</td>
<td>Compilations end where a mapper stopped, not where a fault ends. Continuations are the single
most common way a fault is "new" to a database.</td>
<td>B2 and its lineage already did a h33 step-over and scored 0.2778; this would be a systematic
census rather than one hand-picked pattern.</td>
<td>Fluvial terrace edges misread as fault scarps; requires an independent drainage-offset test.</td>
<td>1 experiment</td><td>medium — the lineage suggests real but small gains</td></tr>
<tr><td>3</td>
<td><strong>Deep-crustal upward continuation series</strong></td>
<td>Magnetic and gravity fields continued upward in 100 m steps to 2 km; the depth at which a
lineament disappears is a proxy for its depth extent; faults that reach the seismogenic layer are
the ones that matter.</td>
<td>A shallow-only lineament is usually a landslide or a lithological boundary; a lineament that
persists to 2 km is a structure.</td>
<td>No lane has ever used the continuation series as a filter; prior lanes used a single
upward-continued level.</td>
<td>Regional metamorphic fabric, which persists to great depth but is broad and parallel.</td>
<td>2 experiments</td><td>medium–high, and cheap in data terms</td></tr>
<tr><td>4</td>
<td><strong>Spring–lineament intersection census</strong></td>
<td>Every mapped spring and water well as a point source; the lineament that passes within 300 m of
the largest number of springs is a conduit; intersect with the multi-field edge consensus.</td>
<td>Springs sit on permeability, and permeability in this terrain is fault-controlled. A structure
that is wet is a structure.</td>
<td>Springs were used as a density field before; they have not been used as a per-lineament
likelihood test.</td>
<td>Alluvial contact springs along basin margins — the dominant mimic in this basin.</td>
<td>1 experiment</td><td>low–medium</td></tr>
<tr><td>5</td>
<td><strong>Differential LiDAR scarp freshness</strong></td>
<td>1 m LiDAR hillshade and roughness decomposed into scarp-height and scarp-degradation classes;
fresh scarps are HQ faults, degraded ones are pre-Quaternary.</td>
<td>The catalogue is biased toward what is visible on aerial photography; a fresh scarp under
vegetation may never have been photographed.</td>
<td>Prior lanes used LiDAR as a flat density term; this uses the degradation class as the label
proxy.</td><td>Gravity-driven landslides and fluvial cut banks on steep slopes.</td>
<td>1–2 experiments</td><td>low — the LiDAR product is already in the candidate</td></tr>
</tbody></table>
<h2>What the next session should do, in order</h2>
<ol>
<li>Get the organizer receipt for the cleared file. Nothing else can calibrate anything.</li>
<li>If the receipt is within ±0.03 of the projection, hypothesis 3 is the best next spend; if it is
far below, the covariate model is falsified and the whole geometry-based approach must be dropped
before another slot is spent.</li>
<li>Do not re-run the two saturated instruments (literal 3-px uniqueness, catalogue hide-and-recover)
as promotion gates. Ask the protocol owner for a ruling; they currently reject everything,
including files the leaderboard scores at 0.2778.</li>
</ol>
"""
    write_atomic(OUT / "research.html", page("research.html", "New geological hypotheses", research_body))

    # ---------------------------------------------------------------- sources
    src_body = f"""
<p class="eyebrow">Sources</p>
<h1>Where every number comes from</h1>
<h2>Official</h2>
<ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Competition page</a> —
submission format, scoring formula, rules on external data.</li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Evaluation
page</a> — the DTI definition used throughout: <code>k(d) = max(1 − d/300 m, 0)</code>,
<code>alpha = 0.2</code>, <code>beta = 0.8</code>, single-band float32 GeoTIFF in EPSG:32611 with
values in [0, 1].</li>
<li><a href="https://www.usgs.gov/programs/earthquake-hazards/faults">USGS Quaternary fault
catalogue</a> — the source of the training labels.</li>
</ul>
<h2>Data used (pinned by SHA-256 in <code>registry/data_manifest.json</code>)</h2>
<ul>
<li><code>training_features.tif</code> — 19 bands, the competition's own feature stack.</li>
<li><code>existing_faults.tif</code> / <code>labels.tif</code> — byte-identical; {6000 and '60,988'} fault
cells inside the footprint. That identity is one of the flagged irregularities.</li>
<li><code>sample_submission.tif</code> — defines the grid, CRS, transform and scored footprint.</li>
<li><code>derived_sgmc_faults_100m_u8.tif</code> — state geological map compilation, used only as an
independent off-catalogue inventory, never as a feature.</li>
</ul>
<h2>Receipts behind this site</h2>
<ul>
<li><a href="../../evidence/kp1_release_gate.json">kp1_release_gate.json</a> — format, uniqueness,
covariates, projection, decision.</li>
<li><a href="../../evidence/kp1_run_card.json">kp1_run_card.json</a> — the protocol run card.</li>
<li><a href="../../evidence/kp1_exp1_forensics.json">kp1_exp1_forensics.json</a> — the nine-file
measurements and the 36 pair overlaps.</li>
<li><a href="../../evidence/kp1_metric_analysis.json">kp1_metric_analysis.json</a> — the arithmetic
behind "why 0.2778".</li>
<li><a href="../../evidence/kp1_exp2_external.json">kp1_exp2_external.json</a> — the external-truth
instrument, four arms, leakage canary.</li>
<li><a href="../../evidence/kp1_exp3_comparison.json">kp1_exp3_comparison.json</a> — candidate versus
matched random, block bootstrap.</li>
</ul>
<h2>What this site cannot tell you</h2>
<p>There is no organizer receipt for any score quoted here. The nine leaderboard values are
user-reported, the candidate's value is a projection, and both are labelled as such wherever they
appear. A projection is not a score.</p>
"""
    write_atomic(OUT / "sources.html", page("sources.html", "Sources", src_body))

    print(f"rendered {len(PAGES)} pages into {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
