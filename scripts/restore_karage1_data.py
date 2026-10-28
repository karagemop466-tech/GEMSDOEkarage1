#!/usr/bin/env python3
"""Restore hash-pinned public GitHub mirrors, not authenticated organizer data.

Each successful file is written atomically after its *full* SHA-256 and byte
count match the committed manifest. No organizer credentials are requested.
The mirrors and derived third-party inputs still require provenance and license
review before competition use; a matching hash proves only mirror consistency.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from gemskarage1.paths import REGISTRY_DIR, data_dir


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _safe_rel(value: str) -> bool:
    if not isinstance(value, str) or not value or "\\" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in ("", ".", "..") for part in value.split("/"))


def normalize_entry(entry: dict) -> dict:
    """Accept both historical manifest layouts, but only immutable safe pins."""
    if not isinstance(entry, dict):
        raise ValueError("manifest entry must be an object")
    source = entry.get("source")
    if source is None:
        source = {k: entry[k] for k in ("repo", "ref", "path", "parts") if k in entry}
        source["kind"] = "git_split_blob" if "parts" in source else "git_blob"
    if not isinstance(source, dict) or source.get("kind") not in ("git_blob", "git_split_blob"):
        raise ValueError("unsupported manifest source")
    repo, ref = source.get("repo"), source.get("ref")
    if not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("invalid repository")
    if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError("source must be pinned to a 40-character commit")
    if source["kind"] == "git_blob":
        paths = [source.get("path")]
    else:
        paths = source.get("parts")
        if not isinstance(paths, list) or not paths:
            raise ValueError("split source has no parts")
    if any(not _safe_rel(p) for p in paths):
        raise ValueError("unsafe source path")
    dest = entry.get("dest")
    if not _safe_rel(dest):
        raise ValueError("unsafe destination path")
    digest, size = entry.get("sha256"), entry.get("bytes")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError("source needs a full SHA-256 pin")
    if type(size) is not int or size <= 0:
        raise ValueError("source needs a positive byte count")
    return {**entry, "source": source, "paths": paths}


def fetch_blob(repo: str, ref: str, path: str, out_fh) -> None:
    endpoint = f"repos/{repo}/contents/{quote(path, safe='/')}?ref={ref}"
    subprocess.run(
        ["gh", "api", endpoint, "-H", "Accept: application/vnd.github.raw"],
        stdout=out_fh, check=True, timeout=600,
    )


def restore_entry(entry: dict, dest_root: Path, *, verify_only: bool = False, fetcher=fetch_blob) -> dict:
    entry = normalize_entry(entry)
    root = dest_root.resolve()
    target = (root / entry["dest"]).resolve()
    if not target.is_relative_to(root):
        raise ValueError("destination escapes data directory")
    def matches(path: Path) -> bool:
        return path.is_file() and path.stat().st_size == entry["bytes"] and sha256_file(path) == entry["sha256"]
    if matches(target):
        return {"dest": entry["dest"], "status": "verified", "bytes": entry["bytes"], "sha256": entry["sha256"]}
    if verify_only:
        raise ValueError(f"missing or mismatched: {entry['dest']}")
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix='.' + target.name + '.', suffix='.partial', dir=target.parent)
    temp = Path(name)
    source = entry["source"]
    try:
        with os.fdopen(fd, "wb") as fh:
            for path in entry["paths"]:
                fetcher(source["repo"], source["ref"], path, fh)
        if not matches(temp):
            raise ValueError(f"size or SHA-256 mismatch for {entry['dest']}")
        os.chmod(temp, 0o644)
        temp.replace(target)
    finally:
        temp.unlink(missing_ok=True)
    return {"dest": entry["dest"], "status": "restored", "bytes": entry["bytes"], "sha256": entry["sha256"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None, help="Destination (default: GEMS_DATA_DIR or ./data)")
    ap.add_argument("--manifest", type=Path, default=REGISTRY_DIR / "karage1_data_manifest.json")
    ap.add_argument("--group", choices=("core", "external", "scored", "all"), default="all")
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()
    root = args.data_dir or data_dir()
    try:
        manifest = json.loads(args.manifest.read_text())
        entries = [normalize_entry(e) for e in manifest["files"]]
        if len({e["dest"] for e in entries}) != len(entries):
            raise ValueError("duplicate destinations in manifest")
        selected = [e for e in entries if args.group == "all" or e.get("group", "scored") == args.group]
        if not selected:
            raise ValueError("manifest selection is empty")
        for entry in selected:
            result = restore_entry(entry, root, verify_only=args.verify_only)
            print(f"[{result['status']}] {result['dest']} ({result['bytes']:,} B, {result['sha256'][:12]}...)", flush=True)
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"RESTORE BLOCKED: {exc}", file=sys.stderr)
        return 1
    print(f"Verified {len(selected)} pinned mirrors in {root}; organizer authenticity is NOT established.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
