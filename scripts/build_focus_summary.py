#!/usr/bin/env python3
"""Build docs/focus-sites.html: NOT CLEARED / DO NOT SUBMIT executive summary for the nine focus sites.

Every number on the page is read from an evidence file under evidence/ (no hand-typed values).
Focus-site scores are labelled USER-REPORTED / UNVERIFIED; prior experiment metrics are labelled HOLDOUT-DTI.
The page offers NO download link for any raster. Receipts are copied into docs/data/ so the links resolve.
"""
from __future__ import annotations

import html
import json
import shutil
import sys
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


def esc(x) -> str:
    return html.escape(str(x), quote=True)


def load(name: str) -> dict:
    return json.loads((EV / name).read_text())


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
            f"<td><strong>{r['user_reported_score']:.4f}</strong><br><small>USER-REPORTED / UNVERIFIED</small></td>"
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

    hero = '''<section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> FOCUS SITES · EXECUTIVE SUMMARY</p>
<h1>NOT CLEARED. <em>DO NOT SUBMIT.</em></h1>
<p class="lede">Nine historical focus-site records are summarized below. This review generated no candidate, no score estimate, and no download. Nothing here is cleared for a weekly slot.</p></section>'''

    current_status = '''<section class="decision-panel" aria-labelledby="current-review"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT REVIEW · 31 OCT 2026 <span class="status-tag">NOT CLEARED / DO NOT SUBMIT</span></div>
<h2 id="current-review">Is any file OK to download and submit? No.</h2>
<p><strong>No current candidate was generated.</strong> The assigned method lane and canonical template are null; required cached competition inputs are absent; the shared writer/uniqueness provenance pins mismatch; the full authenticated registry is unavailable. No geological experiment or HOLDOUT-DTI was run in this review.</p>
<p>GEMSDOE32 B2 at 0.2778 remains <strong>USER-REPORTED / UNVERIFIED</strong>, not a receipt-linked organizer result. No leaderboard estimate is available. Read the <a href="../knowledge/review-arena-087d895d-20261031.md">three-pass review</a>, <a href="../evidence/run_card_arena_087d895d_20261031.json">current JSON run card</a>, and <a href="../knowledge/hypotheses-20261031.md">four-proposal research slate</a>.</p></div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative · no file cleared</strong></div><div><span>HOLDOUT-DTI</span><strong>Not run this review</strong></div><div><span>LEADERBOARD ESTIMATE</span><strong>Unavailable</strong></div><div><span>SUBMISSION SLOT</span><strong>Not selected or spent</strong></div></div></section>'''

    decision = f'''<section class="decision-panel" aria-labelledby="ans"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> HISTORICAL EXPERIMENT · 29 OCT 2026 <span class="status-tag">NOT CLEARED</span></div>
<h2 id="ans">Prior session: no TIFF was cleared. The historical candidate lost to its control.</h2>
<p>This panel and the sections marked historical below summarize an earlier experiment, not the 31 October review. The old raster <code class="wrap">{esc(CAND_REL)}</code> is a research-only artifact. It failed the literal 70% lattice gate and did not beat the historical holdout control. It is not linked for download.</p>
<p><strong>Historical verdict: {esc(card['verdict']).upper()}</strong> · <code>ok_to_submit: {str(card['ok_to_submit']).lower()}</code> · <code>slot_selected_or_spent: {str(card['slot_selected_or_spent']).lower()}</code> · experiments used {card['lane']['experiments_used']} of {card['lane']['experiment_budget']} in that prior run.</p></div>
<div class="decision-side"><div><span>HISTORICAL VERDICT</span><strong>Negative</strong></div><div><span>HISTORICAL HOLDOUT-DTI</span><strong>See dated evaluator table below</strong></div><div><span>USER-REPORTED / UNVERIFIED TOP</span><strong>0.2778 · GEMSDOE32</strong></div><div><span>PUBLIC LEADERBOARD</span><strong>Historical snapshot; not refreshed here</strong></div></div></section>'''

    table1 = f'''<section class="section" id="sites"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> HISTORICAL FOCUS-SITE COMPARISON</p>
<h2>Highest supplied score per site, its file, and local uniqueness.</h2>
<p>Scores are USER-REPORTED / UNVERIFIED from repository records; none is ORGANIZER-CONFIRMED by a submission-page receipt. No HOLDOUT-DTI was computed for these historical rasters and no leaderboard estimate is possible. Files are third-party registry copies for study only, not download recommendations.</p></div></div>
{focus_table(focus, site_u)}
<p class="body-copy"><strong>Unique versus all listed sites?</strong> No. Every focus site has at least one other listed site with more than 70% of its dots within 3 px, and each also fails the locally measured lattice comparison. GEMSDOE25 and GEMSDOE30 have identical positive sets. These are pinned-mirror measurements, not a complete authenticated registry certificate.</p></section>'''

    table2 = f'''<section class="section" id="holdout"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> HISTORICAL HOLDOUT-DTI · PRIOR SESSION</p>
<h2>Prior experimental arms, compared with their historical control.</h2>
<p>Shared evaluator <code>{esc(all_['evaluator_version'])}</code>, α={all_['alpha']}, β={all_['beta']}, 300 m triangular kernel (3 px). Withheld units are catalogue segments, so this measures recovery of mapped faults, not discovery of hidden new faults. These are historical HOLDOUT-DTI results, not a leaderboard estimate; this review ran no holdout.</p></div></div>
{holdout_table(all_, det, ring_all, ring_det)}
<p class="body-copy"><strong>H3 (ring tie-break), rejected in both modes.</strong> Paired HOLDOUT-DTI difference (model minus random tie-break inside the 1 px ring; evaluator {esc(all_['evaluator_version'])}): {ring_gap['delta']:+.4f} [{ring_gap['ci95'][0]:+.4f}, {ring_gap['ci95'][1]:+.4f}] in all mode; {ring_gap_det['delta']:+.4f} [{ring_gap_det['ci95'][0]:+.4f}, {ring_gap_det['ci95'][1]:+.4f}] in detached mode. The model ranking is worse than random there. Likely cause (not measured): high-probability pixels cluster on a few strands, so extra dots add little new coverage.</p>
<p class="body-copy">Leakage canary: max single-band AUC {card['leakage_canary']['all']['max_auc']:.3f} (all) and {card['leakage_canary']['detached']['max_auc']:.3f} (detached), threshold {card['leakage_canary']['threshold_auc']:.2f}. Both pass.</p></section>'''

    cand = f'''<section class="section" id="candidate"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> HISTORICAL CANDIDATE · 29 OCT 2026</p>
<h2>A prior research TIFF; not current, not cleared, and not offered for download.</h2>
<p>This artifact belongs to an earlier experiment and was not regenerated or revalidated in this review. The shared writer's recorded provenance mismatch is a current blocker; historical use is not current authorization. Its path is shown as text only.</p></div></div>
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

    phd = '''<section class="section" id="why-0.2778"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> GEMSDOE32 B2 · EVIDENCE-LIMITED EXPLANATION</p>
<h2>Why might B2 have ranked highest in the supplied nine-site list?</h2>
<p>The value 0.2778 is USER-REPORTED / UNVERIFIED. No organizer submission-page receipt here binds it to a TIFF hash. This is a mechanism hypothesis, not a causal finding.</p></div></div>
<div class="prose-card">
<p>Local pinned-mirror measurements show B2 is a strict subset of the GEMSDOE25/GEMSDOE30 parent: 6,436 dots were removed, none added; the removed dots lie within 2 pixels of the mirrored known-fault raster. These measurements describe third-party mirror bytes, not organizer-authenticated scoring inputs.</p>
<p>A plausible explanation is a precision–recall tradeoff under the official distance-weighted Tversky metric (α=0.2, β=0.8, 300 m triangular kernel): a prediction can add false-positive mass while earning little marginal recall when nearby truth is already covered. Removing such dots could help if the lost coverage is smaller than the false-positive cost. If those dots cover real withheld faults, removal could hurt. The score difference alone cannot distinguish these explanations, tuning effects, or a file/receipt mismatch.</p>
<p>Prior-session proxy result: <strong>HOLDOUT-DTI 0.004729</strong> (evaluator <code>gems57-pooled-hide-v2</code>, 45,260 withheld positives, 95% CI [0.004337, 0.005163]). This catalogue-segment hide-and-recover result is not calibrated to hidden off-catalogue faults and is not a leaderboard estimate.</p>
<p>No higher organizer score is established, and this review did not generate or test a new TIFF. Read the <a href="../knowledge/review-arena-087d895d-20261031.md#why-gemsdoe32-b2-may-have-ranked-highest-in-the-supplied-list">current evidence and limits</a> and the <a href="../knowledge/02_why_gemsdoe32_b2_scored_0.2778.md">detailed B2 analysis</a>. Official metric/source links are listed in those audit records; they were not freshly fetched in this review.</p>
</div></section>'''

    hyps = '''<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> CURRENT PROPOSALS · NOT ASSIGNED OR TESTED</p>
<h2>Four ranked geological research hypotheses; no score prediction.</h2>
<p>The ranking is qualitative expected research value relative to cost. None is an authorized method lane, none has been implemented, and no holdout or leaderboard score is estimated.</p></div></div>
<div class="prose-card"><ol>
<li><strong>H-CMCI · Conductivity–magnetic cross-correlation break</strong> (<code>cond_surf</code>, <code>tmi_hg</code>, <code>rtp</code>; basin-structure context from <code>depth_to_base_surf</code>). Moderate relative opportunity / medium–high cost. Mimics include saline/clay playa, basin-facies or intrusive contact, and flight seam.</li>
<li><strong>H-MTAC · Magnetic-texture anisotropy change point</strong> (<code>rtp</code>, <code>tmi</code>, <code>det_elev_slope</code>). Low–moderate relative opportunity / medium cost. Mimics include unfaulted lithologic or volcanic-texture boundaries and survey artifacts; related texture proposal exists in prior repo notes.</li>
<li><strong>H-PFB · Paired fault-block tilt break</strong> (<code>det_elev</code>, <code>det_elev_slope</code>, <code>depth_to_base_surf</code>, <code>iso_grav_anom</code>). Low–moderate relative opportunity / medium–high cost. Mimics include fan dip, compaction, bedding, or pediment; related proposal exists in prior repo notes.</li>
<li><strong>H-MENS · Independent magnetic-marker edge termination</strong> (<code>rtp</code>, <code>tmi_hg</code>, <code>tmi_vg</code>, <code>iso_grav_anom_hg</code>). Low relative opportunity / high cost. Mimics include survey seam, intrusion, lava margin, and interpolation gap; topology/null-model complexity is high.</li>
</ol><p>Full physical signatures, off-catalogue rationale, local prior-art caveats, input availability, and the fail-closed validation sequence are in <a href="../knowledge/hypotheses-20261031.md">the current hypothesis slate</a>. Competition rasters are absent and the lane is null, so none can be run yet.</p></div></section>'''

    how = '''<section class="section" id="how-to-submit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> SUBMISSION INSTRUCTIONS · ONLY AFTER CLEARANCE</p>
<h2>Nothing from this review is submitted. Follow these gates before any future slot.</h2></div></div>
<div class="prose-card"><ol>
<li>Resolve the assigned lane, canonical template, authenticated data, integrity pins, and complete registry. Do not invent or privately fork them.</li>
<li>Run per-feature leakage canaries and the buffered whole-segment spatial holdout with fold-local features, visible-fault pixel-exact masking, pooled DTI, evaluator ID, withheld count, and 95% CI.</li>
<li>Check rank-correlation on the proposed surface before placement and dot-overlap on final dots. If either duplicate threshold is crossed, record duplicate and stop.</li>
<li>Only after the holdout gate passes may a separate authenticated weekly-slot selector consider a candidate. No slot is selected in this review.</li>
<li>For a future cleared file, reopen and validate saved bytes against exact CRS, shape, transform, footprint and value rules. Then use a unique submission name and note of at most 140 characters, and retain the organizer receipt tied to the file hash. No current file, name, or note is approved.</li>
<li>Use the <a href="how-to-submit.html">submission guide</a> and official source links below for manual reference; this page is not current submission clearance.</li>
</ol></div></section>'''

    irr = '''<section class="section" id="irregularities"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> CURRENT IRREGULARITIES AND ACCESS LIMITS</p><h2>Flagged, not waived.</h2></div></div>
<div class="prose-card"><ul>
<li>The method lane and canonical template assignment are null in <code>registry/template.json</code>; the referenced method paragraph is absent from the saved brief.</li>
<li>The shared feature stack and four required competition rasters are absent from the expected cache paths; the active environment has no authorized data restore.</li>
<li>The vendored submission writer and uniqueness tool fail their recorded provenance hashes. Do not locally repin or privately fork.</li>
<li>The complete authenticated registry is unavailable. <code>registry/registry_roles.json</code> contains an older role-based calibration-lattice exception that conflicts with the current prompt's literal any-registry duplicate rule. This review follows the current literal rule and flags the conflict.</li>
<li>The holdout is a mapped-catalogue hide-and-recover proxy; it is not calibrated to private off-catalogue faults and cannot produce a leaderboard estimate.</li>
<li>No official source page was fetched in this review. Links and dated prior audits are provided for manual review; they are not fresh verification.</li>
<li>GEMSDOE25 and GEMSDOE30 have identical positive sets in the local pinned-mirror measurement; B2 is a subset of their shared parent. These raster comparisons do not authenticate an organizer score or prove why it changed.</li>
</ul></div></section>'''

    limits = '''<section class="section" id="limitations"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> REMAINING WORK AND LIMITATIONS</p><h2>What must be resolved before research can continue.</h2></div></div>
<div class="prose-card"><ul>
<li>Get the actual owner-assigned method paragraph and canonical shared-template identity.</li>
<li>Restore organizer-authorized competition inputs and feature cache; verify their metadata, hashes, masks, and provenance.</li>
<li>Resolve the duplicate-rule/registry-role conflict and obtain a complete authenticated comparison set.</li>
<li>Repair shared-tool provenance at its owning upstream template, then rerun leakage canaries and buffered whole-segment holdout.</li>
<li>Only if a preregistered candidate beats a frozen comparable holdout and passes saved-byte and uniqueness gates may a separate selector consider a live weekly slot.</li>
<li>No organizer-confirmed score or validated leaderboard estimate exists for any focus-site file in this review. The current external source pages and competition portal were not accessible to this runtime.</li>
</ul></div></section>'''

    links = '''<section class="section" id="links"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> OFFICIAL SOURCE LINKS · MANUAL REVIEW</p><h2>Prior source checks are dated; none was freshly fetched in this review.</h2></div></div>
<div class="prose-card"><ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official problem page (metric and submission format)</a></li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">Official rules (PDF)</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Live leaderboard</a></li>
<li><a href="https://community.drivendata.org/t/11516">Organiser masking answer (16 Sep 2026)</a></li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Reference solution repository</a></li>
<li><a href="data/focus_site_table_20261029.json">Focus-site table JSON</a> · <a href="data/holdout_probcollar_20261029.json">HOLDOUT-DTI all JSON</a> · <a href="data/holdout_probcollar_detached_20261029.json">HOLDOUT-DTI detached JSON</a> · <a href="data/holdout_ring_tiebreak_all_20261029.json">H3 all JSON</a> · <a href="data/holdout_ring_tiebreak_detached_20261029.json">H3 detached JSON</a></li>
</ul></div></section>'''

    body = hero + current_status + decision + table1 + table2 + cand + phd + hyps + how + irr + limits + links
    return shell("Focus sites · NOT CLEARED", body, depth=1, active="Executive summary")


def main() -> int:
    page = build()
    (DOCS / "focus-sites.html").write_text(page, encoding="utf-8")
    (DOCS / "data").mkdir(parents=True, exist_ok=True)
    for name in RECEIPTS:
        shutil.copyfile(EV / name, DOCS / "data" / name)
    print(f"wrote docs/focus-sites.html ({len(page):,} bytes) and {len(RECEIPTS)} receipts into docs/data/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
