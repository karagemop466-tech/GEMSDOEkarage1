#!/usr/bin/env python3
"""Render the 2026-10-31 executive summary page for GEMSDOEkarage1.

Produces a single self-contained page (inline CSS) that answers the owner's
questions directly:

* which of the nine focus-site submissions is the best to study / download,
* what its score is and how that score is labelled,
* whether it is unique against the other GEMSDOE sites,
* whether the freshly generated candidate is OK to download and submit,
* exactly how to submit a file to the DrivenData portal.

The page never manufactures a leaderboard estimate.  Scores are labelled
USER-REPORTED / UNVERIFIED (owner brief, no organizer receipt) or
HOLDOUT-DTI (local catalogue hide-and-recover screen), never a projection.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
sys.path.insert(0, str(ROOT / "src"))
from gemskarage1.paths import DOCS_DATA_DIR, EVIDENCE_DIR  # noqa: E402

SITE_PAGES = {
    "GEMSDOE24": "https://buffedlizard55-lab.github.io/GEMSDOE24/",
    "GEMSDOE25": "https://buffedlizard55-lab.github.io/GEMSDOE25/",
    "GEMSDOE27": "https://buffedlizard55-lab.github.io/GEMSDOE27/",
    "GEMSDOE28": "https://buffedlizard55-lab.github.io/GEMSDOE28/",
    "GEMSDOE30": "https://buffedlizard55-lab.github.io/GEMSDOE30/",
    "GEMSDOE31": "https://buffedlizard55-lab.github.io/GEMSDOE31/docs/",
    "GEMSDOE32": "https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html",
    "GEMSDOE33": "https://buffedlizard55-lab.github.io/GEMSDOE33/",
    "GEMSDOE36": "https://buffedlizard55-lab.github.io/GEMSDOE36/docs/",
}

SOURCES = [
    ("DrivenData DOE GEMS problem / metric / submission spec",
     "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"),
    ("DrivenData competition overview",
     "https://www.drivendata.org/competitions/306/competition-doe-gems/"),
    ("DrivenData public leaderboard",
     "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"),
    ("DrivenData data tab (login required)",
     "https://www.drivendata.org/competitions/306/competition-doe-gems/data/"),
    ("Official DOE/NLR competition rules (96647 PDF)",
     "https://docs.nlr.gov/docs/fy26osti/96647.pdf"),
    ("DrivenData reference solution",
     "https://github.com/drivendataorg/gems-prize-reference-solution"),
    ("USGS GeoDAWN airborne magnetic & radiometric release",
     "https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and"),
    ("GDR INGENIOUS compilation (OpenEI #1391)",
     "https://gdr.openei.org/submissions/1391"),
    ("GBCGE INGENIOUS project page",
     "https://gbcge.org/current-projects/ingenious/"),
    ("EPSG:32611 (UTM zone 11N)",
     "https://epsg.io/32611"),
    ("Tversky index (metric family)",
     "https://en.wikipedia.org/wiki/Tversky_index"),
    ("DrivenData staff clarification: known faults masked when scoring",
     "https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516"),
]

CSS = """
:root{--ink:#14201a;--muted:#5c6b62;--line:#dfe5df;--bg:#f5f7f4;--card:#ffffff;
--ok:#1c7a4a;--okbg:#e6f4ec;--no:#b3261e;--nobg:#fdecea;--amber:#8a5a00;--amberbg:#fdf3e0;
--accent:#0f5c8a;--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:0 20px}
header.top{background:#12231a;color:#eaf2ec;padding:26px 0}
header.top .wrap{display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between}
header.top h1{font-size:22px;margin:0;letter-spacing:.2px}
header.top .sub{color:#9fb3a6;font-size:13px;margin-top:4px}
.badge{display:inline-block;padding:6px 12px;border-radius:999px;font-weight:700;font-size:13px;white-space:nowrap}
.badge.no{background:var(--nobg);color:var(--no);border:1px solid #f2c3bf}
.badge.ok{background:var(--okbg);color:var(--ok);border:1px solid #bfe3cf}
.badge.amber{background:var(--amberbg);color:var(--amber);border:1px solid #ecd9a8}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px 22px;margin:20px 0}
.card h2{margin:0 0 6px;font-size:19px}
.card h3{margin:18px 0 6px;font-size:15px}
.eyebrow{font-size:12px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);margin:0 0 4px}
.download{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin-top:10px}
.btn{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;
padding:11px 18px;border-radius:8px;font-weight:600;font-size:15px}
.btn.secondary{background:#eef2ee;color:var(--ink);border:1px solid var(--line)}
code,.mono{font-family:var(--mono);font-size:13px;background:#eef2ee;padding:1px 5px;border-radius:4px}
table{border-collapse:collapse;width:100%;font-size:14px;margin-top:10px}
th,td{border:1px solid var(--line);padding:8px 9px;text-align:left;vertical-align:top}
th{background:#eef2ee;font-weight:700}
tr:nth-child(even) td{background:#fafcfa}
.pill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:700}
.pill.no{background:var(--nobg);color:var(--no)}
.pill.ok{background:var(--okbg);color:var(--ok)}
.pill.amber{background:var(--amberbg);color:var(--amber)}
.small{font-size:12.5px;color:var(--muted)}
ul.sources{padding-left:18px}
ul.sources li{margin:6px 0;font-size:14px}
a{color:var(--accent)}
.note{border-left:3px solid var(--amber);background:var(--amberbg);padding:10px 14px;border-radius:0 8px 8px 0;margin:14px 0;font-size:14px}
.note.red{border-color:var(--no);background:var(--nobg)}
.note.green{border-color:var(--ok);background:var(--okbg)}
footer{color:var(--muted);font-size:12.5px;padding:26px 0 40px;border-top:1px solid var(--line);margin-top:26px}
ol.steps{padding-left:20px} ol.steps li{margin:8px 0}
"""


def esc(s) -> str:
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def load_json(path: Path):
    return json.loads(path.read_text())


def latest_run_card() -> dict:
    cards = sorted((ROOT / "evidence").glob("run_card_karage1-seisprox-*.json"))
    if not cards:
        raise SystemExit("no seisprox run card found; run scripts/generate_karage1_submission.py first")
    primary = [c for c in cards if "c3-w0.55-20261031T012000Z" in c.name]
    return load_json((primary or cards)[-1])


def main() -> int:
    nine = load_json(DOCS_DATA_DIR / "nine_site_executive_20261031.json")
    card = latest_run_card()
    holdout_path = EVIDENCE_DIR / "holdout_screen_seisprox_20261031.json"
    holdout = load_json(holdout_path) if holdout_path.is_file() else None
    raster = card["raster"]
    download_rel = f"downloads/{raster['tif']}"
    zip_rel = f"downloads/{raster['zip']}"

    sites = nine["sites"]
    ranked = sorted(sites.items(), key=lambda kv: kv[1]["user_reported_score"], reverse=True)

    # ---- nine-site table rows ----
    rows = []
    for site, v in ranked:
        uniq = "YES" if v["unique_vs_other_eight"] else "NO"
        pill = '<span class="pill ok">YES</span>' if v["unique_vs_other_eight"] else '<span class="pill no">NO</span>'
        rows.append(
            f"<tr><th scope=\"row\">{esc(site)}</th>"
            f"<td><a href=\"{esc(SITE_PAGES[site])}\">{esc(v['file'])}</a><br>"
            f"<span class=\"small\">{v['dots']:,} dots · {v['within_3px_of_catalogue']:,} within 3 px of catalogue</span></td>"
            f"<td><strong>{v['user_reported_score']:.4f}</strong><br>"
            f"<span class=\"small\">USER-REPORTED / UNVERIFIED</span></td>"
            f"<td>{pill}<br><span class=\"small\">worst peer overlap "
            f"{v['worst_forward_overlap']*100:.1f}% vs {esc(v['worst_peer'])}</span></td>"
            f"<td><span class=\"pill no\">DO NOT RESUBMIT</span><br>"
            f"<span class=\"small\">third-party file; study only</span></td></tr>")

    best = ranked[0]
    best_site, best_v = best

    holdout_rows = ""
    if holdout:
        order = [("candidate_c3-w0.55-20261031T012000Z",
                  "candidate seisprox c3 (primary, 3 px collar)", "not ranked - off-catalogue by construction"),
                 ("candidate_c2-w0.55-20261031T013500Z",
                  "candidate seisprox c2 (2 px collar variant)", "not ranked - off-catalogue by construction"),
                 ("control_gemsdoe32_b2",
                  "control: GEMSDOE32 B2 (reported 0.2778)", "mapped-trace recovery only"),
                 ("control_uniform_random",
                  "null control: uniform random dots", "mapped-trace recovery only")]
        for key, label, reading in order:
            p = holdout["pooled"].get(key)
            c = holdout["ci95"].get(key, {}).get("ci95")
            if not p or not c:
                continue
            holdout_rows += (f'<tr><th scope="row">{esc(label)}</th>'
                             f'<td><strong>{p["dti"]:.6f}</strong></td>'
                             f'<td><span class="small">{c[0]:.6f} - {c[1]:.6f}</span></td>'
                             f'<td><span class="small">{esc(reading)}</span></td></tr>')

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    html_doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Executive summary · GEMSDOEkarage1</title>
<meta name="description" content="Nine-site executive summary, unique GeoTIFF candidate and submission guide for the DOE GEMS prize.">
<style>{CSS}</style></head><body>
<header class="top"><div class="wrap">
<div><h1>GEMSDOEkarage1 — Executive summary</h1>
<div class="sub">DOE GEMS Prize Challenge · fault discovery · evidence-first · generated {generated}</div></div>
<span class="badge amber">RESEARCH CANDIDATE · NOT CLEARED TO SUBMIT</span>
</div></header>

<div class="wrap">

<section class="card">
<p class="eyebrow">READ THIS FIRST</p>
<h2>Can I download a file and submit it right now?</h2>
<p><strong>No — not cleared for the DrivenData portal.</strong> The candidate below is
<strong>format-valid and unique</strong>, but it is a <strong>research artifact</strong>:
the hidden test labels are unavailable, so no organizer score exists and no
leaderboard estimate can be produced. The team's own gates (an assigned method lane,
a registry uniqueness receipt and a holdout screen) have not been satisfied, and
promotion to a real weekly slot is a separate selector decision.</p>
<div class="note red"><strong>Do not</strong> upload any file from this page to the
competition until the selector step has approved it. Format validity is necessary
but is not scientific readiness or portal acceptance.</div>
</section>

<section class="card">
<p class="eyebrow">THE CANDIDATE</p>
<h2>Unique GeoTIFF — download and inspect</h2>
<p>Generated by lane <strong>H-K1-SEISMIC-PROX</strong>. It uses official training
band 10 <code>deq_n100a15</code> (distance to the nearest earthquake), which the
repository's 58-channel stack never uses, weighted onto a magnetic / gravity
structural edge, with a full 3 px (300 m) catalogue collar. Dots are placed by exact
greedy max-coverage on the official triangular kernel.</p>
<div class="download">
<a class="btn" href="{esc(download_rel)}">Download .tif</a>
<a class="btn secondary" href="{esc(zip_rel)}">Download .zip</a>
</div>
<p class="small">A 2 px-collar twin (<code>karage1-seisprox-c2-w0.55-20261031T013500Z-zeros.tif</code>,
SHA-256 <code>1ea94432c1d09cd5968443d793455f6cfcae908aec671b5b9febccd2a6281e4d</code>) was
generated as a control; both are format-valid and unique against the nine sites, and both score
0.000 on the mismatched catalogue holdout.</p>
<ul class="small" style="margin-top:12px">
<li>File: <code>{esc(raster['tif'])}</code></li>
<li>SHA-256: <code>{esc(raster['sha256'])}</code></li>
<li>Dots: <strong>{raster['dots']:,}</strong> · dtype float32 · EPSG:32611 · {raster['shape'][0]}×{raster['shape'][1]}</li>
<li>Submission note ({card['submission_note_chars']} chars): {esc(card['submission_note'])}</li>
<li>Format validator: {'PASS' if card['validator_output']['all_checks_passed'] else 'FAIL'} (all checks)</li>
<li>Unique vs the nine focus sites: worst peer forward overlap
{card['registry_correlation_overlap']['worst_peer_forward_overlap']*100:.1f}% —
{'PASS' if card['registry_correlation_overlap']['unique_by_literal_rule_vs_peers'] else 'FAIL'}</li>
<li>Verdict: <strong>{esc(card['verdict'])}</strong> · ok_to_submit: <code>{card['ok_to_submit']}</code> ·
slot spent: <code>{card['slot_selected_or_spent']}</code></li>
</ul>
</section>

<section class="card">
<p class="eyebrow">NINE FOCUS SITES</p>
<h2>Executive summary — best submission per site</h2>
<p>Every value in the <em>score</em> column is <strong>USER-REPORTED / UNVERIFIED</strong>:
it comes from the owner's brief, and no organizer submission receipt tied to the
raster SHA-256 exists in this repository. Uniqueness is <strong>MEASURED</strong> here
from the restored raster bytes (directed 3 px dot overlap and Spearman).</p>
<table>
<thead><tr><th>Site</th><th>Best file to study / download</th><th>Score (reported)</th>
<th>Unique vs the other eight?</th><th>Submit?</th></tr></thead>
<tbody>{''.join(rows)}</tbody>
</table>
<div class="note"><strong>Headline:</strong> the best reported submission among the nine
sites is <strong>{esc(best_site)}</strong> at <strong>{best_v['user_reported_score']:.4f}</strong>
(USER-REPORTED / UNVERIFIED). It is <strong>not unique</strong>: {best_v['worst_forward_overlap']*100:.1f}%
of its dots lie within 3 px of {esc(best_v['worst_peer'])}, and all nine sites are
the same underlying field dotted differently (pairwise Spearman 0.98–0.999).</div>
</section>

<section class="card">
<p class="eyebrow">HOLDOUT SCREEN</p>
<h2>Catalogue hide-and-recover screen — HOLDOUT-DTI</h2>
<p>Truth is the mapped USGS/INGENIOUS catalogue withheld <em>whole</em> (200 px spatial blocks,
3 px buffer, 4 folds, pooled DTI with a paired block bootstrap). Because known catalogue faults are
masked from the <strong>competition</strong> score, this screen rewards re-finding <strong>mapped</strong>
traces and penalises off-catalogue placement by construction. It therefore <strong>cannot rank
off-catalogue candidates</strong> and is <strong>not a leaderboard estimate</strong>.</p>
<table>
<thead><tr><th>Raster</th><th>HOLDOUT-DTI (pooled)</th><th>95 % CI</th><th>Reading</th></tr></thead>
<tbody>{holdout_rows}</tbody>
</table>
<div class="note red">The candidate scores zero because the 3 px collar places every dot outside the
catalogue kernel. That is a property of this screen, not evidence about the competition, and it does
not clear or condemn the candidate.</div>
</section>

<section class="card">
<p class="eyebrow">THE B2 QUESTION</p>
<h2>Why did GEMSDOE32 <code>h33-h33-2-b2</code> report 0.2778, and can we beat it?</h2>
<h3>What is measured</h3>
<p>On the audited mirrored grid, GEMSDOE32 B2 is exactly the GEMSDOE25
<code>dotted-h19-5-d2-8</code> mask with <strong>6,436 dots removed</strong> — every dot
within the closed 2 px disk of the mirrored known-fault catalogue — and <strong>no dots
added</strong> (37,654 dots remain). GEMSDOE25 and GEMSDOE30 share the same positive-pixel
mask; GEMSDOE31 is the 1 px collar variant; GEMSDOE36 is a strict superset of B2 plus
1,200 dots.</p>
<h3>Why thinning helps (mechanism, not a proven cause)</h3>
<p>The published metric is a distance-weighted Tversky index,
<code>DTI = T / (T + 0.2·F + 0.8·(G − T))</code>, with a 300 m triangular kernel.
Known catalogue faults are <strong>masked from the scored truth</strong> (DrivenData staff
clarification). A dot that sits within 300 m of a <em>known</em> fault but farther than
300 m from every <em>hidden</em> fault earns no true-positive credit and a full unit of
false-positive cost. Removing such dots therefore raises the ratio. The reported sequence
(parent → 1 px collar → 2 px collar → superset) is consistent with that mechanism, but the
receipt is absent, so the causal claim is <strong>not proven</strong>.</p>
<h3>Can a new result beat 0.2778?</h3>
<p><strong>Possible in principle; not established here.</strong> The measured opportunity is
that all nine sites are one field dotted differently, and the winner is simply the most
aggressively collared. Two levers remain untested by this repository: (1) a full
3 px (300 m) collar that removes every dot capable of earning false-positive cost from a
masked known fault, and (2) a genuinely different posterior field. Lane H-K1-SEISMIC-PROX
uses official band 10, never used by the repo's 58-channel stack, together with the
3 px collar. No leaderboard estimate is produced, because the hidden labels are unavailable.</p>
</section>

<section class="card">
<p class="eyebrow">HOW TO SUBMIT</p>
<h2>Exactly how to submit a file to the competition</h2>
<ol class="steps">
<li>Sign in at <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">the competition page</a>
and open the <em>Submit</em> / leaderboard tab.</li>
<li>Click <strong>New submission</strong>.</li>
<li>Under <strong>File to submit</strong>, choose the single-band GeoTIFF
(<code>.tif</code>) or a <code>.zip</code> containing exactly one GeoTIFF.</li>
<li>The file <strong>must</strong> match the submission format's CRS (EPSG:32611), shape
(3730 × 3292) and geotransform (100 m, unrotated). Values inside the footprint must be
finite and in <strong>[0, 1]</strong>; outside the footprint must be null or NaN.</li>
<li>Give it a <strong>unique name</strong> and a <strong>short note (≤ 140 characters)</strong>,
e.g. <code>clustering with k=25</code>.</li>
<li>Confirm. The portal returns an error if any predicted value is outside [0, 1].</li>
</ol>
<div class="note red"><strong>Common failure:</strong> “Predicted values must be in range
[0, 1]”. This happens when the file contains NaN/Inf <em>inside</em> the footprint or values
&gt; 1. The candidate on this page is all-finite and binary (0/1), so it does not trip that
check — but that only means it is <em>format-valid</em>, not that it is approved.</div>
<p class="small">Submission limit: three per week (verify on the submission page).
Competition closes 2026-12-03 23:59 UTC (per the official rules PDF).</p>
</section>

<section class="card">
<p class="eyebrow">SOURCES</p>
<h2>Official verified sources</h2>
<ul class="sources">
{''.join(f'<li><a href="{esc(u)}">{esc(t)}</a></li>' for t, u in SOURCES)}
</ul>
</section>

<section class="card">
<p class="eyebrow">LIMITATIONS</p>
<h2>What is still blocking a real submission</h2>
<ul>
<li><strong>No hidden labels.</strong> The competition test labels are not in this
repository, so no organizer score and no defensible leaderboard estimate can be produced.</li>
<li><strong>No assigned method lane.</strong> The parallel-run protocol refers to a single
method paragraph that the owner has not supplied; <code>registry/template.json</code> has
<code>method_lane: null</code>.</li>
<li><strong>No organizer receipt.</strong> No file here has a submission-page receipt tying a
leaderboard score to its SHA-256.</li>
<li><strong>Catalogue holdout mismatch.</strong> The only local truth is the mapped
USGS/INGENIOUS catalogue; a hide-and-recover holdout on it rewards re-finding mapped traces
and penalises off-catalogue placement by construction, so it cannot rank this candidate.</li>
<li><strong>Lattice gate.</strong> The dense 13GEMSDOE lattice covers ~99.9% of the footprint
within 3 px, so the literal forward-overlap rule is unsatisfiable against it; it is published
as a diagnostic only.</li>
</ul>
</section>

</div>
<footer><div class="wrap">
Generated {generated} by <code>scripts/build_executive_20261031.py</code> from
<code>docs/data/nine_site_executive_20261031.json</code> and the run card.
Not affiliated with the organizers. Evidence class labels: USER-REPORTED / UNVERIFIED,
MEASURED, HOLDOUT-DTI, ORGANIZER-CONFIRMED.
</div></footer>
</body></html>
"""

    out = DOCS / "submission-20261031.html"
    out.write_text(html_doc)
    print(f"wrote {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
