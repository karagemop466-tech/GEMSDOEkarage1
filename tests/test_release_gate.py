import copy
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('gate', Path(__file__).parents[1] / 'scripts/release_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def good():
    return dict(lane='test-only-method', experiments=1, elapsed_seconds=60,
                holdout=dict(label='HOLDOUT-DTI', evaluator_version='test-only', withheld_positives=10,
                             dti=.2, ci95=[.1,.3], same_evaluator_as_best=True, beats_current_best=True,
                             visible_only_features=True, whole_segment_buffered=True),
                canary=dict(feature_aucs={'a': .6}, all_features_tested=True, all_features_have_variation=True, invalid_features=[]),
                registry=dict(complete=True, saved_bytes_checked=True, literal_all_rasters=True,
                              surface_checked_before_placement=True, excluded_registry_rasters=[], duplicate_witnesses=[], surface_max_abs_rho=.1,
                              dots_max_abs_rho=.1, max_directed_overlap_3px=.2),
                validator={k:True for k in ['single_band','float32','all_finite','range_0_1','crs_match','shape_match','transform_match']},
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
    ('canary.feature_aucs',{'bad':float('nan')}),('canary.feature_aucs',{'inverse':.099}),
    ('canary.all_features_tested',False),('canary.all_features_have_variation',False),('canary.invalid_features',['constant']),
    ('registry.complete',False),('registry.saved_bytes_checked',False),
    ('registry.literal_all_rasters',False),('registry.surface_checked_before_placement',False),
    ('registry.excluded_registry_rasters',['lattice']),('registry.excluded_registry_rasters',None),
    ('registry.duplicate_witnesses',[{'lattice':.99}]),('registry.duplicate_witnesses',None),
    ('registry.surface_max_abs_rho',.901),('registry.dots_max_abs_rho',.901),
    ('registry.max_directed_overlap_3px',.701),('validator.range_0_1',False),
    ('validator.all_finite',False),('validator.transform_match',False),
    ('raster_sha256','z'*64),('submission_name',True),('submission_name','  '),('submission_note','  '),('submission_note','x'*141)])
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
    card['canary']['feature_aucs']={'edge':.90}
    assert gate.assess(card)['verdict']=='promote'


@pytest.mark.parametrize("key", ["holdout", "registry", "canary", "validator"])
def test_malformed_sections(key):
    card=good()
    card[key]="not evidence"
    assert gate.assess(card)["verdict"]=="negative"
