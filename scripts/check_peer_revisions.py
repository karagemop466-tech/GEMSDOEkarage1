#!/usr/bin/env python3
"""Check GitHub HEADs against the nine historical audit pins, without scraping scores.

Revision freshness is not a scientific audit, registry completeness, or upload
permission. Changed or unavailable revisions cause a nonzero exit so a stale
comparison cannot look like a passing freshness check. This script reads no
DrivenData pages and does not select or change a submission.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]
SITES = tuple(f"GEMSDOE{n}" for n in (24, 25, 27, 28, 30, 31, 32, 33, 36))
SHA = re.compile(r"[0-9a-f]{40}\Z")


def load_pins(path: Path) -> list[dict]:
    entries = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("reference manifest must be a list")
    pins = []
    for site in SITES:
        matches = [x for x in entries if isinstance(x, dict) and x.get("id") == site]
        if len(matches) != 1:
            raise ValueError(f"exactly one audited source pin required for {site}")
        row = matches[0]
        repo, commit = row.get("repo"), row.get("ref")
        if repo != f"buffedlizard55-lab/{site}" or not isinstance(commit, str) or not SHA.fullmatch(commit):
            raise ValueError(f"invalid repository or immutable audit pin for {site}")
        pins.append({"site": site, "repo": repo, "audit_commit": commit})
    return pins


def github_head(repo: str) -> str:
    """Query only the public GitHub API through the installed GitHub CLI."""
    result = subprocess.run(
        ["gh", "api", f"repos/{repo}/commits/HEAD", "--jq", ".sha"],
        text=True, capture_output=True, check=True, timeout=30,
    )
    return result.stdout.strip()


def check(pins: list[dict], lookup: Callable[[str], str] | None = None) -> dict:
    lookup = lookup or github_head

    def inspect(pin: dict) -> dict:
        try:
            head = lookup(pin["repo"])
            if not isinstance(head, str) or not SHA.fullmatch(head):
                raise ValueError("missing or invalid GitHub HEAD")
            status = "at_audit_pin" if head == pin["audit_commit"] else "changed"
        except (OSError, subprocess.SubprocessError, ValueError):
            head, status = None, "unavailable"
        return {**pin, "head": head, "status": status,
                "source": f'https://github.com/{pin["repo"]}/commits/HEAD'}

    with ThreadPoolExecutor(max_workers=4) as pool:
        rows = list(pool.map(inspect, pins))
    counts = {state: sum(row["status"] == state for row in rows)
              for state in ("at_audit_pin", "changed", "unavailable")}
    return {
        "schema": "karage1-peer-revision-check-v1",
        "checked_utc": datetime.now(timezone.utc).isoformat(),
        "scope": "GitHub HEADs versus historical artifact commits; not a raster, score or full-registry audit.",
        "sites": rows,
        "counts": counts,
        "ok_to_submit": False,
        "slot_selected": False,
    }


def write_report(report: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix="." + path.name + ".", suffix=".partial", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=ROOT / "registry/reference_assets.json")
    parser.add_argument("--out", type=Path, default=ROOT / ".cache/peer-revisions.json")
    args = parser.parse_args()
    try:
        report = check(load_pins(args.manifest))
        write_report(report, args.out)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Revision check blocked: {exc}")
        return 2
    print(json.dumps({"report": str(args.out), **report["counts"], "ok_to_submit": False}))
    return 1 if report["counts"]["changed"] or report["counts"]["unavailable"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
