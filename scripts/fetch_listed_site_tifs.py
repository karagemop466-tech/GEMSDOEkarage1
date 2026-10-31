#!/usr/bin/env python3
"""Inventory and fetch every GeoTIFF in the GitHub repositories behind the listed GEMSDOE sites.

The owner/repo pairs below are transcribed from the GitHub Pages URLs in the session prompt
(``https://<owner>.github.io/<repo>/...``). For each repository this script:

1. reads the default branch with ``gh api repos/<owner>/<repo>`` (GitHub API, authenticated);
2. lists every ``*.tif`` path in the recursive git tree (``git/trees/<branch>?recursive=1``);
3. downloads each blob as raw bytes into ``data/peers/<owner>__<repo>/`` (git-ignored);
4. records path, byte size, SHA-256 and the tree blob SHA in an evidence JSON.

It does not decide anything. A site whose TIFs are not in its repository tree (for example
files attached to a GitHub Release) is recorded as ``no_tif_in_tree``; those files are NOT
checked and must be listed as a limitation.
"""
from __future__ import annotations

import base64
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "peers"
OUT = ROOT / "evidence" / "listed_sites_tif_inventory_20261031.json"

# (owner, repo) — transcribed from the session prompt's site URLs.
SITES = [
    *[("buffedlizard55-lab", r) for r in [
        "GEMSDOE", "6GEMSDOE", "GEMSDOE2", "GEMSDOE3", "GEMSDOE4", "5GEMSDOE", "7GEMSDOE", "8GEMSDOE",
        "GEMSDOE9", "11GEMSDOE", "12GEMSDOE", "15GEMSDOE", "14GEMSDOE", "17GEMSDOE", "18GEMSDOE",
        "19GEMSDOE", "GEMSDOE10", "13GEMSDOE", "16GEMSDOE", "GEMSDOE21", "20GEMSDOE", "GEMSDOE22",
        "GEMSDOE23", "GEMSDOE24", "GEMSDOE25", "GEMSDOE26", "GEMSDOE27", "GEMSDOE28", "GEMSDOE29",
        "GEMSDOE30", "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE34", "GEMSDOE35", "GEMSDOE36",
        "GEMSDOE37", "GEMSDOE38", "GEMSDOE39", "GEMSDOE40", "GEMSDOE41", "GEMSDOE42", "GEMSDOE43",
        "GEMSDOE44", "GEMSDOE45", "GEMSDOE46", "GEMSDOE47", "GEMSDOE48", "GEMSDOE49", "GEMSDOE50",
        "GEMSDOE51", "GEMSDOE52", "GEMSDOE53", "GEMSDOE54", "55GEMSDOE", "56GEMSDOE", "57GEMSDOE",
        "58GEMSDOE", "59GEMSDOE", "60GEMSDOE", "61GEMSDOE", "62GEMSDOE", "GEMSDOE63", "GEMSDOE64",
        "GEMSDOE65", "GEMSDOE66", "GEMSDOE67", "GEMSDOE68", "GEMSDOE69", "GEMSDOE70", "GEMSDOE71",
        "GEMSDOE72", "GEMSDOE73", "GEMSDOE74", "GEMSDOE75", "GEMSDOE76", "GEMSDOE77", "GEMSDOE78",
        "GEMSDOE79", "GEMSDOE80", "GEMSDOE81", "GEMSDOE82", "GEMSDOE83", "GEMSDOE84", "GEMSDOE85",
        "GEMSDOE86", "GEMSDOE87", "GEMSDOE88", "GEMSDOE89", "GEMSDOE90", "GEMSDOE91", "GEMSDOE92"]],
    ("kanlerxz87-cyber", "KANLERGEMSDOE3"), ("kanlerxz87-cyber", "KANLERGEMSDOE1"),
    ("kanlerxz87-cyber", "KANLERGEMSDOE2"),
    ("eugboogieman123-ops", "EUGGEMSDOE3"), ("eugboogieman123-ops", "EUGGEMSDOE2"),
    ("eugboogieman123-ops", "EUGGEMSDOE1"),
    ("wingbangboozle1-lang", "WBGGEMSDOE3"), ("wingbangboozle1-lang", "WBGGEMSDOE2"),
    ("wingbangboozle1-lang", "WBGGEMSDOE1"),
    ("ginnymcfiner23-ux", "GINNYGEMSDOE3"), ("ginnymcfiner23-ux", "GINNYGEMSDOE2"),
    ("ginnymcfiner23-ux", "GINNYGEMSDOE1"),
    ("karagemop466-tech", "GEMSDOEkarage3"), ("karagemop466-tech", "GEMSDOEkarage2"),
    ("karagemop466-tech", "GEMSDOEkarage1"),
    ("apartanish22-droid", "ApartGEMSDOE2"), ("apartanish22-droid", "ApartGEMSDOE3"),
    ("apartanish22-droid", "ApartGEMSDOE1"),
    ("sassnarep3-star", "GEMSDOESASS3"), ("sassnarep3-star", "GEMSDOESASS2"),
    ("sassnarep3-star", "GEMSDOESASS1"),
]


def gh_json(args: list[str]):
    proc = subprocess.run(["gh", "api", *args], capture_output=True, text=True, timeout=120)
    if proc.returncode != 0:
        return None, proc.stderr.strip()[:300]
    return json.loads(proc.stdout), None


def gh_blob(owner: str, repo: str, sha: str, target: Path) -> int:
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as fh:
        proc = subprocess.run(
            ["gh", "api", f"repos/{owner}/{repo}/git/blobs/{sha}", "-H", "Accept: application/vnd.github.raw"],
            stdout=fh, stderr=subprocess.PIPE, timeout=600)
    if proc.returncode != 0:
        target.unlink(missing_ok=True)
        raise RuntimeError(proc.stderr.decode()[:300])
    return target.stat().st_size


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> dict:
    report = {
        "schema": "listed-sites-tif-inventory-v1",
        "date": "2026-10-31",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "method": "gh api: repo metadata -> recursive git tree -> raw blob download; SHA-256 of bytes",
        "sites": [],
    }
    for owner, repo in SITES:
        entry = {"owner": owner, "repo": repo, "url": f"https://{owner}.github.io/{repo}/"}
        meta, err = gh_json([f"repos/{owner}/{repo}"])
        if meta is None:
            entry.update(status="repo_unavailable", error=err, tifs=[])
            report["sites"].append(entry)
            print("unavailable", owner, repo, flush=True)
            continue
        branch = meta.get("default_branch", "main")
        tree, err = gh_json([f"repos/{owner}/{repo}/git/trees/{branch}?recursive=1"])
        if tree is None:
            entry.update(status="tree_unavailable", error=err, branch=branch, tifs=[])
            report["sites"].append(entry)
            print("tree unavailable", owner, repo, flush=True)
            continue
        items = [t for t in tree.get("tree", []) if t.get("type") == "blob"
                 and t.get("path", "").lower().endswith((".tif", ".tiff"))]
        entry.update(branch=branch, tree_truncated=bool(tree.get("truncated")), tifs=[])
        if not items:
            entry["status"] = "no_tif_in_tree"
        else:
            entry["status"] = "fetched"
        for item in items:
            rel = item["path"]
            target = DEST / f"{owner}__{repo}" / rel
            try:
                size = gh_blob(owner, repo, item["sha"], target)
                entry["tifs"].append({"path": rel, "bytes": size, "sha256": sha256(target),
                                      "blob_sha": item["sha"], "local": str(target.relative_to(ROOT))})
            except RuntimeError as exc:  # keep going; record the failure
                entry["tifs"].append({"path": rel, "error": str(exc)})
        report["sites"].append(entry)
        print(f"{entry['status']:>16} {owner}/{repo}: {len(items)} tif", flush=True)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=1) + "\n")
    return report


if __name__ == "__main__":
    r = main()
    counts: dict[str, int] = {}
    for s in r["sites"]:
        counts[s["status"]] = counts.get(s["status"], 0) + 1
    print(json.dumps({"sites": len(r["sites"]), "status_counts": counts,
                      "tifs": sum(len(s["tifs"]) for s in r["sites"])}, indent=1))
    sys.exit(0)
