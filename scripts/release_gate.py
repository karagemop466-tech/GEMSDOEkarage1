"""Evidence policy only. No private metric/writer implementation and no portal upload."""
import math


def finite_number(value):
    return type(value) in (int, float) and math.isfinite(value)


def assess(card):
    reasons = []
    if not isinstance(card, dict):
        return {'verdict': 'negative', 'ok_to_submit': False, 'reasons': ['Missing run card']}
    if not isinstance(card.get('lane'), str) or not card['lane'].strip():
        reasons.append('Named method lane missing')
    if type(card.get('experiments')) is not int or not 1 <= card['experiments'] <= 3:
        reasons.append('No completed experiment within budget')
    elapsed = card.get('elapsed_seconds')
    if not finite_number(elapsed) or not 0 < elapsed <= 7200:
        reasons.append('Elapsed-time budget not evidenced')
    h = card.get('holdout') if isinstance(card.get('holdout'), dict) else {}
    version = h.get('evaluator_version')
    if (h.get('label') != 'HOLDOUT-DTI' or not isinstance(version, str) or not version.strip()
            or type(h.get('withheld_positives')) is not int or h['withheld_positives'] <= 0):
        reasons.append('Incomplete HOLDOUT-DTI provenance')
    score, ci = h.get('dti'), h.get('ci95')
    if (not finite_number(score) or not 0 <= score <= 1 or not isinstance(ci, list)
            or len(ci) != 2 or not all(finite_number(x) for x in ci)
            or not 0 <= ci[0] <= score <= ci[1] <= 1):
        reasons.append('Invalid holdout measurement or CI')
    if h.get('same_evaluator_as_best') is not True or h.get('beats_current_best') is not True:
        reasons.append('No same-evaluator improvement over holdout best')
    if h.get('visible_only_features') is not True or h.get('whole_segment_buffered') is not True:
        reasons.append('Hide-and-recover leakage controls missing')
    canary = card.get('canary') if isinstance(card.get('canary'), dict) else {}
    aucs = canary.get('feature_aucs')
    if (not isinstance(aucs, dict) or not aucs or canary.get('all_features_tested') is not True
            or canary.get('all_features_have_variation') is not True
            or canary.get('invalid_features') != []
            # AUC below .10 is equally alarming after reversing its direction.
            or any(not finite_number(v) or not .10 <= v <= .90 for v in aucs.values())):
        reasons.append('Single-feature leakage canary missing or failed')
    reg = card.get('registry') if isinstance(card.get('registry'), dict) else {}
    if reg.get('complete') is not True or reg.get('saved_bytes_checked') is not True:
        reasons.append('Complete registry / saved-byte comparison missing')
    if reg.get('literal_all_rasters') is not True:
        reasons.append('Literal all-raster registry policy not evidenced')
    if reg.get('surface_checked_before_placement') is not True:
        reasons.append('Surface was not checked before placement')
    excluded = reg.get('excluded_registry_rasters')
    if not isinstance(excluded, list) or excluded:
        reasons.append('Registry exclusions are missing or nonempty')
    witnesses = reg.get('duplicate_witnesses')
    if not isinstance(witnesses, list):
        reasons.append('Registry duplicate-witness ledger missing')
    elif witnesses:
        reasons.append('A duplicate witness was recorded; stop')
    for key, limit in [('surface_max_abs_rho', .90), ('dots_max_abs_rho', .90), ('max_directed_overlap_3px', .70)]:
        value = reg.get(key)
        if not finite_number(value) or not 0 <= value <= limit:
            reasons.append('Registry gate failed or missing: ' + key)
    validator = card.get('validator') if isinstance(card.get('validator'), dict) else {}
    for key in ['single_band', 'float32', 'all_finite', 'range_0_1', 'crs_match', 'shape_match', 'transform_match']:
        if validator.get(key) is not True:
            reasons.append('Saved TIFF validation missing or failed: ' + key)
    digest = card.get('raster_sha256')
    if not isinstance(digest, str) or len(digest) != 64 or any(c not in '0123456789abcdef' for c in digest):
        reasons.append('Saved raster SHA-256 missing')
    note = card.get('submission_note')
    name = card.get('submission_name')
    if (not isinstance(note, str) or not note.strip() or len(note) > 140
            or not isinstance(name, str) or not name.strip()):
        reasons.append('Submission name / short note missing')
    # Scientific promotion is NOT a weekly slot selection or upload authorization.
    return {'verdict': 'negative' if reasons else 'promote', 'ok_to_submit': False,
            'selector_required': True, 'reasons': reasons}
