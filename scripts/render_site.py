#!/usr/bin/env python3
"""Render the historical site table and revision monitor from pinned evidence."""
from __future__ import annotations

import html
import json
import math
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
PAGES = [ROOT / "index.html", ROOT / "docs/executive-summary.html"]


def replace_section(page: str, name: str, content: str) -> str:
    start, end = f"<!-- {name}_START -->", f"<!-- {name}_END -->"
    if page.count(start) != 1 or page.count(end) != 1 or page.index(start) > page.index(end):
        raise ValueError(f"missing or duplicate {name} marker")
    return page[:page.index(start) + len(start)] + "\n" + content + "\n" + page[page.index(end):]


def build() -> tuple[str, str]:
    claims = json.loads((ROOT / "registry/historical_claims.json").read_text())
    entries = json.loads((ROOT / "registry/reference_assets.json").read_text())
    audit = json.loads((ROOT / "docs/data/reference-audit.json").read_text())
    assets = {x["id"]: x for x in entries}
    if len(claims) != 9 or len({x["site"] for x in claims}) != 9:
        raise ValueError("expected exactly nine distinct claims")
    if audit.get("schema") != "karage1-reference-audit-v1" or audit.get("submit_authorized") is not False:
        raise ValueError("unrecognized or unsafe audit")
    if not audit.get("all_72_directed_pairs_exceed_70_percent"):
        raise ValueError("current design assumes every selected historical file fails the pairwise rule")
    rows = []
    chips = []
    for claim in claims:
        name = claim["site"]
        entry = assets[name]
        if claim.get("score_class") != "USER-REPORTED / UNVERIFIED" or not isinstance(claim.get("reported_score"), (int, float)) or isinstance(claim["reported_score"], bool) or not math.isfinite(claim["reported_score"]) or not 0 <= claim["reported_score"] <= 1:
            raise ValueError(f"unverified historical claim is malformed for {name}")
        if audit["rows"][name]["sha256"] != entry["sha256"]:
            raise ValueError(f"audit and manifest disagree for {name}")
        pair_options = [(v["overlap_fraction"], k.split("->")[1]) for k, v in audit["directed_pairs"].items() if k.startswith(name + "->")]
        if len(pair_options) != 8:
            raise ValueError(f"missing comparisons for {name}")
        overlap, witness = max(pair_options)
        if overlap <= .7:
            raise ValueError(f"missing duplicate witness for {name}")
        safe = html.escape
        source = "https://github.com/" + entry["repo"] + "/blob/" + entry["ref"] + "/" + quote(entry["path"], safe="/")
        site_path = {"GEMSDOE31": "docs/", "GEMSDOE32": "docs/index.html", "GEMSDOE36": "docs/"}.get(name, "")
        peer_site = "https://buffedlizard55-lab.github.io/" + name + "/" + site_path
        filename = Path(entry["path"]).name
        best = name == "GEMSDOE32"
        row_class = ' class="best-row"' if best else ""
        best_label = '<span class="best-label">TOP REPORT</span>' if best else ""
        rows.append(
            f'<tr{row_class}>'
            f'<td><a href="{safe(peer_site, quote=True)}">{safe(name)} ↗</a>{best_label}</td>'
            f'<td><a class="file-link" href="{safe(source, quote=True)}" title="{safe(filename, quote=True)} · research only">{safe(claim["display_name"])}</a><span class="cell-sub" title="{safe(filename, quote=True)}">{safe(filename)}</span></td>'
            f'<td><span class="reported">{float(claim["reported_score"]):.4f}</span><span class="cell-sub">USER-REPORTED · UNVERIFIED</span></td>'
            '<td><span class="pill pill-neutral">Unavailable</span></td>'
            f'<td><span class="pill pill-red">NO</span><span class="cell-sub">{overlap * 100:.1f}% vs {safe(witness)}</span></td>'
            '<td><span class="pill pill-red">DO NOT RESUBMIT</span></td></tr>'
        )
        chips.append(
            f'<div class="feed-chip" data-source-repo="{safe(entry["repo"], quote=True)}" '
            f'data-source-ref="{safe(entry["ref"], quote=True)}">{safe(name)} '
            '<span data-source-state data-state="unknown">Not checked</span></div>'
        )
    return "\n".join(rows), "\n".join(chips)



def decision(prefix: str, heading_id: str) -> str:
    """Render the active fail-closed decision from the measured run card."""
    card = json.loads((ROOT / "docs/data/run-card.json").read_text())
    if card.get("verdict") != "negative" or card.get("ok_to_submit") is not False:
        raise ValueError("unexpected release state; require a new reviewed renderer")
    overlap = card["correlation_overlap_vs_registry"]
    if overlap.get("duplicate") is not True:
        raise ValueError("missing independently measured duplicate witness")
    f = html.escape(card["submission_file"])
    digest = html.escape(card["raster_sha256"])
    count = overlap["dots_within_3px"]
    dots = overlap["candidate_dots"]
    frac = overlap["directed_overlap"]
    h = card["holdout_dti"]
    return f'''<section class="decision-panel" aria-labelledby="{heading_id}">
      <div class="decision-main">
        <div class="status-line"><span class="status-dot"></span> CURRENT RELEASE DECISION <span class="status-tag status-stop">DO NOT SUBMIT</span></div>
        <h2 id="{heading_id}">No unique, validated file is authorized for submission.</h2>
        <p>The prior H-K1-1 raster has <strong>{count:,} of {dots:,} dots ({frac:.2%})</strong> within three pixels of a registered lattice: above the protocol’s 70% limit. Its local [0,1] check passed against an owner-mirrored grid; that does not establish uniqueness, portal acceptance, or a leaderboard score.</p>
        <p>Prior-session <strong>HOLDOUT-DTI</strong>: {h['dti']:.6f}, {html.escape(h['evaluator_version'])}, n={h['withheld_positives']:,}, 95% CI [{h['ci95'][0]:.6f}, {h['ci95'][1]:.6f}]. Not independently replayed and not a leaderboard estimate; the original split needs a buffered whole-component rerun.</p>
        <p>Historical name: <code>{html.escape(card['submission_name'])}</code>. Research-only note ({len(card['submission_note'])}/140 characters): <code>{html.escape(card['submission_note'])}</code>. Neither is an authorization to upload.</p>
        <div class="decision-actions"><a class="button button-light" href="{prefix}downloads/{f}" download>↓ Download prior TIFF — RESEARCH ONLY</a><a class="button button-light" href="{prefix}executive-summary.html#submission-guide">Submission instructions ↗</a><a class="button button-light" href="{prefix}data/run-card.json">Current run card ↗</a></div>
        <p class="download-help">Research artifact SHA-256 <code>{digest}</code>. Do not upload or rename it as a unique submission. <a href="{prefix}hmas-sinter/index.html">Review the failure and provenance ↗</a></p>
      </div>
      <div class="decision-side"><div><span>VERDICT</span><strong>Negative · duplicate</strong></div><div><span>LEADERBOARD ESTIMATE</span><strong>Unavailable</strong></div><div><span>SLOT DECISION</span><strong>Not authorized</strong></div><a href="{prefix}data/run-card.json">Machine-readable run card ↗</a></div>
    </section>'''

def main() -> None:
    rows, chips = build()
    for path in PAGES:
        page = replace_section(path.read_text(), "SITE_ROWS", rows)
        is_root = path == ROOT / "index.html"
        page = replace_section(page, "DECISION", decision("docs/" if is_root else "", "decision-title" if is_root else "summary-decision"))
        if is_root:
            page = replace_section(page, "FEED_ROWS", chips)
        path.write_text(page)
        print(f"rendered {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
