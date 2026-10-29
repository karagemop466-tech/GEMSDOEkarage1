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
import subprocess
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
            or latest.get('holdout_dti', {}).get('dti') is not None
            or not str(latest.get('holdout_dti', {}).get('status', '')).startswith('No valid HOLDOUT-DTI score is reported')
            or audit.get('previous_holdout_claim', {}).get('reported_value') is not None
            or audit.get('previous_holdout_claim', {}).get('ci95') is not None
            or not str(audit.get('previous_holdout_claim', {}).get('status', '')).startswith('The prior scalar is suppressed')
            or latest.get('post_run_lattice_audit', {}).get('directed_overlap') != lattice.get('directed_overlap')
            or lattice.get('exceeds_overlap_threshold') is not True
            or lattice.get('literal_rule_verdict') != 'duplicate; stop'
            or audit.get('ok_to_submit') is not False):
        raise ValueError('Conduitcrest candidate lacks a bound fail-closed lattice decision')
    return audit, old_card, latest, candidate_path


def local_and_peer_evidence():
    """Verify current download TIFFs, all Git-tracked TIFF bytes, and pinned peers."""
    def _reject_const(v: str):
        raise ValueError(f'non-standard JSON constant: {v}')

    def _unique_obj(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ValueError(f'duplicate JSON key: {k}')
            out[k] = v
        return out

    path = ROOT / 'evidence/local_downloads_and_peer_audit_20261029.json'
    data = json.loads(path.read_text(encoding='utf-8'), parse_constant=_reject_const, object_pairs_hook=_unique_obj)
    local_rows = data.get('local_downloads', [])
    peer_rows = data.get('peer_rasters', [])
    current_tifs = sorted((DOCS / 'downloads').glob('*.tif'))
    row_files = {row.get('file') for row in local_rows if isinstance(row, dict)}
    expected_files = {f'docs/downloads/{tif.name}' for tif in current_tifs}
    tracked = data.get('tracked_tiff_inventory', {})
    tracked_rows = tracked.get('tracked_tiffs', [])
    tracked_files = {row.get('file') for row in tracked_rows if isinstance(row, dict)}
    try:
        git_tracked = set(subprocess.run(
            ['git', 'ls-files', '--', '*.tif', '*.tiff'], cwd=ROOT,
            check=True, capture_output=True, text=True).stdout.splitlines())
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError('Unable to verify the Git-tracked TIFF inventory') from exc
    archive_audit = tracked.get('quarantined_archive_audit', {})
    archive_audit_path = ROOT / 'docs/data/archive-review.json'
    if (data.get('schema') != 'karage1-local-and-peer-audit-v1'
            or data.get('submit_authorized') is not False
            or data.get('all_local_downloads_blocked') is not True
            or data.get('all_audited_peer_rasters_exceed_70pct_lattice') is not True
            or data.get('local_downloads_count') != len(current_tifs)
            or data.get('peer_rasters_count') != 9
            or len(local_rows) != len(current_tifs)
            or len(peer_rows) != 9
            or row_files != expected_files
            or not data.get('source_authentication', '').startswith('GitHub mirror pins verified')
            or tracked.get('tracked_tiff_paths_count') != len(git_tracked)
            or tracked.get('tracked_tiff_paths_count') != 15
            or tracked.get('unique_tracked_tiff_sha256_count') != 13
            or tracked.get('tracked_download_directory_paths_count') != len(current_tifs)
            or tracked.get('tracked_quarantined_archive_paths_count') != 4
            or tracked_files != git_tracked
            or len(tracked_rows) != len(git_tracked)
            or tracked.get('all_tracked_tiff_bytes_accounted') is not True
            or tracked.get('unaccounted_paths') != []
            or archive_audit.get('file') != 'docs/data/archive-review.json'
            or archive_audit.get('submission_authorized') is not False
            or archive_audit.get('schema') != 'karage1-quarantined-archive-audit-v1'
            or archive_audit.get('verified_asset_count') != 3
            or not archive_audit_path.is_file()
            or archive_audit.get('sha256') != hashlib.sha256(archive_audit_path.read_bytes()).hexdigest()):
        raise ValueError('Dated local-downloads / peer-ecosystem / tracked-TIFF audit is incomplete or not fail-closed')
    if not data.get('scope', '').startswith(f'All {len(current_tifs)} local docs/downloads/*.tif files present at audit time'):
        raise ValueError('Audit scope does not bind its local TIFF inventory count')
    for row in (*local_rows, *peer_rows):
        if row.get('ok_to_submit') is not False or row.get('literal_lattice_duplicate') is not True:
            raise ValueError(f'Blocked audit invariant violated for {row}')
    for row in local_rows:
        p = ROOT / row['file']
        if not p.is_file() or p.stat().st_size != row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError(f'Local download bytes drifted from audited receipt: {row["file"]}')
    seen_tiff_hashes = set()
    allowed_coverage = {'current-download-audit', 'same-bytes-as-current-download-audit', 'verified-quarantined-archive-audit'}
    for row in tracked_rows:
        p = ROOT / row['file']
        digest = hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
        if (digest is None or digest != row.get('sha256') or row.get('audit_coverage') not in allowed_coverage):
            raise ValueError(f'Git-tracked TIFF byte coverage is stale or incomplete: {row.get("file")}')
        seen_tiff_hashes.add(digest)
    if len(seen_tiff_hashes) != tracked.get('unique_tracked_tiff_sha256_count'):
        raise ValueError('Git-tracked TIFF unique-byte count does not match the byte inventory')
    return data


def unique_hyp_evidence():
    """Bind the negative legacy-candidate card to the TIFF and both audit receipts."""
    card_path = ROOT / 'evidence/run_card_arena_2b7c50b3.json'
    card = json.loads(card_path.read_text(encoding='utf-8'))
    current = local_and_peer_evidence()
    filename = card.get('artifact', {}).get('file')
    artifact_path = ROOT / filename if isinstance(filename, str) else ROOT / 'missing.tif'
    digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest() if artifact_path.is_file() else None
    local = next((row for row in current['local_downloads'] if row.get('file') == filename), None)
    inventory = current['tracked_tiff_inventory']
    card_inventory = card.get('tracked_tiff_inventory', {})
    comparisons = card.get('reference_comparisons', [])
    lattice = next((row for row in comparisons if row.get('reference') == 'lattice'), None)
    focus = [row for row in comparisons if isinstance(row, dict) and row.get('reference') != 'lattice']
    expected_assets = json.loads((ROOT / 'registry/reference_assets.json').read_text(encoding='utf-8'))
    asset_hashes = {row.get('id'): row.get('sha256') for row in expected_assets}
    comparison_hashes_ok = all(row.get('reference_sha256') == asset_hashes.get(row.get('reference')) for row in comparisons)
    holdout = card.get('holdout_dti', {})
    lattice_summary = card.get('registry_correlation_overlap', {}).get('lattice', {})
    if (card.get('schema') != 'karage1-historical-raster-reassessment-v1'
            or card.get('verdict') != 'negative'
            or card.get('ok_to_submit') is not False
            or card.get('upload_authorized') is not False
            or card.get('slot_selected_or_spent') is not False
            or card.get('geological_experiments_run_this_session') != 0
            or card.get('leakage_canary', {}).get('status') != 'NOT RUN'
            or card.get('leakage_canary', {}).get('single_feature_auc_leakage_threshold') != 0.90
            or card.get('protocol_holdout_spec', {}).get('status') != 'NOT RUN'
            or card.get('protocol_holdout_spec', {}).get('required_evaluator_version') != 'gems57-pooled-hide-v2'
            or card.get('protocol_holdout_spec', {}).get('alpha') != 0.2
            or card.get('protocol_holdout_spec', {}).get('beta') != 0.8
            or card.get('protocol_holdout_spec', {}).get('triangular_kernel_radius_m') != 300
            or card.get('experiment_budget', {}).get('geological_experiments_this_session') != 0
            or card.get('experiment_budget', {}).get('selector_or_slot_used') is not False
            or digest is None or digest != card.get('artifact', {}).get('sha256')
            or local is None or local.get('sha256') != digest
            or card.get('sources', {}).get('local_peer_audit_sha256') != hashlib.sha256((ROOT / 'evidence/local_downloads_and_peer_audit_20261029.json').read_bytes()).hexdigest()
            or card.get('sources', {}).get('quarantined_archive_audit') != 'docs/data/archive-review.json'
            or card.get('sources', {}).get('quarantined_archive_audit_sha256') != inventory.get('quarantined_archive_audit', {}).get('sha256')
            or card_inventory.get('tracked_tiff_paths_count') != inventory.get('tracked_tiff_paths_count')
            or card_inventory.get('unique_tracked_tiff_sha256_count') != inventory.get('unique_tracked_tiff_sha256_count')
            or card_inventory.get('all_tracked_tiff_bytes_accounted') is not True
            or card_inventory.get('unaccounted_paths') != []
            or card_inventory.get('quarantined_archive_audit') != inventory.get('quarantined_archive_audit')
            or card.get('legacy_claim_retraction', {}).get('superseded_sha256') != '5e278696b783e800579c3eb46a8000aa1e7fc71e73be1e6ac2a80b95286c18e5'
            or card.get('legacy_claim_retraction', {}).get('superseded_file') != 'docs/data/unique-hyp-kth-therm-mask-20261028-zeros.json'
            or not card.get('legacy_claim_retraction', {}).get('reported_numeric_score_suppressed')
            or card.get('legacy_claim_retraction', {}).get('reportable_holdout_result') is not None
            or holdout.get('dti') is not None or holdout.get('ci95') is not None
            or holdout.get('withheld_positive_count') is not None
            or card.get('registry_correlation_overlap', {}).get('preplacement_surface_checked') is not False
            or card.get('registry_correlation_overlap', {}).get('complete_registry_checked') is not False
            or lattice is None or len(focus) != 9 or len(comparisons) != 10
            or not comparison_hashes_ok
            or lattice.get('overlap_exceeds_70_percent') is not True
            or lattice.get('directed_overlap') <= 0.70
            or abs(lattice.get('directed_overlap') - lattice_summary.get('directed_overlap', -1)) > 1e-12
            or not all(row.get('reference') in {f'GEMSDOE{n}' for n in (24,25,27,28,30,31,32,33,36)} for row in focus)
            or any(row.get('overlap_exceeds_70_percent') or row.get('rank_abs_exceeds_0_90') for row in focus)
            or card.get('submission_note_chars') != len(card.get('submission_note', ''))
            or card.get('submission_note_chars', 999) > 140
            or card.get('download_status') != 'Audit/research only; not authorized to submit.'):
        raise ValueError('Historical unique-hyp assessment is stale, incomplete, or not fail-closed')
    public = json.loads((DOCS / 'data/unique-hyp-kth-therm-mask-20261028-zeros.json').read_text())
    current_card = json.loads((DOCS / 'data/current-session-run-card.json').read_text())
    if public != card or current_card != card:
        raise ValueError('Public reassessment summary or current-session card does not match the superseding run card')
    receipt = json.loads((DOCS / 'downloads/unique-hyp-kth-therm-mask-20261028-zeros.json').read_text())
    if (receipt.get('promoted') is not False or receipt.get('approved_for_weekly_slot') is not False
            or receipt.get('verdict') != 'negative' or receipt.get('ok_to_submit') is not False
            or receipt.get('holdout_dti', {}).get('dti') is not None
            or receipt.get('current_assessment') != 'evidence/run_card_arena_2b7c50b3.json'
            or receipt.get('sha256') != digest):
        raise ValueError('Historical TIFF receipt still contains a promotion or score claim')
    return card


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
<main id="main"><div class="container">{body}</div></main><footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div><div class="footer-links"><a href="{doc}data/current-session-run-card.json">Current review card</a><a href="{doc}research.html">Research</a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition ↗</a></div><div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with the organizers.</span></div></div></footer></body></html>'''


def decision(prefix: str):
    _, _, _, audit, card = evidence()
    current_audit = local_and_peer_evidence()
    tracked_inventory = current_audit['tracked_tiff_inventory']
    unique_hyp = unique_hyp_evidence()
    unique_row = next(r for r in current_audit['local_downloads'] if r['file'] == unique_hyp['artifact']['file'])
    synthetic_row = next(r for r in current_audit['local_downloads'] if r['file'].endswith('karage1-unique-alteration-dots-20261028-zeros.tif'))
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
<h2 id="decision-title">No eligible submission file. Every audited local GeoTIFF fails the literal lattice gate.</h2><p><strong>Nothing is cleared for upload.</strong> No approved .tif to download or submit.</p>
<p>The prior BB-STEP file <code class="wrap">{esc(card['submission_name'])}</code> is unique versus the nine focus sites (worst overlap {nine:.1%}) but has {lat:.2%} lattice overlap; it is a duplicate. Its prior-session <strong>HOLDOUT-DTI {dti['value']:.5f}</strong> [{dti['ci95'][0]:.5f}, {dti['ci95'][1]:.5f}] used evaluator {esc(dti['evaluator_version'])} with {dti['withheld_positives']:,} withheld positives. This is not an organizer score and does not override the duplicate stop.</p>
<p>The newer Conduitcrest research file has {clat['candidate_dots']:,} dots; {clat['candidate_dots_within_closed_3px_disk']:,} ({clat['directed_overlap']:.4%}) are within 3 px of the pinned lattice, exceeding the 70% threshold. Its earlier scalar is now retracted from public reporting: the original run card has no 95% CI, and the result was not independently reproduced against these saved TIFF bytes. <strong>No HOLDOUT-DTI result is reportable for Conduitcrest.</strong></p>
<p>Original Conduitcrest uniqueness compared only the nine focus-site rasters, not the lattice or complete fleet. Its pre-placement lattice comparison and per-feature canary are absent. Conduitcrest and the historical K/Th+thermal file are research/audit artifacts only; neither is cleared for upload.</p>
<p>Historical HMAS / GPC-Z files also remain blocked ({ar['directed_overlap']:.2%} and {br['directed_overlap']:.2%} vs lattice).</p>
<p><strong>Current checkout review · 29 Oct 2026:</strong> The dated saved-byte audit covers {current_audit['local_downloads_count']} local <code>docs/downloads/*.tif</code> files and {current_audit['peer_rasters_count']} SHA-pinned sibling/peer GeoTIFFs; every local file exceeds the literal lattice overlap stop threshold. The historical K/Th+thermal TIFF <code>{esc(Path(unique_hyp['artifact']['file']).name)}</code> has {unique_row['lattice_dots_within_3px']:,}/{unique_row['positive_pixels_in_footprint']:,} ({unique_row['lattice_directed_overlap_3px']:.4%}) dots within 3 px of the lattice. Its old <code>promote</code> status and score claim are superseded; no valid HOLDOUT-DTI is reported. Its best overlap against the nine focus-site masks is {unique_row['worst_focus_site_overlap_3px']:.2%} ({esc(unique_row['worst_focus_site_3px'])}), but the complete registry and pre-placement surface are unavailable, so that does not clear it. <a href="{prefix}knowledge/session-review-arena-2b7c50b3.md">Read this session review ↗</a> · <a href="{prefix}knowledge/hypotheses-20261029.md">Review four preregistered hypotheses ↗</a> · <a href="{prefix}evidence/local_downloads_and_peer_audit_20261029.json">{current_audit['local_downloads_count']}-local + {current_audit['peer_rasters_count']}-peer audit JSON ↗</a> · <a href="{prefix}evidence/run_card_arena_2b7c50b3.json">Negative saved-byte run card ↗</a></p>
<p><strong>Additional format irregularity:</strong> <code>karage1-unique-alteration-dots-20261028-zeros.tif</code> has {synthetic_row['outside_unmasked_positive_pixels']:,} unmasked positive pixels outside the competition footprint; it fails the local outside-footprint gate and must not be submitted. <a href="{prefix}evidence/local_downloads_and_peer_audit_20261029.json">See the dated byte audit ↗</a>.</p>
<p><strong>Prior independent review · session 1668dda0:</strong> It audited an earlier 9-local + 9-peer inventory, retracted PR #42's synthetic artifact, quarantined its generator, and hardened format validation. This is historical evidence, not the current inventory. <a href="{prefix}knowledge/session-review-arena-1668dda0.md">Read the 1668dda0 review ↗</a> · <a href="{prefix}evidence/local_downloads_and_peer_audit_20261028.json">Earlier saved-byte audit JSON ↗</a> · <a href="{prefix}evidence/session_1668dda0_run_card.json">Earlier review card ↗</a></p>
<p><strong>Prior session · a1ef4ce0:</strong> The nine-site audit was independently reproduced from pinned bytes; missing baseline-positive counts or pixel-mask evidence fail the automated promotion gate. <a href="{prefix}knowledge/session-review-arena-a1ef4ce0.md">Session a1ef4ce0 review ↗</a> · <a href="{prefix}evidence/session_a1ef4ce0_run_card.json">Session a1ef4ce0 card ↗</a></p>
<div class="decision-actions"><button class="button button-disabled" disabled>No approved .tif to download</button>
<a class="button button-light" href="{prefix}docs/executive-summary.html#audit">Review research-only downloads ↗</a>
<a class="button button-light" href="{prefix}evidence/conduitcrest_lattice_reaudit_20261028.json">Inspect Conduitcrest lattice audit ↗</a>
<a class="button button-light" href="{prefix}evidence/run_card_arena_2b7c50b3.json">Inspect current negative run card ↗</a></div>
<p class="download-help"><strong>Audit-only historical file — DO NOT SUBMIT:</strong> <a href="{prefix}docs/downloads/{quote(Path(unique_hyp['artifact']['file']).name)}">{esc(Path(unique_hyp['artifact']['file']).name)}</a> · SHA-256 <code>{unique_hyp['artifact']['sha256']}</code>. This saved raster is a lattice duplicate; download is for audit/research only. No new TIFF was generated, and no slot was selected or spent.</p></div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative · all audited local TIFs blocked</strong></div><div><span>LEADERBOARD ESTIMATE</span><strong>Unavailable</strong></div><div><span>BB-STEP LATTICE</span><strong>{lat:.2%} · duplicate</strong></div><div><span>CONDUITCREST LATTICE</span><strong>{clat['directed_overlap']:.2%} · duplicate</strong></div><div><span>UNIQUE-HYP LATTICE</span><strong>{unique_row['lattice_directed_overlap_3px']:.2%} · duplicate</strong></div><a href="{prefix}docs/data/current-session-run-card.json">Current session run card ↗</a></div></section>'''


def comparison(prefix: str):
    card = json.loads((DOCS / 'data/run-card.json').read_text())
    dti = card['holdout_dti']
    nine = card['correlation_overlap_vs_registry']['final_dot_overlap_worst_nine']['frac_our_dots_within_3px']
    lat = card['correlation_overlap_vs_registry']['lattice_overlap']
    conduit_audit, conduit_original, latest, conduit_path = conduitcrest_evidence()
    clat = conduit_audit['lattice_witness']
    unique_card = unique_hyp_evidence()
    unique_name = Path(unique_card['artifact']['file']).name
    unique_overlap = unique_card['registry_correlation_overlap']
    conduit_row = (
        f'<tr><th scope="row">GEMSDOEkarage1 (Conduitcrest)</th>'
        f'<td><a class="file-link" href="{prefix}docs/downloads/{quote(conduit_path.name)}">{esc(conduit_path.name)}</a>'
        '<span class="cell-sub">Prior parallel-session research artifact · audit only</span></td>'
        '<td><strong>No reportable HOLDOUT-DTI</strong>'
        '<span class="cell-sub">Legacy scalar retracted · no 95% CI or independent reproduction</span></td>'
        '<td>Unavailable<span class="cell-sub">No organizer estimate</span></td>'
        f'<td><span class="pill pill-red">NO vs lattice</span><span class="cell-sub">{clat["directed_overlap"]:.2%}; 0.0% vs nine focus-site masks</span></td>'
        '<td><span class="pill pill-red">DO NOT SUBMIT</span></td></tr>'
    )
    unique_hyp_row = (
        f'<tr><th scope="row">GEMSDOEkarage1 (historical K/Th + thermal)</th>'
        f'<td><a class="file-link" href="{prefix}docs/downloads/{quote(unique_name)}">{esc(unique_name)}</a>'
        '<span class="cell-sub">Historical saved raster · audit/research only</span></td>'
        '<td><strong>No valid HOLDOUT-DTI</strong>'
        '<span class="cell-sub">Legacy score claim retracted; no current evaluator result</span></td>'
        '<td>Unavailable<span class="cell-sub">No organizer receipt</span></td>'
        f'<td><span class="pill pill-red">NO vs lattice</span><span class="cell-sub">{unique_overlap["lattice"]["directed_overlap"]:.2%}; distinct vs nine focus masks only</span></td>'
        '<td><span class="pill pill-red">DO NOT SUBMIT</span></td></tr>'
    )
    ours = (
        f'<tr><th scope="row">GEMSDOEkarage1</th>'
        f'<td><a class="file-link" href="{prefix}docs/downloads/{quote(card["submission_name"])}">{esc(card["submission_name"])}</a>'
        '<span class="cell-sub">Historical prior-session research artifact · audit only</span></td>'
        f'<td><strong>{dti["value"]:.4f}</strong><span class="cell-sub">HOLDOUT-DTI · {esc(dti["evaluator_version"])} · n={dti["withheld_positives"]:,} · 95% CI [{dti["ci95"][0]:.4f}, {dti["ci95"][1]:.4f}]</span></td>'
        '<td>Unavailable<span class="cell-sub">No organizer forecast</span></td>'
        f'<td><span class="pill pill-red">NO vs lattice</span><span class="cell-sub">Yes vs 9 sites ({nine:.1%}); lattice {lat:.1%}</span></td>'
        '<td><span class="pill pill-red">DO NOT SUBMIT</span></td></tr>'
    )
    return f'''<section class="section comparison" id="comparison"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> DOWNLOAD TABLE</p><h2>Which file, which number, unique or not.</h2><p>Any displayed score is labeled HOLDOUT-DTI with evaluator, withheld-positive count, and 95% CI, or USER-REPORTED / UNVERIFIED. Retracted or incomplete legacy score assertions are not shown as numbers. No projection is written as a score. The generated BB-STEP file is unique versus the nine listed GEMSDOE sites and is still a lattice duplicate under the parallel-run rule.</p></div></div>
<div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table →</div><div class="table-scroll" tabindex="0" role="region" aria-label="Nine focus sites and historical candidate artifacts"><table><thead><tr><th>Site or artifact</th><th>File (research only unless separately cleared)</th><th>Reportable score</th><th>Organizer-confirmed score</th><th>Unique?</th><th>Action</th></tr></thead><tbody>{ours}{conduit_row}{unique_hyp_row}
{rows_for(prefix)}</tbody></table></div></div></section>'''


def home(depth=0):
    p = '../' * depth
    local_audit = local_and_peer_evidence()
    tracked_inventory = local_audit['tracked_tiff_inventory']
    return f'''<div class="page-top"><span>GEMS PRIZE <span class="separator">/</span> DECISION BRIEF</span><span class="page-date">INDEPENDENT AUDIT · 29 OCT 2026</span></div>
<section class="hero compact-hero"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-line"></span> EVIDENCE BEFORE A LEADERBOARD SLOT</p><h1>Find faults.<br><em>Protect every submission.</em></h1><p class="hero-description">A clear, auditable workspace for fault discovery in the Great Basin. We separate format checks, scientific evidence, uniqueness and actual portal acceptance.</p><div class="hero-actions"><a class="text-link" href="#comparison">Compare the nine sites ↓</a><a class="subtle-link" href="{p}docs/research.html">Explore the research ↗</a></div></div>
<div class="terrain-card terrain-small" aria-label="Illustrative contour artwork, not a prediction map"><div class="terrain-top"><span>GEO<span class="terrain-dot">●</span>DAWN</span><span>FIELD NOTE / 01</span></div><svg class="terrain-lines" viewBox="0 0 620 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.5"><path d="M-50 10C90 25 95 155 200 110S305-10 410 55s150 110 250 40"/><path d="M-50 35C80 50 100 180 205 135S310 15 410 80s150 110 250 40"/><path d="M-50 60C70 75 105 205 210 160S315 40 410 105s150 110 250 40"/><path d="M-50 85C60 100 110 230 215 185S320 65 410 130s150 110 250 40"/><path d="M-50 110C50 125 115 255 220 210S325 90 410 155s150 110 250 40"/><path d="M-50 135C40 150 120 280 225 235S330 115 410 180s150 110 250 40"/><path d="M-50 160C30 175 125 305 230 260S335 140 410 205s150 110 250 40"/></g><g class="terrain-focus" fill="none"><circle cx="379" cy="139" r="40"/><circle cx="379" cy="139" r="26"/><path d="M379 89v100M329 139h100"/></g></svg><div class="terrain-caption"><span><b>THE STUDY AREA</b><br>Western Great Basin</span><span>NEVADA + CALIFORNIA<br><b>CONCEPTUAL ONLY</b></span></div></div></section>
{decision(p)}<section class="snapshot" aria-label="Evidence snapshot"><div class="snapshot-item"><div class="snapshot-label">LIVE LEADERBOARD</div><div class="snapshot-value">NOT VERIFIED</div><p>No authenticated refresh or receipt is stored; this site is not a live leaderboard feed. <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Check the official page ↗</a></p></div><div class="snapshot-item"><div class="snapshot-label">CURRENT TIFF AUDIT</div><div class="snapshot-value">{local_audit['local_downloads_count']} <span class="snapshot-context">local files</span></div><p>{local_audit['peer_rasters_count']} pinned peers checked; all {tracked_inventory['tracked_tiff_paths_count']} tracked TIFF paths ({tracked_inventory['unique_tracked_tiff_sha256_count']} unique byte hashes) are accounted. Four archive paths remain quarantined; no TIFF is cleared.</p></div><div class="snapshot-item"><div class="snapshot-label">THIS SESSION</div><div class="snapshot-value">NO MODEL RUN</div><p>Zero geological experiments; no holdout, TIFF generation, or selector action.</p></div><div class="snapshot-item"><div class="snapshot-label">SUBMISSION STATUS</div><div class="snapshot-value">DO NOT SUBMIT</div><p>No current candidate is authorized; feature stack and lane are unavailable.</p></div></section>
{comparison(p)}<section class="section detail-grid"><div><p class="eyebrow"><span class="eyebrow-line"></span> THE B2 QUESTION</p><h2>What made the reported leader different?</h2></div><div class="prose-card"><p>On the audited mirrored grid, GEMSDOE32 B2 is exactly GEMSDOE25's d2.8 mask with 6,436 dots within two pixels of the mirrored known-fault catalogue removed; no new dots were added. GEMSDOE25 and GEMSDOE30 have the same positive-pixel mask.</p><p>Reducing redundant prediction mass <em>could</em> improve the distance-weighted Tversky tradeoff, but it can also remove true coverage. Hidden labels and an artifact-linked receipt are unavailable, so the cause and any improvement over the reported result remain unproven.</p><p>Known fault pixels are masked, but nearby new faults may still matter. A catalogue buffer is not automatically a free scoring exclusion. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">DrivenData staff clarification ↗</a></p><a class="text-link" href="{p}docs/research.html#b2">Read the scientific analysis ↗</a></div></section>
<section class="next-strip"><div><p class="eyebrow">NEXT STEPS</p><h2>Resolve the lattice gate before spending a slot.</h2><p>BB-STEP is unique versus the nine listed sites and still a lattice duplicate. Do not jitter dots to evade the rule. No automatic DrivenData scraping or upload.</p></div><a class="button button-dark" href="{p}docs/executive-summary.html">See the checklist ↗</a></section>'''


def guide(depth=1):
    p = '../' * depth
    _, _, _, audit, _ = evidence()
    current_audit = local_and_peer_evidence()
    tracked_inventory = current_audit['tracked_tiff_inventory']
    unique_card = unique_hyp_evidence()
    cand = audit['candidates']
    card = json.loads((DOCS / 'data/run-card.json').read_text())
    cards = [f'''<article class="audit-card"><p class="eyebrow">PRIOR PARALLEL-SESSION ARTIFACT · BB-STEP</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(card['submission_name'])}</code></p><p>SHA-256 <code class="wrap">{card['raster_sha256']}</code></p><p>17,766 dots. Unique vs nine focus sites (worst 3-px overlap 12.6%, |Spearman| 0.085). Lattice overlap 98.53% · literal duplicate. Inside footprint finite and in [0,1]; CRS/shape/transform match the mirrored sample. Zeros-outside and NaN-outside twins both written. Portal acceptance is untested.</p><p>Name <code>KARAGE1-BBSTEP-72312302675D</code> · note: <code>{esc(card['submission_note'])}</code></p><a class="text-link" href="{p}docs/downloads/{quote(card['submission_name'])}" download>Download for research only ↗</a></article>''']
    conduit_audit, conduit_original, latest, conduit_path = conduitcrest_evidence()
    clat = conduit_audit['lattice_witness']
    chdt = conduit_audit['previous_holdout_claim']
    cards.append(f'''<article class="audit-card"><p class="eyebrow">LATER MAINLINE ARTIFACT · CONDUITCREST</p><h3>DO NOT SUBMIT · LATTICE DUPLICATE</h3><p><strong>Research only; not a submission recommendation.</strong></p><p><code class="wrap">{esc(conduit_path.name)}</code></p><p>SHA-256 <code class="wrap">{conduit_audit['candidate']['sha256']}</code></p><p>{clat['candidate_dots']:,} dots; {clat['candidate_dots_within_closed_3px_disk']:,} ({clat['directed_overlap']:.4%}) within 3 px of the pinned lattice. This exceeds the literal 70% stop rule. It was unique only versus the nine focus-site files; its prior run card omitted the lattice and a pre-placement lattice check.</p><p>The previous scalar is retracted from current reporting: its old card has no 95% CI and no independent reproduction is bound to this saved TIFF. <strong>No HOLDOUT-DTI score is reportable.</strong></p><a class="text-link" href="{p}docs/downloads/{quote(conduit_path.name)}" download>Download for audit only ↗</a> · <a class="text-link" href="{p}evidence/conduitcrest_lattice_reaudit_20261028.json">Reaudit JSON ↗</a></article>''')
    for label, c in zip(('HMAS-SINTER', 'GPC-Z'), cand):
        row = c['comparisons'][0]
        cards.append(f'''<article class="audit-card"><p class="eyebrow">HISTORICAL ARTIFACT · {label}</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(c['file'])}</code></p><p>SHA-256 <code class="wrap">{c['sha256']}</code></p><p>{row['candidate_dots_within_3px']:,} / {row['candidate_dots']:,} dots within 3 px of lattice ({row['directed_overlap']:.2%}) · duplicate. Mirror-grid and inside [0,1] checks pass; null/NaN-outside check fails. Portal acceptance is untested.</p><a class="text-link" href="{p}docs/downloads/{quote(c['file'])}" download>Download for research only ↗</a></article>''')
    u_lat = unique_card['registry_correlation_overlap']['lattice']
    u_focus = unique_card['registry_correlation_overlap']['nine_focus_sites']
    unique_name = Path(unique_card['artifact']['file']).name
    cards.append(f'''<article class="audit-card"><p class="eyebrow">HISTORICAL K/TH + THERMAL ARTIFACT · REASSESSMENT 29 OCT</p><h3>DO NOT SUBMIT · LATTICE DUPLICATE</h3><p><strong>Research only, for audit; not an approved submission.</strong></p><p><code class="wrap">{esc(unique_name)}</code></p><p>SHA-256 <code class="wrap">{unique_card['artifact']['sha256']}</code></p><p>{u_lat['candidate_dots_within_closed_3px_disk']:,}/{u_lat['candidate_dots']:,} ({u_lat['directed_overlap']:.4%}) candidate dots are within 3 px of the pinned lattice; literal duplicate. It is distinct from the nine focus-site masks only under this bounded binary-mask check (worst directed overlap {u_focus['worst_directed_3px_overlap']:.2%}, |Spearman| ≤ {u_focus['maximum_absolute_spearman']:.5f}). Complete registry and pre-placement surface are unavailable.</p><p><strong>No valid HOLDOUT-DTI is reported.</strong> The legacy score claim and <code>promote</code> verdict were retracted; no reproducible evaluator output is bound to these saved bytes in the committed evidence.</p><p>Local format diagnostics: inside values finite and in [0,1], whole-array finite variant passes; outside-null/NaN variant fails because the file uses zeros outside. Organizer acceptance is untested.</p><a class="text-link" href="{p}docs/downloads/{quote(unique_name)}">Download for audit only — DO NOT SUBMIT ↗</a> · <a class="text-link" href="{p}evidence/run_card_arena_2b7c50b3.json">Reassessment JSON ↗</a></article>''')
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> EXECUTIVE SUMMARY</span><span class="page-date">REVIEWED 29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> THE SUBMISSION CHECKLIST</p><h1>One file. <em>Evidence first.</em></h1><p>What to submit, when—and why today's answer is no.</p></section>{decision(p)}
<section class="section" id="audit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> SAVED-BYTE CHECK</p><h2>All {current_audit['local_downloads_count']} local download GeoTIFFs and {current_audit['peer_rasters_count']} audited peer GeoTIFFs fail the literal lattice gate; none cleared.</h2><p>Research downloads are explicitly not submission recommendations. Uniqueness versus the nine focus sites is not uniqueness versus the lattice or a complete fleet registry.</p></div></div><div class="audit-grid">{''.join(cards)}</div><p class="body-copy">The dated 29 October saved-byte report covers every current local download TIFF ({current_audit['local_downloads_count']} files) plus {current_audit['peer_rasters_count']} SHA-pinned peer rasters; every one exceeds the literal 3-px lattice-overlap threshold. A separate exact-byte reconciliation accounts for all {tracked_inventory['tracked_tiff_paths_count']} Git-tracked TIFF paths ({tracked_inventory['unique_tracked_tiff_sha256_count']} unique byte hashes): {tracked_inventory['tracked_download_directory_paths_count']} download-directory paths and {tracked_inventory['tracked_quarantined_archive_paths_count']} quarantined archive paths. No archived artifact is authorized either. This bounded audit is not proof that the registry is complete or that any file is accepted by the organizer. <a href="{p}evidence/local_downloads_and_peer_audit_20261029.json">Inspect the current full inventory audit ↗</a> · <a href="{p}docs/data/archive-review.json">Inspect the quarantined archive audit ↗</a>.</p><p class="body-copy">The prior 9-local + 9-peer audit from session <code>1668dda0</code> remains historical and is not the current inventory. The K/Th+thermal file above is separately reassessed against the lattice and nine focus-site masks; its complete-registry uniqueness, pre-placement surface, mechanism, and legacy score claim remain unverified. <a href="{p}evidence/local_downloads_and_peer_audit_20261028.json">Inspect the earlier 18-raster audit ↗</a> · <a href="{p}evidence/run_card_arena_2b7c50b3.json">Inspect the superseding negative card ↗</a>.</p><p class="body-copy">The official <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format">format description</a> says data outside the bounds should be null or NaN. A strict all-finite check and a null/NaN-outside check are different diagnostics; neither establishes actual portal acceptance. The historical file uses zeros outside, so the null/NaN-outside variant fails even though its strict finite [0,1] diagnostic passes.</p></section>
{comparison(p)}<section class="section" id="steps"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> FOR A FUTURE CLEARED CANDIDATE</p><h2>How to submit, once eligible.</h2><p>These steps are not permission to upload either historical artifact.</p></div></div><div class="steps-grid"><article><span>01 / EVIDENCE</span><h3>Pass the automated gates</h3><p>Use the shared evaluator, fold-local features and per-feature canaries. Beat a frozen comparable holdout best; audit surface and dots against the complete registry; reopen the TIFF and validate saved bytes.</p></article><article><span>02 / SELECTOR</span><h3>Choose a slot separately</h3><p>Only an independent selector may choose an eligible candidate and check the current allowance on the authenticated submission page. The current cap was not verified in this session.</p></article><article><span>03 / DOWNLOAD</span><h3>Choose the exact file</h3><p>Download the approved single-band GeoTIFF (or a ZIP containing one GeoTIFF). Check its displayed SHA-256, unique name and note of at most 140 characters.</p></article><article><span>04 / UPLOAD</span><h3>Use the official form</h3><p>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData</a>, select Submit → Make new submission, choose the .tif or ZIP, and paste the note. Retain the file-linked organizer receipt.</p></article></div><div class="notice guide-notice"><span aria-hidden="true">ⓘ</span><p>The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> require disclosure of generative-AI use in the narrative when applicable. Public leaderboard performance is not the private final score.</p></div></section>'''


def research(depth=1):
    p = '../' * depth
    tracked_inventory = local_and_peer_evidence()['tracked_tiff_inventory']
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> RESEARCH</span><span class="page-date">REVIEWED 29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SCIENCE BEFORE SCORING</p><h1>Understand the ground.<br><em>Respect the unknown.</em></h1><p>The target is previously unmapped geological faults—not proof of a geothermal vent.</p></section>
<section class="notice"><span aria-hidden="true">ⓘ</span><p><strong>Current status:</strong> zero geological experiments and zero holdouts this session. The method lane, canonical template assignment, and required organizer feature stack are unavailable. Exact-SHA review accounts for all {tracked_inventory['tracked_tiff_paths_count']} Git-tracked TIFF paths ({tracked_inventory['unique_tracked_tiff_sha256_count']} unique byte hashes); four archive paths remain quarantined and no file is cleared. No current leaderboard refresh was authenticated; this site is not a live feed. Candidate hypotheses below are proposals only, with qualitative value/cost ranking and no DTI projection.</p></section>
<section class="section detail-grid" id="b2"><div><p class="eyebrow"><span class="eyebrow-line"></span> WHAT THE MIRRORED BYTES SHOW</p><h2>Why B2 may have differed.</h2></div><div class="prose-card"><p>Binary-mask algebra on the hash-pinned mirrors shows GEMSDOE25 and GEMSDOE30 share a 44,090-dot parent mask. GEMSDOE32 B2 is a subset after removing 6,436 dots within two pixels of the mirrored known-fault catalogue; it adds no new dots. GEMSDOE31 and GEMSDOE28 h27-4-r1 are a milder one-pixel collar-ablation variant that removes 3,891 dots. GEMSDOE36 adds 1,200 off-catalogue dots to the B2-sized mask.</p><p>The associated values—0.2708, 0.2778 for GEMSDOE32 B2, and 0.2750—are <strong>USER-REPORTED / UNVERIFIED context only</strong>: no artifact-linked organizer receipt or reproducible HOLDOUT-DTI report with evaluator, withheld-positive count, and 95% CI was verified in this review. They are not presented as validated scores.</p><p>A collar ablation could alter a distance-weighted Tversky tradeoff if the saved false-positive penalty outweighs recall lost near known faults. It could also remove real target coverage. Mask algebra explains the difference in the masks, not why a reported score changed or whether the reported ranking is real. A catalogue buffer is not automatically a free scoring exclusion. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">Review the DrivenData staff clarification ↗</a></p><p>Earlier work reported raw float32 nodata inside the footprint in a mirrored <code>training_features.tif</code>; that is a historical mirror observation, not a current organizer-file check. Inference must follow the assigned template’s exact mask, not assume all finite cells are valid.</p><a class="text-link" href="{p}knowledge/session-review-arena-9ca08e2e.md">Read the earlier mask-algebra and feature audit ↗</a></div></section>
<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> PRE-IMPLEMENTATION HYPOTHESES</p><h2>Four proposals; none assigned or run.</h2><p>The checkout search found no matching implementation for these exact tests; this is not proof of fleet-wide novelty. Rank combines qualitative potential for pooled DTI improvement and implementation cost—not a score forecast. The first candidate is adjacent to an older signed-offset idea, so it is not claimed as a wholly independent lane.</p><a class="text-link" href="{p}knowledge/hypotheses-20261029.md">Full layers, physical signatures, mimics, source-access checks, and blockers ↗</a></div></div><div class="hypothesis-grid">
<article class="hypothesis-card"><span class="hypothesis-rank">01 <span>TOP PROPOSAL · MEDIUM COST</span></span><h3>Cross-spectral potential-field junctions</h3><p>Test multi-wavelength phase coherence and shared edge normals between GeoDAWN magnetics, isostatic gravity, and basement-depth gradients. Buried fault steps may persist under cover without a surface trace.</p><div><b>Named mimic:</b> intrusive/lithologic contacts, volcanic boundaries, or survey seams.</div><small>Potential: highest qualitative in this slate; no measured uplift. Adds cross-field phase congruence and junction topology beyond existing amplitude/gradient ridges. Requires the missing organizer stack and assigned lane.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">02 <span>HIGH COST</span></span><h3>Joint density–susceptibility interface inversion</h3><p>Fit a low-complexity shared faulted-basement interface to gravity and magnetic observations with separate physical contrasts and explicit uncertainty.</p><div><b>Named mimic:</b> volcanic body, lithologic contact, or multiple-source superposition.</div><small>Potential: medium qualitative, high non-uniqueness risk. Distinct from current derivative/edge features; requires synthetic recovery and shared holdout.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">03 <span>HIGH DATA COST · NOT VIABLE YET</span></span><h3>Stratigraphic-contact offset consistency</h3><p>Reward displacement or truncation of a mapped unit contact—not the contact itself—where it independently aligns with geophysical structure.</p><div><b>Named mimic:</b> erosional unconformity, depositional pinch-out, or cartographic boundary.</div><small>Potential: low-to-medium qualitative; high data cost. <a href="https://ngmdb.usgs.gov/">USGS National Geologic Map Database</a> is the official source to check, but coverage, vector downloads, license, and grid registration were not verified here; not data-ready.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">04 <span>HIGH COST · NOT VIABLE YET</span></span><h3>Inter-catchment knickpoint recurrence</h3><p>Test whether area-normalized channel-breaks recur at a common basement position across adjacent catchments, rather than scoring a single scarp.</p><div><b>Named mimic:</b> resistant-bed contact, stream capture, fan incision, or pluvial shoreline bench.</div><small>Potential: low-to-medium qualitative; high cost. <a href="https://www.usgs.gov/3d-elevation-program">USGS 3DEP</a> tile coverage and payload access were not verified; the earlier drainage-asymmetry concept makes lane novelty uncertain.</small></article></div></section>
<section class="section" id="sources"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> TRACEABLE REFERENCES</p><h2>Review the official source.</h2><p>Links are pointers for manual review, not proof that a specific payload is available, complete, or authenticated in this checkout.</p></div></div><div class="source-list"><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"><span><b>DrivenData · problem and metric</b><small>Target, features, score, and format</small></span><span>OFFICIAL ↗</span></a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/"><span><b>DrivenData · competition data tab</b><small>Account access not attempted in this review</small></span><span>OFFICIAL ↗</span></a><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf"><span><b>DOE / NLR · rules</b><small>Submission limits, eligibility, and disclosure</small></span><span>OFFICIAL ↗</span></a><a href="https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and"><span><b>USGS · GeoDAWN</b><small>Magnetic and radiometric data description</small></span><span>OFFICIAL ↗</span></a><a href="https://www.usgs.gov/3d-elevation-program"><span><b>USGS · 3DEP</b><small>External elevation source; exact tiles not verified</small></span><span>OFFICIAL ↗</span></a><a href="https://ngmdb.usgs.gov/"><span><b>USGS · National Geologic Map Database</b><small>External map source; coverage not verified</small></span><span>OFFICIAL ↗</span></a><a href="https://gdr.openei.org/submissions/1391"><span><b>GDR · INGENIOUS</b><small>Third-party evidence requires independent provenance review</small></span><span>REVIEW ↗</span></a><a href="https://github.com/drivendataorg/gems-prize-reference-solution"><span><b>DrivenData · reference implementation</b><small>Organizer-provided starting point</small></span><span>CODE ↗</span></a><a href="{p}evidence/run_card_arena_2b7c50b3.json"><span><b>Current negative audit card</b><small>Saved-byte assessment; no holdout or submission authorized</small></span><span>REVIEW ↗</span></a></div></section>'''


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
    unique_hyp_evidence()
    conduitcrest_evidence()
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
