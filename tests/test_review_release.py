"""Release decision and generator regression tests."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_runner_blocks_all_stages_before_any_writes(tmp_path):
    env = dict(os.environ, GEMS_DATA_DIR=str(tmp_path/'data'), GEMS_CACHE_DIR=str(tmp_path/'cache'))
    for stage in ('fit', 'eval', 'all'):
        p = subprocess.run([sys.executable, 'scripts/run_karage1_experiments.py', '--stage', stage],
                           cwd=ROOT, env=env, text=True, capture_output=True)
        assert p.returncode == 2 and 'BLOCKED' in p.stderr
    assert not (tmp_path/'data').exists() and not (tmp_path/'cache').exists()


def test_active_card_matches_real_saved_bytes_and_evidence():
    card = json.loads((ROOT/'docs/data/run-card.json').read_text())
    audit = json.loads((ROOT/'evidence/release_reassessment_20261028.json').read_text())
    assert card == json.loads((ROOT/'evidence/active_run_card_20261028.json').read_text())
    for alias in ('docs/data/run_card.json', 'evidence/run_card.json', 'evidence/current_run_card.json'):
        assert card == json.loads((ROOT/alias).read_text())
    assert card['verdict'] == 'negative' and not card['selector_approved'] and not card['ok_to_submit']
    assert card['holdout_dti']['independently_replayed_this_review'] is False
    assert card['correlation_overlap_vs_registry']['directed_overlap'] == audit['candidates']['hmas']['lattice_directed_overlap'] > .70
    assert len(card['submission_note']) <= 140
    assert hashlib.sha256((ROOT/'docs/downloads'/card['submission_file']).read_bytes()).hexdigest() == card['raster_sha256']
    assert not card['validator_output']['outside_null_or_nan']
    assert not card['validator_output']['portal_acceptance_tested']


def test_regenerators_keep_all_main_pages_negative():
    for script in ('build_site.py', 'generate_pages.py', 'build_gpcz_site.py', 'render_site.py', 'build_current_review.py', 'build_archived_lanes.py'):
        subprocess.run([sys.executable, 'scripts/'+script], cwd=ROOT, check=True)
    for name in ('index.html', 'docs/index.html', 'docs/executive-summary.html',
                 'docs/hmas-sinter/index.html', 'docs/hmas-sinter/executive-summary.html',
                 'docs/gpcz/index.html', 'docs/gpcz/how-to-submit.html', 'docs/how-to-submit.html',
                 'docs/legacy-executive-summary.html', 'docs/nine-sites.html', 'docs/gpcz/nine-sites.html',
                 'docs/gpcz/knowledge.html', 'docs/gpcz/sources.html', 'docs/sources.html'):
        text = (ROOT/name).read_text()
        assert 'DO NOT SUBMIT' in text, name
        assert 'OK TO SUBMIT' not in text and 'READY FOR PORTAL' not in text, name
    stale = subprocess.run([sys.executable, 'scripts/build_dashboard_and_figures.py'], cwd=ROOT, capture_output=True)
    assert stale.returncode != 0


def test_legacy_experiment_entrypoints_are_blocked_before_work():
    for script in ('run_experiment1_screen.py', 'run_experiment2_gpcz.py', 'run_experiment3_build.py'):
        p = subprocess.run([sys.executable, 'scripts/'+script], cwd=ROOT, text=True, capture_output=True)
        assert p.returncode == 2 and 'BLOCKED' in p.stderr


def test_legacy_pages_do_not_claim_approval_or_receipt():
    from html.parser import HTMLParser
    class Text(HTMLParser):
        def __init__(self):
            super().__init__(); self.parts = []
        def handle_data(self, data): self.parts.append(data)
    for path in (ROOT/'docs').rglob('*.html'):
        parser = Text(); parser.feed(path.read_text())
        text = ' '.join(parser.parts).lower()
        for false_claim in ('yes — gates passed', 'organizer-confirmed values', 'training faults are *not* masked',
                            '3 submissions/week', 'ready for portal', 'one cleared tiff'):
            assert false_claim not in text, (path, false_claim)
    assert 'ORGANIZER-CONFIRMED (owner ledger)' not in (ROOT/'registry/score_ledger.csv').read_text()


def test_independent_audits_and_compatibility_reconciler_agree():
    first = json.loads((ROOT/'evidence/prior_candidate_audit.json').read_text())
    second = json.loads((ROOT/'evidence/release_reassessment_20261028.json').read_text())
    for name in ('hmas', 'gpcz'):
        a, b = first['results'][name], second['candidates'][name]
        assert a['sha256'] == b['sha256']
        assert a['dots_within_closed_3px_disk'] == b['lattice_dots_within_3px_count']
    paths = [ROOT/'docs/data/run-card.json', ROOT/'evidence/active_run_card_20261028.json',
             ROOT/'evidence/release_gate_hmas_sinter.json', ROOT/'evidence/release_gate_gpcz.json']
    before = [p.read_bytes() for p in paths]
    subprocess.run([sys.executable, 'scripts/reconcile_prior_decisions.py'], cwd=ROOT, check=True)
    assert before == [p.read_bytes() for p in paths]
