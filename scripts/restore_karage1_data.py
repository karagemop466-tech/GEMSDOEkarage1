#!/usr/bin/env python3
"""Restore hash-pinned public mirrors; a matching hash does not authenticate the source.

Both the original flat manifest schema and the later nested ``source`` schema
are accepted. Downloads are assembled in a temporary file, checked for size and
SHA-256, and atomically installed only after validation. No data is committed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
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


def normalize_entry(entry: dict, root: Path) -> dict:
    """Validate manifest paths, source schema and integrity pins before any I/O."""
    if not isinstance(entry, dict):
        raise ValueError("manifest entry must be an object")
    dest = entry.get("dest")
    if not isinstance(dest, str) or not dest or "\\" in dest or Path(dest).is_absolute() or ".." in Path(dest).parts:
        raise ValueError(f"unsafe destination: {dest!r}")
    digest = entry.get("sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        raise ValueError(f"missing full SHA-256 pin for {dest}")
    size = entry.get("bytes")
    if type(size) is not int or size <= 0:
        raise ValueError(f"invalid expected byte count for {dest}")
    source = entry.get("source", entry)
    if not isinstance(source, dict):
        raise ValueError(f"invalid source for {dest}")
    repo, ref = source.get("repo"), source.get("ref")
    if (not isinstance(repo, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo)
            or any(part in (".", "..") for part in repo.split("/"))):
        raise ValueError(f"invalid source repository for {dest}")
    if not isinstance(ref, str) or not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError(f"source ref must be an immutable 40-character commit for {dest}")
    kind = source.get("kind", "git_split_blob" if "parts" in source else "git_blob")
    if kind == "git_blob":
        paths = [source.get("path")]
    elif kind == "git_split_blob":
        paths = source.get("parts")
    else:
        raise ValueError(f"unsupported source kind {kind!r}")
    if not isinstance(paths, list) or not paths or any(
        not isinstance(p, str) or not p or "\\" in p or p.startswith("/") or ".." in Path(p).parts for p in paths
    ):
        raise ValueError(f"invalid source paths for {dest}")
    target = root / dest
    # Protect against traversing an already existing symlink in the destination tree.
    if not target.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"destination escapes data directory: {dest}")
    return {"dest": dest, "target": target, "sha256": digest, "bytes": size,
            "repo": repo, "ref": ref, "paths": paths, "id": entry.get("id", dest)}


def fetch_blob(repo: str, ref: str, path: str, out, attempts: int = 3) -> None:
    """Stream a GitHub contents blob to a seekable output, retrying safely."""
    url = f"repos/{repo}/contents/{quote(path, safe='/')}?ref={quote(ref, safe='')}"
    start = out.tell()
    for attempt in range(attempts):
        try:
            subprocess.run(["gh", "api", url, "-H", "Accept: application/vnd.github.raw"],
                           stdout=out, stderr=subprocess.PIPE, check=True, timeout=600)
            return
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
            out.seek(start)
            out.truncate()
            if attempt + 1 == attempts:
                raise RuntimeError(f"GitHub fetch failed for {repo}@{ref}:{path}: {exc}") from exc
            time.sleep(attempt + 1)


def restore_entry(entry: dict, root: Path, *, verify_only: bool = False) -> dict:
    spec = normalize_entry(entry, root)
    target = spec["target"]
    if target.is_file() and target.stat().st_size == spec["bytes"] and sha256_file(target) == spec["sha256"]:
        return {"id": spec["id"], "dest": spec["dest"], "status": "verified", "sha256": spec["sha256"]}
    if verify_only:
        raise ValueError(f"missing or mismatched file: {spec['dest']}")
    target.parent.mkdir(parents=True, exist_ok=True)
    # A random, exclusively-created sibling avoids clobbering or following an
    # attacker-controlled predictable .partial symlink and allows atomic replace.
    handle = tempfile.NamedTemporaryFile(mode="wb", prefix=target.name + ".", suffix=".partial",
                                         dir=target.parent, delete=False)
    tmp = Path(handle.name)
    try:
        with handle as fh:
            for path in spec["paths"]:
                fetch_blob(spec["repo"], spec["ref"], path, fh)
        got_size = tmp.stat().st_size
        got_hash = sha256_file(tmp)
        if got_size != spec["bytes"] or got_hash != spec["sha256"]:
            raise ValueError(f"integrity mismatch for {spec['dest']}: bytes={got_size}, sha256={got_hash}")
        tmp.replace(target)
    finally:
        tmp.unlink(missing_ok=True)
    return {"id": spec["id"], "dest": spec["dest"], "status": "restored", "sha256": spec["sha256"]}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None)
    ap.add_argument("--manifest", type=Path, default=REGISTRY_DIR / "karage1_data_manifest.json")
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--id", action="append", default=[], help="Restore only these manifest IDs (repeatable); destinations also accepted")
    ap.add_argument("--group", help="Restrict to a manifest group, e.g. core or external")
    args = ap.parse_args()
    root = args.data_dir or data_dir()
    try:
        manifest = json.loads(args.manifest.read_text())
        entries = manifest["files"]
        if not isinstance(entries, list) or not entries:
            raise ValueError("manifest contains no files")
        chosen = [e for e in entries if (not args.group or e.get("group") == args.group)
                  and (not args.id or e.get("id") in args.id or e.get("dest") in args.id)]
        if not chosen:
            raise ValueError("no manifest entries matched the requested selection")
        if args.id:
            found = {x for e in chosen for x in (e.get("id"), e.get("dest"))}
            missing = set(args.id) - found
            if missing:
                raise ValueError(f"unknown manifest IDs/destinations: {sorted(missing)}")
        # Validate every selected entry before starting transfers.
        specs = [normalize_entry(e, root) for e in chosen]
        if len({s["dest"] for s in specs}) != len(specs):
            raise ValueError("duplicate destination in selected manifest")
        root.mkdir(parents=True, exist_ok=True)
        failed = []
        for entry in chosen:
            try:
                rec = restore_entry(entry, root, verify_only=args.verify_only)
                print(f"[{rec['status']}] {rec['dest']} {rec['sha256']}", flush=True)
            except (OSError, ValueError, RuntimeError) as exc:
                failed.append(str(exc))
                print(f"[FAILED] {exc}", file=sys.stderr, flush=True)
        if failed:
            print(f"Restoration incomplete: {len(failed)}/{len(chosen)} selected files failed.", file=sys.stderr)
            return 1
        print(f"Verified {len(chosen)} hash-pinned public mirrors in {root}; organizer authenticity is not established.")
        return 0
    except (KeyError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Restoration preflight failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
