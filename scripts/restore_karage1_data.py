#!/usr/bin/env python3
"""Deterministic SHA-256-verified restorer for GEMSDOEkarage1 core & external layers.

Restores all competition inputs, public-domain external geological layers (USGS GeoDAWN,
USGS 3DEP 1 m LiDAR & 10 m Seamless DEM / chi-knickpoints, BLM MLRS closed lode claims,
DOE GDR #1391 INGENIOUS thermal/sinter/vents), and scored focus-site rasters from
``registry/karage1_data_manifest.json`` into ``GEMS_DATA_DIR`` (default ``/tmp/gems_data``).
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from gemskarage1.paths import REGISTRY_DIR, data_dir  # noqa: E402


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _fetch_part(repo: str, ref: str, rel_path: str, out_fh, attempts: int = 4) -> None:
    quoted = urllib.parse.quote(rel_path, safe="/")
    has_gh = shutil.which("gh") is not None
    last_err: Exception | None = None
    for i in range(attempts):
        try:
            if has_gh:
                proc = subprocess.run(
                    [
                        "gh",
                        "api",
                        f"repos/{repo}/contents/{quoted}?ref={ref}",
                        "-H",
                        "Accept: application/vnd.github.raw",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=True,
                )
                out_fh.write(proc.stdout)
                return
            raw_url = f"https://api.github.com/repos/{repo}/contents/{quoted}?ref={ref}"
            req = urllib.request.Request(
                raw_url,
                headers={
                    "Accept": "application/vnd.github.raw",
                    "User-Agent": "GEMSDOEkarage1-restore/2.1",
                },
            )
            with urllib.request.urlopen(req, timeout=180) as resp:
                shutil.copyfileobj(resp, out_fh, 1 << 20)
            return
        except Exception as exc:  # pragma: no cover - transient network retry
            last_err = exc
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"Failed fetching {repo}@{ref[:8]}:{rel_path}: {last_err}")


def _resolve_source(entry: dict) -> tuple[str, str, list[str]]:
    src = entry.get("source") if isinstance(entry.get("source"), dict) else entry
    repo = src["repo"]
    ref = src["ref"]
    if "parts" in src and src["parts"]:
        parts = list(src["parts"])
    else:
        parts = [src["path"]]
    return repo, ref, parts


def _restore_one(entry: dict, target_dir: Path) -> tuple[str, str, int]:
    dest = target_dir / entry["dest"]
    expected = entry["sha256"].lower()
    if dest.is_file() and _sha256(dest) == expected:
        return entry["dest"], "cached", dest.stat().st_size

    dest.parent.mkdir(parents=True, exist_ok=True)
    repo, ref, parts = _resolve_source(entry)
    tmp = dest.with_suffix(dest.suffix + ".part")
    with tmp.open("wb") as out:
        for rel in parts:
            _fetch_part(repo, ref, rel, out)
    actual = _sha256(tmp)
    if actual != expected:
        tmp.unlink(missing_ok=True)
        raise RuntimeError(f"SHA-256 mismatch for {dest}: got {actual}, expected {expected}")
    tmp.replace(dest)
    return entry["dest"], "restored", dest.stat().st_size


def restore_manifest(manifest_path: Path, target_dir: Path, workers: int = 6) -> dict:
    manifest = json.loads(manifest_path.read_text())
    entries = manifest.get("files", manifest.get("entries", []))
    restored = 0
    skipped = 0
    errors: list[str] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(_restore_one, e, target_dir): e["dest"] for e in entries}
        for fut in as_completed(futs):
            name = futs[fut]
            try:
                dest_rel, status, nbytes = fut.result()
                if status == "cached":
                    skipped += 1
                else:
                    restored += 1
                print(f"[{status.upper():8s}] {dest_rel} ({nbytes:,} bytes)")
            except Exception as exc:  # pragma: no cover
                errors.append(f"{name}: {exc}")
                print(f"[ERROR   ] {name}: {exc}", file=sys.stderr)
    if errors:
        raise RuntimeError(f"{len(errors)} files failed to restore: {errors[:3]}")
    return {"restored": restored, "skipped": skipped, "total": len(entries), "target_dir": str(target_dir)}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", type=Path, default=REGISTRY_DIR / "karage1_data_manifest.json")
    ap.add_argument("--target-dir", type=Path, default=data_dir())
    ap.add_argument("--workers", type=int, default=6)
    args = ap.parse_args()
    res = restore_manifest(args.manifest, args.target_dir, workers=args.workers)
    print(json.dumps(res, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
