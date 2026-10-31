#!/usr/bin/env python3
"""Build this branch's fail-closed executive decision page from committed audit JSON."""
from __future__ import annotations

import html
import json
import os
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DATA = DOCS / "data" / "nine_site_executive_20261031.json"
CARD = ROOT / "evidence" / "run_card_arena_fd3e38cf_20261031.json"
OUT = DOCS / "current-review-20261031.html"


def e(value: object) -> str:
    return html.escape(str(value), quote=True)


def build() -> str:
    audit = json.loads(DATA.read_text(encoding="utf-8"))
    card = json.loads(CARD.read_text(encoding="utf-8"))
    if card.get("verdict") != "negative" or card.get("ok_to_submit") is not False:
        raise ValueError("refusing to render a non-negative or malformed current run card")
    if set(audit.get("sites", {})) != {f"GEMSDOE{n}" for n in (24, 25, 27, 28, 30, 31, 32, 33, 36)}:
        raise ValueError("the nine-site audit is incomplete")

    rows: list[str] = []
    for site, r in audit["sites"].items():
        score = r.get("user_reported_score")
        score_cell = "Not supplied"
        if isinstance(score, (int, float)):
            score_cell = f'{score:.4f} <span class="label">USER-REPORTED / UNVERIFIED</span>'
        filename = e(r["file"])
        peer_pct = 100.0 * float(r["worst_forward_overlap"])
        rows.append(
            "<tr>"
            f"<th scope=\"row\">{e(site)}</th>"
            f"<td><code>{filename}</code><span class=\"sub\">Historical reference; study only, not offered for submission.</span></td>"
            f"<td>{score_cell}</td>"
            "<td><strong>NOT ESTIMABLE</strong><span class=\"sub\">No calibrated link from local holdout to hidden leaderboard score.</span></td>"
            f"<td><strong>NO</strong><span class=\"sub\">MEASURED overlap with {e(r['worst_peer'])}: {peer_pct:.2f}% (saved-byte audit).</span></td>"
            "<td><strong class=\"bad\">NO — DO NOT RESUBMIT</strong></td>"
            "</tr>"
        )

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Current fail-closed DOE GEMS submission decision, nine-site comparison and research next steps.">
<title>Current decision · GEMS Field Intelligence</title>
<link rel="stylesheet" href="assets/styles.css"><link rel="stylesheet" href="assets/decision.css">
<style>
.decision{{border-left:7px solid #a83232;background:#fff0ef;padding:1.35rem 1.5rem;margin:1.5rem 0;border-radius:8px}}
.decision h1{{margin:.2rem 0 .6rem}} .label,.sub{{display:block;font-size:.86em;color:#52605a;margin-top:.25rem}}
.bad{{color:#a12c2c}} table{{width:100%;border-collapse:collapse}} th,td{{padding:.8rem;border-bottom:1px solid #d9ded8;text-align:left;vertical-align:top}}
code{{overflow-wrap:anywhere}} .table-wrap{{overflow-x:auto}} .rank{{font-weight:700}}
</style></head>
<body><a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><div class="header-inner container">
<a class="brand" href="../index.html"><span><strong>GEMS</strong><small>FIELD INTELLIGENCE</small></span></a>
<nav class="main-nav" aria-label="Main navigation"><a href="../index.html">Overview</a><a aria-current="page" href="current-review-20261031.html">Current decision</a><a href="executive-summary.html">Executive summary</a><a href="how-to-submit.html">How to submit</a><a href="research.html">Research</a></nav>
<a class="header-link" href="https://github.com/karagemop466-tech/GEMSDOEkarage1">View repository ↗</a></div></header>
<main id="main"><div class="container">
<section class="decision" role="alert"><p class="eyebrow">CURRENT REVIEW · 31 OCT 2026 · {e(card['session'])}</p>
<h1>DO NOT SUBMIT — no file is cleared.</h1>
<p>No new TIFF was generated. The assigned method lane and canonical shared-template assignment are absent; required local feature stack and competition rasters are missing; template provenance preflight fails. A TIF produced without these would not satisfy the required scientific and reproducibility gates.</p>
<p><strong>No download button is provided for a submission candidate.</strong> Historical artifacts below are references for study only. No slot selected or spent.</p>
<p><a class="button button-dark" href="../evidence/run_card_arena_fd3e38cf_20261031.json">Open this session's JSON run card ↗</a> <a class="button button-light" href="../knowledge/session-review-arena-fd3e38cf-20261031.md">Read full three-pass review ↗</a></p></section>
<section class="section"><p class="eyebrow">NINE FOCUS SITES</p><h2>Best historical reports, uniqueness and download decision</h2>
<p>Every score is owner-supplied and unverified; the score estimate column is intentionally not estimable. Files are named for audit but are not linked as downloads. MEASURED overlap uses the pinned local reference masks and does not prove comparison against the complete organizer registry.</p>
<div class="table-wrap"><table><thead><tr><th>Site</th><th>Historical file (reference only)</th><th>Reported value</th><th>Estimated score</th><th>Unique vs other focus sites?</th><th>Submit?</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section>
<section class="section"><h2>Why GEMSDOE32 B2 leads this list</h2>
<p><strong>0.2778 is USER-REPORTED / UNVERIFIED</strong>, not an organizer receipt in this repository. The saved-byte lineage audit says B2 is GEMSDOE25's dot set with 6,436 catalogue-adjacent dots removed and none added. In this task, removing predictions near already mapped traces plausibly reduces false positives while retaining candidates away from mapped traces. This is a plausible explanation, not a causal proof: the scores are unverified, the files are highly related, and the local catalogue-recovery holdout does not reproduce their ordering. Further thinning alone is not a scientifically supported route to a higher score.</p>
<p><strong>Can a score above 0.2778 be achieved?</strong> Possibly, but there is no validated evidence here that it has been. The necessary path is a distinct off-catalogue geological signal that beats a frozen, comparable spatial holdout and survives leakage, uniqueness and format checks. Do not call a projection or catalogue HOLDOUT-DTI a leaderboard score.</p></section>
<section class="section"><h2>Research proposals — not tested or validated</h2><p>Ranks are qualitative prioritization, not numerical score forecasts. See the review for detailed physical rationale, mimics and gates.</p>
<ol><li><span class="rank">H-SPEC</span> — cross-scale gravity/magnetic phase stability (`iso_grav_anom`, `rtp`/`tmi`); proposed first validation; medium–high implementation cost.</li>
<li><span class="rank">H-CB-OFFSET</span> — signed lateral offset between conductive-surface and basement boundaries (`cond_surf`, `depth_to_base_surf`); low–medium cost.</li>
<li><span class="rank">H-TOPO-ASYM</span> — signed paired-profile flexure from detrended elevation/slope, conditioned on a subsurface edge; medium cost.</li>
<li><span class="rank">H-E3</span> — joint magnetic/gravity Euler depth-coincidence; single-field Euler experiments already exist, so this is a distinct, untested joint variant; medium cost and lower priority.</li></ol>
<p>All are proposals only. No feature canary or holdout ran in this session. The project data tab is login-gated per the prior repository audit, and no feature stack is present locally.</p></section>
<section class="section"><h2>Official review links</h2><ul>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData competition rules and overview ↗</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">DrivenData task description ↗</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/">Competition data tab (login required) ↗</a></li>
<li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Official leaderboard ↗</a></li>
<li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Organizer reference solution ↗</a></li>
<li><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">NLR rules PDF ↗</a></li>
<li><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN source ↗</a></li>
</ul><p>These are source links recorded in the repository; they were not freshly fetched in this restricted-network review. The supplied mirror hashes establish byte consistency only, not organizer authenticity.</p></section>
</div></main><footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div><div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with competition organizers.</span></div></div></footer></body></html>'''


def main() -> None:
    content = build()
    fd, temp_name = tempfile.mkstemp(prefix="." + OUT.name + ".", suffix=".partial", dir=OUT.parent)
    temp = Path(temp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content + "\n")
        os.chmod(temp, 0o644)
        os.replace(temp, OUT)
    finally:
        temp.unlink(missing_ok=True)
    print(f"Rendered {OUT.relative_to(ROOT)}; no submission authorized.")


if __name__ == "__main__":
    main()
