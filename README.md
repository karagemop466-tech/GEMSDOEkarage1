# GEMSDOEkarage1 · Evidence before submission

> **Current decision: NO submission-ready GeoTIFF. DO NOT SUBMIT.**
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
