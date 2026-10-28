#!/usr/bin/env python3
"""Supersede inherited release decisions using the saved lattice-witness audit.

Preserves old scientific measurements as historical claims; never makes a new
score, model, prediction, portal upload, or weekly-slot selection.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.release_gate import assess  # noqa: E402


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def main():
    audit_path = ROOT / 'evidence/prior_candidate_audit.json'
    audit = load(audit_path)
    if audit.get('schema') != 'karage1-prior-candidate-audit-v1':
        raise ValueError('missing or invalid candidate audit')
    ref = audit['reference_sources']['lattice']
    for name in ('hmas', 'gpcz'):
        r = audit['results'][name]
        if not r['lattice_rule_exceeded'] or r['directed_overlap_fraction'] <= 0.70:
            raise ValueError('lattice duplicate witness missing; review before changing decision')

    old_hmas = ROOT / 'evidence/run_card_hmas_sinter.json'
    hmas = load(old_hmas)
    r = audit['results']['hmas']
    if hmas['raster_sha256'] != r['sha256']:
        raise ValueError('historical HMAS card is not bound to audited bytes')
    hmas.setdefault('verdict_before_2026_10_28_review', hmas['verdict'])
    hmas['verdict'] = 'negative'
    hmas['ok_to_submit'] = False
    hmas['correction'] = ('2026-10-28: the prior gate excluded a registered lattice and is superseded. '
                          'The saved candidate fails the literal directed-overlap rule. Prior holdouts have not been replayed.')
    hmas['registry_correlation_overlap']['passed'] = False
    hmas['registry_correlation_overlap']['literal_lattice_witness'] = {
        'file_sha256': ref['sha256'], 'dots_within_3px': r['dots_within_closed_3px_disk'],
        'candidate_dots': r['dots'], 'directed_overlap': r['directed_overlap_fraction']}
    save(old_hmas, hmas)

    gpcz_path = ROOT / 'evidence/run_card_gpcz.json'
    gpcz = load(gpcz_path)
    g = audit['results']['gpcz']
    if gpcz['raster']['sha256'] != g['sha256']:
        raise ValueError('historical GPC-Z card is not bound to audited bytes')
    gpcz.setdefault('verdict_before_2026_10_28_review', gpcz['verdict'])
    gpcz['verdict'] = 'negative'
    gpcz['verdict_reason'] = 'Superseded: the registered lattice exceeds the literal 3-pixel overlap rule; stop.'
    gpcz['uniqueness']['unique'] = False
    gpcz['uniqueness']['rule_overlap_le_0.70'] = False
    gpcz['uniqueness']['literal_lattice_overlap'] = g['directed_overlap_fraction']
    gpcz['correction'] = '2026-10-28 saved-byte recheck; do not exempt the lattice or treat the old release gate as valid.'
    save(gpcz_path, gpcz)

    fleet_path = ROOT / 'evidence/fleet_uniqueness_593.json'
    fleet = load(fleet_path)
    fleet.setdefault('prior_scanner_passed_before_correction', fleet['passed'])
    fleet['passed'] = False
    fleet['correction'] = ('Historical diagnostic only; the old pass excluded lattice and dense witnesses, '
                           'and the full inventory was not replayed on 2026-10-28.')
    fleet['literal_lattice_witness'] = hmas['registry_correlation_overlap']['literal_lattice_witness']
    save(fleet_path, fleet)

    ledger_path = ROOT / 'evidence/experiments_summary.json'
    ledger = load(ledger_path)
    ledger.setdefault('prior_verdict_before_correction', ledger['verdict'])
    ledger['verdict'] = 'negative'
    ledger['gates']['uniqueness_gate_passed'] = False
    ledger['gates']['leakage_canary_passed'] = False
    ledger['correction'] = ('Prior holdout results not replayed. Literal lattice witness fails; '
                            'the old canary treated its constant footprint feature as AUC 0.5.')
    save(ledger_path, ledger)

    # Reassess old gate inputs instead of trusting their previous summary maxima.
    for name, result in [('hmas_sinter', r), ('gpcz', g)]:
        path = ROOT / f'evidence/release_gate_{name}.json'
        gate = load(path)
        inp = gate['input']
        inp['registry'].update({
            'complete': False,
            'surface_checked_before_placement': False,
            'expected_count': 1,
            'max_directed_overlap_3px': result['directed_overlap_fraction'],
            'records': [{
                'id': 'registered-r13-lattice', 'sha256': ref['sha256'],
                'surface_abs_rho': None,
                'dots_abs_rho': abs(result['binary_spearman_vs_lattice']) if result['binary_spearman_vs_lattice'] is not None else None,
                'directed_overlap_3px': result['directed_overlap_fraction'],
            }],
        })
        inp['canary']['all_features_tested'] = False
        inp['validator']['outside_encoding_compatible'] = False
        inp['validator']['template_official_authenticated'] = False
        gate.setdefault('result_before_2026_10_28_review', gate['result'])
        gate['result'] = assess(inp)
        gate['correction'] = 'Reassessed against the known lattice witness; only one witness rechecked, not the complete inventory.'
        save(path, gate)

    receipt_path = ROOT / 'docs/downloads/karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.json'
    receipt = load(receipt_path)
    receipt.update(promoted=False, approved_for_weekly_slot=False, uniqueness_gate_passed=False,
                   verdict='negative', status='Superseded: local format only; literal lattice overlap fails; do not submit.')
    save(receipt_path, receipt)
    gpcz_receipt = ROOT / 'docs/downloads/gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-receipt.json'
    receipt2 = load(gpcz_receipt)
    receipt2.update(verdict='negative', approved_for_weekly_slot=False,
                    correction='Local format receipt only. Lattice overlap failed; do not submit.')
    save(gpcz_receipt, receipt2)

    # A single current card, containing a prior explicitly-not-replayed holdout,
    # plus the independently measured saved-byte validator and lattice witness.
    h = hmas['holdout_dti']['gems57_pooled_hide_v2_detached']
    fmt = r['format_diagnostic']
    card = {
        'schema': 'karage1-run-card-v2', 'created_utc': audit['created_utc'],
        'lane': 'No new lane assigned; review of prior HMAS-SINTER-ENV only',
        'hypothesis': 'Buried hydrothermal fault corridors may combine magnetic and gravity structure with shallow thermal or sinter observations.',
        'mechanism': 'A conduit may locally alter magnetization or conductivity while basin-fill cover obscures a surface scarp; this is an unproven hypothesis.',
        'named_non_fault_mimic': 'Lithologic contacts and volcanic flow margins can create magnetic and gravity contrasts without a fault.',
        'holdout_dti': {
            'label': 'HOLDOUT-DTI', 'evaluator_version': h['evaluator_version'],
            'withheld_positives': h['withheld_positives'], 'value': h['dti'], 'ci95': h['ci95'],
            'status': 'Prior run report only; not replayed or independently verified in this session; not a leaderboard estimate.'},
        'correlation_overlap_vs_registry': {
            'preplacement_surface_spearman': None,
            'preplacement_status': r['surface_status'],
            'final_dot_spearman_vs_lattice': r['binary_spearman_vs_lattice'],
            'final_dot_overlap_vs_lattice': r['directed_overlap_fraction'],
            'candidate_dot_count': r['dots'], 'dots_within_3px': r['dots_within_closed_3px_disk'],
            'registry_coverage': 'One pinned lattice witness rechecked; not a complete registry.'},
        'raster_sha256': r['sha256'],
        'validator_output': {
            'no_nan_inside_footprint': fmt['checks']['no_nonfinite_inside'],
            'values_in_0_1': fmt['checks']['inside_values_in_0_1'],
            'crs_shape_transform_match': fmt['checks']['crs_shape_transform_match_mirror'],
            'whole_array_finite_and_in_range': fmt['checks']['whole_array_strict_finite_0_1'],
            'outside_all_null_or_nan': fmt['checks']['outside_all_null_or_nan'],
            'status': 'Local check against a pinned peer mirror; official template authenticity and portal acceptance unverified.'},
        'submission_file': Path(r['file']).name,
        'submission_name': hmas['submission_name'], 'submission_note': hmas['submission_note'],
        'download_available': False, 'ok_to_submit': False,
        'slot_selected_or_spent': False, 'weekly_allowance_verified': False,
        'geological_experiments_run': 0, 'portal_submissions_this_session': 0,
        'verdict': 'negative',
        'blockers': [
            'The prior HMAS file exceeds the literal overlap limit against a registered lattice; stop.',
            'The pre-placement surface, current complete registry, and comparable verified holdout best are unavailable.',
            'The inherited single-feature canary marked a constant footprint channel as a pass.',
            'The sample template is a peer mirror and outside-footprint encoding versus portal validation is unresolved.',
            'The current prompt references an assigned method paragraph but supplies none.'
        ],
        'evidence': 'evidence/prior_candidate_audit.json',
    }
    assert len(card['submission_note']) <= 140
    save(ROOT / 'docs/data/run-card.json', card)
    save(ROOT / 'docs/data/latest-run-card.json', card)
    save(ROOT / 'docs/data/run_card.json', card)
    save(ROOT / 'evidence/run_card.json', card)
    save(ROOT / 'evidence/current_run_card.json', card)
    # Public copy for a Pages installation rooted at /docs or repository root.
    shutil.copyfile(audit_path, ROOT / 'docs/data/prior_candidate_audit.json')
    public_gpcz = ROOT / 'docs/data/run-card-gpcz.json'
    gc_old = load(public_gpcz)
    gc = {k: gc_old.get(k) for k in ('schema', 'created_utc', 'hypothesis', 'mechanism',
           'named_non_fault_mimic', 'raster_sha256', 'submission_name', 'submission_note')}
    # The original public card contained multiple incomparable metrics and a
    # stale assertion that all release gates passed; keep the full historical
    # source card as a link instead of repeating those claims as current data.
    gc.update(verdict='negative', ok_to_submit=False, download_available=False,
              historical_holdout_status='See evidence/run_card_gpcz.json; prior metrics have not been replayed.',
              literal_lattice_overlap=g['directed_overlap_fraction'],
              blockers=['Lattice overlap exceeds the literal limit; stop.'],
              correction='Superseded by the 2026-10-28 saved-byte audit.',
              full_card='evidence/run_card_gpcz.json')
    save(public_gpcz, gc)

    canary_path = ROOT / 'evidence/leakage_canary_58ch.json'
    canary = load(canary_path)
    canary.setdefault('prior_all_passed_before_review', canary['all_passed'])
    canary['all_passed'] = False
    canary['review_status'] = ('Not rerun. Footprint is constant in the evaluated footprint and '
                               'has mathematical AUC 0.5, but under the current conservative policy '
                               'that channel is untestable and cannot establish a feature-quality pass.')
    canary['untestable_features'] = ['footprint']
    for row in canary['channels']:
        if row['feature'] == 'footprint':
            row['status'] = 'constant_no_variation'
            row['passed_current_policy'] = False
    save(canary_path, canary)

    hedge_path = ROOT / 'evidence/hedge_sqrt_receipt_REJECTED_89pct_same_as_primary.json'
    hedge = load(hedge_path)
    hedge['uniqueness']['unique'] = False
    hedge['uniqueness']['rule_overlap_le_0.70'] = False
    hedge['correction'] = ('Historical receipt already recorded 99.897% overlap with the lattice but '
                           'incorrectly exempted it. The hedge remains rejected; not re-audited in this session.')
    hedge['verdict'] = 'negative'
    save(hedge_path, hedge)
    # Retain prior numerical diagnostics while withdrawing all derived clearance
    # and replacing unverified causal stories with explicit historical status.
    rows_path = ROOT / 'evidence/nine_site_audit.json'
    rows = load(rows_path)
    for row in rows:
        prior_badge = row.get('uniqueness_badge')
        if prior_badge and 'prior_relative_badge_unverified' not in row:
            row['prior_relative_badge_unverified'] = ('Old peer-pair diagnostic, not a full-registry gate; '
                                                       'see git history for the superseded wording.')
        if 'prior_relative_badge_unverified' in row:
            row['prior_relative_badge_unverified'] = ('Old peer-pair diagnostic, not a full-registry gate; '
                                                       'see git history for the superseded wording.')
        row['uniqueness_badge'] = 'FAIL — literal registered lattice witness'
        row['reported_score_status'] = 'USER-REPORTED / UNVERIFIED; no organizer receipt'
        row['prior_metrics_status'] = ('Historical diagnostics; not replayed 2026-10-28; '
                                       'not leaderboard scores or evidence of release approval.')
        if row['site'].startswith('GEMSDOEkarage1'):
            row.update(owner_score_label='NO VERIFIED PORTAL RESULT — DO NOT SUBMIT',
                       download_url=None, zip_download_url=None,
                       exec_summary='Inherited HMAS file fails literal lattice overlap; old gate and canary are superseded.')
        else:
            row['owner_score_label'] = f"{row['owner_reported_dti']} USER-REPORTED / UNVERIFIED"
            row['exec_summary'] = ('Historical peer research, not a verified score or new submission. '
                                   'See the pinned nine-site byte audit and source for provenance.')
    save(rows_path, rows)
    dashboard_path = ROOT / 'docs/data/dashboard_data.json'
    dashboard = load(dashboard_path)
    dashboard['run_card'] = card
    dashboard['experiments_summary'] = ledger
    dashboard['uniqueness_summary'] = {
        'passed': False, 'registry_complete': False,
        'literal_lattice_overlap': r['directed_overlap_fraction'],
        'evidence': 'data/prior_candidate_audit.json',
        'status': 'Prior fleet summary is superseded; only one registry witness was rechecked.'}
    dashboard['comparison_rows'] = rows
    dashboard['status'] = 'NEGATIVE — historical dashboard; no file is approved for upload.'
    dashboard['leakage_canary_status'] = 'Historical results not rerun; constant features cannot be treated as passed.'
    save(dashboard_path, dashboard)
    print('Historical releases superseded; current verdict: negative. No slot selected or spent.')


if __name__ == '__main__':
    main()
