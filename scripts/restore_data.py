#!/usr/bin/env python3
"""Restore every file in registry/data_manifest.json into .cache/gems_data and verify SHA-256.

All transfers go over github.com (the only route available from the sandbox). Each file is
hash-checked against the manifest pin. Entries flagged ``sha256_prefix_only`` were pinned from a
sibling repository's receipt that only recorded a 12-character prefix; after a successful prefix
match the full digest is written back into the manifest so the pin becomes exact.

Usage: python3 scripts/restore_data.py [--group core|external|registry|all] [--target-dir DIR]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "registry" / "data_manifest.json"
DEFAULT_TARGET = ROOT / ".cache" / "gems_data"


def sha256_file(p: Path) -> str:
    h = hashlib.sha256()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(repo: str, ref: str, path: str, dest: Path, attempts: int = 4) -> None:
    """Fetch one blob with ``gh api`` (raw media type). Retries on transient failures."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".partial")
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            with tmp.open("wb") as out:
                subprocess.run(
                    ["gh", "api", f"repos/{repo}/contents/{path}?ref={ref}", "-H", "Accept: application/vnd.github.raw"],
                    stdout=out, stderr=subprocess.PIPE, check=True,
                )
            tmp.replace(dest)
            return
        except subprocess.CalledProcessError as exc:  # pragma: no cover - network path
            last_err = exc
            tmp.unlink(missing_ok=True)
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"fetch failed for {repo}@{ref[:8]}:{path}: {last_err}")


def restore_entry(entry: dict, root: Path) -> dict:
    dest = root / entry["dest"]
    pin = entry["sha256"]
    prefix_only = bool(entry.get("sha256_prefix_only"))

    def matches(digest: str) -> bool:
        return digest.startswith(pin) if prefix_only else digest == pin

    if dest.exists():
        got = sha256_file(dest)
        if matches(got):
            return {**_rec(entry, dest, got), "status": "present"}
        dest.unlink()
    if "parts" in entry:
        tmp = dest.with_suffix(".assembling")
        tmp.parent.mkdir(parents=True, exist_ok=True)
        with tmp.open("wb") as out:
            for part in entry["parts"]:
                p = root / "raw_parts" / Path(part).name
                fetch(entry["repo"], entry["ref"], part, p)
                with p.open("rb") as src:
                    shutil.copyfileobj(src, out, 1 << 20)
                p.unlink()
        got = sha256_file(tmp)
        if not matches(got):
            tmp.unlink(missing_ok=True)
            raise SystemExit(f"HASH MISMATCH for {entry['id']}: {got} != {pin}")
        tmp.replace(dest)
    else:
        fetch(entry["repo"], entry["ref"], entry["path"], dest)
        got = sha256_file(dest)
        if not matches(got):
            dest.unlink(missing_ok=True)
            raise SystemExit(f"HASH MISMATCH for {entry['id']}: {got} != {pin}")
    return {**_rec(entry, dest, got), "status": "restored"}


def _rec(entry: dict, dest: Path, digest: str) -> dict:
    return {"id": entry["id"], "dest": entry["dest"], "group": entry["group"], "bytes": dest.stat().st_size, "sha256": digest}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--group", default="all", choices=["core", "external", "registry", "all"])
    ap.add_argument("--target-dir", default=str(DEFAULT_TARGET))
    args = ap.parse_args()
    root = Path(args.target_dir)
    root.mkdir(parents=True, exist_ok=True)
    manifest = json.loads(MANIFEST.read_text())
    receipts = []
    changed = False
    for entry in manifest["files"]:
        if args.group != "all" and entry["group"] != args.group:
            continue
        rec = restore_entry(entry, root)
        receipts.append(rec)
        if entry.get("sha256_prefix_only") and rec["sha256"] != entry["sha256"]:
            entry["sha256"] = rec["sha256"]
            entry.pop("sha256_prefix_only", None)
            changed = True
        print(f"[{rec['status']:8s}] {rec['dest']}  {rec['bytes']:>12,d} B  {rec['sha256'][:16]}", flush=True)
    if changed:
        MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
        print("manifest updated with full SHA-256 digests")
    out = ROOT / "data"
    out.mkdir(exist_ok=True)
    receipt = {"generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "storage_root": str(root), "verified_files_count": len(receipts), "files": receipts}
    (out / "restore_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(f"OK: {len(receipts)} files verified; receipt at data/restore_receipt.json")


if __name__ == "__main__":
    sys.exit(main())
