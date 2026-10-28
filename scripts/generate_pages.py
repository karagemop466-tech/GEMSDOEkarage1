#!/usr/bin/env python3
"""Render safe historical lane pages from the active, independently checked run card."""
from __future__ import annotations
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def page(title: str, body: str) -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{html.escape(title)}</title><link rel="stylesheet" href="../style.css"></head><body><header><a href="../../index.html">GEMS / KARAGE 1</a><nav><a href="../executive-summary.html">Executive summary</a><a href="../research.html">Research</a><a href="../submission-guide.html">Submission guide</a></nav></header><main>{body}</main><footer>Evidence first. No automated portal uploads.</footer></body></html>'''


def build_lanes() -> None:
    audit = json.loads((ROOT / "evidence/release_reassessment_20261028.json").read_text())
    if audit["verdict"] != "negative":
        raise ValueError("release state changed; review lane renderer")
    for key, folder, label in (("hmas", "hmas-sinter", "H-K1-1 HMAS-SINTER"),
                               ("gpcz", "gpcz", "GPC-Z")):
        c = audit["candidates"][key]
        fname = Path(c["file"]).name
        body = f'''<p class="eyebrow">INDEPENDENT REASSESSMENT · 28 OCT 2026</p><h1>{html.escape(label)} — research only</h1>
<section class="alert"><h2>DO NOT SUBMIT</h2><p>This previously generated raster is a literal registry duplicate. {c['lattice_dots_within_3px_count']:,} of {c['dots_in_footprint']:,} dots ({c['lattice_directed_overlap']:.2%}) lie within three pixels of a registered lattice; the limit is 70%.</p></section>
<p><a href="../downloads/{html.escape(fname)}" download>Download prior TIFF for research only</a> · <a href="../../evidence/release_reassessment_20261028.json">Independent audit JSON</a></p>
<p>SHA-256 <code>{c['sha256']}</code>. Local saved-byte checks pass for finite [0,1] values and the mirrored grid, but do not establish organizer acceptance. The official description asks for null/NaN outside bounds while the reported portal error makes outside handling uncertain.</p>
<p>No new file is cleared, no forecast is available, and the previous nonliteral fleet clearance is superseded. The prior pre-placement surface was not independently replayed.</p>
<p><a href="../executive-summary.html#comparison">Nine-site executive table</a> · <a href="../executive-summary.html#submission-guide">Future submission steps</a> · <a href="../data/run-card.json">Current negative run card</a></p>'''
        out = DOCS / folder
        out.mkdir(exist_ok=True)
        (out / "index.html").write_text(page(label, body))
        guide = '''<h1>How to submit a future candidate</h1><section class="alert"><h2>DO NOT SUBMIT the current historical raster</h2><p>The uniqueness gate failed; the file is for research only.</p></section><ol><li>Wait for a new, genuinely distinct TIFF to pass the whole-component holdout, canary, literal full-registry, and saved-byte checks.</li><li>A separate selector checks the account's currently displayed weekly limit.</li><li>Download the approved single-band TIFF, verify its SHA-256, then choose it on the DrivenData New submission form.</li><li>Enter the short note from its run card and save the resulting organizer receipt. A local holdout is not a leaderboard score.</li></ol><p><a href="../executive-summary.html#submission-guide">Complete checklist and official links</a></p>'''
        (out / ("executive-summary.html" if key == "hmas" else "how-to-submit.html")).write_text(page("Submission guide", guide))
    # Retire older GPC-Z subpage copies that claimed an unverified score or approval.
    for name, target, description in (("nine-sites.html", "../nine-sites.html", "Nine-site comparison"),
                                      ("knowledge.html", "../knowledge.html", "Scientific context"),
                                      ("sources.html", "../sources.html", "Sources and data")):
        body = f'<h1>{description}</h1><section class="alert"><h2>DO NOT SUBMIT</h2><p>The earlier GPC-Z raster failed the literal uniqueness rule.</p></section><p><a href="{target}">Open the current {description.lower()}</a></p>'
        (DOCS / "gpcz" / name).write_text(page(description, body))
    # Older top-level alias previously claimed that GPC-Z was approved.
    (DOCS / "how-to-submit.html").write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Submission guide</title><link rel="stylesheet" href="style.css"></head><body><main><h1>Submission guide</h1><section class="alert"><h2>DO NOT SUBMIT</h2><p>No file is currently approved. The earlier GPC-Z and H-K1-1 files failed the literal uniqueness gate.</p></section><p><a href="executive-summary.html#submission-guide">Read the current step-by-step guide</a> · <a href="../index.html">Home</a></p></main></body></html>''')


def main() -> int:
    build_lanes()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
