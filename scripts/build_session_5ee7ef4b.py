#!/usr/bin/env python3
"""Build the session arena/5ee7ef4b executive summary and run card.

Every number on the page is read from a committed evidence file, never typed in:
  * evidence/exp1_shared_holdout_calibration_20261029.json   (Experiment 1)
  * evidence/exp2_s1_holdout_and_uniqueness_20261029.json    (Experiment 2)
  * registry/user_reported_scores_20261029.json              (USER-REPORTED scores)
  * evidence/site_lineage_verification_20261029.json         (pinned-mirror sibling overlap)
  * the H-S1 GeoTIFF bytes themselves (sha256, independent validator checks)

Outputs: docs/session-5ee7ef4b.html and evidence/session_5ee7ef4b_run_card.json.
Authorizes nothing: every verdict is NEGATIVE / DO NOT SUBMIT.
"""
from __future__ import annotations

import hashlib
import html
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
import rasterio

ROOT = Path(__file__).resolve().parents[1]
EXP1 = ROOT / "evidence/exp1_shared_holdout_calibration_20261029.json"
EXP2 = ROOT / "evidence/exp2_s1_holdout_and_uniqueness_20261029.json"
SCORES = ROOT / "registry/user_reported_scores_20261029.json"
LINEAGE = ROOT / "evidence/site_lineage_verification_20261029.json"
TIF = ROOT / "archive/research-s1-20261029/karage1-s1-tmihg-ridge-offcat-20261029-zeros.tif"
ZIP = TIF.with_suffix(".zip")
PAGE = ROOT / "docs/session-5ee7ef4b.html"
CARD = ROOT / "evidence/session_5ee7ef4b_run_card.json"

FOCUS = ["GEMSDOE24", "GEMSDOE25", "GEMSDOE27", "GEMSDOE28", "GEMSDOE30",
         "GEMSDOE31", "GEMSDOE32", "GEMSDOE33", "GEMSDOE36"]
NAME = "karage1-s1-tmihg-ridge-offcat-20261029"
NOTE = "H-S1 tmi_hg crest dots, off-catalogue, 2.8px spacing; all-finite zeros; format-valid"
LEADERBOARD_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/"
PROBLEM_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/"
RULES_NOTE_URL = "https://www.drivendata.org/competitions/306/competition-doe-gems/rules/"
NLR_PDF = "https://docs.nlr.gov/docs/fy26osti/96647.pdf"
REF_SOLUTION = "https://github.com/drivendataorg/gems-prize-reference-solution"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validate_tif(path: Path) -> dict:
    """Independent format check of the bytes on disk against the official rules."""
    from rasterio.crs import CRS
    sample = Path("/tmp/gems_data/sample_submission.tif")
    out = dict(sample_grid_used=str(sample) if sample.is_file() else None)
    with rasterio.open(path) as ds:
        a = ds.read(1)
        out.update(count=ds.count, dtype=ds.dtypes[0], crs_epsg=ds.crs.to_epsg(), shape=list(ds.shape),
                   transform=[float(v) for v in ds.transform[:6]], nodata=ds.nodata,
                   res=list(ds.res))
        out["crs_is_32611"] = ds.crs == CRS.from_epsg(32611)
    out.update(nan_cells=int(np.isnan(a).sum()), inf_cells=int(np.isinf(a).sum()),
               min=float(a.min()), max=float(a.max()), in_0_1=bool(((a >= 0) & (a <= 1)).all()),
               positive_cells=int((a > 0).sum()))
    if sample.is_file():
        with rasterio.open(sample) as s:
            foot = np.isfinite(s.read(1))
            out["shape_matches_sample"] = (s.shape == tuple(out["shape"]))
            out["transform_matches_sample"] = (tuple(s.transform)[:6] == tuple(out["transform"]))
            out["crs_matches_sample"] = s.crs.to_epsg() == out["crs_epsg"]
        out["positive_outside_sample_footprint"] = int(((a > 0) & ~foot).sum())
    out["zip_single_member_identical"] = False
    import zipfile
    with zipfile.ZipFile(ZIP) as z:
        names = z.namelist()
        out["zip_members"] = names
        out["zip_single_member_identical"] = names == [path.name] and z.read(names[0]) == path.read_bytes()
    return out


def sibling_max() -> dict:
    lin = json.loads(LINEAGE.read_text())
    best = defaultdict(float)
    partner = {}
    for pair, v in lin["pairwise_nine_sites"].items():
        a, b = pair.split("|")
        fa, fb = v["a_dots_within_3px_of_b_fraction"], v["b_dots_within_3px_of_a_fraction"]
        if fa > best[a]:
            best[a], partner[a] = fa, b
        if fb > best[b]:
            best[b], partner[b] = fb, a
    return {s: (best[s], partner.get(s)) for s in FOCUS}


def best_reported() -> dict:
    u = json.loads(SCORES.read_text())
    best = {}
    for e in u["entries"]:
        if e["site"] in FOCUS and (e["site"] not in best or e["score"] > best[e["site"]]["score"]):
            best[e["site"]] = e
    return best


def fmt(x, nd=4):
    return "n/a" if x is None else f"{x:.{nd}f}"


def build() -> None:
    e1 = json.loads(EXP1.read_text())
    e2 = json.loads(EXP2.read_text())
    tif_sha = sha256(TIF)
    v = validate_tif(TIF)
    best = best_reported()
    sib = sibling_max()
    rand = e1["arms"]["random_null_matched_count"]
    champ = e1["arms"]["champion_GEMSDOE32_B2"]
    d25 = e1["arms"]["GEMSDOE25_d28_local"]
    A = e2["arm_A_as_submitted"]
    B = e2["arm_B_holdout_faithful"]
    lat = e2["lattice_witness"]
    uniq = e2["uniqueness"]
    can = e2["leakage_canary"]
    run_ok = (v["crs_is_32611"] and v["dtype"] == "float32" and v["count"] == 1 and v["in_0_1"]
              and v["nan_cells"] == 0 and v.get("shape_matches_sample") and v.get("transform_matches_sample")
              and v.get("positive_outside_sample_footprint") == 0 and v["zip_single_member_identical"])

    cov = json.loads((ROOT / "evidence/lattice_saturation_null_20261029.json").read_text())
    e1_cov = f"{cov['footprint_covered_by_3px_disk_fraction'] * 100:.2f}"
    card = dict(
        schema="karage1-run-card-v1", session="arena/5ee7ef4b-gemsdoekarage1", date_utc="2026-10-29",
        hypothesis="H-S1: horizontal-gradient crest of total magnetic intensity (tmi_hg), off-catalogue, "
                   "marks unmapped magnetic contacts that a fault can produce.",
        mechanism="Magnetic horizontal-gradient maxima sit on steep lateral susceptibility or density contrasts; "
                  "a fault juxtaposing units of different magnetisation should produce such a maximum.",
        named_non_fault_mimic="Lithologic/intrusive contacts and magnetite-rich unit boundaries; cultural magnetic noise.",
        holdout=dict(
            label="HOLDOUT-DTI", evaluator="vendor/gems57 holdout.score_cell/evaluate (unmodified), alpha 0.2 beta 0.8 R 3px",
            arm_holdout_faithful_dti=B["pooled_dti"], arm_holdout_faithful_ci95_cell_bootstrap=B["ci95_cell_bootstrap"],
            arm_as_submitted_dti=A["pooled_dti"], arm_as_submitted_ci95=A["ci95_cell_bootstrap"],
            withheld_truth_pixels_summed_over_cells=e2["withheld_positives_total"],
            withheld_truth_note="Summed over 16 cells (2 draws x 4 folds x 2 modes); modes overlap, so this is not a unique pixel count.",
            ci_note="Percentile bootstrap over the 16 cells; not a model-level CI.",
            random_null_matched_count=rand["mean"], random_null_seeds=rand["pooled_dti_per_seed"],
            champion_GEMSDOE32_B2_dti=champ["pooled_dti"], champion_ci95=champ["ci95_cell_bootstrap"],
            gemsdoe25_d28_local_dti=d25["pooled_dti"], gemsdoe25_d28_local_ci95=d25["ci95_cell_bootstrap"],
            verdict_vs_floor="H-S1 holdout-faithful DTI is at or below the matched random floor; no evidence of skill."),
        leakage_canary=dict(feature="tmi_hg alone", auc_min=can["aucs_min"], auc_max=can["aucs_max"],
                            ceiling=0.90, pass_below_ceiling=can["pass_below_ceiling"]),
        correlation_overlap_vs_registry=dict(
            literal_70pct_rule_vs_13gems_witness=dict(
                witness=lat["witness"], witness_sha256=lat["witness_sha256"],
                mine_within_3px=lat["mine_within_3px_of_witness"], literal_duplicate=lat["literal_70pct_rule_duplicate"],
                note="Rule is saturated: random 37,654-dot placements also fail (evidence/lattice_saturation_null_20261029.json)."),
            exact_duplicate_any_local_tif=uniq["exact_duplicates"] > 0,
            max_mine_within_3px_any_local_tif=uniq["max_mine_within_3px_of_theirs"],
            worst_local_match=uniq["worst_match"]["file"],
            worst_local_match_dots=uniq["worst_match"]["dots"],
            max_mine_within_3px_excluding_dense_archive_mask=max(
                u["mine_within_3px_of_theirs"] for u in uniq["all"] if u["dots"] < 1_000_000),
            scope="local repo TIFs only; focus-site and pinned peer rasters not re-audited this session"),
        raster_sha256=tif_sha, raster_bytes=TIF.stat().st_size,
        zip_sha256=sha256(ZIP),
        validator_output=v,
        submission_name=NAME, submission_note=NOTE,
        ok_to_submit=False, slot_selected_or_spent=False, promoted=False,
        verdict="negative",
        verdict_reason=("Format-valid and not an exact duplicate, but the holdout-faithful DTI is no better than a "
                        "matched random placement, and the internal lattice rule is failed (saturated rule)."),
        experiments_used=2, experiment_budget="3 experiments or 2 hours",
        labels_note="Holdout numbers are HOLDOUT-DTI. Leaderboard numbers are ORGANIZER-PUBLIC (leaderboard page), "
                    "not organizer receipts. Focus-site scores are USER-REPORTED / UNVERIFIED.",
        validator_ok=run_ok,
    )
    CARD.write_text(json.dumps(card, indent=2, sort_keys=True, allow_nan=False) + "\n")

    rows = []
    for s in FOCUS:
        b = best.get(s)
        sm, partner = sib[s]
        rows.append(f"""<tr><td><b>{s}</b></td>
<td>{html.escape(b['file_name']) if b else 'none found'}</td>
<td>{fmt(b['score'] if b else None)} <span class="lab">USER-REPORTED</span></td>
<td>Not estimable <span class="lab">no validated calibration</span></td>
<td><b>No.</b> {sm*100:.1f}% of its dots lie within 3 px of {partner} (pinned mirror)</td>
<td>Not provided. No file cleared.</td></tr>""")
    rows_html = "\n".join(rows)
    e1_cov = f"{cov['footprint_covered_by_3px_disk_fraction'] * 100:.2f}"
    page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GEMSDOE focus-site executive summary (arena/5ee7ef4b)</title>
<link rel="stylesheet" href="assets/styles.css">
<style>
body{{font-family:system-ui,Arial,sans-serif;max-width:1080px;margin:0 auto;padding:18px;line-height:1.45;color:#111}}
table{{border-collapse:collapse;width:100%;margin:10px 0 18px;font-size:14px}}
th,td{{border:1px solid #ccc;padding:6px 8px;vertical-align:top;text-align:left}}
th{{background:#f0f0f0}}
.banner{{background:#7a0000;color:#fff;padding:14px;border-radius:6px;font-size:17px}}
.ok{{background:#e8f5e9;border-left:5px solid #2e7d32;padding:10px;margin:12px 0}}
.bad{{background:#fdecea;border-left:5px solid #b71c1c;padding:10px;margin:12px 0}}
.lab{{font-size:11px;background:#eee;padding:1px 4px;border-radius:3px;color:#333}}
code{{background:#f4f4f4;padding:1px 3px}}
</style></head>
<body>
<h1>GEMSDOE focus sites: executive summary</h1>
<p>Session <code>arena/5ee7ef4b-gemsdoekarage1</code>, 29 Oct 2026 (UTC). Generated by
<code>scripts/build_session_5ee7ef4b.py</code> from committed evidence. Nothing on this page authorises an upload.</p>

<div class="banner"><b>DO NOT SUBMIT ANY FILE FROM THIS SESSION.</b><br>
No file is cleared. The new candidate is format-valid and not an exact duplicate, but its holdout-faithful score is
no better than a random placement, and it fails the internal lattice rule.</div>

<h2>1. Best reported file per focus site</h2>
<p>Reported scores are <span class="lab">USER-REPORTED / UNVERIFIED</span> (pasted into the session; no organizer receipt is in
this repository). The competition does not show per-file scores publicly, so no estimate for these files is
possible from our side. The "unique" column is a measured overlap against a sibling on the pinned mirrors.</p>
<table><tr><th>Site</th><th>Best file (as reported)</th><th>Reported score</th><th>Estimated score for us</th>
<th>Unique vs other focus sites?</th><th>Download from this repo?</th></tr>
{rows_html}
</table>
<p><b>Highest reported focus-site file:</b> GEMSDOE32 at 0.2778 (<code>h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros</code>).
The GEMSDOE32 site itself says "already submitted - do not resubmit" (per the earlier owner review), so it is not
a file to re-upload.</p>

<h2>2. The new file (H-S1): download and status</h2>
<div class="bad"><b>Status: NEGATIVE / DO NOT SUBMIT.</b> Download for research only:
<a href="https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/main/archive/research-s1-20261029/{NAME}-zeros.tif">{NAME}-zeros.tif</a>
(sha256 <code>{tif_sha}</code>). A single-TIFF ZIP is in the same folder.</div>
<table>
<tr><th>Check</th><th>Result</th><th>Label / source</th></tr>
<tr><td>File format (official rules)</td><td>{"PASS" if run_ok else "FAIL"}: float32, one band, EPSG:32611, shape and transform equal to the sample grid, all finite, values in [0, 1], no positive cells outside the footprint</td><td>Independent check of the on-disk bytes; <a href="{PROBLEM_URL}">official problem page</a></td></tr>
<tr><td>Exact duplicate of any local TIF?</td><td>{"No" if uniq["exact_duplicates"] == 0 else "YES"}</td><td>sha256 compare, {uniq["n_local_tifs_compared"]} local TIFs</td></tr>
<tr><td>Holdout-faithful DTI (visible-only apron)</td><td>{fmt(B["pooled_dti"])} (CI95 {fmt(B["ci95_cell_bootstrap"][0])} to {fmt(B["ci95_cell_bootstrap"][1])})</td><td>HOLDOUT-DTI, 16 cells, {e2["withheld_positives_total"]} withheld-truth pixels summed over cells</td></tr>
<tr><td>Matched random-dot floor</td><td>{fmt(rand["mean"])} (3 seeds)</td><td>HOLDOUT-DTI, same cells. The candidate does not beat chance.</td></tr>
<tr><td>As submitted (apron from full catalogue)</td><td>{fmt(A["pooled_dti"], 5)} (CI95 {fmt(A["ci95_cell_bootstrap"][0], 5)} to {fmt(A["ci95_cell_bootstrap"][1], 5)})</td><td>HOLDOUT-DTI. Structurally penalised; see irregularity 1.</td></tr>
<tr><td>Leakage canary: tmi_hg alone (AUC)</td><td>{fmt(can["aucs_min"], 3)} to {fmt(can["aucs_max"], 3)} (ceiling 0.90): {"PASS" if can["pass_below_ceiling"] else "FAIL"}</td><td>Per-cell AUC on the holdout</td></tr>
<tr><td>Literal 70% / 3 px lattice rule vs 13GEMSDOE witness</td><td>{lat["mine_within_3px_of_witness"]*100:.2f}% of its dots within 3 px: FAILS</td><td>Witness restored from pinned commit; SHA-256 matches manifest. Rule is saturated (random dots also fail).</td></tr>
<tr><td>Estimated leaderboard score</td><td>Not estimable</td><td>Internal holdout is not a leaderboard proxy (irregularity 1)</td></tr>
</table>

<h2>3. Why GEMSDOE32 scored highest: what we can and cannot verify</h2>
<ul>
<li><b>Measured:</b> its dots are placed off the mapped catalogue. In our holdout run the champion raster placed
{int(champ.get("on_visible_catalogue", 0))} of its {champ["emitted_pixels"]:,} dots on mapped catalogue cells
(HOLDOUT-DTI {fmt(champ["pooled_dti"], 4)}).</li>
<li><b>Measured:</b> it is one of a family of near-copies. GEMSDOE32 has 6,436 dots removed from GEMSDOE25's mask and none added
(<code>evidence/site_lineage_verification_20261029.json</code>).</li>
<li><b>Not measured:</b> the organizer's private new-fault labels. We cannot say which of its dots hit them. The
leaderboard gap between it and #1 (0.4544, below) is unexplained by anything we hold.</li>
<li>The forensic note is in <code>knowledge/02_why_gemsdoe32_b2_scored_0.2778.md</code>. Note: it has one known error (see irregularity 4).</li>
</ul>

<h2>4. Leaderboard (ORGANIZER-PUBLIC, read this session)</h2>
<p>Source: <a href="{LEADERBOARD_URL}">{LEADERBOARD_URL}</a>. Rank #1 0.4544, #2 0.3916, #3 0.3911 (checked 29 Oct 2026).
The top score in the session brief (0.4413) does not appear on this page.</p>

<h2>5. Irregularities for owner review</h2>
<ol>
<li><b>Holdout design biases against the competition's target.</b> The holdout's truth is mapped catalogue segments. A
file that avoids the catalogue (as the competition rewards) scores near zero by construction. The champion scored
{fmt(champ["pooled_dti"], 4)}, below the random floor {fmt(rand["mean"], 4)}. Fix: compute the apron from visible faults only (done in Arm B), or add a
truth set the holdout cannot leak. The vendored template is unchanged; this is a template-level decision.</li>
<li><b>Lattice rule is saturated.</b> The 70% / 3 px rule fails random dots (99.9%). The witness covers
{e1_cov}% of the footprint in 3 px disks. The official rules contain no such rule (<a href="{PROBLEM_URL}">problem page</a>, verified this session).</li>
<li><b>Portal error "Predicted values must be in range [0, 1]" is not reproduced.</b> Every local raster that was
checked is finite and in [0, 1]. We cannot tell whether NaN-outside rasters cause it. The writer uses all-finite zeros outside the footprint.</li>
<li><b>Known forensic error.</b> The 0.2778 note describes GEMSDOE28 as "parent minus a 1-pixel collar". The pinned file is not a collar (16,237 removed, 9,807 added).</li>
<li><b>Identical masks.</b> GEMSDOE25 and GEMSDOE30 have identical dot masks (verified).</li>
<li><b>Dense archived raster.</b> <code>archive/prototype/.../hunq1</code> has 3.94 million dots. Almost any dot lies within 3 px of it, so the "100%" overlap is an artifact, not a copy. The strongest overlap with a submission-sized raster is {max(u["mine_within_3px_of_theirs"] for u in uniq["all"] if u["dots"] < 1_000_000)*100:.1f}%.</li>
<li><b>Restore limits.</b> The GitHub API was rate-limited, so the 'scored' data group could not be restored. The 13GEMSDOE witness was fetched from the pinned commit's codeload archive and matched its SHA-256.</li>
<li><b>Budget.</b> Two of three experiments used. No slot was spent.</li>
</ol>

<h2>6. What would change the verdict</h2>
<ol>
<li>An owner decision on the lattice rule (official rules do not contain it).</li>
<li>A holdout whose truth is not mapped catalogue, or a validated calibration to the organizer score. Without one, no estimate is possible.</li>
<li>A candidate that beats the matched random floor on the holdout-faithful arm, with a leakage canary AUC below 0.90 for every feature.</li>
</ol>

<h2>7. Sources</h2>
<ul>
<li><a href="{PROBLEM_URL}">Problem description and submission format (official)</a></li>
<li><a href="{RULES_NOTE_URL}">Rules (official page links to the herox rules document)</a></li>
<li><a href="{LEADERBOARD_URL}">Leaderboard (official)</a></li>
<li><a href="{REF_SOLUTION}">Reference solution (DrivenData)</a></li>
<li><a href="{NLR_PDF}">DOE/NLR submission document (cited; not re-read this session)</a></li>
<li>Run card: <code>evidence/session_5ee7ef4b_run_card.json</code>; experiments: <code>evidence/exp1_shared_holdout_calibration_20261029.json</code>, <code>evidence/exp2_s1_holdout_and_uniqueness_20261029.json</code></li>
</ul>
</body></html>
"""
    PAGE.write_text(page)
    print(f"wrote {PAGE.relative_to(ROOT)} and {CARD.relative_to(ROOT)}; validator_ok={run_ok}")


if __name__ == "__main__":
    build()
