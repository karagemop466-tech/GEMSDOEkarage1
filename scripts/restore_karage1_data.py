#!/usr/bin/env python3
"""Autonomous SHA-256-verified restoration of all competition, external GeoDAWN/INGENIOUS, and benchmark files."""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
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


def _normalize_source(entry: dict) -> dict:
    """Normalize both flat legacy manifest entries and nested `source` entries."""
    if "source" in entry and isinstance(entry["source"], dict):
        return entry["source"]
    if "parts" in entry:
        return {
            "kind": "git_split_blob",
            "repo": entry["repo"],
            "ref": entry["ref"],
            "parts": entry["parts"],
        }
    if "path" in entry:
        return {
            "kind": "git_blob",
            "repo": entry["repo"],
            "ref": entry["ref"],
            "path": entry["path"],
        }
    raise ValueError(f"Manifest entry missing source specification: {entry.get('dest') or entry.get('id')}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data-dir", type=Path, default=None, help="Destination directory (default: /tmp/gems_data or ./data)")
    ap.add_argument("--manifest", type=Path, default=REGISTRY_DIR / "karage1_data_manifest.json")
    ap.add_argument("--verify-only", action="store_true")
    args = ap.parse_args()

    dest_root = args.data_dir or Path(sys.modules["os"].environ.get("GEMS_DATA_DIR", "/tmp/gems_data"))
    dest_root.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(args.manifest.read_text())
    fetcher = GitBlobFetcher(Path("/tmp/gems_git_cache"))

    ok = 0
    for entry in manifest["files"]:
        rel = entry.get("dest") or entry["name"]
        expected = entry["sha256"]
        target = dest_root / rel
        if target.is_file() and sha256_file(target) == expected:
            ok += 1
            continue
        if args.verify_only:
            print(f"[MISSING/MISMATCH] {rel}", file=sys.stderr)
            return 1
        target.parent.mkdir(parents=True, exist_ok=True)
        src = _normalize_source(entry)
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

    print(f"[restore_data] Verified {ok}/{len(manifest['files'])} SHA-256-pinned files in {dest_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
