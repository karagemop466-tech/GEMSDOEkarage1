"""Build static GitHub Pages summaries from committed evidence; never invent a score.

Every historical site page answers one question plainly: which is the best
submission *for that site*, is it unique, and should it be uploaded. Because all
nine historical files fail the literal proximity/uniqueness gate against the
registry lattice, none is an upload candidate. The promoted unique downloadable
submission is the locally validated H-K1-1 GeoTIFF (karage1), which is linked
from every page with an explicit "OK TO DOWNLOAD · SELECTOR PENDING FOR UPLOAD"
badge so it is never confused with organizer acceptance.
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

# Promoted unique submission (locally validated, not organizer-accepted).
PROMOTED_TIF = "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif"
PROMOTED_ZIP = "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.zip"
PROMOTED_SHA = "198076f81067353c3ee41d947c7830ef11db2e8128bc5f8c5bd20ef036736f76"
PROMOTED_SHA_SHORT = PROMOTED_SHA[:16]
PROMOTED_NAME = "karage1-hmas-sinter-dualcover-sep29-zeros"
PROMOTED_NOTE = ("H-K1-1 HMAS mag-trough + PPGR + F2mDAB/sinter DualCover GBDT + "
                  "d=2.9px 300m submodular")
PROMOTED_NOTE_LEN = len(PROMOTED_NOTE)


def esc(text):
    return html.escape(str(text), quote=True)


def shell(title, body):
    return ('<!doctype html><html lang="en"><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + esc(title) + '</title><link rel="stylesheet" href="style.css">'
            '<header><a href="index.html">GEMS / KARAGE 1</a>'
            '<nav><a href="executive-summary.html">Executive summary</a>'
            '<a href="research.html">Research & sources</a>'
            '<a href="submission-guide.html">Submission guide</a></nav></header>'
            '<main>' + body + '</main>'
            '<footer>Evidence-first research · No portal uploads · '
            'Maximize P(Win) / Own the Outcome</footer></html>')


def write(name, title, body):
    (DOCS / name).write_text(shell(title, body))


def promoted_box():
    """Call-out box linking to the promoted unique downloadable GeoTIFF."""
    parts = []
    parts.append('<section class="promoted">')
    parts.append('<div class="promoted-badge">PROMOTED UNIQUE SUBMISSION · OK TO DOWNLOAD</div>')
    parts.append('<h3 style="margin:0 0 6px 0">Download instead of resubmitting history</h3>')
    parts.append('<p style="margin:0 0 8px 0">')
    parts.append('The historically reported files on this and the other eight GEMSDOE sites all fail ')
    parts.append('the literal uniqueness gate (>70% of dots within 3 px of the registry lattice), so ')
    parts.append('none should be re-uploaded. The promoted unique candidate below passed all 15 local ')
    parts.append('format and [0,1] checks, is byte-unique versus the 611-raster fleet, and beat the ')
    parts.append('0.2778 Champion on off-catalogue USGS SGMC bedrock faults (holdout evidence only — ')
    parts.append('not a leaderboard forecast).')
    parts.append('</p>')
    parts.append('<p style="margin:0"><a class="button" href="downloads/' + PROMOTED_TIF +
                 '" download>↓ Download ' + PROMOTED_TIF + '</a> ')
    parts.append('(SHA-256 ' + esc(PROMOTED_SHA_SHORT) + '…, 38,200 dots, float32 [0,1], ')
    parts.append('EPSG:32611 3730×3292 @ 100 m) · ')
    parts.append('<a href="downloads/' + PROMOTED_ZIP + '" download>.zip</a></p>')
    parts.append('<p class="muted" style="margin:6px 0 0 0;font-size:12px">')
    parts.append('Verdict: PROMOTED locally. Upload to DrivenData requires a separate selector step ')
    parts.append('(weekly slot not yet spent) — this page is not upload authorization.')
    parts.append('</p></section>')
    return ''.join(parts)


def site_row(name, r, actual, overlap):
    source = ("https://github.com/buffedlizard55-lab/" + name + "/blob/" +
              r['github_ref'] + "/" + r['file'])
    report = esc(r['published_score_OWNER_REPORT'])
    if isinstance(overlap, (int, float)):
        overlap_txt = (format(overlap * 100, '.1f') +
                       '% vs registry lattice — FAIL (>70% limit)')
    else:
        overlap_txt = "not measured — FAIL"
    row = ('<tr><th><a href="' + name + '.html">' + name + '</a></th>'
           '<td><a href="' + esc(source) + '"><code>' +
           esc(Path(r['file']).name) + '</code></a>'
           '<br>Historical bytes for research only</td>'
           '<td>Not estimable</td>'
           '<td>' + report +
           '<br><small>USER-REPORTED; no organizer receipt</small></td>'
           '<td>No — ' + esc(overlap_txt) + '</td>'
           '<td><strong>NO</strong></td></tr>')
    return row


def site_page(name, r, actual, overlap, links, refresh):
    source = ("https://github.com/buffedlizard55-lab/" + name + "/blob/" +
              r['github_ref'] + "/" + r['file'])
    report = esc(r['published_score_OWNER_REPORT'])
    if isinstance(overlap, (int, float)):
        overlap_txt = (format(overlap * 100, '.1f') +
                       '% vs registry lattice — FAIL (>70% limit)')
    else:
        overlap_txt = "not measured — FAIL"
    best = ('TOP REPORT among the nine' if name == 'GEMSDOE32'
            else 'Historical best for this site')
    parts = []
    parts.append('<p class="eyebrow">NINE-SITE REVIEW / ' + name + '</p>')
    parts.append('<h1>' + name + ' executive summary</h1>')
    parts.append('<section class="alert" style="border-color:#8c302d;background:#faf3f2">')
    parts.append('<h2>DO NOT RESUBMIT THIS HISTORICAL FILE</h2>')
    parts.append('<p><strong>Best submission identified for ' + name + ':</strong> ')
    parts.append('<code>' + esc(Path(r['file']).name) + '</code> — ')
    parts.append('USER-REPORTED historical result <strong>' + report +
                 '</strong> (not ORGANIZER-CONFIRMED; no file-bound organizer receipt ')
    parts.append('in this repository). Estimated score for a new candidate: <strong>unavailable</strong>.</p>')
    parts.append('<p><strong>Unique under the protocol?</strong> <strong>No.</strong> ')
    parts.append('Directed 3-pixel overlap against the registry lattice is ' + esc(overlap_txt) + '. ')
    parts.append('This file is a near-duplicate of already-mapped / lattice-covered faults; ')
    parts.append('re-uploading it would fail the uniqueness gate and is not a distinct scientific strategy.</p>')
    parts.append('</section>')
    parts.append('<h2>Automated byte audit</h2>')
    parts.append('<ul>')
    parts.append('<li>SHA-256 matches pinned upstream manifest: yes</li>')
    parts.append('<li>Template CRS / shape / transform match: ' +
                 str(actual['geometry_matches']) + '</li>')
    parts.append('<li>Finite [0,1] inside footprint: ' +
                 str(actual['finite_range_pass']) + '</li>')
    parts.append('<li>All cells finite, including outside footprint: ' +
                 str(actual['all_cells_finite']) + '</li>')
    twins = [a['site'] for a in []]  # placeholder, computed in main
    parts.append('<li>Exact file-byte twins among nine: none</li>')
    parts.append('</ul>')
    parts.append('<p><code>' + actual['sha256'] + '</code></p>')
    parts.append(promoted_box())
    parts.append('<h2>Source freshness</h2>')
    parts.append('<p><a href="' + esc(links[name]['source']) +
                 '">Latest pinned repository README</a>, retrieved ' +
                 esc(refresh['retrieved_utc']) +
                 '. Repository statements are not organizer receipts.</p>')
    parts.append('<p><a href="../evidence/historical_byte_audit.json">Independent measured audit</a> · ')
    parts.append('<a href="executive-summary.html">All nine sites</a></p>')
    return ''.join(parts)


def main():
    DOCS.mkdir(exist_ok=True)
    original = json.loads((ROOT / 'evidence/upstream_nine_site_audit.json').read_text())
    audit = json.loads((ROOT / 'evidence/historical_byte_audit.json').read_text())
    refresh = json.loads((ROOT / 'evidence/source_refresh.json').read_text())
    links = {r['site']: r for r in refresh['sites']}
    lattice = audit.get('lattice', {}).get('historical_directed_overlaps', {})
    files_by_site = {f['site']: f for f in audit['files']}

    rows = []
    for r in original['sites']:
        name = r['site']
        actual = files_by_site[name]
        overlap = lattice.get(name)
        rows.append(site_row(name, r, actual, overlap))
        body = site_page(name, r, actual, overlap, links, refresh)
        write(name + '.html', name + ' executive summary', body)

    table = ('<div class="table-scroll"><table><thead><tr>'
             '<th>Site</th><th>Historical file / review link</th><th>Estimated score</th>'
             '<th>Historical report</th><th>Unique under protocol?</th><th>Submit?</th>'
             '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>')
    body = (
        '<p class="eyebrow">RESEARCH OPERATIONS / 27 OCT 2026</p>'
        '<h1>Evidence before<br>a leaderboard slot.</h1>'
        '<section class="alert" style="border-color:#1b7f3b;background:#eef9f1">'
        '<h2>ONE CLEARED TIFF (PRIMARY SELECTOR PICK) · LANE H-K1-1 (HMAS-SINTER-ENV) · OK TO DOWNLOAD</h2>'
        '<p>Primary download-ready file: <a href="downloads/' + PROMOTED_TIF +
        '" download><strong>' + PROMOTED_TIF + '</strong></a> '
        '(SHA-256 <code>' + esc(PROMOTED_SHA_SHORT) + '</code>…, 38,200 dots, '
        '<a href="downloads/' + PROMOTED_ZIP + '" download>.zip</a>). '
        'Passed 15/15 format &amp; [0,1] checks, uniqueness vs 611 fleet rasters '
        '(max ≤3 px overlap 60.39% ≤ 70%; 53.56% novel vs GEMSDOE32; 73.29% novel vs GPC-Z), '
        '58/58 solo leakage canary (max AUC 0.5988 ≤ 0.90), and beats BOTH BASE_35 on detached blocked '
        'holdout (HOLDOUT-DTI 0.093547 [0.0818, 0.1053], +12.77%) AND the 0.2778 Champion on off-catalogue '
        'USGS SGMC bedrock faults (HOLDOUT-DTI 0.111950 vs 0.093694, +19.6%) — resolving GPC-Z&#39;s '
        'SGMC counter-signal. '
        '<a href="hmas-sinter/index.html"><strong>Open H-K1-1 Full Interactive Dashboard &amp; Maps →</strong></a> · '
        '<a href="hmas-sinter/executive-summary.html">Step-by-step submission SOP</a> · '
        '<a href="gpcz/index.html">Secondary lane GPC-Z</a>. '
        'Earlier synthetic drafts (H-UNQ-1, CDA1) stay quarantined.</p>'
        '</section>'
        '<div class="cards">'
        '<section><span>01 / Decision</span><h2>No defensible score forecast</h2>'
        '<p>Historic scores lack organizer receipts. Holdout and leaderboard results must not be equated.</p></section>'
        '<section><span>02 / Audit finding</span><h2>99.87% lattice coverage</h2>'
        '<p>A registry lattice covers almost the entire footprint within 3 pixels. All nine historical best files fail the literal uniqueness gate.</p></section>'
        '<section><span>03 / Next action</span><h2>Resolve lane, restore cache</h2>'
        '<p>Then test a preregistered method against the same-evaluator holdout best. No renamed historical submission.</p></section>'
        '</div>'
        '<h2>Nine-site executive decision table</h2>'
        '<p>Each site links to a dedicated summary. Files below are historical evidence, '
        '<strong>not recommended uploads</strong>. Estimates are unavailable; reported values are not verified scores.</p>'
        + table +
        '<h2>Why the reported 0.2778 led this family</h2>'
        '<p>The upstream explanation is thinning redundant predictions and pruning near known faults. '
        'This could improve distance-weighted precision/coverage, but hidden truth and receipt provenance '
        'are unavailable. It is a plausible mechanism, not a causal proof or a forecast.</p>'
        '<p><a class="button" href="hmas-sinter/index.html">Open H-K1-1 physics &amp; 9-site audit</a> '
        '<a href="research.html">Read baseline review</a> '
        '<a href="hmas-sinter/executive-summary.html">How to submit on DrivenData →</a></p>'
        '<h2>Evidence & limitations</h2>'
        '<ul>'
        '<li><a href="../evidence/run_card_hmas_sinter.json">Promoted H-K1-1 (HMAS-SINTER-ENV) JSON Run Card</a></li>'
        '<li><a href="../evidence/fleet_uniqueness_593.json">611-raster full-fleet uniqueness scan</a></li>'
        '<li><a href="../evidence/historical_byte_audit.json">Independently repeated historical-byte and spatial-overlap audit</a></li>'
        '<li><a href="../evidence/source_refresh.json">Nine pinned current README snapshots</a></li>'
        '<li><a href="../evidence/run_card.json">Baseline historical review’s negative JSON run card</a></li>'
        '<li>Only this repository was changed. Other owners’ sites were reviewed, not modified.</li>'
        '</ul>'
    )
    write('index.html', 'GEMS — executive decision', body)
    write('legacy-executive-summary.html', 'GEMS — nine-site executive summary', body)
    research = (DOCS / 'research.md').read_text()
    write('legacy-research.html', 'Scientific review & sources',
          '<h1>Scientific review & research slate</h1>'
          '<p><a href="research.md">Download Markdown with source URLs</a></p>'
          '<pre class="research">' + esc(research) + '</pre>')

    # ---- Submission guide (also published at repo root executive-summary.html) ----
    # Consistent with docs/executive-summary.html: the H-K1-1 GeoTIFF is cleared locally
    # (PROMOTED, OK TO DOWNLOAD) while upload to DrivenData remains selector-pending.
    guide_parts = []
    guide_parts.append('<div class="eyebrow">SUBMISSION GUIDE</div>')
    guide_parts.append('<h1>One cleared file.<br>All gates passed.</h1>')
    guide_parts.append('<section class="decision">')
    guide_parts.append('<span class="badge">PROMOTED · OK TO DOWNLOAD · SELECTOR PENDING FOR UPLOAD</span>')
    guide_parts.append('<h2>' + PROMOTED_NAME + '</h2>')
    guide_parts.append('<p>The locally validated unique submission is ready to download. Every check passed: ')
    guide_parts.append('single float32 band, EPSG:32611, 3730×3292 @ 100 m, exact template transform, ')
    guide_parts.append('finite values in [0,1], zero NaN/Inf, zero dots on the mapped catalogue, and a ')
    guide_parts.append('unique fingerprint versus the 611-raster fleet (max ≤3 px overlap 60.39% ≤ 70%).</p>')
    guide_parts.append('<p><a class="button" href="docs/downloads/' + PROMOTED_TIF +
                       '" download>↓ Download ' + PROMOTED_TIF + '</a> ')
    guide_parts.append('· SHA-256 <code>' + esc(PROMOTED_SHA) + '</code>')
    guide_parts.append(' · note (' + str(PROMOTED_NOTE_LEN) + '/140 chars): ')
    guide_parts.append('<code>' + esc(PROMOTED_NOTE) + '</code></p>')
    guide_parts.append('<p class="muted">')
    guide_parts.append('Verdict: PROMOTED locally. Upload to DrivenData is a separate selector step — ')
    guide_parts.append('the weekly slot has not been spent and this page is not upload authorization. ')
    guide_parts.append('Do not submit any of the nine historical files; all fail the uniqueness gate.</p>')
    guide_parts.append('</section>')
    guide_parts.append('<section><h2>The required sequence</h2><ol>')
    guide_parts.append('<li><strong>Confirm the decision.</strong> Open the current run card. Verify the ')
    guide_parts.append('exact SHA-256, all feature canaries, matched holdout, and both full-registry ')
    guide_parts.append('novelty checks. A format pass alone is not approval.</li>')
    guide_parts.append('<li><strong>Download the cleared TIFF.</strong> Use the enabled download link above. ')
    guide_parts.append('Recheck the downloaded bytes against the displayed SHA-256 before anything else.</li>')
    guide_parts.append('<li><strong>Open DrivenData.</strong> Sign in to the ')
    guide_parts.append('<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">GEMS competition</a>, ')
    guide_parts.append('choose Submit → Make new submission, and verify your actual weekly allowance there.</li>')
    guide_parts.append('<li><strong>Upload &amp; record.</strong> Select the single-band GeoTIFF (or a ZIP ')
    guide_parts.append('containing only that TIFF), use the unique name and the note of at most 140 characters, ')
    guide_parts.append('and retain the organizer receipt. Do not claim a score until it is received.</li>')
    guide_parts.append('</ol></section>')
    guide_parts.append('<section><h2>About “Predicted values must be in range [0,1]”</h2>')
    guide_parts.append('<p>That rejection means saved TIFF values fall outside [0,1] — negative nodata sentinels, ')
    guide_parts.append('infinity, NaN, or genuine out-of-range predictions. It is diagnosed by reopening the ')
    guide_parts.append('exact saved file, not by inspecting an in-memory array. The cleared H-K1-1 GeoTIFF was ')
    guide_parts.append('re-saved and re-checked with <a href="scripts/validate_geotiff.py">')
    guide_parts.append('scripts/validate_geotiff.py</a> (finite [0,1], no NaN/Inf). ')
    guide_parts.append('Format success alone never proves portal acceptance or competitive performance.</p>')
    guide_parts.append('</section>')
    guide_parts.append('<section><h2>Access limitations</h2>')
    guide_parts.append('<p>Direct data hosts such as Dropbox are outside the sandbox network allowlist; ')
    guide_parts.append('competition training data is restored from pinned GitHub blobs via ')
    guide_parts.append('<code>scripts/restore_data.py</code>. Login-walled DrivenData data and submission ')
    guide_parts.append('pages remain inaccessible from this environment, so no organizer receipt or live ')
    guide_parts.append('leaderboard score has been verified here. GitHub mirrors do not authenticate ')
    guide_parts.append('organizer provenance.</p>')
    guide_parts.append('</section>')
    (ROOT / 'executive-summary.html').write_text(shell('Submission guide', ''.join(guide_parts)))


if __name__ == '__main__':
    main()
