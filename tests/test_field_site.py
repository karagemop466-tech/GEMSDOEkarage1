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
    render_site.main()
    rows, _ = render_site.build()
    assert rows.count("DO NOT RESUBMIT") == 9
    assert rows.count("USER-REPORTED · UNVERIFIED") == 9
    assert rows.count("Unavailable") == 9
    for path, prefix in ((ROOT / "index.html", ""), (ROOT / "docs/executive-summary.html", "../")):
        text = path.read_text()
        assert render_site.rows_for(prefix) in text
        parser = Tags(); parser.feed(text)
        assert parser.disabled_downloads >= 1
        assert "DO NOT SUBMIT" in text and "Nothing is cleared for upload" in text
        assert "No approved .tif to download" in text
        assert "99.93%" in text and "99.89%" in text
    card = json.loads((ROOT / "docs/data/run-card.json").read_text())
    assert card["verdict"] == "negative" and card["ok_to_submit"] is False
    assert card["slot_selected_or_spent"] is False
    assert "not authorization" in card["download_available_meaning"].lower()


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


def test_dipdual_archive_obeys_literal_lattice_stop_without_role_exemption():
    summary = (ROOT / "docs/dipdual-20261028/index.html").read_text()
    guide = (ROOT / "docs/dipdual-20261028/how-to-submit.html").read_text()
    assert "99.8885%" in summary and "37,612 / 37,654" in summary
    assert "literal duplicate; stop" in summary
    assert "Safe to download for audit/research only: yes. Safe to submit: no." in summary
    assert "DO NOT SUBMIT" in summary
    assert "<span>UPLOAD AUTHORIZED</span><strong>No</strong>" in summary
    assert "YES vs discrete registry" not in summary
    assert "selector acknowledgment" in summary
    assert "do not override this result" in summary
    assert "There is no cleared file to submit from this archive." in guide
    assert "no cleared file to submit" in guide.lower()
    assert "Make new submission" not in guide


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
        'evidence/run_card_gpcz.json', 'evidence/bbstep_uniqueness.json',
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
    card = json.loads((tmp_path / 'docs/data/run-card.json').read_text())
    bb = tmp_path / 'docs/downloads' / card['submission_name']
    bb.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'docs/downloads' / card['submission_name'], bb)
    monkeypatch.setattr(render_site, 'ROOT', tmp_path)
    monkeypatch.setattr(render_site, 'DOCS', tmp_path / 'docs')
    render_site.evidence()

    audit['candidates'][0]['comparisons'][0]['directed_overlap'] = 0.2
    audit_path.write_text(json.dumps(audit))
    with pytest.raises(ValueError, match='disagree'):
        render_site.evidence()

    audit['candidates'][0]['comparisons'][0]['directed_overlap'] = 38174 / 38200
    audit_path.write_text(json.dumps(audit))
    card_path = tmp_path / 'docs/data/run-card.json'
    card = json.loads(card_path.read_text())
    card['slot_selected_or_spent'] = True
    card_path.write_text(json.dumps(card))
    with pytest.raises(ValueError, match='decision incomplete'):
        render_site.evidence()


def test_secondary_site_evidence_renders_and_fails_closed(tmp_path, monkeypatch):
    import shutil
    import pytest

    sec = render_site.secondary_evidence()
    assert len(sec['rows']) == 12
    assert 'gems28-s18-mxtp-20261025-3e95505c011a-allfinite.tif' in (ROOT / 'docs/GEMSDOE28.html').read_text()

    sec_copy = tmp_path / 'evidence/nine_sites_secondary_audit_20261028.json'
    sec_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'evidence/nine_sites_secondary_audit_20261028.json', sec_copy)
    registry_copy = tmp_path / 'registry/reference_assets.json'
    registry_copy.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT / 'registry/reference_assets.json', registry_copy)
    monkeypatch.setattr(render_site, 'ROOT', tmp_path)
    assert len(render_site.secondary_evidence()['rows']) == 12

    tampered = json.loads(sec_copy.read_text())
    tampered['rows'][0]['ok_to_submit'] = True
    sec_copy.write_text(json.dumps(tampered))
    with pytest.raises(ValueError, match='secondary site evidence failed fail-closed check'):
        render_site.secondary_evidence()


def test_newer_conduitcrest_candidate_is_lattice_duplicate_and_not_download_cleared():
    import hashlib
    render_site.main()
    audit, original, latest, raster = render_site.conduitcrest_evidence()
    lattice = audit['lattice_witness']
    assert lattice['candidate_dots_within_closed_3px_disk'] == 17301
    assert lattice['candidate_dots'] == 17415
    assert lattice['exceeds_overlap_threshold'] is True
    assert latest['verdict'] == 'negative' and latest['ok_to_submit'] is False
    assert latest['holdout_dti']['dti'] is None
    assert audit['previous_holdout_claim']['reported_value'] is None
    assert hashlib.sha256(raster.read_bytes()).hexdigest() == audit['candidate']['sha256']
    page = (ROOT / 'docs/executive-summary.html').read_text()
    assert '99.3454%' in page and 'no 95% CI' in page
    assert 'No HOLDOUT-DTI result is reportable for Conduitcrest.' in page
    assert '0.017415' not in page
    assert 'DO NOT SUBMIT' in page

