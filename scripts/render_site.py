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

    def load_receipt(path: Path):
        return json.loads(
            path.read_text(encoding='utf-8'),
            parse_constant=_reject_const,
            object_pairs_hook=_unique_obj,
        )

    historical = load_receipt(ROOT / 'evidence/local_downloads_and_peer_audit_20261028.json')
    if (historical.get('schema') != 'karage1-local-and-peer-audit-v1'
            or historical.get('submit_authorized') is not False
            or historical.get('local_downloads_count') != 9
            or historical.get('peer_rasters_count') != 9
            or len(historical.get('local_downloads', [])) != 9
            or len(historical.get('peer_rasters', [])) != 9):
        raise ValueError('Historical 2026-10-28 local/peer receipt is missing or changed')
    for row in historical['local_downloads']:
        p = ROOT / row['file']
        if not p.is_file() or p.stat().st_size != row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError(f'Historical local bytes drifted from preserved receipt: {row["file"]}')

    data = load_receipt(ROOT / 'evidence/local_downloads_and_peer_audit_20261029.json')
    local_rows, peer_rows = data.get('local_downloads'), data.get('peer_rasters')
    actual_tifs = {f'docs/downloads/{p.name}' for p in (ROOT / 'docs/downloads').glob('*.tif')}
    audited_tifs = {row.get('file') for row in local_rows or []}
    if (data.get('schema') != 'karage1-local-and-peer-audit-v1'
            or data.get('submit_authorized') is not False
            or data.get('all_local_downloads_blocked') is not True
            or data.get('all_audited_peer_rasters_exceed_70pct_lattice') is not True
            or data.get('local_downloads_count') != len(local_rows or [])
            or data.get('peer_rasters_count') != len(peer_rows or [])
            or data.get('local_downloads_count') != 11
            or data.get('peer_rasters_count') != 9
            or audited_tifs != actual_tifs
            or f"All {len(actual_tifs)} local docs/downloads/*.tif artifacts" not in data.get('scope', '')
            or len(data.get('immutable_ecosystem_repos', [])) != 22):
        raise ValueError('Current local-downloads / peer audit missing, stale, or not fail-closed')
    for row in (*local_rows, *peer_rows):
        if row.get('ok_to_submit') is not False or row.get('literal_lattice_duplicate') is not True:
            raise ValueError(f'Blocked audit invariant violated for {row}')
    for row in local_rows:
        p = ROOT / row['file']
        if not p.is_file() or p.stat().st_size != row['bytes'] or hashlib.sha256(p.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError(f'Local download bytes drifted from audited receipt: {row["file"]}')
    kth = next((r for r in local_rows if r['file'].endswith('unique-hyp-kth-therm-mask-20261028-zeros.tif')), None)
    if (kth is None or kth['sha256'] != 'a18e8fea158c2c53357b2d9651a6ce874b6329f1fdff690b4e17e8b0bb6a75eb'
            or kth['lattice_dots_within_3px'] != 37617
            or kth['positive_pixels_in_footprint'] != 37654
            or kth['literal_lattice_duplicate'] is not True):
        raise ValueError('KTH historical candidate no longer matches its fail-closed saved-byte audit')
    kth_card = json.loads((ROOT / 'evidence/kth_candidate_audit_20261029.json').read_text(),
                          parse_constant=_reject_const, object_pairs_hook=_unique_obj)
    if (kth_card.get('candidate_sha256') != kth['sha256']
            or kth_card.get('verdict') != 'negative' or kth_card.get('ok_to_submit') is not False
            or kth_card.get('holdout_DTI', {}).get('value') is not None
            or kth_card.get('legacy_claim_classification') != 'LEGACY-UNVERIFIED CLAIM; not accepted as a HOLDOUT-DTI result'):
        raise ValueError('KTH candidate summary is stale, score-mislabeled, or not fail-closed')
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
        worst_pair = max(
            (v['overlap_fraction'], k.split('->')[1])
            for k, v in ref['directed_pairs'].items() if k.startswith(name + '->')
        )
        rows.append(
            f'<tr><th scope="row"><a href="{prefix}docs/{name}.html">{esc(name)} ↗</a></th>'
            f'<td><a class="file-link" href="{esc(artifact_url(entry), quote=True)}">{esc(filename)}</a>'
            '<span class="cell-sub">Strongest supplied historical file · research only</span></td>'
            f'<td><strong>{claim["reported_score"]:.4f}</strong><span class="cell-sub">USER-REPORTED / UNVERIFIED</span></td>'
            '<td>Unavailable<span class="cell-sub">No defensible forecast. No organizer-confirmed score or projection</span></td>'
            f'<td><span class="pill pill-red">NO</span><span class="cell-sub">lattice {measured["lattice_directed_overlap"]:.2%}; '
            f'worst focus pair {esc(worst_pair[1])} {worst_pair[0]:.2%}; both exceed 70%</span></td>'
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
    audit_card = p + 'evidence/session_73de02e3_run_card.json'
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
<main id="main"><div class="container">{body}</div></main><footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div><div class="footer-links"><a href="{audit_card}">Current review card</a><a href="{doc}research.html">Research</a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition ↗</a></div><div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with the organizers.</span></div></div></footer></body></html>'''


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
    current = local_and_peer_evidence()
    kth = next(r for r in current['local_downloads'] if r['file'].endswith('unique-hyp-kth-therm-mask-20261028-zeros.tif'))
    kth_card = json.loads((ROOT / 'evidence/kth_candidate_audit_20261029.json').read_text())
    legacy_claim = kth_card['legacy_holdout_claim']
    kth_overlap = kth['lattice_directed_overlap_3px']
    return f'''<section class="decision-panel" aria-labelledby="decision-title"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT SUBMISSION DECISION <span class="status-tag">DO NOT SUBMIT</span></div>
<h2 id="decision-title">No eligible submission file. All 11 local downloads and 9 pinned peers fail the lattice stop.</h2><p><strong>No GeoTIFF is cleared for upload; no approved .tif is available.</strong> This review generated no raster, ran no geological experiment, and selected or spent no slot.</p>
<p><strong>Fresh saved-byte audit · 29 Oct 2026:</strong> all {current['local_downloads_count']} local <code>docs/downloads/*.tif</code> files and all {current['peer_rasters_count']} peer rasters exceed the literal &gt;70% 3-pixel lattice-overlap stop rule. The SHA-pinned inputs come from {len(current['immutable_ecosystem_repos'])} GitHub-mirror repository commits; this is not organizer authentication or a complete registry. <a href="{prefix}evidence/local_downloads_and_peer_audit_20261029.json">Inspect the current 11-local + 9-peer receipt ↗</a>.</p>
<p><strong>K/Th + thermal legacy TIFF:</strong> <code class="wrap">unique-hyp-kth-therm-mask-20261028-zeros.tif</code> has {kth['positive_pixels_in_footprint']:,} positive pixels; {kth['lattice_dots_within_3px']:,} ({kth_overlap:.4%}) fall within 3 px of the pinned lattice. The final-dot literal duplicate gate fails. No pre-placement surface is available, so uniqueness is not certified. Its old sidecar's {esc(str(legacy_claim['holdout_DTI']))} is a <strong>LEGACY-UNVERIFIED claim—not an accepted HOLDOUT-DTI measurement</strong>; the old script also overrode its gate. <a href="{prefix}evidence/kth_candidate_audit_20261029.json">Current KTH audit ↗</a> · <a href="{prefix}evidence/legacy_kth_claim_quarantine_20261029.json">Preserved superseded claim ↗</a>.</p>
<p>The prior BB-STEP research file <code class="wrap">{esc(card['submission_name'])}</code> is unique versus the nine focus sites (worst overlap {nine:.1%}) but has {lat:.2%} lattice overlap; it is a duplicate. Its prior-session <strong>HOLDOUT-DTI {dti['value']:.5f}</strong> (95% CI [{dti['ci95'][0]:.5f}, {dti['ci95'][1]:.5f}]; evaluator {esc(dti['evaluator_version'])}; {dti['withheld_positives']:,} withheld positives). This is not an organizer score and does not override the duplicate stop.</p>
<p>The Conduitcrest research file has {clat['candidate_dots']:,} dots; {clat['candidate_dots_within_closed_3px_disk']:,} ({clat['directed_overlap']:.4%}) are within 3 px of the pinned lattice, exceeding the 70% threshold. Its old card's incomplete HOLDOUT-DTI claim ({chdt['reported_value']:.6f}; evaluator {esc(chdt['evaluator_version'])}; {chdt['withheld_positives']:,} withheld positives) has <strong>no 95% CI</strong> and is not a release-grade result. HMAS / GPC-Z also fail the lattice gate ({ar['directed_overlap']:.2%} and {br['directed_overlap']:.2%}).</p>
<p><strong>Leaderboard context is unresolved:</strong> prompt passages conflict between 0.3195 and 0.4413; an older repository snapshot says 0.4544. All are <strong>USER-REPORTED / UNVERIFIED or stale repository context</strong>; no live organizer value or receipt was authenticated. None is a current score, projection, or confirmed ranking. <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Official leaderboard page ↗</a> (not authenticated in this review).</p>
<p><strong>Next review:</strong> three novelty-screened hypotheses are qualitative proposals only; no assigned lane or official data payload was available, so none was tested. <a href="{prefix}knowledge/session-review-arena-73de02e3.md#novelty-screened-hypotheses">Read the ranked hypothesis screen ↗</a> · <a href="{prefix}knowledge/session-review-arena-73de02e3.md">Three-pass review and limitations ↗</a>.</p>
<div class="decision-actions"><button class="button button-disabled" disabled>No approved .tif to download</button>
<a class="button button-light" href="{prefix}docs/executive-summary.html#audit">Review research-only downloads ↗</a>
<a class="button button-light" href="{prefix}evidence/conduitcrest_lattice_reaudit_20261028.json">Inspect Conduitcrest lattice audit ↗</a>
<a class="button button-light" href="{prefix}evidence/bbstep_uniqueness.json">Inspect BB-STEP uniqueness ↗</a>
<a class="button button-light" href="{prefix}evidence/session_73de02e3_run_card.json">Current review card ↗</a></div>
<p class="download-help">Conduitcrest research file (audit only): <a href="{prefix}docs/downloads/{quote(conduit_path.name)}">{esc(conduit_path.name)}</a> · SHA-256 <code>{conduit_audit['candidate']['sha256']}</code>. Not approved for submission. The separate selector and weekly cap remain untouched.</p></div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative · no file cleared</strong></div><div><span>LEADERBOARD VALUE</span><strong>Conflicting · unverified</strong></div><div><span>CURRENT LOCAL AUDIT</span><strong>{current['local_downloads_count']} blocked</strong></div><div><span>KTH LATTICE OVERLAP</span><strong>{kth_overlap:.2%} · duplicate</strong></div><a href="{prefix}evidence/kth_candidate_audit_20261029.json">Current saved-byte audit ↗</a></div></section>'''

def comparison(prefix: str):
    return f'''<section class="section comparison" id="comparison"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> NINE-SITE EXECUTIVE TABLE</p><h2>Strongest supplied file, evidence label, uniqueness, action.</h2><p>These are historical research files, not recommended submissions. Reported values are USER-REPORTED / UNVERIFIED; no organizer-confirmed score or projection is supplied. The measured uniqueness scope is the nine focus files plus the pinned lattice—not a complete official registry.</p></div></div>
<div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table →</div><div class="table-scroll" tabindex="0" role="region" aria-label="Nine-site comparison"><table><thead><tr><th>Site</th><th>Strongest supplied historical file (research only)</th><th>Score evidence</th><th>Organizer-confirmed score</th><th>Unique?</th><th>Action</th></tr></thead><tbody>{rows_for(prefix)}</tbody></table></div></div></section>'''

def home(depth=0):
    p = '../' * depth
    return f'''<div class="page-top"><span>GEMS PRIZE <span class="separator">/</span> DECISION BRIEF</span><span class="page-date">INDEPENDENT AUDIT · 29 OCT 2026</span></div>
<section class="hero compact-hero"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-line"></span> EVIDENCE BEFORE A LEADERBOARD SLOT</p><h1>Find faults.<br><em>Protect every submission.</em></h1><p class="hero-description">A clear, auditable workspace for fault discovery in the Great Basin. We separate format checks, scientific evidence, uniqueness and actual portal acceptance.</p><div class="hero-actions"><a class="text-link" href="#comparison">Compare the nine sites ↓</a><a class="subtle-link" href="{p}docs/research.html">Explore the research ↗</a></div></div>
<div class="terrain-card terrain-small" aria-label="Illustrative contour artwork, not a prediction map"><div class="terrain-top"><span>GEO<span class="terrain-dot">●</span>DAWN</span><span>FIELD NOTE / 01</span></div><svg class="terrain-lines" viewBox="0 0 620 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.5"><path d="M-50 10C90 25 95 155 200 110S305-10 410 55s150 110 250 40"/><path d="M-50 35C80 50 100 180 205 135S310 15 410 80s150 110 250 40"/><path d="M-50 60C70 75 105 205 210 160S315 40 410 105s150 110 250 40"/><path d="M-50 85C60 100 110 230 215 185S320 65 410 130s150 110 250 40"/><path d="M-50 110C50 125 115 255 220 210S325 90 410 155s150 110 250 40"/><path d="M-50 135C40 150 120 280 225 235S330 115 410 180s150 110 250 40"/><path d="M-50 160C30 175 125 305 230 260S335 140 410 205s150 110 250 40"/></g><g class="terrain-focus" fill="none"><circle cx="379" cy="139" r="40"/><circle cx="379" cy="139" r="26"/><path d="M379 89v100M329 139h100"/></g></svg><div class="terrain-caption"><span><b>THE STUDY AREA</b><br>Western Great Basin</span><span>NEVADA + CALIFORNIA<br><b>CONCEPTUAL ONLY</b></span></div></div></section>
{decision(p)}<section class="snapshot" aria-label="Evidence snapshot"><div class="snapshot-item"><div class="snapshot-label">LIVE LEADERBOARD VALUE</div><div class="snapshot-value">UNVERIFIED</div><p>Conflicting user/repo snapshots: 0.3195, 0.4413, 0.4544. No current organizer value authenticated · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">official page ↗</a></p></div><div class="snapshot-item"><div class="snapshot-label">BEST SUPPLIED NINE-SITE REPORT</div><div class="snapshot-value">0.2778</div><p>GEMSDOE32 · USER-REPORTED / UNVERIFIED</p></div><div class="snapshot-item"><div class="snapshot-label">CURRENT AUDIT SCOPE</div><div class="snapshot-value">11 + 9</div><p>Local and pinned peer rasters · every audited file blocked by lattice gate</p></div><div class="snapshot-item"><div class="snapshot-label">NEW EXPERIMENTS THIS REVIEW</div><div class="snapshot-value">0</div><p>No assigned lane or authorized template; no slot selected or spent</p></div></section>
{comparison(p)}<section class="section detail-grid"><div><p class="eyebrow"><span class="eyebrow-line"></span> THE B2 QUESTION</p><h2>What made the reported leader different?</h2></div><div class="prose-card"><p>On the audited mirrored grid, GEMSDOE32 B2 is exactly GEMSDOE25's d2.8 mask with 6,436 dots within two pixels of the mirrored known-fault catalogue removed; no new dots were added. GEMSDOE25 and GEMSDOE30 have the same positive-pixel mask.</p><p>Reducing redundant prediction mass <em>could</em> improve the distance-weighted Tversky tradeoff, but it can also remove true coverage. Hidden labels and an artifact-linked receipt are unavailable, so the cause and any improvement over the reported result remain unproven.</p><p>Known fault pixels are masked, but nearby new faults may still matter. A catalogue buffer is not automatically a free scoring exclusion. <a href="https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516">DrivenData staff clarification ↗</a></p><a class="text-link" href="{p}docs/research.html#b2">Read the scientific analysis ↗</a></div></section>
<section class="next-strip"><div><p class="eyebrow">NEXT STEPS</p><h2>Resolve the lattice gate before spending a slot.</h2><p>BB-STEP is unique versus the nine listed sites and still a lattice duplicate. Do not jitter dots to evade the rule. No automatic DrivenData scraping or upload.</p></div><a class="button button-dark" href="{p}docs/executive-summary.html">See the checklist ↗</a></section>'''


def guide(depth=1):
    p = '../' * depth
    _, _, _, audit, _ = evidence()
    cand = audit['candidates']
    card = json.loads((DOCS / 'data/run-card.json').read_text())
    cards = [f'''<article class="audit-card"><p class="eyebrow">PRIOR PARALLEL-SESSION ARTIFACT · BB-STEP</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(card['submission_name'])}</code></p><p>SHA-256 <code class="wrap">{card['raster_sha256']}</code></p><p>17,766 dots. Unique vs nine focus sites (worst 3-px overlap 12.6%, |Spearman| 0.085). Lattice overlap 98.53% · literal duplicate. Inside footprint finite and in [0,1]; CRS/shape/transform match the mirrored sample. Zeros-outside and NaN-outside twins both written. Portal acceptance is untested.</p><p>Name <code>KARAGE1-BBSTEP-72312302675D</code> · note: <code>{esc(card['submission_note'])}</code></p><a class="text-link" href="{p}docs/downloads/{quote(card['submission_name'])}" download>Download for research only ↗</a></article>''']
    current_audit = local_and_peer_evidence()
    kth = next(r for r in current_audit['local_downloads'] if r['file'].endswith('unique-hyp-kth-therm-mask-20261028-zeros.tif'))
    kth_card = json.loads((ROOT / 'evidence/kth_candidate_audit_20261029.json').read_text())
    kth_legacy = kth_card['legacy_holdout_claim']
    cards.append(f'''<article class="audit-card"><p class="eyebrow">LEGACY K/TH + THERMAL · QUARANTINED</p><h3>DO NOT SUBMIT · 99.9017% LATTICE OVERLAP</h3><p><strong>Historical research only; not an upload recommendation.</strong></p><p><code class="wrap">unique-hyp-kth-therm-mask-20261028-zeros.tif</code></p><p>SHA-256 <code class="wrap">{kth_card['candidate_sha256']}</code></p><p>{kth['lattice_dots_within_3px']:,} / {kth['positive_pixels_in_footprint']:,} positive pixels within 3 px of the pinned lattice ({kth['lattice_directed_overlap_3px']:.4%}); final-dot gate fails. No pre-placement surface or complete registry proof exists, so uniqueness is not certified.</p><p>Local mirror-grid checks: one float32 band, EPSG:32611, shape/transform match, inside values in [0,1], no NaN or masked/nodata values inside, and zero outside. This is format-only; outside-encoding semantics and portal acceptance are untested.</p><p>The superseded sidecar's {esc(str(kth_legacy['holdout_DTI']))} claim is LEGACY-UNVERIFIED, not an accepted HOLDOUT-DTI: evaluator {esc(kth_legacy['holdout_version'])}, {kth_legacy['withheld_positives']:,} claimed withheld positives, claimed CI {esc(kth_legacy['CI_95'])}. The legacy runner overrode its uniqueness gate. <a href="{p}evidence/legacy_kth_claim_quarantine_20261029.json">See quarantine record ↗</a></p><a class="text-link" href="{p}docs/downloads/unique-hyp-kth-therm-mask-20261028-zeros.tif" download>Download for audit only ↗</a> · <a class="text-link" href="{p}evidence/kth_candidate_audit_20261029.json">Saved-byte audit ↗</a></article>''')
    conduit_audit, conduit_original, latest, conduit_path = conduitcrest_evidence()
    clat = conduit_audit['lattice_witness']
    chdt = conduit_audit['previous_holdout_claim']
    cards.append(f'''<article class="audit-card"><p class="eyebrow">LATER MAINLINE ARTIFACT · CONDUITCREST</p><h3>DO NOT SUBMIT · LATTICE DUPLICATE</h3><p><strong>Research only; not a submission recommendation.</strong></p><p><code class="wrap">{esc(conduit_path.name)}</code></p><p>SHA-256 <code class="wrap">{conduit_audit['candidate']['sha256']}</code></p><p>{clat['candidate_dots']:,} dots; {clat['candidate_dots_within_closed_3px_disk']:,} ({clat['directed_overlap']:.4%}) within 3 px of the pinned lattice. This exceeds the literal 70% stop rule. It was unique only versus the nine focus-site files; its prior run card omitted the lattice and a pre-placement lattice check.</p><p>The prior card contains an incomplete HOLDOUT-DTI claim of {chdt['reported_value']:.6f} (evaluator {esc(chdt['evaluator_version'])}, {chdt['withheld_positives']:,} withheld positives); the 95% CI is missing and the result was not independently rerun here.</p><a class="text-link" href="{p}docs/downloads/{quote(conduit_path.name)}" download>Download for audit only ↗</a> · <a class="text-link" href="{p}evidence/conduitcrest_lattice_reaudit_20261028.json">Reaudit JSON ↗</a></article>''')
    for label, c in zip(('HMAS-SINTER', 'GPC-Z'), cand):
        row = c['comparisons'][0]
        cards.append(f'''<article class="audit-card"><p class="eyebrow">HISTORICAL ARTIFACT · {label}</p><h3>DO NOT SUBMIT</h3><p><code class="wrap">{esc(c['file'])}</code></p><p>SHA-256 <code class="wrap">{c['sha256']}</code></p><p>{row['candidate_dots_within_3px']:,} / {row['candidate_dots']:,} dots within 3 px of lattice ({row['directed_overlap']:.2%}) · duplicate. Mirror-grid and inside [0,1] checks pass; null/NaN-outside check fails. Portal acceptance is untested.</p><a class="text-link" href="{p}docs/downloads/{quote(c['file'])}" download>Download for research only ↗</a></article>''')
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> EXECUTIVE SUMMARY</span><span class="page-date">REVIEWED 29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> THE SUBMISSION CHECKLIST</p><h1>One file. <em>Evidence first.</em></h1><p>What to submit, when—and why today's answer is no.</p></section>{decision(p)}
<section class="section" id="audit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> SAVED-BYTE CHECK</p><h2>All 11 local download GeoTIFFs and 9 audited peer GeoTIFFs fail the literal lattice stop; none is cleared.</h2><p>Research downloads are explicitly not submission recommendations. Uniqueness versus the nine focus sites is not uniqueness versus the lattice or a complete fleet registry.</p></div></div><div class="audit-grid">{''.join(cards)}</div><p class="body-copy">The 29 Oct saved-byte receipt covers every current local TIFF (11) and 9 SHA-pinned peer rasters from 22 commit-pinned GitHub-mirror repositories; all fail the literal &gt;70% lattice-overlap rule. It does not authenticate organizer files or constitute a complete registry. <a href="{p}evidence/local_downloads_and_peer_audit_20261029.json">Current 11-local + 9-peer audit ↗</a> · <a href="{p}evidence/local_downloads_and_peer_audit_20261028.json">Preserved 28 Oct historical 9-local + 9-peer receipt ↗</a>. The synthetic PR #42 artifact was separately retracted for 2,113 outside-footprint positives; see the historical receipt and <a href="{p}knowledge/session-review-arena-1668dda0.md">prior review ↗</a>.</p><p class="body-copy">The official <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format">format description</a> says data outside the bounds should be null or NaN. A strict all-finite check and a null/NaN-outside check are different diagnostics; neither establishes actual portal acceptance. The rejected original file was not supplied, so the cause of its range error is unknown.</p></section>
{comparison(p)}<section class="section" id="steps"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> FOR A FUTURE CLEARED CANDIDATE</p><h2>How to submit, once eligible.</h2><p>These steps are not permission to upload either historical artifact.</p></div></div><div class="steps-grid"><article><span>01 / EVIDENCE</span><h3>Pass the automated gates</h3><p>Use the shared evaluator, fold-local features and per-feature canaries. Beat a frozen comparable holdout best; audit surface and dots against the complete registry; reopen the TIFF and validate saved bytes.</p></article><article><span>02 / SELECTOR</span><h3>Choose a slot separately</h3><p>Only an independent selector may choose an eligible candidate and check the current allowance on the authenticated submission page and current rules. This review did not authenticate the live cap.</p></article><article><span>03 / DOWNLOAD</span><h3>Choose the exact file</h3><p>Download the approved single-band GeoTIFF (or a ZIP containing one GeoTIFF). Check its displayed SHA-256, unique name and note of at most 140 characters.</p></article><article><span>04 / UPLOAD</span><h3>Use the official form</h3><p>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData</a>, select Submit → Make new submission, choose the .tif or ZIP, and paste the note. Retain the file-linked organizer receipt.</p></article></div><div class="notice guide-notice"><span aria-hidden="true">ⓘ</span><p>The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> require disclosure of generative-AI use in the narrative when applicable. Public leaderboard performance is not the private final score.</p></div></section>'''


def research(depth=1):
    p = '../' * depth
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> RESEARCH</span><span class="page-date">REVIEWED 29 OCT 2026</span></div>
<section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SCIENCE BEFORE SCORING</p><h1>Understand the ground.<br><em>Respect the unknown.</em></h1><p>The target is previously unmapped geological faults, not proof of an active geothermal vent.</p></section>
<section class="notice"><span aria-hidden="true">ⓘ</span><p><strong>Negative / no experiment this review:</strong> no method lane, canonical-template assignment, authenticated organizer data payload, or complete registry is available. The current local/peer audit is a saved-byte comparison to commit-pinned GitHub mirrors, not organizer authentication. New hypotheses below are qualitative proposals—not DTI results, score projections, lane assignments, or global novelty claims.</p></section>
<section class="section detail-grid" id="b2"><div><p class="eyebrow"><span class="eyebrow-line"></span> WHAT THE BYTES SHOW</p><h2>Why B2 may have worked.</h2></div><div class="prose-card"><p>Cross-site mask algebra shows GEMSDOE32 B2 (37,654 positive pixels) is GEMSDOE25's 44,090-pixel mask minus 6,436 pixels within 2 px of the mirrored catalogue; no pixels were added. GEMSDOE25 and GEMSDOE30 have identical masks; GEMSDOE32 is also a subset of GEMSDOE36. The reported 0.2778 is <strong>USER-REPORTED / UNVERIFIED</strong>; these geometric facts do not establish why that value occurred.</p><p>Under the organizer's distance-weighted Tversky metric, trimming near-catalogue mass could improve the false-positive / recall tradeoff only if saved false-positive penalty outweighs lost coverage. No hidden-label causal experiment tied to this cross-site mask relation was run. A catalogue buffer is not a free scoring exclusion; nearby unmapped faults may still matter.</p><p>The prompt gives conflicting leaderboard values (0.3195 and 0.4413); an old repository snapshot says 0.4544. None was authenticated against a live organizer page or receipt. <strong>No current value or projection is reported.</strong> <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric">Official metric description ↗</a> · <a class="text-link" href="{p}knowledge/session-review-arena-73de02e3.md">Current forensic review ↗</a></p></div></section>
<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> NOVELTY-SCREENED HYPOTHESES</p><h2>Three proposals. None tested.</h2><p>Ranks reflect qualitative expected held-out DTI benefit relative to implementation cost—not score forecasts. Screened against BB-STEP/DIPDUAL gravity-depth-magnetic work, existing radiometric/thermal/strain/LiDAR features, and vendor relay-bend geometry. Full layer, rationale, confounder, official-source and access notes are in the <a href="{p}knowledge/hypothesis-screen-2026-10-29.md">hypothesis screen ↗</a>.</p></div></div><div class="hypothesis-grid">
<article class="hypothesis-card"><span class="hypothesis-rank">01 <span>MEDIUM BENEFIT · MEDIUM COST</span></span><h3>Multi-catchment bedrock-incision coherence</h3><p>From official USGS 3DEP elevation plus hydrography, derive channel networks, drainage area, longitudinal profiles, knickzones and cross-valley asymmetry. Look for repeatable responses across neighboring catchments, not an isolated DEM edge.</p><div><b>Off-catalogue rationale:</b> buried or degraded structures may perturb several channels where a scarp is absent.</div><small><b>Confounders:</b> lithology, base-level change, capture, alluvial fans, dams and incision lag. USGS 3DEP / 3DHP program links exist; exact tile coverage, versions and payloads were not checked. No catchment graph feature was found in the screened modules.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">02 <span>LOW–MEDIUM BENEFIT · HIGH COST</span></span><h3>Focal-mechanism-consistent microseismic lineaments</h3><p>Use USGS event locations, moment-tensor nodal planes, uncertainty and local strain orientation; test spatially coherent event families whose mechanisms support a structural corridor.</p><div><b>Off-catalogue rationale:</b> a recently active segment can be seismogenic without a clear mapped surface trace.</div><small><b>Novelty boundary:</b> the existing Walker Lane feature uses strain × microseismicity; this adds mechanism-orientation coherence, not event density. <b>Confounders:</b> sparse mechanisms, location error, aftershocks and induced seismicity. ComCat is an official source; footprint coverage was not checked.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">03 <span>LOW / NARROW BENEFIT · VERY HIGH COST</span></span><h3>Persistent InSAR deformation discontinuities</h3><p>Use public Sentinel-1 interferograms or time-series displacement, coherence masks, viewing geometry and multi-epoch displacement gradients; require persistence across independent acquisitions.</p><div><b>Off-catalogue rationale:</b> a currently creeping or repeatedly deforming structure beneath alluvium may lack surface expression; quiet faults will not be detected.</div><small><b>Confounders:</b> atmospheric delay, vegetation, groundwater subsidence, seasonal moisture, unwrapping and geometry. ASF DAAC is an official access route; study-area scenes, processing product and temporal coverage were not checked.</small></article></div><p class="body-copy">Before any experiment: obtain an explicit lane and canonical-template assignment, authenticate and hash the source payload, freeze the common baseline, test each feature alone for leakage, and apply the full two-phase literal registry gate. No shared-template holdout or slot was run here.</p></section>
<section class="section" id="sources"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> TRACEABLE REFERENCES</p><h2>Official access routes, not proof of fetched data.</h2><p>Links identify providers; they do not authenticate mirror bytes, prove local availability, or validate a hypothesis.</p></div></div><div class="source-list"><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"><span><b>DrivenData · problem and metric</b><small>Competition description and format</small></span><span>OFFICIAL ↗</span></a><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf"><span><b>DOE / NLR · rules</b><small>Submission rules and disclosure</small></span><span>OFFICIAL ↗</span></a><a href="https://www.usgs.gov/3d-elevation-program"><span><b>USGS · 3DEP</b><small>Elevation source route; local tiles not checked</small></span><span>OFFICIAL ↗</span></a><a href="https://www.usgs.gov/national-hydrography/3d-hydrography-program"><span><b>USGS · 3D Hydrography Program</b><small>Hydrography source route; local payload not checked</small></span><span>OFFICIAL ↗</span></a><a href="https://earthquake.usgs.gov/fdsnws/event/1/"><span><b>USGS · ComCat FDSN</b><small>Event catalog endpoint; mechanism coverage not checked</small></span><span>OFFICIAL ↗</span></a><a href="https://asf.alaska.edu/"><span><b>NASA / ASF DAAC</b><small>SAR archive route; study-area scenes not checked</small></span><span>OFFICIAL ↗</span></a><a href="{p}knowledge/hypothesis-screen-2026-10-29.md"><span><b>Novelty-screened research slate</b><small>Methods, confounders, differences, data access and release blockers</small></span><span>REVIEW ↗</span></a><a href="{p}knowledge/sources-2026-10-28.md"><span><b>Project source register</b><small>Provenance and access limitations</small></span><span>REVIEW ↗</span></a></div></section>'''

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
