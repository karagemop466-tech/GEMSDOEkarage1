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
    assert card['verdict']=='negative'
    assert card['raster_sha256'] is None
    assert card['holdout']['dti'] is None


def test_all_legacy_page_builders_delegate_to_fail_closed_renderer():
    paths = [ROOT / 'index.html', ROOT / 'executive-summary.html', *sorted((ROOT / 'docs').glob('**/*.html'))]
    before = {path: path.read_bytes() for path in paths}
    for entry in ('build_site.py', 'build_current_review.py', 'generate_pages.py',
                  'build_detail_pages.py', 'build_gpcz_site.py'):
        subprocess.run([sys.executable, f'scripts/{entry}'], cwd=ROOT, check=True, capture_output=True)
        assert {path: path.read_bytes() for path in paths} == before, entry
    blocked = subprocess.run([sys.executable, 'scripts/build_dashboard_and_figures.py'],
                             cwd=ROOT, capture_output=True, text=True)
    assert blocked.returncode != 0 and 'Quarantined' in blocked.stderr
    assert {path: path.read_bytes() for path in paths} == before
