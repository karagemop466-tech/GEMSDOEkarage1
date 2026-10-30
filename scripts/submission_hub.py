#!/usr/bin/env python3
"""Submission hub: the one-page executive summary and download decision (2026-10-29).

Every number on the hub is read from an evidence file written by a script in this repo:
  evidence/tiltgrav_exp1_canary_20261029.json   EXP-1 leakage canary (per feature, AUC)
  evidence/tiltgrav_exp2_holdout_20261029.json  EXP-2 holdout (candidate vs controls)
  evidence/tiltgrav_exp3_spacing_20261029.json  EXP-3 spacing-matched sweep (last budgeted experiment)
  evidence/tiltgrav_final_20261029.json         final file receipt + registry overlap audit
  evidence/site_overlap_matrix_20261029.json    measured overlap among the nine focus files, lattice, candidate
Labels: USER-REPORTED (scores supplied in the user's brief; no organizer receipt),
HOLDOUT-DTI (shared evaluator, withheld positives, 95% CI), REGISTRY-MEASUREMENT (overlap).
Nothing here is an organizer score or a leaderboard estimate.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVID = ROOT / "evidence"
DATA_OUT = ROOT / "docs" / "data" / "submission-hub.json"
NAME = "karage1-tiltgrav-ridge-sp6-37654-20261029"
TIF_NAME = f"{NAME}.tif"
DRIVEN = "https://www.drivendata.org/competitions/306/competition-doe-gems/"
PAGE = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"
RULES = "https://docs.nlr.gov/docs/fy26osti/96647.pdf"
LEADER = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
# Exact site URLs as supplied in the brief (not reconstructed).
SITE_PAGES = {
    "GEMSDOE24": "https://buffedlizard55-lab.github.io/GEMSDOE24/",
    "GEMSDOE25": "https://buffedlizard55-lab.github.io/GEMSDOE25/",
    "GEMSDOE27": "https://buffedlizard55-lab.github.io/GEMSDOE27/",
    "GEMSDOE28": "https://buffedlizard55-lab.github.io/GEMSDOE28/",
    "GEMSDOE30": "https://buffedlizard55-lab.github.io/GEMSDOE30/",
    "GEMSDOE31": "https://buffedlizard55-lab.github.io/GEMSDOE31/docs/",
    "GEMSDOE32": "https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html",
    "GEMSDOE33": "https://buffedlizard55-lab.github.io/GEMSDOE33/",
    "GEMSDOE36": "https://buffedlizard55-lab.github.io/GEMSDOE36/docs/",
}
LATTICE_GATE = 0.70
RHO_GATE = 0.90


def esc(v, quote=True):
    return html.escape(str(v), quote=quote)


def _load(name):
    return json.loads((EVID / name).read_text(encoding="utf-8"))


def _load_optional(name):
    """Shared-validator receipt for the candidate (evidence/audit_*.json); None if absent."""
    path = EVID / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def facts() -> dict:
    """Assemble all displayed facts from the evidence files (no hand-typed numbers)."""
    canary = _load("tiltgrav_exp1_canary_20261029.json")["exp1_canary"]
    hold = _load("tiltgrav_exp2_holdout_20261029.json")["exp2_holdout"]
    spac = _load("tiltgrav_exp3_spacing_20261029.json")["exp3_spacing_sweep"]
    final = _load("tiltgrav_final_20261029.json")
    mat = _load("site_overlap_matrix_20261029.json")
    rec = final["final_receipt"]
    val = rec["validator"]
    audit = final["registry_audit"]
    lattice_row = next(r for r in audit if r["registry_file"].startswith("13GEMSDOE"))
    focus_rows = [r for r in audit if not r["registry_file"].startswith("13GEMSDOE")]
    max_canary = max(canary.items(), key=lambda kv: kv[1]["auc_mean_over_folds"])
    cand_c = spac["scores"]["candidate_spaced"]
    rand_c = spac["scores"]["random_spaced_null"]
    delta_c = spac["paired_differences"]["random_spaced_null"]
    return dict(
        canary=dict(n_features=len(canary) - 1, max_feature=max_canary[0],
                    max_auc=max_canary[1]["auc_mean_over_folds"], alarm_gate=0.90,
                    any_alarm=any(v["leakage_alarm"] for v in canary.values()),
                    candidate_score_auc=canary["CANDIDATE_SCORE"]["auc_mean_over_folds"]),
        holdout_unspaced={a: hold["scores"][a] for a in hold["scores"]},
        holdout_unspaced_delta_vs_random=hold["paired_differences"]["random_null"],
        spacing={"candidate_spaced": cand_c, "random_spaced_null": rand_c},
        spacing_delta=delta_c,
        spacing_px=spac["spacing_px"],
        withheld_total=spac["withheld_positive_pixels"] if "withheld_positive_pixels" in spac
        else spac["scores"]["candidate_spaced"]["withheld_positive_pixels"],
        evaluator=spac["evaluator_version"],
        bootstrap=spac["bootstrap"],
        file=dict(name=TIF_NAME, sha256=rec["sha256"], bytes=rec["bytes"], zip_sha256=rec["zip_sha256"],
                  dots=val["in_footprint_positive_pixels"] if "in_footprint_positive_pixels" in val
                  else val["in_footprint_positive"], outside_nan=val["outside_nan_cells"],
                  all_checks_passed=val["all_checks_passed"], checks=val["checks"],
                  name_text=rec["submission_name"], note_text=rec["submission_note"],
                  note_chars=rec["submission_note_chars"]),
        lattice=dict(file=lattice_row["registry_file"], fwd=lattice_row["my_dots_within_3px_of_theirs"],
                     rho=lattice_row["spearman_full_footprint"]),
        focus_max_fwd=max(r["my_dots_within_3px_of_theirs"] for r in focus_rows),
        focus_max_fwd_file=max(focus_rows, key=lambda r: r["my_dots_within_3px_of_theirs"])["registry_file"],
        focus_max_abs_rho=max(abs(r["spearman_full_footprint"]) for r in focus_rows),
        registry_checked=len(audit),
        matrix=mat,
        spearman=_load("site_spearman_matrix_20261029.json"),
    )


def site_rows(f: dict) -> list[dict]:
    """One row per focus site: best user-reported file, measured duplicate partners, verdict."""
    mat = f["matrix"]
    items = mat["items"]
    M = mat["matrix"]
    focus_idx = [i for i, it in enumerate(items) if it["label"].startswith("GEMSDOE")]
    lattice_idx = next(i for i, it in enumerate(items) if it["label"].startswith("13GEMSDOE"))
    cand_idx = next(i for i, it in enumerate(items) if it["label"].startswith("NEW"))
    pairs = f["spearman"]["pairs"]

    def rho_partners(label):
        out = []
        for pr in pairs:
            other = pr["b"] if pr["a"] == label else pr["a"] if pr["b"] == label else None
            if other and other.startswith("GEMSDOE") and abs(pr["spearman_full_footprint"]) > RHO_GATE:
                out.append(other)
        return out

    rows = []
    for i in focus_idx:
        it = items[i]
        dup_focus = [items[j]["label"] for j in focus_idx if j != i and M[i][j] > LATTICE_GATE]
        dup_rho = rho_partners(it["label"])
        lattice_fwd = M[i][lattice_idx]
        rows.append(dict(
            site=it["label"], file=it["file"], registry_path=it["path"], dots=it["dots"],
            sha256=it["sha256"], reported=it["reported"],
            page=SITE_PAGES[it["label"]],
            dup_focus=dup_focus, dup_rho=dup_rho, lattice_fwd=lattice_fwd,
            cand_fwd=M[cand_idx][i],
            unique=(not dup_focus and not dup_rho and lattice_fwd <= LATTICE_GATE),
        ))
    return rows


def _pct(x):
    return f"{100 * x:.2f}%"


def _dti(s):
    return f"{s['dti']:.4f} [{s['ci95'][0]:.4f}, {s['ci95'][1]:.4f}]"


def body(f: dict, depth: int) -> str:
    """HTML for the hub. depth=0 -> root index, depth=1 -> docs/*."""
    doc = "docs/" if depth == 0 else ""
    dl = f"{doc}downloads/{TIF_NAME}"
    rows = site_rows(f)
    sp = f["spacing"]
    fl = f["file"]
    ex_rows = []
    for r in rows:
        dup = (", ".join(esc(x) for x in r["dup_focus"]) if r["dup_focus"] else "none")
        dup_r = (", ".join(esc(x) for x in r["dup_rho"]) if r["dup_rho"] else "none")
        ex_rows.append(
            "<tr>"
            f"<td><strong>{esc(r['site'])}</strong><br><a href=\"{esc(r['page'], quote=True)}\">site page ↗</a></td>"
            f"<td><code class=\"wrap\">{esc(r['file'])}</code><br><small>{r['dots']:,} dots · registry copy "
            f"<code>{esc(r['registry_path'])}</code></small></td>"
            f"<td><strong>{r['reported']:.4f}</strong><br><small>USER-REPORTED · UNVERIFIED (no organizer receipt)</small></td>"
            f"<td>UNAVAILABLE<br><small>no validated leaderboard estimator</small></td>"
            f"<td>{'YES' if r['unique'] else 'NO'}<br><small>lattice {_pct(r['lattice_fwd'])} · "
            f"dot-overlap duplicates among focus files: {dup}<br>rank duplicates (rho &gt; 0.90): {dup_r}</small></td>"
            "<td><strong>NOT CLEARED: DO NOT SUBMIT</strong><br><small>a USER-REPORTED registry copy (leaderboard placement not verified); "
            "re-upload is a copy, and it fails the lattice gate</small></td>"
            "</tr>")
    _shared = _load_optional("audit_tiltgrav_ridge_sp6_20261029.json")
    shared_problems = "; ".join(esc(x) for x in _shared["format_report_problems"]) if _shared else "receipt missing"
    checks = "".join(
        f"<li><code>{esc(k)}</code>: {'PASS' if v else 'FAIL'}</li>" for k, v in fl["checks"].items())
    return f"""
<section class="hub-decision" id="download" aria-labelledby="hub-title">
  <p class="eyebrow">SUBMISSION DECISION · 29 OCT 2026</p>
  <h1 id="hub-title">Is anything OK to download and submit? <span class="tag-no">NO — NOT CLEARED: DO NOT SUBMIT</span></h1>
  <p><strong>No file on this site is cleared for DrivenData upload.</strong> The new GeoTIFF below is valid in
  format and passes the rank and dot-overlap checks against the nine focus files. It fails the literal 3-px lattice gate, and its holdout is negative. It must not be submitted.</p>
  <ul class="why">
    <li><strong>Holdout is negative.</strong> HOLDOUT-DTI {sp['candidate_spaced']['dti']:.4f}
    [{sp['candidate_spaced']['ci95'][0]:.4f}, {sp['candidate_spaced']['ci95'][1]:.4f}] versus a spacing-matched random
    null at {sp['random_spaced_null']['dti']:.4f} (paired Δ {f['spacing_delta']['delta']:+.4f},
    95% CI [{f['spacing_delta']['ci95'][0]:+.4f}, {f['spacing_delta']['ci95'][1]:+.4f}] — includes zero).</li>
    <li><strong>Lattice gate fails.</strong> {_pct(f['lattice']['fwd'])} of its dots lie within 3 px of the
    13GEMSDOE calibration lattice; the literal stop is &gt; {int(LATTICE_GATE*100)}%.</li>
    <li><strong>No organizer receipt.</strong> No submission-page score, organizer acceptance, or live slot
    allowance was verifiable from this sandbox (DrivenData login-walled).</li>
  </ul>
  <article class="audit-card download-card">
    <p class="eyebrow">NEW FILE · research only · NOT CLEARED: DO NOT SUBMIT</p>
    <h2><a class="download-link" href="{esc(dl, quote=True)}" download>Download {esc(TIF_NAME)}</a></h2>
    <p><small>Single-band float32 GeoTIFF · EPSG:32611 · 100 m · 3292×3730 · values 0–1 inside the footprint ·
    NaN outside the footprint (official text: null or NaN). SHA-256 <code class="wrap">{esc(fl['sha256'])}</code>.
    Name: <code>{esc(fl['name_text'])}</code> · Note ({fl['note_chars']} chars): <code>{esc(fl['note_text'])}</code></small></p>
    <p><span class="tag-no">DO NOT SUBMIT</span> Reason: negative holdout and lattice duplicate (see above).
    If the protocol owner rules the lattice gate out of scope, this file still has to clear the holdout test to be
    worth a slot — it does not.</p>
  </article>
</section>

<section class="hub-table" aria-labelledby="sites-title">
  <p class="eyebrow">EXECUTIVE SUMMARY · NINE FOCUS SITES</p>
  <h2 id="sites-title">Best file per site, its score, estimate, and uniqueness</h2>
  <p>Scores are <strong>USER-REPORTED / UNVERIFIED</strong> from the brief. None is ORGANIZER-CONFIRMED. The overlap
  columns are measured on the restored, SHA-pinned mirror rasters (REGISTRY-MEASUREMENT). Duplicate =
  &gt; {int(LATTICE_GATE*100)}% of a file's dots within 3 px of another file's dots (the project's literal gate).
  A file is only "unique" if it clears the gate against all focus files <em>and</em> the lattice.</p>
  <div class="table-scroll"><table>
    <thead><tr><th>Site</th><th>File to download</th><th>Score (user-reported)</th>
    <th>Estimated score</th><th>Unique vs the other GEMSDOE files?</th><th>OK to submit?</th></tr></thead>
    <tbody>{''.join(ex_rows)}</tbody></table></div>
  <p><small>Most focus files duplicate one another under the literal rule (for example, GEMSDOE24, 25, 27 and 30 each
  have forward overlap 1.0000 with the others in the measured matrix). Full matrix:
  <a href="{doc}../evidence/site_overlap_matrix_20261029.json">evidence/site_overlap_matrix_20261029.json</a>.</small></p>
</section>

<section class="hub-table" aria-labelledby="estimate-title">
  <p class="eyebrow">HOW WE ESTIMATE A SCORE</p>
  <h2 id="estimate-title">Estimates: what we can and cannot say</h2>
  <p>We have one shared evaluator (<code>gems57-pooled-hide-v2</code>, α=0.2, β=0.8, 300 m kernel) and a
  hide-and-recover holdout over the mapped faults. On that holdout, a uniform random placement at the same budget
  scores about 0.05, while the user-reported (unverified) values for the nine files sit at 0.22–0.28.
  <strong>The holdout is therefore not calibrated to the leaderboard and cannot produce a leaderboard estimate.</strong>
  Holdout values below are HOLDOUT-DTI only.</p>
  <p>Why GEMSDOE32 <code>h33-h33-2-b2</code> (user-reported 0.2778) scored highest among the listed sites, and whether a higher score is achievable: <a href="https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/main/knowledge/02_why_gemsdoe32_b2_scored_0.2778.md">explanation in the repository</a> (the link opens on main after the merge).</p>
  <table><thead><tr><th>Arm (same budget 37,654 dots/fold)</th><th>HOLDOUT-DTI [95% CI]</th><th>Notes</th></tr></thead><tbody>
  <tr><td>NEW candidate, spacing 6 px (file above)</td><td>{_dti(sp['candidate_spaced'])}</td><td>EXP-3, withheld positives {f['withheld_total']:,}</td></tr>
  <tr><td>Random null, spacing 6 px</td><td>{_dti(sp['random_spaced_null'])}</td><td>best comparable control</td></tr>
  <tr><td>NEW candidate, no spacing</td><td>{_dti(f['holdout_unspaced']['candidate'])}</td><td>EXP-2</td></tr>
  <tr><td>Random null, no spacing</td><td>{_dti(f['holdout_unspaced']['random_null'])}</td><td>EXP-2; candidate minus this is significantly negative</td></tr>
  <tr><td>Proximity shell (3–6 px from visible faults)</td><td>{_dti(f['holdout_unspaced']['proximity_shell'])}</td><td>EXP-2</td></tr>
  </tbody></table>
  <p><small>Leakage canary (EXP-1): {f['canary']['n_features']} feature layers tested alone; highest holdout AUC
  {f['canary']['max_auc']:.4f} ({esc(f['canary']['max_feature'])}); alarm threshold 0.90; alarms: {f['canary']['any_alarm']}.</small></p>
</section>

<section class="hub-table" id="how-to-submit" aria-labelledby="how-title">
  <p class="eyebrow">HOW TO SUBMIT (WHEN A FILE IS CLEARED)</p>
  <h2 id="how-title">Step-by-step for the upload form</h2>
  <ol class="steps">
    <li>Confirm the file's status on this page says <strong>CLEARED FOR UPLOAD</strong>. Right now every file says NOT CLEARED.</li>
    <li>Download the single <code>.tif</code> (or the one-TIFF <code>.zip</code>). Do not download from the
    registry copies; they are third-party copies, not this team's output.</li>
    <li>Check on your machine: one band, float32, EPSG:32611, shape 3730×3292, 100 m, identical transform to
    the sample, values in [0, 1] inside the footprint, NaN outside (public spec: "data outside the bounds is null or nan").</li>
    <li>Give it a unique name (≤ 140 characters) and a short note (≤ 140 characters) on the form, for example
    the name and note above.</li>
    <li>Use the official page for the rules: <a href="{PAGE}">submission format</a> and the
    <a href="{RULES}">official rules PDF</a>. Three submissions per week; one final submission is selected before the
    deadline. The data tab is login-walled from this sandbox, and no upload was attempted.</li>
  </ol>
  <details><summary>Local validator results for the file above (all checks)</summary>
  <ul class="checks">{checks}</ul></details>
  <p class="shared-check"><strong>Shared template validator: FAILS on this file.</strong> <code>scripts/audit_local_tif.py</code>
  (receipt <code>evidence/audit_tiltgrav_ridge_sp6_20261029.json</code>) reports <code>format_report_ok: false</code>:
  {shared_problems}. The shared policy requires zeros outside the footprint; the official spec allows null or NaN.
  This is the unresolved NaN-versus-zeros conflict and is one more reason the file is not cleared.</p>
</section>

<section class="hub-table" id="irregularities" aria-labelledby="irr-title">
  <p class="eyebrow">IRREGULARITIES FLAGGED FOR MANUAL REVIEW</p>
  <h2 id="irr-title">What does not match, and why it matters</h2>
  <ul class="why">
    <li>A 29 Oct partial read recorded #1 at 0.4544 but did not cover pages 2–3. The independent 30 Oct live re-read (<a href="../knowledge/session-review-arena-89955dc0.md">review ↗</a>) confirms the public leaderboard values (ORGANIZER-PUBLIC): #1 0.4544, 0.3195 at rank #48, and 0.4413 not in the top 50. These do not verify any of the nine user-reported GEMSDOE scores.</li>
    <li>The organizer's sample description says the sample "predicts total fault absence" (<a href="{PAGE}">problem page</a>).
    The mirrored <code>sample_submission.tif</code> has 60,988 positive cells, exactly equal to the label raster. The mirror does not match the description.</li>
    <li>The mirrored <code>labels.tif</code> and <code>existing_faults.tif</code> are byte-identical (same SHA-256).</li>
    <li>The problem page lists a "top-of-crustal magnetic source depth estimate" layer; none of the 19 bands in the mirrored
    <code>training_features.tif</code> carries that name.</li>
    <li>Two holdout evaluators exist: the protocol's shared <code>gems57-pooled-hide-v2</code> and an older
    <code>gemsk-hide-recover-v1</code> used by earlier experiments. Their numbers are not comparable.</li>
    <li>The vendored shared writer and validator write zeros outside the footprint and reject NaN. The official page and
    the organizer sample use null or NaN outside. This session used a separate NaN-outside adapter and did not edit the pinned shared template.</li>
    <li>The 13GEMSDOE lattice overlap gate blocks every dotted file (measured {_pct(f['lattice']['fwd'])} for the new file; all
    {f['registry_checked']} restored registry rasters with dots were measured in the registry audit). The literal gate has no
    passing dotted candidate, which the protocol owner must decide.</li>
    <li>Another team's TIF on <code>main</code>, <code>karage1-convect-cell-upflow-20261029-zeros.tif</code>, is not covered by the fleet audit that <code>main</code> ships with. The shared validator (receipt <code>evidence/audit_convect_cell_upflow_20261029.json</code>) reports 65 emitted pixels outside the footprint and dots on the mapped catalogue. It was appended to the fleet audit with <code>ok_to_submit: false</code>. Flagged for review; not modified here.</li>
    <li>Also on <code>main</code> (PR #81): <code>gems-karage1-unique-novelterritory-20261029T120000Z-5a6b7c8d-zeros.tif</code> has 46 dots on the mapped catalogue (its own check <code>zero_dots_on_mapped_catalogue</code> fails), and 0.0 lattice overlap. Its saved-byte receipt is <code>evidence/audit_novelterritory_20261029.json</code>. It is not a fleet row, because a non-lattice file would break the fleet test's lattice invariant. Flagged; not modified here.</li>
    <li>The method lane paragraph the parallel-run protocol refers to is absent from the brief; the registry records
    <code>method_lane: null</code>.</li>
  </ul>
</section>

<section class="hub-table" id="decision-needed" aria-labelledby="decision-title">
  <p class="eyebrow">DECISION NEEDED FROM THE PROTOCOL OWNER</p>
  <h2 id="decision-title">Which gate applies to the lattice?</h2>
  <p>(a) Keep the literal rule: no dotted file can be cleared, and the team stops uploading dotted candidates.
  (b) Treat the 13GEMSDOE lattice as a calibration probe, as <code>registry/registry_roles.json</code> already
  describes it, and apply the 70% gate only to team registry entries. (c) Something else. Until this is decided,
  no file on this site is OK to submit.</p>
</section>
"""


def summary_strip(depth: int) -> str:
    """Short decision strip for the top of the home page (links to the hub)."""
    doc = "docs/" if depth == 0 else ""
    return (f'<section class="hub-strip" aria-label="Submission decision"><p class="eyebrow">DECISION · 29 OCT 2026</p>'
            f'<p><strong>NOT CLEARED: DO NOT SUBMIT — no file is cleared.</strong></p>'
            f'<p>New research file (format-valid, not cleared; research only): <a href="{doc}downloads/{TIF_NAME}">'
            f'<code>{TIF_NAME}</code></a> · status <strong>NOT CLEARED: DO NOT SUBMIT</strong> · '
            f'<a href="{doc}submission-hub.html">executive summary and how to submit ↗</a></p></section>')


def write_data(f: dict) -> None:
    """Machine-readable copy of the hub (every value traceable to evidence/*.json)."""
    rows = site_rows(f)
    payload = dict(
        schema="karage1-submission-hub-v1", date="2026-10-29",
        decision="NOT CLEARED: DO NOT SUBMIT - no file is cleared",
        new_file=dict(name=TIF_NAME, sha256=f["file"]["sha256"], dots=f["file"]["dots"],
                      validator_all_checks_passed=f["file"]["all_checks_passed"],
                      holdout_spaced=f["spacing"]["candidate_spaced"],
                      random_null_spaced=f["spacing"]["random_spaced_null"],
                      spacing_delta=f["spacing_delta"],
                      lattice_forward_overlap=f["lattice"]["fwd"],
                      max_focus_forward_overlap=f["focus_max_fwd"],
                      max_focus_abs_spearman=f["focus_max_abs_rho"]),
        sites=rows,
        labels=dict(USER_REPORTED="USER-REPORTED / UNVERIFIED", HOLDOUT_DTI="HOLDOUT-DTI",
                    REGISTRY_MEASUREMENT="REGISTRY-MEASUREMENT"),
        limits=dict(lattice_gate=LATTICE_GATE, rho_gate=RHO_GATE),
    )
    DATA_OUT.parent.mkdir(parents=True, exist_ok=True)
    DATA_OUT.write_text(json.dumps(payload, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def build_facts() -> dict:
    f = facts()
    write_data(f)
    return f
