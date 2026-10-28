"""Evidence policy only. No private metric/writer implementation and no portal upload."""
import math


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def assess(card):
    reasons = []
    if not isinstance(card, dict):
        return {'verdict': 'negative', 'ok_to_submit': False, 'reasons': ['Missing run card']}
    for key in ('hypothesis', 'mechanism', 'named_non_fault_mimic'):
        if not isinstance(card.get(key), str) or not card[key].strip():
            reasons.append('Missing scientific run-card field: ' + key)
    if not isinstance(card.get('lane'), str) or not card['lane'].strip():
        reasons.append('Named method lane missing')
    if type(card.get('experiments')) is not int or not 1 <= card['experiments'] <= 3:
        reasons.append('No completed experiment within budget')
    elapsed = card.get('elapsed_seconds')
    if not finite_number(elapsed) or not 0 < elapsed <= 7200:
        reasons.append('Elapsed-time budget not evidenced')
    h = card.get('holdout') if isinstance(card.get('holdout'), dict) else {}
    if (h.get('label') != 'HOLDOUT-DTI' or not isinstance(h.get('evaluator_version'), str)
            or not h['evaluator_version'].strip()
            or type(h.get('withheld_positives')) is not int or h['withheld_positives'] <= 0):
        reasons.append('Incomplete HOLDOUT-DTI provenance')
    score, ci = h.get('dti'), h.get('ci95')
    if (not finite_number(score) or not 0 <= score <= 1 or not isinstance(ci, list)
            or len(ci) != 2 or not all(finite_number(x) for x in ci)
            or not 0 <= ci[0] <= score <= ci[1] <= 1):
        reasons.append('Invalid holdout measurement or CI')
    best = h.get('current_best_dti')
    if (h.get('same_evaluator_as_best') is not True or h.get('beats_current_best') is not True
            or not finite_number(best) or not 0 <= best <= 1 or not finite_number(score) or score <= best
            or h.get('current_best_evaluator_version') != h.get('evaluator_version')):
        reasons.append('No same-evaluator improvement over holdout best')
    if (h.get('visible_only_features') is not True or h.get('whole_segment_buffered') is not True
            or h.get('visible_faults_masked_pixel_exact') is not True
            or h.get('alpha') != .2 or h.get('beta') != .8 or h.get('kernel_radius_m') != 300):
        reasons.append('Hide-and-recover leakage controls or metric parameters missing')
    canary = card.get('canary') if isinstance(card.get('canary'), dict) else {}
    aucs = canary.get('feature_aucs')
    statuses = canary.get('feature_status')
    expected_features = canary.get('expected_features')
    if (not isinstance(aucs, dict) or not aucs or canary.get('all_features_tested') is not True
            or canary.get('all_features_have_variation') is not True
            or canary.get('nonconstant_features_verified') is not True
            or canary.get('invalid_features') != []
            or not isinstance(statuses, dict) or set(statuses) != set(aucs)
            or any(v != 'tested' for v in statuses.values())
            or not isinstance(expected_features, list) or any(not isinstance(x, str) for x in expected_features)
            or len(expected_features) != len(set(expected_features)) or set(expected_features) != set(aucs)
            or any(not finite_number(v) or not .5 <= v <= .90 for v in aucs.values())):
        reasons.append('Single-feature leakage canary missing, untestable or failed')
    reg = card.get('registry') if isinstance(card.get('registry'), dict) else {}
    if (reg.get('complete') is not True or reg.get('saved_bytes_checked') is not True
            or reg.get('surface_checked_before_placement') is not True
            or reg.get('all_registry_rasters_included') is not True
            or reg.get('exact_ranks') is not True or reg.get('literal_all_rasters') is not True):
        reasons.append('Complete registry / pre-placement / saved-byte comparison missing')
    if reg.get('excluded_registry_rasters') != []:
        reasons.append('Registry exclusions are missing or nonempty')
    if reg.get('duplicate_witnesses') != []:
        reasons.append('Duplicate-witness ledger missing or nonempty')
    for key in ('inventory_sha256', 'preplacement_surface_sha256'):
        value = reg.get(key)
        if not isinstance(value, str) or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
            reasons.append('Registry receipt hash missing or invalid: ' + key)
    if (reg.get('preplacement_inventory_sha256') != reg.get('inventory_sha256')
            or reg.get('candidate_sha256') != card.get('raster_sha256')):
        reasons.append('Registry receipt is not bound to the same inventory and saved raster')
    records = reg.get('records')
    expected_count = reg.get('expected_count')
    if (not isinstance(records, list) or not records or type(expected_count) is not int
            or expected_count != len(records)):
        reasons.append('Per-raster registry evidence missing or incomplete')
    else:
        seen = set()
        for row in records:
            if not isinstance(row, dict) or not isinstance(row.get('id'), str) or not row['id'] or row['id'] in seen:
                reasons.append('Registry has invalid or repeated reference IDs')
                continue
            seen.add(row['id'])
            digest = row.get('sha256')
            if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
                reasons.append('Registry reference SHA-256 missing or invalid: ' + row['id'])
            for key, limit in [('surface_abs_rho', .90), ('dots_abs_rho', .90), ('directed_overlap_3px', .70)]:
                value = row.get(key)
                if not finite_number(value) or not 0 <= value <= limit:
                    reasons.append('Registry gate failed or missing: ' + row['id'] + ' / ' + key)
        # Summaries may not understate any measured witness. Never apply a
        # density, lattice, or "calibration probe" exemption here.
        for summary_key, row_key, limit in [('surface_max_abs_rho','surface_abs_rho',.90),
                                            ('dots_max_abs_rho','dots_abs_rho',.90),
                                            ('max_directed_overlap_3px','directed_overlap_3px',.70)]:
            value = reg.get(summary_key)
            vals = [r.get(row_key) for r in records if isinstance(r, dict)]
            if (not finite_number(value) or not 0 <= value <= limit or len(vals) != len(records)
                    or any(not finite_number(v) for v in vals)
                    or (vals and value < max(vals))):
                reasons.append('Registry summary missing or understates a reference: ' + summary_key)
    validator = card.get('validator') if isinstance(card.get('validator'), dict) else {}
    for key in ['single_band', 'float32', 'all_finite', 'range_0_1', 'crs_match', 'shape_match', 'transform_match',
                'outside_encoding_compatible', 'template_official_authenticated']:
        if validator.get(key) is not True:
            reasons.append('Saved TIFF validation missing or failed: ' + key)
    digest = card.get('raster_sha256')
    if validator.get('raster_sha256') != digest:
        reasons.append('Validator receipt is not bound to the saved raster')
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        reasons.append('Saved raster SHA-256 missing')
    note = card.get('submission_note')
    if (not isinstance(note, str) or not note.strip() or len(note) > 140
            or not isinstance(card.get('submission_name'), str) or not card['submission_name'].strip()):
        reasons.append('Submission name / short note missing')
    # Scientific promotion is NOT a weekly slot selection or upload authorization.
    return {'verdict': 'negative' if reasons else 'promote', 'ok_to_submit': False,
            'selector_required': True, 'reasons': reasons}
