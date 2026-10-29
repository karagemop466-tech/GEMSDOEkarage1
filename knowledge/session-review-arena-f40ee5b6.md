# Current review — `arena/f40ee5b6-gemsdoekarage1` · 29 October 2026

> **Verdict: NEGATIVE / DO NOT SUBMIT.** Repository, source and website review only. No new TIFF, geological experiment, holdout evaluation, score estimate or slot selection was produced.

## Executive decision

The highest supplied focus-site number is **0.2778 for GEMSDOE32 B2, USER-REPORTED / UNVERIFIED**. A fresh check of the third-party GEMSDOE32 page confirms that it labels 0.2778 `OWNER-REPORT` and says no submission-page receipt links the reported score to the raster hash. This is a peer-page assertion, not an organizer receipt.

The pinned mirror rasters show a geometric lineage: GEMSDOE25 and GEMSDOE30 have identical 44,090-dot masks; GEMSDOE32 B2 has 37,654 dots, exactly the parent support minus 6,436 dots within two pixels of the mirrored catalogue, with no additions; GEMSDOE36 keeps B2 and adds 1,200 dots. This does **not** identify why a hidden-label score changed. Removing near-catalogue dots could reduce weighted false-positive cost or lose withheld-fault coverage. No causal claim, comparative holdout score or beatability estimate is justified.

The nine requested focus-site reports and pinned peer-file links are on the [executive summary](../docs/executive-summary.html). All nine peer rasters trigger the user's internal >70%-within-3-px stop against another listed peer; the largest directional overlap ranges from 97.58% to 100%. These are saved-mask geometry checks only—not continuous-surface rank correlations, not proof of causal similarity, and not an organizer rule. There is no newly cleared project file.

## Execution and release gates

The saved [shared preflight](../evidence/session_f40ee5b6_shared_preflight.json) exits nonzero and reports `ready_for_shared_tools: false`, `ok_to_submit: false`:

- `method_lane` is null and no valid `canonical_template_assignment` is recorded.
- Missing inputs: `.cache/gems_work/feature_stack.npy`, `.cache/gems_data/existing_faults.tif`, `training_features.tif`, `sample_submission.tif`, and `labels.tif`.
- The local immutable-pin audit finds mismatches in `vendor/gems57/submission_writer.py` and `vendor/gems57/uniqueness.py`; it also reports that the vendored source and template pin differ. See [template integrity JSON](../evidence/session_f40ee5b6_template_integrity.json). Hash consistency alone would not establish owner authorization.
- The shared evaluator/writer are therefore not authorized. The historical private runner was invoked only to verify its gate and refused before producing output (`BLOCKED: Historical H-K1-1 runner disabled...`). No experiment was executed and no TIFF was created.
- No candidate exists for continuous-surface correlation, final-dot registry overlap, format validation, SHA-256 or HOLDOUT-DTI. The complete organizer registry is not present.

The one registered run-card deliverable is [here](../evidence/session_f40ee5b6_run_card.json). It records the proposed top queue item, physical mechanism, named mimics, all HOLDOUT-DTI fields as not run, both uniqueness checks as not run, no raster/hash, no validator result, a ≤140-character no-submission note, zero experiments and a negative verdict.

## Current official-source findings

The claim-by-claim register is [knowledge/official-sources-verified-2026-10-29.md](official-sources-verified-2026-10-29.md). Key observations fetched on 29 October:

- [DrivenData problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) gives the fault-mapping goal, 100 m / EPSG:32611 float32 GeoTIFF specification and distance-weighted Tversky metric (α=0.2, β=0.8, 300 m triangular kernel).
- [DrivenData data route](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) redirects to login. Official training rasters and labels were not accessed or downloaded.
- [Public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) snapshot: #1 0.4544, #2 0.3916, #3 0.3911, #47 0.3195, #50 0.3167. The page shows relative timestamps, not an exact fetch time; this is neither the private nor final board. The reported 0.4413 is not in the fetched top 50.
- [DOE/NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), sections reviewed in chunks 0–2: single-band 100 m GeoTIFF; three submissions per week as specified on the contest site; one final set is selected; the public board may differ from private final scoring; generative-AI use must be disclosed in the narrative when applicable.
- [USGS GeoDAWN ScienceBase release](https://doi.org/10.5066/P93LGLVQ) lists downloadable Area 1 and Area 2 GeoTIFF bundles (43.57 MB and 230.54 MB). USGS describes the data as CC0. Catalog-level availability is checked; no payload, CRS, exact local coverage, or feature independence was inspected.
- [USGS 3DEP product page](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) says products are free and without use restrictions; it describes full seamless 1/3-arc-second coverage over the contiguous U.S. and distinguishes still-expanding/limited 1 m availability. No local tile was fetched or grid-aligned.

## Four pre-implementation research hypotheses

The [research page](../docs/research.html) and [hypothesis slate](../docs/research/hypotheses-20261029.md) list four ranked proposals, all **unimplemented and unvalidated**. Ordering is qualitative—not expected DTI gain. Rank 1 is a queue preference only, not an assigned lane.

1. **CP-DPCS — Cross-Potential Dip-Polarity Co-Gradient Step** (medium): paired signed RTP magnetic phase and gravity-gradient relation across continuation scales under low-relief cover. Mimics include plutonic/metasedimentary contacts, caldera margins, basalt edges, paleochannels and survey seams. Proposed inputs are on the login-gated contest stack; no local data or lane.
2. **BERB-STC — Biharmonic Elastic Relay-Bridge Stress-Transfer Corridor** (medium–high): fold-local visible segment endpoints with strain/seismicity and conductivity/gravity corroboration. Mimics include mining/geothermal induced seismicity, playa brines and interpolation bullseyes. No fold-local data/graph or valid paired holdout.
3. **WD-KRMT — Wavelet-Destriped Potassium-Residual Magnetics Trough** (medium–high): line-corrected GeoDAWN radiometric residuals paired with a magnetic trough. Mimics include potassic intrusions, weathering, volcanic units, evaporites and flight-line artifacts. Official files are catalog-listed; payload and local suitability remain unverified.
4. **CF-DIKA — Cross-Fan Drainage-Incision Knickzone Alignment** (high): replicated drainage deflection / knickzones across three or more adjacent catchments at a gravity step using 3DEP elevation. Mimics include Lahontan shoreline benches, fan avulsion, piracy and lithologic ledges. Product-level coverage is described by USGS; local tile/alignment is untested.

Earlier Lahontan shoreline-datum and terrace-riser ideas are deferred; their required candidate-area source layers were not verified. Any future experiment must use fold-local catalogue features, exact visible-fault masking, whole buffered fault-segment holdout, the pooled metric, individual feature leakage canaries, pre-placement surface comparison and final-dot checks, and the shared evaluator/writer.

## Three review passes

1. **Implement / verify:** refreshed official and peer-page source checks; audited the shared-tool preflight and template hashes; rewrote the README as a project starting point; updated the central renderer to place the current decision and nine-site table consistently on generated pages; added the four-candidate, source-linked research slate. No scientific experiment or TIFF was run or produced.
2. **Adversarial review:** verified that preflight fails closed on the missing assignment/cache and two vendored hash mismatches; verified the historical runner refuses execution without output; compared B2 mask algebra without treating it as score causality; marked peer overlap as dot geometry and internal policy, not official rule; checked that external-source catalog availability is not described as local data validation.
3. **Request re-check:** nine focus sites are ranked with highest supplied file/score and peer-overlap stop; GEMSDOE32’s 0.2778 is labeled unverified with the peer receipt caveat; four hypotheses name layers, mechanism, mimics, distinction and source readiness; no holdout, new TIFF, upload slot or score forecast is asserted. Public pages remain DO NOT SUBMIT.

## Tests and deliverables

The post-edit full suite passed: **380 passed, 119 warnings** (`./.venv/bin/python -m pytest -q`). The pre-edit baseline was **373 passed, 119 warnings**. The seven added feed/regression checks account for the increase; these are software checks only, not model-performance evidence or a geological score. The site build also completed deterministically: `Rendered 32 deterministic decision pages; no submission authorized.`

- [README project brief](../README.md)
- [Generated executive summary and submission guide](../docs/executive-summary.html)
- [Generated research and source page](../docs/research.html)
- [Official source register](official-sources-verified-2026-10-29.md)
- [Run card](../evidence/session_f40ee5b6_run_card.json)
- [Preflight](../evidence/session_f40ee5b6_shared_preflight.json)

## Remaining work / limitations

1. Obtain the explicit assigned method paragraph and authoritative canonical-template assignment. Have the owning template maintainers resolve pin mismatches upstream; do not repin or fork locally.
2. Obtain the organizer data through an authorized account, verify raster/label roles and source hashes, restore the shared stack and evaluator inputs, and authenticate a complete registry.
3. Resolve how the user’s internal 70% / 3-px / Spearman rule applies; it is not in the official competition specification. Do not jitter or otherwise evade it.
4. Verify shared holdout controls, implement only the assigned lane, use fold-local visible data and whole buffered-segment holdouts, run leakage canaries, and stop within the three-experiment/two-hour budget.
5. Compare every continuous candidate surface before placement and final dots against the complete registry. Generate and validate a float32 GeoTIFF only after eligibility gates pass. Record the exact hash, validators and note in the run card.
6. Promotion and weekly-slot selection remain separate. Do not submit any file without all evidence gates and an independent selector decision.

No credentials were requested. The requested “proceed without manual input” does not authorize inventing a lane, bypassing missing data or falsifying holdout/uniqueness results; these blockers are recorded for the next authorized step.
