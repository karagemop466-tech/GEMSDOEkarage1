# GEMSDOEkarage1 · Evidence before submission

> **Current decision (2026-10-27, lane GPC-Z): one unique GeoTIFF has passed every automated gate — OK to download; spending a weekly slot is the selector's call.**
> File: `docs/downloads/gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif`
> (sha256 `75ac577a…6dbd`, 36,000 dots, float32, EPSG:32611, no NaN anywhere). HOLDOUT-DTI 0.1273 [0.1169, 0.1374]
> (`gemsk-hide-recover-v1`, 60,988 withheld px) — **not a leaderboard estimate**. Counter-signal: the 0.2778 champion scores
> higher on the shared template's SGMC off-catalogue calibration (0.0641 vs 0.0545, IR-K1-SGMC-01).
> Site: https://karagemop466-tech.github.io/GEMSDOEkarage1/ · lane pages: [docs/gpcz/](docs/gpcz/index.html) ·
> [how to submit](docs/gpcz/how-to-submit.html) · run cards: [evidence/run_card_gpcz.json](evidence/run_card_gpcz.json),
> [docs/data/run-card.json](docs/data/run-card.json) · release gate: [evidence/release_gate_gpcz.json](evidence/release_gate_gpcz.json).
> The earlier fail-closed review below (no candidate, DO NOT SUBMIT) is preserved as history; its own run card `evidence/run_card.json` stays negative.

## Lane GPC-Z — what was done this session (3 experiments, ≈2 h)

Hypothesis: unmapped faults are low scarps in the damage zone of mapped ones, facing the basin like their parents. Emit label-free
topographic *step edges* (det_elev, 1 m LiDAR step), gated by concordance between the scarp's downhill direction and the basin-deepening
direction from isostatic gravity + depth-to-basement, weighted by a near-catalogue prior g(d) measured by hide-and-recover
(67% of withheld strands lie within 1.5 km of a visible one), pruned ≥3 px from the catalogue, 36,000 binary dots at 2.8 px spacing.

| Gate | Result | Evidence |
|---|---|---|
| Format validator (ours + review's `validate_geotiff.py`) | pass, 11/11; whole array finite, values {0,1} | `docs/downloads/*-receipt.json`, `evidence/validate_geotiff_gpcz.json` |
| Uniqueness vs 15 registry rasters | max 31.7% of dots within 3 px; |ρ| ≤ 0.017 (lattice probe 99.9%, reported, IR-K1-LATTICE-01) | `evidence/run_card_gpcz.json` |
| Leakage canary | all single features AUC 0.35–0.57; prior alone 0.78 (< 0.90) | `evidence/leakage_canary_aucs.json` |
| HOLDOUT-DTI, same evaluator, vs the H19-5 field that produced 0.2778 | 0.1298 vs 0.1049 at 37,654 (interleaved); paired gain over physics-only +0.060 [+0.050, +0.069] | `evidence/exp2_gpcz_holdout.json` |
| Shared template evaluator (GEMSDOE32 pin, unmodified) on the final rasters | hide-recover v3: 0.0123 vs champion 0.0045; **SGMC off-catalogue: 0.0545 vs champion 0.0641** | `evidence/template_evaluate_holdout_*.json` |
| Review's `release_gate.py` | `promote` (ok_to_submit is never set by design; selector separate) | `evidence/release_gate_gpcz.json` |
| Negative results | contour-obliquity gate falsified (AUC 0.42); sqrt-prior hedge 89% identical → dropped; blocked 20 km holdout inverts the distance prior | `evidence/`, `docs/gpcz/research.html` |

Code: `src/gemsk/` (grid, metric verified against brute force, holdout blocked+interleaved, features, NMS emission, prior, submission
writer+validator, uniqueness, pipeline); `scripts/run_experiment{1,2,3}_*.py`; `scripts/build_gpcz_site.py` → `docs/gpcz/`;
13 lane tests in `tests/test_{metric,emission,holdout_prior,submission_writer}.py` (78 pass overall). Reproduce:

```bash
pip install -r requirements.txt && python3 scripts/restore_data.py --group all
PYTHONPATH=src python3 -c "from gemsk import grid; grid.prepare_bands()"
PYTHONPATH=src python3 scripts/run_experiment1_screen.py 37654 && PYTHONPATH=src python3 scripts/run_experiment2_gpcz.py
PYTHONPATH=src python3 scripts/run_experiment3_build.py && python3 scripts/build_gpcz_site.py && python3 -m pytest -q
```

Standing brief (clause-by-clause reconstruction; paste the verbatim prompt over it): [`docs/standing-prompt.md`](docs/standing-prompt.md).
Knowledge base: [`knowledge/geothermal-fault-knowledge.md`](knowledge/geothermal-fault-knowledge.md); sources table: [`docs/sources.md`](docs/sources.md).

### Remaining work / limitations for the next session
1. Selector (human, weekly cap): decide whether to spend a slot on the file above; record the organizer score as ORGANIZER-CONFIRMED in `registry/score_ledger.csv`, then re-run `build_gpcz_site.py`.
2. IR-K1-SGMC-01: the champion beats GPC-Z on the SGMC off-catalogue instrument. Next experiment budget should test whether a 44,090-dot GPC-Z emission or a looser prior (g(d) floor) closes that gap without losing the hide-recover advantage — both are one call to `gemsk.pipeline.build`.
3. H3 (radiometric across-edge juxtaposition) is runnable with data on hand; H4/H5 need `earthquake.usgs.gov` (ComCat, Monte Cristo rupture) mirrored to github.
4. Shoreline mimic (IR-K1-OBLIQ-01): obtain Reheis (1999) pluvial-lake shoreline polygons (USGS MF-2323) and down-weight contour-parallel steps at Lahontan highstand elevations.
5. Data provenance: pins are mirror-consistent, not organizer-authenticated; nothing outside github.com/pypi.org is reachable from the sandbox.

---

## Earlier parallel review (preserved verbatim)

> **Decision of that review: NO submission-ready GeoTIFF. DO NOT SUBMIT.** (superseded for lane GPC-Z by the section above)
> The initial checkout contained only this README. This session audited pinned
> historical files and built a fail-closed decision site; it did not run a
> geological experiment, generate a new candidate TIFF, spend a submission slot,
> or receive an organizer score. [Open the executive summary](docs/executive-summary.html)
> and [run card](docs/data/run-card.json). [Three review passes](knowledge/three-pass-review.md).

## Starting brief — read this before every session

The owner's goal is a **new, scientifically grounded, genuinely unique** fault
prediction GeoTIFF that can compete for the DOE GEMS Prize. The project must
show a prominent, easy-to-use download **only when** automated format,
scientific, uniqueness and separate slot-selection gates permit it; otherwise
it must explicitly say **DO NOT SUBMIT**. Never copy or rename an old submission
as a new one. The output must be a single-band float32 GeoTIFF with values in
`[0,1]` and the official CRS, shape and transform. Preserve the user's reported
portal error, “Predicted values must be in range [0, 1]”, as an unresolved
format concern; do not promise portal acceptance from a local test alone.

**Focus:** compare GEMSDOE24, 25, 27, 28, 30, 31, 32, 33 and 36 in a clear
executive table, with exact historical artifact links, evidence labels,
uniqueness and submit status. Distinguish a catalogue-holdout DTI from a
leaderboard score; a projection is not a score. Historical scores supplied by
the owner are **USER-REPORTED / UNVERIFIED**, unless an actual submission-page
receipt ties the score to the file. No calibrated leaderboard estimate is
currently available. Review official rules, source links, data licensing and
geological alternatives; flag irregularities rather than guessing. The target
is **fault structure relevant to geothermal resources**, not proof of a vent.

**Core values:** maximize the probability of winning by protecting submission
slots and taking evidence-led decisions; own the outcome by tracing errors,
limitations, measurements and next steps end to end. Work without a human
inspector; invalid or incomplete checks fail closed. Execute three review passes
and report the actual result, including negative outcomes.

### Parallel-run protocol (owner's instruction)

1. **Lane:** “Your lane is the single method paragraph below. Stay inside it. If
   your raster's rank-correlation with any registry raster exceeds [0.90], or
   more than [70%] of your dots fall within 3 px of one registry raster's dots,
   you have drifted into another lane: log it as a duplicate and stop. Check this
   on the surface before placement AND on the final dots.” The provided prompt
   does not actually identify a single method paragraph. Do not invent an
   assignment or quietly exempt the calibration lattice.
2. **Reuse:** use the assigned template's cached feature stack,
   `evaluate_holdout.py` and `submission_writer.py`. Hide whole fault segments
   with a buffer, derive every catalogue feature only from visible faults, mask
   visible faults pixel-exactly, score pooled DTI (α 0.2, β 0.8, 300 m triangular
   kernel). Fix a wrong shared tool once in its template; do not keep a private
   fork. This checkout has neither the cache nor an agreed template: peers pin
   different template families.
3. **Evidence:** label numbers as HOLDOUT-DTI (evaluator version, withheld
   positives, 95% CI) or ORGANIZER-CONFIRMED (actual submission-page receipt).
   User claims that cannot meet either label remain visibly unverified; never
   recast a projection as a score.
4. **Leakage canary:** test each feature alone on the holdout. AUC above 0.90 is
   leakage until proven otherwise.
5. **Run card:** end with one JSON card covering hypothesis, mechanism, named
   non-fault mimic, holdout DTI + CI, correlation/overlap versus registry, raster
   SHA-256, validation, submission name and ≤140-character note, and verdict.
   Negative results are deliverables.
6. **Budget:** stop after 3 experiments or 2 hours. Do not choose a submission
   slot; that is a separate selector step within the live weekly allowance.

Before implementation, rank 3–5 specific, untried-in-this-checkout geological
hypotheses with input layers, signatures, reasons they might find missing faults,
non-fault mimics, novelty caveats, data availability and cost. Validate the
assigned top candidate against a comparable current-best spatial holdout before
spending a slot. See [research review](knowledge/research-review.md).

## Verified this session

- Pinned raster audit: [JSON](docs/data/reference-audit.json),
  [reference manifest](registry/reference_assets.json); historical files are
  source references only. All 72 directed comparisons among these nine rasters
  exceeded the 70% 3-pixel rule. This is **not** the full current registry.
- The same audit independently verified that GEMSDOE32 B2 is the GEMSDOE25 d2.8
  mask minus the ≤2-pixel mirrored-catalogue collar. This supports an emission
  hypothesis, not a causal explanation of a hidden score.
- One registered lattice covers 99.8713% of the mirrored footprint within
  3 pixels. At 37,654 distinct in-footprint dots the minimum possible directed
  overlap is 82.3418%; the literal threshold is >70%. The bound is not a score,
  and says nothing conclusive about other budgets.
- The owner-mirrored “sample submission” has 60,988 positive pixels identical
  to the mirrored labels, contrary to the official description of the example
  as total absence. The mirror is not organizer-authenticated and is used only
  as grid/footprint evidence here; do not use its values as predictions.
- A pinned GEMSDOE24 `make_note` helper allows 200 characters, exceeding the owner’s 140-character limit. The 57 writer enforces 140, but no shared template has been assigned. The discrepancy is [reproduced and recorded](docs/data/template-review.json); no private writer was created or upstream code modified.
- The problem page specifies null/NaN outside bounds, while the user reports a
  portal range error. Some historical NaN-outside files fail a hypothetical
  strict *whole-array* `[0,1]` check; zero-outside files differ from the written
  outside-null instruction. **Neither encoding has been tested with the portal
  in this session.**

## Reproduce the independent audit

Requires Python, `gh`, authenticated or sufficient public GitHub API access and
about 14 MB of reference files. Bulk data and caches remain Git-ignored.

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python scripts/audit_references.py --fetch
python scripts/preflight.py  # exits 1: blocked / negative is not an upload pass
pytest -q
```

The audit downloads only immutable GitHub reference bytes, verifies size and
SHA-256, reopens GeoTIFFs, checks geometry/range and computes binary-dot
correlation and directed Euclidean overlap. It does **not** run the shared
holdout, generate a model, check all registered rasters, select a slot, or
submit to DrivenData. The separate preflight always writes a negative card for
this incomplete run and exits with status 1: a blocked result must never look
like an automated upload pass.

A later, peer-generated GEMSDOE25 H79 research raster was independently
checked after the historical snapshot. It has 37,654 dots and **100% overlap
with the registered lattice** at 3 px; its owner also marks it DO NOT SUBMIT.
This is not a project-generated candidate, and its holdout was not reproduced.
See [concurrent review](docs/data/concurrent-review.json). To rerun it after
the main reference audit: `python scripts/audit_concurrent.py --fetch`.

### Diagnose a future file's exact bytes

```bash
python scripts/validate_geotiff.py path/to/prediction.tif --template path/to/sample_submission.tif --out format-diagnostic.json
```

This read-only tool separately reports the in-footprint `[0,1]` check,
null/NaN-outside variant and strict whole-array variant; it never repairs data or
asserts that a supplied template is organizer-authenticated. A successful
format diagnostic is **not** authorization to submit. An optional
`--template-sha256` checks a separately obtained pin. Use an authenticated
sample and the agreed shared writer for a real candidate.

## Data, access and next steps

The [official data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
redirects to login in the research view. No DrivenData account, account quota,
organizer-authenticated data, private truth, or score-to-file receipts are
available here. The owner mirror of the large feature raster is identified in
[a peer manifest](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/registry/data_manifest.json),
but the prepared feature cache is not present. GPU is **not** proven mandatory:
the official [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
supports CPU as well as GPU; performance and resources depend on method.
Direct downloads outside GitHub/package registries are restricted in this
sandbox. See the [source and scientific review](knowledge/research-review.md).

Next: obtain a coordinator-assigned single lane and policy for the literal
space-filling registry control; restore an agreed shared template and its
feature cache with source/byte verification; establish a frozen comparable
baseline and complete registry; then run canaries, buffered holdout and both
novelty gates before any selector considers a slot. Do not optimize predictions
around lattice holes just to produce a green badge. The site checks GitHub
source revisions in the visitor's browser, but does not scrape DrivenData's
leaderboard because of its [terms](https://www.drivendata.org/termsofuse/).

## Parallel integration and archived demonstrators

Other sessions merged onto main while this review was in progress. Their
independent detailed pages, source evidence, release gate, and GitHub Actions
workflows are retained alongside this dashboard. The main dashboard links to
[the detailed nine-site review](docs/index.html); [legacy overview](legacy-overview.html)
and [prior negative card](docs/data/run_card.json) remain available. This
review’s active, stricter explanatory card is [run-card.json](docs/data/run-card.json).

Two inherited artifact sets are **synthetic demonstrators, DO NOT SUBMIT**:
[H-UNQ-1](archive/prototype/README.md) has a placeholder transform that does
not match the mirrored sample, and [CDA1](archive/cda1-demonstrator/README.md)
uses synthetic layers and a holdout function that returns fixed numbers. CDA1's
claimed holdout/CI is **not a measurement**. Its actual lattice overlap is
37,570/37,654 = 99.7769%, not its archived 99.99% claim.
[Independent archive diagnostics](docs/data/archive-review.json) are reproducible
with `python scripts/audit_archives.py` after fetching the reference cache.
The original archive content remains in Git history; warnings have been added.

`python scripts/build_site.py` rebuilds the retained detailed/legacy views;
`python scripts/render_site.py` rebuilds this homepage and current executive
table. The GitHub Actions tests exercise the combined project. The scheduled
evidence refresh uploads an Actions artifact, not an automatic Pages update.
