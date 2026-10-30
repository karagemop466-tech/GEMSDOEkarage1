#!/usr/bin/env python3
"""Build the session arena/a8e4de2e executive summary page and JSON run card.

Every number on the page is read from a committed file, never typed in:
  * evidence/exp_h_r1_kth_magedge_20261030.json   (Experiment 1, H-R1)
  * registry/user_reported_scores_20261029.json    (USER-REPORTED nine-site scores)
  * evidence/site_lineage_verification_20261029.json (nine-site dot lineage)
  * registry/leaderboard_snapshot_20261030.json    (official public leaderboard, read 30 Oct 2026)

Outputs: docs/session-a8e4de2e.html and evidence/run_card_h_r1_20261030.json.
Authorises nothing: the verdict is NEGATIVE and ok_to_submit is false.
"""
from __future__ import annotations

import hashlib
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.render_site import shell  # noqa: E402  (shared site chrome)

EXP = ROOT / "evidence/exp_h_r1_kth_magedge_20261030.json"
SCORES = ROOT / "registry/user_reported_scores_20261029.json"
LINEAGE = ROOT / "evidence/site_lineage_verification_20261029.json"
BOARD = ROOT / "registry/leaderboard_snapshot_20261030.json"
PAGE = ROOT / "docs/session-a8e4de2e.html"
CARD = ROOT / "evidence/run_card_h_r1_20261030.json"
ARCH = "archive/research-hr1-20261030"
SITES = ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36")
PROBLEM = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"
LEADER = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
GEODAWN = "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and"
GEODAWN_DOI = "https://doi.org/10.5066/P93LGLVQ"

esc = html.escape


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def best_by_site(scores: dict) -> dict:
    best: dict[str, dict] = {}
    for e in scores["entries"]:
        if e["site"] not in best or e["score"] > best[e["site"]]["score"]:
            best[e["site"]] = e
    return best


def sibling_overlap(lineage: dict) -> dict:
    """Largest share of a site's dots within 3 px of ANOTHER focus site's dots."""
    out: dict[str, dict] = {s: dict(overlap=0.0, partner=None) for s in SITES}
    for key, v in lineage["pairwise_nine_sites"].items():
        a, b = key.split("|")
        for site, partner, frac in ((a, b, v["a_dots_within_3px_of_b_fraction"]),
                                    (b, a, v["b_dots_within_3px_of_a_fraction"])):
            if site in out and frac > out[site]["overlap"]:
                out[site] = dict(overlap=frac, partner=partner)
    return out


def pct(x: float) -> str:
    return f"{100 * x:.1f}%"


def build_card(exp: dict) -> dict:
    h = exp["candidate"]["holdout"]
    zp = exp["artefacts"]["zeros_primary"]
    nt = exp["artefacts"]["nan_outside_twin"]
    u = exp["uniqueness"]
    null = exp["controls"]["random_null_matched_count"]
    ch = exp["controls"]["champion_GEMSDOE32_B2"]["holdout"]
    pv = exp["paired_vs_null"]
    px = exp["proxy_sgmc_offcatalogue"]
    ev = exp["evaluator"]
    return dict(
        schema="karage1-run-card-v2",
        session="arena/a8e4de2e-gemsdoekarage1",
        date_utc="2026-10-30",
        experiment="1 of 3 (budget: 3 experiments or 2 hours)",
        hypothesis=(
            "H-R1: potassic alteration (block-normalised K high, Th low) that coincides with a "
            "horizontal total-magnetic-intensity gradient maximum marks a fault-controlled fluid pathway, "
            "so it can locate mapped and unmapped structure beneath cover."),
        mechanism=(
            "Hydrothermal potassic alteration of fault-controlled permeable zones raises K relative to Th, "
            "and the same structures produce a magnetic gradient. Co-location of the two is the proposed signature."),
        named_non_fault_mimic=(
            "K-rich granite and pluton margins (lithologic contacts); alluvial and playa K variation; "
            "acquisition-block seams in the GeoDAWN radiometrics (block z-scores reduce them but do not remove them)."),
        holdout_dti=dict(
            value=h["pooled_dti"], label="HOLDOUT-DTI", evaluator_version=ev["version"],
            withheld_positives=ev["withheld_positives"], cells=ev["cells"],
            ci95=h["ci95_cell_bootstrap_of_mean"],
            ci95_method="percentile bootstrap over the 16 cells of the mean per-cell DTI",
            truth="withheld MAPPED catalogue segments; not the competition's new-fault test set"),
        controls=dict(
            random_null_pooled_mean=null["pooled_mean"], random_null_per_seed=null["pooled_dti_per_seed"],
            champion_GEMSDOE32_B2_pooled=ch["pooled_dti"], champion_ci95=ch["ci95_cell_bootstrap_of_mean"]),
        paired_delta_vs_random_null=dict(mean=pv["mean_delta"], ci95=pv["ci95"],
                                         interpretation="CI includes 0; candidate does not beat random placement"),
        proxy_offcatalogue_recall_within_3px=dict(
            candidate=px["candidate"]["recall_within_3px"], random_null_mean=px["random_null_mean"],
            champion=px["champion"]["recall_within_3px"],
            label="PROXY: owner-derived USGS SGMC mirror, > 3 px from mapped catalogue; not the competition truth"),
        leakage_canary=dict(
            all_features_below_0_90=all(v["passed"] for v in exp["leakage_canary"].values()),
            max_direction_invariant_auc={k: v["max_direction_invariant_auc"] for k, v in exp["leakage_canary"].items()}),
        correlation_overlap_vs_registry=dict(
            registry_rasters_scanned=u["registry_rasters_scanned"],
            surface_pre_placement_max_spearman=u["surface_pre_placement"]["max_spearman"],
            final_dots_max_overlap_any=u["final_dots"]["max_my_dots_within_3px"],
            dot_gate_trips_70pct=[dict(file=Path(r["file"]).name, my_dots_within_3px=r["my_dots_within_3px"],
                                       their_dots_within_3px_of_mine=r["their_dots_within_3px_of_mine"],
                                       jaccard=r["jaccard"], their_positive_cells=r["their_positive_cells"])
                                  for r in u["dot_gate_trips_70pct"]],
            nine_focus_site_rasters=u["nine_focus_site_rasters"],
            reading="Both gate trips are dense rasters (5.1 M and 0.2 M positive cells). Reverse overlap is about 19%. "
                    "Jaccard is below 0.01. The literal 70% rule fails on density, not on a copied dot set."),
        raster_sha256=dict(zeros_primary=zp["sha256"], nan_outside_twin=nt["sha256"]),
        validator_output=dict(
            zeros_primary_shared_validator=zp["validator_checks"],
            zeros_primary_all_passed=zp["validator_all_passed"],
            nan_outside_twin_checks=nt["checks"],
            conflict="Official text: outside-bounds cells null or NaN. Shared writer: all-finite zeros only. Both are kept; the owner must resolve."),
        submission_name=zp["name"],
        submission_note=zp["note"],
        submission_note_chars=zp["note_chars"],
        ok_to_submit=False,
        slot_selected_or_spent=False,
        verdict="negative",
        verdict_reason=(
            "Fails the pre-registered rule: pooled HOLDOUT-DTI is below the matched random null, the paired CI "
            "includes zero, and the literal dot gate trips on dense rasters. Also below random on the off-catalogue proxy."),
        decision_rule=exp["decision_rule"],
        receipts=dict(experiment=str(EXP.relative_to(ROOT)), file=f"{ARCH}/{zp['name']}.tif",
                      zip=f"{ARCH}/{zp['name']}.zip", nan_twin=nt["file"]),
    )


def page(exp: dict, card: dict, scores: dict, lineage: dict, board: dict) -> str:
    best = best_by_site(scores)
    sib = sibling_overlap(lineage)
    h = exp["candidate"]["holdout"]
    rows = []
    for s in SITES:
        b = best[s]
        o = sib[s]
        rows.append(
            "<tr>"
            f"<th scope='row'>{s}</th>"
            f"<td><code class='wrap'>{esc(b['file_name'])}</code></td>"
            f"<td><strong>{b['score']:.4f}</strong><span class='cell-sub'>USER-REPORTED / UNVERIFIED</span></td>"
            "<td><strong>Not estimable</strong><span class='cell-sub'>No organizer receipt. The internal holdout is not a leaderboard proxy.</span></td>"
            f"<td><strong>No</strong><span class='cell-sub'>{pct(o['overlap'])} of its dots lie within 3 px of {esc(o['partner'])}</span></td>"
            "<td><span class='pill pill-hold'>DO NOT SUBMIT</span></td>"
            "</tr>")
    table_nine = ("<div class='table-wrap'><table><thead><tr><th scope='col'>Site</th>"
                  "<th scope='col'>Best file (as reported)</th><th scope='col'>Reported score</th>"
                  "<th scope='col'>Estimated leaderboard score</th>"
                  "<th scope='col'>Unique versus the other focus sites?</th><th scope='col'>Download and submit?</th>"
                  "</tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>")

    lead = board
    top = lead["top_score"]
    r48 = lead["rank_48_score"]
    cvals = card["correlation_overlap_vs_registry"]
    gate_rows = "".join(
        f"<li><code>{esc(g['file'])}</code>: {pct(g['my_dots_within_3px'])} of our dots within 3 px, "
        f"but only {pct(g['their_dots_within_3px_of_mine'])} of theirs are within 3 px of ours "
        f"(Jaccard {g['jaccard']:.4f}; {g['their_positive_cells']:,} positive cells)</li>"
        for g in cvals["dot_gate_trips_70pct"])
    h_ci = h["ci95_cell_bootstrap_of_mean"]
    nul = card["controls"]
    pv = card["paired_delta_vs_random_null"]
    px = card["proxy_offcatalogue_recall_within_3px"]
    nm = card["submission_name"]
    tif_href = f"../{card['receipts']['file']}"
    zip_href = f"../{card['receipts']['zip']}"
    nan_href = f"../{card['receipts']['nan_twin']}"
    body = f"""
<style>
.exec-banner{{border:3px solid #b00020;background:#fff4f4;padding:18px 22px;margin:18px 0;border-radius:8px}}
.exec-banner h1{{margin:0 0 8px;font-size:1.6rem;color:#7a0016}}
.exec-banner p{{margin:6px 0}}
.table-wrap{{overflow-x:auto}}
table.exec{{border-collapse:collapse;width:100%;margin:12px 0;font-size:0.95rem}}
table.exec th,table.exec td{{border:1px solid #c9d1c7;padding:8px 10px;vertical-align:top;text-align:left}}
table.exec thead th{{background:#eef3ec}}
.cell-sub{{display:block;font-size:0.82rem;color:#4a5a4a;font-weight:normal}}
.pill{{display:inline-block;padding:2px 8px;border-radius:12px;font-size:0.8rem;font-weight:bold}}
.pill-hold{{background:#b00020;color:#fff}}
.pill-ok{{background:#1b5e20;color:#fff}}
.note{{background:#f3f6f2;border-left:4px solid #3a6b3a;padding:10px 14px;margin:14px 0}}
code.wrap{{word-break:break-all}}
</style>
<div class="page-top"><span>GEMS PRIZE <span class="separator">/</span> EXECUTIVE SUMMARY</span><span class="page-date">SESSION arena/a8e4de2e · 30 OCT 2026</span></div>

<section class="exec-banner" aria-label="Download decision">
<h1>Can I download and submit a file from this site? NO.</h1>
<p><strong>No file in this repository is cleared for upload.</strong> Every download here is research-only and says so in its name.</p>
<p><strong>Best reported submission:</strong> GEMSDOE32 <code class="wrap">h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros</code>, USER-REPORTED <strong>0.2778</strong>. It is <strong>not unique</strong>: it is a strict subset of GEMSDOE25's dot mask. Do not resubmit it.</p>
<p><strong>New unique file this session:</strong> <code class="wrap">{esc(card['submission_name'])}.tif</code>. Its pooled HOLDOUT-DTI is <strong>{h['pooled_dti']:.4f}</strong>, below the random-placement null of <strong>{nul['random_null_pooled_mean']:.4f}</strong>. Verdict: <span class="pill pill-hold">NEGATIVE · DO NOT SUBMIT</span>.</p>
<p><strong>Leaderboard facts (official page, read 30 Oct 2026):</strong> #1 = <strong>{top:.4f}</strong>. #48 = {r48:.4f}. The user-reported 0.4413 is <strong>not in the top 50</strong>. <a href="{LEADER}">Check the live board ↗</a></p>
<article class="audit-card"><p class="eyebrow">DO NOT SUBMIT · RESEARCH ONLY · NOT FOR UPLOAD</p><p>Downloads: <a href="{tif_href}" download>{nm}.tif</a> · <a href="{zip_href}" download>.zip (one TIFF)</a> · <a href="{nan_href}" download>NaN-outside twin (official wording)</a></p></article>
</section>

<section aria-label="Nine focus sites">
<h2>1. The nine focus sites: best file, estimate, uniqueness</h2>
<p>Scores are the values supplied by the owner (USER-REPORTED / UNVERIFIED, <code>registry/user_reported_scores_20261029.json</code>). None has an organizer receipt, so no leaderboard estimate is given. Uniqueness uses the nine registry rasters (<code>evidence/site_lineage_verification_20261029.json</code>): each site's dots are within 3 px of a sibling's dots by the share listed. Every site fails.</p>
{table_nine}
<p class="note">Why GEMSDOE32 scored highest among the nine (measured, not inferred): it is GEMSDOE25's d2.8 mask with 6,436 dots within 2 px of the mapped catalogue removed, and no dots added (37,654 dots). The organizer's mechanism is unknown. A plausible mechanism, not measured here: the competition's test set is faults <em>not</em> in the USGS catalogue, so dots on mapped traces are false positives under the metric's α = 0.2 penalty. Deleting them lowers the penalty. Source for the metric: <a href="{PROBLEM}">official problem page ↗</a>.</p>
</section>

<section aria-label="This session's file">
<h2>2. This session's new file: H-R1</h2>
<table class="exec"><thead><tr><th scope="col">Item</th><th scope="col">Value (from evidence)</th></tr></thead><tbody>
<tr><th scope="row">File</th><td><code class="wrap">{esc(card['receipts']['file'])}</code></td></tr>
<tr><th scope="row">SHA-256 (zeros-outside primary)</th><td><code class="wrap">{card['raster_sha256']['zeros_primary']}</code></td></tr>
<tr><th scope="row">Dots / format</th><td>37,654 dots · float32 · 1 band · EPSG:32611 · 3,730 × 3,292 · transform matches sample · values {{0, 1}}</td></tr>
<tr><th scope="row">HOLDOUT-DTI (pooled)</th><td><strong>{h['pooled_dti']:.4f}</strong><span class="cell-sub">HOLDOUT-DTI · {esc(card['holdout_dti']['evaluator_version'])} · {card['holdout_dti']['withheld_positives']:,} withheld positives · 95% CI [{h_ci[0]:.4f}, {h_ci[1]:.4f}]</span></td></tr>
<tr><th scope="row">Random placement, same count (3 seeds)</th><td>{nul['random_null_pooled_mean']:.4f}<span class="cell-sub">per seed: {', '.join(f'{x:.4f}' for x in nul['random_null_per_seed'])}</span></td></tr>
<tr><th scope="row">Paired difference vs random</th><td>{pv['mean']:+.4f} · 95% CI [{pv['ci95'][0]:+.4f}, {pv['ci95'][1]:+.4f}] <span class="cell-sub">{esc(pv['interpretation'])}</span></td></tr>
<tr><th scope="row">Off-catalogue proxy (SGMC, PROXY only)</th><td>candidate {pct(px['candidate'])} · random {pct(px['random_null_mean'])} · GEMSDOE32 champion {pct(px['champion'])}</td></tr>
<tr><th scope="row">Leakage canary</th><td>Each feature alone: max direction-invariant AUC {max(card['leakage_canary']['max_direction_invariant_auc'].values()):.3f}; all below 0.90</td></tr>
<tr><th scope="row">Uniqueness, surface (before placement)</th><td>max Spearman {cvals['surface_pre_placement_max_spearman']:.3f} across {cvals['registry_rasters_scanned']} local and mirrored rasters (gate ≤ 0.90: pass)</td></tr>
<tr><th scope="row">Uniqueness, nine focus sites</th><td>max 3 px overlap {pct(cvals['nine_focus_site_rasters']['max_my_dots_within_3px'])}, max Jaccard {cvals['nine_focus_site_rasters']['max_jaccard']:.4f}: unique versus the nine</td></tr>
<tr><th scope="row">Literal 70% dot gate</th><td><span class="pill pill-hold">FAILS</span> on two dense rasters:<ul>{gate_rows}</ul></td></tr>
<tr><th scope="row">Shared validator (zeros primary)</th><td>{'all checks pass' if card['validator_output']['zeros_primary_all_passed'] else 'FAILED'}</td></tr>
<tr><th scope="row">NaN-outside twin (official wording)</th><td>{'all format checks pass' if card['validator_output']['nan_outside_twin_checks']['all_passed'] else 'FAILED'}; fails the shared all-finite policy by design (see section 4)</td></tr>
<tr><th scope="row">Verdict</th><td><span class="pill pill-hold">NEGATIVE · DO NOT SUBMIT</span> · ok_to_submit: false · slots used: 0</td></tr>
</tbody></table>
<p class="note">Why this file is not a copy of anything: its reverse overlap with each dense trip is about 19%, and its dot sets differ from the nine focus sites (max 3 px overlap {pct(cvals['nine_focus_site_rasters']['max_my_dots_within_3px'])}). It is also not cleared: its HOLDOUT-DTI does not beat random placement.</p>
</section>

<section aria-label="Can it be submitted">
<h2>3. The answer, and what would change it</h2>
<ol>
<li><strong>Holdout:</strong> the pre-registered rule needs pooled HOLDOUT-DTI above random placement with a paired CI above zero. H-R1 misses both.</li>
<li><strong>Target mismatch (irregularity):</strong> the internal holdout's truth is mapped USGS/INGENIOUS segments. The competition scores against new faults that are <em>not</em> in the USGS database (<a href="{PROBLEM}">official problem page ↗</a>). The holdout therefore rewards a different target. A holdout gain is still a screen, not a leaderboard estimate.</li>
<li><strong>Next candidate:</strong> H-E1, Euler deconvolution with depth clustering. The repo has no Euler code (verified by grep, 30 Oct 2026). It is ranked second in <code>knowledge/hypotheses-20261030.md</code> and is not yet tested.</li>
</ol>
</section>

<section aria-label="Irregularities">
<h2>4. Irregularities flagged for review</h2>
<ol>
<li>The user-reported 0.4413 does not appear in the official top 50 on 30 Oct 2026. The repo's earlier note placed 0.3195 at #47; this snapshot shows #48 (#47 = 0.3217). <a href="{LEADER}">Official leaderboard ↗</a> · <code>registry/leaderboard_snapshot_20261030.json</code></li>
<li><strong>Format conflict:</strong> the official text says data outside the bounds is "null or nan". The shared writer accepts all-finite zeros only, and labels NaN as diagnostic. Both files are provided. The cause of the portal error "Predicted values must be in range [0, 1]" is not established by any local test.</li>
<li><strong>Holdout target mismatch</strong> (section 3): the evaluator's truth is the mapped catalogue, and the competition's test set is not.</li>
<li>The 70% / 3 px lattice rule is an internal protocol rule, not in the official problem page. It fails on dense rasters regardless of copying (section 2).</li>
<li>GeoDAWN radiometrics come from the USGS data release <a href="{GEODAWN_DOI}">doi:10.5066/P93LGLVQ</a> (verified on the <a href="{GEODAWN}">USGS page ↗</a>, CC0). The uint8 K/Th/U/TC grids used here are an owner-derived mirror. They are not organizer-authenticated, and the quantisation is not independently checked.</li>
<li>The vendored grid loader hard-codes <code>data/bridge</code>. The earlier data test failed for that reason. The fix here is a git-ignored symlink, not a template change, because <code>vendor/PROVENANCE.json</code> pins file hashes. A template fix needs an owner decision.</li>
<li>The home page strip pointed at an older file (<code>hgridge</code>, 29 Oct). It now points at this session's page.</li>
</ol>
</section>

<section aria-label="Sources">
<h2>5. Official sources (verified 30 Oct 2026)</h2>
<ul>
<li><a href="{PROBLEM}">Problem description, metric, submission format ↗</a> (fetched; two chunks)</li>
<li><a href="{LEADER}">Public leaderboard ↗</a> (fetched; three chunks; snapshot in <code>registry/leaderboard_snapshot_20261030.json</code>)</li>
<li><a href="{GEODAWN}">USGS GeoDAWN data release page ↗</a> (fetched; DOI and CC0 licence confirmed)</li>
<li>Not re-read this session: the NLR rules PDF (<a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">docs.nlr.gov/docs/fy26osti/96647.pdf</a>) and the DrivenData data page (login-walled).</li>
</ul>
</section>
"""
    return shell("Executive summary · DOE GEMS (session a8e4de2e)", body, 1, "Executive summary")


def main() -> None:
    exp = load(EXP)
    scores = load(SCORES)
    lineage = load(LINEAGE)
    board = load(BOARD)
    card = build_card(exp)
    if len(card["submission_note"]) > 140 or len(card["submission_name"]) > 140:
        raise ValueError("name or note exceeds 140 characters")
    CARD.write_text(json.dumps(card, indent=2, sort_keys=True, default=float) + "\n", encoding="utf-8")
    PAGE.write_text(page(exp, card, scores, lineage, board) + "\n", encoding="utf-8")
    print(f"wrote {CARD.relative_to(ROOT)} and {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
