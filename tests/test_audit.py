import json
from pathlib import Path
import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from scripts.audit_rasters import overlap, binary_spearman
from scripts.validate_artifact import validate


def test_overlap_direction_and_boundary():
    a = np.zeros((10, 10), bool); b = a.copy(); foot = np.ones_like(a)
    a[1, 1] = True; b[1, 4] = True; b[9, 9] = True
    assert overlap(a, b, foot) == 1
    assert overlap(b, a, foot) == .5
    assert overlap(np.zeros_like(a), b, foot) is None
    assert overlap(a, np.zeros_like(a), foot) == 0
    assert binary_spearman(a, a, foot) == 1
    assert binary_spearman(foot, a, foot) is None


def write(path, arr, **kw):
    profile = dict(driver='GTiff', width=arr.shape[1], height=arr.shape[0], count=1,
                   dtype='float32', crs='EPSG:32611', transform=from_origin(0, 1000, 100, 100))
    profile.update(kw)
    with rasterio.open(path, 'w', **profile) as d:
        d.write(arr.astype('float32'), 1)


@pytest.mark.parametrize('bad', [float('nan'), float('inf'), -1, 1.01])
def test_invalid_values(tmp_path, bad):
    t, f, c = [tmp_path / n for n in ('t.tif', 'f.tif', 'c.tif')]
    a = np.ones((3, 3)); write(t, a); write(f, a)
    a[0, 0] = bad; write(c, a)
    assert not validate(c, t, f)['format_pass']


def test_valid_format_not_permission(tmp_path):
    t, f, c = [tmp_path / n for n in ('t.tif', 'f.tif', 'c.tif')]
    a = np.ones((3, 3)); write(t, a); write(f, a); write(c, a)
    assert validate(c, t, f)['format_pass']
    assert not validate(c, t, f)['submission_ready']
    write(c, a, transform=from_origin(1, 1000, 100, 100))
    assert not validate(c, t, f)['format_pass']
    write(c, a); write(f, np.zeros((3, 3)))
    assert not validate(c, t, f)['format_pass']


def test_evidence_scope():
    root = Path(__file__).resolve().parents[1]
    s = json.loads((root/'docs/data/sources.json').read_text())
    a = json.loads((root/'docs/data/raster_audit.json').read_text())
    assert len(s['sites']) == len(a['rasters']) == 9
    for row in s['sites']:
        assert row['estimate'] is None and row['organizer_confirmed'] is None
        assert not row['submit']
        assert len(row['artifact_sha256']) == 64
    assert all(r['literal_duplicate'] for r in a['rasters'])


def test_research_downloads_are_labeled_and_match_audited_bytes():
    """No primary download is offered; research copies must be the audited duplicates."""
    import hashlib
    from html.parser import HTMLParser
    from urllib.parse import unquote, urlsplit
    root = Path(__file__).resolve().parents[1]
    audit = json.loads((root/'evidence/candidate_audit_20261028.json').read_text())
    expected = {row['sha256'] for row in audit['candidates']}
    assert len(expected) == 2
    for gate_name in ('release_gate_hmas_sinter.json', 'release_gate_gpcz.json'):
        gate = json.loads((root/'evidence'/gate_name).read_text())
        assert gate['result']['verdict'] == 'negative' and gate['result']['ok_to_submit'] is False
    class Links(HTMLParser):
        def __init__(self, page):
            super().__init__(); self.page = page; self.downloads = []; self.in_audit = False; self.label = ''
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'article' and 'audit-card' in attrs.get('class', ''):
                self.in_audit = True; self.label = ''; self.article_downloads = []
            for key in ('href', 'src'):
                value = attrs.get(key, '')
                url = urlsplit(value)
                if value and not url.scheme and not url.netloc and url.path:
                    assert (self.page.parent / unquote(url.path)).is_file(), (self.page, value)
            if 'download' in attrs:
                assert self.in_audit, 'research file must be inside an audit warning card'
                target = (self.page.parent / unquote(urlsplit(attrs['href']).path)).resolve()
                self.article_downloads.append(hashlib.sha256(target.read_bytes()).hexdigest())
        def handle_data(self, text):
            if self.in_audit: self.label += text
        def handle_endtag(self, tag):
            if tag == 'article' and self.in_audit:
                assert 'DO NOT SUBMIT' in self.label and 'research only' in self.label.lower()
                self.downloads.extend(self.article_downloads); self.in_audit = False
    home = Links(root/'index.html'); home.feed((root/'index.html').read_text())
    assert not home.downloads
    for page in (root/'executive-summary.html', root/'docs/executive-summary.html'):
        parsed = Links(page); parsed.feed(page.read_text())
        assert set(parsed.downloads) == expected


def test_run_card_and_source_hashes():
    import hashlib
    root = Path(__file__).resolve().parents[1]
    card = json.loads((root/'docs/data/run_card.json').read_text())
    assert card['verdict'] == 'negative' and not card['submission_ready']
    assert len(card['note']) <= 140
    for row in json.loads((root/'docs/data/sources.json').read_text())['sites']:
        raw = (root/'evidence/sources'/f"{row['site']}-README.md").read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['readme_sha256']
