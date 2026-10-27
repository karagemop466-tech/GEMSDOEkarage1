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
    rows, chips = render_site.build()
    assert rows.count("DO NOT RESUBMIT") == 9
    assert rows.count("USER-REPORTED · UNVERIFIED") == 9
    assert rows.count("Unavailable") == 9
    assert chips.count("data-source-repo=") == 9
    for path in (ROOT / "index.html", ROOT / "docs/executive-summary.html"):
        text = path.read_text()
        assert rows in text
        assert 'class="button button-disabled"' in text
        assert "No file is approved" in text or "Do not submit a file" in text
    assert chips in (ROOT / "index.html").read_text()
    card = json.loads((ROOT / "docs/data/run-card.json").read_text())
    assert card["verdict"] == "negative" and card["ok_to_submit"] is False


def test_all_local_links_and_fragments_work():
    paths = [ROOT / "index.html", ROOT / "docs/executive-summary.html", ROOT / "docs/research.html"]
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
    assert "data/concurrent-review.json" in (ROOT / "index.html").read_text()


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
