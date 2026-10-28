"""Generate accessible static executive summaries from measured evidence."""
from pathlib import Path
import html
import json
ROOT = Path(__file__).resolve().parents[1]
esc = html.escape

def shell(title, body):
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} · GEMS research</title><link rel="stylesheet" href="style.css"></head><body><header><a class="brand" href="index.html">GEMS <span>/ KARAGE 01</span></a><nav><a href="index.html">Overview</a><a href="executive-summary.html">Submission guide</a><a href="https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/main/knowledge/REVIEW.md">Research</a></nav></header><main>{body}</main><footer>Evidence first. No automatic competition submissions. <a href="docs/data/run_card.json">Machine-readable run card ↗</a></footer></body></html>'''


def main():
    import runpy
    runpy.run_path(str(ROOT / 'scripts/build_current_review.py'), run_name='__main__')
    return
    # Preserve the concurrently merged detailed site and its independent audit.
    from build_detail_pages import main as build_details
    build_details()
    data = json.loads((ROOT/'docs/data/sources.json').read_text())
    audit = json.loads((ROOT/'docs/data/raster_audit.json').read_text())
    bysite = {r['site']: r for r in audit['rasters']}
    rows, cards = [], []
    for s in data['sites']:
        r = bysite[s['site']]
        maximum = max(c['within_3px_fraction'] for c in r['comparisons'])
        exact = [c['site'] for c in r['comparisons'] if c['same_dot_mask']]
        rows.append(f'''<tr><th><a href="#{s['site']}">{s['site']}</a></th><td><a href="{esc(s['artifact_url'])}">{esc(s['artifact'])}</a><small>Historical research file — not a new submission</small></td><td>Not estimable<small>No artifact-linked organizer receipt</small></td><td><span class="bad">FAIL</span><small>{maximum:.1%} max 3-px overlap</small></td><td>No</td></tr>''')
        cards.append(f'''<article id="{s['site']}"><div class="eyebrow">SITE EXECUTIVE SUMMARY</div><h3>{s['site']}</h3><p><strong>Submit: no.</strong> This is the historical best identified in the owner's supplied ranking, not a verified current winner. No new submission is recommended.</p><p>{r['dots']:,} positive pixels. {'Exactly the same positive-pixel mask as '+', '.join(exact)+'.' if exact else 'No exact mask match among the other eight audited files.'} It nevertheless fails the literal proximity rule: maximum directional overlap is {maximum:.2%}.</p><p>Leaderboard estimate: <strong>not estimable</strong>. Surface uniqueness, leakage and comparable holdout improvement are not certified by this historical audit.</p><details><summary>Artifact identity &amp; evidence</summary><p><a href="{esc(s['source_url'])}">Pinned source README ↗</a></p><p class="mono">{s['artifact_sha256']}</p><p>Grid: {esc(r['crs'])}; {r['shape'][0]} × {r['shape'][1]}. {'Whole-array finite.' if r['all_finite'] else 'Contains NaN: not cleared by our strict upload validator.'} Comparison domain is peer-derived, not an authenticated submission template.</p></details></article>''')
    body = f'''<div class="eyebrow">FAULT-MAPPING RESEARCH / EVIDENCE REVIEW</div><h1>A clear decision.<br>Before the next submission.</h1><p class="lead">Nine historical candidates audited. The locally validated unique H-K1-1 GeoTIFF is cleared to download; upload to DrivenData remains selector-pending. Historical reports are not organizer-confirmed.</p><section class="decision"><span class="badge">PROMOTED · OK TO DOWNLOAD · SELECTOR PENDING</span><h2>One cleared unique TIFF (H-K1-1)</h2><p>Primary file <code>' + PROMOTED_TIF + '</code> (SHA-256 <code>' + esc(PROMOTED_SHA[:16]) + '…</code>, 38,200 dots, float32 [0,1], EPSG:32611 3730×3292 @ 100 m). Passed 15/15 format and [0,1] checks and is byte-unique versus the 611-raster fleet. Upload to DrivenData requires a separate selector step — the weekly slot has not been spent.</p><a class="button" href="docs/downloads/' + PROMOTED_TIF + '" download>↓ Download cleared TIFF</a> <a class="button" href="executive-summary.html">Full submission guide →</a></section><div class="stats"><div><strong>9 / 9</strong><span>historical masks fail overlap</span></div><div><strong>0</strong><span>training experiments / slots used</span></div><div><strong>Unavailable</strong><span>defensible score estimate</span></div></div><section><div class="eyebrow">EXECUTIVE COMPARISON</div><h2>What to download — and what not to submit</h2><p>Links below open pinned historical artifacts for research only. They are not new submission downloads. Counts and overlap percentages are audit measurements, not performance scores.</p><p class="muted">Source check: {esc(data['checked_at'])}. Scope: nine historical files, not a complete live registry.</p><div class="table-wrap"><table><thead><tr><th>Site</th><th>Historical file / source</th><th>Estimated leaderboard score</th><th>Unique under protocol?</th><th>Submit?</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div></section><section><h2>What the H33-B2 result actually tells us</h2><p>H33-B2 is the highest result in the supplied nine-site historical ranking. Without an artifact-linked organizer receipt, that ranking is not organizer-confirmed evidence. Our independent raster audit establishes strong family similarity, not the causal explanation for the reported performance.</p><p>Thinning redundant predictions can retain distance-tolerant coverage while reducing false-positive mass. That is a testable explanation, not a validated forecast. Reproducing its dots is not a distinct scientific strategy.</p><a href="https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/main/knowledge/REVIEW.md">Read hypotheses, confounders and next steps ↗</a></section><div class="site-grid">{''.join(cards)}</div><section><h2>Evidence you can audit</h2><ul><li><a href="docs/data/sources.json">Source refs, artifact names and SHA-256 hashes</a></li><li><a href="docs/data/raster_audit.json">Independent pairwise comparisons</a></li><li><a href="docs/data/run_card.json">Negative run card and missing evidence</a></li><li><a href="https://github.com/drivendataorg/gems-prize-reference-solution">Official organizer reference implementation</a></li><li><a href="https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/">Official leaderboard — not verified live here</a></li></ul></section>'''
    # Keep the first integrated dashboard as a reproducible legacy view.
    # The current homepage is maintained by render_site.py.
    (ROOT/'legacy-overview.html').write_text(shell('Executive overview', body))
    PROMOTED_TIF = "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif"
    PROMOTED_ZIP = "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.zip"
    PROMOTED_SHA = "198076f81067353c3ee41d947c7830ef11db2e8128bc5f8c5bd20ef036736f76"
    PROMOTED_NAME = "karage1-hmas-sinter-dualcover-sep29-zeros"
    PROMOTED_NOTE = ("H-K1-1 HMAS mag-trough + PPGR + F2mDAB/sinter DualCover GBDT + "
                     "d=2.9px 300m submodular")
    guide = ('<div class="eyebrow">SUBMISSION GUIDE</div><h1>One cleared file.<br>All gates passed.</h1>'
             '<section class="decision">'
             '<span class="badge">PROMOTED · OK TO DOWNLOAD · SELECTOR PENDING FOR UPLOAD</span>'
             '<h2>' + PROMOTED_NAME + '</h2>'
             '<p>The locally validated unique submission is ready to download. Every check passed: '
             'single float32 band, EPSG:32611, 3730×3292 @ 100 m, exact template transform, finite '
             'values in [0,1], zero NaN/Inf, zero dots on the mapped catalogue, and a unique fingerprint '
             'versus the 611-raster fleet (max ≤3 px overlap 60.39% ≤ 70%).</p>'
             '<p><a class="button" href="docs/downloads/' + PROMOTED_TIF +
             '" download>↓ Download ' + PROMOTED_TIF + '</a> '
             '· SHA-256 <code>' + esc(PROMOTED_SHA) + '</code>'
             ' · note (' + str(len(PROMOTED_NOTE)) + '/140 chars): <code>' +
             esc(PROMOTED_NOTE) + '</code></p>'
             '<p class="muted">Verdict: PROMOTED locally. Upload to DrivenData is a separate selector '
             'step — the weekly slot has not been spent and this page is not upload authorization. '
             'Do not submit any of the nine historical files; all fail the uniqueness gate.</p>'
             '</section>'
             '<section><h2>The required sequence</h2><ol>'
             '<li><strong>Confirm the decision.</strong> Open the current run card. Verify the exact SHA-256, '
             'all feature canaries, matched holdout, and both full-registry novelty checks. A format pass '
             'alone is not approval.</li>'
             '<li><strong>Download the cleared TIFF.</strong> Use the enabled download link above. Recheck the '
             'downloaded bytes against the displayed SHA-256 before anything else.</li>'
             '<li><strong>Open DrivenData.</strong> Sign in to the '
             '<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">GEMS competition</a>, '
             'choose Submit → Make new submission, and verify your actual weekly allowance there.</li>'
             '<li><strong>Upload & record.</strong> Select the single-band GeoTIFF (or a ZIP containing only '
             'that TIFF), use the unique name and the note of at most 140 characters, and retain the organizer '
             'receipt. Do not claim a score until it is received.</li>'
             '</ol></section>'
             '<section><h2>About “Predicted values must be in range [0,1]”</h2>'
             '<p>That rejection means saved TIFF values fall outside [0,1] — negative nodata sentinels, '
             'infinity, NaN, or genuine out-of-range predictions. It is diagnosed by reopening the exact saved '
             'file, not by inspecting an in-memory array. The cleared H-K1-1 GeoTIFF was re-saved and '
             're-checked with <a href="scripts/validate_geotiff.py">scripts/validate_geotiff.py</a> '
             '(finite [0,1], no NaN/Inf). Format success alone never proves portal acceptance or competitive '
             'performance.</p></section>'
             '<section><h2>Access limitations</h2>'
             '<p>Direct data hosts such as Dropbox are outside the sandbox network allowlist; competition '
             'training data is restored from pinned GitHub blobs via <code>scripts/restore_data.py</code>. '
             'Login-walled DrivenData data and submission pages remain inaccessible from this environment, '
             'so no organizer receipt or live leaderboard score has been verified here. GitHub mirrors do '
             'not authenticate organizer provenance.</p></section>')
    (ROOT/'executive-summary.html').write_text(shell('Submission guide', guide))

if __name__ == '__main__':
    main()
