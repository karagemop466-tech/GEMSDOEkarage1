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
    assert 'Not estimable' in (ROOT/'docs/executive-summary.html').read_text()


def test_evidence_strict_json():
    def reject(value):
        raise ValueError(value)
    for path in list((ROOT/'evidence').glob('*.json'))+list((ROOT/'registry').glob('*.json')):
        json.loads(path.read_text(),parse_constant=reject)
    card=json.loads((ROOT/'evidence/run_card.json').read_text())
    assert card['verdict']=='negative'
    assert card['raster_sha256'] is None
    assert card['holdout']['dti'] is None
