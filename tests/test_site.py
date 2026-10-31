from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
import sys
import pytest
from urllib.parse import urlsplit, unquote

ROOT=Path(__file__).parents[1]

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self,tag,attrs):
        for key,value in attrs:
            if key in ('href','src') and value:
                self.links.append(value)


def test_site_links_and_negative_banner():
    subprocess.run([sys.executable,'scripts/build_site.py'],cwd=ROOT,check=True)
    subprocess.run([sys.executable,'scripts/build_focus_summary.py'],cwd=ROOT,check=True)
    for path in [ROOT/'index.html', *(ROOT/'docs').rglob('*.html')]:
        text=path.read_text()
        parser=Links()
        parser.feed(text)
        for link in parser.links:
            url=urlsplit(link)
            if not url.scheme and url.path:
                assert (path.parent/unquote(url.path)).exists(), (path,link)
    index = (ROOT/'docs/index.html').read_text()
    assert 'DO NOT SUBMIT' in index
    assert 'No approved .tif to download' in index
    assert 'Latest review 2026-10-31: no file cleared; this repository-safety review produced no candidate or score estimate' in index
    assert 'HOLDOUT-DTI 0.04330 [0.03559, 0.04629] · gems57-pooled-hide-v2 · n=45,260 withheld positives' in index
    assert 'paired Δ vs matched random -0.00291 [95% CI -0.00707, +0.00095]' in index
    assert 'LATEST REVIEW · 2026-10-31' in index
    assert 'HISTORICAL EXPERIMENT · SESSION arena/fb1e3550 · 29 OCT 2026' in index
    assert 'PRIOR CANDIDATE REVIEW · 29 OCT 2026' in index
    assert 'Historical experiment run card' in index
    assert 'ORGANIZER-PUBLIC; live re-read 31 Oct 2026' in index
    assert '0.3195 is rank #50' in index
    hub = (ROOT/'docs/submission-hub.html').read_text()
    assert 'independent 30 Oct live re-read' in hub
    assert '0.3195 at rank #50' in hub
    assert 'Neither 0.4413 nor 0.3195 was confirmed' not in hub
    focus = (ROOT/'docs/focus-sites.html').read_text()
    assert 'Latest review 2026-10-31: no file cleared; this repository-safety review produced no candidate or score estimate' in focus
    assert 'href="../evidence/run_card_arena_946f7668_20261031.json"' in focus
    assert 'href="../knowledge/review-arena-946f7668-20261031.md"' in index
    assert 'href="../evidence/run_card_arena_946f7668_20261031.json"' in index
    assert 'No defensible forecast' in (ROOT/'docs/executive-summary.html').read_text()


def test_evidence_strict_json():
    def reject(value):
        raise ValueError(value)
    for path in list((ROOT/'evidence').glob('*.json'))+list((ROOT/'registry').glob('*.json')):
        json.loads(path.read_text(),parse_constant=reject)
    card=json.loads((ROOT/'evidence/run_card.json').read_text())
    assert card == json.loads((ROOT/'docs/data/run-card.json').read_text())
    assert card['verdict']=='negative' and card['ok_to_submit'] is False
    assert card['holdout_dti']['label']=='HOLDOUT-DTI'
    assert card['holdout_dti']['value'] is not None
    assert card['holdout_dti']['evaluator_version']
    assert card['slot_selected_or_spent'] is False


def test_current_review_renderer_fails_closed(tmp_path, monkeypatch):
    from scripts import render_site

    card = json.loads((ROOT/'evidence/run_card_arena_946f7668_20261031.json').read_text())
    assert render_site.current_review()['verdict'] == 'negative'
    card['ok_to_submit'] = True
    candidate = tmp_path/'current-review.json'
    candidate.write_text(json.dumps(card))
    monkeypatch.setattr(render_site, 'CURRENT_REVIEW_CARD', candidate)
    with pytest.raises(ValueError, match='not fail-closed'):
        render_site.current_review()


def test_all_legacy_page_builders_delegate_to_fail_closed_renderer():
    paths = [ROOT / 'index.html', ROOT / 'executive-summary.html', *sorted((ROOT / 'docs').glob('**/*.html'))]
    before = {path: path.read_bytes() for path in paths}
    for entry in ('build_site.py', 'build_current_review.py', 'generate_pages.py',
                  'build_detail_pages.py', 'build_gpcz_site.py', 'build_archived_lanes.py',
                  'build_executive_summary.py'):
        subprocess.run([sys.executable, f'scripts/{entry}'], cwd=ROOT, check=True, capture_output=True)
        assert {path: path.read_bytes() for path in paths} == before, entry
    blocked = subprocess.run([sys.executable, 'scripts/build_dashboard_and_figures.py'],
                             cwd=ROOT, capture_output=True, text=True)
    assert blocked.returncode != 0 and 'Quarantined' in blocked.stderr
    assert {path: path.read_bytes() for path in paths} == before


def test_concurrent_rendering_never_exposes_partial_pages():
    import time
    paths = [ROOT / 'index.html', ROOT / 'executive-summary.html', *sorted((ROOT / 'docs').glob('**/*.html'))]
    processes = [subprocess.Popen([sys.executable, 'scripts/build_site.py'], cwd=ROOT,
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE) for _ in range(3)]
    try:
        while any(p.poll() is None for p in processes):
            for page in paths:
                content = page.read_bytes()
                assert content.startswith(b'<!doctype html>') and content.rstrip().endswith(b'</html>'), page
            time.sleep(.002)
        for process in processes:
            out, err = process.communicate(timeout=10)
            assert process.returncode == 0, (out, err)
    finally:
        for process in processes:
            if process.poll() is None:
                process.kill()
                process.wait()
