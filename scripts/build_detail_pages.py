"""Build static GitHub Pages summaries from committed evidence; never invent a score.

Every historical site page answers one question plainly: which is the best
submission *for that site*, is it unique, and should it be uploaded. All nine
historical files fail the literal uniqueness/unproven-score gates, so none is
an upload candidate. A locally built unique GeoTIFF is retained as a
downloadable research artifact, but it is explicitly NOT cleared to submit:
it fails the strict Parallel-Run Protocol Rule-1 lattice gate (a registry
uniform-lattice raster overlaps 99.932% of its dots within 3 px, above the
70% limit), so the only defensible status is "do not submit."
"""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

# Locally built unique research artifact (NOT organizer-cleared to submit).
UNIQUE_TIF = "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif"
UNIQUE_ZIP = "karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.zip"
UNIQUE_SHA = "198076f81067353c3ee41d947c7830ef11db2e8128bc5f8c5bd20ef036736f76"
UNIQUE_NAME = "karage1-hmas-sinter-dualcover-sep29-zeros"
UNIQUE_NOTE = ("H-K1-1 HMAS mag-trough + PPGR + F2mDAB/sinter DualCover GBDT + "
               "d=2.9px 300m submodular")
UNIQUE_NOTE_LEN = len(UNIQUE_NOTE)
LATTICE_OVERLAP = 0.99932  # vs uniform_lattice_diagnostic registry raster


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


def status_box():
    """Honest status call-out: unique artifact, not cleared to submit."""
    parts = []
    parts.append('<section class="status fail-closed">')
    parts.append('<div class="status-badge">NOT CLEARED TO SUBMIT · FAIL CLOSED</div>')
    parts.append('<h3 style="margin:0 0 6px 0">Unique downloadable artifact · do not upload</h3>')
    parts.append('<p style="margin:0 0 8px 0">')
    parts.append('A locally built unique single-band GeoTIFF is retained below for download and review. ')
    parts.append('It is byte-unique versus the discrete peer submissions (max 60.39% within 3 px), but it ')
    parts.append('FAILS the strict Rule-1 lattice uniqueness gate: a registry uniform-lattice raster ')
    parts.append('overlaps ' + format(LATTICE_OVERLAP * 100, '.3f') + '% of its dots within 3 px, above ')
    parts.append('the 70% limit. Per the Parallel-Run Protocol it must be logged as a duplicate/drift and ')
    parts.append('stopped — it is NOT cleared for the DrivenData portal.</p>')
    parts.append('<p style="margin:0"><a class="button" href="downloads/' + UNIQUE_TIF +
                 '" download>↓ Download ' + UNIQUE_TIF + '</a> ')
    parts.append('(SHA-256 ' + esc(UNIQUE_SHA[:16]) + '…, 38,200 dots, float32 [0,1], ')
    parts.append('EPSG:32611 3730×3292 @ 100 m) · ')
    parts.append('<a href="downloads/' + UNIQUE_ZIP + '" download>.zip</a></p>')
    parts.append('<p class="muted" style="margin:6px 0 0 0;font-size:12px">')
    parts.append('Status: NOT OK to submit. This page is not upload authorization. No organizer receipt or ')
    parts.append('live leaderboard score has been verified from this sandbox.</p>')
    parts.append('</section>')
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
    return ('<tr><th><a href="' + name + '.html">' + name + '</a></th>'
            '<td><a href="' + esc(source) + '"><code>' +
            esc(Path(r['file']).name) + '</code></a>'
            '<br>Historical bytes for research only</td>'
            '<td>Not estimable</td>'
            '<td>' + report +
            '<br><small>USER-REPORTED; no organizer receipt</small></td>'
            '<td>No — ' + esc(overlap_txt) + '</td>'
            '<td><strong>NO</strong></td></tr>')


def site_page(name, r, actual, overlap, links, refresh):
    source = ("https://github.com/buffedlizard55-lab/" + name + "/blob/" +
              r['github_ref'] + "/" + r['file'])
    report = esc(r['published_score_OWNER_REPORT'])
    if isinstance(overlap, (int, float)):
        overlap_txt = (format(overlap * 100, '.1f') +
                       '% vs registry lattice — FAIL (>70% limit)')
    else:
        overlap_txt = "not measured — FAIL"
    best = ('Highest reported of the nine' if name == 'GEMSDOE32'
            else 'Historical best for this site')
    parts = []
    parts.append('<p class="eyebrow">NINE-SITE REVIEW / ' + name + '</p>')
    parts.append('<h1>' + name + ' executive summary</h1>')
    parts.append('<section class="status fail-closed">')
    parts.append('<h2>DO NOT RESUBMIT THIS HISTORICAL FILE</h2>')
    parts.append('<p><strong>Best submission identified for ' + name + ':</strong> ')
    parts.append('<code>' + esc(Path(r['file']).name) + '</code> — ')
    parts.append('USER-REPORTED historical result <strong>' + report +
                 '</strong> (not ORGANIZER-CONFIRMED; no file-bound organizer receipt ')
    parts.append('in this repository). Estimated score for a new candidate: <strong>unavailable</strong>.</p>')
    parts.append('<p><strong>Unique under the protocol?</strong> <strong>No.</strong> ')
    parts.append('Directed 3-pixel overlap against the registry lattice is ' + esc(overlap_txt) + '. ')
    parts.append('It is a near-duplicate of lattice-covered faults; re-uploading it fails the uniqueness ')
    parts.append('gate and is not a distinct scientific strategy.</p>')
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
    parts.append('<li>Byte-unique among nine: yes (different bytes; still not spatially unique)</li>')
    parts.append('</ul>')
    parts.append('<p><code>' + actual['sha256'] + '</code></p>')
    parts.append(status_box())
    parts.append('<h2>Source freshness</h2>')
    parts.append('<p><a href="' + esc(links[name]['source']) +
                 '">Latest pinned repository README</a>, retrieved ' +
                 esc(refresh['retrieved_utc']) +
                 '. Repository statements are not organizer receipts.</p>')
    parts.append('<p><a href="../evidence/fleet_uniqueness_593.json">Full-fleet uniqueness audit</a> · ')
    parts.append('<a href="../evidence/review_2026-10-28.json">Current review (fail closed)</a> · ')
    parts.append('<a href="executive-summary.html">All nine sites</a></p>')
    return ''.join(parts)


def build_home_body(table):
    parts = []
    parts.append('<p class="eyebrow">RESEARCH OPERATIONS / 28 OCT 2026</p>')
    parts.append('<h1>Evidence before<br>a leaderboard slot.</h1>')
    parts.append('<section class="status fail-closed">')
    parts.append('<h2>One unique artifact · not cleared to submit</h2>')
    parts.append('<p>Locally built unique file: <a href="downloads/' + UNIQUE_TIF +
                 '" download><strong>' + UNIQUE_TIF + '</strong></a> '
                 '(SHA-256 <code>' + esc(UNIQUE_SHA[:16]) + '</code>…, 38,200 dots, '
                 '<a href="downloads/' + UNIQUE_ZIP + '" download>.zip</a>). '
                 'It is byte-unique versus the discrete peer fleet, but it FAILS the strict Rule-1 lattice '
                 'uniqueness gate: a registry uniform-lattice raster overlaps ' +
                 format(LATTICE_OVERLAP * 100, '.3f') + '% of its dots within 3 px (limit 70%). '
                 'Verdict: <strong>NOT OK to submit</strong> — logged as a duplicate/drift, stopped.</p>')
    parts.append('</section>')
    parts.append('<div class="cards">')
    parts.append('<section><span>01 / Finding</span><h2>No defensible score forecast</h2>'
                 '<p>Historic scores lack organizer receipts. Holdout and leaderboard results must not be equated.</p></section>')
    parts.append('<section><span>02 / Audit finding</span><h2>Lattice uniqueness gate fails</h2>'
                 '<p>A registry uniform-lattice raster overlaps 99.932% of the unique artifact\'s dots within 3 px, '
                 'above the 70% limit. All nine historical best files also fail the uniqueness gate.</p></section>')
    parts.append('<section><span>03 / Next action</span><h2>Do not spend a weekly slot</h2>'
                 '<p>No candidate in this checkout passes the strict uniqueness gate. Do not submit any historical '
                 'file or the retained artifact until a fresh method clears lattice, canary, holdout and saved-byte '
                 'gates on authenticated data. Earlier synthetic drafts (H-UNQ-1, CDA1) stay quarantined.</p></section>')
    parts.append('</div>')
    parts.append('<h2>Nine-site executive decision table</h2>')
    parts.append('<p>Each site links to a dedicated summary. Files below are historical evidence, '
                 '<strong>not recommended uploads</strong>. Estimates are unavailable; reported values are not verified scores.</p>')
    parts.append(table)
    parts.append('<h2>Why the reported 0.2778 led this family</h2>')
    parts.append('<p>The upstream explanation is thinning redundant predictions and pruning near known faults. '
                 'That is a plausible mechanism, not a causal proof or a forecast. Reproducing its dots is not '
                 'a distinct scientific strategy.</p>')
    parts.append('<p><a href="research.html">Read baseline review</a> · '
                 '<a href="submission-guide.html">Submission guide →</a></p>')
    parts.append('<h2>Evidence & limitations</h2>')
    parts.append('<ul>')
    parts.append('<li><a href="../evidence/review_2026-10-28.json">Current review (fail closed)</a></li>')
    parts.append('<li><a href="../evidence/fleet_uniqueness_593.json">Full-fleet uniqueness audit</a></li>')
    parts.append('<li><a href="../evidence/historical_byte_audit.json">Historical byte & geometry audit</a></li>')
    parts.append('<li><a href="../evidence/source_refresh.json">Nine pinned current README snapshots</a></li>')
    parts.append('<li>Only this repository was changed. Other owners’ sites were reviewed, not modified.</li>')
    parts.append('</ul>')
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

    write('index.html', 'GEMS — executive decision', build_home_body(table))
    write('legacy-executive-summary.html', 'GEMS — nine-site executive summary', build_home_body(table))
    research = (DOCS / 'research.md').read_text()
    write('legacy-research.html', 'Scientific review & sources',
          '<h1>Scientific review & research slate</h1>'
          '<p><a href="research.md">Download Markdown with source URLs</a></p>'
          '<pre class="research">' + esc(research) + '</pre>')

    # ---- Submission guide (also published at repo root executive-summary.html) ----
    # Honest fail-closed guidance consistent with docs/executive-summary.html.
    guide_parts = []
    guide_parts.append('<div class="eyebrow">SUBMISSION GUIDE</div>')
    guide_parts.append('<h1>No file is cleared to submit.<br>Fail closed.</h1>')
    guide_parts.append('<section class="status fail-closed">')
    guide_parts.append('<span class="status-badge">NOT CLEARED TO SUBMIT · FAIL CLOSED</span>')
    guide_parts.append('<h2>' + UNIQUE_NAME + ' (unique artifact, not cleared)</h2>')
    guide_parts.append('<p>The locally built unique artifact is available for download and review, but it is ')
    guide_parts.append('NOT cleared to submit: it fails the strict Rule-1 lattice uniqueness gate (' +
                       format(LATTICE_OVERLAP * 100, '.3f') + '% of dots within 3 px of a registry '
                       'uniform-lattice raster; limit 70%). Do not spend a weekly slot on it.</p>')
    guide_parts.append('<p><a class="button" href="docs/downloads/' + UNIQUE_TIF +
                       '" download>↓ Download ' + UNIQUE_TIF + '</a> ')
    guide_parts.append('· SHA-256 <code>' + esc(UNIQUE_SHA) + '</code>')
    guide_parts.append(' · note (' + str(UNIQUE_NOTE_LEN) + '/140 chars): ')
    guide_parts.append('<code>' + esc(UNIQUE_NOTE) + '</code></p>')
    guide_parts.append('<p class="muted">Status: NOT OK to submit. This page is not upload authorization. ')
    guide_parts.append('Do not submit any of the nine historical files; all fail the uniqueness gate.</p>')
    guide_parts.append('</section>')
    guide_parts.append('<section><h2>Why the retained artifact cannot be submitted</h2><ul>')
    guide_parts.append('<li><strong>Lattice uniqueness gate fails.</strong> A registry uniform-lattice raster '
                       'overlaps ' + format(LATTICE_OVERLAP * 100, '.3f') + '% of the artifact\'s dots within ')
    guide_parts.append('3 px, above the 70% protocol limit (Parallel-Run Protocol Rule 1).</li>')
    guide_parts.append('<li><strong>No organizer confirmation.</strong> No DrivenData auth is available from ')
    guide_parts.append('this sandbox, so no live leaderboard score or ORGANIZER-CONFIRMED receipt exists.</li>')
    guide_parts.append('<li><strong>No held-out improvement verified.</strong> No fresh same-evaluator holdout ')
    guide_parts.append('run beats the current best on authenticated data.</li>')
    guide_parts.append('</ul></section>')
    guide_parts.append('<section><h2>The required sequence (when a candidate clears all gates)</h2><ol>')
    guide_parts.append('<li><strong>Clear every gate first.</strong> Lattice uniqueness ≤70%, rank correlation ')
    guide_parts.append('≤0.90, single-feature leakage canary ≤0.90, same-evaluator holdout improvement with 95% CI, ')
    guide_parts.append('and exact saved-byte format validation (float32 [0,1], matching CRS/shape/transform).</li>')
    guide_parts.append('<li><strong>Download the cleared TIFF.</strong> Recheck downloaded bytes against the SHA-256.</li>')
    guide_parts.append('<li><strong>Open DrivenData.</strong> Sign in to the ')
    guide_parts.append('<a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">GEMS competition</a>, ')
    guide_parts.append('choose Submit → Make new submission, and verify your actual weekly allowance there.</li>')
    guide_parts.append('<li><strong>Upload & record.</strong> Use the unique name and a note of at most 140 ')
    guide_parts.append('characters; retain the organizer receipt. Do not claim a score until received.</li>')
    guide_parts.append('</ol></section>')
    guide_parts.append('<section><h2>About “Predicted values must be in range [0,1]”</h2>')
    guide_parts.append('<p>That rejection means saved TIFF values fall outside [0,1] (negative nodata sentinels, ')
    guide_parts.append('infinity, NaN, or genuine out-of-range predictions). Diagnose it by reopening the exact ')
    guide_parts.append('saved file — e.g. <a href="scripts/validate_geotiff.py">scripts/validate_geotiff.py</a> — ')
    guide_parts.append('not by inspecting an in-memory array. The retained artifact was verified finite [0,1] with ')
    guide_parts.append('no NaN/Inf, but format validity never proves scientific novelty or submit-ability.</p>')
    guide_parts.append('</section>')
    guide_parts.append('<section><h2>Access limitations</h2><p>')
    guide_parts.append('Direct data hosts such as Dropbox and login-walled DrivenData pages are outside this ')
    guide_parts.append('sandbox network allowlist; competition data is restored from pinned GitHub blobs via ')
    guide_parts.append('<code>scripts/restore_data.py</code>. No organizer receipt or live leaderboard score has ')
    guide_parts.append('been verified here. GitHub mirrors do not authenticate organizer provenance.</p>')
    guide_parts.append('</section>')
    (ROOT / 'executive-summary.html').write_text(shell('Submission guide', ''.join(guide_parts)))


if __name__ == '__main__':
    main()
