#!/usr/bin/env python3
"""Replace superseded lane dashboards with clear, auditable stop notices.

The original lane evidence remains in evidence/ and git history. These pages do
not manufacture a new candidate or offer a disabled candidate as a download.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'


def page(title: str, body: str, prefix: str = '../') -> str:
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} · GEMS</title><link rel="stylesheet" href="{prefix}style.css"></head><body><header><a href="{prefix}../index.html">GEMS / KARAGE 1</a><nav><a href="{prefix}executive-summary.html">Executive summary</a><a href="{prefix}research.html">Research</a></nav></header><main>{body}</main><footer>Historical research only · No competition submission authorized</footer></body></html>'''


def lane_body(key: str, prefix: str) -> str:
    data = json.loads((ROOT / 'evidence/prior_candidate_audit.json').read_text())
    r = data['results'][key]
    name = 'HMAS-SINTER-ENV' if key == 'hmas' else 'GPC-Z'
    return f'''<div class="eyebrow">SUPERSEDED LANE / {name}</div><h1>Historical result.<br>Not a submission.</h1><section class="alert"><h2>DO NOT SUBMIT</h2><p>The earlier clearance was withdrawn: {r["dots_within_closed_3px_disk"]:,} of {r["dots"]:,} dots ({r["directed_overlap_fraction"]:.4%}) lie within 3 pixels of a registered lattice. The protocol limit is 70%. This is a proximity rule, not proof of an exact pixel copy.</p><p>Saved bytes are kept for research and audit only; no weekly slot has been selected in this session.</p><p><a href="{prefix}data/prior_candidate_audit.json">Reproduced byte and geometry audit →</a> · <a href="{prefix}data/run-card.json">Current run card →</a></p></section><section><h2>What the local format check proves</h2><p>The old all-finite file has one float32 band, finite in-footprint values in [0,1], and matches a pinned peer template’s CRS, shape, and transform. The peer template is not organizer-authenticated; its outside-footprint values are not null/NaN, and portal acceptance has not been tested.</p><p>File under review: <code>{html.escape(Path(r['file']).name)}</code><br>SHA-256: <code>{r['sha256']}</code></p><p>Old holdout claims are historical, have not been replayed in this session and cannot be converted into a leaderboard score. The complete registry and original pre-placement surface have not been independently rechecked.</p></section><section><h2>Next steps</h2><p>Follow the current <a href="{prefix}executive-summary.html">executive summary and submission guide</a>; do not rerun the retired lane after its duplicate stop. The <a href="{prefix}research.html">research review</a> separates hypotheses from measurements.</p></section>'''


def build() -> None:
    for key, names in {
        'hmas': ['index.html', 'executive-summary.html'],
        'gpcz': ['index.html', 'how-to-submit.html', 'nine-sites.html', 'research.html',
                 'knowledge.html', 'sources.html', 'standing-prompt.html'],
    }.items():
        folder = DOCS / ('hmas-sinter' if key == 'hmas' else 'gpcz')
        folder.mkdir(parents=True, exist_ok=True)
        for name in names:
            (folder / name).write_text(page(f'{key.upper()} historical lane', lane_body(key, '../')))
    # Older top-level aliases used to point to an obsolete GPC-Z upload guide.
    aliases = {
        'how-to-submit.html': ('Submission guide', 'submission-guide.html'),
        'nine-sites.html': ('Nine-site review', 'executive-summary.html#comparison'),
        'knowledge.html': ('Research and knowledge', 'research.html'),
        'sources.html': ('Official sources', 'research.html#sources'),
        'standing-prompt.html': ('Standing brief', '../README.md'),
    }
    for name, (title, target) in aliases.items():
        body = f'''<div class="eyebrow">CURRENT RESOURCE</div><h1>{html.escape(title)}</h1><section class="alert"><h2>DO NOT SUBMIT</h2><p>The previous lane clearance is superseded. There is no approved competition TIFF.</p><p><a href="{target}">Open the current {html.escape(title.lower())} →</a></p></section>'''
        # This file lives directly in docs/, so point at its local stylesheet.
        (DOCS / name).write_text(page(title, body, prefix=''))
    print('Built fail-closed historical lane notices and current resource aliases.')


if __name__ == '__main__':
    build()
