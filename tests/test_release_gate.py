import copy
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('gate', Path(__file__).parents[1] / 'scripts/release_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def good():
    return dict(lane='test-only-method', hypothesis='synthetic fault hypothesis',
                mechanism='synthetic mechanism', named_non_fault_mimic='synthetic lithologic contact',
                experiments=1, elapsed_seconds=60,
                holdout=dict(label='HOLDOUT-DTI', evaluator_version='test-only', withheld_positives=10,
                             dti=.2, ci95=[.1,.3], same_evaluator_as_best=True, beats_current_best=True,
                             current_best_dti=.15, current_best_evaluator_version='test-only',
                             visible_only_features=True, whole_segment_buffered=True,
                             visible_faults_masked_pixel_exact=True, alpha=.2, beta=.8, kernel_radius_m=300),
                canary=dict(feature_aucs={'a': .6}, all_features_tested=True,
                            feature_status={'a': 'tested'}, expected_features=['a'], all_features_have_variation=True,
                            nonconstant_features_verified=True, invalid_features=[]),
                registry=dict(complete=True, saved_bytes_checked=True, surface_checked_before_placement=True,
                              all_registry_rasters_included=True, exact_ranks=True, literal_all_rasters=True,
                              excluded_registry_rasters=[], duplicate_witnesses=[],
                              expected_count=1, inventory_sha256='c'*64, preplacement_inventory_sha256='c'*64,
                              preplacement_surface_sha256='d'*64, candidate_sha256='a'*64,
                              records=[dict(id='prior', sha256='b'*64,
                                  surface_abs_rho=.1, dots_abs_rho=.1, directed_overlap_3px=.2)],
                              surface_max_abs_rho=.1, dots_max_abs_rho=.1, max_directed_overlap_3px=.2),
                validator={**{k:True for k in ['single_band','float32','all_finite','range_0_1','crs_match',
                          'shape_match','transform_match','outside_encoding_compatible','template_official_authenticated']},
                          'raster_sha256':'a'*64},
                raster_sha256='a'*64, submission_name='test', submission_note='Synthetic unit-test evidence, not a scientific result.')


def test_missing():
    assert gate.assess(None)['verdict'] == 'negative'
    assert gate.assess({})['verdict'] == 'negative'


def test_promotion_never_selects_slot():
    result = gate.assess(good())
    assert result['verdict'] == 'promote'
    assert result['ok_to_submit'] is False


@pytest.mark.parametrize('path,value', [
    ('lane',None),('experiments',True),('experiments',0),('experiments',4),('elapsed_seconds',7201),
    ('holdout.dti',float('nan')),('holdout.ci95',[.3,.1]),('holdout.withheld_positives',0),
    ('holdout.same_evaluator_as_best',False),('holdout.visible_only_features',False),
    ('holdout.beats_current_best',False),('holdout.whole_segment_buffered',False),
    ('canary.feature_aucs',{}),('canary.feature_aucs',{'bad':.901}),
    ('canary.feature_aucs',{'bad':float('nan')}),('canary.all_features_tested',False),
    ('canary.all_features_have_variation',False),('canary.nonconstant_features_verified',False),('canary.invalid_features',['constant']),
    ('registry.complete',False),('registry.saved_bytes_checked',False),('registry.excluded_registry_rasters',['lattice']),
    ('registry.duplicate_witnesses',[{'witness':.99}]),('registry.literal_all_rasters',False),
    ('registry.all_registry_rasters_included',False),('registry.exact_ranks',False),
    ('registry.surface_max_abs_rho',.901),('registry.dots_max_abs_rho',.901),
    ('registry.max_directed_overlap_3px',.701),('validator.range_0_1',False),
    ('validator.all_finite',False),('validator.transform_match',False),
    ('raster_sha256','z'*64),('submission_note','  '),('submission_name',True),('submission_note','x'*141)])
def test_fail_closed(path,value):
    card=copy.deepcopy(good())
    parts=path.split('.')
    node=card
    for part in parts[:-1]:
        node=node[part]
    node[parts[-1]]=value
    assert gate.assess(card)['verdict']=='negative'


def test_exact_thresholds():
    card=good()
    card['registry'].update(surface_max_abs_rho=.90,dots_max_abs_rho=.90,max_directed_overlap_3px=.70)
    card['canary']['feature_aucs']={'a':.90}
    card['registry']['records'][0].update(surface_abs_rho=.90,dots_abs_rho=.90,directed_overlap_3px=.70)
    assert gate.assess(card)['verdict']=='promote'


@pytest.mark.parametrize("key", ["holdout", "registry", "canary", "validator"])
def test_malformed_sections(key):
    card=good()
    card[key]="not evidence"
    assert gate.assess(card)["verdict"]=="negative"


def test_one_bad_reference_cannot_be_hidden_by_summary_or_calibration_label():
    card = good()
    card['registry']['expected_count'] = 2
    card['registry']['records'].append(dict(id='lattice-calibration', sha256='c'*64,
                                           surface_abs_rho=.1, dots_abs_rho=.1, directed_overlap_3px=.95))
    card['registry']['max_directed_overlap_3px'] = .2  # falsely low summary
    result = gate.assess(card)
    assert result['verdict'] == 'negative'
    assert any('lattice-calibration' in reason for reason in result['reasons'])
    assert any('understates' in reason for reason in result['reasons'])


def test_bool_improvement_claim_cannot_replace_comparable_measurements():
    card = good()
    card['holdout']['current_best_dti'] = .21
    assert gate.assess(card)['verdict'] == 'negative'
    card = good()
    card['holdout']['current_best_evaluator_version'] = 'different'
    assert gate.assess(card)['verdict'] == 'negative'


@pytest.mark.parametrize('key,value', [
    ('expected_features', ['a', 'missing']), ('feature_status', {'a':'constant_no_variation'}),
    ('feature_aucs', {'a':.49}), ('feature_aucs', {'a':float('nan')})])
def test_canary_never_ignores_missing_or_untestable_channels(key, value):
    card = good()
    card['canary'][key] = value
    assert gate.assess(card)['verdict'] == 'negative'


@pytest.mark.parametrize('section,key,value', [
    ('registry', 'candidate_sha256', 'f'*64),
    ('registry', 'preplacement_inventory_sha256', 'f'*64),
    ('registry', 'preplacement_surface_sha256', None),
    ('validator', 'raster_sha256', 'f'*64),
])
def test_release_receipts_must_match_candidate_and_inventory(section, key, value):
    card = good()
    card[section][key] = value
    assert gate.assess(card)['verdict'] == 'negative'


def test_historical_lattice_witness_is_negative():
    import json
    root = Path(__file__).parents[1]
    scan = json.loads((root/'evidence/fleet_uniqueness_593.json').read_text())
    assert any('lattice' in r['ref'] and r['cand_in_ref_3px'] > .70 for r in scan['non_competing_lattice_or_continuous_rasters_gt_70pct_cov'])
    prior = json.loads((root/'evidence/release_gate_hmas_sinter.json').read_text())
    assert gate.assess(prior['input'])['verdict'] == 'negative'
