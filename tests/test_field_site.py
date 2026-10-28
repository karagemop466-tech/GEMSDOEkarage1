from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlparse

from scripts import render_site

ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()
        self.duplicates = set()
        self.disabled_downloads = 0
        self._button = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            if attrs["id"] in self.ids:
                self.duplicates.add(attrs["id"])
            self.ids.add(attrs["id"])
        for name in ("href", "src"):
            if name in attrs:
                self.links.append(attrs[name])
        if tag == "button" and "disabled" in attrs:
            self.disabled_downloads += 1


def test_site_tables_are_rendered_from_evidence_and_never_approve():
    rows, _ = render_site.build()
    assert rows.count("DO NOT RESUBMIT") == 9
    assert rows.count("USER-REPORTED · UNVERIFIED") == 9
    assert rows.count("Unavailable") == 9
    for path, prefix in ((ROOT / "index.html", ""), (ROOT / "docs/executive-summary.html", "../")):
        text = path.read_text()
        assert render_site.rows_for(prefix) in text
        parser = Tags(); parser.feed(text)
        assert parser.disabled_downloads >= 1
        assert "DO NOT SUBMIT" in text and "No eligible submission file yet" in text
        assert "99.93%" in text and "99.89%" in text
    card = json.loads((ROOT / "docs/data/run-card.json").read_text())
    assert card["verdict"] == "negative" and card["ok_to_submit"] is False
    assert card["download_available"] is False and card["slot_selected_or_spent"] is False


def test_all_local_links_and_fragments_work():
    paths = [ROOT / "index.html", ROOT / "executive-summary.html", *ROOT.glob("docs/**/*.html")]
    for page in paths:
        parser = Tags(); parser.feed(page.read_text())
        assert not parser.duplicates, (page, parser.duplicates)
        for link in parser.links:
            u = urlparse(link)
            if u.scheme or u.netloc or link.startswith("mailto:"):
                continue
            target = (page.parent / unquote(u.path)).resolve() if u.path else page
            assert target.exists(), (page, link)
            if u.fragment and target.suffix == ".html":
                target_parser = Tags(); target_parser.feed(target.read_text())
                assert u.fragment in target_parser.ids, (page, link)


def test_published_monitor_has_nine_pinned_sources_and_a_loaded_script():
    class Monitor(HTMLParser):
        def __init__(self):
            super().__init__()
            self.chips, self.scripts, self.ids = [], [], set()
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if 'data-source-repo' in attrs:
                self.chips.append((attrs.get('data-source-repo'), attrs.get('data-source-ref')))
            if tag == 'script':
                self.scripts.append(attrs.get('src'))
            if 'id' in attrs:
                self.ids.add(attrs['id'])

    entries = {r['id']: r for r in json.loads((ROOT / 'registry/reference_assets.json').read_text())}
    for rel in ('index.html', 'docs/index.html', 'docs/executive-summary.html'):
        page = ROOT / rel
        parsed = Monitor(); parsed.feed(page.read_text())
        assert {'feed-status', 'refresh-sources'} <= parsed.ids
        assert len(parsed.chips) == 9
        assert set(parsed.chips) == {(entries[s]['repo'], entries[s]['ref']) for s in render_site.SITES}
        assert len(parsed.scripts) == 1 and (page.parent / parsed.scripts[0]).resolve() == ROOT / 'docs/assets/app.js'
        assert 'does not check scores' in page.read_text()
        assert 'DO NOT SUBMIT' in page.read_text()


def test_source_monitor_javascript_on_success_error_and_offline():
    import shutil
    import subprocess
    import pytest
    if not shutil.which('node'):
        pytest.skip('Node.js unavailable for browser monitor regression')
    result = subprocess.run(['node', 'tests/js/test-source-monitor.cjs'], cwd=ROOT,
                            text=True, capture_output=True, timeout=30)
    assert result.returncode == 0, result.stderr


def test_concurrent_update_is_clearly_research_only():
    result = json.loads((ROOT / "docs/data/concurrent-review.json").read_text())
    cmp = result["comparisons_candidate_to_reference"]
    assert cmp["lattice"]["candidate_dots"] == 37654
    assert cmp["lattice"]["within_3px_fraction"] == 1.0
    assert cmp["lattice"]["strictly_exceeds_70_percent"]
    assert result["submission_authorized"] is False
    assert result["holdout_reproduced"] is False
    assert "DO NOT SUBMIT" in result["owner_status"]
    assert result["surface_correlation_checked"] is False


def test_archives_are_quarantined_and_invalid_claims_are_not_promoted():
    data = json.loads((ROOT / "docs/data/archive-review.json").read_text())
    cda = data["assets"]["CDA1_zero"]
    assert not data["submission_authorized"]
    assert cda["vs_lattice"]["within_3px_count"] == 37570
    assert cda["vs_lattice"]["candidate_dots"] == 37654
    assert cda["vs_lattice"]["strictly_exceeds_70_percent"]
    assert "hard-coded" in cda["purported_holdout_status"]
    for name in ("HUNQ1_dots", "HUNQ1_zero"):
        assert not data["assets"][name]["format_diagnostic"]["diagnostics"]["grid_and_inside_pass"]
    for filename in ("index.html", "executive-summary.html"):
        page = (ROOT / "archive/cda1-demonstrator/docs" / filename).read_text()
        assert "QUARANTINED SYNTHETIC DEMONSTRATOR" in page
        assert "not measured" in page


def test_legacy_builder_does_not_overwrite_current_pages():
    import subprocess
    import sys
    current = [ROOT / "index.html", ROOT / "docs/executive-summary.html", ROOT / "docs/research.html"]
    before = [p.read_bytes() for p in current]
    subprocess.run([sys.executable, "scripts/build_site.py"], cwd=ROOT, check=True)
    assert [p.read_bytes() for p in current] == before


def test_renderer_fails_closed_on_tampered_decision_data(tmp_path, monkeypatch):
    import shutil
    import pytest

    relative = [
        'registry/historical_claims.json', 'registry/reference_assets.json',
        'docs/data/reference-audit.json', 'docs/data/run-card.json',
        'evidence/candidate_audit_20261028.json', 'evidence/run_card_hmas_sinter.json',
        'evidence/run_card_gpcz.json',
    ]
    for rel in relative:
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, target)
    audit_path = tmp_path / 'evidence/candidate_audit_20261028.json'
    audit = json.loads(audit_path.read_text())
    for c in audit['candidates']:
        target = tmp_path / 'docs/downloads' / c['file']
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / 'docs/downloads' / c['file'], target)
    monkeypatch.setattr(render_site, 'ROOT', tmp_path)
    monkeypatch.setattr(render_site, 'DOCS', tmp_path / 'docs')
    render_site.evidence()

    # The displayed nine-site witness must be backed by all 72 consistent
    # directional rows, not just a stale boolean or a self-reported fraction.
    ref_path = tmp_path / 'docs/data/reference-audit.json'
    reference = json.loads(ref_path.read_text())
    original_reference = json.dumps(reference)
    reference['directed_pairs']['GEMSDOE32->GEMSDOE36']['overlap_fraction'] = float('nan')
    ref_path.write_text(json.dumps(reference))
    with pytest.raises(ValueError, match='pair evidence'):
        render_site.evidence()
    reference = json.loads(original_reference)
    del reference['directed_pairs']['GEMSDOE32->GEMSDOE36']
    ref_path.write_text(json.dumps(reference))
    with pytest.raises(ValueError, match='pairwise evidence incomplete'):
        render_site.evidence()
    reference = json.loads(original_reference)
    reference['rows']['GEMSDOE32']['lattice_directed_overlap'] = float('nan')
    ref_path.write_text(json.dumps(reference))
    with pytest.raises(ValueError, match='bad reference evidence'):
        render_site.evidence()
    ref_path.write_text(original_reference)

    audit['candidates'][0]['comparisons'][0]['directed_overlap'] = 0.2
    audit_path.write_text(json.dumps(audit))
    with pytest.raises(ValueError, match='disagree'):
        render_site.evidence()

    audit['candidates'][0]['comparisons'][0]['directed_overlap'] = 38174 / 38200
    clean_audit = json.dumps(audit)
    # NaN must never slip through numeric comparisons, and the published format
    # claims must agree with the recorded diagnostics, not just the filename.
    for section, key, value in (
        ('witness', 'directed_overlap', float('nan')),
        ('witness', 'candidate_dots_within_3px', float('nan')),
        ('witness', 'candidate_dots_within_3px', 40000),
        ('witness', 'overlap_exceeds_70_percent', False),
        ('format', 'no_nonfinite_inside', False),
        ('format', 'masked_inside_count', 1),
        ('format', 'outside_all_null_or_nan', True),
    ):
        modified = json.loads(clean_audit)
        candidate = modified['candidates'][0]
        target = candidate['comparisons'][0] if section == 'witness' else candidate['format_checks']
        target[key] = value
        audit_path.write_text(json.dumps(modified))
        with pytest.raises(ValueError, match='disagree'):
            render_site.evidence()
    audit_path.write_text(clean_audit)
    card_path = tmp_path / 'docs/data/run-card.json'
    card = json.loads(card_path.read_text())
    card['slot_selected_or_spent'] = True
    card_path.write_text(json.dumps(card))
    with pytest.raises(ValueError, match='decision incomplete'):
        render_site.evidence()
