# GEMSDOEkarage1 — fault discovery, evidence first

> **DO NOT SUBMIT — no eligible new GeoTIFF exists.** The two previously
> promoted research files each duplicate a registered lattice under the user's
> literal rule. No geological experiment, competition upload, or weekly-slot
> selection was made in this session. A format check is not submission approval.

[Decision dashboard](docs/index.html) · [Executive summary and future submission guide](docs/executive-summary.html) · [Nine-site audit](docs/data/reference-audit.json) · [Shared-template audit](evidence/shared_template_audit_20261028.json) · [Latest negative run card](evidence/run_card_arena_a2fe7ce0_20261028.json) · [Research hypotheses](docs/research.html) · [Official source register](knowledge/sources-2026-10-28.md)

## Latest review — 28 October 2026, session `arena/a2fe7ce0-gemsdoekarage1`

**DO NOT SUBMIT — no new candidate TIFF exists.** The current runtime restored
and hash-verified 16 third-party mirror inputs and built the pinned template's
35-channel float32 cache (`3730 × 3292 × 35`, 1,719,082,528 bytes, SHA-256
`f95486ffa937e0237c53c5e7f59e49cc142825ae5ea56b166d64dcbfeef5bdc0`).
Those ignored bytes may not persist and are not organizer-authenticated. Data
placement is no longer the immediate local blocker, but it is not sufficient.

An unchanged replay of the reviewed shared-template pin found that its claimed
15-pixel buffered holdout has a measured minimum truth-to-visible distance of
**2 pixels** in every cell; **15,705 / 22,232** withheld-positive pixel
instances lie inside the claimed collar, and 76 selected connected-component
instances are only partly scored. A deliberately leaking full-catalogue static
input is still nested under a `HOLDOUT-DTI` label and numerically returns
`1.0 [1.0, 1.0]`; this is explicitly **INVALID-HOLDOUT / LEAKAGE-CANARY**, not a
score. The defects were reported centrally as [upstream issue 60](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/60)
and [issue 61](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/61), alongside
open cache/filter [issues 49](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/49)
and [53](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/53). No private
fork was made.

The prompt still provides no single method-lane paragraph. Preflight now binds
the exact shared checkout, tool bytes and six runtime assets (including the
1.7 GB cache) to a machine-readable contract and blocks even with all local
inputs present. No geological experiment, score estimate, uniqueness
claim, portal upload, or weekly-slot selection occurred. See the [three-pass
review](knowledge/session-a2fe7ce0-review.md), [tool/cache evidence](evidence/shared_template_audit_20261028.json),
and [session run card](evidence/run_card_arena_a2fe7ce0_20261028.json).

## Prior review — 28 October 2026, session `arena/0fb1ec81-gemsdoekarage1`

The previously reported lattice failure was independently replayed from pinned
mirrors: 38,174/38,200 historical HMAS dots and 35,959/36,000 historical GPC-Z
dots are within 3 px. The [reassessment](evidence/reassessment_arena_0fb1_20261028.json)
is reproducible but uses a third-party footprint, not an authenticated organizer
sample. All 31 pinned mirrors were restored into ignored `data/` in this
runtime; those local bytes are not tracked and may not persist between sessions.
No geological experiment, candidate raster, holdout score or submission was made.
The old `prepare_data.py` is intentionally blocked: it builds a quarantined
private stack, not an assigned shared cache. Data placement alone is **not** the
only blocker.

A selectable ID was added for the B2 reference; the format diagnostic now
refuses to overwrite its input, and the release policy requires the validator's
candidate SHA-256 to agree with the run card. This hash agreement does **not**
independently authenticate a report or its template; the policy still consumes
assertions and is not a substitute for evidence provenance and a selector.
The scheduled GitHub workflow archives a refresh artifact; it does not publish
a live verified leaderboard or automatically update the public Pages site.
See the [session review](knowledge/review-arena-0fb1-20261028.md) for tests,
constraints and next actions.

## Current parallel-run warning — 28 October 2026

Independent saved-byte checks show the pinned [PR 20 TD-KSCK and PR 19 CTWS-2D candidates](knowledge/parallel-candidate-audit-2026-10-28.md) also fail the literal lattice stop: 37,584/37,654 (99.8141%) and 37,999/38,200 (99.4738%) of their dots respectively lie within 3 pixels of that witness. Their own reports excluded it from the passing maximum. **DO NOT SUBMIT either.** This is a one-witness negative audit, not a holdout or complete registry scan. The mirror is not authenticated; no slot was spent.

## Latest follow-up: release-gate consistency

[Session review](knowledge/session-0f04bfcc-review.md) ·
[Negative session run card](evidence/session_0f04bfcc_run_card.json). The local
release gate now rejects a candidate SHA-256 identical to any reported registry
raster even if the card claims the bytes differ. This is an internal consistency
check, not independent hash or registry authentication. No experiment, new TIFF,
score estimate or slot selection was made; **do not submit**. Full suite: 219
passed, with 53 rasterio warnings.

## Earlier follow-up: automation preflight


The shared-tool adapter now exits **1** when the assigned lane or required
cached inputs are absent, including `existing_faults.tif`. A successful JSON
report write is not a readiness pass. Even exit 0 checks input presence only,
not provenance, scientific merit, uniqueness or upload authorization.
[Three-pass follow-up review](knowledge/session-a0f0d036-review.md) ·
[Session negative run card](evidence/session_a0f0d036_run_card.json).
Full suite: **216 passed**. No new experiment, score, TIFF or slot selection.

### Latest follow-up — session `5b69d76e`

An independent saved-byte recheck fetched the pinned peer sample and lattice:
[replay evidence](evidence/session_5b69d76e_prior_audit.json) and [session run
card](evidence/session_5b69d76e_run_card.json). Both historical TIFFs again fail
on the lattice witness; no new raster, holdout result, upload or slot selection
was made. The session did not receive the protocol's promised single method-lane
paragraph. Neither the full registry nor organizer-authenticated template is
established; the mirrored sample is not official proof.

The release gate now requires candidate/template hashes in the validation
record and matching hash-pinned holdout fold assignments for the baseline and
candidate. Hash equality is a consistency check, **not** proof of provenance,
proper spatial splits, or authenticity. Synthetic regression tests cover missing
and conflicting bindings. The shared template was not modified; its upstream
identity and previously reported comparator defect still need resolution. See
[three-pass follow-up](knowledge/session-5b69d76e-review.md).
### Latest independent session review

The [three-pass session review](knowledge/session-review-arena-9ad4a8a0.md) and [negative session run card](evidence/run_card_arena_9ad4a8a0.json) record a fresh restoration of the pinned mirrors, an exact reproduction of the duplicate audit, and a fix for masked in-footprint pixels in the strict local format checker. **No new TIFF, holdout estimate, or submission-slot decision was produced.** The restored mirrors are not authenticated organizer inputs; the assigned lane, shared stack and complete registry remain unresolved. The scheduled refresh creates a workflow artifact, not a live published feed.

### This branch's independent checkout review

The [review record](evidence/session_review_2026-10-28_arena-470a3424.json)
reproduced the fail-closed software status; no geological experiment or
submission was made. Its initial preflight reported no assigned lane and lacked
the feature stack and input rasters. The inherited TIFFs already fail the
literal 3-pixel lattice-overlap gate; this is not a pre-placement uniqueness
check for a new candidate. At that checkout point, the suite had **205 passed,
0 failed, 0 skipped** (53 Rasterio deprecation warnings) and the site builder
rendered 32 pages deterministically. A later merged follow-up records 219
passing tests and strengthens preflight/gate behavior. After synchronizing this
branch with the latest main, the complete suite passed **221 tests** (62
Rasterio warnings). Neither test count is a holdout result or submission
authorization.

## What changed on 28 October 2026

An independent audit reopened the **already committed** TIFF bytes against nine
pinned historical references and the pinned lattice. It did not audit the
pre-placement surfaces or the complete current registry. The old fleet and
GPC-Z uniqueness reports excluded the lattice, and their `promote` decisions
and slot-approval claim are superseded.

| Prior research file | SHA-256 | Within 3 px of lattice | Decision |
| --- | --- | --- | --- |
| `karage1-hmas-sinter-dualcover-sep29-20261027T220000Z-zeros.tif` | `198076f81067353c3ee41d947c7830ef11db2e8128bc5f8c5bd20ef036736f76` | 38,174 / 38,200 = **99.9319%** | duplicate · DO NOT SUBMIT |
| `gemsk1-gpcz-polarity-damagezone-36000dots-20261027T213002Z-636ed4c9-zeros.tif` | `75ac577a9131f6837b2de28be8932c326d1083bb46fcaebc1efc28e177526dbd` | 35,959 / 36,000 = **99.8861%** | duplicate · DO NOT SUBMIT |

Both exceed the strict **>70%** rule, so no high-level uniqueness pass is
possible. Research-only downloads, with explicit warnings, are available on
the [audit page](docs/executive-summary.html#audit); they are **not** a new
submission or permission to upload. The prior weekly slot status is unknown;
this session selected or spent none.

The lattice itself lies within 3 px of 5,160,724 / 5,167,373 mirrored-footprint
cells (99.8713%). Only 6,649 cells lie outside this radius. Consequently, a
37,654-dot raster must overlap by at least 31,005 / 37,654 = **82.34%** even in
the most favorable placement. At most 22,163 dots can theoretically satisfy the
lattice limit at that footprint; this is only a necessary bound, not proof that
any smaller candidate passes other gates or is scientifically valid.

The files are single-band float32, match the **owner-mirrored** CRS/shape/
transform and are finite in [0,1] inside the footprint. They contain zeros
outside that footprint, not null/NaN. The [official format description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format)
uses null/NaN outside the bounds; a whole-array finite check tests a different
condition. Neither convention has been portal-tested here, and the cause of the
prior reported `[0,1]` rejection is **unknown**. The mirror is not authenticated
against organizer bytes.

## Nine-site comparison — historical claims, not forecasts

Values below were supplied/reported by the user or owner; none is backed here
by an artifact-linked organizer receipt. `New score` is **unavailable**: no
projection is presented as a score. Each row uses one hash-pinned historic file;
uniqueness failure against one registry witness suffices, while passing this
limited audit would not establish uniqueness against all submissions.

| Site | Audited historic file · research only | User-reported, unverified | Dots | Lattice overlap | New score |
| --- | --- | ---: | ---: | --- | --- |
| [GEMSDOE32](docs/GEMSDOE32.html) | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 | 37,654 | 99.92% · duplicate | unavailable |
| [GEMSDOE36](docs/GEMSDOE36.html) | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 | 38,854 | 99.92% · duplicate | unavailable |
| [GEMSDOE28](docs/GEMSDOE28.html) | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 | 37,660 | 99.91% · duplicate | unavailable |
| [GEMSDOE31](docs/GEMSDOE31.html) | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 | 40,199 | 99.92% · duplicate | unavailable |
| [GEMSDOE33](docs/GEMSDOE33.html) | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 | 41,865 | 99.91% · duplicate | unavailable |
| [GEMSDOE25](docs/GEMSDOE25.html) | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 | 44,090 | 99.92% · duplicate | unavailable |
| [GEMSDOE30](docs/GEMSDOE30.html) | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 | 44,090 | 99.92% · duplicate | unavailable |
| [GEMSDOE24](docs/GEMSDOE24.html) | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 | 60,069 | 99.92% · duplicate | unavailable |
| [GEMSDOE27](docs/GEMSDOE27.html) | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 | 61,328 | 99.92% · duplicate | unavailable |

## Why might GEMSDOE32 B2 have looked promising?

The **0.2778 is USER-REPORTED / UNVERIFIED**; a receipt tying that score to the
file is absent. The exact audited B2 mask equals GEMSDOE25 d2.8 after deleting
6,436 points within 2 px of the mirrored known-fault catalogue; no points were
added. GEMSDOE25 and GEMSDOE30 have identical dot masks on the audited grid.
These are geometric relationships, not causal proof.

The [official distance-weighted Tversky metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric)
rewards the best weighted prediction within 300 m of each true fault while
charging for predicted mass not near truth. Thinning a redundant prediction may
save more false-positive mass than true coverage and improve DTI, but it can
also delete real recoverable faults. The [staff clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)
says known pixels are masked, not that their surrounding 300 m is free. An
identical-fold, fold-local ablation is necessary to test the mechanism. A higher
result is conceivable but **not established** by this audit; a public
leaderboard snapshot was **0.4544 on 28 Oct 2026**, not a future rank or a
score for our file. [Check the organizer leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/).

## Research, not experiments

The [research review](knowledge/research-review.md) explains the DTI algebra,
data requirements and confounders. Four qualitative, ranked proposals are:

1. **Medium cost:** signed two-scale magnetic/gravity offsets with topography;
   lithologic contacts or flow edges can mimic faults. Distinct from prior
   unsigned HMAS edges in the reviewed code; fleet-wide novelty is unverified.
2. **Medium cost:** local K/eTh alteration-boundary residuals aligned with
   magnetic edges; weathering, potassic intrusions and survey blocks mimic them.
   [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
   lists free products; official bytes not fetched.
3. **High cost:** repeated catchment drainage asymmetry on
   [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) DEMs; erosion and
   stream piracy mimic fault-related drainage. Exact tile coverage not checked.
4. **High cost:** sampling-aware cross-fitted thermal-probe residuals with
   gravity boundaries using [GDR INGENIOUS](https://gdr.openei.org/submissions/1391);
   solar heating, groundwater and access bias mimic the signal. Official raw
   probes and local coverage not independently verified.

Ordering is a qualitative assessment of expected promise and cost, not a
measured or predicted DTI. No new lane was supplied; no hypothesis was fit. The
GEMS target is unmapped **faults**, not direct proof of geothermal vents.

## Data, tools and reproducibility

All **31** pinned GitHub mirrors were restored and rechecked (4 core, 12
external, 15 scored; 551,538,109 bytes). The [receipt](evidence/data_restore_verification_20261028.json)
and [manifest](registry/karage1_data_manifest.json) record size, SHA-256 and
immutable source commits. The cache is excluded from Git and snapshots; rerun
restoration in a fresh environment. These hashes establish mirror consistency,
not organizer origin or data license for every derived layer. Notably the
mirrored sample's positive mask equals the mirrored labels, contrary to the
organizer's description of an all-absence sample: use it only as a grid and
footprint until official bytes are checked.

```bash
python -m pip install -r requirements.txt
# Public GitHub mirrors, not a DrivenData download:
bash scripts/download_competition_data.sh --data-dir .cache/gems_data
bash scripts/download_competition_data.sh --data-dir .cache/gems_data --verify-only
python scripts/shared_tools.py bootstrap
python scripts/shared_tools.py audit --report-only  # negative until the upstream contract is fixed
python scripts/shared_tools.py preflight            # currently blocked by lane + contract, not input placement
python scripts/build_site.py                        # deterministic, negative decision pages
python -m pytest -q
```

Historical private experiment/stack builders and lane-specific report builders
are quarantined. The single site renderer refuses to build when the audited
bytes or negative decision disagree. `scripts/release_gate.py` requires
comparison rows, the pinned lattice, holdout provenance and validator checks,
but it **cannot authenticate self-attested rows or establish registry
completeness**. Even a future scientific `promote` is not a slot selection:
`ok_to_submit` remains false until a separate selector step. The historical
canary treated constants as passing at AUC .5 and substituted invalid values.
The later local safeguard rejects constant and nonfinite channels, but has not
been run on a current lane or fixed in the agreed shared template; the old
recorded pass is not proof of no leakage. The inherited
holdout's chunking also needs confirmation as whole original fault segments.
Do not silently modify a vendor copy instead of fixing the agreed shared
upstream template.

## Remaining work and next session

- Obtain the missing method-lane paragraph. Resolve the dense lattice protocol
  conflict without renaming, jittering or weakening the literal rule.
- Resolve shared-template issues [49](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/49),
  [53](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/53),
  [60](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/60) and
  [61](https://github.com/buffedlizard55-lab/GEMSDOE32/issues/61) centrally;
  publish immutable tool/cache hashes and rerun the contract. Do not retain a
  downstream evaluator fork.
- Establish an authenticated, complete registry; validate source surfaces
  **before** placement and saved final dots against every raster. Agree how to
  resolve the official null/NaN-outside wording versus any portal checks.
- Authenticate official data and use a corrected shared whole-segment buffered
  hide-and-recover evaluator. Recompute catalogue features from visible faults
  within every fold; mask known pixels exactly; run every feature solo for
  leakage. Establish a frozen same-evaluator holdout best and paired 95% CI.
- Only a genuinely new result passing all gates can be evaluated by the
  separate weekly-slot selector. Preserve the 140-character note cap and any
  applicable generative-AI disclosure. Do not assume a score or portal receipt.
- Follow **Maximize P(Win)** and **Own the Outcome**; review prior next steps
  first and complete implementation, adversarial-review and request-recheck
  passes. Historical reports are evidence to investigate, not certificates.

## Standing task and parallel protocol

The original request was not preserved verbatim in the workspace. The two
reconstructed records below are retained for continuity, without claiming that
they are an exact or complete transcript. New explicit instructions take
precedence over assumptions in older summaries.

<details><summary>Reconstructed standing brief — expand</summary>

# Standing brief (the user's prompt) — read at the start of every session

**Provenance note:** this is a normalized standing requirements record assembled from the current and prior user requests, not a verbatim chat transcript. Repeated score/site ledgers are preserved in the repository registries rather than duplicated here. Apply newer explicit instructions first; never claim this file proves the exact wording of the original chat.

## Arena Core Values (keep as focus)

- **Maximize P(Win).** Favor reproducible evidence that can raise the probability of a higher organizer-confirmed score. The prior GEMSDOE32 0.2778 is user-reported, without a verified receipt here; the owner cited multiple leaderboard benchmarks that may be stale.
- **Own the Outcome.** Negative results, blocked data, and unprovable claims are reported as such; nothing is projected as a score; irregularities are flagged for review, not hidden.

## Requirements

1. Build a project in this repository for the DrivenData DOE GEMS competition (https://www.drivendata.org/competitions/306/competition-doe-gems/) that generates a **unique, valid, submit-ready single-band GeoTIFF** (values in [0, 1]; CRS/shape/geotransform identical to the submission format, EPSG:32611) that scores higher than the previous GEMSDOE best 0.2778 and ideally above the leaderboard top.
2. **Highest urgency: a UNIQUE TIF.** Previous submissions (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36 and the wider GEMSDOE series) may be used for learning only — never copied. It must be **obvious** whether a TIF is OK to download and submit.
3. The site must show, at the very top, the download link and the OK / NOT-OK-to-submit status. An executive summary with a table for each of the nine focus sites (GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, 36): which file to download, the estimated score, and whether it is unique versus all listed GEMSDOE submissions. A subpage must explain exactly how to submit: the file, a unique name, and a short note (≤140 characters).
4. Every score number must be labelled **HOLDOUT-DTI** (with evaluator version, number of withheld positives, 95% CI) or **ORGANIZER-CONFIRMED**. A projection is never written as a score.
5. Validation must be done autonomously by the project (no human inspector / manual step); irregularities are flagged for review. The validator must guarantee values in [0, 1] and no NaN inside the footprint — an earlier submission was rejected with "Predicted values must be in range [0, 1]".
6. Give a PhD-level explanation of why and how `h33-h33-2-b2` scored 0.2778 and whether it can be beaten; use that understanding to generate the unique TIF.
7. Propose 3–5 **new geological hypotheses** (layers used, physical signature, why the targeted faults are off-catalogue, how it differs from existing submissions), ranked by expected DTI gain and cost. Validate the top candidate on a **spatially-blocked hide-and-recover holdout** before any submission slot is used. If external data are needed, name specific free official sources and check obtainability (only free, publicly available, official/verified data).
8. Follow the **PARALLEL-RUN PROTOCOL**: stay in your lane; duplicate check against the registry (rank-correlation > 0.90 or > 70% of dots within 3 px of a registry raster = duplicate → log it and stop); reuse the template tools (`evaluate_holdout.py`, `submission_writer.py`) — fix shared tools once in the template, never keep a private fork; label every number; leakage canary (any single feature with AUC > 0.90 on withheld truth = leakage until proven otherwise); budget ≤ 3 experiments or 2 hours; do **not** pick submissions (the selector step is separate and subject to the weekly cap); end with a **JSON run card** (hypothesis, mechanism, mimicking non-fault process, holdout DTI + CI, correlation/overlap vs registry, raster SHA-256, validator output, submission name + note ≤140 chars, verdict promote / negative). Negative results are deliverables.
9. No hallucinations: verify line by line from official, trusted sources and provide links for manual review. Collect and organise the competition data and knowledge into auditable tables; store a research knowledge base in the repository.
10. State limitations and access needs. There is no DrivenData login in the sandbox (the data tab redirects to login); use the Dropbox links, https://gdr.openei.org/submissions/1391, USGS GeoDAWN and the NLR rules PDF 96647 as sources.
11. A clean, simple GitHub Pages site under `docs/`.
12. Put the full prompt into the repository README (this file) and read it at the start of every session. Work on the "next steps" left by the previous session first.
13. Run three passes: (1) implement and verify, (2) review and fix bugs, (3) recheck against the request. Then create a pull request and merge it to `main`; list the remaining work and limitations for the next session.


</details>

<details>
<summary>Earlier stored prompt and protocol snapshot (reconstruction; not proven verbatim)</summary>

```text
Compete in the DrivenData DOE GEMS Prize (https://www.drivendata.org/competitions/306/competition-doe-gems/, EPSG:32611, pooled Distance-Weighted Tversky Index DTI with alpha=0.2, beta=0.8, 300 m triangular kernel; overall leaderboard high: 0.4413, secondary benchmark cited: 0.3195; user registry high: 0.2778).

Core deliverables:
1. Review repo, put the user prompt into README.md, and complete prior/next-step tasks autonomously (including competition data acquisition/preparation if missing).
2. Analyze the 9 focus sites (GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36) plus the broader GEMSDOE registry. Provide PhD-level analysis explaining why/how GEMSDOE32 (h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778) achieved the highest score and how to surpass 0.2778 (targeting >0.3195 / 0.4413).
3. Before coding experiments, propose 3-5 untried geological hypotheses naming: specific layer(s), physical signature targeted, why it captures uncatalogued faults missed by USGS/INGENIOUS rather than catalogued ones, difference vs existing repo methods, and free official data source (verified obtainable) if external data is used. Rank by expected DTI gain and implementation cost.
4. Implement and validate top candidate(s) on the spatially-blocked hide-and-recover holdout (max 3 experiments / 2 hours) under the Parallel-Run Protocol.
5. Generate a genuinely UNIQUE single-band GeoTIFF (.tif) submission passing automated validation gates (no human-inspection placeholder), with obvious download link, clear OK-TO-SUBMIT / DO-NOT-SUBMIT badge, unique filename, and <=140-char submission note.
6. Build clean GitHub Pages UI (docs/index.html + executive summary subpage explaining step-by-step contest submission) featuring per-site executive summaries for the 9 focus sites and an auditable comparison table (file to download, labeled score / holdout DTI, uniqueness status vs all GEMSDOE sites, verified official links).
7. Execute 3 full verification passes, emit the Parallel-Run Protocol JSON Run Card, create and merge a PR onto main (if git/remote available), and list remaining work and limitations.

Parallel-Run Protocol:
1. Lane & Duplication Gate: Stay in one method lane. If rank-correlation with any registry raster > 0.90 OR > 70% of dots lie within 3 px of any registry raster's dots (checked on BOTH continuous surface pre-placement AND final dots), log as duplicate and stop.
2. Reuse, Don't Rebuild: Reuse template's cached feature stack, evaluate_holdout.py, and submission_writer.py. Holdout = hide-and-recover (withhold whole fault segments + buffer, compute catalogue features strictly from visible faults, pixel-exact mask of visible faults, score pooled DTI alpha=0.2, beta=0.8, 300 m triangular kernel). Fix shared tools in template if needed; no private forks.
3. Strict Metric Labeling: Label every score as HOLDOUT-DTI (with evaluator version, withheld positive count, 95% CI) or ORGANIZER-CONFIRMED (from submission receipt). Never write an unverified projection as a score.
4. Leakage Canary: Test each feature solo on holdout first; single-feature AUC > 0.90 = leakage until proven otherwise.
5. Run Card: Conclude with one JSON card (hypothesis, mechanism, mimic_process, holdout_dti + CI, registry_correlation_overlap, raster_sha256, validator_output, submission_name, submission_note <=140 chars, verdict: promote or negative). Negative results are valid deliverables.
6. Budget: Max 3 experiments or 2 hours; do not spend a submission slot on a candidate that fails to beat holdout best.
```
</details>
