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
import sys as _sys
if str(ROOT) not in _sys.path:
    _sys.path.insert(0, str(ROOT))
from scripts import submission_hub  # noqa: E402  (submission decision + download hub, 2026-10-29)
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


def _lane_latest(pattern: str) -> Path:
    files = sorted((ROOT / 'evidence').glob(pattern))
    if not files:
        raise ValueError(f'missing lane evidence: {pattern}')
    return files[-1]


def lane_status():
    """K1-HGRID-STRAIN receipts. Fail closed unless the run card blocks submission."""
    card = json.loads(_lane_latest('hgridge_run_card_*.json').read_text(encoding='utf-8'))
    build = json.loads(_lane_latest('hgridge_e3_build_*.json').read_text(encoding='utf-8'))
    e2 = json.loads((ROOT / 'evidence/hgridge_e2_holdout.json').read_text(encoding='utf-8'))
    if card.get('ok_to_submit') is not False or card.get('verdict') != 'negative' or card.get('slot_selected_or_spent'):
        raise ValueError('K1-HGRID-STRAIN run card is not fail-closed')
    if build['sha256'] != card['raster_sha256']:
        raise ValueError('run card hash does not match the build receipt')
    return card, build, e2


def status_line(p: str) -> str:
    card, build, _ = lane_status()
    name = build['file'].split('/')[-1]
    return (f'<strong>DO NOT SUBMIT</strong> · NOT CLEARED · Newest file <a href="{p}{quote(build["file"])}">{esc(name)}</a>'
            f' · SHA-256 <code>{build["sha256"][:16]}…</code> · download for audit only · '
            'literal lattice gate fails (pigeonhole floor 82.3%) · holdout not above random placement · no slot spent.')


def nine_site_summary(p: str) -> str:
    audit = json.loads((ROOT / 'evidence/nine_site_executive_20261029.json').read_text(encoding='utf-8'))
    card, build, e2 = lane_status()
    rows = audit['rows']
    site_of = {r['registry_id']: r['site'] for r in rows if r.get('registry_id')}
    by_site: dict = {}
    for r in rows:
        by_site.setdefault(r['site'], []).append(r)
    trs = []
    for site in SITES:
        best = max(by_site[site], key=lambda r: r['user_reported_score'])
        if best['pinned']:
            file_cell = (f'<a class="file-link" href="{esc(best["download_url"], quote=True)}">{esc(best["label"])}</a>'
                         '<span class="cell-sub">Pinned mirror · SHA-256 ' + esc(best['pinned_sha256'][:16]) + '…</span>')
            worst = best['worst_cross_site_forward_3px_overlap']
            wsite = site_of.get(best['worst_cross_site_file'], '?')
            unique = ('<span class="pill pill-red">NO</span>'
                      f'<span class="cell-sub">{worst:.1%} of its dots within 3 px of {esc(wsite)}</span>')
            lattice = f'{best["lattice_forward_3px_overlap"]:.1%}'
        else:
            file_cell = esc(best['label']) + '<span class="cell-sub">Not pinned in this checkout</span>'
            unique = '<span class="cell-sub">Not measured (no bytes)</span>'
            lattice = 'n/a'
        trs.append(
            f'<tr><th scope="row"><a href="{p}docs/{site}.html">{site} ↗</a></th>'
            f'<td>{file_cell}</td>'
            f'<td><strong>{best["user_reported_score"]:.4f}</strong><span class="cell-sub">USER-REPORTED · UNVERIFIED</span></td>'
            '<td>Unavailable<span class="cell-sub">No reproduced pipeline; no organizer receipt</span></td>'
            f'<td>{unique}</td><td>{lattice}</td>'
            '<td><span class="pill pill-red">NO</span><span class="cell-sub">Already listed; re-upload cannot change the score</span></td></tr>'
        )
    hold = card['holdout']['deliverable_catalogue_pruned']
    base = card['holdout']['label_blind_same_K']
    rnd = card['holdout']['random_control_same_K']
    cand_file = build['file']
    trs.append(
        '<tr><th scope="row">GEMSDOEkarage1 · K1-HGRID-STRAIN</th>'
        f'<td><a class="file-link" href="{p}{quote(cand_file)}">{esc(cand_file.split("/")[-1])}</a>'
        f'<span class="cell-sub">{build["dots"]:,} dots · SHA-256 {esc(build["sha256"][:16])}… · generated this session</span></td>'
        f'<td><strong>{hold["pooled_dti"]:.4f}</strong><span class="cell-sub">HOLDOUT-DTI · gems57-pooled-hide-v2 · n={hold["withheld_positives"]:,} · 95% CI [{hold["ci95"][0]:.4f}, {hold["ci95"][1]:.4f}] (catalogue-pruned, conservative). Label-blind arm {base["pooled_dti"]:.4f} [{base["ci95"][0]:.4f}, {base["ci95"][1]:.4f}]; random placement {rnd["pooled_dti"]:.4f}</span></td>'
        '<td>Unavailable<span class="cell-sub">Holdout is a catalogue proxy, not the new-fault test set</span></td>'
        f'<td><span class="pill pill-green">YES</span><span class="cell-sub">Worst of 15 pinned non-lattice rasters (incl. GEMS19 parent) {card["correlation_and_overlap_vs_registry"]["worst_focus_forward_3px_overlap"]:.1%}; max |ρ| {card["correlation_and_overlap_vs_registry"]["worst_focus_abs_spearman"]:.3f}</span></td>'
        f'<td>{card["correlation_and_overlap_vs_registry"]["lattice_forward_3px_overlap"]:.1%}<span class="cell-sub">literal FAIL; floor {card["correlation_and_overlap_vs_registry"]["lattice_floor_forward_overlap"]:.1%}</span></td>'
        '<td><span class="pill pill-red">NO</span><span class="cell-sub">Negative: holdout ≈ random; lattice literal fail</span></td></tr>'
    )
    best_row = max(rows, key=lambda r: r['user_reported_score'])
    return f'''<section class="section comparison" id="nine-sites"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> NINE-SITE EXECUTIVE SUMMARY · 29 OCT 2026</p><h2>Best file per site, estimate, and uniqueness.</h2><p>Highest USER-REPORTED file per site. Estimated score is UNAVAILABLE for every row: no organizer receipt exists and no pipeline is reproduced here. "Unique" is measured against the pinned focus-site rasters and the 13GEMSDOE lattice only. Highest listed score: <strong>{esc(best_row['label'])} ({best_row['user_reported_score']:.4f}, USER-REPORTED)</strong>; it is not unique against the other focus-site files, so re-uploading it is not a new candidate.</p></div></div>
<div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table →</div><div class="table-scroll" tabindex="0" role="region" aria-label="Nine-site executive summary"><table><thead><tr><th>Site</th><th>Best file to download</th><th>Score</th><th>Estimated score</th><th>Unique vs other focus sites?</th><th>Lattice overlap</th><th>Submit?</th></tr></thead><tbody>{''.join(trs)}</tbody></table></div></div></section>'''


def shell(title: str, body: str, depth: int = 0, active: str = 'Overview'):
    p = '../' * depth
    doc = p + 'docs/'
    links = [('Overview', p + 'index.html'), ('Submit now', doc + 'submission-hub.html'),
             ('Executive summary', doc + 'executive-summary.html'),
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
<div class="container"><p class="global-hold">{status_line(p)}</p></div></header>
<main id="main"><div class="container">{body}</div></main><footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div><div class="footer-links"><a href="{doc}data/latest-run-card.json">Latest run card</a><a href="{doc}research.html">Research</a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition ↗</a></div><div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with the organizers.</span></div></div></footer></body></html>'''


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
    return f'''<section class="decision-panel" aria-labelledby="decision-title"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT SUBMISSION DECISION <span class="status-tag">DO NOT SUBMIT</span></div>
<h2 id="decision-title">No eligible submission file yet. Two research rasters fail the literal lattice gate.</h2><p><strong>not cleared for upload.</strong> No approved .tif to download.</p>
<p>The prior BB-STEP file <code class="wrap">{esc(card['submission_name'])}</code> is unique versus the nine focus sites (worst overlap {nine:.1%}) but has {lat:.2%} lattice overlap; it is a duplicate. Its prior-session <strong>HOLDOUT-DTI {dti['value']:.5f}</strong> [{dti['ci95'][0]:.5f}, {dti['ci95'][1]:.5f}] used evaluator {esc(dti['evaluator_version'])} with {dti['withheld_positives']:,} withheld positives. This is not an organizer score and does not override the duplicate stop.</p>
<p>The newer Conduitcrest research file has {clat['candidate_dots']:,} dots; {clat['candidate_dots_within_closed_3px_disk']:,} ({clat['directed_overlap']:.4%}) are within 3 px of the pinned lattice, exceeding the 70% threshold. Its prior run card's incomplete <strong>HOLDOUT-DTI {chdt['reported_value']:.6f}</strong> claim names evaluator {esc(chdt['evaluator_version'])} and {chdt['withheld_positives']:,} withheld positives but provides <strong>no 95% CI</strong>; it is not a release-grade result.</p>
<p>Original Conduitcrest uniqueness compared only the nine focus-site rasters, not the lattice or complete fleet. Its pre-placement lattice comparison and per-feature canary are absent. Both candidates are research/audit files only; neither is cleared for upload.</p>
<p>Historical HMAS / GPC-Z files also remain blocked ({ar['directed_overlap']:.2%} and {br['directed_overlap']:.2%} vs lattice).</p>
<p><strong>Current review · session 1668dda0:</strong> Audited all 9 local <code>docs/downloads/*.tif</code> files and 9 SHA-pinned sibling/peer GeoTIFFs across 22 commit-pinned ecosystem repositories (<code>GEMSDOEkarage2/3</code>, <code>GEMSDOE91/92</code>, <code>KANLER</code>, <code>EUG</code>, <code>WBG</code>, <code>GINNY</code>, <code>Apart</code>, <code>SASS</code>). Retracted PR #42's synthetic <code>karage1-unique-alteration-dots-20261028-zeros.tif</code> (2,113 outside-footprint positives + 99.86% lattice overlap), quarantined <code>generate_unique_submission.py</code> &amp; <code>run_bbstep_experiments.py</code>, and hardened <code>validate_geotiff.py</code> against all-finite bogus templates and outside-footprint positives. <a href="{prefix}knowledge/session-review-arena-1668dda0.md">Read session 1668dda0 review &amp; 4 hypotheses ↗</a> · <a href="{prefix}evidence/local_downloads_and_peer_audit_20261028.json">9-local + 9-peer saved-byte audit JSON ↗</a> · <a href="{prefix}evidence/session_1668dda0_run_card.json">Session 1668dda0 run card ↗</a></p>
<p><strong>Prior session · a1ef4ce0:</strong> The nine-site audit was independently reproduced from pinned bytes; missing baseline-positive counts or pixel-mask evidence fail the automated promotion gate. <a href="{prefix}knowledge/session-review-arena-a1ef4ce0.md">Session a1ef4ce0 review ↗</a> · <a href="{prefix}evidence/session_a1ef4ce0_run_card.json">Session a1ef4ce0 card ↗</a></p>
<div class="decision-actions"><button class="button button-disabled" disabled>No approved .tif to download</button>
<a class="button button-light" href="{prefix}docs/executive-summary.html#audit">Review research-only downloads ↗</a>
<a class="button button-light" href="{prefix}evidence/conduitcrest_lattice_reaudit_20261028.json">Inspect latest lattice audit ↗</a>
<a class="button button-light" href="{prefix}evidence/bbstep_uniqueness.json">Inspect BB-STEP uniqueness ↗</a></div>
<p class="download-help">Conduitcrest research file (research only): <a href="{prefix}docs/downloads/{quote(conduit_path.name)}">{esc(conduit_path.name)}</a> · SHA-256 <code>{conduit_audit['candidate']['sha256']}</code>. Download is for audit only, not submission. No weekly slot was selected or spent.</p></div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative · lattice duplicates</strong></div><div><span>LEADERBOARD ESTIMATE</span><strong>Unavailable</strong></div><div><span>BB-STEP LATTICE</span><strong>{lat:.2%} · duplicate</strong></div><div><span>CONDUITCREST LATTICE</span><strong>{clat['directed_overlap']:.2%} · duplicate</strong></div><a href="{prefix}docs/data/latest-run-card.json">Latest superseding run card ↗</a></div></section>'''


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
        '<span class="cell-sub">Generated this session · research only</span></td>'
        f'<td><strong>{dti["value"]:.4f}</strong><span class="cell-sub">HOLDOUT-DTI · {esc(dti["evaluator_version"])} · n={dti["withheld_positives"]:,} · 95% CI [{dti["ci95"][0]:.4f}, {dti["ci95"][1]:.4f}]</span></td>'
        '<td>Unavailable<span class="cell-sub">No organizer forecast</span></td>'
        f'<td><span class="pill pill-red">NO vs lattice</span><span class="cell-sub">Yes vs 9 sites ({nine:.1%}); lattice {lat:.1%}</span></td>'
        '<td><span class="pill pill-red">DO NOT SUBMIT</span></td></tr>'
    )
    return f'''<section class="section comparison" id="comparison"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> DOWNLOAD TABLE</p><h2>Which file, which number, unique or not.</h2><p>Only HOLDOUT-DTI or USER-REPORTED / UNVERIFIED numbers appear. No projection is written as a score. The generated BB-STEP file is unique versus the nine listed GEMSDOE sites and is still a lattice duplicate under the parallel-run rule.</p></div></div>
<div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table →</div><div class="table-scroll" tabindex="0" role="region" aria-label="Nine-site comparison"><table><thead><tr><th>Site</th><th>File to download</th><th>Labeled number</th><th>New organizer estimate</th><th>Unique?</th><th>Action</th></tr></thead><tbody>{ours}{conduit_row}
{rows_for(prefix)}</tbody></table></div></div></section>'''


NINE_SCORES = ROOT / 'registry/user_reported_scores_20261029.json'
NINE_LINEAGE = ROOT / 'evidence/site_lineage_verification_20261029.json'
LOCAL_AUDIT_20261029 = ROOT / 'evidence/local_downloads_audit_20261029.json'


def nine_site_section(prefix: str) -> str:
    """Top-of-site decision table for the nine focus sites.

    Every number is read from a committed file: user-reported scores (labelled
    USER-REPORTED / UNVERIFIED) and the SHA-pinned mirror overlap audit. Nothing
    here is a score estimate, and no file is cleared for upload.
    """
    scores = json.loads(NINE_SCORES.read_text())['entries']
    lineage = json.loads(NINE_LINEAGE.read_text())
    local = json.loads(LOCAL_AUDIT_20261029.read_text())
    # Largest share of a site's dots lying within 3 px of any single sibling's dots.
    best_share: dict[str, tuple[float, str]] = {s: (0.0, '') for s in SITES}
    for key, v in lineage['pairwise_nine_sites'].items():
        a, b = key.split('|')
        for x, y, frac in ((a, b, v['a_dots_within_3px_of_b_fraction']),
                           (b, a, v['b_dots_within_3px_of_a_fraction'])):
            if x in best_share and frac > best_share[x][0]:
                best_share[x] = (frac, y)
    rows = []
    for site in SITES:
        mine = [e for e in scores if e['site'] == site]
        top = max(mine, key=lambda e: e['score'])
        share, sibling = best_share[site]
        rows.append((top['score'], site, top, share, sibling, len(mine)))
    rows.sort(key=lambda r: -r[0])
    body = []
    for rank, (score, site, top, share, sibling, n) in enumerate(rows, 1):
        body.append(
            f'<tr><th scope="row">#{rank} · {site}</th>'
            f'<td><code class="wrap">{esc(top["file_name"])}</code>'
            f'<span class="cell-sub">Third-party file · learning only · do not resubmit · <a href="{esc(top["url"])}">source ↗</a></span></td>'
            f'<td><strong>{score:.4f}</strong><span class="cell-sub">USER-REPORTED / UNVERIFIED · {n} listed file(s)</span></td>'
            f'<td><span class="pill pill-red">NO</span><span class="cell-sub">{share:.1%} of its dots lie within 3 px of {sibling}</span></td>'
            '<td><span class="pill pill-red">DO NOT SUBMIT</span></td></tr>')
    lat = local['local_downloads']
    worst_lat = min(r['lattice_directed_overlap_3px'] for r in lat)
    cleared = sum(1 for r in lat if r.get('ok_to_submit'))
    checks = lineage['checks']
    gate_note = ('yes' if checks['GEMSDOE25_equals_GEMSDOE30'] else 'no')
    removed = checks['GEMSDOE32_vs_GEMSDOE25_remove_within_2px_of_labels']['removed']
    worst_sibling = min(v for v in [best_share[s][0] for s in SITES])
    return (
        '<section class="section nine-site-decision" id="nine-site-decision" aria-labelledby="nine-site-title">'
        '<div class="section-heading"><div>'
        '<p class="eyebrow"><span class="eyebrow-line"></span> SUBMISSION DECISION · NINE FOCUS SITES</p>'
        '<h2 id="nine-site-title">Which file is best, and is it OK to submit?</h2>'
        f'<p><strong>Answer: no file is OK to download and submit.</strong> Our own files cleared: <strong>{cleared} of {len(lat)}</strong>. '
        'The highest public file in the nine focus sites is GEMSDOE32 at <strong>0.2778 (USER-REPORTED / UNVERIFIED)</strong>; '
        'it is a third-party file, so we may study it but must not resubmit it.</p></div></div>'
        '<div class="table-shell"><div class="table-scroll" tabindex="0" role="region" aria-label="Nine focus sites ranked by reported score">'
        '<table><thead><tr><th>Rank · site</th><th>Best public file (learning only)</th><th>Score label</th>'
        '<th>Unique vs listed GEMSDOE sites?</th><th>Submit?</th></tr></thead>'
        f'<tbody>{"".join(body)}</tbody></table></div></div>'
        '<p class="cell-sub">Scores come from <code>registry/user_reported_scores_20261029.json</code>. '
        'Uniqueness is measured on SHA-pinned mirror rasters in '
        f'<code>{esc(str(NINE_LINEAGE.relative_to(ROOT)))}</code>: GEMSDOE25 and GEMSDOE30 have identical dot masks ({gate_note}); '
        f'GEMSDOE32 is GEMSDOE25 minus {removed:,} dots. Every focus site has at least {worst_sibling:.1%} of its dots within 3 px of one sibling. '
        f'Our own worst lattice overlap is {worst_lat:.2%} (literal duplicate; threshold 70%). '
        'No estimate for any of our files is possible without a holdout run and an organizer receipt.</p>'
        '<p class="cell-sub">Live public leaderboard checked 29 Oct 2026: #1 0.4544, #2 0.3916, #3 0.3911 '
        '(<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">DrivenData ↗</a>). '
        'The 0.4413 and 0.3195 figures in the session brief do not match that page.</p>'
        '</section>')



def home(depth=0):
    p = '../' * depth
    return f'''<div class="page-top"><span>GEMS PRIZE <span class="separator">/</span> DECISION BRIEF</span><span class="page-date">INDEPENDENT AUDIT · 28 OCT 2026</span></div>
<section class="hero compact-hero"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-line"></span> EVIDENCE BEFORE A LEADERBOARD SLOT</p><h1>Find faults.<br><em>Protect every submission.</em></h1><p class="hero-description">A clear, auditable workspace for fault discovery in the Great Basin. We separate format checks, scientific evidence, uniqueness and actual portal acceptance.</p><div class="hero-actions"><a class="text-link" href="#comparison">Compare the nine sites ↓</a><a class="subtle-link" href="{p}docs/research.html">Explore the research ↗</a></div></div>
<div class="terrain-card terrain-small" aria-label="Illustrative contour artwork, not a prediction map"><div class="terrain-top"><span>GEO<span class="terrain-dot">●</span>DAWN</span><span>FIELD NOTE / 01</span></div><svg class="terrain-lines" viewBox="0 0 620 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.5"><path d="M-50 10C90 25 95 155 200 110S305-10 410 55s150 110 250 40"/><path d="M-50 35C80 50 100 180 205 135S310 15 410 80s150 110 250 40"/><path d="M-50 60C70 75 105 205 210 160S315 40 410 105s150 110 250 40"/><path d="M-50 85C60 100 110 230 215 185S320 65 410 130s150 110 250 40"/><path d="M-50 110C50 125 115 255 220 210S325 90 410 155s150 110 250 40"/><path d="M-50 135C40 150 120 280 225 235S330 115 410 180s150 110 250 40"/><path d="M-50 160C30 175 125 305 230 260S335 140 410 205s150 110 250 40"/></g><g class="terrain-focus" fill="none"><circle cx="379" cy="139" r="40"/><circle cx="379" cy="139" r="26"/><path d="M379 89v100M329 139h100"/></g></svg><div class="terrain-caption"><span><b>THE STUDY AREA</b><br>Western Great Basin</span><span>NEVADA + CALIFORNIA<br><b>CONCEPTUAL ONLY</b></span></div></div></section>
{nine_site_section(p)}{decision(p)}{nine_site_summary(p)}<section class="snapshot" aria-label="Evidence snapshot"><div class="snapshot-item"><div class="snapshot-label">PUBLIC LEADERBOARD SNAPSHOT</div><div class="snapshot-value">0.4544</div><p>Organizer public leaderboard · direct read 29 Oct 2026 · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">check current ↗</a></p></div><div class="snapshot-item"><div class="snapshot-label">BEST SUPPLIED NINE-SITE REPORT</div><div class="snapshot-value">0.2778</div><p>GEMSDOE32 · USER-REPORTED, not confirmed</p></div><div class="snapshot-item"><div class="snapshot-label">PRIOR BB-STEP SESSION</div><div class="snapshot-value">3 <span class="snapshot-context">experiments</span></div><p>Separate parallel run · lattice stop applied</p></div><div class="snapshot-item"><div class="snapshot-label">INPUT RESTORATION</div><div class="snapshot-value">21 <span class="snapshot-context">files</span></div><p>Hash-pinned mirrors · not organizer-authenticated</p></div></section>
{comparison(p)}<section class="section detail-grid"><div><p class="eyebrow"><span class="eyebrow-line"></span> THE B2 QUESTION</p><h2>What made the reported leader different?</h2></div><div class="prose-card"><p>On the audited mirrored grid, GEMSDOE32 B2 is exactly GEMSDOE25's d2.8 mask with 6,436 dots within two pixels of the mirrored known-fault catalogue removed; no new dots were added. GEMSDOE25 and GEMSDOE30 have the same positive-pixel mask.</p><p>Reducing redundant prediction mass <em>could</em> improve the distance-weighted Tversky tradeoff, but it can also remove true coverage. Hidden labels and an artifact-linked receipt are unavailable, so the cause and any improvement over the reported result remain unproven.</p><p>Known fault pixels are masked, but nearby new faults may still matter. A catalogue buffer is not automatically a free scoring exclusion. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">DrivenData staff clarification ↗</a></p><a class="text-link" href="{p}docs/research.html#b2">Read the scientific analysis ↗</a></div></section>
<section class="next-strip"><div><p class="eyebrow">NEXT STEPS</p><h2>Resolve the lattice gate before spending a slot.</h2><p>BB-STEP is unique versus the nine listed sites and still a lattice duplicate. Do not jitter dots to evade the rule. No automatic DrivenData scraping or upload.</p></div><a class="button button-dark" href="{p}docs/executive-summary.html">See the checklist ↗</a></section>'''


def upload_packet(p: str) -> str:
    """Upload packet for the newest lane file. Always blocked until a separate selector clears it."""
    card, build, _ = lane_status()
    note = card['submission_note']
    if len(note) > 140 or len(card['submission_name']) > 140:
        raise ValueError('upload packet exceeds the 140-character limit')
    return (f'<section class="section" id="upload-packet"><div class="section-heading"><div>'
            '<p class="eyebrow"><span class="eyebrow-line"></span> UPLOAD PACKET · BLOCKED</p>'
            '<h2>File, unique name and note (≤ 140 characters).</h2>'
            '<p>Use only after an independent selector clears the file. Nothing here is permission to upload.</p></div></div>'
            '<div class="prose-card"><p><strong>Status: DO NOT SUBMIT · NOT CLEARED.</strong> Download for audit only.</p>'
            f'<p>File: <a class="file-link" href="{p}{quote(build["file"])}">{esc(build["file"].split("/")[-1])}</a></p>'
            f'<p>SHA-256: <code class="wrap">{build["sha256"]}</code></p>'
            f'<p>Unique name: <code class="wrap">{esc(card["submission_name"])}</code></p>'
            f'<p>Note ({len(note)} characters): <code class="wrap">{esc(note)}</code></p></div></section>')


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
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> EXECUTIVE SUMMARY</span><span class="page-date">REVIEWED 28 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> THE SUBMISSION CHECKLIST</p><h1>One file. <em>Evidence first.</em></h1><p>What to submit, when—and why today's answer is no.</p></section>{decision(p)}
{nine_site_summary(p)}
{upload_packet(p)}
<section class="section" id="audit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> SAVED-BYTE CHECK</p><h2>The 9 local and 9 sibling/peer GeoTIFFs covered by the 1668dda0 receipt fail its gate; later candidates are audited separately below.</h2><p>Research downloads are explicitly not submission recommendations. Uniqueness versus the nine focus sites is not uniqueness versus the lattice or a complete fleet registry.</p></div></div><div class="audit-grid">{''.join(cards)}</div><p class="body-copy">In addition to the four cards above (and the <code>-nan.tif</code> twins for BB-STEP and GPC-Z plus the quarantined CDA1 <code>-zeros.tif</code>/<code>-nan.tif</code> pair), session <code>1668dda0</code> audited and retracted <code>karage1-unique-alteration-dots-20261028-zeros.tif</code> (SHA-256 <code>8bc4dae02a99da68…</code>): 2,113 of its 3,500 positive pixels lie outside the competition footprint (<code>outside_encoding_accepted = false</code>) and 99.8558% (1,385/1,387) of its inside-footprint positives lie within 3 px of the pinned lattice. Sibling <code>GEMSDOEkarage2</code> (99.86%), <code>GEMSDOEkarage3</code> (99.35%), and newly audited peer GeoTIFFs across <code>GEMSDOE91</code>, <code>KANLERGEMSDOE3</code>, <code>WBGGEMSDOE1</code>, <code>ApartGEMSDOE1/2</code>, and <code>GEMSDOESASS1</code> also overlap 99.35%–99.95% within 3 px of the lattice (<a href="{p}evidence/local_downloads_and_peer_audit_20261028.json">inspect full 18-raster receipt ↗</a>).</p><p class="body-copy">The historical K/Th + thermal candidate <code>unique-hyp-kth-therm-mask-20261028-zeros.tif</code> has been moved out of the public download directory. Its prior promotion claim is superseded. A pinned-mirror saved-byte audit records 99.9017% directed 3-px overlap with the lattice, exceeding the literal duplicate threshold; the former holdout claim is not reproduced. It remains quarantined for audit only; see <a href="{p}archive/quarantined-20261029/README-review-dc2e4c0c.md">archive note ↗</a> and <a href="{p}evidence/unique_hyp_kth_therm_mask_retraction_20261029.json">retraction receipt ↗</a>.</p><p class="body-copy">The official <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format">format description</a> says data outside the bounds should be null or NaN. A strict all-finite check and a null/NaN-outside check are different diagnostics; neither establishes actual portal acceptance. The rejected original file was not supplied, so the cause of its range error is unknown.</p></section>
{comparison(p)}<section class="section" id="steps"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> FOR A FUTURE CLEARED CANDIDATE</p><h2>How to submit, once eligible.</h2><p>These steps are not permission to upload either historical artifact.</p></div></div><div class="steps-grid"><article><span>01 / EVIDENCE</span><h3>Pass the automated gates</h3><p>Use the shared evaluator, fold-local features and per-feature canaries. Beat a frozen comparable holdout best; audit surface and dots against the complete registry; reopen the TIFF and validate saved bytes.</p></article><article><span>02 / SELECTOR</span><h3>Choose a slot separately</h3><p>Only an independent selector may choose an eligible candidate and check the current allowance on the authenticated submission page. The September rules say three submissions per week.</p></article><article><span>03 / DOWNLOAD</span><h3>Choose the exact file</h3><p>Download the approved single-band GeoTIFF (or a ZIP containing one GeoTIFF). Check its displayed SHA-256, unique name and note of at most 140 characters.</p></article><article><span>04 / UPLOAD</span><h3>Use the official form</h3><p>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData</a>, select Submit → Make new submission, choose the .tif or ZIP, and paste the note. Retain the file-linked organizer receipt.</p></article></div><div class="notice guide-notice"><span aria-hidden="true">ⓘ</span><p>The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> require disclosure of generative-AI use in the narrative when applicable. Public leaderboard performance is not the private final score.</p></div></section>'''


def research(depth=1):
    p = '../' * depth
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> RESEARCH</span><span class="page-date">REVIEWED 28 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SCIENCE BEFORE SCORING</p><h1>Understand the ground.<br><em>Respect the unknown.</em></h1><p>The target is previously unmapped geological faults, not direct proof of a geothermal vent.</p></section>
<section class="notice"><span aria-hidden="true">ⓘ</span><p><strong>Research only:</strong> A prior parallel session ran three BB-STEP experiments and another generated Conduitcrest. Both fail the literal lattice gate. No geological experiment was run by the active `9ca08e2e` audit session. Novelty across the whole fleet remains unverified; HOLDOUT-DTI is not an organizer score.</p></section>
<section class="section detail-grid" id="b2"><div><p class="eyebrow"><span class="eyebrow-line"></span> WHAT THE BYTES SHOW</p><h2>Why B2 may have worked.</h2></div><div class="prose-card"><p>Cross-site binary-mask algebra establishes a collar-ablation ladder on the identical GEMSDOE25/GEMSDOE30 parent mask (44,090 dots): removing 3,891 dots within 1 pixel of the mirrored catalogue yields GEMSDOE31 and GEMSDOE28 h27-4-r1 (40,199 dots, 0.2708 user-reported); removing 6,436 dots within 2 pixels yields GEMSDOE32 B2 (37,654 dots, 0.2778 user-reported). GEMSDOE36 (38,854 dots, 0.2750 user-reported) is an exact superset that adds 1,200 off-catalogue dots.</p><p>For the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric">organizer metric</a>, deleting near-catalogue digitization halos helps only if saved false-positive penalty outweighs lost distance-weighted recall. Firsthand inspection of restored <code>training_features.tif</code> found 3,073 raw float32 nodata pixels inside the submission footprint and strictly positive Band 6 <code>tc</code> curvature values, both requiring explicit inference masking.</p><p>The reported 0.2778 is an unverified user report. No experiment in the active session establishes a higher leaderboard result. <a class="text-link" href="{p}knowledge/session-review-arena-9ca08e2e.md">Read the complete forensic &amp; 9-site audit ↗</a></p></div></section>
<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> RANKED HYPOTHESES</p><h2>One executed. Four still qualitative.</h2><p>Latest session <code>1668dda0</code> preregistration slate: Cross-Potential Dip-Polarity Co-Gradient Step (<code>CP-DPCS</code>), Biharmonic Elastic Relay-Bridge Stress-Transfer Corridor (<code>BERB-STC</code>), Wavelet-Destriped Potassium-Residual Magnetics Trough (<code>WD-KRMT</code>), and Cross-Fan Drainage-Incision Knickzone Alignment (<code>CF-DIKA</code>). <a href="{p}knowledge/session-review-arena-1668dda0.md#4-pre-implementation-generation--qualitative-ranking-of-four-untried-geological-hypotheses">Exact layers, off-catalogue rationale, non-fault mimics and sibling differences ↗</a></p><p>Additional session a1ef4ce0 preregistration slate: magnetic texture change points, paired block-tilt breaks and magnetic edge-network severance. All are untested proposals, not assigned lanes. <a href="{p}knowledge/session-review-arena-a1ef4ce0.md#2-preregistered-research-slate--proposals-only-not-assigned-lanes">Layers, confounders, relative cost and validation blockers ↗</a></p><p>Ordering reflects qualitative promise relative to cost, not a predicted DTI improvement. BB-STEP used only competition gravity, depth-to-basement, slope and RTP bands restored from hash-pinned mirrors.</p></div></div><div class="hypothesis-grid">
<article class="hypothesis-card"><span class="hypothesis-rank">00 <span>EXECUTED · NEGATIVE</span></span><h3>Buried basement-step (BB-STEP)</h3><p>Isostatic-gravity and depth-to-basement NMS ridges, sign-invariant alignment, low topographic-slope veto. Targets intra-basin faults the scarp catalogue misses. Max leakage-canary AUC 0.53. Unique vs nine focus sites (12.6%); lattice 98.5%.</p><div><b>Confounders:</b> lithologic contacts, volcanic-flow density edges, basin-fill compaction.</div><small>Opposite of H19-5 / GPC-Z (slope is a veto). Fold-local HOLDOUT-DTI 0.0318 [0.0271, 0.0363], evaluator gemsk-hide-recover-v1, n=60,988. Not an organizer score.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">01 <span>MEDIUM COST</span></span><h3>Signed multiscale offsets</h3><p>Use RTP magnetics, isostatic gravity and detrended elevation: compare oriented, signed cross-profiles at two scales. Stable offsets may indicate a buried discontinuity without a mapped scarp.</p><div><b>Confounders:</b> lithologic contacts, volcanic flow edges and survey artifacts.</div><small>Differs from BB-STEP (unsigned aligned ridges) by testing signed profile displacement; global novelty unverified.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">02 <span>MEDIUM COST</span></span><h3>Alteration-boundary residuals</h3><p>Compare local background-normalized K/eTh radiometric boundaries with oriented RTP edges. An altered structure under cover might differ from the catalogue.</p><div><b>Confounders:</b> weathering, potassium-rich intrusions and acquisition blocks.</div><small>Tests directional residuals rather than the prior raw radiometric plume. <a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and">USGS GeoDAWN ↗</a></small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">03 <span>HIGH COST</span></span><h3>Drainage asymmetry</h3><p>On USGS 3DEP DEMs, test repeated cross-valley asymmetry among adjacent catchments, conditioned on drainage area. A degraded or obscured trace could alter drainage geometry.</p><div><b>Confounders:</b> stream piracy, fan deposition and erosion.</div><small>Different from the prior pixel-level scarp score. <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP ↗</a>; local official tiles not fetched.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">04 <span>HIGH COST</span></span><h3>Sampling-aware thermal residuals</h3><p>Cross-fit INGENIOUS 2 m probe temperatures against terrain and access, then compare residual patterns with gravity boundaries. Concealed flow could remain near an unmapped structure.</p><div><b>Confounders:</b> solar heating, groundwater and access-biased sampling.</div><small>Unlike the earlier raw thermal plume, explicitly models sampling bias. <a href="https://gdr.openei.org/submissions/1391">GDR 1391 ↗</a>; official raw bytes not authenticated locally.</small></article></div></section>
<section class="section" id="sources"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> TRACEABLE REFERENCES</p><h2>Go back to the source.</h2><p>These official descriptions do not authenticate the third-party mirrors or validate the hypotheses.</p></div></div><div class="source-list"><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"><span><b>DrivenData · problem and metric</b><small>Target, features, score and format</small></span><span>OFFICIAL ↗</span></a><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf"><span><b>DOE / NLR · rules</b><small>Submission limits, eligibility and AI disclosure</small></span><span>OFFICIAL ↗</span></a><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and"><span><b>USGS · GeoDAWN</b><small>Magnetic and radiometric grids · CC0</small></span><span>OFFICIAL ↗</span></a><a href="https://gdr.openei.org/submissions/1391"><span><b>GDR · INGENIOUS</b><small>Thermal, geology and geophysics compilation · CC BY 4.0</small></span><span>OFFICIAL ↗</span></a><a href="https://github.com/drivendataorg/gems-prize-reference-solution"><span><b>DrivenData · reference implementation</b><small>Organizer-provided starting point</small></span><span>CODE ↗</span></a><a href="{p}knowledge/sources-2026-10-28.md"><span><b>Project source register</b><small>Access, provenance and limitations</small></span><span>REVIEW ↗</span></a><a href="{p}knowledge/session-review-arena-9ca08e2e.md"><span><b>Latest forensic &amp; 9-site audit</b><small>21 focus files, B2 algebra and 19-band feature audit</small></span><span>REVIEW ↗</span></a></div></section>'''


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
    return f'''<div class="page-top"><span>NINE-SITE REVIEW <span class="separator">/</span> {name}</span><span class="page-date">28 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SITE EXECUTIVE SUMMARY</p><h1>{name}. <em>Research only.</em></h1><p>The reported historical leader is not a newly eligible submission.</p></section>{decision('../')}
<section class="section detail-grid"><div><p class="eyebrow">HISTORICAL FILE</p><h2>What the evidence says.</h2></div><div class="prose-card"><p><a class="wrap" href="{esc(artifact_url(entry), quote=True)}">{esc(Path(entry['path']).name)} ↗</a><br>SHA-256 <code class="wrap">{entry['sha256']}</code></p><p><strong>{claim['reported_score']:.4f} USER-REPORTED · UNVERIFIED.</strong> No artifact-linked organizer submission receipt is available. A new leaderboard estimate is unavailable.</p><p>The file has {row['positive_pixels']:,} positive pixels; {row['lattice_directed_overlap']:.2%} fall within 3 pixels of the registered lattice. It also overlaps {pair[0]:.2%} with {pair[1]} in the directional nine-file audit. Both exceed the literal 70% threshold. <strong>DO NOT RESUBMIT.</strong></p><p>These are geometric measurements, not proof of equal geologic predictions or a forecast. Scope is historical focus-site rasters plus the lattice; complete current-registry uniqueness was not checked.</p><a class="text-link" href="data/reference-audit.json">Review the measured audit ↗</a></div></section>{secondary_section}<section class="next-strip"><div><p class="eyebrow">BACK TO THE DECISION</p><h2>No new file is cleared.</h2><p>Check the current gates and submission guide before considering any upload.</p></div><a class="button button-dark" href="executive-summary.html">Executive summary ↗</a></section>'''


def main():
    # One builder owns all public decision/guide pages so an old lane-specific
    # generator cannot silently restore a false green badge.
    evidence()
    secondary_evidence()
    local_and_peer_evidence()
    hub = submission_hub.build_facts()
    pages = {
        ROOT / 'index.html': shell('Submission overview', submission_hub.summary_strip(0) + home(0), 0),
        DOCS / 'submission-hub.html': shell('Submit now: executive summary and download', submission_hub.body(hub, 1), 1, 'Submit now'),
        ROOT / 'legacy-overview.html': shell('Submission overview', home(0), 0),
        ROOT / 'executive-summary.html': shell('Submission guide', nine_site_section('') + guide(0), 0, 'Executive summary'),
        DOCS / 'index.html': shell('Submission overview', submission_hub.summary_strip(1) + home(1), 1),
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
