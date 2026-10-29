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
import re
from pathlib import Path
import tempfile
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
SITES = tuple(f'GEMSDOE{n}' for n in (24, 25, 27, 28, 30, 31, 32, 33, 36))
esc = html.escape


def evidence():
    claims = json.loads((ROOT / 'registry/historical_claims.json').read_text())
    entries = json.loads((ROOT / 'registry/reference_assets.json').read_text())
    ref = json.loads((DOCS / 'data/reference-audit.json').read_text())
    audit = json.loads((ROOT / 'evidence/candidate_audit_20261028.json').read_text())
    card = json.loads((DOCS / 'data/run-card.json').read_text())
    try:
        uniq = json.loads((ROOT / 'evidence/bbstep_uniqueness.json').read_text())
    except FileNotFoundError as exc:
        raise ValueError('BB-STEP uniqueness evidence missing') from exc
    if (len(claims) != 9 or {r['site'] for r in claims} != set(SITES)
            or card.get('verdict') != 'negative' or card.get('ok_to_submit') is not False
            or audit.get('upload_authorized') is not False or audit.get('registry_complete') is not False):
        raise ValueError('site evidence incomplete or not fail-closed')
    if card.get('slot_selected_or_spent') is not False:
        raise ValueError('candidate or slot decision incomplete')
    assets = {a['id']: a for a in entries}
    for claim in claims:
        name = claim['site']
        if (claim['score_class'] != 'USER-REPORTED / UNVERIFIED'
                or ref['rows'][name]['sha256'] != assets[name]['sha256']
                or not ref['rows'][name]['literal_lattice_duplicate']):
            raise ValueError(f'bad reference evidence for {name}')
    candidates = audit.get('candidates', [])
    if len(candidates) != 2:
        raise ValueError('candidate or slot decision incomplete')
    historical = (json.loads((ROOT / 'evidence/run_card_hmas_sinter.json').read_text()),
                  json.loads((ROOT / 'evidence/run_card_gpcz.json').read_text()))
    files = (historical[0]['submission_file'], historical[1]['raster']['zeros_tif'])
    hashes = (historical[0]['raster_sha256'], historical[1]['raster']['sha256'])
    for c, filename, expected_hash in zip(candidates, files, hashes):
        digest = hashlib.sha256((DOCS / 'downloads' / c['file']).read_bytes()).hexdigest()
        witness = c['comparisons'][0]
        if (c['file'] != filename or c['sha256'] != expected_hash or digest != expected_hash
                or c['verdict'] != 'duplicate' or witness['reference'] != 'lattice'
                or witness['reference_sha256'] != assets['lattice']['sha256']
                or witness['candidate_dots'] != c['positive_pixels_in_footprint']
                or witness['candidate_dots_within_3px'] * 10 <= witness['candidate_dots'] * 7
                or abs(witness['directed_overlap'] - witness['candidate_dots_within_3px'] / witness['candidate_dots']) > 1e-12):
            raise ValueError(f'candidate audit and saved bytes disagree: {c["file"]}')
    bb = DOCS / 'downloads' / card['submission_name']
    if hashlib.sha256(bb.read_bytes()).hexdigest() != card['raster_sha256']:
        raise ValueError('current card does not match the generated BB-STEP bytes')
    if (not uniq.get('unique_vs_nine_focus_sites') or not uniq.get('lattice_duplicate_literal')
            or card['correlation_overlap_vs_registry']['lattice_duplicate_literal'] is not True
            or card['holdout_dti']['label'] != 'HOLDOUT-DTI' or card['holdout_dti']['value'] is None):
        raise ValueError('BB-STEP uniqueness / holdout evidence incomplete')
    if card.get('download_available') and 'not authorization' not in card.get('download_available_meaning', '').lower():
        raise ValueError('research download must not be presented as upload authorization')
    return claims, assets, ref, audit, card


def secondary_evidence():
    """Load and independently fail closed on the 12 secondary focus-site artifacts."""
    path = ROOT / 'evidence/nine_sites_secondary_audit_20261028.json'
    def _reject_constant(value: str):
        raise ValueError(f'non-standard JSON constant: {value}')
    data = json.loads(path.read_text(), parse_constant=_reject_constant)
    entries = json.loads((ROOT / 'registry/reference_assets.json').read_text())
    lattice = [x for x in entries if x.get('id') == 'lattice']
    rows = data.get('rows')
    if (data.get('schema') != 'karage1-nine-sites-secondary-audit-v1'
            or data.get('submit_authorized') is not False or len(lattice) != 1
            or data.get('lattice_sha256') != lattice[0].get('sha256')
            or not isinstance(rows, list) or len(rows) != 12):
        raise ValueError('secondary site evidence incomplete or not fail-closed')
    seen_hashes = set()
    seen_sources = set()
    for row in rows:
        site = row.get('site')
        dots = row.get('positive_pixels_in_footprint')
        hits = row.get('lattice_dots_within_3px')
        overlap = row.get('lattice_directed_overlap')
        reported = row.get('user_reported_score')
        ref = row.get('ref')
        digest = row.get('sha256')
        rel_path = row.get('path')
        filename = row.get('matched_file')
        if (site not in SITES or row.get('repo') != f'buffedlizard55-lab/{site}'
                or row.get('score_class') != 'USER-REPORTED / UNVERIFIED'
                or row.get('ok_to_submit') is not False
                or row.get('literal_lattice_duplicate') is not True
                or row.get('grid_and_unmasked_inside_pass') is not True
                or row.get('is_binary_inside') is not True
                or type(dots) is not int or dots <= 0
                or type(hits) is not int or not 0 <= hits <= dots or hits * 10 <= dots * 7
                or type(overlap) not in (int, float) or not math.isfinite(overlap) or abs(overlap - hits / dots) > 1e-12
                or type(reported) not in (int, float) or not math.isfinite(reported) or not 0 <= reported <= 1
                or not isinstance(ref, str) or not re.fullmatch(r'[0-9a-f]{40}', ref)
                or not isinstance(digest, str) or not re.fullmatch(r'[0-9a-f]{64}', digest)
                or digest in seen_hashes
                or type(row.get('bytes')) is not int or row['bytes'] <= 0
                or not isinstance(filename, str) or Path(filename).name != filename or not filename.endswith('.tif')
                or not isinstance(rel_path, str) or rel_path != f'docs/downloads/{filename}'
                or (site, filename) in seen_sources):
            raise ValueError(f'secondary site evidence failed fail-closed check: {row.get("matched_file")}')
        seen_hashes.add(digest)
        seen_sources.add((site, filename))
    return data


def conduitcrest_evidence():
    """Verify the superseding saved-byte lattice audit and negative decision."""
    def _reject_constant(value: str):
        raise ValueError(f'non-standard JSON constant: {value}')
    audit = json.loads((ROOT / 'evidence/conduitcrest_lattice_reaudit_20261028.json').read_text(),
                       parse_constant=_reject_constant)
    old_card_path = ROOT / 'evidence/run_card_gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4.json'
    old_card = json.loads(old_card_path.read_text(), parse_constant=_reject_constant)
    latest = json.loads((DOCS / 'data/latest-run-card.json').read_text(), parse_constant=_reject_constant)
    candidate = audit.get('candidate', {})
    lattice = audit.get('lattice_witness', {})
    name = candidate.get('path')
    if not name:
        name = 'docs/downloads/' + old_card.get('submission_name', '')
    if name.startswith('docs/downloads/'):
        candidate_path = ROOT / name
    else:
        candidate_path = DOCS / 'downloads' / name
    if (audit.get('schema') != 'karage1-mainline-candidate-lattice-audit-v1'
            or not candidate_path.is_file()
            or hashlib.sha256(candidate_path.read_bytes()).hexdigest() != candidate.get('sha256')
            or candidate.get('sha256') != old_card.get('raster', {}).get('sha256')
            or old_card.get('verdict') != 'negative'
            or old_card.get('registry_correlation_overlap', {}).get('unique_by_literal_rule') is not False
            or old_card.get('holdout_dti', {}).get('ci95') is not None
            or old_card.get('leakage_canary', {}).get('passed') is not False
            or latest.get('verdict') != 'negative'
            or latest.get('ok_to_submit') is not False
            or latest.get('assigned_method_lane', {}).get('active_assignment') is not False
            or latest.get('raster', {}).get('sha256') != candidate.get('sha256')
            or latest.get('registry_correlation_overlap', {}).get('unique_by_literal_rule') is not False
            or latest.get('post_run_lattice_audit', {}).get('directed_overlap') != lattice.get('directed_overlap')
            or lattice.get('exceeds_overlap_threshold') is not True
            or lattice.get('literal_rule_verdict') != 'duplicate; stop'
            or audit.get('ok_to_submit') is not False):
        raise ValueError('Conduitcrest candidate lacks a bound fail-closed lattice decision')
    return audit, old_card, latest, candidate_path


def local_and_peer_evidence():
    def _reject_const(v: str):
        raise ValueError(f'non-standard JSON constant: {v}')

    def _unique_obj(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError(f'duplicate JSON key: {k}')
            out[k] = v
        return out

    data = json.loads(
        (ROOT / 'evidence/local_downloads_and_peer_audit_20261028.json').read_text(encoding='utf-8'),
        parse_constant=_reject_const,
        object_pairs_hook=_unique_obj,
    )
    if (data.get('schema') != 'karage1-local-and-peer-audit-v1'
            or data.get('submit_authorized') is not False
            or data.get('all_local_downloads_blocked') is not True
            or data.get('all_audited_peer_rasters_exceed_70pct_lattice') is not True
            or data.get('local_downloads_count') != 9
            or data.get('peer_rasters_count') != 9
            or len(data.get('local_downloads', [])) != 9
            or len(data.get('peer_rasters', [])) != 9):
        raise ValueError('Local-downloads / peer-ecosystem audit missing or not fail-closed')
    for row in (*data['local_downloads'], *data['peer_rasters']):
        if row.get('ok_to_submit') is not False or row.get('literal_lattice_duplicate') is not True:
            raise ValueError(f'Blocked audit invariant violated for {row}')
    for row in data['local_downloads']:
        p = ROOT / row['file']
        if not p.is_file() or p.stat().st_size != row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError(f'Local download bytes drifted from audited receipt: {row["file"]}')
    return data


def artifact_url(entry):
    return ('https://github.com/' + entry['repo'] + '/blob/' + entry['ref'] + '/'
            + quote(entry['path'], safe='/'))


def rows_for(prefix: str):
    claims, assets, ref, _, _ = evidence()
    rows = []
    for claim in sorted(claims, key=lambda x: -x['reported_score']):
        name = claim['site']
        entry, measured = assets[name], ref['rows'][name]
        filename = Path(entry['path']).name
        rows.append(
            f'<tr><th scope="row"><a href="{prefix}docs/{name}.html">{esc(name)} ↗</a></th>'
            f'<td><a class="file-link" href="{esc(artifact_url(entry), quote=True)}">{esc(filename)}</a>'
            '<span class="cell-sub">Historical reference · research only</span></td>'
            f'<td><strong>{claim["reported_score"]:.4f}</strong><span class="cell-sub">USER-REPORTED · UNVERIFIED</span></td>'
            '<td>Unavailable<span class="cell-sub">No defensible forecast</span></td>'
            f'<td><span class="pill pill-red">NO</span><span class="cell-sub">{measured["lattice_directed_overlap"]:.2%} vs lattice</span></td>'
            '<td><span class="pill pill-red">DO NOT RESUBMIT</span></td></tr>'
        )
    return '\n'.join(rows)


def build():
    """Compatibility entry point used by site tests; no live score scraper."""
    rows = rows_for('')
    chips = '\n'.join(f'<span data-source-repo="buffedlizard55-lab/{s}">{s}</span>' for s in SITES)
    return rows, chips


def shell(title: str, body: str, depth: int = 0, active: str = 'Overview'):
    p = '../' * depth
    doc = p + 'docs/'
    links = [('Overview', p + 'index.html'), ('Executive summary', doc + 'executive-summary.html'),
             ('Research', doc + 'research.html')]
    nav = ''.join(f'<a {"class=active aria-current=page " if n == active else ""}href="{href}">{n}</a>' for n, href in links)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="Auditable submission decisions and research for the DOE GEMS fault-mapping prize.">
<meta name="theme-color" content="#f6f8f5"><title>{esc(title)} · GEMS Field Intelligence</title>
<link rel="stylesheet" href="{doc}assets/styles.css"><link rel="stylesheet" href="{doc}assets/decision.css"></head>
<body><a class="skip-link" href="#main">Skip to content</a><header class="site-header"><div class="header-inner container">
<a class="brand" href="{p}index.html"><span class="brand-mark" aria-hidden="true"><svg viewBox="0 0 36 36"><path d="M5 25 13.3 8h8.5L31 25h-7.3L17.5 13 11.8 25Z"/><path d="M12 25h13"/></svg></span><span><strong>GEMS</strong><small>FIELD INTELLIGENCE</small></span></a>
<nav class="main-nav" aria-label="Main navigation">{nav}</nav><a class="header-link" href="https://github.com/karagemop466-tech/GEMSDOEkarage1">View repository ↗</a></div>
<div class="container"><p class="global-hold"><strong>DO NOT SUBMIT</strong> · No candidate has been cleared.</p></div></header>
<main id="main"><div class="container">{body}</div></main><footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div><div class="footer-links"><a href="{doc}data/latest-run-card.json">Latest run card</a><a href="{doc}research.html">Research</a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition ↗</a></div><div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with the organizers.</span></div></div></footer></body></html>'''


def decision(prefix: str):
    '''One fail-closed status panel shared across all generated decision pages.'''
    return f'''<section class="decision-panel" aria-labelledby="decision-title"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT SUBMISSION DECISION · 29 OCT 2026 <span class="status-tag">DO NOT SUBMIT</span></div>
<h2 id="decision-title">No eligible submission file. No new candidate was evaluated.</h2>
<p><strong>No file is cleared for download and submission.</strong> Existing local and peer rasters are <strong>not cleared for upload</strong>. This review produced no new TIFF, geological experiment, HOLDOUT-DTI result, score estimate, or weekly-slot selection. Historical research files are not approval.</p>
<p><strong>Execution is blocked before science:</strong> no method lane or authoritative canonical-template assignment is recorded; all five required shared feature/data cache inputs are missing; and the local shared-tool audit reports two vendored hash mismatches plus a template/source pin mismatch. The shared evaluator and writer therefore remain unauthorized. The historical runner also refuses to execute; it produced no TIFF.</p>
<p><strong>Highest focus-site report:</strong> GEMSDOE32 B2, 0.2778 <strong>USER-REPORTED / UNVERIFIED</strong>. The linked peer page calls it an owner report and says no submission-page receipt ties the score to the raster hash. Its 37,654-dot mask equals the GEMSDOE25 mask after removing 6,436 pixels within 2 px of the mirrored catalogue, with no added dots. That geometry does not explain the score change or show whether B2 beats another file.</p>
<p><strong>Public context:</strong> the official leaderboard snapshot fetched 29 Oct 2026 showed #1 0.4544 and #47 0.3195. Public standings are not private/final scores and do not verify the nine peer-site reports.</p>
<div class="decision-actions"><button class="button button-disabled" disabled>No cleared TIFF available</button>
<a class="button button-light" href="{prefix}docs/executive-summary.html">Nine-site executive summary ↗</a>
<a class="button button-light" href="{prefix}docs/how-to-submit.html">Submission guide ↗</a>
<a class="button button-light" href="{prefix}knowledge/session-review-arena-f40ee5b6.md">Three-pass review ↗</a>
<a class="button button-light" href="{prefix}evidence/session_f40ee5b6_shared_preflight.json">Shared preflight ↗</a></div>
<p class="download-help">Current status: research-only. No slot was selected or spent. Resume only after the assigned lane, authoritative template, permitted data, and exact registry gate are resolved; then use the shared evaluator, writer, and separate slot selector.</p></div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative · blocked</strong></div><div><span>HOLDOUT-DTI</span><strong>Not run</strong></div><div><span>SUBMISSION FILE</span><strong>None cleared</strong></div><div><span>LANE / TEMPLATE</span><strong>Unassigned / unauthorized</strong></div><a href="{prefix}evidence/session_f40ee5b6_run_card.json">Current JSON run card ↗</a></div></section>'''


def comparison(prefix: str):
    card = json.loads((DOCS / 'data/run-card.json').read_text())
    dti = card['holdout_dti']
    nine = card['correlation_overlap_vs_registry']['final_dot_overlap_worst_nine']['frac_our_dots_within_3px']
    lat = card['correlation_overlap_vs_registry']['lattice_overlap']
    conduit_audit, conduit_original, latest, conduit_path = conduitcrest_evidence()
    chdt = conduit_audit['previous_holdout_claim']
    clat = conduit_audit['lattice_witness']
    conduit_row = (
        f'<tr><th scope="row">GEMSDOEkarage1 (Conduitcrest)</th>'
        f'<td><a class="file-link" href="{prefix}docs/downloads/{quote(conduit_path.name)}">{esc(conduit_path.name)}</a>'
        '<span class="cell-sub">Prior parallel-session research artifact · audit only</span></td>'
        f'<td><strong>Incomplete HOLDOUT-DTI claim {chdt["reported_value"]:.6f}</strong>'
        f'<span class="cell-sub">{esc(chdt["evaluator_version"])} · n={chdt["withheld_positives"]:,} · 95% CI missing; not independently rerun</span></td>'
        '<td>Unavailable<span class="cell-sub">No organizer estimate</span></td>'
        f'<td><span class="pill pill-red">NO vs lattice</span><span class="cell-sub">{clat["directed_overlap"]:.2%}; 0.0% vs nine focus-site masks</span></td>'
        '<td><span class="pill pill-red">DO NOT SUBMIT</span></td></tr>'
    )
    ours = (
        f'<tr><th scope="row">GEMSDOEkarage1</th>'
        f'<td><a class="file-link" href="{prefix}docs/downloads/{quote(card["submission_name"])}">{esc(card["submission_name"])}</a>'
        '<span class="cell-sub">Prior-session research artifact · not this review</span></td>'
        f'<td><strong>{dti["value"]:.4f}</strong><span class="cell-sub">HOLDOUT-DTI · {esc(dti["evaluator_version"])} · n={dti["withheld_positives"]:,} · 95% CI [{dti["ci95"][0]:.4f}, {dti["ci95"][1]:.4f}]</span></td>'
        '<td>Unavailable<span class="cell-sub">No organizer forecast</span></td>'
        f'<td><span class="pill pill-red">NO vs lattice</span><span class="cell-sub">Yes vs 9 sites ({nine:.1%}); lattice {lat:.1%}</span></td>'
        '<td><span class="pill pill-red">DO NOT SUBMIT</span></td></tr>'
    )
    return f'''<section class="section comparison" id="comparison"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> HISTORICAL FILES · RESEARCH ONLY</p><h2>Peer reports and prior research artifacts—not current approvals.</h2><p>This table includes focus-site peer files and research artifacts from earlier sessions. No new candidate was generated or evaluated in the current review. Historical HOLDOUT-DTI values are not organizer scores; no projection is written as a score.</p></div></div>
<div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table →</div><div class="table-scroll" tabindex="0" role="region" aria-label="Nine-site comparison"><table><thead><tr><th>Site</th><th>File to download</th><th>Labeled number</th><th>New organizer estimate</th><th>Unique?</th><th>Action</th></tr></thead><tbody>{ours}{conduit_row}
{rows_for(prefix)}</tbody></table></div></div></section>'''


NINE_SCORES = ROOT / 'registry/user_reported_scores_20261029.json'
NINE_LINEAGE = ROOT / 'evidence/site_lineage_verification_20261029.json'
def nine_site_section(prefix: str) -> str:
    """Render the nine-site evidence table without implying a score forecast.

    Scores are user-supplied reports, and the peer rasters are third-party
    research artifacts. The directional 3-pixel overlap is a geometry check,
    not a score, causal explanation, or organizer rule.
    """
    score_doc = json.loads(NINE_SCORES.read_text())
    scores = score_doc['entries']
    lineage = json.loads(NINE_LINEAGE.read_text())
    assets = {row['id']: row for row in json.loads((ROOT / 'registry/reference_assets.json').read_text())}
    if score_doc.get('status_label') != 'USER-REPORTED / UNVERIFIED':
        raise ValueError('focus-site score evidence lost its unverified label')

    # Highest directional share of each site's dots within 3 px of one peer.
    nearest_peer: dict[str, tuple[float, str]] = {site: (0.0, '') for site in SITES}
    for pair, measurement in lineage['pairwise_nine_sites'].items():
        a, b = pair.split('|')
        for site, peer, fraction in (
            (a, b, measurement['a_dots_within_3px_of_b_fraction']),
            (b, a, measurement['b_dots_within_3px_of_a_fraction']),
        ):
            if site in nearest_peer and fraction > nearest_peer[site][0]:
                nearest_peer[site] = (fraction, peer)

    rows = []
    for site in SITES:
        site_scores = [row for row in scores if row['site'] == site]
        if not site_scores or site not in assets:
            raise ValueError(f'missing focus-site score or pinned file: {site}')
        top = max(site_scores, key=lambda row: row['score'])
        asset = assets[site]
        filename = Path(asset['path']).name
        if top['file_name'] not in filename:
            raise ValueError(f'score and pinned asset do not identify the same file: {site}')
        overlap, peer = nearest_peer[site]
        peer_url = 'https://raw.githubusercontent.com/' + asset['repo'] + '/' + asset['ref'] + '/' + quote(asset['path'], safe='/')
        source_url = top['url']
        rows.append((top['score'], site, top, filename, peer_url, source_url, overlap, peer, len(site_scores)))

    rows.sort(key=lambda row: (-row[0], row[1]))
    body = []
    for rank, (score, site, top, filename, download_url, source_url, overlap, peer, count) in enumerate(rows, 1):
        duplicate_status = 'NO · INTERNAL STOP' if overlap > 0.70 else 'NOT ESTABLISHED'
        body.append(
            f'<tr><th scope="row">#{rank} · <a href="{prefix}docs/{esc(site)}.html">{esc(site)} ↗</a></th>'
            f'<td><a class="file-link wrap" href="{esc(download_url, quote=True)}">{esc(filename)}</a>'
            f'<span class="cell-sub">Pinned third-party mirror · research download only</span>'
            f'<span class="cell-sub"><a href="{esc(source_url, quote=True)}">Owner project page ↗</a></span></td>'
            f'<td><strong>{score:.4f}</strong><span class="cell-sub">USER-REPORTED / UNVERIFIED · {count} supplied file(s)</span></td>'
            f'<td><span class="pill pill-red">{duplicate_status}</span>'
            f'<span class="cell-sub">{overlap:.2%} of dots within 3 px of {esc(peer)}</span></td>'
            '<td><span class="pill pill-red">DO NOT SUBMIT</span>'
            '<span class="cell-sub">Research file only; no organizer receipt tied to this hash is in this checkout.</span></td></tr>'
        )

    worst_peer = min(value[0] for value in nearest_peer.values())
    return (
        '<section class="section nine-site-decision" id="nine-site-decision" aria-labelledby="nine-site-title">'
        '<div class="section-heading"><div>'
        '<p class="eyebrow"><span class="eyebrow-line"></span> CURRENT FEED · NINE FOCUS SITES · 29 OCT 2026</p>'
        '<h2 id="nine-site-title">Highest reported file, peer overlap, and download decision</h2>'
        '<p><strong>SUBMISSION STATUS: NO FILE APPROVED.</strong> The highest supplied report is GEMSDOE32 B2 at '
        '<strong>0.2778 USER-REPORTED / UNVERIFIED</strong>. The linked TIFFs are pinned third-party artifacts '
        'for research only. A download link is not permission to upload; no weekly slot was selected.</p></div></div>'
        '<div class="table-shell"><div class="table-scroll" tabindex="0" role="region" aria-label="Nine focus sites ranked by user-reported score">'
        '<table><thead><tr><th>Rank · peer site</th><th>Reported maximum · research download</th>'
        '<th>Evidence class</th><th>Peer uniqueness</th><th>Submit status</th></tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div></div>'
        '<p class="cell-sub">The scores were supplied by the user and are not linked here to organizer receipts. '
        'The 3-pixel figure is a directional dot-mask comparison among these nine pinned peer rasters; it is not a '
        'continuous-surface Spearman test. Every site exceeds the project’s internal 70% duplicate stop '
        f'(lowest maximum peer overlap: {worst_peer:.2%}); that threshold is not stated as an organizer rule. '
        'No candidate HOLDOUT-DTI, 95% CI, or score projection is available for this checkout.</p>'
        '</section>')


def home(depth=0):
    p = '../' * depth
    return f'''<div class="page-top"><span>GEMS PRIZE <span class="separator">/</span> DECISION BRIEF</span><span class="page-date">CURRENT FEED · 29 OCT 2026</span></div>
<section class="hero compact-hero"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-line"></span> EVIDENCE BEFORE A LEADERBOARD SLOT</p><h1>Find faults.<br><em>Protect every submission.</em></h1><p class="hero-description">A clear, auditable workspace for fault discovery in the Great Basin. We separate format checks, scientific evidence, uniqueness and actual portal acceptance.</p><div class="hero-actions"><a class="text-link" href="#comparison">Compare the nine sites ↓</a><a class="subtle-link" href="{p}docs/research.html">Explore the research ↗</a></div></div>
<div class="terrain-card terrain-small" aria-label="Illustrative contour artwork, not a prediction map"><div class="terrain-top"><span>GEO<span class="terrain-dot">●</span>DAWN</span><span>FIELD NOTE / 01</span></div><svg class="terrain-lines" viewBox="0 0 620 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.5"><path d="M-50 10C90 25 95 155 200 110S305-10 410 55s150 110 250 40"/><path d="M-50 35C80 50 100 180 205 135S310 15 410 80s150 110 250 40"/><path d="M-50 60C70 75 105 205 210 160S315 40 410 105s150 110 250 40"/><path d="M-50 85C60 100 110 230 215 185S320 65 410 130s150 110 250 40"/><path d="M-50 110C50 125 115 255 220 210S325 90 410 155s150 110 250 40"/><path d="M-50 135C40 150 120 280 225 235S330 115 410 180s150 110 250 40"/><path d="M-50 160C30 175 125 305 230 260S335 140 410 205s150 110 250 40"/></g><g class="terrain-focus" fill="none"><circle cx="379" cy="139" r="40"/><circle cx="379" cy="139" r="26"/><path d="M379 89v100M329 139h100"/></g></svg><div class="terrain-caption"><span><b>THE STUDY AREA</b><br>Western Great Basin</span><span>NEVADA + CALIFORNIA<br><b>CONCEPTUAL ONLY</b></span></div></div></section>
{nine_site_section(p)}{decision(p)}<section class="snapshot" aria-label="Current evidence snapshot"><div class="snapshot-item"><div class="snapshot-label">PUBLIC LEADERBOARD SNAPSHOT</div><div class="snapshot-value">0.4544</div><p>Organizer public page · fetched 29 Oct 2026 · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">check source ↗</a></p></div><div class="snapshot-item"><div class="snapshot-label">BEST FOCUS-SITE REPORT</div><div class="snapshot-value">0.2778</div><p>GEMSDOE32 · USER-REPORTED / UNVERIFIED</p></div><div class="snapshot-item"><div class="snapshot-label">METHOD LANE</div><div class="snapshot-value">None</div><p>Assignment not recorded · execution blocked</p></div><div class="snapshot-item"><div class="snapshot-label">CONTEST DATA</div><div class="snapshot-value">Login</div><p>Official data page redirects to sign-in</p></div></section>
{comparison(p)}<section class="section detail-grid"><div><p class="eyebrow"><span class="eyebrow-line"></span> THE B2 QUESTION</p><h2>What made the reported leader different?</h2></div><div class="prose-card"><p>On the audited mirrored grid, GEMSDOE32 B2 is exactly GEMSDOE25's d2.8 mask with 6,436 dots within two pixels of the mirrored known-fault catalogue removed; no new dots were added. GEMSDOE25 and GEMSDOE30 have the same positive-pixel mask.</p><p>Reducing redundant prediction mass <em>could</em> improve the distance-weighted Tversky tradeoff, but it can also remove true coverage. Hidden labels and an artifact-linked receipt are unavailable, so the cause and any improvement over the reported result remain unproven.</p><p>The GEMSDOE32 peer page labels 0.2778 an owner report and says no submission-page receipt links it to the raster hash. That peer-site statement is not organizer confirmation. Known fault pixels are masked, but nearby new faults may still matter; a catalogue buffer is not automatically a free scoring exclusion. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">DrivenData staff clarification ↗</a></p><a class="text-link" href="{p}docs/research.html#b2">Read the scientific analysis ↗</a></div></section>
<section class="next-strip"><div><p class="eyebrow">NEXT STEPS · NO EXPERIMENT YET</p><h2>Resolve assignment, data access, and template provenance first.</h2><p>Do not run a private fork, manufacture a TIFF, or spend a slot. Once the owner records a method lane and authorized canonical template and supplies permitted data, use the shared evaluator and writer; keep slot selection separate.</p></div><a class="button button-dark" href="{p}knowledge/session-review-arena-f40ee5b6.md">Read the review ↗</a></section>'''


def guide(depth=1):
    p = '../' * depth
    _, _, _, audit, _ = evidence()
    cand = audit['candidates']
    card = json.loads((DOCS / 'data/run-card.json').read_text())
    cards = [f'''<article class="audit-card"><p class="eyebrow">PRIOR PARALLEL-SESSION ARTIFACT · BB-STEP</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(card['submission_name'])}</code></p><p>SHA-256 <code class="wrap">{card['raster_sha256']}</code></p><p>17,766 dots. Unique vs nine focus sites (worst 3-px overlap 12.6%, |Spearman| 0.085). Lattice overlap 98.53% · literal duplicate. Inside footprint finite and in [0,1]; CRS/shape/transform match the mirrored sample. Zeros-outside and NaN-outside twins both written. Portal acceptance is untested.</p><p>Name <code>KARAGE1-BBSTEP-72312302675D</code> · note: <code>{esc(card['submission_note'])}</code></p><a class="text-link" href="{p}docs/downloads/{quote(card['submission_name'])}" download>Download for research only ↗</a></article>''']
    conduit_audit, conduit_original, latest, conduit_path = conduitcrest_evidence()
    clat = conduit_audit['lattice_witness']
    chdt = conduit_audit['previous_holdout_claim']
    cards.append(f'''<article class="audit-card"><p class="eyebrow">LATER MAINLINE ARTIFACT · CONDUITCREST</p><h3>DO NOT SUBMIT · LATTICE DUPLICATE</h3><p><strong>Research only; not a submission recommendation.</strong></p><p><code class="wrap">{esc(conduit_path.name)}</code></p><p>SHA-256 <code class="wrap">{conduit_audit['candidate']['sha256']}</code></p><p>{clat['candidate_dots']:,} dots; {clat['candidate_dots_within_closed_3px_disk']:,} ({clat['directed_overlap']:.4%}) within 3 px of the pinned lattice. This exceeds the literal 70% stop rule. It was unique only versus the nine focus-site files; its prior run card omitted the lattice and a pre-placement lattice check.</p><p>The prior card contains an incomplete HOLDOUT-DTI claim of {chdt['reported_value']:.6f} (evaluator {esc(chdt['evaluator_version'])}, {chdt['withheld_positives']:,} withheld positives); the 95% CI is missing and the result was not independently rerun here.</p><a class="text-link" href="{p}docs/downloads/{quote(conduit_path.name)}" download>Download for audit only ↗</a> · <a class="text-link" href="{p}evidence/conduitcrest_lattice_reaudit_20261028.json">Reaudit JSON ↗</a></article>''')
    for label, c in zip(('HMAS-SINTER', 'GPC-Z'), cand):
        row = c['comparisons'][0]
        cards.append(f'''<article class="audit-card"><p class="eyebrow">HISTORICAL ARTIFACT · {label}</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(c['file'])}</code></p><p>SHA-256 <code class="wrap">{c['sha256']}</code></p><p>{row['candidate_dots_within_3px']:,} / {row['candidate_dots']:,} dots within 3 px of lattice ({row['directed_overlap']:.2%}) · duplicate. Mirror-grid and inside [0,1] checks pass; null/NaN-outside check fails. Portal acceptance is untested.</p><a class="text-link" href="{p}docs/downloads/{quote(c['file'])}" download>Download for research only ↗</a></article>''')
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> EXECUTIVE SUMMARY</span><span class="page-date">REVIEWED 29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> THE SUBMISSION CHECKLIST</p><h1>One file. <em>Evidence first.</em></h1><p>What to submit, when—and why today's answer is no.</p></section>{decision(p)}
<section class="section" id="audit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> SAVED-BYTE CHECK</p><h2>The 9 local and 9 sibling/peer GeoTIFFs covered by the 1668dda0 receipt fail its gate; later candidates are audited separately below.</h2><p>Research downloads are explicitly not submission recommendations. Uniqueness versus the nine focus sites is not uniqueness versus the lattice or a complete fleet registry.</p></div></div><div class="audit-grid">{''.join(cards)}</div><p class="body-copy">In addition to the four cards above (and the <code>-nan.tif</code> twins for BB-STEP and GPC-Z plus the quarantined CDA1 <code>-zeros.tif</code>/<code>-nan.tif</code> pair), session <code>1668dda0</code> audited and retracted <code>karage1-unique-alteration-dots-20261028-zeros.tif</code> (SHA-256 <code>8bc4dae02a99da68…</code>): 2,113 of its 3,500 positive pixels lie outside the competition footprint (<code>outside_encoding_accepted = false</code>) and 99.8558% (1,385/1,387) of its inside-footprint positives lie within 3 px of the pinned lattice. Sibling <code>GEMSDOEkarage2</code> (99.86%), <code>GEMSDOEkarage3</code> (99.35%), and newly audited peer GeoTIFFs across <code>GEMSDOE91</code>, <code>KANLERGEMSDOE3</code>, <code>WBGGEMSDOE1</code>, <code>ApartGEMSDOE1/2</code>, and <code>GEMSDOESASS1</code> also overlap 99.35%–99.95% within 3 px of the lattice (<a href="{p}evidence/local_downloads_and_peer_audit_20261028.json">inspect full 18-raster receipt ↗</a>).</p><p class="body-copy">The historical K/Th + thermal candidate <code>unique-hyp-kth-therm-mask-20261028-zeros.tif</code> has been moved out of the public download directory. Its prior promotion claim is superseded. A pinned-mirror saved-byte audit records 99.9017% directed 3-px overlap with the lattice, exceeding the literal duplicate threshold; the former holdout claim is not reproduced. It remains quarantined for audit only; see <a href="{p}archive/quarantined-20261029/README-review-dc2e4c0c.md">archive note ↗</a> and <a href="{p}evidence/unique_hyp_kth_therm_mask_retraction_20261029.json">retraction receipt ↗</a>.</p><p class="body-copy">The official <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format">format description</a> says data outside the bounds should be null or NaN. A strict all-finite check and a null/NaN-outside check are different diagnostics; neither establishes actual portal acceptance. The rejected original file was not supplied, so the cause of its range error is unknown.</p></section>
{comparison(p)}<section class="section" id="steps"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> FOR A FUTURE CLEARED CANDIDATE</p><h2>How to submit, once eligible.</h2><p>These steps are not permission to upload either historical artifact.</p></div></div><div class="steps-grid"><article><span>01 / EVIDENCE</span><h3>Pass the automated gates</h3><p>Use the shared evaluator, fold-local features and per-feature canaries. Beat a frozen comparable holdout best; audit surface and dots against the complete registry; reopen the TIFF and validate saved bytes.</p></article><article><span>02 / SELECTOR</span><h3>Choose a slot separately</h3><p>Only an independent selector may choose an eligible candidate and check the current allowance on the authenticated submission page. The September rules say three submissions per week.</p></article><article><span>03 / DOWNLOAD</span><h3>Choose the exact file</h3><p>Download the approved single-band GeoTIFF (or a ZIP containing one GeoTIFF). Check its displayed SHA-256, unique name and note of at most 140 characters.</p></article><article><span>04 / UPLOAD</span><h3>Use the official form</h3><p>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData</a>, select Submit → Make new submission, choose the .tif or ZIP, and paste the note. Retain the file-linked organizer receipt.</p></article></div><div class="notice guide-notice"><span aria-hidden="true">ⓘ</span><p>The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> require disclosure of generative-AI use in the narrative when applicable. Public leaderboard performance is not the private final score.</p></div></section>'''


def research(depth=1):
    p = '../' * depth
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> RESEARCH</span><span class="page-date">SOURCE REVIEW · 29 OCT 2026</span></div>
<section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> GEOLOGY BEFORE SCORING</p><h1>Research slate.<br><em>No score forecasts.</em></h1><p>Four ranked, unexecuted geological hypotheses. Ranking is qualitative (expected scientific leverage relative to cost), not a predicted DTI gain, and none is assigned as the required method lane.</p></section>
<section class="notice"><span aria-hidden="true">ⓘ</span><p><strong>Execution blocked:</strong> the method lane and canonical-template assignment are absent, the competition data page redirects to login, required shared cache inputs are missing, and the vendored shared-tool audit fails two file hashes. No hypothesis was implemented or holdout-tested in this review. Do not use a private fork or spend a submission slot.</p></section>
<section class="section detail-grid" id="b2"><div><p class="eyebrow"><span class="eyebrow-line"></span> B2 · EVIDENCE-LIMITED EXPLANATION</p><h2>Why did the 0.2778 report change?</h2></div><div class="prose-card"><p>The 0.2778 value is <strong>USER-REPORTED / UNVERIFIED</strong>. The GEMSDOE32 peer page calls it an owner report and says no submission-page receipt links the score to the raster hash; that is a third-party statement, not organizer confirmation. The public leaderboard does not identify this report as a top-50 result.</p><p>On hash-pinned peer rasters, GEMSDOE25/30 have the same 44,090-dot mask. GEMSDOE32 B2 has 37,654 dots: the parent mask with 6,436 dots within 2 px of a mirrored catalogue removed, and no dots added. GEMSDOE36 keeps the B2 mask and adds 1,200 dots. This is a geometric lineage, not a controlled score ablation.</p><p>Under the official distance-weighted Tversky metric (α=0.2, β=0.8, R=300 m), removing near-catalogue predictions could reduce false-positive penalty, but could also remove hidden-fault coverage. The raster counts cannot determine which occurred. No causal explanation, comparative holdout score, or beatability estimate is supported.</p><a class="text-link" href="https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html">GEMSDOE32 peer page · inspect the owner-report caveat ↗</a> · <a class="text-link" href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric">Official metric ↗</a></div></section>
<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> PRE-IMPLEMENTATION SLATE · FOUR CANDIDATES</p><h2>Ranked research questions, not lane assignments.</h2><p>All four are proposals only. Each needs fold-local, pixel-exact visible-fault handling; whole buffered fault-segment holdout; pooled DTI with α=0.2, β=0.8 and a 300 m triangular kernel; per-feature leakage canaries; and the shared evaluator/writer. A feature-only AUC above 0.90 is a leakage stop. Budget: at most 3 experiments or 2 hours after all authorization gates pass.</p></div></div><div class="hypothesis-grid">
<article class="hypothesis-card"><span class="hypothesis-rank">01 <span>MEDIUM · QUALITATIVE TOP PRIORITY</span></span><h3>Cross-Potential Dip-Polarity Co-Gradient Step (CP-DPCS)</h3><p><b>Layers / signature:</b> RTP, total-field magnetic horizontal/vertical gradients, isostatic-gravity anomaly and gradients, plus low-slope conditioning. Compare signed magnetic phase with the gravity-gradient direction across multiple upward-continuation heights; target along-strike persistence of their joint relation beneath basin cover.</p><p><b>Mechanism:</b> a concealed normal-fault basement step can juxtapose magnetic basement and lower-density basin fill beneath subdued topography. This differs from an unsigned single-band ridge by testing a signed, scale-consistent paired field relation.</p><p><b>Named non-fault mimics:</b> plutonic/metasedimentary contacts, caldera margins, basalt-flow edges, buried channels and flight-line stitching/seams.</p><small><b>Readiness:</b> only in-stack feature names are proposed; the official contest rasters are login-gated and absent here. The hash-pinned mirror is not organizer-authenticated. No local coverage, fold test, leakage test or holdout result exists.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">02 <span>MEDIUM–HIGH · QUALITATIVE</span></span><h3>Biharmonic Elastic Relay-Bridge Stress-Transfer Corridor (BERB-STC)</h3><p><b>Layers / signature:</b> shear/dilatational strain and second invariant, earthquake/induced-earthquake density, conductivity and gravity gradients; use only visible fault-segment endpoints inside each training fold. Predict relay-ramp corridors and require independent geophysical contrast.</p><p><b>Mechanism:</b> interacting en-echelon fault tips may transfer deformation across relay ramps where individual surface traces fade. Unlike static endpoint cones, this tests fold-local tip-pair coupling and corroborating conductivity/gravity structure before placement.</p><p><b>Named non-fault mimics:</b> mining or geothermal induced seismicity, conductive playa brines, and interpolation bullseyes in coarse strain fields.</p><small><b>Readiness:</b> proposed input names are from the login-gated competition stack. No assigned lane, local feature stack, fold-local graph, or valid paired holdout is available. A related planning idea exists in earlier repository notes, so the concept is not novel within this repository.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">03 <span>MEDIUM–HIGH · EXTERNAL DATA</span></span><h3>Wavelet-Destriped Potassium-Residual Magnetics Trough (WD-KRMT)</h3><p><b>Layers / signature:</b> public GeoDAWN potassium, eTh, eU and magnetic grids plus acquisition block/flight-line metadata. Remove line/flight-level artifacts using blocked robust residualization, then test whether a narrow radiometric boundary coincides with a magnetite-destruction trough.</p><p><b>Mechanism:</b> hydrothermal alteration may produce a localized potassium residual and magnetic low where a surface scarp is absent. This differs from raw K/Th ratio or broad plume rules by controlling for flight lines and testing paired residual structure.</p><p><b>Named non-fault mimics:</b> potassic intrusive rocks, weathering/soil changes, volcanic units, playa evaporites and flight-height/leveling stripes.</p><small><b>Readiness:</b> official USGS GeoDAWN ScienceBase catalog lists downloadable GeoTIFF bundles (Area 1: 43.57 MB; Area 2: 230.54 MB) and documents CC0 rights. Catalog availability is verified; bytes were not fetched, footprint/projection were not checked, and overlap with existing features is unknown. <a href="https://doi.org/10.5066/P93LGLVQ">Official USGS DOI ↗</a></small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">04 <span>HIGH · EXTERNAL DATA / PROCESSING</span></span><h3>Cross-Fan Drainage-Incision Knickzone Alignment (CF-DIKA)</h3><p><b>Layers / signature:</b> a USGS 3DEP 1/3-arc-second DEM (~10 m), competition elevation/slope and gravity gradient. Test repeated channel-deflection and knickzone alignment across at least three adjacent catchments at a gravity step, conditioned on basin and drainage area.</p><p><b>Mechanism:</b> degraded or low-relief fault throw may perturb several neighboring catchments even where no single scarp is clear. This differs from pixel-level scarp scoring by requiring replicated drainage geometry and independent subsurface corroboration.</p><p><b>Named non-fault mimics:</b> Lake Lahontan shoreline benches, fan avulsion, stream piracy, lithologic ledges and resistant caprock.</p><small><b>Readiness:</b> USGS describes seamless 1/3-arc-second coverage across the conterminous U.S. and products without use restrictions; 1 m products have limited/expanding coverage. A specific tile, local grid alignment, resampling plan and useful resolution have not been checked. <a href="https://www.usgs.gov/3d-elevation-program/about-3dep-products-services">Official 3DEP product page ↗</a></small></article></div>
<p class="body-copy">The ordering is a qualitative work queue only—not an expected score ranking. GeoDAWN/3DEP source records establish catalog-level availability, not local scientific suitability. No candidate was promoted, no TIFF was produced, and slot selection remains separate.</p></section>
<section class="section" id="sources"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> TRUSTED SOURCES · MANUAL REVIEW</p><h2>Primary references and what was checked.</h2><p>Source register records the verified text, access restrictions, and the limits of each check.</p></div></div><div class="source-list"><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"><span><b>DrivenData · problem, metric and format</b><small>Fault target, feature description, DTI and GeoTIFF requirements</small></span><span>OFFICIAL ↗</span></a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/"><span><b>DrivenData · competition data</b><small>Redirects to login in this review; bytes not inspected</small></span><span>LOGIN ↗</span></a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"><span><b>DrivenData · public leaderboard</b><small>Snapshot fetched 29 Oct 2026; not private/final results</small></span><span>OFFICIAL ↗</span></a><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf"><span><b>DOE / NLR · official prize rules</b><small>Submission limits, originality, phase process and AI disclosure</small></span><span>OFFICIAL ↗</span></a><a href="https://doi.org/10.5066/P93LGLVQ"><span><b>USGS · GeoDAWN ScienceBase release</b><small>Airborne magnetic/radiometric grids; downloadable GeoTIFF bundles listed; CC0 noted by USGS</small></span><span>OFFICIAL ↗</span></a><a href="https://www.usgs.gov/3d-elevation-program/about-3dep-products-services"><span><b>USGS · 3DEP products and services</b><small>Coverage and resolution differ by product; exact tile not acquired</small></span><span>OFFICIAL ↗</span></a><a href="{p}knowledge/official-sources-verified-2026-10-29.md"><span><b>Line-by-line source register</b><small>Evidence, access, and limitations · updated 29 Oct</small></span><span>REVIEW ↗</span></a><a href="{p}knowledge/session-review-arena-f40ee5b6.md"><span><b>Current three-pass repository review</b><small>Findings, blockers, and next-step gates</small></span><span>REVIEW ↗</span></a></div></section>'''


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
    pair = max((v['overlap_fraction'], k.split('->')[1]) for k,v in ref['directed_pairs'].items() if k.startswith(name + '->'))
    secondary = [r for r in secondary_evidence()['rows'] if r['site'] == name]
    secondary_section = ''
    if secondary:
        items = ''.join(
            f'<li><a class="wrap" href="{esc(artifact_url(r), quote=True)}">{esc(r["matched_file"])} ↗</a>'
            f' · SHA-256 <code>{esc(r["sha256"][:16])}…</code>'
            f' · <strong>{r["user_reported_score"]:.4f} USER-REPORTED · UNVERIFIED</strong>'
            f' · {r["positive_pixels_in_footprint"]:,} dots'
            f' · {r["lattice_directed_overlap"]:.2%} within 3 px of lattice'
            ' · <strong>DO NOT RESUBMIT</strong></li>'
            for r in secondary
        )
        secondary_section = (
            f'<section class="section detail-grid"><div><p class="eyebrow">ADDITIONAL AUDITED FILES</p>'
            f'<h2>Secondary historical runs.</h2></div><div class="prose-card">'
            f'<p>Additional prompt-listed files from {esc(name)} audited against the pinned lattice:</p>'
            f'<ul>{items}</ul>'
            f'<a class="text-link" href="../evidence/nine_sites_secondary_audit_20261028.json">Inspect secondary 9-site audit JSON ↗</a></div></section>'
        )
    return f'''<div class="page-top"><span>NINE-SITE REVIEW <span class="separator">/</span> {name}</span><span class="page-date">29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SITE EXECUTIVE SUMMARY</p><h1>{name}. <em>Research only.</em></h1><p>The reported historical leader is not a newly eligible submission.</p></section>{decision('../')}
<section class="section detail-grid"><div><p class="eyebrow">HISTORICAL FILE</p><h2>What the evidence says.</h2></div><div class="prose-card"><p><a class="wrap" href="{esc(artifact_url(entry), quote=True)}">{esc(Path(entry['path']).name)} ↗</a><br>SHA-256 <code class="wrap">{entry['sha256']}</code></p><p><strong>{claim['reported_score']:.4f} USER-REPORTED · UNVERIFIED.</strong> No artifact-linked organizer submission receipt is available. A new leaderboard estimate is unavailable.</p><p>The file has {row['positive_pixels']:,} positive pixels; {row['lattice_directed_overlap']:.2%} fall within 3 pixels of the registered lattice. It also overlaps {pair[0]:.2%} with {pair[1]} in the directional nine-file audit. Both exceed the literal 70% threshold. <strong>DO NOT RESUBMIT.</strong></p><p>These are geometric measurements, not proof of equal geologic predictions or a forecast. Scope is historical focus-site rasters plus the lattice; complete current-registry uniqueness was not checked.</p><a class="text-link" href="data/reference-audit.json">Review the measured audit ↗</a></div></section>{secondary_section}<section class="next-strip"><div><p class="eyebrow">BACK TO THE DECISION</p><h2>No new file is cleared.</h2><p>Check the current gates and submission guide before considering any upload.</p></div><a class="button button-dark" href="executive-summary.html">Executive summary ↗</a></section>'''


def main():
    # One builder owns all public decision/guide pages so an old lane-specific
    # generator cannot silently restore a false green badge.
    evidence()
    secondary_evidence()
    local_and_peer_evidence()
    pages = {
        ROOT / 'index.html': shell('Submission overview', home(0), 0),
        ROOT / 'legacy-overview.html': shell('Submission overview', home(0), 0),
        ROOT / 'executive-summary.html': shell('Submission guide', nine_site_section('') + guide(0), 0, 'Executive summary'),
        DOCS / 'index.html': shell('Submission overview', home(1), 1),
        DOCS / 'executive-summary.html': shell('Executive summary', nine_site_section('../') + guide(1), 1, 'Executive summary'),
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
