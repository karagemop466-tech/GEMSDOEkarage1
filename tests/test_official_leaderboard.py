"""Fail-closed tests for the public-only DrivenData leaderboard feed."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import refresh_official_leaderboard as feed


HTML = """<!doctype html><html><body>
<table><thead><tr><th>Rank</th><th>Team members</th><th>Participant</th>
<th>Best public DW-Tversky</th><th>Shared work</th></tr></thead><tbody>
<tr><td>#1</td><td></td><td><a>xiaofanhu</a><br>2d ago · 34 submissions</td><td>0.4544</td><td></td></tr>
<tr><td>#2</td><td></td><td>cfld__</td><td>0.3916</td><td></td></tr>
<tr><td>#3</td><td></td><td>Batik Shirt Brothers</td><td>0.3911</td><td></td></tr>
</tbody></table></body></html>"""


def test_parse_public_leaderboard_rows_and_scope():
    result = feed.parse_leaderboard_html(HTML, "2026-10-29T09:25:00+00:00")
    assert result["schema"] == "gems-official-public-leaderboard-v1"
    assert result["retrieved_at_utc"] == "2026-10-29T09:25:00+00:00"
    assert result["row_count"] == 3
    assert result["rows"][0] == {
        "rank": 1,
        "participant": "xiaofanhu 2d ago · 34 submissions",
        "best_public_dw_tversky": 0.4544,
    }
    assert "not a file-linked" in result["scope"]


def test_parser_rejects_layout_drift_and_short_or_ambiguous_rows():
    with pytest.raises(ValueError, match="header"):
        feed.parse_leaderboard_html("<table><tr><td>Rank</td><td>Score</td></tr></table>")
    with pytest.raises(ValueError, match="fewer than three"):
        feed.parse_leaderboard_html("""<table><tr><th>Rank</th><th>Best public DW-Tversky</th></tr>
        <tr><td>#1</td><td>0.4</td></tr><tr><td>#2</td><td>0.3</td></tr></table>""")
    ambiguous = HTML.replace("<td>0.4544</td>", "<td>0.4544 (0.4500)</td>")
    with pytest.raises(ValueError, match="ambiguous"):
        feed.parse_leaderboard_html(ambiguous)


def test_parser_rejects_duplicate_ranks_and_out_of_range_scores():
    duplicate = HTML.replace(
        "<tr><td>#2</td><td></td><td>cfld__</td><td>0.3916</td><td></td></tr>",
        "<tr><td>#1</td><td></td><td>cfld__</td><td>0.3916</td><td></td></tr>",
    )
    with pytest.raises(ValueError, match="duplicate ranks"):
        feed.parse_leaderboard_html(duplicate)
    outside = HTML.replace("<td>0.4544</td>", "<td>1.1</td>")
    with pytest.raises(ValueError, match="outside"):
        feed.parse_leaderboard_html(outside)


def test_failed_refresh_does_not_overwrite_last_good_snapshot(tmp_path, monkeypatch):
    output = tmp_path / "leaderboard.json"
    old_bytes = b'{"previous": "good snapshot"}\n'
    output.write_bytes(old_bytes)
    monkeypatch.setattr(feed, "fetch_leaderboard", lambda: "not an HTML leaderboard")
    with pytest.raises(SystemExit) as exc:
        feed.main(["--output", str(output)])
    assert exc.value.code == 2
    assert output.read_bytes() == old_bytes


def test_snapshot_is_explicitly_scoped_and_has_rank_one():
    path = Path(__file__).resolve().parents[1] / "docs/data/official-leaderboard.json"
    snapshot = json.loads(path.read_text())
    assert snapshot["schema"] == "gems-official-public-leaderboard-v1"
    assert "not a file-linked" in snapshot["scope"]
    assert snapshot["rows"][0]["rank"] == 1
    assert snapshot["rows"][0]["best_public_dw_tversky"] == pytest.approx(0.4544)
    if snapshot.get("partial_snapshot"):
        assert snapshot["observed_on_utc"] == "2026-10-29"
    else:
        assert snapshot["row_count"] >= 3
        assert snapshot["retrieved_at_utc"]


def test_renderer_uses_dated_public_feed_and_current_session_card():
    from scripts.render_site import home

    page = home(1)
    assert "OFFICIAL PUBLIC LEADERBOARD #1" in page
    assert "0.4544" in page and "observed 2026-10-29" in page
    assert "#47 0.3195" in page
    assert "not a file-linked submission receipt" in page.lower()
    assert "session_09bbfea3_run_card.json" in page
    assert "Current review · session 09bbfea3" in page


def test_current_session_card_is_negative_and_has_no_invented_raster_values():
    path = Path(__file__).resolve().parents[1] / "evidence/session_09bbfea3_run_card.json"
    card = json.loads(path.read_text())
    assert card["verdict"] == "negative"
    assert card["candidate"]["experiment_count"] == 0
    assert card["candidate"]["weekly_slot_selected_or_spent"] is False
    assert card["holdout"]["status"] == "NOT_RUN"
    assert card["holdout"]["value"] is None and card["holdout"]["ci95"] is None
    assert card["raster"]["filename"] is None and card["raster"]["sha256"] is None
    assert card["raster"]["validator_output"]["status"] == "NOT_RUN"
    assert card["submission"]["slot_selected_or_spent"] is False
