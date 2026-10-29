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


def official_leaderboard():
    """Validate the public-only snapshot consumed by all decision pages."""
    path = DOCS / 'data/official-leaderboard.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    rows = data.get('rows')
    if (data.get('schema') != 'gems-official-public-leaderboard-v1'
            or data.get('competition_id') != 306
            or not str(data.get('source_url', '')).startswith('https://www.drivendata.org/competitions/306/')
            or not isinstance(rows, list) or not rows
            or 'not a file-linked' not in data.get('scope', '').lower()):
        raise ValueError('official public leaderboard snapshot is incomplete or mislabeled')
    seen = set()
    for row in rows:
        rank, score = row.get('rank'), row.get('best_public_dw_tversky')
        if (type(rank) is not int or rank < 1 or rank in seen
                or type(score) not in (int, float) or not math.isfinite(score)
                or not 0 <= score <= 1):
            raise ValueError('invalid rank/score in official public leaderboard snapshot')
        seen.add(rank)
    if 1 not in seen:
        raise ValueError('official public leaderboard snapshot does not include rank 1')
    return data, sorted(rows, key=lambda row: row['rank'])


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


def prior_mainline_candidate_evidence():
    """Validate the later GSE/HALO research records without treating either as cleared."""
    audit = json.loads((ROOT / 'evidence/local_downloads_audit_20261029.json').read_text())
    gse = json.loads((ROOT / 'evidence/run_card_gse_exp1.json').read_text())
    halo = json.loads((ROOT / 'evidence/run_card_karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.json').read_text())
    gse_rows = [row for row in audit.get('local_downloads', [])
                if 'karage1-gse-geothermal-surface-24000dots-' in row.get('file', '')
                and row.get('file', '').endswith('-zeros.tif')]
    if len(gse_rows) != 1:
        raise ValueError('GSE saved-byte audit row is missing or ambiguous')
    gse_row = gse_rows[0]
    gse_path = ROOT / gse_row['file']
    halo_path = ROOT / 'docs/downloads/karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.tif'
    gse_holdout = gse.get('holdout_dti', {})
    halo_holdout = halo.get('holdout_dti', {})
    halo_registry = halo.get('correlation_overlap_vs_registry', {})
    if (gse_row.get('ok_to_submit') is not False
            or gse_row.get('literal_lattice_duplicate') is not True
            or gse_row.get('lattice_directed_overlap_3px', 0) <= .70
            or hashlib.sha256(gse_path.read_bytes()).hexdigest() != gse_row.get('sha256')
            or gse.get('raster', {}).get('sha256') != gse_row.get('sha256')
            or gse.get('ok_to_submit') is not False
            or gse.get('slot_selected_or_spent') is not False
            or gse_holdout.get('value') is not None):
        raise ValueError('GSE audit/run-card/bytes do not agree on the blocked status')
    if (not halo_path.is_file()
            or hashlib.sha256(halo_path.read_bytes()).hexdigest() != halo.get('raster_sha256')
            or halo.get('ok_to_submit') is not False
            or halo.get('slot_selected_or_spent') is not False
            or halo_holdout.get('value') is not None
            or halo_registry.get('preplacement_surface_spearman') is not None
            or halo_registry.get('final_dot_overlap') is not None):
        raise ValueError('HALO run-card/bytes do not agree on the unverified status')
    return gse_row, gse, halo


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
<main id="main"><div class="container">{body}</div></main><footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div><div class="footer-links"><a href="{p}evidence/session_09bbfea3_run_card.json">Current session card</a><a href="{doc}research.html">Research</a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition ↗</a></div><div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with the organizers.</span></div></div></footer></body></html>'''


def decision(prefix: str):
    _, _, _, audit, card = evidence()
    a, b = audit['candidates']
    ar, br = a['comparisons'][0], b['comparisons'][0]
    dti = card['holdout_dti']
    lat = card['correlation_overlap_vs_registry']['lattice_overlap']
    nine = card['correlation_overlap_vs_registry']['final_dot_overlap_worst_nine']['frac_our_dots_within_3px']
    conduit_audit, conduit_original, latest, conduit_path = conduitcrest_evidence()
    clat = conduit_audit['lattice_witness']
    chdt = conduit_audit['previous_holdout_claim']
    gse_row, gse_card, halo_card = prior_mainline_candidate_evidence()
    return f'''<section class="decision-panel" aria-labelledby="decision-title"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT SUBMISSION DECISION <span class="status-tag">DO NOT SUBMIT</span></div>
<h2 id="decision-title">No eligible submission file yet. Multiple audited rasters fail the literal lattice gate.</h2><p><strong>not cleared for upload.</strong> No approved .tif to download.</p>
<p>The prior BB-STEP file <code class="wrap">{esc(card['submission_name'])}</code> is unique versus the nine focus sites (worst overlap {nine:.1%}) but has {lat:.2%} lattice overlap; it is a duplicate. Its prior-session <strong>HOLDOUT-DTI {dti['value']:.5f}</strong> [{dti['ci95'][0]:.5f}, {dti['ci95'][1]:.5f}] used evaluator {esc(dti['evaluator_version'])} with {dti['withheld_positives']:,} withheld positives. This is not an organizer score and does not override the duplicate stop.</p>
<p>The newer Conduitcrest research file has {clat['candidate_dots']:,} dots; {clat['candidate_dots_within_closed_3px_disk']:,} ({clat['directed_overlap']:.4%}) are within 3 px of the pinned lattice, exceeding the 70% threshold. Its prior run card's incomplete <strong>HOLDOUT-DTI {chdt['reported_value']:.6f}</strong> claim names evaluator {esc(chdt['evaluator_version'])} and {chdt['withheld_positives']:,} withheld positives but provides <strong>no 95% CI</strong>; it is not a release-grade result.</p>
<p>Original Conduitcrest uniqueness compared only the nine focus-site rasters, not the lattice or complete fleet. Its pre-placement lattice comparison and per-feature canary are absent. Both candidates are research/audit files only; neither is cleared for upload.</p>
<p>Historical HMAS / GPC-Z files also remain blocked ({ar['directed_overlap']:.2%} and {br['directed_overlap']:.2%} vs lattice).</p>
<p><strong>Prior mainline GSE / HALO artifacts:</strong> The GSE file's earlier uniqueness result excluded the lattice; the later audit finds {gse_row['lattice_directed_overlap_3px']:.4%} of its dots within 3 px, so it fails the literal gate. The HALO artifact has no measured registry comparison or HOLDOUT-DTI. Both are historical research files, not products of this review, and neither is cleared. Audit-only files: <a href="{prefix}docs/downloads/{quote(gse_card['submission_name'])}">GSE GeoTIFF</a> · <a href="{prefix}docs/downloads/{quote(halo_card['submission_name'])}">HALO GeoTIFF</a> · <a href="{prefix}evidence/local_downloads_audit_20261029.json">GSE/lattice audit ↗</a> · <a href="{prefix}evidence/run_card_karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.json">HALO run card ↗</a>. These links are not submission authorization.</p>
<p><strong>Current review · session 09bbfea3 (29 Oct 2026):</strong> Baseline suite before this review: 365 passed; after mainline integration and fixes: 387 passed (119 warnings). The official/shared-tool preflight still fails: no assigned lane or canonical template, two vendored file pins mismatch, and organizer inputs/cache are absent from this checkout. A prior mainline receipt records mirror restoration, but the recorded mirror bytes are not currently available here and are not organizer-authenticated. The legacy preparation entry point printed BLOCKED but continued and created a temporary cache before failing; it is now quarantined and has a no-write regression test. No experiment, new raster, holdout estimate, or slot selection occurred. <a href="{prefix}knowledge/session-review-arena-09bbfea3.md">Read the current review and three-hypothesis slate ↗</a> · <a href="{prefix}evidence/session_09bbfea3_run_card.json">Current session run card ↗</a></p>
<p><strong>Prior forensic audit · session 1668dda0:</strong> Its nine-local/nine-peer saved-byte checks and historical candidate retractions remain available as prior evidence, not this session's work. <a href="{prefix}knowledge/session-review-arena-1668dda0.md">Read the prior audit ↗</a> · <a href="{prefix}evidence/local_downloads_and_peer_audit_20261028.json">Saved-byte audit JSON ↗</a></p>
<div class="decision-actions"><button class="button button-disabled" disabled>No approved .tif to download</button>
<a class="button button-light" href="{prefix}docs/executive-summary.html#audit">Review research-only downloads ↗</a>
<a class="button button-light" href="{prefix}evidence/conduitcrest_lattice_reaudit_20261028.json">Inspect latest lattice audit ↗</a>
<a class="button button-light" href="{prefix}evidence/bbstep_uniqueness.json">Inspect BB-STEP uniqueness ↗</a></div>
<p class="download-help">Conduitcrest research file (research only): <a href="{prefix}docs/downloads/{quote(conduit_path.name)}">{esc(conduit_path.name)}</a> · SHA-256 <code>{conduit_audit['candidate']['sha256']}</code>. Download is for audit only, not submission. No weekly slot was selected or spent.</p></div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative · lattice duplicates</strong></div><div><span>LEADERBOARD ESTIMATE</span><strong>Unavailable</strong></div><div><span>BB-STEP LATTICE</span><strong>{lat:.2%} · duplicate</strong></div><div><span>CONDUITCREST LATTICE</span><strong>{clat['directed_overlap']:.2%} · duplicate</strong></div><a href="{prefix}evidence/session_09bbfea3_run_card.json">Current session card ↗</a></div></section>'''


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
        '<span class="cell-sub">Prior-session artifact · research only</span></td>'
        f'<td><strong>{dti["value"]:.4f}</strong><span class="cell-sub">HOLDOUT-DTI · {esc(dti["evaluator_version"])} · n={dti["withheld_positives"]:,} · 95% CI [{dti["ci95"][0]:.4f}, {dti["ci95"][1]:.4f}]</span></td>'
        '<td>Unavailable<span class="cell-sub">No organizer forecast</span></td>'
        f'<td><span class="pill pill-red">NO vs lattice</span><span class="cell-sub">Yes vs 9 sites ({nine:.1%}); lattice {lat:.1%}</span></td>'
        '<td><span class="pill pill-red">DO NOT SUBMIT</span></td></tr>'
    )
    return f'''<section class="section comparison" id="comparison"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> DOWNLOAD TABLE</p><h2>Which file, which number, unique or not.</h2><p>Only HOLDOUT-DTI or USER-REPORTED / UNVERIFIED numbers appear. No projection is written as a score. The generated BB-STEP file is unique versus the nine listed GEMSDOE sites and is still a lattice duplicate under the parallel-run rule.</p></div></div>
<div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table →</div><div class="table-scroll" tabindex="0" role="region" aria-label="Nine-site comparison"><table><thead><tr><th>Site</th><th>File to download</th><th>Labeled number</th><th>New organizer estimate</th><th>Unique?</th><th>Action</th></tr></thead><tbody>{ours}{conduit_row}
{rows_for(prefix)}</tbody></table></div></div></section>'''


def home(depth=0):
    p = '../' * depth
    leaderboard, leaderboard_rows = official_leaderboard()
    leader = next(row for row in leaderboard_rows if row['rank'] == 1)
    rank_47 = next((row for row in leaderboard_rows if row['rank'] == 47), None)
    observed = leaderboard.get('retrieved_at_utc') or leaderboard.get('observed_on_utc')
    observed_day = str(observed)[:10]
    board_note = (f"#47 {rank_47['best_public_dw_tversky']:.4f} in this dated snapshot"
                  if rank_47 else "lower ranks not included in this snapshot")
    snapshot_note = ("exact page-capture time unavailable; partial official-page snapshot"
                     if leaderboard.get('partial_snapshot') else f"feed refreshed {observed}")
    return f'''<div class="page-top"><span>GEMS PRIZE <span class="separator">/</span> DECISION BRIEF</span><span class="page-date">INDEPENDENT AUDIT · {esc(observed_day)}</span></div>
<section class="hero compact-hero"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-line"></span> EVIDENCE BEFORE A LEADERBOARD SLOT</p><h1>Find faults.<br><em>Protect every submission.</em></h1><p class="hero-description">A clear, auditable workspace for fault discovery in the Great Basin. We separate format checks, scientific evidence, uniqueness and actual portal acceptance.</p><div class="hero-actions"><a class="text-link" href="#comparison">Compare the nine sites ↓</a><a class="subtle-link" href="{p}docs/research.html">Explore the research ↗</a></div></div>
<div class="terrain-card terrain-small" aria-label="Illustrative contour artwork, not a prediction map"><div class="terrain-top"><span>GEO<span class="terrain-dot">●</span>DAWN</span><span>FIELD NOTE / 01</span></div><svg class="terrain-lines" viewBox="0 0 620 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.5"><path d="M-50 10C90 25 95 155 200 110S305-10 410 55s150 110 250 40"/><path d="M-50 35C80 50 100 180 205 135S310 15 410 80s150 110 250 40"/><path d="M-50 60C70 75 105 205 210 160S315 40 410 105s150 110 250 40"/><path d="M-50 85C60 100 110 230 215 185S320 65 410 130s150 110 250 40"/><path d="M-50 110C50 125 115 255 220 210S325 90 410 155s150 110 250 40"/><path d="M-50 135C40 150 120 280 225 235S330 115 410 180s150 110 250 40"/><path d="M-50 160C30 175 125 305 230 260S335 140 410 205s150 110 250 40"/></g><g class="terrain-focus" fill="none"><circle cx="379" cy="139" r="40"/><circle cx="379" cy="139" r="26"/><path d="M379 89v100M329 139h100"/></g></svg><div class="terrain-caption"><span><b>THE STUDY AREA</b><br>Western Great Basin</span><span>NEVADA + CALIFORNIA<br><b>CONCEPTUAL ONLY</b></span></div></div></section>
{decision(p)}<section class="snapshot" aria-label="Evidence snapshot"><div class="snapshot-item"><div class="snapshot-label">OFFICIAL PUBLIC LEADERBOARD #1</div><div class="snapshot-value">{leader['best_public_dw_tversky']:.4f}</div><p>{esc(leader.get('participant', 'Participant'))} · observed {esc(observed_day)} · {esc(board_note)} · {esc(snapshot_note)} · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">open live board ↗</a><br>Not a file-linked submission receipt or project score.</p></div><div class="snapshot-item"><div class="snapshot-label">BEST SUPPLIED NINE-SITE REPORT</div><div class="snapshot-value">0.2778</div><p>GEMSDOE32 · USER-REPORTED, not confirmed</p></div><div class="snapshot-item"><div class="snapshot-label">PRIOR BB-STEP SESSION</div><div class="snapshot-value">3 <span class="snapshot-context">experiments</span></div><p>Separate parallel run · lattice stop applied</p></div><div class="snapshot-item"><div class="snapshot-label">INPUT RESTORATION</div><div class="snapshot-value">31 <span class="snapshot-context">files</span></div><p>Hash-pinned mirrors · not organizer-authenticated</p></div></section>
{comparison(p)}<section class="section detail-grid"><div><p class="eyebrow"><span class="eyebrow-line"></span> THE B2 QUESTION</p><h2>What made the reported leader different?</h2></div><div class="prose-card"><p>On the audited mirrored grid, GEMSDOE32 B2 is exactly GEMSDOE25's d2.8 mask with 6,436 dots within two pixels of the mirrored known-fault catalogue removed; no new dots were added. GEMSDOE25 and GEMSDOE30 have the same positive-pixel mask.</p><p>Reducing redundant prediction mass <em>could</em> improve the distance-weighted Tversky tradeoff, but it can also remove true coverage. Hidden labels and an artifact-linked receipt are unavailable, so the cause and any improvement over the reported result remain unproven.</p><p>Known fault pixels are masked, but nearby new faults may still matter. A catalogue buffer is not automatically a free scoring exclusion. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">DrivenData staff clarification ↗</a></p><a class="text-link" href="{p}docs/research.html#b2">Read the scientific analysis ↗</a></div></section>
<section class="next-strip"><div><p class="eyebrow">NEXT STEPS</p><h2>Obtain the assigned lane and authorized inputs first.</h2><p>Keep the literal registry/lattice stop in force. BB-STEP is distinct from the nine listed sites but still a lattice duplicate. Do not jitter, rename, or re-encode dots to evade the rule. No automatic DrivenData scraping or upload.</p></div><a class="button button-dark" href="{p}docs/executive-summary.html">See the checklist ↗</a></section>'''


def guide(depth=1):
    p = '../' * depth
    _, _, _, audit, _ = evidence()
    cand = audit['candidates']
    card = json.loads((DOCS / 'data/run-card.json').read_text())
    cards = [f'''<article class="audit-card"><p class="eyebrow">PRIOR PARALLEL-SESSION ARTIFACT · BB-STEP</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(card['submission_name'])}</code></p><p>SHA-256 <code class="wrap">{card['raster_sha256']}</code></p><p>17,766 dots. Unique vs nine focus sites (worst 3-px overlap 12.6%, |Spearman| 0.085). Lattice overlap 98.53% · literal duplicate. Inside footprint finite and in [0,1]; CRS/shape/transform match the mirrored sample. Zeros-outside and NaN-outside twins both written. Portal acceptance is untested.</p><p>Name <code>KARAGE1-BBSTEP-72312302675D</code> · note: <code>{esc(card['submission_note'])}</code></p><a class="text-link" href="{p}docs/downloads/{quote(card['submission_name'])}" download>Download for research only ↗</a></article>''']
    conduit_audit, conduit_original, latest, conduit_path = conduitcrest_evidence()
    clat = conduit_audit['lattice_witness']
    chdt = conduit_audit['previous_holdout_claim']
    gse_row, gse_card, halo_card = prior_mainline_candidate_evidence()
    cards.append(f'''<article class="audit-card"><p class="eyebrow">LATER MAINLINE ARTIFACT · CONDUITCREST</p><h3>DO NOT SUBMIT · LATTICE DUPLICATE</h3><p><strong>Research only; not a submission recommendation.</strong></p><p><code class="wrap">{esc(conduit_path.name)}</code></p><p>SHA-256 <code class="wrap">{conduit_audit['candidate']['sha256']}</code></p><p>{clat['candidate_dots']:,} dots; {clat['candidate_dots_within_closed_3px_disk']:,} ({clat['directed_overlap']:.4%}) within 3 px of the pinned lattice. This exceeds the literal 70% stop rule. It was unique only versus the nine focus-site files; its prior run card omitted the lattice and a pre-placement lattice check.</p><p>The prior card contains an incomplete HOLDOUT-DTI claim of {chdt['reported_value']:.6f} (evaluator {esc(chdt['evaluator_version'])}, {chdt['withheld_positives']:,} withheld positives); the 95% CI is missing and the result was not independently rerun here.</p><a class="text-link" href="{p}docs/downloads/{quote(conduit_path.name)}" download>Download for audit only ↗</a> · <a class="text-link" href="{p}evidence/conduitcrest_lattice_reaudit_20261028.json">Reaudit JSON ↗</a></article>''')
    cards.append(f'''<article class="audit-card"><p class="eyebrow">PRIOR MAINLINE ARTIFACT · GSE</p><h3>DO NOT SUBMIT · LATTICE DUPLICATE</h3><p><strong>Research only; not cleared for upload.</strong></p><p><code class="wrap">{esc(gse_card['submission_name'])}</code></p><p>SHA-256 <code class="wrap">{gse_row['sha256']}</code></p><p>{gse_row['positive_pixels_in_footprint']:,} dots; {gse_row['lattice_dots_within_3px']:,} ({gse_row['lattice_directed_overlap_3px']:.4%}) within 3 px of the pinned lattice. The earlier uniqueness claim excluded this witness and is superseded. The run card records no HOLDOUT-DTI and no slot selection.</p><a class="text-link" href="{p}docs/downloads/{quote(gse_card['submission_name'])}" download>Download for audit only ↗</a> · <a class="text-link" href="{p}evidence/local_downloads_audit_20261029.json">Saved-byte audit ↗</a> · <a class="text-link" href="{p}evidence/run_card_gse_exp1.json">Run card ↗</a></article>''')
    cards.append(f'''<article class="audit-card"><p class="eyebrow">PRIOR MAINLINE ARTIFACT · HALO</p><h3>DO NOT SUBMIT · REGISTRY AND HOLDOUT NOT MEASURED</h3><p><strong>Research only; not cleared for upload.</strong></p><p><code class="wrap">{esc(halo_card['submission_name'])}</code></p><p>SHA-256 <code class="wrap">{halo_card['raster_sha256']}</code></p><p>The prior card reports local format checks, but `preplacement_surface_spearman` and `final_dot_overlap` are null; no HOLDOUT-DTI or 95% CI exists. A continuous field's structural difference from dot masks is not a uniqueness test. No assigned lane; no clearance.</p><a class="text-link" href="{p}docs/downloads/{quote(halo_card['submission_name'])}" download>Download for audit only ↗</a> · <a class="text-link" href="{p}evidence/run_card_karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.json">Run card ↗</a></article>''')
    for label, c in zip(('HMAS-SINTER', 'GPC-Z'), cand):
        row = c['comparisons'][0]
        cards.append(f'''<article class="audit-card"><p class="eyebrow">HISTORICAL ARTIFACT · {label}</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(c['file'])}</code></p><p>SHA-256 <code class="wrap">{c['sha256']}</code></p><p>{row['candidate_dots_within_3px']:,} / {row['candidate_dots']:,} dots within 3 px of lattice ({row['directed_overlap']:.2%}) · duplicate. Mirror-grid and inside [0,1] checks pass; null/NaN-outside check fails. Portal acceptance is untested.</p><a class="text-link" href="{p}docs/downloads/{quote(c['file'])}" download>Download for research only ↗</a></article>''')
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> EXECUTIVE SUMMARY</span><span class="page-date">REVIEWED 29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> THE SUBMISSION CHECKLIST</p><h1>One file. <em>Evidence first.</em></h1><p>What to submit, when—and why today's answer is no.</p></section>{decision(p)}
<section class="section" id="audit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> SAVED-BYTE CHECK</p><h2>The 9 local and 9 sibling/peer GeoTIFFs covered by the 1668dda0 receipt fail its gate; later candidates are audited separately below.</h2><p>Research downloads are explicitly not submission recommendations. Uniqueness versus the nine focus sites is not uniqueness versus the lattice or a complete fleet registry.</p></div></div><div class="audit-grid">{''.join(cards)}</div><p class="body-copy">In addition to the research cards above (and the <code>-nan.tif</code> twins for BB-STEP and GPC-Z plus the quarantined CDA1 <code>-zeros.tif</code>/<code>-nan.tif</code> pair), session <code>1668dda0</code> audited and retracted <code>karage1-unique-alteration-dots-20261028-zeros.tif</code> (SHA-256 <code>8bc4dae02a99da68…</code>): 2,113 of its 3,500 positive pixels lie outside the competition footprint (<code>outside_encoding_accepted = false</code>) and 99.8558% (1,385/1,387) of its inside-footprint positives lie within 3 px of the pinned lattice. Sibling <code>GEMSDOEkarage2</code> (99.86%), <code>GEMSDOEkarage3</code> (99.35%), and newly audited peer GeoTIFFs across <code>GEMSDOE91</code>, <code>KANLERGEMSDOE3</code>, <code>WBGGEMSDOE1</code>, <code>ApartGEMSDOE1/2</code>, and <code>GEMSDOESASS1</code> also overlap 99.35%–99.95% within 3 px of the lattice (<a href="{p}evidence/local_downloads_and_peer_audit_20261028.json">inspect full 18-raster receipt ↗</a>).</p><p class="body-copy">The historical K/Th + thermal candidate <code>unique-hyp-kth-therm-mask-20261028-zeros.tif</code> has been moved out of the public download directory. Its prior promotion claim is superseded. A pinned-mirror saved-byte audit records 99.9017% directed 3-px overlap with the lattice, exceeding the literal duplicate threshold; the former holdout claim is not reproduced. It remains quarantined for audit only; see <a href="{p}archive/quarantined-20261029/README-review-dc2e4c0c.md">archive note ↗</a> and <a href="{p}evidence/unique_hyp_kth_therm_mask_retraction_20261029.json">retraction receipt ↗</a>.</p><p class="body-copy">The official <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format">format description</a> says data outside the bounds should be null or NaN. A strict all-finite check and a null/NaN-outside check are different diagnostics; neither establishes actual portal acceptance. The rejected original file was not supplied, so the cause of its range error is unknown.</p></section>
{comparison(p)}<section class="section" id="steps"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> FOR A FUTURE CLEARED CANDIDATE</p><h2>How to submit, once eligible.</h2><p>These steps are not permission to upload either historical artifact.</p></div></div><div class="steps-grid"><article><span>01 / EVIDENCE</span><h3>Pass the automated gates</h3><p>Use the shared evaluator, fold-local features and per-feature canaries. Beat a frozen comparable holdout best; audit surface and dots against the complete registry; reopen the TIFF and validate saved bytes.</p></article><article><span>02 / SELECTOR</span><h3>Choose a slot separately</h3><p>Only an independent selector may choose an eligible candidate and check the current allowance on the authenticated submission page. The September rules say three submissions per week.</p></article><article><span>03 / DOWNLOAD</span><h3>Choose the exact file</h3><p>Download the approved single-band GeoTIFF (or a ZIP containing one GeoTIFF). Check its displayed SHA-256, unique name and note of at most 140 characters.</p></article><article><span>04 / UPLOAD</span><h3>Use the official form</h3><p>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData</a>, select Submit → Make new submission, choose the .tif or ZIP, and paste the note. Retain the file-linked organizer receipt.</p></article></div><div class="notice guide-notice"><span aria-hidden="true">ⓘ</span><p>The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> require disclosure of generative-AI use in the narrative when applicable. Public leaderboard performance is not the private final score.</p></div></section>'''


def research(depth=1):
    p = '../' * depth
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> RESEARCH</span><span class="page-date">REVIEWED 29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SCIENCE BEFORE SCORING</p><h1>Understand the ground.<br><em>Respect the unknown.</em></h1><p>The target is previously unmapped geological faults, not direct proof of a geothermal vent.</p></section>
<section class="notice"><span aria-hidden="true">ⓘ</span><p><strong>Current status: proposals only.</strong> The assigned method paragraph is absent; shared-template provenance fails; organizer inputs are unavailable. No geological experiment was run in this session. These hypotheses are not an assignment, a score estimate, or a claim of fleet-wide novelty.</p></section>
<section class="section detail-grid" id="b2"><div><p class="eyebrow"><span class="eyebrow-line"></span> WHAT THE BYTES SHOW</p><h2>Why B2 may have worked.</h2></div><div class="prose-card"><p>Cross-site binary-mask algebra on pinned peer mirrors shows that GEMSDOE32 B2 is a reduced version of a GEMSDOE25/GEMSDOE30 parent mask. The reported 0.2778 remains USER-REPORTED / UNVERIFIED; no artifact-linked organizer receipt is available.</p><p>Under the official distance-weighted Tversky metric, reducing redundant prediction mass could reduce false-positive penalty, but deleting true coverage can lower recall. The available mask comparison does not establish which effect caused the reported value or whether it can be beaten.</p><p>See the <a href="{p}knowledge/02_why_gemsdoe32_b2_scored_0.2778.md">evidence-limited B2 analysis ↗</a>, <a href="{p}knowledge/session-review-arena-9ca08e2e.md">prior forensic audit ↗</a>, and <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric">official metric description ↗</a>.</p></div></section>
<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> PRE-IMPLEMENTATION HYPOTHESES</p><h2>Three candidates. None assigned or tested.</h2><p>Ranked qualitatively by expected benefit relative to cost; no numerical DTI projection is made. Exact layers, mechanisms, mimics, novelty scope, prerequisites, and validation protocol are in the <a href="{p}knowledge/hypotheses-20261029.md">full preregistration slate ↗</a>.</p></div></div><div class="hypothesis-grid">
<article class="hypothesis-card"><span class="hypothesis-rank">01 <span>LOW–MEDIUM COST</span></span><h3>Completeness-conditioned seismic shadow</h3><p>Test a local seismic-density deficit conditional on geodetic strain and verified catalogue completeness. The contrast is locked/slowly slipping buried structure versus positive-seismicity corridor methods.</p><div><b>Mimics:</b> uneven event detection, geodetic smoothing, aseismic creep, production-induced seismicity.</div><small>Shared-stack bands only, pending metadata; medium but uncertain upside. No holdout validation has been run.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">02 <span>MEDIUM–HIGH DATA COST</span></span><h3>Aqueous mixing residuals</h3><p>After schema review, test raw well/spring aqueous-analyte mixing residuals against local lithology and evaporative concentration—not another temperature plume or geothermometer threshold.</p><div><b>Mimics:</b> playa evaporation, water-rock reactions, sampling bias, mixed labs.</div><small>GDR 1391 page lists aqueous geochemistry under CC BY 4.0; direct ZIP fetch returned HTTP 500. Data and coverage remain unverified.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">03 <span>HIGH COVERAGE RISK</span></span><h3>Fault-focused hydrograph anomalies</h3><p>Use public USGS daily/continuous discharge, temperature, or groundwater-level time series to test persistent seasonal residuals relative to neighboring basins or wells.</p><div><b>Mimics:</b> pumping, irrigation, snowmelt, reservoirs, aquifer boundaries and site-placement bias.</div><small>Official API is documented; footprint coverage has not been queried. Sparse points may not support a 100 m prediction grid.</small></article></div></section>
<section class="section" id="prerequisites"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> GATES BEFORE ANY RUN</p><h2>Do not start an experiment yet.</h2></div></div><div class="prose-card"><ul><li>Supply the exact assigned method paragraph; do not invent the lane.</li><li>Resolve shared-template pin/source mismatches with the owner and record the canonical assignment. Do not patch a private fork.</li><li>Obtain organizer-authenticated inputs; the mirror restorer is not an official downloader.</li><li>Then use the owner template evaluator/writer, feature-alone leakage canaries, buffered whole-fault-segment holdout, and the literal pre-placement plus final-dot registry gate.</li><li>Use the experiment/time cap; never select a live slot here. Keep HOLDOUT-DTI separate from an organizer receipt.</li></ul><p>No new TIFF or geological experiment was produced in the current session; no current-session holdout score/CI, candidate registry comparison, or portal validation exists. Prior GSE/HALO artifacts are linked above and remain blocked.</p></div></section>
<section class="section" id="sources"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> TRACEABLE REFERENCES</p><h2>Go back to the source.</h2><p>Official descriptions establish source listings, not local bytes, data coverage, scientific performance, or portal acceptance.</p></div></div><div class="source-list"><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"><span><b>DrivenData · problem and metric</b><small>Target, features, score and format</small></span><span>OFFICIAL ↗</span></a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"><span><b>DrivenData · public leaderboard</b><small>Dated public snapshot; not a submission receipt</small></span><span>OFFICIAL ↗</span></a><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf"><span><b>DOE / NLR · rules</b><small>Submission limits, eligibility and AI disclosure</small></span><span>OFFICIAL ↗</span></a><a href="https://gdr.openei.org/submissions/1391"><span><b>GDR · INGENIOUS</b><small>Regional compilation and aqueous geochemistry listing · CC BY 4.0</small></span><span>OFFICIAL ↗</span></a><a href="https://api.waterdata.usgs.gov/ogcapi/v0/collections"><span><b>USGS · Water Data APIs</b><small>Monitoring locations, measurements, and time-series collections</small></span><span>OFFICIAL ↗</span></a><a href="{p}knowledge/official-sources-verified-2026-10-29.md"><span><b>Verified official-source register</b><small>Claims, current leaderboard ranks, and access limitations</small></span><span>REVIEW ↗</span></a><a href="{p}docs/data/official-leaderboard.json"><span><b>Dated leaderboard snapshot</b><small>Public ranks only; partial until automatic refresh succeeds</small></span><span>DATA ↗</span></a><a href="{p}knowledge/session-review-arena-09bbfea3.md"><span><b>Current session review</b><small>Fail-closed fix, preflight, tests, and next steps</small></span><span>REVIEW ↗</span></a></div></section>'''


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
    return f'''<div class="page-top"><span>NINE-SITE REVIEW <span class="separator">/</span> {name}</span><span class="page-date">REVIEWED 29 OCT · BYTE AUDIT 28 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SITE EXECUTIVE SUMMARY</p><h1>{name}. <em>Research only.</em></h1><p>The reported historical leader is not a newly eligible submission.</p></section>{decision('../')}
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
