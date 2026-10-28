#!/usr/bin/env python3
"""Render the public decision pages from the current, fail-closed audit.

This is a deterministic static build. It never downloads from DrivenData,
changes a registry or treats a historical file as a new submission.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
SITES = tuple(f'GEMSDOE{n}' for n in (24, 25, 27, 28, 30, 31, 32, 33, 36))
esc = html.escape


def strongest_peer_witness(name: str, ref: dict) -> tuple[float, str]:
    """Return the strongest directional nine-site overlap, validating its evidence.

    This reports only the nine historical, hash-pinned files; it cannot certify
    complete registry uniqueness or check an unavailable placement surface.
    """
    expected_count = ref['rows'][name]['positive_pixels']
    witnesses = []
    for peer in SITES:
        if peer == name:
            continue
        pair = ref['directed_pairs'][f'{name}->{peer}']
        if not isinstance(pair, dict):
            raise ValueError(f'bad directional pair evidence for {name} and {peer}')
        hits, count, fraction = (pair.get('candidate_dots_within_3px'),
                                 pair.get('candidate_dots'), pair.get('overlap_fraction'))
        if (type(hits) is not int or type(count) is not int or count != expected_count
                or count <= 0 or not 0 <= hits <= count
                or type(fraction) not in (int, float) or not 0 <= fraction <= 1
                or not math.isfinite(fraction) or abs(fraction - hits / count) > 1e-12
                or pair.get('overlap_exceeds_70_percent') is not (hits * 10 > count * 7)):
            raise ValueError(f'bad directional pair evidence for {name} and {peer}')
        witnesses.append((fraction, peer))
    strongest = max(witnesses)
    if strongest[0] <= 0.70:
        raise ValueError(f'no peer duplicate witness for {name}')
    return strongest


def evidence():
    claims = json.loads((ROOT / 'registry/historical_claims.json').read_text())
    entries = json.loads((ROOT / 'registry/reference_assets.json').read_text())
    ref = json.loads((DOCS / 'data/reference-audit.json').read_text())
    audit = json.loads((ROOT / 'evidence/candidate_audit_20261028.json').read_text())
    card = json.loads((DOCS / 'data/run-card.json').read_text())
    session = json.loads((ROOT / 'evidence/session_run_card_5c261093.json').read_text())
    holdout = session.get('holdout_dti')
    if (len(claims) != 9 or {r['site'] for r in claims} != set(SITES)
            or card.get('verdict') != 'negative' or card.get('ok_to_submit') is not False
            or audit.get('upload_authorized') is not False or audit.get('registry_complete') is not False
            or session.get('verdict') != 'negative' or session.get('ok_to_submit') is not False
            or session.get('download_available') is not False or session.get('slot_selected_or_spent') is not False
            or session.get('raster_sha256') is not None or type(session.get('geological_experiments_run')) is not int
            or session['geological_experiments_run'] != 0
            or not isinstance(holdout, dict) or holdout.get('value') is not None):
        raise ValueError('site evidence incomplete or not fail-closed')
    assets = {a['id']: a for a in entries}
    expected_pairs = {f'{a}->{b}' for a in SITES for b in SITES if a != b}
    pairs = ref.get('directed_pairs')
    if ref.get('submit_authorized') is not False or not isinstance(pairs, dict) or set(pairs) != expected_pairs:
        raise ValueError('nine-site pairwise evidence incomplete')
    for claim in claims:
        name = claim['site']
        row = ref['rows'][name]
        n, hits = row['positive_pixels'], row['lattice_nearby_count']
        overlap = row['lattice_directed_overlap']
        if (claim['score_class'] != 'USER-REPORTED / UNVERIFIED'
                or row['sha256'] != assets[name]['sha256']
                or assets[name]['repo'] != f'buffedlizard55-lab/{name}'
                or not re.fullmatch(r'[0-9a-f]{40}', assets[name]['ref'])
                or type(n) is not int or type(hits) is not int or n <= 0 or not 0 <= hits <= n
                or hits * 10 <= n * 7 or row['literal_lattice_duplicate'] is not True
                or type(overlap) not in (int, float) or not 0 <= overlap <= 1
                or not math.isfinite(overlap) or abs(overlap - hits / n) > 1e-12):
            raise ValueError(f'bad reference evidence for {name}')
        strongest_peer_witness(name, ref)
    candidates = audit.get('candidates', [])
    if len(candidates) != 2 or card.get('download_available') is not False or card.get('slot_selected_or_spent') is not False:
        raise ValueError('candidate or slot decision incomplete')
    historical = (json.loads((ROOT / 'evidence/run_card_hmas_sinter.json').read_text()),
                  json.loads((ROOT / 'evidence/run_card_gpcz.json').read_text()))
    files = (historical[0]['submission_file'], historical[1]['raster']['zeros_tif'])
    hashes = (historical[0]['raster_sha256'], historical[1]['raster']['sha256'])
    for c, filename, expected_hash in zip(candidates, files, hashes):
        digest = hashlib.sha256((DOCS / 'downloads' / c['file']).read_bytes()).hexdigest()
        witness = c['comparisons'][0]
        count, hits, overlap = (witness.get('candidate_dots'),
                                witness.get('candidate_dots_within_3px'),
                                witness.get('directed_overlap'))
        checks = c['format_checks']
        required_true = ('single_band', 'float32', 'crs_shape_transform_match_mirror',
                         'no_nonfinite_inside', 'inside_values_in_0_1')
        required_zero = ('nonfinite_inside_count', 'out_of_range_inside_count', 'masked_inside_count')
        if (c['file'] != filename or c['sha256'] != expected_hash or digest != expected_hash
                or c['verdict'] != 'duplicate' or witness['reference'] != 'lattice'
                or witness['reference_sha256'] != assets['lattice']['sha256']
                or type(count) is not int or count <= 0
                or type(hits) is not int or not 0 <= hits <= count
                or count != c['positive_pixels_in_footprint'] or hits * 10 <= count * 7
                or witness.get('overlap_exceeds_70_percent') is not True
                or type(overlap) not in (int, float) or not 0 <= overlap <= 1
                or not math.isfinite(overlap) or abs(overlap - hits / count) > 1e-12
                or any(checks.get(key) is not True for key in required_true)
                or any(type(checks.get(key)) is not int or checks[key] != 0 for key in required_zero)
                or checks.get('outside_all_null_or_nan') is not False):
            raise ValueError(f'candidate audit and saved bytes disagree: {c["file"]}')
    if card['raster_sha256'] != candidates[0]['sha256']:
        raise ValueError('current card does not identify the audited artifact')
    return claims, assets, ref, audit, card


def artifact_url(entry):
    return ('https://github.com/' + entry['repo'] + '/blob/' + entry['ref'] + '/'
            + quote(entry['path'], safe='/'))


def rows_for(prefix: str):
    claims, assets, ref, _, _ = evidence()
    rows = []
    for claim in sorted(claims, key=lambda x: -x['reported_score']):
        name = claim['site']
        entry, measured = assets[name], ref['rows'][name]
        peer_overlap, peer_name = strongest_peer_witness(name, ref)
        filename = Path(entry['path']).name
        rows.append(
            f'<tr><th scope="row"><a href="{prefix}docs/{name}.html">{esc(name)} ↗</a></th>'
            f'<td><a class="file-link" href="{esc(artifact_url(entry), quote=True)}">{esc(filename)}</a>'
            '<span class="cell-sub">Historical reference · research only</span></td>'
            f'<td><strong>{claim["reported_score"]:.4f}</strong><span class="cell-sub">USER-REPORTED · UNVERIFIED</span></td>'
            '<td>Unavailable<span class="cell-sub">No defensible forecast</span></td>'
            f'<td><span class="pill pill-red">NO</span><span class="cell-sub">{peer_overlap:.2%} of its dots within 3 px of {esc(peer_name)}</span>'
            f'<span class="cell-sub">{measured["lattice_directed_overlap"]:.2%} vs lattice</span></td>'
            '<td><span class="pill pill-red">DO NOT RESUBMIT</span></td></tr>'
        )
    return '\n'.join(rows)


def source_chips():
    """Use each audited artifact's immutable commit, not a guessed HEAD."""
    _, assets, _, _, _ = evidence()
    return '\n'.join(
        f'<div class="feed-chip" data-source-repo="{esc(assets[s]["repo"], quote=True)}" '
        f'data-source-ref="{esc(assets[s]["ref"], quote=True)}">'
        f'<a href="https://github.com/{esc(assets[s]["repo"], quote=True)}">{esc(s)}</a>'
        ' <span data-source-state data-state="unknown">Not checked</span></div>'
        for s in SITES
    )


def build():
    """Compatibility entry point used by site tests; no live score scraper."""
    return rows_for(''), source_chips()


def source_monitor():
    return f'''<section class="feed-panel" aria-labelledby="feed-title">
<div class="feed-intro"><div><p class="eyebrow">PEER REPOSITORY MONITOR</p>
<h2 id="feed-title">Are the source revisions newer?</h2><p>Your browser checks the nine public GitHub repositories against the immutable commits used for these historical files. This does not check scores, inspect newer rasters or approve a submission.</p></div>
<button type="button" class="button button-outline" id="refresh-sources">Check revisions</button></div>
<p class="feed-status" id="feed-status" role="status" aria-live="polite">Not checked yet. A failed or unavailable check is not a pass.</p>
<div class="feed-grid">{source_chips()}</div>
<p class="feed-footnote">Changed means the repository has moved; its newer contents have not been audited. Even an unchanged revision does not establish a complete registry. Checks use GitHub, not the DrivenData site; GitHub rate limits or network errors are reported as unavailable.</p>
<noscript><p class="feed-footnote">JavaScript is disabled; source revisions have not been checked.</p></noscript></section>'''


def shell(title: str, body: str, depth: int = 0, active: str = 'Overview'):
    p = '../' * depth
    doc = p + 'docs/'
    links = [('Overview', p + 'index.html'), ('Executive summary', doc + 'executive-summary.html'),
             ('Research', doc + 'research.html')]
    nav = ''.join(f'<a {"class=active aria-current=page " if n == active else ""}href="{href}">{n}</a>' for n, href in links)
    monitor_script = f'<script defer src="{doc}assets/app.js"></script>' if 'id="refresh-sources"' in body else ''
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Auditable submission decisions and research for the DOE GEMS fault-mapping prize.">
<meta name="theme-color" content="#f6f8f5"><title>{esc(title)} · GEMS Field Intelligence</title>
<link rel="stylesheet" href="{doc}assets/styles.css"><link rel="stylesheet" href="{doc}assets/decision.css">{monitor_script}</head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="header-inner container">
<a class="brand" href="{p}index.html"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 36 36"><path d="M5 25 13.3 8h8.5L31 25h-7.3L17.5 13 11.8 25Z"/><path d="M12 25h13"/></svg></span><span><strong>GEMS</strong><small>FIELD INTELLIGENCE</small></span></a>
<nav class="main-nav" aria-label="Main navigation">{nav}</nav><a class="header-link" href="https://github.com/karagemop466-tech/GEMSDOEkarage1">View repository ↗</a></div>
<div class="container"><p class="global-hold"><strong>DO NOT SUBMIT</strong> · No candidate has been cleared.</p></div></header>
<main id="main"><div class="container">{body}</div></main><footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div><div class="footer-links"><a href="{p}evidence/session_run_card_5c261093.json">Session run card</a><a href="{doc}research.html">Research</a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition ↗</a></div><div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with the organizers.</span></div></div></footer></body></html>'''


def parallel_candidates(assets: dict) -> tuple[dict, dict]:
    """Validate the separate, single-witness parallel audit before displaying it."""
    report = json.loads((ROOT / 'evidence/parallel_candidates_audit_20261028.json').read_text())
    if not isinstance(report, dict):
        raise ValueError('Parallel candidate evidence must be reviewed before rendering')
    rows = report.get('candidates')
    if (report.get('lattice_sha256') != assets['lattice']['sha256']
            or report.get('template_sha256') != assets['template']['sha256']
            or not isinstance(rows, dict) or set(rows) != {'td', 'ctws'}):
        raise ValueError('Parallel candidate evidence must be reviewed before rendering')
    for name, pr in (('td', 20), ('ctws', 19)):
        row = rows[name]
        if not isinstance(row, dict):
            raise ValueError('Parallel candidate evidence must be reviewed before rendering')
        count, hits, overlap = (row.get('candidate_dots_in_footprint'),
                                row.get('dots_within_3px'), row.get('directed_overlap'))
        if (row.get('pr') != pr or type(count) is not int or count <= 0
                or type(hits) is not int or not 0 <= hits <= count or hits * 10 <= count * 7
                or type(overlap) not in (int, float) or not 0 <= overlap <= 1
                or not math.isfinite(overlap) or abs(overlap - hits / count) > 1e-12
                or row.get('duplicate_over_70_percent') is not True
                or row.get('preplacement_surface_checked') is not False
                or row.get('ok_to_submit') is not False
                or not isinstance(row.get('sha256'), str)
                or not re.fullmatch(r'[0-9a-f]{64}', row['sha256'])):
            raise ValueError('Parallel candidate evidence must be reviewed before rendering')
    return rows['td'], rows['ctws']


def decision(prefix: str):
    _, assets, _, audit, _ = evidence()
    a, b = audit['candidates']
    ar, br = a['comparisons'][0], b['comparisons'][0]
    td, ctws = parallel_candidates(assets)
    return f'''<section class="decision-panel" aria-labelledby="decision-title"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT SUBMISSION DECISION <span class="status-tag">DO NOT SUBMIT</span></div>
<h2 id="decision-title">No eligible submission file yet.</h2><p>Both previously promoted files fail the required registry proximity rule. The saved HMAS file has <strong>{ar['directed_overlap']:.2%}</strong> of its dots within 3 pixels of the registered lattice; GPC-Z has <strong>{br['directed_overlap']:.2%}</strong>. The limit is 70%. A different hash is not enough to prove uniqueness.</p>
<p>Parallel PR candidates TD-KSCK and CTWS-2D also fail this rule: <strong>{td['directed_overlap']:.2%}</strong> and <strong>{ctws['directed_overlap']:.2%}</strong> within 3 pixels of the same lattice. Their alternative pass reports excluded that witness. <a href="{prefix}knowledge/parallel-candidate-audit-2026-10-28.md">Review the independent audit ↗</a></p>
<div class="decision-actions"><button class="button button-disabled" disabled>No approved .tif to download</button><a class="button button-light" href="{prefix}docs/executive-summary.html">Read the submission guide ↗</a><a class="button button-light" href="{prefix}evidence/candidate_audit_20261028.json">Inspect the audit ↗</a></div>
<p class="download-help">No new experiment or competition upload was run in this review. A separate selector decides a weekly slot only after all gates pass. <a href="{prefix}evidence/session_5b69d76e_prior_audit.json">Replayed lattice audit ↗</a></p></div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative · duplicate</strong></div><div><span>LEADERBOARD ESTIMATE</span><strong>Unavailable</strong></div><div><span>PRE-PLACEMENT SURFACE</span><strong>Not available</strong></div><a href="{prefix}evidence/session_run_card_5c261093.json">Session run card ↗</a></div></section>'''


def comparison(prefix: str):
    return f'''<section class="section comparison" id="comparison"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> HISTORICAL REFERENCE</p><h2>Nine sites. One careful decision.</h2><p>The highest figures supplied for each site are unverified user reports, not file-linked organizer receipts. They are not predictions of a new file's score. For each historical file the table shows its strongest directional overlap with one of the other eight, plus the lattice witness. None is recommended for resubmission; this is not a complete registry audit.</p></div></div>
<div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table →</div><div class="table-scroll" tabindex="0" role="region" aria-label="Nine-site comparison"><table><thead><tr><th>Site</th><th>Historical file · research only</th><th>Historical report</th><th>New score estimate</th><th>Unique vs eight?</th><th>Action</th></tr></thead><tbody>{rows_for(prefix)}</tbody></table></div></div></section>'''


def home(depth=0):
    p = '../' * depth
    return f'''<div class="page-top"><span>GEMS PRIZE <span class="separator">/</span> DECISION BRIEF</span><span class="page-date">INDEPENDENT AUDIT · 28 OCT 2026</span></div>
<section class="hero compact-hero"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-line"></span> EVIDENCE BEFORE A LEADERBOARD SLOT</p><h1>Find faults.<br><em>Protect every submission.</em></h1><p class="hero-description">A clear, auditable workspace for fault discovery in the Great Basin. We separate format checks, scientific evidence, uniqueness and actual portal acceptance.</p><div class="hero-actions"><a class="text-link" href="#comparison">Compare the nine sites ↓</a><a class="subtle-link" href="{p}docs/research.html">Explore the research ↗</a></div></div>
<div class="terrain-card terrain-small" aria-label="Illustrative contour artwork, not a prediction map"><div class="terrain-top"><span>GEO<span class="terrain-dot">●</span>DAWN</span><span>FIELD NOTE / 01</span></div><svg class="terrain-lines" viewBox="0 0 620 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.5"><path d="M-50 10C90 25 95 155 200 110S305-10 410 55s150 110 250 40"/><path d="M-50 35C80 50 100 180 205 135S310 15 410 80s150 110 250 40"/><path d="M-50 60C70 75 105 205 210 160S315 40 410 105s150 110 250 40"/><path d="M-50 85C60 100 110 230 215 185S320 65 410 130s150 110 250 40"/><path d="M-50 110C50 125 115 255 220 210S325 90 410 155s150 110 250 40"/><path d="M-50 135C40 150 120 280 225 235S330 115 410 180s150 110 250 40"/><path d="M-50 160C30 175 125 305 230 260S335 140 410 205s150 110 250 40"/></g><g class="terrain-focus" fill="none"><circle cx="379" cy="139" r="40"/><circle cx="379" cy="139" r="26"/><path d="M379 89v100M329 139h100"/></g></svg><div class="terrain-caption"><span><b>THE STUDY AREA</b><br>Western Great Basin</span><span>NEVADA + CALIFORNIA<br><b>CONCEPTUAL ONLY</b></span></div></div></section>
{decision(p)}<section class="snapshot" aria-label="Evidence snapshot"><div class="snapshot-item"><div class="snapshot-label">PUBLIC LEADERBOARD SNAPSHOT</div><div class="snapshot-value">0.4544</div><p>ORGANIZER-PUBLISHED public leaderboard snapshot · 28 Oct 2026 · not a score for this project · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">check current ↗</a></p></div><div class="snapshot-item"><div class="snapshot-label">BEST SUPPLIED NINE-SITE REPORT</div><div class="snapshot-value">0.2778</div><p>GEMSDOE32 · USER-REPORTED, not confirmed</p></div><div class="snapshot-item"><div class="snapshot-label">THIS SESSION</div><div class="snapshot-value">0 <span class="snapshot-context">experiments</span></div><p>Duplicate stop rule applied</p></div><div class="snapshot-item"><div class="snapshot-label">PRIOR INPUT RESTORATION</div><div class="snapshot-value">31 <span class="snapshot-context">files</span></div><p>Prior hash-pinned mirrors · not organizer-authenticated or necessarily present now</p></div></section>
{comparison(p)}<section class="section detail-grid"><div><p class="eyebrow"><span class="eyebrow-line"></span> THE B2 QUESTION</p><h2>What made the reported leader different?</h2></div><div class="prose-card"><p>On the audited mirrored grid, GEMSDOE32 B2 is exactly GEMSDOE25's d2.8 mask with 6,436 dots within two pixels of the mirrored known-fault catalogue removed; no new dots were added. GEMSDOE25 and GEMSDOE30 have the same positive-pixel mask.</p><p>Reducing redundant prediction mass <em>could</em> improve the distance-weighted Tversky tradeoff, but it can also remove true coverage. Hidden labels and an artifact-linked receipt are unavailable, so the cause and any improvement over the reported result remain unproven.</p><p>Known fault pixels are masked, but nearby new faults may still matter. A catalogue buffer is not automatically a free scoring exclusion. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">DrivenData staff clarification ↗</a></p><a class="text-link" href="{p}docs/research.html#b2">Read the scientific analysis ↗</a></div></section>
{source_monitor()}<section class="next-strip"><div><p class="eyebrow">NEXT STEPS</p><h2>Resolve the gate before spending a slot.</h2><p>Restore the shared feature cache, establish the assigned lane and complete registry, then run a fold-safe holdout. No automatic DrivenData scraping or upload.</p></div><a class="button button-dark" href="{p}docs/executive-summary.html">See the checklist ↗</a></section>'''


def guide(depth=1):
    p = '../' * depth
    _, _, _, audit, _ = evidence()
    cand = audit['candidates']
    cards = []
    for label, c in zip(('HMAS-SINTER', 'GPC-Z'), cand):
        row = c['comparisons'][0]
        cards.append(f'''<article class="audit-card"><p class="eyebrow">HISTORICAL ARTIFACT · {label}</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(c['file'])}</code></p><p>SHA-256 <code class="wrap">{c['sha256']}</code></p><p>{row['candidate_dots_within_3px']:,} / {row['candidate_dots']:,} dots within 3 px of lattice ({row['directed_overlap']:.2%}) · duplicate. Mirror-grid and inside [0,1] checks pass; null/NaN-outside check fails. Portal acceptance is untested.</p><a class="text-link" href="{p}docs/downloads/{quote(c['file'])}" download>Download for research only ↗</a></article>''')
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> EXECUTIVE SUMMARY</span><span class="page-date">REVIEWED 28 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> THE SUBMISSION CHECKLIST</p><h1>One file. <em>Evidence first.</em></h1><p>What to submit, when—and why today's answer is no.</p></section>{decision(p)}
<section class="section" id="audit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> SAVED-BYTE CHECK</p><h2>Two prior files, both blocked.</h2><p>Research downloads are explicitly not submission recommendations. The comparisons cover a pinned lattice and one historical raster from each focus site, not the complete registry.</p></div></div><div class="audit-grid">{''.join(cards)}</div><p class="body-copy">The official <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format">format description</a> says data outside the bounds should be null or NaN. These files use zeros outside the mirrored footprint. A strict all-finite check and a null/NaN-outside check are different diagnostics; neither establishes actual portal acceptance. The rejected original file was not supplied, so the cause of its range error is unknown.</p></section>
{comparison(p)}{source_monitor()}<section class="section" id="steps"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> FOR A FUTURE CLEARED CANDIDATE</p><h2>How to submit, once eligible.</h2><p>These steps are not permission to upload either historical artifact.</p></div></div><div class="steps-grid"><article><span>01 / EVIDENCE</span><h3>Pass the automated gates</h3><p>Use the shared evaluator, fold-local features and per-feature canaries. Beat a frozen comparable holdout best; audit surface and dots against the complete registry; reopen the TIFF and validate saved bytes.</p></article><article><span>02 / SELECTOR</span><h3>Choose a slot separately</h3><p>Only an independent selector may choose an eligible candidate and check the current allowance on the authenticated submission page. The September rules say three submissions per week.</p></article><article><span>03 / DOWNLOAD</span><h3>Choose the exact file</h3><p>Download the approved single-band GeoTIFF (or a ZIP containing one GeoTIFF). Check its displayed SHA-256, unique name and note of at most 140 characters.</p></article><article><span>04 / UPLOAD</span><h3>Use the official form</h3><p>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData</a>, select Submit → Make new submission, choose the .tif or ZIP, and paste the note. Retain the file-linked organizer receipt.</p></article></div><div class="notice guide-notice"><span aria-hidden="true">ⓘ</span><p>The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> require disclosure of generative-AI use in the narrative when applicable. Public leaderboard performance is not the private final score.</p></div></section>'''


def research(depth=1):
    p = '../' * depth
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> RESEARCH</span><span class="page-date">REVIEWED 28 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SCIENCE BEFORE SCORING</p><h1>Understand the ground.<br><em>Respect the unknown.</em></h1><p>The target is previously unmapped geological faults, not direct proof of a geothermal vent.</p></section>
<section class="notice"><span aria-hidden="true">ⓘ</span><p><strong>Research only:</strong> The ideas below are qualitative proposals. No assigned lane or validated new candidate is available, and novelty across all peer work is unverified.</p></section>
<section class="section detail-grid" id="b2"><div><p class="eyebrow"><span class="eyebrow-line"></span> WHAT THE BYTES SHOW</p><h2>Why B2 may have worked.</h2></div><div class="prose-card"><p>The mirrored B2 mask is exactly the GEMSDOE25 parent minus 6,436 dots within 2 pixels of the visible catalogue. That geometric relationship is measurable; its effect on hidden-label DTI is not.</p><p>For the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric">organizer metric</a>, deleting predictions helps only if the saved false-positive penalty outweighs the loss of distance-weighted true coverage. Spacing can reduce redundant mass; deleting near a catalogue can also miss a nearby new fault. A controlled, identical-fold ablation is needed.</p><p>The reported 0.2778 is an unverified user report. No experiment here establishes a higher leaderboard result.</p></div></section>
<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> RANKED HYPOTHESES · NOT EXECUTED</p><h2>Four ideas worth testing.</h2><p>Ordering reflects qualitative promise relative to cost, not a predicted DTI improvement. The first requires the shared cached layers and an assigned lane; it has not passed holdout.</p></div></div><div class="hypothesis-grid">
<article class="hypothesis-card"><span class="hypothesis-rank">01 <span>MEDIUM COST</span></span><h3>Signed multiscale offsets</h3><p>Use RTP magnetics, isostatic gravity and detrended elevation: compare oriented, signed cross-profiles at two scales. Stable offsets may indicate a buried discontinuity without a mapped scarp.</p><div><b>Confounders:</b> lithologic contacts, volcanic flow edges and survey artifacts.</div><small>Proposes paired magnetic–gravity displacement, but HMAS already measures gravity-crest migration; distinctness requires verification.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">02 <span>MEDIUM COST</span></span><h3>Alteration-boundary residuals</h3><p>Compare local background-normalized K/eTh radiometric boundaries with oriented RTP edges. An altered structure under cover might differ from the catalogue.</p><div><b>Confounders:</b> weathering, potassium-rich intrusions and acquisition blocks.</div><small>Tests directional residuals rather than the prior raw radiometric plume. <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN ↗</a></small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">03 <span>HIGH COST</span></span><h3>Drainage asymmetry</h3><p>On USGS 3DEP DEMs, test repeated cross-valley asymmetry among adjacent catchments, conditioned on drainage area. A degraded or obscured trace could alter drainage geometry.</p><div><b>Confounders:</b> stream piracy, fan deposition and erosion.</div><small>Different from the prior pixel-level scarp score. <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP ↗</a>; local official tiles not fetched.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">04 <span>HIGH COST</span></span><h3>Sampling-aware thermal residuals</h3><p>Cross-fit INGENIOUS 2 m probe temperatures against terrain and access, then compare residual patterns with gravity boundaries. Concealed flow could remain near an unmapped structure.</p><div><b>Confounders:</b> solar heating, groundwater and access-biased sampling.</div><small>Unlike the earlier raw thermal plume, explicitly models sampling bias. <a href="https://gdr.openei.org/submissions/1391">GDR 1391 ↗</a>; official raw bytes not authenticated locally.</small></article></div></section>
<section class="section" id="sources"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> TRACEABLE REFERENCES</p><h2>Go back to the source.</h2><p>These official descriptions do not authenticate the third-party mirrors or validate the hypotheses.</p></div></div><div class="source-list"><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"><span><b>DrivenData · problem and metric</b><small>Target, features, score and format</small></span><span>OFFICIAL ↗</span></a><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf"><span><b>DOE / NLR · rules</b><small>Submission limits, eligibility and AI disclosure</small></span><span>OFFICIAL ↗</span></a><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and"><span><b>USGS · GeoDAWN</b><small>Magnetic and radiometric grids · CC0</small></span><span>OFFICIAL ↗</span></a><a href="https://gdr.openei.org/submissions/1391"><span><b>GDR · INGENIOUS</b><small>Thermal, geology and geophysics compilation · CC BY 4.0</small></span><span>OFFICIAL ↗</span></a><a href="https://github.com/drivendataorg/gems-prize-reference-solution"><span><b>DrivenData · reference implementation</b><small>Organizer-provided starting point</small></span><span>CODE ↗</span></a><a href="{p}knowledge/sources-2026-10-28.md"><span><b>Project source register</b><small>Access, provenance and limitations</small></span><span>REVIEW ↗</span></a></div></section>'''


def standing_brief(depth=1):
    p = '../' * depth
    brief = (DOCS / 'standing-prompt.md').read_text()
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> STANDING BRIEF</span><span class="page-date">RECONSTRUCTED REQUIREMENTS</span></div>
<section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> READ BEFORE EACH SESSION</p><h1>Standards. <em>Not shortcuts.</em></h1><p>This inherited record is reconstructed, not a verbatim transcript of the original user prompt.</p></section>
{decision(p)}<section class="section"><div class="prose-card"><pre class="brief-pre">{esc(brief)}</pre></div></section>'''


def site_page(name: str):
    claims, assets, ref, _, _ = evidence()
    claim = next(x for x in claims if x['site'] == name)
    entry, row = assets[name], ref['rows'][name]
    pair = strongest_peer_witness(name, ref)
    return f'''<div class="page-top"><span>NINE-SITE REVIEW <span class="separator">/</span> {name}</span><span class="page-date">28 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SITE EXECUTIVE SUMMARY</p><h1>{name}. <em>Research only.</em></h1><p>The reported historical leader is not a newly eligible submission.</p></section>{decision('../')}
<section class="section detail-grid"><div><p class="eyebrow">HISTORICAL FILE</p><h2>What the evidence says.</h2></div><div class="prose-card"><p><a class="wrap" href="{esc(artifact_url(entry), quote=True)}">{esc(Path(entry['path']).name)} ↗</a><br>SHA-256 <code class="wrap">{entry['sha256']}</code></p><p><strong>{claim['reported_score']:.4f} USER-REPORTED · UNVERIFIED.</strong> No artifact-linked organizer submission receipt is available. A new leaderboard estimate is unavailable.</p><p>The file has {row['positive_pixels']:,} positive pixels; {row['lattice_directed_overlap']:.2%} fall within 3 pixels of the registered lattice. It also overlaps {pair[0]:.2%} with {pair[1]} in the directional nine-file audit. Both exceed the literal 70% threshold. <strong>DO NOT RESUBMIT.</strong></p><p>These are geometric measurements, not proof of equal geologic predictions or a forecast. Scope is one historical raster per site plus the lattice; complete current-registry uniqueness was not checked.</p><a class="text-link" href="data/reference-audit.json">Review the measured audit ↗</a></div></section><section class="next-strip"><div><p class="eyebrow">BACK TO THE DECISION</p><h2>No new file is cleared.</h2><p>Check the current gates and submission guide before considering any upload.</p></div><a class="button button-dark" href="executive-summary.html">Executive summary ↗</a></section>'''


def main():
    # One builder owns all public decision/guide pages so an old lane-specific
    # generator cannot silently restore a false green badge.
    evidence()
    pages = {
        ROOT / 'index.html': shell('Submission overview', home(0), 0),
        ROOT / 'legacy-overview.html': shell('Submission overview', home(0), 0),
        ROOT / 'executive-summary.html': shell('Submission guide', guide(0), 0, 'Executive summary'),
        DOCS / 'index.html': shell('Submission overview', home(1), 1),
        DOCS / 'executive-summary.html': shell('Executive summary', guide(1), 1, 'Executive summary'),
        DOCS / 'legacy-executive-summary.html': shell('Executive summary', guide(1), 1, 'Executive summary'),
        DOCS / 'how-to-submit.html': shell('Submission guide', guide(1), 1, 'Executive summary'),
        DOCS / 'submission-guide.html': shell('Submission guide', guide(1), 1, 'Executive summary'),
        DOCS / 'nine-sites.html': shell('Nine-site comparison', home(1), 1),
        DOCS / 'research.html': shell('Research', research(1), 1, 'Research'),
        DOCS / 'sources.html': shell('Sources', research(1), 1, 'Research'),
        DOCS / 'knowledge.html': shell('Knowledge', research(1), 1, 'Research'),
        DOCS / 'legacy-research.html': shell('Research', research(1), 1, 'Research'),
        DOCS / 'standing-prompt.html': shell('Standing brief', standing_brief(1), 1),
        DOCS / 'gpcz/standing-prompt.html': shell('Standing brief', standing_brief(2), 2),
        DOCS / 'gpcz/index.html': shell('GPC-Z audit', guide(2), 2, 'Executive summary'),
        DOCS / 'gpcz/how-to-submit.html': shell('Submission guide', guide(2), 2, 'Executive summary'),
        DOCS / 'gpcz/nine-sites.html': shell('Nine-site comparison', home(2), 2),
        DOCS / 'gpcz/research.html': shell('Research', research(2), 2, 'Research'),
        DOCS / 'gpcz/knowledge.html': shell('Knowledge', research(2), 2, 'Research'),
        DOCS / 'gpcz/sources.html': shell('Sources', research(2), 2, 'Research'),
        DOCS / 'hmas-sinter/index.html': shell('HMAS audit', guide(2), 2, 'Executive summary'),
        DOCS / 'hmas-sinter/executive-summary.html': shell('Submission guide', guide(2), 2, 'Executive summary'),
    }
    for name in SITES:
        pages[DOCS / f'{name}.html'] = shell(name + ' executive summary', site_page(name), 1)
    for path, content in pages.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        # Never expose truncated pages to readers or concurrent CI/build jobs.
        fd, temp_name = tempfile.mkstemp(prefix='.' + path.name + '.', suffix='.partial', dir=path.parent)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as out:
                out.write(content + '\n')
            os.chmod(temp_name, 0o644)
            os.replace(temp_name, path)
        finally:
            Path(temp_name).unlink(missing_ok=True)
    print(f'Rendered {len(pages)} deterministic decision pages; no submission authorized.')


if __name__ == '__main__':
    main()
