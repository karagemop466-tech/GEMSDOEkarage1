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
    return (f'<strong>DO NOT SUBMIT</strong> · 29 OCT 2026 · No TIFF is authorized for upload. '
            f'<a href="{p}knowledge/session-review-arena-f40ee5b6.md">Current review ↗</a> · '
            f'<a href="{p}evidence/session_f40ee5b6_run_card.json">Run card ↗</a> · '
            'Existing project TIFFs are research-only unless every release gate is independently met.')

def current_artifacts_section(prefix: str) -> str:
    """Show selected upstream research TIFFs without implying they were cleared here."""
    entries = [
        ('Novel-territory dot field',
         'docs/downloads/gems-karage1-unique-novelterritory-20261029T120000Z-5a6b7c8d-zeros.tif',
         'evidence/run_card_gems-karage1-unique-novelterritory-20261029T120000Z-5a6b7c8d.json',
         'Format-valid, but no HOLDOUT-DTI, no assigned lane, and no pre-placement continuous-surface check; the run-card registry scan is not a complete organizer registry.'),
        ('HGRID strain',
         'docs/downloads/karage1-hgridge-strain-K37654-20261029T181321Z-zeros.tif',
         'evidence/hgridge_run_card_20261029T181321Z.json',
         'HOLDOUT-DTI confidence intervals overlap the random control (no measurable skill over random placement), and the saved dots fail the literal lattice-overlap gate; research only.'),
        ('Damage-zone halo',
         'docs/downloads/karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.tif',
         'evidence/run_card_karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.json',
         'Format-valid only; HOLDOUT-DTI and measured registry uniqueness are absent, so the structural-uniqueness description is not a clearance.'),
        ('Convection-cell upflow',
         'docs/downloads/karage1-convect-cell-upflow-20261029-zeros.tif',
         'evidence/session_convect_20261029_run_card.json',
         'Format-valid research raster; no HOLDOUT-DTI, no assigned lane, and no registry-clearance evidence.'),
        ('Geothermal surface (GSE)',
         'docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif',
         'evidence/run_card_gse_exp1.json',
         'No HOLDOUT-DTI, no assigned lane, and no completed registry-uniqueness gate.'),
        ('Conduitcrest',
         'docs/downloads/gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4-zeros.tif',
         'evidence/run_card_gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4.json',
         'A superseding saved-byte audit found a literal lattice duplicate; the earlier HOLDOUT-DTI claim has no 95% CI and is not release-grade.'),
    ]
    rows = []
    for label, file_name, card_name, reason in entries:
        raster = ROOT / file_name
        card_path = ROOT / card_name
        if not raster.is_file() or not card_path.is_file():
            raise ValueError(f'missing research artifact or run card: {file_name}')
        card = json.loads(card_path.read_text(encoding='utf-8'))
        expected = card.get('raster_sha256') or (card.get('raster') or {}).get('sha256')
        actual = hashlib.sha256(raster.read_bytes()).hexdigest()
        if (card.get('ok_to_submit') is not False or 'negative' not in str(card.get('verdict', '')).lower()
                or card.get('slot_selected_or_spent') not in (False, None)
                or not expected or expected != actual):
            raise ValueError(f'research artifact is not fail-closed or card hash disagrees: {file_name}')
        rows.append(
            f'<tr><th scope="row">{esc(label)}</th>'
            f'<td><a class="file-link wrap" href="{prefix}{quote(file_name)}">{esc(Path(file_name).name)}</a>'
            f'<span class="cell-sub">Research/audit download only · SHA-256 {actual[:16]}… · '
            f'<a href="{prefix}{quote(card_name)}">negative run card ↗</a></span></td>'
            f'<td><span class="pill pill-red">DO NOT SUBMIT</span><span class="cell-sub">{esc(reason)}</span></td></tr>'
        )
    return (
        '<section class="section comparison" id="current-research-artifacts"><div class="section-heading"><div>'
        '<p class="eyebrow"><span class="eyebrow-line"></span> SELECTED MAINLINE RESEARCH ARTIFACTS · 29 OCT 2026</p>'
        '<h2>Files exist; none is cleared.</h2>'
        '<p>These files predate the current review and are linked to their own negative run cards. This review did not generate or rerun them. SHA-256 checks below bind each visible file to its card; they do not validate its science, provenance, holdout skill, or upload eligibility. This is a selected recent inventory, not the full historical <code>docs/downloads/</code> archive.</p>'
        '</div></div><div class="table-shell"><div class="table-scroll" tabindex="0" role="region" aria-label="Selected research-only TIFFs">'
        '<table><thead><tr><th>Research artifact</th><th>Saved file and evidence</th><th>Release status</th></tr></thead><tbody>'
        + ''.join(rows) + '</tbody></table></div></div></section>'
    )

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
<div class="container"><p class="global-hold">{status_line(p)}</p></div></header>
<main id="main"><div class="container">{body}</div></main><footer class="site-footer"><div class="container footer-inner"><div><strong>GEMS</strong><span>FIELD INTELLIGENCE</span><p>Evidence before a leaderboard slot.</p></div><div class="footer-links"><a href="{p}evidence/session_f40ee5b6_run_card.json">Current review run card</a><a href="{doc}research.html">Research</a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">Official competition ↗</a></div><div class="footer-end">MAXIMIZE P(WIN) / OWN THE OUTCOME<br><span>Not affiliated with the organizers.</span></div></div></footer></body></html>'''


def session_evidence():
    """Fail-closed loader for the 2026-10-29 StrainPhase / SignedOffset holdout runs."""
    def load(name):
        return json.loads((ROOT / 'evidence' / name).read_text())
    lanes = []
    for lane, prefix in (('strainphase', 'strainphase'), ('signedoffset', 'signedoffset')):
        e1 = load(f'exp1_{prefix}_canary.json')
        e2 = load(f'exp2_{prefix}_holdout.json')
        if (e1.get('any_alarm') is not False or e2.get('evaluator_version') != 'gemsk-hide-recover-v1'
                or e2.get('withheld_positives') != 60988 or e2.get('beats_gpc_control') is not False
                or e2['control_reproduction_vs_exp2_dipdual']['abs_difference'] > 1e-9):
            raise ValueError(f'{lane} holdout evidence incomplete or control not reproduced')
        lanes.append((lane, e2))
    overlap = load('surface_registry_overlap_20261029.json')
    if overlap.get('registry_files_checked', 0) < 15:
        raise ValueError('surface registry overlap evidence incomplete')
    return lanes, overlap


def session_panel(prefix: str):
    lanes, overlap = session_evidence()
    e2 = lanes[0][1]
    gpc = e2['arms']['GPC_control']['dti']
    gpc_ci = e2['bootstrap']['GPC_control']['ci95']
    rows = []
    for lane, d in lanes:
        dti = d['arms'][lane]['dti']
        ci = d['bootstrap'][lane]['ci95']
        delta = d['bootstrap'][lane]['paired_delta_vs_GPC_control']
        rows.append(
            f'<tr><th scope="row">{esc(lane.upper())}<span class="cell-sub">lane H-K1-{esc(lane.upper())}</span></th>'
            f'<td><strong>{dti:.6f}</strong><span class="cell-sub">HOLDOUT-DTI · {esc(d["evaluator_version"])} · n={d["withheld_positives"]:,} withheld positives · 95% CI [{ci[0]:.6f}, {ci[1]:.6f}]</span></td>'
            f'<td>{delta["mean"]:+.6f} [{delta["ci95"][0]:+.6f}, {delta["ci95"][1]:+.6f}]<span class="cell-sub">paired vs GPC control</span></td>'
            '<td><span class="pill pill-red">NEGATIVE</span><span class="cell-sub">below holdout best; no slot spent</span></td></tr>'
        )
    worst = overlap['worst_abs_spearman_by_surface']
    worst_overlap = max(r['share_registry_dots_within_3px_of_top_budget'] for r in overlap['rows'])
    return f'''<section class="decision-panel" aria-labelledby="session-title"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> PRIOR SESSION arena/fb1e3550 · 29 OCT 2026 <span class="status-tag">NOTHING CLEARED</span></div>
<h2 id="session-title">No TIFF is cleared to submit. Both outputs from this prior session are negative; research downloads are listed separately.</h2>
<p><strong>Submission answer:</strong> no file is cleared; prior-session candidates tested below the reproduced GPC control. The two new candidates (STRAINPHASE, SIGNEDOFFSET) were built and tested on the shared hide-and-recover holdout, and both score below the reproduced GPC control. Following the protocol, neither was rasterised for placement and no weekly slot was spent.</p>
<div class="table-shell"><div class="table-scroll" tabindex="0" role="region" aria-label="Session holdout results"><table><thead><tr><th scope="col">Candidate</th><th scope="col">Holdout result (not a leaderboard estimate)</th><th scope="col">Paired difference</th><th scope="col">Verdict</th></tr></thead><tbody>
<tr><th scope="row">GPC control (reproduced)<span class="cell-sub">gemskarage1.dipdual gpc_physics control</span></th><td><strong>{gpc:.6f}</strong><span class="cell-sub">HOLDOUT-DTI · gemsk-hide-recover-v1 · n=60,988 · 95% CI [{gpc_ci[0]:.6f}, {gpc_ci[1]:.6f}] · matches recorded value exactly</span></td><td>reference</td><td><span class="pill">BASELINE</span></td></tr>
{''.join(rows)}
</tbody></table></div></div>
<p>Leakage canary (each feature alone, blocked folds): maximum direction-invariant AUC {max(r["max_direction_invariant_auc"] for r in json.loads((ROOT / "evidence/exp1_strainphase_canary.json").read_text())["canary_rows"]):.3f} and {max(r["max_direction_invariant_auc"] for r in json.loads((ROOT / "evidence/exp1_signedoffset_canary.json").read_text())["canary_rows"]):.3f}; both below the 0.90 alarm.</p>
<p>Pre-placement surface check against 15 restored registry rasters: worst |Spearman| {worst["strainphase"]["spearman_rho"]:+.4f} (STRAINPHASE) and {worst["signedoffset"]["spearman_rho"]:+.4f} (SIGNEDOFFSET); worst share of registry dots within 3 px of the surface's top-budget pixels {worst_overlap:.1%}. Neither surface is a duplicate. Their weakness is detection skill, not uniqueness.</p>
<p>Public leaderboard (organizer, 28–29 Oct 2026): #1 is 0.4544; 0.3195 is rank #47 (see <a href="{prefix}knowledge/official-sources-verified-2026-10-29.md">official-sources register</a>). None of the nine GEMSDOE scores appears in the top 50 and they remain USER-REPORTED / UNVERIFIED.</p>
<div class="decision-actions"><button class="button button-disabled" disabled>No cleared TIF to download for submission</button>
<a class="button button-light" href="{prefix}evidence/exp2_strainphase_holdout.json">STRAINPHASE holdout JSON ↗</a>
<a class="button button-light" href="{prefix}evidence/exp2_signedoffset_holdout.json">SIGNEDOFFSET holdout JSON ↗</a>
<a class="button button-light" href="{prefix}evidence/surface_registry_overlap_20261029.json">Surface overlap JSON ↗</a>
<a class="button button-light" href="{prefix}knowledge/session-review-arena-fb1e3550.md">Session review ↗</a></div>
</div>
<div class="decision-side"><div><span>VERDICT</span><strong>Negative · no file cleared</strong></div><div><span>LEADERBOARD ESTIMATE</span><strong>Not produced</strong></div><div><span>BEST NEW RESULT</span><strong>Below GPC control · HOLDOUT-DTI table</strong></div><div><span>SLOTS SPENT</span><strong>0</strong></div></div></section>'''


def decision(prefix: str):
    current = f'''<section class="decision-panel" aria-labelledby="decision-title"><div class="decision-main">
<div class="status-line"><span class="status-dot"></span> CURRENT SUBMISSION DECISION · 29 OCT 2026 · ARENA/F40EE5B6 <span class="status-tag">DO NOT SUBMIT</span></div>
<h2 id="decision-title">No eligible submission file. No new candidate was evaluated. This review did not produce a project TIFF or authorize an upload.</h2>
<p>No cleared TIFF available. This review ran no geological experiment or holdout, made no score estimate, and selected or spent no submission slot. Research TIFFs already present from earlier mainline work remain separate artifacts with their own negative run cards; this review did not regenerate, rerun, or promote them. Selected files are linked in the research-only inventory on the overview and submission-guide pages; they are not cleared for upload.</p>
<p><strong>Execution remains blocked:</strong> no method lane or authoritative canonical-template assignment is recorded; the five required organizer cache inputs (<code>feature_stack.npy</code>, <code>existing_faults.tif</code>, <code>training_features.tif</code>, <code>sample_submission.tif</code>, and <code>labels.tif</code>) are absent. The shared-tool integrity check found two vendored SHA-256 pin mismatches and a template/source-pin mismatch. Do not create a private stack, evaluator, or writer to route around these gates.</p>
<p>The highest supplied peer score, GEMSDOE32 at <strong>0.2778</strong>, remains USER-REPORTED / UNVERIFIED; there is no artifact-linked organizer receipt. The nine-site table separates that report from geometric uniqueness and the unavailable organizer estimate. The public leaderboard is a separate snapshot, not a substitute for the missing receipt.</p>
<p><strong>Current records:</strong> <a href="{prefix}knowledge/session-review-arena-f40ee5b6.md">three-pass review ↗</a> · <a href="{prefix}evidence/session_f40ee5b6_run_card.json">current JSON run card ↗</a> · <a href="{prefix}evidence/session_f40ee5b6_shared_preflight.json">shared preflight ↗</a> · <a href="{prefix}evidence/session_f40ee5b6_template_integrity.json">template integrity ↗</a> · <a href="{prefix}docs/research/hypotheses-20261029.md">ranked hypothesis slate ↗</a> · <a href="{prefix}knowledge/official-sources-verified-2026-10-29.md">official-source register ↗</a>.</p>
<div class="decision-actions"><button class="button button-disabled" disabled>No cleared TIF to download for submission</button>
<a class="button button-light" href="{prefix}index.html#current-research-artifacts">Research-only artifacts ↗</a>
<a class="button button-light" href="{prefix}knowledge/session-review-arena-f40ee5b6.md">Read the current review ↗</a></div>
</div><div class="decision-side"><div><span>THIS REVIEW</span><strong>No experiment · no new TIFF</strong></div><div><span>HOLDOUT / SCORE</span><strong>Not run / not estimated</strong></div><div><span>UPLOAD SLOT</span><strong>Not selected or spent</strong></div><div><span>PROJECT STATUS</span><strong>No TIFF cleared</strong></div></div></section>'''
    return current + session_panel(prefix)

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
        '<span class="cell-sub">Prior-session research artifact · audit only</span></td>'
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


def nine_site_section(prefix: str) -> str:
    """Rank the highest supplied file per focus site using pinned lineage evidence."""
    scores = json.loads(NINE_SCORES.read_text(encoding='utf-8'))['entries']
    assets = {row['id']: row for row in json.loads((ROOT / 'registry/reference_assets.json').read_text(encoding='utf-8'))}
    lineage = json.loads(NINE_LINEAGE.read_text(encoding='utf-8'))
    pairwise = lineage['pairwise_nine_sites']
    best_share: dict[str, tuple[float, str]] = {site: (0.0, '') for site in SITES}
    for key, values in pairwise.items():
        a, b = key.split('|')
        for site, peer, fraction in (
            (a, b, values['a_dots_within_3px_of_b_fraction']),
            (b, a, values['b_dots_within_3px_of_a_fraction']),
        ):
            if site in best_share and fraction > best_share[site][0]:
                best_share[site] = (fraction, peer)
    ranked = []
    for site in SITES:
        candidates = [row for row in scores if row['site'] == site]
        asset = assets.get(site)
        if not candidates or not asset:
            raise ValueError(f'missing reported score or pinned source asset for {site}')
        top = max(candidates, key=lambda row: row['score'])
        if not Path(asset['path']).stem.endswith(top['file_name']):
            raise ValueError(f'highest reported file does not match pinned asset name for {site}')
        overlap, peer = best_share[site]
        if not peer or overlap <= 0.70:
            raise ValueError(f'peer-overlap evidence incomplete or expected stop absent for {site}')
        ranked.append((top['score'], site, top, asset, overlap, peer))
    ranked.sort(key=lambda row: -row[0])
    trs = []
    for rank, (score, site, top, asset, overlap, peer) in enumerate(ranked, 1):
        raw_url = f"https://raw.githubusercontent.com/{asset['repo']}/{asset['ref']}/{asset['path']}"
        trs.append(
            f'<tr><th scope="row"><a href="{prefix}docs/{site}.html">#{rank} · {site} ↗</a></th>'
            f'<td><a class="file-link wrap" href="{esc(raw_url, quote=True)}">{esc(Path(asset["path"]).name)}</a>'
            f'<span class="cell-sub">Exact SHA-pinned peer TIFF · SHA-256 {esc(asset["sha256"][:16])}… · '
            f'<a href="{esc(top["url"], quote=True)}">peer source page ↗</a></span></td>'
            f'<td><strong>{score:.4f}</strong><span class="cell-sub">USER-REPORTED / UNVERIFIED</span></td>'
            '<td>UNAVAILABLE<span class="cell-sub">No artifact-linked organizer receipt or reproduced estimate</span></td>'
            f'<td><span class="pill pill-red">NO · INTERNAL STOP</span>'
            f'<span class="cell-sub">{overlap:.2%} of this file’s dots within 3 px of {esc(peer)}</span></td>'
            '<td><strong>DO NOT SUBMIT</strong></td></tr>'
        )
    top_score, top_site = ranked[0][0], ranked[0][1]
    worst_peer = min(row[4] for row in ranked)
    return (
        '<section class="section comparison" id="nine-sites"><div class="section-heading"><div>'
        '<p class="eyebrow"><span class="eyebrow-line"></span> CURRENT FEED · NINE FOCUS SITES · 29 OCT 2026</p>'
        '<h2>Highest reported file, peer overlap, and download decision</h2>'
        f'<p><strong>SUBMISSION STATUS: NO FILE APPROVED.</strong> The highest supplied row is {esc(top_site)} at '
        f'<strong>{top_score:.4f} USER-REPORTED / UNVERIFIED</strong>. Exact SHA-pinned peer TIFFs below are for research only. '
        'No artifact-linked organizer receipt exists, so the organizer estimate is unavailable for every row. '
        'The peer column is a directional discrete-dot comparison of saved masks, not a continuous-surface Spearman test and not proof of geological equivalence. '
        f'Every best peer file exceeds the user-defined 70% internal stop (lowest worst-peer overlap: {worst_peer:.2%}); that threshold is not stated as an organizer rule. Do not resubmit peer-owned files.</p>'
        '</div></div><div class="table-shell"><div class="table-scroll-hint">Scroll to see the full table →</div>'
        '<div class="table-scroll" tabindex="0" role="region" aria-label="Nine-site executive summary"><table>'
        '<thead><tr><th>Rank · site</th><th>Highest supplied peer TIFF (research download)</th><th>Score label</th>'
        '<th>New organizer estimate</th><th>Unique vs listed peer files?</th><th>Submit?</th></tr></thead>'
        f'<tbody>{"".join(trs)}</tbody></table></div></div>'
        '<p class="cell-sub">Scores: <code>registry/user_reported_scores_20261029.json</code>. Pairwise overlaps: <code>evidence/site_lineage_verification_20261029.json</code>, scoped to the SHA-pinned owner mirrors in <code>registry/reference_assets.json</code>. Historical peer-dot checks do not replace the separate continuous-surface and complete-registry gates for a new candidate.</p>'
        '</section>'
    )

def home(depth=0):
    p = '../' * depth
    return f'''<div class="page-top"><span>GEMS PRIZE <span class="separator">/</span> DECISION BRIEF</span><span class="page-date">INDEPENDENT REVIEW · 29 OCT 2026</span></div>
<section class="hero compact-hero"><div class="hero-copy"><p class="eyebrow"><span class="eyebrow-line"></span> EVIDENCE BEFORE A LEADERBOARD SLOT</p><h1>Find faults.<br><em>Protect every submission.</em></h1><p class="hero-description">A clear, auditable workspace for fault discovery in the Great Basin. We separate format checks, scientific evidence, uniqueness and actual portal acceptance.</p><div class="hero-actions"><a class="text-link" href="#comparison">Compare the nine sites ↓</a><a class="subtle-link" href="{p}docs/research.html">Explore the research ↗</a></div></div>
<div class="terrain-card terrain-small" aria-label="Illustrative contour artwork, not a prediction map"><div class="terrain-top"><span>GEO<span class="terrain-dot">●</span>DAWN</span><span>FIELD NOTE / 01</span></div><svg class="terrain-lines" viewBox="0 0 620 340" preserveAspectRatio="xMidYMid slice" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="1.5"><path d="M-50 10C90 25 95 155 200 110S305-10 410 55s150 110 250 40"/><path d="M-50 35C80 50 100 180 205 135S310 15 410 80s150 110 250 40"/><path d="M-50 60C70 75 105 205 210 160S315 40 410 105s150 110 250 40"/><path d="M-50 85C60 100 110 230 215 185S320 65 410 130s150 110 250 40"/><path d="M-50 110C50 125 115 255 220 210S325 90 410 155s150 110 250 40"/><path d="M-50 135C40 150 120 280 225 235S330 115 410 180s150 110 250 40"/><path d="M-50 160C30 175 125 305 230 260S335 140 410 205s150 110 250 40"/></g><g class="terrain-focus" fill="none"><circle cx="379" cy="139" r="40"/><circle cx="379" cy="139" r="26"/><path d="M379 89v100M329 139h100"/></g></svg><div class="terrain-caption"><span><b>THE STUDY AREA</b><br>Western Great Basin</span><span>NEVADA + CALIFORNIA<br><b>CONCEPTUAL ONLY</b></span></div></div></section>
{nine_site_section(p)}{decision(p)}{current_artifacts_section(p)}<section class="snapshot" aria-label="Evidence snapshot"><div class="snapshot-item"><div class="snapshot-label">PUBLIC LEADERBOARD SNAPSHOT</div><div class="snapshot-value">0.4544</div><p>Organizer public leaderboard · direct read 29 Oct 2026 · <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">check current ↗</a></p></div><div class="snapshot-item"><div class="snapshot-label">BEST SUPPLIED NINE-SITE REPORT</div><div class="snapshot-value">0.2778</div><p>GEMSDOE32 · USER-REPORTED, not confirmed</p></div><div class="snapshot-item"><div class="snapshot-label">PRIOR BB-STEP SESSION</div><div class="snapshot-value">3 <span class="snapshot-context">experiments</span></div><p>Separate parallel run · lattice stop applied</p></div><div class="snapshot-item"><div class="snapshot-label">INPUT RESTORATION</div><div class="snapshot-value">21 <span class="snapshot-context">files</span></div><p>Hash-pinned mirrors · not organizer-authenticated</p></div></section>
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
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> EXECUTIVE SUMMARY</span><span class="page-date">INDEPENDENT REVIEW · 29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> THE SUBMISSION CHECKLIST</p><h1>One file. <em>Evidence first.</em></h1><p>What to submit, when—and why today's answer is no.</p></section>{nine_site_section(p)}
{decision(p)}
{current_artifacts_section(p)}
{upload_packet(p)}
<section class="section" id="audit"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> SAVED-BYTE CHECK</p><h2>The 9 local and 9 sibling/peer GeoTIFFs covered by the 1668dda0 receipt fail its gate; later candidates are audited separately below.</h2><p>Research downloads are explicitly not submission recommendations. Uniqueness versus the nine focus sites is not uniqueness versus the lattice or a complete fleet registry.</p></div></div><div class="audit-grid">{''.join(cards)}</div><p class="body-copy">In addition to the four cards above (and the <code>-nan.tif</code> twins for BB-STEP and GPC-Z plus the quarantined CDA1 <code>-zeros.tif</code>/<code>-nan.tif</code> pair), session <code>1668dda0</code> audited and retracted <code>karage1-unique-alteration-dots-20261028-zeros.tif</code> (SHA-256 <code>8bc4dae02a99da68…</code>): 2,113 of its 3,500 positive pixels lie outside the competition footprint (<code>outside_encoding_accepted = false</code>) and 99.8558% (1,385/1,387) of its inside-footprint positives lie within 3 px of the pinned lattice. Sibling <code>GEMSDOEkarage2</code> (99.86%), <code>GEMSDOEkarage3</code> (99.35%), and newly audited peer GeoTIFFs across <code>GEMSDOE91</code>, <code>KANLERGEMSDOE3</code>, <code>WBGGEMSDOE1</code>, <code>ApartGEMSDOE1/2</code>, and <code>GEMSDOESASS1</code> also overlap 99.35%–99.95% within 3 px of the lattice (<a href="{p}evidence/local_downloads_and_peer_audit_20261028.json">inspect full 18-raster receipt ↗</a>).</p><p class="body-copy">The historical K/Th + thermal candidate <code>unique-hyp-kth-therm-mask-20261028-zeros.tif</code> has been moved out of the public download directory. Its prior promotion claim is superseded. A pinned-mirror saved-byte audit records 99.9017% directed 3-px overlap with the lattice, exceeding the literal duplicate threshold; the former holdout claim is not reproduced. It remains quarantined for audit only; see <a href="{p}archive/quarantined-20261029/README-review-dc2e4c0c.md">archive note ↗</a> and <a href="{p}evidence/unique_hyp_kth_therm_mask_retraction_20261029.json">retraction receipt ↗</a>.</p><p class="body-copy">The official <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format">format description</a> says data outside the bounds should be null or NaN. A strict all-finite check and a null/NaN-outside check are different diagnostics; neither establishes actual portal acceptance. The rejected original file was not supplied, so the cause of its range error is unknown.</p></section>
{comparison(p)}<section class="section" id="steps"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> FOR A FUTURE CLEARED CANDIDATE</p><h2>How to submit, once eligible.</h2><p>These steps are not permission to upload either historical artifact.</p></div></div><div class="steps-grid"><article><span>01 / EVIDENCE</span><h3>Pass the automated gates</h3><p>Use the shared evaluator, fold-local features and per-feature canaries. Beat a frozen comparable holdout best; audit surface and dots against the complete registry; reopen the TIFF and validate saved bytes.</p></article><article><span>02 / SELECTOR</span><h3>Choose a slot separately</h3><p>Only an independent selector may choose an eligible candidate and check the current allowance on the authenticated submission page. The September rules say three submissions per week.</p></article><article><span>03 / DOWNLOAD</span><h3>Choose the exact file</h3><p>Download the approved single-band GeoTIFF (or a ZIP containing one GeoTIFF). Check its displayed SHA-256, unique name and note of at most 140 characters.</p></article><article><span>04 / UPLOAD</span><h3>Use the official form</h3><p>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">DrivenData</a>, select Submit → Make new submission, choose the .tif or ZIP, and paste the note. Retain the file-linked organizer receipt.</p></article></div><div class="notice guide-notice"><span aria-hidden="true">ⓘ</span><p>The <a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf">official rules</a> require disclosure of generative-AI use in the narrative when applicable. Public leaderboard performance is not the private final score.</p></div></section>'''


def research(depth=1):
    p = '../' * depth
    return f'''<div class="page-top"><span>OVERVIEW <span class="separator">/</span> RESEARCH</span><span class="page-date">REVIEWED · 29 OCT 2026</span></div>
<section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SCIENCE BEFORE SCORING</p><h1>Understand the ground.<br><em>Respect the unknown.</em></h1><p>The target is previously unmapped geological faults, not direct proof of a geothermal vent.</p></section>
<section class="notice"><span aria-hidden="true">ⓘ</span><p><strong>Proposals only:</strong> no hypothesis was implemented or holdout-tested in the current review; the four ranked proposals were not assigned as the method lane. They are a qualitative queue, not a predicted DTI gain. The shared preflight is blocked; no experiment or new TIFF was produced.</p><p>The official pooled metric uses α=0.2, β=0.8 and a 300 m triangular kernel. The USGS GeoDAWN catalog lists Area 1: 43.57 MB; Area 2: 230.54 MB. Catalog availability is verified; bytes were not fetched. No specific tile was downloaded or aligned.</p></section>
<section class="section detail-grid" id="b2"><div><p class="eyebrow"><span class="eyebrow-line"></span> B2 CAVEAT</p><h2>A geometry clue, not a score explanation.</h2></div><div class="prose-card"><p>On the pinned peer rasters, GEMSDOE25 and GEMSDOE30 share the same 44,090-dot mask. GEMSDOE32 B2 has 37,654 dots: the parent mask minus 6,436 dots within 2 px of the mirrored catalogue, with no dots added. GEMSDOE36 is a strict superset with 1,200 additional dots. The reported <strong>0.2778</strong> for GEMSDOE32 is USER-REPORTED / UNVERIFIED; no artifact-linked organizer receipt ties it to the raster hash.</p><p>Under the official distance-weighted Tversky metric, removing redundant prediction mass could reduce false-positive cost, but could also remove withheld-fault coverage. These mask relationships are not a controlled ablation and do not establish why the reported score differs.</p><p>See the <a href="{p}knowledge/session-review-arena-f40ee5b6.md">current review ↗</a>, <a href="{p}knowledge/session-review-arena-1668dda0.md">prior byte audit ↗</a>, and the <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric">official metric description ↗</a>.</p></div></section>
<section class="section" id="hypotheses"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> RANKED HYPOTHESES</p><h2>Four qualitative proposals; none is an assigned lane.</h2><p>Rank reflects mechanistic plausibility relative to cost only—not a predicted DTI gain. Exact inputs, mimics, differences and data blockers are recorded in the <a href="{p}docs/research/hypotheses-20261029.md">complete hypothesis slate ↗</a>.</p></div></div><div class="hypothesis-grid">
<article class="hypothesis-card"><span class="hypothesis-rank">01 <span>MEDIUM COST · PROPOSAL</span></span><h3>Cross-Potential Dip-Polarity Co-Gradient Step (CP-DPCS)</h3><p>Compare signed RTP-magnetic phase with isostatic-gravity gradients across continuation scales, conditioned on low relief. A concealed fault could juxtapose magnetic basement and lower-density basin fill under subdued cover.</p><div><b>Non-fault mimics:</b> intrusive contacts, caldera margins, basalt edges, paleochannels and survey seams.</div><small>Proposed contest-stack layers are not locally authenticated; related ideas exist, so fleet-wide novelty is unknown. <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official contest description ↗</a></small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">02 <span>MEDIUM–HIGH COST · PROPOSAL</span></span><h3>Biharmonic Elastic Relay-Bridge Stress-Transfer Corridor (BERB-STC)</h3><p>Use fold-visible fault-segment endpoints to estimate tip-pair stress transfer, then test whether conductivity and gravity discontinuities corroborate relay-ramp corridors connecting traces beneath young fans.</p><div><b>Non-fault mimics:</b> induced seismicity, conductive playa brines and coarse strain-grid interpolation bullseyes.</div><small>Needs fold-local feature derivation and a shared spatial holdout. Contest data and an assigned lane are absent; not run.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">03 <span>MEDIUM–HIGH COST · PROPOSAL</span></span><h3>Wavelet-Destriped Potassium-Residual Magnetics Trough (WD-KRMT)</h3><p>Remove flight-line structure from GeoDAWN potassium/eTh/eU fields, then test a radiometric boundary paired with a magnetic trough that may persist where erosion or burial hides a scarp.</p><div><b>Non-fault mimics:</b> potassic intrusions, weathering, volcanic units, playa evaporites and survey stripes.</div><small><a href="https://doi.org/10.5066/P93LGLVQ">USGS GeoDAWN catalog ↗</a> lists public bundles; catalog access was verified, but no payload, exact local projection or contest-grid overlap was checked.</small></article>
<article class="hypothesis-card"><span class="hypothesis-rank">04 <span>HIGH COST · PROPOSAL</span></span><h3>Cross-Fan Drainage-Incision Knickzone Alignment (CF-DIKA)</h3><p>Require replicated channel deflection or knickzones across at least three adjacent catchments at an independent gravity step. Repeated drainage perturbations may survive where individual scarps are obscured.</p><div><b>Non-fault mimics:</b> Lake Lahontan shoreline benches, fan avulsion, stream piracy and lithologic ledges.</div><small><a href="https://www.usgs.gov/3d-elevation-program/about-3dep-products-services">USGS 3DEP products ↗</a> documents public coverage; no tile, alignment or useful-resolution check was performed.</small></article>
</div><p class="body-copy">Queue decision: CP-DPCS is the qualitative first question only. Do not start until lane/template authorization, permitted data, repaired shared-tool provenance, complete registry access, feature-alone leakage canaries, and the prescribed holdout evaluator are available. See the <a href="{p}evidence/session_f40ee5b6_shared_preflight.json">blocked preflight ↗</a>.</p></section>
<section class="section" id="sources"><div class="section-heading"><div><p class="eyebrow"><span class="eyebrow-line"></span> TRACEABLE REFERENCES</p><h2>Official source register.</h2><p>Official catalog or rule pages do not authenticate third-party mirrors, establish local data readiness, or validate the hypotheses.</p></div></div><div class="source-list"><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"><span><b>DrivenData · problem, metric and format</b><small>Official description</small></span><span>OFFICIAL ↗</span></a><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/data/"><span><b>DrivenData · data tab</b><small>Login-gated in the current review; payload not obtained</small></span><span>OFFICIAL ↗</span></a><a href="https://docs.nlr.gov/docs/fy26osti/96647.pdf"><span><b>DOE / NLR · rules</b><small>Submission limits and AI disclosure</small></span><span>OFFICIAL ↗</span></a><a href="https://doi.org/10.5066/P93LGLVQ"><span><b>USGS · GeoDAWN catalog</b><small>Public magnetic/radiometric metadata and bundles; no payload downloaded</small></span><span>OFFICIAL ↗</span></a><a href="https://www.usgs.gov/3d-elevation-program/about-3dep-products-services"><span><b>USGS · 3DEP</b><small>Product coverage and resolution information</small></span><span>OFFICIAL ↗</span></a><a href="{p}knowledge/official-sources-verified-2026-10-29.md"><span><b>Verified-source register</b><small>Line-by-line access and limitation notes</small></span><span>REVIEW ↗</span></a></div></section>'''

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
    return f'''<div class="page-top"><span>NINE-SITE REVIEW <span class="separator">/</span> {name}</span><span class="page-date">INDEPENDENT REVIEW · 29 OCT 2026</span></div><section class="subpage-hero"><p class="eyebrow"><span class="eyebrow-line"></span> SITE EXECUTIVE SUMMARY</p><h1>{name}. <em>Research only.</em></h1><p>The reported historical leader is not a newly eligible submission.</p></section>{decision('../')}
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
