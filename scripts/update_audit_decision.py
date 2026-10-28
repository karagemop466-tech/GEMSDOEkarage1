#!/usr/bin/env python3
"""Synchronize current decisions with the independent saved-byte audit.

Historical scientific claims are retained as historical records; the prior
promotion is superseded. This routine never writes predictions or selects slots.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.release_gate import assess
from scripts.audit_references import sha256

AUDIT_PATH = ROOT / 'evidence/candidate_audit_20261028.json'


def load(path):
    return json.loads(path.read_text())


def save(path, value):
    text = json.dumps(value, indent=2, allow_nan=False) + '\n'
    fd, name = tempfile.mkstemp(prefix='.' + path.name + '.', suffix='.partial', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            out.write(text)
        os.chmod(name, 0o644)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def main():
    audit = load(AUDIT_PATH)
    if (audit.get('schema') != 'karage1-existing-candidate-audit-v1'
            or audit.get('upload_authorized') is not False or audit.get('registry_complete') is not False):
        raise ValueError('audit is missing or malformed')
    candidates = audit.get('candidates', [])
    historical = (load(ROOT / 'evidence/run_card_hmas_sinter.json'),
                  load(ROOT / 'evidence/run_card_gpcz.json'))
    expected_files = (historical[0]['submission_file'], historical[1]['raster']['zeros_tif'])
    expected_hashes = (historical[0]['raster_sha256'], historical[1]['raster']['sha256'])
    lattice_pin = next(x['sha256'] for x in load(ROOT / 'registry/reference_assets.json') if x['id'] == 'lattice')
    if len(candidates) != 2:
        raise ValueError('expected both historical candidate audits')
    for c, expected_file, expected_hash in zip(candidates, expected_files, expected_hashes):
        path = ROOT / 'docs/downloads' / c['file']
        witness = c['comparisons'][0] if c['comparisons'] else None
        if (c['file'] != expected_file or c['sha256'] != expected_hash or sha256(path) != c['sha256']
                or c['verdict'] != 'duplicate' or not witness or witness['reference'] != 'lattice'
                or witness['reference_sha256'] != lattice_pin or not witness['overlap_exceeds_70_percent']
                or witness['candidate_dots'] != c['positive_pixels_in_footprint']
                or witness['candidate_dots_within_3px'] * 10 <= witness['candidate_dots'] * 7
                or abs(witness['directed_overlap'] - witness['candidate_dots_within_3px'] / witness['candidate_dots']) > 1e-12):
            raise ValueError(f"candidate audit inconsistent: {c.get('file')}")

    notice = ('SUPERSEDED 2026-10-28: the earlier promotion exempted a registered lattice. '
              'The independent saved-byte audit applies the literal protocol; this artifact is a duplicate. '
              'Prior holdout figures are retained as unverified historical claims, not reproduced here.')
    for label, candidate in zip(('hmas_sinter', 'gpcz'), candidates):
        path = ROOT / f'evidence/release_gate_{label}.json'
        gate = load(path)
        if 'original_result_superseded' not in gate:
            gate['original_result_superseded'] = gate.get('result')
        reg = gate['input'].get('registry', {})
        if 'superseded_registry_summary' not in gate:
            gate['superseded_registry_summary'] = dict(reg)
        reg['complete'] = False
        reg['saved_bytes_checked'] = True
        reg['expected_rasters'] = len(candidate['comparisons'])
        reg['comparisons'] = [dict(
            id=r['reference'], sha256=r['reference_sha256'], surface_spearman=None,
            dot_spearman=r['binary_dot_spearman'], dots_within_3px=r['candidate_dots_within_3px'],
            candidate_dots=r['candidate_dots'], identical_bytes=candidate['sha256'] == r['reference_sha256'],
            identical_pixels=r['exact_dot_mask_match']) for r in candidate['comparisons']]
        gate['input']['registry'] = reg
        gate['input']['canary']['passed'] = False
        gate['input']['canary']['status'] = 'Historical canary implementation could mask invalid or constant data; not independently established.'
        gate['result'] = assess(gate['input'])
        gate['supersession_notice'] = notice
        save(path, gate)

    for filename in ('run_card_hmas_sinter.json', 'run_card_gpcz.json'):
        path = ROOT / 'evidence' / filename
        data = load(path)
        data.setdefault('original_verdict_superseded', data.get('verdict'))
        data['verdict'] = 'negative'
        data['ok_to_submit'] = False
        if filename == 'run_card_gpcz.json':
            data['uniqueness']['unique'] = False
            data['uniqueness']['rule_overlap_le_0.70'] = False
            data['uniqueness']['literal_lattice_overlap'] = candidates[1]['comparisons'][0]['directed_overlap']
            data['verdict_reason'] = 'Literal lattice overlap exceeds 70%; prior restricted-registry pass is superseded.'
            data['leakage_canary'].setdefault('original_verdict_superseded', data['leakage_canary'].get('verdict'))
            data['leakage_canary']['verdict'] = 'not established; historical output was not independently reproduced'
        else:
            data['registry_correlation_overlap']['literal_lattice_overlap'] = candidates[0]['comparisons'][0]['directed_overlap']
            data['registry_correlation_overlap']['literal_uniqueness_passed'] = False
        data['supersession_notice'] = notice
        data['independent_audit'] = 'evidence/candidate_audit_20261028.json'
        save(path, data)

    path = ROOT / 'evidence/fleet_uniqueness_593.json'
    fleet = load(path)
    fleet.setdefault('original_passed_superseded', fleet.get('passed'))
    fleet['passed'] = False
    fleet['supersession_notice'] = notice
    fleet['literal_lattice_overlap'] = candidates[0]['comparisons'][0]['directed_overlap']
    fleet['independent_audit'] = 'evidence/candidate_audit_20261028.json'
    save(path, fleet)

    path = ROOT / 'evidence/experiments_summary.json'
    ledger = load(path)
    ledger.setdefault('original_verdict_superseded', ledger.get('verdict'))
    ledger['verdict'] = 'negative'
    ledger['supersession_notice'] = notice
    if isinstance(ledger.get('gates'), dict):
        ledger['gates']['uniqueness_gate_passed'] = False
        ledger['gates']['leakage_canary_passed'] = False
    ledger['holdout_reproduced_this_session'] = False
    save(path, ledger)

    path = ROOT / 'evidence/leakage_canary_58ch.json'
    canary = load(path)
    canary.setdefault('original_all_passed_superseded', canary.get('all_passed'))
    canary['all_passed'] = False
    canary['validation_status'] = ('Not established: historical implementation substitutes zero for nonfinite values '
                                   'and treats constant features as AUC 0.5; reported AUCs were not reproduced.')
    save(path, canary)

    hedge_path = ROOT / 'evidence/hedge_sqrt_receipt_REJECTED_89pct_same_as_primary.json'
    hedge = load(hedge_path)
    hedge['uniqueness'].setdefault('original_unique_superseded', hedge['uniqueness'].get('unique'))
    hedge['uniqueness']['unique'] = False
    hedge['uniqueness']['rule_overlap_le_0.70'] = False
    hedge['supersession_notice'] = ('Historical receipt only; its own lattice row reports 99.8972% overlap, '
                                   'which violates the literal rule. Hedge raster bytes were not rechecked in this session.')
    hedge['approved_for_weekly_slot'] = False
    save(hedge_path, hedge)

    receipt = ROOT / 'docs/downloads' / (Path(candidates[0]['file']).stem + '.json')
    receipt_data = load(receipt)
    receipt_data['promoted'] = False
    receipt_data['approved_for_weekly_slot'] = False
    receipt_data['uniqueness_gate_passed'] = False
    receipt_data['verdict'] = 'negative'
    receipt_data['supersession_notice'] = notice
    save(receipt, receipt_data)
    gp_receipt = next((ROOT / 'docs/downloads').glob('gemsk1-*-receipt.json'))
    receipt_data = load(gp_receipt)
    receipt_data['verdict'] = 'negative'
    receipt_data['approved_for_weekly_slot'] = False
    receipt_data['supersession_notice'] = notice
    save(gp_receipt, receipt_data)

    existing = load(ROOT / 'docs/data/run-card.json')
    if (existing.get('lane') == 'H-K1-BBSTEP' and existing.get('verdict') == 'negative'
            and existing.get('ok_to_submit') is False and existing.get('slot_selected_or_spent') is False):
        print('Reconciled historical receipts; preserved current negative BB-STEP card; no slot selected.')
        return

    c = candidates[0]
    lattice = c['comparisons'][0]
    current = {
        'schema': 'karage1-run-card-v2',
        'created_utc': audit['created_utc'],
        'session': 'arena/9a5c837d-gemsdoekarage1',
        'hypothesis': 'Historical H-K1-1 hydrothermal magnetic-trough and thermal/sinter conduit hypothesis; no new lane assigned.',
        'mechanism': 'The prior candidate combined potential-field, terrain and hydrothermal proxy features with sparse dot placement; this session audits its saved bytes only.',
        'named_non_fault_mimic': 'Lithologic contacts and Lake Lahontan shorelines can resemble the proposed structural signal.',
        'holdout_dti': {'label': 'HOLDOUT-DTI', 'value': None, 'evaluator_version': None,
                        'withheld_positives': None, 'ci95': None,
                        'status': 'Not run in this session; prior claims were not independently reproduced.'},
        'correlation_overlap_vs_registry': {
            'preplacement_surface_spearman': None,
            'final_dot_spearman_vs_lattice': lattice['binary_dot_spearman'],
            'final_dot_overlap_vs_lattice': lattice['directed_overlap'],
            'overlapping_dots': lattice['candidate_dots_within_3px'],
            'candidate_dots': lattice['candidate_dots'],
            'registry_coverage': audit['reference_scope'],
            'registry_complete': False,
        },
        'raster_sha256': c['sha256'],
        'raster_status': 'Existing historical artifact; not generated in this session; duplicate under literal registry rule.',
        'validator_output': {
            'no_nan_inside_footprint': c['format_checks']['no_nonfinite_inside'],
            'values_in_0_1': c['format_checks']['inside_values_in_0_1'],
            'crs_shape_transform_match': c['format_checks']['crs_shape_transform_match_mirror'],
            'all_finite_whole_array': c['format_checks']['whole_array_strict_finite_0_1'],
            'outside_null_or_nan': c['format_checks']['outside_all_null_or_nan'],
            'reference': 'Hash-pinned owner mirror; organizer authenticity not established.',
            'portal_acceptance': 'not tested',
        },
        'submission_name': c['file'],
        'submission_note': 'Historical HMAS candidate: audit only; fails literal lattice overlap gate. Do not submit.',
        'download_available': False,
        'download_available_meaning': 'No submission-ready download; clearly labeled historical files remain available for research only.',
        'ok_to_submit': False,
        'slot_selected_or_spent': False,
        'geological_experiments_run_this_session': 0,
        'blockers': [
            'Both existing candidates exceed the literal 70% overlap limit against the registered lattice; stop.',
            'The current prompt does not provide the referenced single method-lane paragraph.',
            'The complete current registry, pre-placement surfaces, cached shared feature stack and a comparable current-best holdout are not established.',
            'The mirrored sample is not organizer-authenticated; zeros outside its footprint are not the published null/NaN convention.',
        ],
        'verdict': 'negative',
        'audit': 'evidence/candidate_audit_20261028.json',
    }
    if len(current['submission_note']) > 140:
        raise ValueError('note too long')
    for path in ('docs/data/run-card.json', 'docs/data/latest-run-card.json',
                 'docs/data/run_card.json', 'evidence/run_card.json', 'evidence/current_run_card.json',
                 'evidence/active_run_card_20261028.json'):
        save(ROOT / path, current)

    gp_path = ROOT / 'docs/data/run-card-gpcz.json'
    gp = load(gp_path)
    gp.setdefault('original_verdict_superseded', gp.get('verdict'))
    gp.update(verdict='negative', ok_to_submit=False, download_available=False,
              ok_to_submit_meaning='False: literal lattice duplicate. Scientific promotion and weekly selection are separate; neither is authorized.',
              supersession_notice=notice, full_card=load(ROOT / 'evidence/run_card_gpcz.json'))
    gp['correlation_overlap_vs_registry'] = {
        'literal_lattice_overlap': candidates[1]['comparisons'][0]['directed_overlap'],
        'preplacement_surface_spearman': None, 'registry_complete': False}
    save(gp_path, gp)

    dashboard_path = ROOT / 'docs/data/dashboard_data.json'
    dashboard = {'schema': 'karage1-dashboard-decision-v2', 'current_verdict': 'negative',
                 'run_card': current, 'supersession_notice': notice,
                 'historical_reports': ['evidence/experiments_summary.json',
                                        'evidence/leakage_canary_58ch.json',
                                        'evidence/fleet_uniqueness_593.json']}
    save(dashboard_path, dashboard)
    print('Reconciled historical receipts and published a negative current card; no slot selected.')


if __name__ == '__main__':
    main()
