#!/usr/bin/env python3
"""Build fail-closed public entry points from the current review and prior claims.

Publishes the nine-site historical comparison and retains the locally built
unique GeoTIFF as a downloadable research artifact — explicitly NOT cleared to
submit, because it fails the strict Parallel-Run Protocol Rule-1 lattice gate
(a registry uniform-lattice raster overlaps 99.932% of its dots within 3 px,
above the 70% limit).
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'
claims = json.loads((ROOT / 'registry/historical_claims.json').read_text())
assets = {x['id']: x for x in json.loads((ROOT / 'registry/reference_assets.json').read_text())}

# Locally built unique research artifact (NOT organizer-cleared to submit).
UNIQUE_TIF = "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif"
UNIQUE_SHA = "198076f81067353c3ee41d947c7830ef11db2e8128bc5f8c5bd20ef036736f76"
UNIQUE_NAME = "karage1-hmas-sinter-dualcover-sep29-zeros"
UNIQUE_NOTE = ("H-K1-1 HMAS mag-trough + PPGR + F2mDAB/sinter DualCover GBDT + "
               "d=2.9px 300m submodular")
UNIQUE_NOTE_LEN = len(UNIQUE_NOTE)
LATTICE_OVERLAP = 0.99932  # vs uniform_lattice_diagnostic registry raster


def esc(text):
    return html.escape(str(text), quote=True)


def status_box(prefix):
    """Honest status call-out: unique artifact, not cleared to submit."""
    rel = prefix + 'downloads/' if prefix else 'downloads/'
    parts = []
    parts.append('<section class="status fail-closed">')
    parts.append('<div class="status-badge">NOT CLEARED TO SUBMIT · FAIL CLOSED</div>')
    parts.append('<h2 style="margin:0 0 8px 0">Unique artifact · download for review only · do not upload</h2>')
    parts.append('<p>A locally built unique single-band GeoTIFF is retained below for download and review. ')
    parts.append('It is byte-unique versus the discrete peer submissions, but it FAILS the strict Rule-1 ')
    parts.append('lattice uniqueness gate: a registry uniform-lattice raster overlaps ')
    parts.append(format(LATTICE_OVERLAP * 100, '.3f') + '% of its dots within 3 px, above the 70% limit. ')
    parts.append('Per the Parallel-Run Protocol it must be logged as a duplicate/drift and stopped — it is ')
    parts.append('<strong>NOT OK to submit</strong> to the DrivenData portal.</p>')
    parts.append('<p><a class="button" href="' + rel + UNIQUE_TIF + '" download>')
    parts.append('↓ Download ' + UNIQUE_TIF + '</a> ')
    parts.append('(SHA-256 <code>' + esc(UNIQUE_SHA[:16]) + '</code>…, 38,200 dots, float32 [0,1], ')
    parts.append('EPSG:32611 3730×3292 @ 100 m)</p>')
    parts.append('<p class="muted" style="font-size:12px">Status: NOT OK to submit. This page is not upload ')
    parts.append('authorization. No organizer receipt or live leaderboard score has been verified from this ')
    parts.append('sandbox.</p>')
    parts.append('</section>')
    return ''.join(parts)


def render(prefix):
    rows = []
    for c in sorted(claims, key=lambda c: -c['reported_score']):
        name = c['site']
        asset = assets[name]
        filename = html.escape(Path(asset['path']).name)
        rows.append(f'<tr><th><a href="{prefix}{name}.html">{name}</a></th><td>{filename} <small>historical only</small></td><td>{c["reported_score"]:.4f} <small>USER-REPORTED, unverified</small></td><td>Unavailable</td><td>No: prior lattice witness</td></tr>')
    table = ''.join(rows)
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>GEMS executive decision</title><link rel="stylesheet" href="{prefix}style.css"></head><body><header><a href="{prefix}index.html">GEMS / KARAGE 1</a><nav><a href="{prefix}submission-guide.html">Submission guide</a><a href="{prefix}research.html">Research</a><a href="{prefix}sources.html">Sources</a></nav></header><main><p class="eyebrow">CURRENT REVIEW · 28 OCT 2026</p><h1>Executive decision</h1>{status_box(prefix)}<section class="alert"><h2>DO NOT SUBMIT — no cleared new TIFF</h2><p>The earlier HMAS and GPC-Z promotion claims are superseded. Each prior audit recorded a registry lattice exceeding the literal three-pixel overlap limit, but excluded it from its claimed passing maximum. The HMAS canary also treated a constant feature as passing. Official template and registry completeness have not been independently verified here.</p><p><a href="https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/main/knowledge/review-2026-10-28.md">Read the review and next steps</a> · <a href="https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/main/evidence/review_2026-10-28.json">Current machine-readable decision</a></p></section><h2>Nine-site historical comparison</h2><p>Historical reports are not organizer receipts. The table identifies past files for research, not files to submit; a new score cannot be estimated reliably from these numbers. The highest user-reported result is GEMSDOE32, not evidence of a winning new candidate.</p><div class="table-scroll"><table><thead><tr><th>Site</th><th>Historical file</th><th>Reported score</th><th>New score estimate</th><th>Unique under literal protocol?</th></tr></thead><tbody>{table}</tbody></table></div><h2>What might explain the historical leader</h2><p>Removing redundant dots and some near mapped faults may have improved the coverage-versus-false-positive tradeoff; private labels and a receipt are unavailable, so this is not a causal proof or a forecast. <a href="https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/main/knowledge/research-review.md">See analysis and hypotheses.</a></p><h2>Next steps</h2><p>Resolve the missing parallel-run lane and registry scope; restore the official template and shared cached data; rerun visible-only spatial holdouts, canaries, full registry comparison and saved-byte validation. A separate selector must confirm a submission slot. No portal upload was performed.</p><p><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/">Official competition problem and metric</a> · <a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official reference solution</a></p></main><footer>Evidence first · Maximize P(Win) · Own the Outcome</footer></body></html>'''


for path, prefix in [(ROOT/'index.html', 'docs/'), (ROOT/'executive-summary.html', 'docs/'), (DOCS/'index.html', ''), (DOCS/'executive-summary.html', ''), (DOCS/'legacy-executive-summary.html', ''), (DOCS/'hmas-sinter/index.html', '../'), (DOCS/'hmas-sinter/executive-summary.html', '../'), (DOCS/'gpcz/index.html', '../'), (DOCS/'gpcz/how-to-submit.html', '../'), (DOCS/'how-to-submit.html', '')]:
    path.write_text(render(prefix), encoding='utf-8')
