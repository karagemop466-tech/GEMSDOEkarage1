import copy
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('gate', Path(__file__).parents[1] / 'scripts/release_gate.py')
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def good():
    row = dict(id='lattice', sha256=gate._lattice_pin(), surface_spearman=.1, dot_spearman=.1,
               dots_within_3px=20, candidate_dots=100, identical_bytes=False, identical_pixels=False)
    return dict(lane='test-only-method', hypothesis='synthetic', mechanism='synthetic',
                named_non_fault_mimic='synthetic', experiments=1, elapsed_seconds=60,
                holdout=dict(label='HOLDOUT-DTI', evaluator_version='test-only', withheld_positives=10,
                             dti=.2, ci95=[.1,.3], baseline_dti=.1, baseline_evaluator_version='test-only',
                             paired_delta_ci95=[.01,.15], same_evaluator_as_best=True, visible_only_features=True,
                             fold_assignment_sha256='e'*64, baseline_fold_assignment_sha256='e'*64,
                             whole_segment_buffered=True, pixel_exact_visible_mask=True, alpha=.2, beta=.8,
                             kernel_radius_m=300),
                canary=dict(feature_aucs={'a': .6}, feature_status={'a': 'tested'}, expected_features=['a'],
                            all_features_tested=True, passed=True, n_features=1, nonconstant_features_verified=True,
                            all_features_have_variation=True, invalid_features=[]),
                registry=dict(complete=True, saved_bytes_checked=True, all_registry_rasters_included=True,
                              literal_all_rasters=True, excluded_registry_rasters=[], duplicate_witnesses=[],
                              exact_ranks=True, surface_checked_before_placement=True, inventory_sha256='b'*64,
                              preplacement_inventory_sha256='b'*64, preplacement_surface_sha256='c'*64,
                              candidate_sha256='a'*64, expected_rasters=1, comparisons=[row]),
                validator={**{k:True for k in ['single_band','float32','all_finite_inside','range_0_1_inside',
                                            'crs_match','shape_match','transform_match','outside_encoding_accepted',
                                            'template_official_authenticated']},
                           'candidate_sha256': 'a'*64, 'template_sha256': 'f'*64},
                raster_sha256='a'*64, submission_name='test',
                submission_note='Synthetic unit-test evidence, not a scientific result.')


def test_missing():
    assert gate.assess(None)['verdict'] == 'negative'
    assert gate.assess({})['verdict'] == 'negative'


def test_promotion_never_selects_slot():
    result = gate.assess(good())
    assert result['verdict'] == 'promote'
    assert result['ok_to_submit'] is False
    assert result['selector_required'] is True


@pytest.mark.parametrize('path,value', [
    ('lane',None),('hypothesis',''),('mechanism',None),('named_non_fault_mimic',''),
    ('experiments',True),('experiments',0),('experiments',4),('elapsed_seconds',7201),
    ('holdout.dti',float('nan')),('holdout.ci95',[.3,.1]),('holdout.withheld_positives',0),
    ('holdout.baseline_evaluator_version','other'),('holdout.alpha',.1),('holdout.beta',.5),
    ('holdout.kernel_radius_m',299),
    ('holdout.same_evaluator_as_best',False),('holdout.visible_only_features',False),
    ('holdout.baseline_dti',.2),('holdout.paired_delta_ci95',[-.01,.01]),
    ('holdout.fold_assignment_sha256',None),('holdout.fold_assignment_sha256','z'*64),
    ('holdout.baseline_fold_assignment_sha256','d'*64),
    ('holdout.paired_delta_ci95',[.3,.4]), ('holdout.paired_delta_ci95',[.01,1.1]),
    ('holdout.whole_segment_buffered',False),('holdout.pixel_exact_visible_mask',False),
    ('canary.feature_aucs',{}),('canary.feature_aucs',{'bad':.901}),
    ('canary.feature_aucs',{'bad':float('nan')}),('canary.feature_aucs',{'bad':.05}),
    ('canary.all_features_tested',False),('canary.passed',False),('canary.n_features',2),
    ('canary.nonconstant_features_verified',False), ('canary.all_features_have_variation',False),
    ('canary.invalid_features',['a']), ('canary.feature_status',{'a':'untestable'}),
    ('canary.expected_features',['a','b']), ('holdout.evaluator_version',True),
    ('registry.complete',False),('registry.saved_bytes_checked',False),
    ('registry.all_registry_rasters_included',False),('registry.exact_ranks',False),
    ('registry.literal_all_rasters',False),('registry.excluded_registry_rasters',['lattice']),
    ('registry.duplicate_witnesses',['lattice']),
    ('registry.surface_checked_before_placement',False),('registry.inventory_sha256','z'*64),
    ('registry.preplacement_surface_sha256',None),('registry.preplacement_inventory_sha256','d'*64),
    ('registry.candidate_sha256','d'*64),
    ('registry.expected_rasters',2),('registry.comparisons',[]),
    ('validator.range_0_1_inside',False),('validator.all_finite_inside',False),
    ('validator.transform_match',False),('validator.outside_encoding_accepted',False),
    ('validator.template_official_authenticated',False),
    ('validator.candidate_sha256','b'*64),('validator.candidate_sha256',None),
    ('validator.template_sha256',None),('validator.template_sha256','z'*64),
    ('raster_sha256','z'*64),('submission_note','   '),('submission_note','x'*141)])
def test_fail_closed(path,value):
    card=copy.deepcopy(good())
    parts=path.split('.')
    node=card
    for part in parts[:-1]:
        node=node[part]
    node[parts[-1]]=value
    assert gate.assess(card)['verdict']=='negative'


@pytest.mark.parametrize('key,value', [
    ('id','other'), ('sha256','a'*64), ('surface_spearman',.901), ('surface_spearman',None),
    ('dot_spearman',-.901), ('dots_within_3px',71), ('candidate_dots',0),
    ('identical_bytes',True), ('identical_pixels',True),
])
def test_literal_witness_cannot_be_omitted_or_exempted(key, value):
    card=good()
    card['registry']['comparisons'][0][key]=value
    assert gate.assess(card)['verdict']=='negative'


def test_exact_thresholds_are_not_strict_exceedances():
    card=good()
    card['registry']['comparisons'][0].update(surface_spearman=.90,dot_spearman=.90,dots_within_3px=70)
    card['canary']['feature_aucs']={'a':.90}
    assert gate.assess(card)['verdict']=='promote'


@pytest.mark.parametrize('key', ['holdout', 'registry', 'canary', 'validator'])
def test_malformed_sections(key):
    card=good()
    card[key]='not evidence'
    assert gate.assess(card)['verdict']=='negative'


def test_real_prior_claims_are_no_longer_cleared():
    import json
    root=Path(__file__).resolve().parents[1]
    for name in ('release_gate_hmas_sinter.json', 'release_gate_gpcz.json'):
        report=json.loads((root/'evidence'/name).read_text())
        result=gate.assess(report['input'])
        assert result['verdict']=='negative'
        assert not result['ok_to_submit']
        assert any('lattice' in reason.lower() for reason in result['reasons'])


def test_inconsistent_candidate_dot_counts_fail_closed():
    card = copy.deepcopy(good())
    second = dict(card['registry']['comparisons'][0])
    second.update(id='another', sha256='b' * 64, candidate_dots=200)
    card['registry']['comparisons'].append(second)
    card['registry']['expected_rasters'] = 2
    result = gate.assess(card)
    assert result['verdict'] == 'negative'
    assert any('dot counts disagree' in reason for reason in result['reasons'])


def test_matching_registry_hash_cannot_be_overridden_by_identity_flags():
    card = copy.deepcopy(good())
    second = dict(card['registry']['comparisons'][0])
    second.update(id='other', sha256=card['raster_sha256'], identical_bytes=False,
                  identical_pixels=False)
    card['registry']['comparisons'].append(second)
    card['registry']['expected_rasters'] = 2
    result = gate.assess(card)
    assert result['verdict'] == 'negative'
    assert any('Candidate hash matches registry raster' in reason for reason in result['reasons'])


def test_duplicate_registry_hashes_and_whitespace_ids_and_self_template_fail_closed():
    card = copy.deepcopy(good())
    duplicate_hash = dict(card['registry']['comparisons'][0])
    duplicate_hash['id'] = 'distinct-id-same-hash'
    card['registry']['comparisons'].append(duplicate_hash)
    card['registry']['expected_rasters'] = 2
    result = gate.assess(card)
    assert result['verdict'] == 'negative'
    assert any('Duplicate registry raster hash' in reason for reason in result['reasons'])

    ws_card = copy.deepcopy(good())
    ws_card['registry']['comparisons'][0]['id'] = '   '
    ws_res = gate.assess(ws_card)
    assert ws_res['verdict'] == 'negative'
    assert any('Missing or duplicate registry identity' in reason for reason in ws_res['reasons'])

    self_tmpl = copy.deepcopy(good())
    self_tmpl['validator']['template_sha256'] = self_tmpl['raster_sha256']
    self_res = gate.assess(self_tmpl)
    assert self_res['verdict'] == 'negative'
    assert any('Saved TIFF validation not bound' in reason for reason in self_res['reasons'])

    null_bind = copy.deepcopy(good())
    null_bind['raster_sha256'] = None
    null_bind['registry']['candidate_sha256'] = None
    null_res = gate.assess(null_bind)
    assert null_res['verdict'] == 'negative'
    assert any('Registry receipt is not bound' in reason for reason in null_res['reasons'])


def test_historical_hedge_does_not_exempt_its_lattice_witness():
    import json
    root = Path(__file__).parents[1]
    hedge = json.loads((root / 'evidence/hedge_sqrt_receipt_REJECTED_89pct_same_as_primary.json').read_text())
    rows = hedge['uniqueness']['rows']
    lattice = next(r for r in rows if 'lattice' in r['registry_id'])
    assert lattice['frac_our_dots_within_3px'] > .7
    assert hedge['uniqueness']['original_unique_superseded'] is True
    assert hedge['uniqueness']['unique'] is False
    assert hedge['approved_for_weekly_slot'] is False
