"""Guards for the arena/d454d34a executive table (31 Oct 2026).

The table is generated from evidence/registry_overlap_matrix_20261031.json and the run card,
so these tests check that the generated pages carry the verified numbers and labels.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD = json.loads((ROOT / "evidence/run_card_arena_d454d34a_20261031.json").read_text())
OV = json.loads((ROOT / "evidence/registry_overlap_matrix_20261031.json").read_text())


def _section(html: str) -> str:
    start = html.index('id="answer-d454d34a"')
    return html[start:html.index("</section>", start)]


def test_executive_pages_carry_current_block_and_sha():
    for rel in ("executive-summary.html", "docs/executive-summary.html"):
        sec = _section((ROOT / rel).read_text(encoding="utf-8"))
        assert CARD["raster"]["sha256"] in sec, rel
        assert "ELIGIBLE TO UPLOAD · NOT VALIDATED" in sec, rel
        assert "not a score" in sec, rel
        assert "0.2789" in sec and "PROJECTED" in sec, rel


def test_executive_table_has_nine_focus_rows_and_candidate():
    sec = _section((ROOT / "docs/executive-summary.html").read_text(encoding="utf-8"))
    for site in ("GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
                 "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"):
        assert f'<th scope="row">{site}</th>' in sec, site
    assert "Candidate (new)" in sec


def test_overlap_numbers_match_run_card_and_are_below_limit():
    card_share = CARD["correlation_and_overlap_vs_registry"]["max_share_kp1_dots_within_3px_of_any_focus_file"]
    assert abs(OV["kp1_max_share_into_focus"] - card_share) < 1e-4
    assert OV["kp1_max_share_into_focus"] < 0.70
    assert OV["rho_max_abs"] < 0.90
    assert OV["format"]["nan_count"] == 0 and OV["format"]["min"] >= 0 and OV["format"]["max"] <= 1
    assert OV["format"]["dot_count"] == 32000
    assert all(OV["grid_matches_candidate"].values())
