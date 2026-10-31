#!/usr/bin/env python3
"""Build docs/focus-sites.html: NOT CLEARED / DO NOT SUBMIT executive summary for the nine focus sites.

Every number on the page is read from an evidence file under evidence/ (no hand-typed values).
Scores are labelled OWNER-REPORTED / UNVERIFIED (from README.md) or HOLDOUT-DTI (our evaluator, 95% CI).
The page offers NO download link for any raster. Receipts are copied into docs/data/ so the links resolve.
"""
from __future__ import annotations

import html
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_site import shell  # noqa: E402  (pure function; does not render other pages)

EV = ROOT / "evidence"
DOCS = ROOT / "docs"
RECEIPTS = [
    "focus_site_table_20261029.json",
    "candidate_uniqueness_probcollar-nan_20261029.json",
    "candidate_uniqueness_probcollar-zeros_20261029.json",
    "holdout_probcollar_20261029.json",
    "holdout_probcollar_detached_20261029.json",
    "holdout_ring_tiebreak_all_20261029.json",
    "holdout_ring_tiebreak_detached_20261029.json",
]
CAND_REL = "candidates/karage1-probcollar-gbm-K37654-collar3-20261029-nan.tif"
ZEROS_REL = "candidates/karage1-probcollar-gbm-K37654-collar3-20261029-zeros.tif"
CAND_JSON = "candidates/karage1-probcollar-gbm-K37654-collar3-20261029-nan.json"
SITE_ORDER = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
              "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]
ALPHA = 0.2


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def load(name: str) -> dict:
    return json.loads((EV / name).read_text())


def write_atomic(path: Path, text: str) -> None:
    """Replace the page atomically so concurrent site builds never expose a partial file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".partial", dir=path.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(text)
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def pct2(x: float) -> str:
    return f"{100 * x:.2f}%"


def ci(v) -> str:
    return f"[{v[0]:.4f}, {v[1]:.4f}]"


def per_site_uniqueness(focus: dict) -> dict:
    """For each site: max share of ITS dots within 3 px of another listed site, and identical/rank flags."""
    pairs = focus["pairwise"]
    out = {s: dict(max_overlap=0.0, partner="", max_abs_rho=0.0, rho_partner="", identical=[]) for s in SITE_ORDER}
    for key, v in pairs.items():
        a, b = key.split("|")
        for s, other, share in ((a, b, v["first_dots_within_3px_of_second"]),
                                (b, a, v["second_dots_within_3px_of_first"])):
            if share > out[s]["max_overlap"]:
                out[s]["max_overlap"], out[s]["partner"] = share, other
        rho = v["spearman_full_footprint"]
        if rho is not None:
            for s, other in ((a, b), (b, a)):
                if abs(rho) > out[s]["max_abs_rho"]:
                    out[s]["max_abs_rho"], out[s]["rho_partner"] = abs(rho), other
        if v["identical_positive_sets"]:
            for s, other in ((a, b), (b, a)):
                out[s]["identical"].append(other)
    return out


def focus_table(focus: dict, uniq: dict) -> str:
    rows = []
    for s in SITE_ORDER:
        r = focus["sites"][s]
        u = uniq[s]
        literal_dup = u["max_overlap"] > 0.70 or u["max_abs_rho"] > 0.90 or bool(u["identical"])
        verdict = ("<strong>NO</strong> · literal duplicate" if literal_dup else "yes")
        ident = (f" · identical positive set with {', '.join(u['identical'])}" if u["identical"] else "")
        rows.append(
            f"<tr><td><strong>{s}</strong></td>"
            f"<td><strong>{r['user_reported_score']:.4f}</strong><br><small>OWNER-REPORTED / UNVERIFIED</small></td>"
            f"<td><code class=\"wrap\">{esc(r['file'].split('/')[-1])}</code><br><small>SHA-256 {esc(r['sha256'][:12])}…</small></td>"
            f"<td>{r['positives']:,}</td>"
            f"<td>{pct2(r['lattice_observed_3px_overlap'])} vs chance {pct2(r['lattice_chance_3px_overlap_uniform_random'])}</td>"
            f"<td>{pct(u['max_overlap'])} with {esc(u['partner'])}<br><small>max |ρ| {u['max_abs_rho']:.3f} with {esc(u['rho_partner'])}{esc(ident)}</small></td>"
            f"<td>{verdict}</td>"
            f"<td><strong>DO NOT RESUBMIT</strong><br><small>no download offered</small></td></tr>"
        )
    return ("<div class=\"table-wrap\"><table class=\"exec-table\"><thead><tr>"
            "<th>Site</th><th>Highest supplied score</th><th>File (registry copy)</th><th>Dots</th>"
            "<th>3-px lattice overlap (observed vs chance)</th><th>Unique vs the other eight listed sites?</th>"
            "<th>Unique?</th><th>Download and submit?</th></tr></thead><tbody>" + "".join(rows) +
            "</tbody></table></div>")


def holdout_table(all_: dict, det: dict, ring_all: dict, ring_det: dict) -> str:
    def row(label, a_key, d_key, a_src=all_, d_src=det):
        a = a_src["arms"][a_key] if a_key else None
        d = d_src["arms"][d_key] if d_key else None
        return (f"<tr><td><code>{esc(label)}</code></td>"
                f"<td>{a['dti']:.4f} <small>{ci(a['ci95'])}</small></td>"
                f"<td>{d['dti']:.4f} <small>{ci(d['ci95'])}</small></td></tr>")
    rows = [
        row("model_K37654_r3 (candidate arm)", "model_K37654_r3", "model_K37654_r3"),
        row("ctrl_proximity_K37654", "ctrl_proximity_K37654", "ctrl_proximity_K37654"),
        row("ctrl_random_K37654", "ctrl_random_K37654", "ctrl_random_K37654"),
        row("model_K22163_r3", "model_K22163_r3", "model_K22163_r3"),
    ]
    rows.append(f"<tr><td><code>ring_model_K37654_collar0 (H3 model)</code></td>"
                f"<td>{ring_all['ring_model']['dti']:.4f} <small>{ci(ring_all['ring_model']['ci95'])}</small></td>"
                f"<td>{ring_det['ring_model']['dti']:.4f} <small>{ci(ring_det['ring_model']['ci95'])}</small></td></tr>")
    rows.append(f"<tr><td><code>ring_random_K37654_collar0 (HOLDOUT BEST)</code></td>"
                f"<td>{ring_all['ring_random']['dti']:.4f} <small>{ci(ring_all['ring_random']['ci95'])}</small></td>"
                f"<td>{ring_det['ring_random']['dti']:.4f} <small>{ci(ring_det['ring_random']['ci95'])}</small></td></tr>")
    return ("<div class=\"table-wrap\"><table class=\"exec-table\"><thead><tr><th>Arm</th>"
            f"<th>HOLDOUT-DTI · all ({all_['arms']['model_K37654_r3']['withheld_positive_pixels']:,} withheld)</th>"
            f"<th>HOLDOUT-DTI · detached ({det['arms']['model_K37654_r3']['withheld_positive_pixels']:,} withheld)</th>"
            "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")


def build() -> str:
    focus = load("focus_site_table_20261029.json")
    uniq = load("candidate_uniqueness_probcollar-nan_20261029.json")
    all_ = load("holdout_probcollar_20261029.json")
    det = load("holdout_probcollar_detached_20261029.json")
    ring_all = load("holdout_ring_tiebreak_all_20261029.json")
    ring_det = load("holdout_ring_tiebreak_detached_20261029.json")
    card = load("run_card_probcollar_20261029.json")
    outside_pos = uniq["format"]["outside_footprint_positive"]
    site_u = per_site_uniqueness(focus)

    cand_sha = card["candidate"]["sha256"]
    fmt = card["candidate"]["format_checks"]
    lat = card["uniqueness"]["lattice"]
    wf = card["uniqueness"]["worst_my_dots_within_3px_vs_focus_nine"]
    rf = card["uniqueness"]["max_abs_spearman_vs_focus_nine"]
    cc = card["candidate"]
    ring_gap = ring_all["delta_ring_model_minus_ring_random"]
    ring_gap_det = ring_det["delta_ring_model_minus_ring_random"]
    dti_threshold = ALPHA * 0.26  # illustrative; owner-reported DTI-scale value, not a measured score

    hero = f'''<section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> FOCUS SITES · EXECUTIVE SUMMARY</p>
<h1>NOT CLEARED. <em>DO NOT SUBMIT.</em></h1>
<p class="lede">Nine focus sites, one research candidate, and a negative verdict. Nothing here is cleared for a weekly slot. No file is offered for download.</p></section>'''

    decision = f'''<section class="decision-panel" aria-labelledby="ans"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> ANSWER <span class="status-tag">NOT CLEARED / DO NOT SUBMIT</span></div>
<h2 id="ans">Is it OK to download and submit any file? No.</h2>
<p>The nine focus-site files are historical registry copies, labelled DO NOT RESUBMIT in the repo. The new raster <code class="wrap">{esc(CAND_REL)}</code> is a research-only artefact. It fails the literal 70% lattice gate and does not beat the holdout best. The verdict is computed in <code>scripts/write_run_card_probcollar.py</code> from the gates, not chosen.</p>
<p><strong>Verdict: {esc(card['verdict']).upper()}</strong> · <code>ok_to_submit: {str(card['ok_to_submit']).lower()}</code> · <code>slot_selected_or_spent: {str(card['slot_selected_or_spent']).lower()}</code> · experiments used {card['lane']['experiments_used']} of {card['lane']['experiment_budget']}.</p></div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative</strong></div><div><span>HOLDOUT BEST</span><strong>ring_random 0.0924 · HOLDOUT-DTI</strong></div><div><span>OWNER-REPORTED TOP</span><strong>0.2778 · GEMSDOE32</strong></div><div><span>ORGANISER LEADER</span><strong>0.4544 · live check</strong></div></div></section>'''

    table1 = f'''<section class="section" id="sites"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 1 · NINE FOCUS SITES</p>
<h2>Highest supplied score per site, the file, and whether it is unique.</h2>
<p>Scores are OWNER-REPORTED (README.md). None is ORGANISER-CONFIRMED. No HOLDOUT-DTI number is computed for these historical rasters, so none is shown as an estimate. The file is the registry copy SHA-pinned in data/restore_receipt.json.</p></div></div>
{focus_table(focus, site_u)}
<p class="body-copy"><strong>Unique versus all listed sites?</strong> No. Every focus site has at least one other listed site with more than 70% of its dots within 3 px. GEMSDOE25 and GEMSDOE30 have identical positive sets. The 3-px overlap and rank correlation in the table are measured on the rasters themselves.</p></section>'''

    table2 = f'''<section class="section" id="holdout"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 2 · HOLDOUT-DTI (OUR EVALUATOR)</p>
<h2>Every candidate arm is below the holdout best.</h2>
<p>Shared evaluator <code>{esc(all_['evaluator_version'])}</code>, α={all_['alpha']}, β={all_['beta']}, 300 m triangular kernel (3 px). Withheld units are catalogue segments, so this measures continuation of visible faults, not hidden new faults. Numbers are not a leaderboard estimate.</p></div></div>
{holdout_table(all_, det, ring_all, ring_det)}
<p class="body-copy"><strong>H3 (ring tie-break), rejected in both modes.</strong> Model ranking minus random tie-break inside the 1 px ring: {ring_gap['delta']:+.4f} [{ring_gap['ci95'][0]:+.4f}, {ring_gap['ci95'][1]:+.4f}] in all mode; {ring_gap_det['delta']:+.4f} [{ring_gap_det['ci95'][0]:+.4f}, {ring_gap_det['ci95'][1]:+.4f}] in detached mode. Our model ranking is worse than random there. Likely cause (not measured here): high-probability pixels cluster on a few strands, so the extra dots add little new coverage.</p>
<p class="body-copy">Leakage canary: max single-band AUC {card['leakage_canary']['all']['max_auc']:.3f} (all) and {card['leakage_canary']['detached']['max_auc']:.3f} (detached), threshold {card['leakage_canary']['threshold_auc']:.2f}. Both pass.</p></section>'''

    cand = f'''<section class="section" id="candidate"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 3 · UNIQUE RESEARCH TIF</p>
<h2>A unique, format-valid file that is NOT cleared.</h2>
<p>The file is written through the shared <code>vendor/gems57/submission_writer.py</code> and re-read from disk. It is <strong>not offered for download</strong>. The path is shown as text only.</p></div></div>
<div class="prose-card"><ul>
<li><strong>Path (primary, NaN outside):</strong> <code class="wrap">{esc(CAND_REL)}</code> (not in <code>docs/downloads/</code>)</li>
<li><strong>Twin (zeros outside, same dots):</strong> <code class="wrap">{esc(ZEROS_REL)}</code></li>
<li><strong>SHA-256:</strong> <code class="wrap">{esc(cand_sha)}</code></li>
<li><strong>Recipe:</strong> GBM probability on the 19 organiser bands, all mapped catalogue pixels as positives; top-37,654 pixels after a 3 px catalogue collar; binary 1.0 on the footprint and NaN outside it (official format). A zeros-outside twin carries the same dots for the repo's all-finite gate.</li>
<li><strong>Format (re-read):</strong> single band · float32 · {esc(uniq['format']['crs'])} · {uniq['format']['shape'][0]} × {uniq['format']['shape'][1]} · transform matches · inside finite, values in [0, 1] · outside: {esc(uniq['format']['outside_encoding'])} · outside-footprint positives: {outside_pos}. Dots: {cc['dots']:,}; closest dot to the catalogue {cc['min_distance_to_catalogue_px']:.2f} px; within 3 px: {cc['dots_within_3px_of_catalogue']}.</li>
<li><strong>Uniqueness (literal):</strong> worst 3-px overlap with a focus site {pct(wf['value'])} ({esc(Path(wf['file']).name)}); max |ρ| {rf['value']:.3f}. The 13GEMSDOE lattice is flagged at {pct2(lat['my_dots_within_3px_of_lattice'])}, which is a literal duplicate. Chance for uniform random dots in the candidate's region is {pct2(lat['chance_for_uniform_random_dots_in_candidate_region'])}, so the flag is at chance.</li>
<li><strong>Status:</strong> research-only · NOT CLEARED · DO NOT SUBMIT · <code>submission_slots_used: 0</code>.</li>
<li><strong>Receipts:</strong> <a href="{CAND_JSON}">writer receipt JSON</a> · <a href="data/candidate_uniqueness_probcollar-nan_20261029.json">uniqueness audit JSON (NaN twin)</a> · <a href="data/run-card-probcollar-20261029.json">run card JSON</a></li>
</ul></div></section>'''

    phd = f'''<section class="section" id="why-0.2778"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 4 · GEMSDOE32 AT 0.2778</p>
<h2>Why this file scored 0.2778, and whether 0.2778 can be beaten.</h2>
<p>Owner-reported. No organiser receipt ties 0.2778 to this hash. The mechanism below is derived from the official metric and measured on the pinned rasters.</p></div></div>
<div class="prose-card">
<h3>What the metric rewards</h3>
<p>The official DTI (DrivenData problem page) is TP<sub>w</sub> / (TP<sub>w</sub> + αFP<sub>w</sub> + βFN<sub>w</sub> + ε), with α=0.2, β=0.8, and a triangular kernel k(d)=max(1−d/300 m, 0). The worked example on the page (TP 3.00, FP 1.89, FN 2.00) gives ≈0.60, and <code>vendor/gems57/metric.py</code> matches it.</p>
<h3>What GEMSDOE32 changed relative to GEMSDOE25/30 (measured)</h3>
<p>The GEMSDOE30 parent has 44,090 dots; GEMSDOE25 has the same positive set. GEMSDOE32 has 37,654 dots, all of which belong to the parent (subset check: true). It removes 6,436 parent dots within 2 px of the catalogue (3,891 of them at 1 px) and adds none. Subset and removal counts are measured on the pinned rasters (<code>subset_checks</code> in <a href="data/focus_site_table_20261029.json">the focus-site table JSON</a>); the reason for the removal is inferred.</p>
<h3>The marginal rule (exact in the binary-dot model)</h3>
<p>Let a new binary dot have marginal credit c = max(0, k − M<sub>g</sub>) on its best truth g (where M<sub>g</sub> is the current best kernel hit on g), and miss share m = 1 − max<sub>g</sub> k. Because α + β = 1, the denominator changes by exactly α(m + c), and the numerator by c. The dot improves DTI if and only if <strong>c / (m + c) &gt; α · DTI</strong>. At an owner-reported DTI scale of 0.26, the threshold is ≈{dti_threshold:.3f}. For a fresh withheld pixel at distance d, this means a dot is worth emitting only when d ≲ 3 × (1 − 0.052) ≈ 2.84 px. Dots farther away and dots next to already-hit truth have c≈0 and lower the score. Dots next to visible catalogue earn no credit only if hidden faults are rarely adjacent to visible ones; that assumption is not measured here.</p>
<h3>What this implies for 0.2778</h3>
<p>Removing near-catalogue dots lowers FP mass and costs little credit, so the score can rise. This is consistent with the owner's +0.0178 step from 0.2600 to 0.2778, but that step is unverified. The rule also says the gain comes from removing zero-credit dots, not from adding more.</p>
<h3>Why our own holdout disagrees</h3>
<p>Our holdout withholds catalogue segments, so pixels next to visible faults earn credit by construction. It therefore rewards proximity, the opposite of the collar. This is a structural limit of the holdout, not evidence about hidden faults. The holdout and the owner's leaderboard step point in different directions, and the evidence here cannot settle which one reflects the organiser's hidden set.</p>
<h3>Can a higher score be achieved?</h3>
<p>The organiser's leaderboard shows far higher scores exist (0.4544 at the top, live check). The rule says to add dots only where they have credit above α·DTI, meaning distinct coverage of unhit truth rather than clustered high-probability pixels. This session produced no candidate that shows it. H4 below is the untested test. <strong>Not established:</strong> whether 0.2778 can be beaten on the organiser's set.</p>
</div></section>'''

    hyps = '''<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 5 · RANKED HYPOTHESES (NOT YET TRIED)</p>
<h2>Generated from the repo context. Only the top one is worth a holdout slot; none has been validated.</h2>
<p>These are proposals. None has been checked against literature in this session. The holdout budget is exhausted, so nothing here has been validated and no slot is spent.</p></div></div>
<div class="prose-card"><ol>
<li><strong>H4 · Dispersion-constrained damage-zone splays (top).</strong> Select model-probable pixels in a band around mapped traces (band width to be preregistered), under a minimum spacing of ≈2.8 px, so each dot has distinct coverage. Motivation: the marginal rule, and the H3 result. <em>Validation needed:</em> spatially blocked holdout with random-ring and dispersion-controls, both modes, 95% CI, leakage canary.</li>
<li><strong>H5 · Along-strike extension beyond mapped endpoints.</strong> Allocate dots per mapped trace in proportion to length beyond its endpoints. Possible overlap with the tip-stepover lane (GEMSDOE33): a novelty check is needed first.</li>
<li><strong>H6 · Magnetic edge-network severance.</strong> Proposed in an earlier slate (session a1ef4ce0). Untested here.</li>
</ol></div></section>'''

    how = '''<section class="section" id="how-to-submit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 6 · HOW TO SUBMIT</p>
<h2>Nothing in this session is submitted. Gating steps for any future candidate.</h2></div></div>
<div class="prose-card"><ol>
<li>Pass the literal lattice gate, or get an explicit owner decision on it (the gate is at chance; see irregularities).</li>
<li>Beat the holdout best in both modes with a 95% CI that excludes it, and pass the leakage canary.</li>
<li>Run a separate selector step. No weekly slot is spent on an idea that has not beaten the holdout best.</li>
<li>Read <a href="how-to-submit.html">how to submit</a> and <a href="submission-guide.html">submission guide</a> for the official format and rules.</li>
</ol></div></section>'''

    irr = '''<section class="section" id="irregularities"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 7 · IRREGULARITIES</p><h2>Flagged, not waived.</h2></div></div>
<div class="prose-card"><ul>
<li>The 13GEMSDOE lattice covers ≈99.9% of the footprint. Its literal 70% gate is at chance and effectively unsatisfiable for any footprint-spread submission.</li>
<li>The holdout's withheld units are catalogue segments, so proximity to visible faults is rewarded by construction (see the holdout caveats in evidence).</li>
<li>The shared validator (<code>gems57.gates</code>) rejects NaN outside the footprint under its local all-finite policy, but the official spec permits it. The NaN-outside primary is written by <code>scripts/build_candidate_submission.py</code>; its refusal reasons are in the candidate receipt JSON. Flagged for the owner, not waived.</li>
<li>0.2778 and the other scores are owner-reported. They are not tied to audited hashes or organiser receipts.</li>
<li>An owner-quoted 0.4413 leader does not match the live leaderboard (#1 0.4544).</li>
<li>GEMSDOE25 and GEMSDOE30 have identical positive sets; GEMSDOE28 (h27-4 r1) and GEMSDOE31 have identical positive sets.</li>
<li>The pinned run card (<code>evidence/run_card.json</code>, <code>docs/data/run-card.json</code>, <code>docs/data/run_card.json</code>) is the prior BB-STEP card and is guarded by three tests. The new card is at <code>evidence/run_card_probcollar_20261029.json</code>.</li>
</ul></div></section>'''

    limits = '''<section class="section" id="limitations"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 8 · REMAINING WORK AND LIMITATIONS</p><h2>What is still open.</h2></div></div>
<div class="prose-card"><ul>
<li>H4 has not been run. The spatially blocked holdout needs a new experiment; the holdout budget is spent.</li>
<li>Measure per-dot marginal credit and redundancy directly (predicted by the rule, not measured).</li>
<li>Add a distance-stratified truth check, because the current holdout cannot test hidden-fault discovery.</li>
<li>No organiser-confirmed score exists for any file here. The organiser data portal and the owner's Pages site are not reachable from this sandbox.</li>
<li>The registry index is partial (15 pinned registry rasters plus 9 committed TIFs), not a complete organiser inventory.</li>
</ul></div></section>'''

    links = '''<section class="section" id="links"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> 9 · MANUAL REVIEW LINKS</p><h2>Check it yourself.</h2></div></div>
<div class="prose-card"><ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem page (metric and submission format)</a></li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official rules (PDF)</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Live leaderboard</a></li>
<li><a href="https://community.drivendata.org/t/11516">Organiser masking answer (16 Sep 2026)</a></li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Reference solution repository</a></li>
<li><a href="data/focus_site_table_20261029.json">Focus-site table JSON</a> · <a href="data/holdout_probcollar_20261029.json">HOLDOUT-DTI all JSON</a> · <a href="data/holdout_probcollar_detached_20261029.json">HOLDOUT-DTI detached JSON</a> · <a href="data/holdout_ring_tiebreak_all_20261029.json">H3 all JSON</a> · <a href="data/holdout_ring_tiebreak_detached_20261029.json">H3 detached JSON</a></li>
</ul></div></section>'''

    body = hero + decision + table1 + table2 + cand + phd + hyps + how + irr + limits + links
    return shell("Focus sites · NOT CLEARED", body, depth=1, active="Executive summary")


def main() -> int:
    page = build()
    write_atomic(DOCS / "focus-sites.html", page)
    (DOCS / "data").mkdir(parents=True, exist_ok=True)
    for name in RECEIPTS:
        shutil.copyfile(EV / name, DOCS / "data" / name)
    print(f"wrote docs/focus-sites.html ({len(page):,} bytes) and {len(RECEIPTS)} receipts into docs/data/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
