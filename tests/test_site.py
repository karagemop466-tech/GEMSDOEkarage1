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
    assert 'Unavailable' in (ROOT/'docs/executive-summary.html').read_text()


def test_evidence_strict_json():
    def reject(value):
        raise ValueError(value)
    for path in list((ROOT/'evidence').glob('*.json'))+list((ROOT/'registry').glob('*.json')):
        json.loads(path.read_text(),parse_constant=reject)
    card=json.loads((ROOT/'evidence/run_card.json').read_text())
    assert card['verdict']=='negative'
    assert len(card['raster_sha256']) == 64
    assert card['holdout_dti']['status'].startswith('Prior run report only')
    assert card['geological_experiments_run'] == 0 and not card['slot_selected_or_spent']


def test_all_published_pages_have_valid_local_references_and_no_stale_release_claims():
    from urllib.parse import urlsplit
    pages = [ROOT/'index.html', ROOT/'executive-summary.html', ROOT/'legacy-overview.html',
             *(ROOT/'docs').rglob('*.html')]
    class Page(HTMLParser):
        def __init__(self):
            super().__init__(); self.links=[]; self.downloads=[]; self.ids=set(); self.duplicates=[]
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if attrs.get('id') in self.ids: self.duplicates.append(attrs['id'])
            if attrs.get('id'): self.ids.add(attrs['id'])
            for key in ('href','src'):
                if attrs.get(key): self.links.append(attrs[key])
            if tag == 'a' and 'download' in attrs: self.downloads.append(attrs.get('href'))
    parsed = {}
    for page in pages:
        body = page.read_text()
        assert 'READY FOR PORTAL' not in body and 'ONE CLEARED TIFF' not in body
        assert 'CLEARED · SELECTOR PENDING' not in body
        parser = Page(); parser.feed(body); parsed[page.resolve()] = parser
        assert not parser.downloads, (page, parser.downloads)
        assert not parser.duplicates, (page, parser.duplicates)
    for page in pages:
        parser=parsed[page.resolve()]
        for link in parser.links:
            u=urlsplit(link)
            if u.scheme or u.netloc: continue
            target=(page.parent/unquote(u.path)).resolve() if u.path else page.resolve()
            if target.is_dir(): target=target/'index.html'
            assert target.exists(), (page,link)
            if u.fragment and target in parsed:
                assert unquote(u.fragment) in parsed[target].ids, (page,link)


def test_legacy_lane_generators_cannot_reinstate_approval():
    import hashlib
    files = [ROOT/'docs/hmas-sinter/index.html', ROOT/'docs/gpcz/index.html',
             ROOT/'docs/how-to-submit.html', ROOT/'docs/nine-sites.html']
    before = [hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
    for script in ('scripts/generate_pages.py', 'scripts/build_gpcz_site.py'):
        subprocess.run([sys.executable, script], cwd=ROOT, check=True)
    assert before == [hashlib.sha256(p.read_bytes()).hexdigest() for p in files]
    assert all('DO NOT SUBMIT' in p.read_text() for p in files)
