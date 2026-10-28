"""Build static GitHub Pages summaries from committed evidence; never invent a score."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'docs'

def esc(text):
    return html.escape(str(text), quote=True)

def shell(title, body):
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><link rel="stylesheet" href="style.css"><header><a href="index.html">GEMS / KARAGE 1</a><nav><a href="executive-summary.html">Executive summary</a><a href="research.html">Research & sources</a><a href="submission-guide.html">Submission guide</a></nav></header><main>'+body+'</main><footer>Evidence-first research · No portal uploads · Maximize P(Win) / Own the Outcome</footer></html>'

def write(name,title,body):
    (DOCS/name).write_text(shell(title,body))

def main():
    DOCS.mkdir(exist_ok=True)
    original=json.loads((ROOT/'evidence/upstream_nine_site_audit.json').read_text())
    audit=json.loads((ROOT/'evidence/historical_byte_audit.json').read_text())
    refresh=json.loads((ROOT/'evidence/source_refresh.json').read_text())
    links={r['site']:r for r in refresh['sites']}
    rows=[]
    for r in original['sites']:
        name=r['site']
        actual=next(a for a in audit['files'] if a['site']==name)
        twins=[a['site'] for a in audit['files'] if a['site']!=name and a['sha256']==actual['sha256']]
        source=f"https://github.com/buffedlizard55-lab/{name}/blob/{r['github_ref']}/{r['file']}"
        report=esc(r['published_score_OWNER_REPORT'])
        rows.append(f'<tr><th><a href="{name}.html">{name}</a></th><td><a href="{source}"><code>{esc(Path(r["file"]).name)}</code></a><br>Historical bytes for review only</td><td>Not estimable</td><td>{report}<br><small>USER-REPORTED; no organizer receipt</small></td><td>No — literal overlap gate fails</td><td><strong>NO</strong></td></tr>')
        body=f'<p class="eyebrow">NINE-SITE REVIEW / {name}</p><h1>{name} executive summary</h1><section class="alert"><h2>DO NOT SUBMIT</h2><p>No new approved submission exists in this repository. Historical best does not mean unique or presently authorized.</p></section><h2>Historical benchmark</h2><p><a href="{source}"><code>{esc(Path(r["file"]).name)}</code></a></p><p>USER-REPORTED historical result: <strong>{report}</strong>. Not ORGANIZER-CONFIRMED. Estimated score for a new candidate: <strong>unavailable</strong>.</p><h2>Automated byte audit</h2><ul><li>SHA-256 matches pinned upstream manifest: yes</li><li>Template CRS / shape / transform match: {actual["geometry_matches"]}</li><li>Finite [0,1] inside footprint: {actual["finite_range_pass"]}</li><li>All cells finite, including outside footprint: {actual["all_cells_finite"]}</li><li>Exact file-byte twins among nine: {esc(", ".join(twins) or "none; this does not prove spatial uniqueness")}</li><li>Directed 3-pixel overlap against registry lattice: {audit["lattice"]["historical_directed_overlaps"][name]:.4%} — FAIL</li></ul><p><code>{actual["sha256"]}</code></p><h2>Source freshness</h2><p><a href="{esc(links[name]["source"])}">Latest pinned repository README</a>, retrieved {esc(refresh["retrieved_utc"])}. Repository statements are not organizer receipts.</p><p><a href="../evidence/historical_byte_audit.json">Independent measured audit</a> · <a href="executive-summary.html">All sites</a></p>'
        write(name+'.html',name+' executive summary',body)
    table='<div class="table-scroll"><table><thead><tr><th>Site</th><th>Historical file / review link</th><th>Estimated score</th><th>Historical report</th><th>Unique under protocol?</th><th>Submit?</th></tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>'
    body='<p class="eyebrow">REVIEWED 28 OCT 2026</p><h1>Evidence before<br>a leaderboard slot.</h1><section class="alert"><h2>DO NOT SUBMIT — no candidate cleared</h2><p>The previous H-K1-1 file has 38,174 / 38,200 dots within 3 pixels of a registered lattice, exceeding the literal 70% limit. <a href="hmas-sinter/index.html">Review the research-only file and evidence</a>. A passing [0,1] format check does not approve a submission.</p></section><div class="cards"><section><span>01 / Decision</span><h2>No defensible score forecast</h2><p>Historical claims lack artifact-linked organizer receipts. Holdout and leaderboard values are not interchangeable.</p></section><section><span>02 / Audit finding</span><h2>Literal overlap failure</h2><p>Both earlier local candidates fail the registered lattice witness. Their earlier nonliteral clearance is superseded.</p></section><section><span>03 / Next action</span><h2>Restore the shared process</h2><p>A lane and whole-component buffered rerun are needed; do not rename a historical file.</p></section></div><h2>Nine-site executive decision table</h2><p>Historical files are research references, not recommended uploads. Estimates are unavailable.</p>'+table+'<h2>Why did the reported H33-B2 result lead?</h2><p>Thinning can reduce redundant false-positive mass while preserving some coverage; hidden labels are unavailable, so this is a hypothesis, not an established cause.</p><p><a href="executive-summary.html">Current executive summary</a> · <a href="research.html">Research</a> · <a href="submission-guide.html">Future submission instructions</a></p><h2>Evidence</h2><ul><li><a href="../evidence/release_reassessment_20261028.json">Independent literal-overlap reassessment</a></li><li><a href="data/run-card.json">Current negative run card</a></li><li><a href="../evidence/historical_byte_audit.json">Historical byte and spatial audit</a></li><li>Only this repository is changed; the nine peer sites are linked for review.</li></ul>'
    write('index.html','GEMS — executive decision',body)
    write('legacy-executive-summary.html','GEMS — nine-site executive summary',body)
    write('nine-sites.html','GEMS — nine-site executive summary',body)

    # Preserve readable research as plain text without a third-party runtime dependency.
    research=(DOCS/'research.md').read_text()
    write('legacy-research.html','Scientific review & sources','<h1>Scientific review & research slate</h1><p><a href="research.md">Download Markdown with source URLs</a></p><pre class="research">'+esc(research)+'</pre>')
    write('submission-guide.html','Competition submission guide','<h1>How to submit — only after every gate passes</h1><section class="alert"><h2>Nothing is approved for upload today.</h2><p>There is no authorized download button. This guide is for a future selected artifact, not permission to upload a historical TIFF.</p></section><ol><li>Read the executive decision. Scientific promotion requires complete holdout, canary, uniqueness, provenance, and saved-byte checks. A separate selector must confirm an available weekly slot using the authenticated submission screen.</li><li>Download only the exact approved single-band GeoTIFF (or ZIP containing only that TIFF), with its unique name, SHA-256 and note. Do not rename an old raster to imply uniqueness.</li><li>The saved-byte validator must confirm float32, finite values in [0,1] inside the footprint, and exact template CRS, shape and transform. Report strict whole-array and null/NaN-outside diagnostics separately; confirm organizer-compatible outside encoding before submission.</li><li>Open <a href="https://www.drivendata.org/competitions/306/competition-doe-gems/">the official competition</a>, review its current rules and submission cap, then choose New submission.</li><li>Choose File to submit, select the authorized TIFF or ZIP, and paste the recorded note (at most 140 characters). This repository does not automate portal uploads.</li><li>Save the organizer’s submission-page receipt and the artifact SHA-256. Only then label the result ORGANIZER-CONFIRMED. A HOLDOUT-DTI measurement is not a leaderboard score.</li></ol><h2>Range error prevention</h2><p>“Predicted values must be in range [0, 1]” requires checking saved TIFF values, not merely an in-memory array. A strict whole-array check rejects NaNs, but organizer text requests null/NaN outside bounds. Neither encoding has been portal-tested here; obtain organizer clarification and an authenticated template. A passing format check alone never proves high performance or uniqueness.</p>')

if __name__=='__main__':
    main()
