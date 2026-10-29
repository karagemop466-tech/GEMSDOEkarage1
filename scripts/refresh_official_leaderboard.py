#!/usr/bin/env python3
"""Fetch and validate the organizer's public leaderboard, then atomically save it.

This deliberately reads only the public leaderboard page. It does not log in,
inspect submissions, select a slot, or create an organizer receipt. A changed
page layout or an unparseable response fails closed and leaves the prior
snapshot untouched.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.error import URLError
from urllib.request import Request, urlopen


LEADERBOARD_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
SCHEMA = "gems-official-public-leaderboard-v1"
MAX_RESPONSE_BYTES = 8 * 1024 * 1024
TIMEOUT_SECONDS = 30


class _TableRows(HTMLParser):
    """Collect table cells without depending on a particular CSS framework."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:  # noqa: ANN001 - HTMLParser API
        tag = tag.lower()
        if tag == "tr":
            self._row = []
            self._cell = None
        elif tag in {"th", "td"} and self._row is not None:
            self._cell = []
        elif tag == "br" and self._cell is not None:
            self._cell.append(" ")

    def handle_data(self, data: str) -> None:
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in {"th", "td"} and self._row is not None and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            if self._cell is not None:
                self._row.append(" ".join("".join(self._cell).split()))
            if self._row:
                self.rows.append(self._row)
            self._row = None
            self._cell = None


def _header_indices(rows: list[list[str]]) -> tuple[int, int, int | None]:
    for row in rows:
        normalized = [re.sub(r"\s+", " ", cell).strip().lower() for cell in row]
        rank_idx = next((i for i, cell in enumerate(normalized) if cell == "rank"), None)
        score_idx = next((i for i, cell in enumerate(normalized)
                          if "public" in cell and ("tversky" in cell or "score" in cell)), None)
        participant_idx = next((i for i, cell in enumerate(normalized)
                                if cell in {"participant", "team", "team name"}), None)
        if rank_idx is not None and score_idx is not None:
            return rank_idx, score_idx, participant_idx
    raise ValueError("public leaderboard table header (rank + public Tversky score) not found")


def parse_leaderboard_html(html_text: str, retrieved_at_utc: str | None = None) -> dict:
    """Parse the public rank/score table and reject ambiguous or incomplete data."""
    parser = _TableRows()
    parser.feed(html_text)
    rank_idx, score_idx, participant_idx = _header_indices(parser.rows)
    parsed: list[dict] = []
    score_pattern = re.compile(r"(?<![\w.])(?:\d+(?:\.\d*)?|\.\d+)(?![\w.])")
    for row in parser.rows:
        if max(rank_idx, score_idx) >= len(row):
            continue
        rank_match = re.fullmatch(r"\s*#?\s*(\d+)\s*", row[rank_idx])
        if not rank_match:
            continue
        rank = int(rank_match.group(1))
        matches = score_pattern.findall(row[score_idx])
        if len(matches) != 1:
            raise ValueError(f"rank {rank} has an ambiguous public-score cell")
        score = float(matches[0])
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"rank {rank} public score is outside [0, 1]")
        participant = ""
        if participant_idx is not None and participant_idx < len(row):
            participant = row[participant_idx].strip()
        parsed.append({
            "rank": rank,
            "participant": participant,
            "best_public_dw_tversky": score,
        })

    if not parsed:
        raise ValueError("no ranked public leaderboard rows were parsed")
    parsed.sort(key=lambda item: item["rank"])
    ranks = [item["rank"] for item in parsed]
    if len(ranks) != len(set(ranks)):
        raise ValueError("duplicate ranks in public leaderboard response")
    if ranks[0] != 1:
        raise ValueError("public leaderboard response does not include rank 1")
    if len(parsed) < 3:
        raise ValueError("fewer than three public leaderboard rows; refusing to publish a partial parse")

    return {
        "schema": SCHEMA,
        "competition_id": 306,
        "source_url": LEADERBOARD_URL,
        "retrieved_at_utc": retrieved_at_utc or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "scope": "Organizer public leaderboard only; not a file-linked submission-page receipt, private score, or project estimate.",
        "row_count": len(parsed),
        "rows": parsed,
    }


def fetch_leaderboard(url: str = LEADERBOARD_URL) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": "GEMSDOEkarage1-public-leaderboard-refresh/1.0",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            final_url = response.geturl()
            if "drivendata.org/competitions/306/" not in final_url:
                raise ValueError(f"unexpected leaderboard redirect: {final_url}")
            body = response.read(MAX_RESPONSE_BYTES + 1)
    except (OSError, URLError) as exc:
        raise RuntimeError(f"official public leaderboard fetch failed: {exc}") from exc
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("leaderboard response exceeds the 8 MiB safety limit")
    return body.decode("utf-8", errors="replace")


def write_snapshot(path: Path, snapshot: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(snapshot, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=Path("docs/data/official-leaderboard.json"))
    args = parser.parse_args(argv)
    try:
        html_text = fetch_leaderboard()
        snapshot = parse_leaderboard_html(html_text)
        write_snapshot(args.output, snapshot)
    except Exception as exc:
        parser.exit(2, f"LEADERBOARD REFRESH BLOCKED: {exc}\n")
    print(f"Saved {snapshot['row_count']} official public ranks to {args.output} "
          f"({snapshot['retrieved_at_utc']}). This is not a submission receipt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
