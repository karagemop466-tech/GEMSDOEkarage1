from html.parser import HTMLParser
from pathlib import Path
import json
import subprocess
import sys
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
    for path in (ROOT/'docs').glob('*.html'):
        text=path.read_text()
        parser=Links()
        parser.feed(text)
        for link in parser.links:
            url=urlsplit(link)
            if not url.scheme and url.path:
                assert (path.parent/unquote(url.path)).exists(), (path,link)
    assert 'DO NOT SUBMIT' in (ROOT/'docs/index.html').read_text()
    assert 'No approved .tif to download' in (ROOT/'docs/index.html').read_text()
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


def test_current_session_is_visible_and_fails_closed():
    card = json.loads((ROOT / "evidence/session_07823dcc_run_card.json").read_text())
    assert card["verdict"] == "negative"
    assert card["ok_to_submit"] is False
    assert card["download_available"] is False
    assert card["slot_selected_or_spent"] is False
    assert card["geological_experiments_run"] == 0
    assert card["holdout_dti"]["value"] is None
    assert card["raster_sha256"] is None
    assert card["validator_output"]["status"] == "not run; no raster generated"
    gse = json.loads((ROOT / "evidence/gse_concurrent_artifact_reaudit_20261029.json").read_text())
    candidate = ROOT / gse["candidate_file"]
    assert gse["decision"] == "negative" and gse["submit_authorized"] is False
    assert gse["holdout"]["value"] is None
    assert gse["inherited_uniqueness_receipt_irregularity"]["receipt_compared_rows"] == 11
    assert gse["inherited_uniqueness_receipt_irregularity"]["receipt_candidate_name"] != candidate.name
    for page in (ROOT / "index.html", ROOT / "docs/index.html", ROOT / "docs/executive-summary.html"):
        text = page.read_text()
        assert "DO NOT SUBMIT" in text
        assert "No approved .tif to download" in text
        assert "session-review-arena-07823dcc-2026-10-29.md" in text
        assert "session_07823dcc_run_card.json" in text
        assert "karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif" in text
        assert "gse_concurrent_artifact_reaudit_20261029.json" in text
        assert "UNPROVEN" in text


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
