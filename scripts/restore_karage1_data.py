#!/usr/bin/env python3
"""Autonomous SHA-256-verified restoration of all competition, external GeoDAWN/INGENIOUS, and benchmark files."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import re
from pathlib import Path

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


class GitBlobFetcher:
    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._prepared: set[tuple[str, str]] = set()

    def _repo_dir(self, repo: str) -> Path:
        return self.cache_dir / repo.replace("/", "__")

    def ensure_commit(self, repo: str, ref: str) -> Path:
        git_dir = self._repo_dir(repo)
        url = f"https://github.com/{repo}.git"
        if not (git_dir / "HEAD").exists():
            subprocess.run(
                ["git", "clone", "--quiet", "--bare", "--filter=blob:none", "--no-tags", "--depth=1", url, str(git_dir)],
                check=True,
                timeout=300,
            )
        if (repo, ref) not in self._prepared:
            has_ref = (
                subprocess.run(
                    ["git", "--git-dir", str(git_dir), "cat-file", "-e", f"{ref}^{{commit}}"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                ).returncode
                == 0
            )
            if not has_ref:
                subprocess.run(
                    ["git", "--git-dir", str(git_dir), "fetch", "--quiet", "--depth=1", "origin", ref],
                    check=True,
                    timeout=300,
                )
            self._prepared.add((repo, ref))
        return git_dir

    def write_blob(self, repo: str, ref: str, path: str, out_fh) -> None:
        git_dir = self.ensure_commit(repo, ref)
        subprocess.run(
            ["git", "--git-dir", str(git_dir), "show", f"{ref}:{path}"],
            stdout=out_fh,
            check=True,
            timeout=600,
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None, help="Destination directory (default: /tmp/gems_data or ./data)")
    ap.add_argument("--manifest", type=Path, default=REGISTRY_DIR / "karage1_data_manifest.json")
    ap.add_argument("--verify-only", action="store_true")
    ap.add_argument("--group", help="Restore only one manifest group (for example core)")
    ap.add_argument("--id", action="append", dest="ids", help="Restore only named manifest id(s); may be repeated")
    args = ap.parse_args()

    dest_root = args.data_dir or data_dir()
    dest_root.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text())
    entries = manifest.get("files")
    if not isinstance(entries, list) or not entries:
        raise ValueError("manifest contains no files")
    if args.group:
        entries = [e for e in entries if e.get("group") == args.group]
    if args.ids:
        requested = set(args.ids)
        entries = [e for e in entries if e.get("id") in requested]
        if {e.get("id") for e in entries} != requested:
            raise ValueError("one or more requested manifest ids were not found")
    if not entries:
        raise ValueError("selection contains no files")
    fetcher = GitBlobFetcher(ROOT / ".cache" / "gems_git_cache")

    ok = 0
    for entry in entries:
        rel = entry["dest"]
        expected = entry["sha256"]
        # Manifest paths are data, not an instruction to write outside the
        # requested directory, and checksums must be complete SHA-256 pins.
        if not isinstance(rel, str) or Path(rel).is_absolute() or any(p in ("", ".", "..") for p in rel.split("/")):
            raise ValueError(f"unsafe destination: {rel!r}")
        if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
            raise ValueError(f"invalid SHA-256 pin for {rel}")
        target = dest_root / rel
        if not target.resolve().is_relative_to(dest_root.resolve()):
            raise ValueError(f"destination escapes data directory through a symlink: {rel!r}")
        if target.is_file() and sha256_file(target) == expected:
            ok += 1
            continue
        if args.verify_only:
            print(f"[MISSING/MISMATCH] {rel}", file=sys.stderr)
            return 1
        target.parent.mkdir(parents=True, exist_ok=True)
        # The manifest contains both the original top-level source schema and
        # the later nested-source schema. Normalize rather than silently
        # ignoring the 30 original entries.
        src = entry.get("source")
        if src is None:
            src = {"repo": entry.get("repo"), "ref": entry.get("ref"),
                   "kind": "git_split_blob" if "parts" in entry else "git_blob"}
            if "parts" in entry:
                src["parts"] = entry["parts"]
            else:
                src["path"] = entry.get("path")
        if not isinstance(src, dict) or not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", str(src.get("repo", ""))) or not re.fullmatch(r"[0-9a-f]{40}", str(src.get("ref", ""))):
            raise ValueError(f"source must have a repository and immutable commit for {rel}")
        if src.get("kind") not in ("git_blob", "git_split_blob"):
            raise ValueError(f"unsupported source kind for {rel}")
        paths = src.get("parts") if src.get("kind") == "git_split_blob" else [src.get("path")]
        if not isinstance(paths, list) or not paths or any(
            not isinstance(p, str) or p.startswith("/") or any(part in ("", ".", "..") for part in p.split("/"))
            for p in paths
        ):
            raise ValueError(f"invalid source path for {rel}")
        tmp = target.with_suffix(target.suffix + ".part")
        with tmp.open("wb") as fh:
            if src["kind"] == "git_blob":
                fetcher.write_blob(src["repo"], src["ref"], src["path"], fh)
            elif src["kind"] == "git_split_blob":
                for part in src["parts"]:
                    fetcher.write_blob(src["repo"], src["ref"], part, fh)
            else:
                raise ValueError(f"Unsupported source kind: {src['kind']}")
        got = sha256_file(tmp)
        if got != expected:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(f"SHA-256 mismatch for {rel}: expected {expected}, got {got}")
        tmp.replace(target)
        ok += 1
        print(f"[restored] {rel} ({got[:12]}...)")

    print(f"[restore_data] Verified {ok}/{len(entries)} SHA-256-pinned mirror files in {dest_root}; organizer authenticity is not established")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
