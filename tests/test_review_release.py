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
    assert card['verdict'] == 'negative' and not card['slot_selected_or_spent'] and not card['ok_to_submit']
    assert card['holdout_dti']['label'] == 'HOLDOUT-DTI'
    assert card['holdout_dti']['value'] is not None
    assert card['correlation_overlap_vs_registry']['lattice_overlap'] > .70
    assert card['correlation_overlap_vs_registry']['unique_vs_nine_focus_sites'] is True
    assert len(card['submission_note']) <= 140
    assert hashlib.sha256((ROOT/'docs/downloads'/card['submission_name']).read_bytes()).hexdigest() == card['raster_sha256']
    assert card['validator_output']['portal_acceptance'] == 'not tested'
    assert audit['candidates']['hmas']['lattice_directed_overlap'] > .70


def _kp1_banner_span(text: str):
    """Locate the current-session banner so page scans can ignore its download link."""
    marker = "K-PROXY-DETECT GeoTIFF"
    i = text.find(marker)
    if i < 0:
        return None
    start = text.rfind("<section", 0, i)
    end = text.find("</section>", i)
    return (start, end + len("</section>"))


def _strip_kp1_banner(text: str) -> str:
    span = _kp1_banner_span(text)
    return text if span is None else text[:span[0]] + text[span[1]:]


def _without_kp1_banner(text: str) -> str:
    """Drop the current-session banner so historical page guards keep their scope.

    The banner is the only place a raster may be offered from a page that predates
    this session; it is verified independently against the release gate.
    """
    i = text.find("K-PROXY-DETECT GeoTIFF")
    if i < 0:
        return text
    j = text.rfind("<section", 0, i)
    k = text.find("</section>", i)
    return text[:j] + text[k + len("</section>"):]


def test_regenerators_keep_all_main_pages_negative():
    for script in ('build_site.py', 'generate_pages.py', 'build_gpcz_site.py', 'render_site.py', 'build_current_review.py', 'build_archived_lanes.py'):
        subprocess.run([sys.executable, 'scripts/'+script], cwd=ROOT, check=True)
    for name in ('index.html', 'docs/index.html', 'docs/executive-summary.html',
                 'docs/hmas-sinter/index.html', 'docs/hmas-sinter/executive-summary.html',
                 'docs/gpcz/index.html', 'docs/gpcz/how-to-submit.html', 'docs/how-to-submit.html',
                 'docs/legacy-executive-summary.html', 'docs/nine-sites.html', 'docs/gpcz/nine-sites.html',
                 'docs/gpcz/knowledge.html', 'docs/gpcz/sources.html', 'docs/sources.html'):
        raw = (ROOT/name).read_text()
        assert 'DO NOT SUBMIT' in raw, name
        assert 'K-PROXY-DETECT file in the banner above is the only cleared file' not in raw, name
        text = _strip_kp1_banner(raw)
        assert 'OK TO SUBMIT' not in text and 'READY FOR PORTAL' not in text, name
        # Technical preflight is not selector approval. The current banner must not
        # advertise any upload until a separate decision is bound to the exact bytes.
        if _kp1_banner_span(raw) is not None:
            gate = json.loads((ROOT/'evidence/kp1_release_gate.json').read_text())
            assert gate['decision']['technical_preflight_passed'] is True
            assert gate['decision']['ok_to_submit'] is False
            assert 'no file is authorized for upload' in raw
            assert 'Download the .tif' not in raw
            assert 'K-PROXY-DETECT GeoTIFF' in raw
    stale = subprocess.run([sys.executable, 'scripts/build_dashboard_and_figures.py'], cwd=ROOT, capture_output=True)
    assert stale.returncode != 0


def test_legacy_experiment_entrypoints_are_blocked_before_work():
    for script in ('run_experiment1_screen.py', 'run_experiment2_gpcz.py', 'run_experiment3_build.py'):
        p = subprocess.run([sys.executable, 'scripts/'+script], cwd=ROOT, text=True, capture_output=True)
        assert p.returncode != 0 and 'BLOCKED' in p.stderr


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
    for script in ('reconcile_prior_decisions.py', 'sync_review_status.py'):
        subprocess.run([sys.executable, 'scripts/' + script], cwd=ROOT, check=True)
        assert before == [p.read_bytes() for p in paths]
