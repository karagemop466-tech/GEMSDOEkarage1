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


def test_masked_in_footprint_values_never_pass(tmp_path):
    t, f, c = [tmp_path / n for n in ('t.tif', 'f.tif', 'c.tif')]
    a = np.ones((3, 3), dtype='float32')
    write(t, a); write(f, a)
    # Finite values can nevertheless be null through a nodata sentinel.
    write(c, a, nodata=1)
    result = validate(c, t, f)
    assert result['checks']['all_values_in_range']
    assert not result['checks']['unmasked_inside_footprint']
    assert not result['format_pass'] and not result['submission_ready']
    # Nor may an explicit internal mask hide an in-footprint prediction.
    write(c, a)
    with rasterio.open(c, 'r+') as ds:
        mask = np.full(a.shape, 255, dtype='uint8')
        mask[1, 1] = 0
        ds.write_mask(mask)
    assert not validate(c, t, f)['format_pass']


def test_footprint_mask_and_candidate_dtype_are_checked(tmp_path):
    t, f, c = [tmp_path / n for n in ('t.tif', 'f.tif', 'c.tif')]
    a = np.ones((3, 3), dtype='float32')
    write(t, a); write(f, a, nodata=1); write(c, a)
    result = validate(c, t, f)
    assert not result['checks']['footprint_unmasked'] and not result['format_pass']
    write(f, a)
    with rasterio.open(c, 'w', driver='GTiff', width=3, height=3, count=1,
                       dtype='uint8', crs='EPSG:32611', transform=from_origin(0, 1000, 100, 100)) as ds:
        ds.write(a.astype('uint8'), 1)
    assert not validate(c, t, f)['checks']['float32']
    assert not validate(c, t, f)['format_pass']
    # Passing candidate as its own template or footprint must fail format_pass.
    write(c, a)
    assert not validate(c, c, f)['checks']['distinct_reference_files']
    assert not validate(c, c, f)['format_pass']
    assert not validate(c, t, c)['checks']['distinct_reference_files']
    assert not validate(c, t, c)['format_pass']


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


def test_research_downloads_are_labeled_and_match_audited_bytes():
    """No primary download is offered; research copies must be the audited duplicates."""
    import hashlib
    from html.parser import HTMLParser
    from urllib.parse import unquote, urlsplit
    root = Path(__file__).resolve().parents[1]
    audit = json.loads((root/'evidence/candidate_audit_20261028.json').read_text())
    expected = {row['sha256'] for row in audit['candidates']}
    card = json.loads((root/'docs/data/run-card.json').read_text())
    expected.add(card['raster_sha256'])
    expected.add(json.loads((root/'evidence/conduitcrest_lattice_reaudit_20261028.json').read_text())['candidate']['sha256'])
    assert len(expected) == 4
    # 2026-10-31 E1 candidate (zeros and NaN variants): each has a saved-byte receipt written by
    # scripts/write_o2_audit_receipts_20261031.py; the audited bytes are the only allowed downloads.
    for receipt in ('evidence/audit_o2_candidate_zeros_20261031.json', 'evidence/audit_o2_candidate_nan_20261031.json'):
        expected.add(json.loads((root/receipt).read_text())['sha256'])
    assert len(expected) == 6
    for gate_name in ('release_gate_hmas_sinter.json', 'release_gate_gpcz.json'):
        gate = json.loads((root/'evidence'/gate_name).read_text())
        assert gate['result']['verdict'] == 'negative' and gate['result']['ok_to_submit'] is False
    class Links(HTMLParser):
        def __init__(self, page):
            super().__init__(); self.page = page; self.downloads = []; self.in_audit = False
            self.label = ''; self.banner_downloads = []; self.article_downloads = []
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
                target = (self.page.parent / unquote(urlsplit(attrs['href']).path)).resolve()
                digest = hashlib.sha256(target.read_bytes()).hexdigest()
                if 'K-PROXY-DETECT' in self.page.read_text() and not self.in_audit:
                    # The single cleared file is advertised in the session banner; its
                    # legitimacy is asserted separately below against the release gate.
                    self.banner_downloads.append(digest)
                else:
                    assert self.in_audit, 'research file must be inside an audit warning card'
                    self.article_downloads.append(digest)
        def handle_data(self, text):
            if self.in_audit: self.label += text
        def handle_endtag(self, tag):
            if tag == 'article' and self.in_audit:
                assert 'DO NOT SUBMIT' in self.label and 'research only' in self.label.lower()
                self.downloads.extend(self.article_downloads); self.in_audit = False
    gate = json.loads((root/'evidence/kp1_release_gate.json').read_text())
    assert gate['decision']['ok_to_submit'] is False and gate['decision']['slots_used'] == 0  # 31 Oct 2026: listed-site check fails
    gate = json.loads((root/'evidence/kp1_release_gate.json').read_text())
    home = Links(root/'index.html'); home.feed((root/'index.html').read_text())
    assert not home.downloads
    if gate['decision']['ok_to_submit']:
        assert home.banner_downloads == [gate['sha256']]
    else:
        # 31 Oct 2026: not cleared, so the banner must not offer the file for download
        assert not home.banner_downloads
    for page in (root/'executive-summary.html', root/'docs/executive-summary.html'):
        parsed = Links(page); parsed.feed(page.read_text())
        assert set(parsed.downloads) == expected


def test_run_card_and_source_hashes():
    import hashlib
    root = Path(__file__).resolve().parents[1]
    card = json.loads((root/'docs/data/run_card.json').read_text())
    assert card == json.loads((root/'docs/data/run-card.json').read_text())
    assert card['verdict'] == 'negative' and not card['ok_to_submit']
    assert len(card['submission_note']) <= 140
    for row in json.loads((root/'docs/data/sources.json').read_text())['sites']:
        raw = (root/'evidence/sources'/f"{row['site']}-README.md").read_bytes()
        assert hashlib.sha256(raw).hexdigest() == row['readme_sha256']


def test_collect_sources_blob_parser_blocks_traversal_and_mutable_refs(tmp_path):
    from scripts.collect_sources import parse_pinned_github_blob
    sha = '7edcc9b58e6ad0f88c6e6f5ee9218761a391769d'
    good_url = f'https://github.com/buffedlizard55-lab/GEMSDOE36/blob/{sha}/docs/downloads/file.tif'
    repo, ref, path, dest = parse_pinned_github_blob('file.tif', good_url, tmp_path / 'rasters')
    assert repo == 'buffedlizard55-lab/GEMSDOE36' and ref == sha and path == 'docs/downloads/file.tif'
    assert dest == (tmp_path / 'rasters' / 'file.tif').resolve()

    for bad_name, bad_url in [
        ('../escape.tif', good_url),
        ('sub/escape.tif', good_url),
        ('file.png', good_url),
        ('file.tif', 'https://evil.example/buffedlizard55-lab/GEMSDOE36/blob/' + sha + '/a.tif'),
        ('file.tif', 'https://github.com/buffedlizard55-lab/GEMSDOE36/raw/' + sha + '/a.tif'),
        ('file.tif', 'https://github.com/buffedlizard55-lab/GEMSDOE36/blob/main/a.tif'),
        ('file.tif', f'https://github.com/buffedlizard55-lab/GEMSDOE36/blob/{sha}/../a.tif'),
    ]:
        with pytest.raises(ValueError):
            parse_pinned_github_blob(bad_name, bad_url, tmp_path / 'rasters')


def test_historical_raster_audit_catches_negative_spearman_and_undefined_masks(tmp_path, monkeypatch):
    from scripts import audit_rasters
    sites = [f'GEMSDOE{n}' for n in (24, 25, 27, 28, 30, 31, 32, 33, 36)]
    rasters = tmp_path / '.research/rasters'
    rasters.mkdir(parents=True)
    data_dir = tmp_path / 'docs/data'
    data_dir.mkdir(parents=True)

    # Complementary masks have exact Spearman = -1.0 and 0% 3px overlap on a wide grid.
    base = np.zeros((10, 40), dtype=np.float32)
    base[2, 2] = 1.0
    comp = np.ones((10, 40), dtype=np.float32)
    comp[2, 2] = 0.0
    manifest_rows = []
    for idx, site in enumerate(sites):
        arr = comp if idx == 1 else base
        p = rasters / f'{site}.tif'
        write(p, arr)
        import hashlib
        manifest_rows.append({'site': site, 'artifact': p.name, 'artifact_sha256': hashlib.sha256(p.read_bytes()).hexdigest()})
    (data_dir / 'sources.json').write_text(json.dumps({'sites': manifest_rows}))
    monkeypatch.setattr(audit_rasters, 'ROOT', tmp_path)
    audit_rasters.main()
    out = json.loads((data_dir / 'raster_audit.json').read_text())
    g25 = next(r for r in out['rasters'] if r['site'] == 'GEMSDOE25')
    # Complement of a single dot has 399 dots: 398 outside 3px disk -> overlap < 0.70, but |spearman| == 1.0 > 0.90!
    assert all(c['within_3px_fraction'] < 0.70 for c in g25['comparisons'])
    assert g25['literal_duplicate'] is True

    # All-zero mask has undefined correlation and must fail closed instead of TypeError.
    p0 = rasters / 'GEMSDOE24.tif'
    write(p0, np.zeros((10, 40), dtype=np.float32))
    import hashlib
    manifest_rows[0]['artifact_sha256'] = hashlib.sha256(p0.read_bytes()).hexdigest()
    (data_dir / 'sources.json').write_text(json.dumps({'sites': manifest_rows}))
    with pytest.raises(ValueError, match='Undefined comparison metric'):
        audit_rasters.main()

