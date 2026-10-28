# GEMSDOEkarage1 — fault discovery, evidence first

> **Earlier repository review — 28 October 2026, `arena/3fa432c5-gemsdoekarage1`: DO NOT SUBMIT.** No new TIFF, experiment, holdout score, or slot selection was produced. Shared preflight was blocked: no assigned method lane, cached feature stack, or required raster inputs. Its software suite passed **240 tests**; this is not scientific validation. See the [session review](knowledge/review-arena-3fa432c5-2026-10-28.md) and [negative run card](evidence/session_run_card_arena_3fa432c5_20261028.json).

> **DO NOT SUBMIT — no eligible new GeoTIFF exists.** The two previously
> promoted research files each duplicate a registered lattice under the user's
> literal rule. No geological experiment, competition upload, or weekly-slot
> selection was made in this session. A format check is not submission approval.

[Latest three-pass review](knowledge/session-review-2026-10-28-5c261093.md) · [Decision dashboard](docs/index.html) · [Executive summary and future submission guide](docs/executive-summary.html) · [Nine-site audit](docs/data/reference-audit.json) · [Two-candidate saved-byte audit](evidence/candidate_audit_20261028.json) · [This session's negative run card](evidence/session_run_card_5c261093.json) · [Research hypotheses](docs/research.html) · [Official source register](knowledge/sources-2026-10-28.md)

## Parallel BB-STEP raster — research only, DO NOT SUBMIT

Another session generated [BB-STEP](docs/downloads/karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif)
(SHA-256 `72312302675d65cd1983239dd436412b5db1118a7c08f2a5807ef436b5536d6a`;
research note: `BB-STEP buried grav/dtb ridge; research only; DO NOT SUBMIT`).
Our independent [saved-byte audit](evidence/bbstep_independent_audit_5c261093.json)
finds **17,504 / 17,766 = 98.5253%** of dots within 3 px of the lattice, so
it fails the literal >70% duplicate stop. Its strongest final-dot overlap against
the nine pinned historical files was 2,243 / 17,766 = 12.6252% vs GEMSDOE27;
that scoped result is not a pre-placement check or complete-registry clearance.
The zero and NaN TIFF variants match the mirrored grid and are finite in [0,1]
inside its footprint, but only the NaN version is null/NaN outside it. The
mirror is not organizer-authenticated; portal acceptance is untested.

The parallel session reported exploratory **HOLDOUT-DTI 0.03179**
[0.02714, 0.03627], evaluator `gemsk-hide-recover-v1`, 60,988 positives
assigned and 60,625 scored. It used different settings from the saved TIFF,
local rather than agreed shared tools, and a fixed full-catalogue B2 control
versus fold-local candidate emissions. It is not a validated score for this
file, a fair promotion comparison or a leaderboard estimate. No owner lane
was identified and the surface comparison occurred after placement. The
[corrected review](knowledge/review-bbstep-2026-10-28.md) records these
limitations; the runner is quarantined. Two vendored tool files also differ
from their recorded pins ([integrity audit](evidence/template_integrity_20261028.json));
shared execution remains blocked pending an upstream repair.

## Earlier follow-up — session `arena/7e7b4964-gemsdoekarage1`

[Three-pass review](knowledge/session-7e7b4964-review.md) · [negative run card](evidence/session_7e7b4964_run_card.json). That session restored and reverified the 31 pinned third-party mirrors in its own runtime; their organizer provenance remains unverified and its cache is not this checkout's cache. Preflight now flags that the mirrored labels and existing-fault files have identical bytes, without claiming this alone proves leakage. The assigned lane and shared cache remain missing. No new TIFF, holdout, score estimate or slot selection was made. **Do not submit.**

## Earlier adapter review — session `ea042946` (28 October 2026)

[Three-pass review](knowledge/session-ea042946-review.md) ·
[Session run card](evidence/session_ea042946_run_card.json) ·
[Actual preflight](evidence/session_ea042946_preflight.json).
The shared-tool invocation adapter now rejects **empty and unreadable** cached
inputs as well as missing files; empty download placeholders can no longer
report readiness. This is not format or provenance validation. Verification:
**272 tests passed** (90 Rasterio pending-deprecation warnings); all 32 decision
pages rebuilt without changes. No new geological experiment, TIFF, score
estimate, or slot selection was made. **DO NOT SUBMIT.** The method lane and
all five required shared cached inputs are absent in this checkout. Existing
nine-site summaries and the four-hypothesis slate remain planning/audit
material, not evidence of a new high-scoring eligible submission.

## Earlier follow-up — session `fafb84ff`

**DO NOT SUBMIT: no new eligible TIFF or measured score.** Shared preflight now
rejects empty cached input files before execution, in addition to missing inputs
and the absent assigned lane. This is not data authentication or scientific
validation. [Three-pass review](knowledge/review-fafb84ff.md) ·
[Current preflight](evidence/preflight-fafb84ff.json) ·
[Negative run card](evidence/run-card-fafb84ff.json). Full suite: 245 passed.
The existing nine-site executive summary and four qualified hypotheses remain
research material, not submission recommendations.

## Earlier follow-up — 28 October 2026, session `arena/0404f8f1-gemsdoekarage1`

The shared-tool preflight now blocks a merely suggested template pin until a
recorded canonical assignment matches the lane, repository and immutable
commit. This is a consistency check, not authentication of the assignment,
cache, holdout or release evidence. A fresh pinned audit reproduced both
parallel candidates' lattice failures. No new TIFF, holdout score or slot was
created; **do not submit**. See the [three-pass review](knowledge/session-0404f8f1-review.md),
[reproduced audit](evidence/session_0404f8f1_parallel_audit.json) and
[negative run card](evidence/session_0404f8f1_run_card.json).

## Earlier checkout review — session `arena/43868644`

**No new eligible TIFF; do not submit.** The assigned lane and shared cached
inputs are missing. The release policy now requires an explicit GeoTIFF driver
check and fails safely on oversized numeric inputs. This is not evidence of
candidate quality or organizer acceptance. See the [three-pass review](knowledge/session-review-arena-43868644.md)
and [negative run card](evidence/run_card_arena_43868644.json). Tests: 243 passed;
no experiment, holdout score or weekly slot selection. The archived hypothesis
preregistration contains speculative gains and provenance claims that are not
verified and must not be treated as measured scores.

## Earlier review — 28 October 2026, session `arena/0fb1ec81-gemsdoekarage1`

The previously reported lattice failure was independently replayed from pinned
mirrors: 38,174/38,200 historical HMAS dots and 35,959/36,000 historical GPC-Z
dots are within 3 px. The [reassessment](evidence/reassessment_arena_0fb1_20261028.json)
is reproducible but uses a third-party footprint, not an authenticated organizer
sample. The 31 pinned mirrors were restored into ignored `data/` in a prior
review runtime; they are not tracked and are **absent from this checkout**. No
geological experiment, candidate raster, holdout score or submission was made.
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

## Latest follow-up: independent replay and freshness

A fresh 12-file hash-verified mirror replay reproduced all 72 directed
nine-site overlaps and both prior candidate audits. On 28 October at 16:29 UTC,
[all nine peer GitHub HEADs differed from their historical pins](evidence/peer_revisions_20261028.json).
A [16:40 recheck](evidence/peer_revisions_20261028_1640.json) again found all
nine changed; four HEADs moved again in that interval. This does not establish
a raster change or a cleared candidate. The site now
checks GitHub revision freshness in the browser and scheduled workflow; changed
or unavailable sources make the workflow check fail. It does not scrape
DrivenData or grant submission permission. The full review also
records a shared-metric documentation counterexample and an upstream issue
creation blocked by integration permissions. After incorporating parallel
safeguards and the BB-STEP audit, 304 tests passed (90 Rasterio
pending-deprecation warnings). No new experiment, TIFF, estimate, or slot
selection was made in this review.

## Earlier follow-up: release-gate consistency

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
report write is not a readiness pass. The current preflight also checks for a recorded canonical assignment. Neither
input presence nor an assignment assertion authenticates provenance or establishes
scientific merit, uniqueness or upload authorization.
[Three-pass follow-up review](knowledge/session-a0f0d036-review.md) ·
[Session negative run card](evidence/session_a0f0d036_run_card.json).
Full suite: **216 passed**. No new experiment, score, TIFF or slot selection.

### Earlier follow-up — session `5b69d76e`

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
### Earlier independent session review

The [three-pass session review](knowledge/session-review-arena-9ad4a8a0.md) and [negative session run card](evidence/run_card_arena_9ad4a8a0.json) record a fresh restoration of the pinned mirrors, an exact reproduction of the duplicate audit, and a fix for masked in-footprint pixels in the strict local format checker. **No new TIFF, holdout estimate, or submission-slot decision was produced.** The restored mirrors are not authenticated organizer inputs; the assigned lane, shared stack and complete registry remain unresolved. The scheduled refresh creates a workflow artifact, not a live published feed.

### Earlier independent checkout review

The [review record](evidence/session_review_2026-10-28_arena-470a3424.json)
reproduced the fail-closed software status; no geological experiment or
submission was made. Its initial preflight reported no assigned lane and lacked
the feature stack and input rasters. The inherited TIFFs already fail the
literal 3-pixel lattice-overlap gate; this is not a pre-placement uniqueness
check for a new candidate. At that checkout point, the suite had **205 passed,
0 failed, 0 skipped** (53 Rasterio deprecation warnings) and the site builder
rendered 32 pages deterministically. A later merged follow-up records 219
passing tests and strengthens preflight/gate behavior. After synchronizing that
branch with the then-current main, the complete suite passed **240 tests** (90
Rasterio/Affine pending-deprecation warnings). The final review record
[here](knowledge/session-review-final-2026-10-28.md) also documented that the
assigned lane and cached inputs were absent in that checkout, and there was no
authenticated/live leaderboard feed. The current GitHub monitor checks only
repository revisions. Neither test count is a holdout result or submission
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
   lithologic contacts or flow edges can mimic faults. Paired displacement is
   proposed, but HMAS already includes gravity-crest migration; distinctness
   from prior work is unproven.
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

An earlier session restored and rechecked **31** pinned GitHub mirrors (4 core,
12 external, 15 scored; 551,538,109 bytes); its [receipt](evidence/data_restore_verification_20261028.json)
and [manifest](registry/karage1_data_manifest.json) record their size, SHA-256
and immutable source commits. The excluded cache did not persist into this
session: only 12 reference TIFFs were freshly restored and checked for the
independent audit. Rerun restoration in a fresh environment. These hashes establish mirror consistency,
not organizer origin or data license for every derived layer. Notably the
mirrored sample's positive mask equals the mirrored labels, contrary to the
organizer's description of an all-absence sample: use it only as a grid and
footprint until official bytes are checked.

```bash
python -m pip install -r requirements.txt
# Public GitHub mirrors, not a DrivenData download:
bash scripts/download_competition_data.sh --data-dir .cache/gems_data
bash scripts/download_competition_data.sh --data-dir .cache/gems_data --verify-only
python scripts/shared_tools.py preflight        # lane and shared feature stack currently missing
python scripts/build_site.py                     # deterministic, negative decision pages
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

- Obtain the method-lane paragraph and identify one authoritative upstream
  template/cache. Resolve the dense lattice protocol conflict with the owner;
  don't evade it by renaming, jittering or weakening the rule.
- Establish an authenticated, complete registry; validate source surfaces
  **before** placement and saved final dots against every raster. Agree how to
  resolve the official null/NaN-outside wording versus any portal checks.
- Authenticate official data and use the shared whole-segment buffered
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

**Provenance note:** the original prompt was not preserved verbatim in the workspace. What follows is a reconstruction from earlier session memory, not proof that every original clause or exact word was retained. Apply these requirements together with any newer explicit user instructions; do not claim this is an original transcript.

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


## Full owner request — 28 October 2026

The following working transcription combines an [immutable prior owner brief](https://github.com/buffedlizard55-lab/GEMSDOE25/blob/a728c9f42e6298aaa5b65013806ac578f1b2a3ef/README.md) with the additions and corrections in the current request. Whitespace and the earlier source were not machine-compared with the full chat, so this is not claimed as a byte-exact transcript. Scores inside are owner-supplied claims, not verified receipts. Read this together with the current decision and the latest session review at the start of every session.

<details><summary>Expand the full standing request and historical context</summary>

````text
Review the repo.

I want to focus on  the highest scoring submissions from the following sites, GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, GEMSDOE36.  I want an executive summary on every site that is clear and obvious which is the best submission to submit to obtain a high score on the leaderboard.  It should also be unique and not an exact duplicate of any previous submission that is the same as below.  Keep iterating and testing until we have the highest scoring submission to download and submit.

We should be able to estimate the score for a submission.  I want a table in the executive summary that clearly lists what file to download, what the estimate score is, and whether it is a unique submission unlike any of the other GEMDOE sites listed below.

THE FOLLOWING IS THE HIGHEST URGENCY AND MUST BE FOLLOWED!

MUST GENERATE A UNIQUE TIF SUBMISSION FOR THE COMPETITION.  DO NOT COPY A PREVIOUS SUBMISSION UNLESS IT'S FOR LEARNING AND EDUCATION.  BUT WE MUST GENERATE A UNIQUE TIF SUBMISSION.  IT MUST BE OBVIOUS WHETHER IT IS OK TO DOWNLOAD AND SUBMIT THE GENERATED TIF SUBMISSION.

There should be an easy to download submission tif file as described by the prompt.  Read the entire prompt.  A lot of sites mention inspection only and a human inspector, but the inspection needs to be done through the project and needs to be validated for submission without human intervention.

PARALLEL-RUN PROTOCOL — read first. This session is one of several running from this same prompt.

1. LANE. Your lane is the single method paragraph below. Stay inside it. If your raster's rank-correlation with any registry raster exceeds [0.90], or more than [70%] of your dots fall within 3 px of one registry raster's dots, you have drifted into another lane: log it as a duplicate and stop. Check this on the surface before placement AND on the final dots.

2. REUSE, DON'T REBUILD. Use the template's cached feature stack, evaluate_[holdout.py](http://holdout.py) and submission_[writer.py](http://writer.py). Holdout = hide-and-recover: withhold whole fault segments with a buffer, derive every catalogue-based feature only from the visible faults, mask visible faults pixel-exactly, score pooled DTI (alpha 0.2, beta 0.8, 300 m triangular kernel). If a shared tool is wrong, fix it once in the template and report it; never keep a private fork.

3. LABEL EVERY NUMBER as HOLDOUT-DTI (evaluator version, number of withheld positives, 95% CI) or ORGANIZER-CONFIRMED (copied from a submission-page receipt). A projection is never written as a score.

4. LEAKAGE CANARY. Test each feature alone on the holdout before trusting any result. AUC above [0.90] means leakage until proven otherwise.

5. RUN CARD. End with one JSON card: hypothesis; mechanism; the named non-fault process that could mimic it; holdout DTI + CI; correlation/overlap vs registry; raster sha256; validator output (no NaN inside the footprint, values in [0,1], CRS/shape/transform match); submission name + note of at most 140 characters; verdict promote / negative. Negative results are deliverables.

6. BUDGET. Stop after [3] experiments or [2] hours. Do not pick submissions: promotion to a real slot is a separate selector step, within the weekly cap shown on the submission page.

The following sites should serve as a starting point for understanding how to generate TIF submissions.  These websites are researched, and tested and have generated TIF submissions.  But we need to generate high scoring submissions.

Here are the results from submissions into the competition, separated by ....:

WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:

[https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778

Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778?

Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition.  Must be unique submission unlike any within the GEMSDOE sites above.  Verify working line by line no hallucinations.

Current competition leaderboard GEMSDOE high score:

0.4413

WE NEED TO STUDY, ANALYZE, AND UNDERSTAND THE HIGHEST SCORE FROM THE GEMDOE SITE WHERE THE SUBMISSION TIF IS DOWNLOADED FROM WHICH IS THE FOLLOWING:

[https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778

Why and how did this get the highest score and are we able to generate a submission that scores higher than 0.2778?

Answer the question using Phd level experience, knowledge, and judgement. Then use the answer to generate a unique TIF submission into the competition.  Must be unique submission unlike any within the GEMSDOE sites above.  Verify working line by line no hallucinations.

Current competition leaderboard GEMSDOE high score:

0.4413

[https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE/docs/index.html)

gems-submission-20260925T001403Z-7f00890a: 0.1563

....

[https://buffedlizard55-lab.github.io/6GEMSDOE/](https://buffedlizard55-lab.github.io/6GEMSDOE/)

gems6_hgb88-topk03_33cec71ff0: 0.0286

....

[https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE3/docs/index.html)

pindrop-v4-nodes-20260925T152420Z-f347b70daa: 0.1193

pindrop-v4-discovery-20260925T152423Z-37f9d5b855: 0.0830

pindrop-v4-ridge-20260925T152422Z-4e03fc9705: 0.1152

....

[https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE2/docs/index.html)

gemsdoe2-dual-family-union-20260925T160406Z-f68e590f: 0.1560

....

[https://buffedlizard55-lab.github.io/GEMSDOE4/](https://buffedlizard55-lab.github.io/GEMSDOE4/)

gems-submission-20260926T163915Z-237f0063: 0.0343

....

[https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/5GEMSDOE/docs/index.html)

gems-submission-20260926T175114Z-7f00890a: 0.1563

....

[https://buffedlizard55-lab.github.io/7GEMSDOE/](https://buffedlizard55-lab.github.io/7GEMSDOE/)

lidarscarp-ridge-top2pct-36c3a3f341c8: 0.1461

....

[https://buffedlizard55-lab.github.io/8GEMSDOE/](https://buffedlizard55-lab.github.io/8GEMSDOE/)

Hedge-v2_submission: 0.1563

....

[https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE9/docs/index.html)

2314b599: 0.0107

....

[https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/11GEMSDOE/docs/index.html)

gems-structural-area06-v1: 0.0202

....

[https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/12GEMSDOE/docs/index.html)

r7-nms3-dem10-scarp_0c9199f14e62:0.1294

r7-nms3-dem10-scarp_0c9199f14e62_allfinite:0.1294

....

[https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/15GEMSDOE/docs/index.html)

gems-tso1-20260929T005627Z-conj_alteration_mag: 0.0782

....

[https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/14GEMSDOE/docs/index.html)

GEMS_r5-geom-horse-ensemble_20260929T154852Z_ccbe1de0_site_e96e942f: 0.0020

....

[https://buffedlizard55-lab.github.io/17GEMSDOE/](https://buffedlizard55-lab.github.io/17GEMSDOE/)

17GEMSDOE_F-ensemble-2pct_20260930T050626Z:0.0187

....

[https://buffedlizard55-lab.github.io/18GEMSDOE/](https://buffedlizard55-lab.github.io/18GEMSDOE/)

H19-C_20260930T212401Z_c11e495e: 0.0297

....

[https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/19GEMSDOE/docs/index.html)

h19-4-multiline-corroborated-openness-thermal-pop-20260930-691e4dfa-nan: 0.1894

h19-5-powerlaw-budget-multiline-corroborated-20260930-e27054cf-nan: 0.1922

....

[https://buffedlizard55-lab.github.io/GEMSDOE10/](https://buffedlizard55-lab.github.io/GEMSDOE10/)

h16-continuation-20260927T065521077735Z-3431b83c7c: 0.0461

h20-dem10-scarp-thin-20260927T155223039488Z-ffc91a1686: 0.0921

H25-ctx-ridge-20260927T232947704150Z-6452ae1d00: 0.1280

h28-dotted-ridge-20260928T020256236880Z-6452ae1d00: 0.1839

....

[https://buffedlizard55-lab.github.io/13GEMSDOE/](https://buffedlizard55-lab.github.io/13GEMSDOE/)

20261001_r13-lattice-s5_v2_nan-outside:0.0904

....

[https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/16GEMSDOE/docs/index.html)

h16-1-topo-geophys-baseline-ridges-20260930-df20f65e-nan: 0.1855

h18-3a-topo-geophys-x-complexity-prior-20260930-c502dfab-nan: 0.0976

h18-4-usgs-geologic-map-faults-gap-20260930-aef8f42c-nan: 0.0360

....

[https://buffedlizard55-lab.github.io/GEMSDOE21/](https://buffedlizard55-lab.github.io/GEMSDOE21/)

h19-4-reference-20260930-691e4dfa: 0.1894

....

[https://buffedlizard55-lab.github.io/20GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/20GEMSDOE/docs/index.html)

h20-1-sarnnpu-powerlaw-pi0363-tilt-wingcrack-20260930-be0e8f6b-nan: 0.1890

h20-5-continuous-pu-proxy-unverified-20260930-824ce73a-nan: 0.1859

....

[https://buffedlizard55-lab.github.io/GEMSDOE22/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE22/docs/index.html)

h23-a-dti-optimal-emission-6pct-20261002-e2ec4b49-nan: 0.1002

h23-b-dti-optimal-emission-10pct-20261002-86176698-nan: 0.0748

....

[https://buffedlizard55-lab.github.io/GEMSDOE23/](https://buffedlizard55-lab.github.io/GEMSDOE23/)

h30-arrangement-matched-habitat-20261002-0d4e02e8-nan: 0.1352

....

[https://buffedlizard55-lab.github.io/GEMSDOE24/](https://buffedlizard55-lab.github.io/GEMSDOE24/)

h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan: 0.2477

....

[https://buffedlizard55-lab.github.io/GEMSDOE25/](https://buffedlizard55-lab.github.io/GEMSDOE25/)

dotted-h19-5-d2-8-20261002-e56ea318af89-nan: 0.2600

....

[https://buffedlizard55-lab.github.io/GEMSDOE26/](https://buffedlizard55-lab.github.io/GEMSDOE26/)

dilcond-oof-v1-20261003-47629f496133-nan: 0.1223

....

[https://buffedlizard55-lab.github.io/GEMSDOE27/](https://buffedlizard55-lab.github.io/GEMSDOE27/)

topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan: 0.2449

....

[https://buffedlizard55-lab.github.io/GEMSDOE30/](https://buffedlizard55-lab.github.io/GEMSDOE30/)

d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca: 0.2600

....

[https://buffedlizard55-lab.github.io/GEMSDOE31/docs/](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/)

h27-4-solo-d28-20261004-8acb75e1-nan:0.2708

....

[https://buffedlizard55-lab.github.io/GEMSDOE33/](https://buffedlizard55-lab.github.io/GEMSDOE33/)

h33d-analog-tip-stepover-r30-20261004-cb490425926e: 0.2632

....

[https://buffedlizard55-lab.github.io/GEMSDOE34/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE34/docs/index.html)

h34-scatter-q50-arr-matched-20261004T223317Z: 0.0778

....

[https://buffedlizard55-lab.github.io/GEMSDOE35/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE35/docs/index.html)

h35-06-aaa86efb25-20261004T225420098147Z-candidate: 0.0418

....

[https://buffedlizard55-lab.github.io/GEMSDOE36/docs/](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/)

anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros: 0.2750

....

[https://buffedlizard55-lab.github.io/GEMSDOE37/](https://buffedlizard55-lab.github.io/GEMSDOE37/)

h6-physics-dotted-80k-20261005T055000Z-0bef9211631c: 0.1193

....

[https://buffedlizard55-lab.github.io/GEMSDOE38/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE38/docs/index.html)

D-step-3p0-07pct-tipProt-20261005-ecfbf59e2b48-zero: 0.0763

....

[https://buffedlizard55-lab.github.io/GEMSDOE42/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE42/docs/index.html)

xscale-worm-persistence-20261006T000541Z-nan: 0.0581

....

[https://buffedlizard55-lab.github.io/GEMSDOE43/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE43/docs/index.html)

sup01-hgb21-sep40-n40000-20261006-bc2e4e9a8d6f-nan: 0.0424

....

[https://buffedlizard55-lab.github.io/GEMSDOE45/](https://buffedlizard55-lab.github.io/GEMSDOE45/)

h51-km-faultzone-20261006-zeros: 0.0106

....

[https://buffedlizard55-lab.github.io/GEMSDOE49/](https://buffedlizard55-lab.github.io/GEMSDOE49/)

gate_ortho_w0.25-40k-20261006T213721Z-nan: 0.2376

....

[https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778

....

[https://buffedlizard55-lab.github.io/GEMSDOE28/](https://buffedlizard55-lab.github.io/GEMSDOE28/)

h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan: 0.2708

h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan: 0.2649

h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan: 0.2710

h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan: 0.2707

....

[https://buffedlizard55-lab.github.io/GEMSDOE29/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE29/docs/index.html)

efd28-repro-20261003-1cc7dc534d51-nan: 0.2600

repo-c0-habitat-emission-20261003-a4d439b07426-nan: 0.0041

sgmc-off-catalogue-44k-20261003-c8dcd780e3fd-nan: 0.0512

wormrank-d28-20261003-59dcaf6dd11d-zeros:0.2560

wormsurv-filter-20261003-921f10960d6e-zeros: 0.0532

xfit-c0-habitat-20261003-ca879db0089a-zeros:0.0439

xfit-h41-union-qfaults-20261003-9edb34b99e3a-zeros: 0.0356

....

[https://buffedlizard55-lab.github.io/GEMSDOE46/](https://buffedlizard55-lab.github.io/GEMSDOE46/)

r11f-scarp-radiometric-fusion-00e049b51218-zeros:0.1589

r12-scarp-rad-concordance-23e807e2de9f-zeros: 0.0843

....

[https://buffedlizard55-lab.github.io/GEMSDOE39/](https://buffedlizard55-lab.github.io/GEMSDOE39/)

h40-e-disc-h40e-30k-zeros: 0.0339

....

[https://buffedlizard55-lab.github.io/GEMSDOE40/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE40/docs/index.html)

h8-euler-lineament-depthcluster-20261006-785c4f5d5ce1: 0.0355

h8-euler-lineament-depthcluster-20261006-785c4f5d5ce1-hard: 0.0397

h45-eulerdepthreadcluster-20261006-f28e5cff6826-zeros: 0.0984

....

[https://buffedlizard55-lab.github.io/GEMSDOE41/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE41/docs/index.html)

h42-submission-primary: 0.0245

....

[https://buffedlizard55-lab.github.io/GEMSDOE44/docs/](https://buffedlizard55-lab.github.io/GEMSDOE44/docs/)

h46-twostageAB_20261006T160000Z_b0cfe956-zeros: 0.0715

....

[https://buffedlizard55-lab.github.io/GEMSDOE47/](https://buffedlizard55-lab.github.io/GEMSDOE47/)

h60-lidarscarp-s2p0-20261007-nanoutside: 0.0430

....

[https://buffedlizard55-lab.github.io/GEMSDOE48/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE48/docs/index.html)

h59-cover-ds-belief-b2xh33d-20261008T184547Z-b79c4c61d8d8: 0.2296

....

[https://buffedlizard55-lab.github.io/GEMSDOE50/](https://buffedlizard55-lab.github.io/GEMSDOE50/)

h59-sharpened-scarp-scatter-90k-20261007T171954Z-allfinite: 0.0764

....

[https://buffedlizard55-lab.github.io/GEMSDOE51/](https://buffedlizard55-lab.github.io/GEMSDOE51/)

h53-twostage-20261008T040951Z-9a0b32c871: 0.1047

....

[https://buffedlizard55-lab.github.io/GEMSDOE52/](https://buffedlizard55-lab.github.io/GEMSDOE52/)

h97b-candidate: 0.0856

....

[https://buffedlizard55-lab.github.io/GEMSDOE53/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE53/docs/index.html)

h8-tiprelay-ridgeconcord-pr2-n80000-20261009-49bec522-zeros: 0.0159

....

[https://buffedlizard55-lab.github.io/GEMSDOE54/docs/](https://buffedlizard55-lab.github.io/GEMSDOE54/docs/)

h54c-manifest-edge-20261009T025732Z-73454bc5:0.0449

....

[https://buffedlizard55-lab.github.io/55GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/55GEMSDOE/docs/index.html)

tensor_full-n16000-sep3-20261009T211747Z-nan: 0.0290

....

[https://buffedlizard55-lab.github.io/56GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/56GEMSDOE/docs/index.html)

h56-final-dotted-ridge-d2p8-20261009T190421Z:0.0658

....

[https://buffedlizard55-lab.github.io/57GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/57GEMSDOE/docs/index.html)

h57r-joint-strata-38000dots-20261010T214547Z-00cf5b2066f1-zeros: 0.0254

....

[https://buffedlizard55-lab.github.io/58GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/58GEMSDOE/docs/index.html)

ml-binary-ridge-20261012T000000Z: 0.0180

....

[https://buffedlizard55-lab.github.io/59GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/59GEMSDOE/docs/index.html)

h59j-coherence-consensus-dotted-20261011T043000Z: 0.0499

....

[https://buffedlizard55-lab.github.io/60GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/60GEMSDOE/docs/index.html)

h73-chi-coherent-corridor-12000-20261011T195818Z-zeros: 0.0351

....

[https://buffedlizard55-lab.github.io/61GEMSDOE/docs/index.html](https://buffedlizard55-lab.github.io/61GEMSDOE/docs/index.html)

h61a-basement-step-20000dots-20261011T012029Z-eb2ae4bb024b-zeros: 0.0009

h61o-vardepth-none-40000dots-20261011T160711Z-28d4fac611ea-zeros-zeros:0.0751

....

[https://buffedlizard55-lab.github.io/62GEMSDOE/](https://buffedlizard55-lab.github.io/62GEMSDOE/)

datum-lahontan-strain-gauge-defensible-440dots-zeros: 0.0000

....

[https://buffedlizard55-lab.github.io/GEMSDOE63/](https://buffedlizard55-lab.github.io/GEMSDOE63/)

cvarlw-thin-s3p17-54864-20261011T220606Z-c58f60c4-zeros: 0.2303

....

[https://buffedlizard55-lab.github.io/GEMSDOE64/](https://buffedlizard55-lab.github.io/GEMSDOE64/)

h64-lidar-scarp-cv-20261011T220000Z:0.0383

....

[https://buffedlizard55-lab.github.io/GEMSDOE65/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE65/docs/index.html)

sar-em-propensity-half-20261011T223500Z-5e4660cd-zeros:0.0431

....

[https://buffedlizard55-lab.github.io/GEMSDOE66/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE66/docs/index.html)

gems66-lidar03-cvretrain-reliefdecile-37654dots-20261020T190152Z-zeros:0.1152

....

[https://buffedlizard55-lab.github.io/GEMSDOE67/](https://buffedlizard55-lab.github.io/GEMSDOE67/)

h67a-orientip-lane-29447dots-20261012T021226Z-allfinite:0.0356

ovtr-ml-cover-tau3p0-20261012-nan:0.1426

....

[https://buffedlizard55-lab.github.io/GEMSDOE68/](https://buffedlizard55-lab.github.io/GEMSDOE68/)

gems68-autoctx-s3-strands-35000dots-20261020T210000Z-849a0f04-nan:0.0437

gems68-autoctx-s3-strands-35000dots-20261020T210000Z-849a0f04-zeros: 0.0437

....

[https://buffedlizard55-lab.github.io/GEMSDOE69/](https://buffedlizard55-lab.github.io/GEMSDOE69/)

gems69-joint-relayramp-pullapart-38669-20261020T201504Z-f29b6df5:0.0053

....

[https://buffedlizard55-lab.github.io/GEMSDOE70/](https://buffedlizard55-lab.github.io/GEMSDOE70/)

gems70-p5-dual-submod300-oof38k-20261020:0.2478

....

[https://buffedlizard55-lab.github.io/GEMSDOE71/](https://buffedlizard55-lab.github.io/GEMSDOE71/)

gems71-hydro-conduit-38800-20261020T120000Z-zeros: 0.0558

....

[https://buffedlizard55-lab.github.io/GEMSDOE72/](https://buffedlizard55-lab.github.io/GEMSDOE72/)

gemsdoe72-h72-1-sgmc-offcatalogue-20261020T195456Z-6e6525e5-zeros: 0.0492

....

[https://buffedlizard55-lab.github.io/GEMSDOE73/](https://buffedlizard55-lab.github.io/GEMSDOE73/)

gems73-h73-mcsc-seamfree-blakely-37654dots-20261021T073716Z-b27ac445-zeros: 0.1917

....

[https://buffedlizard55-lab.github.io/GEMSDOE74/](https://buffedlizard55-lab.github.io/GEMSDOE74/)

gemsdoe74-triregime-radon-piedmont-37654-20261021T051000Z-zeros:0.0669

....

[https://buffedlizard55-lab.github.io/GEMSDOE75/](https://buffedlizard55-lab.github.io/GEMSDOE75/)

gems75-trlt-radon-loco-ridge-20261021-zeros:0.1627

....

[https://buffedlizard55-lab.github.io/GEMSDOE76/](https://buffedlizard55-lab.github.io/GEMSDOE76/)

gems76_h76_3_geotherm_tilt_axial_submod_20261021_zeros:0.1555

gems76-ptcf-tiltworm-submod39k-20261021T034000Z-6316481d-zeros:0.2343

....

[https://buffedlizard55-lab.github.io/GEMSDOE77/](https://buffedlizard55-lab.github.io/GEMSDOE77/)

gems85-h85-edti-collar35-skel-r33-20261021-d97b248e-zeros:0.0964

....

[https://buffedlizard55-lab.github.io/GEMSDOE78/](https://buffedlizard55-lab.github.io/GEMSDOE78/)

gems78-h78sigx-fuse-b5-44090dots-20261022T021932Z-zeros:0.1564

....

[https://buffedlizard55-lab.github.io/GEMSDOE79/](https://buffedlizard55-lab.github.io/GEMSDOE79/)

gems79-tilt-ring-100000dots-20261022T212135Z-50a5d7498c71-zeros:0.0005

....

[https://buffedlizard55-lab.github.io/GEMSDOE80/](https://buffedlizard55-lab.github.io/GEMSDOE80/)

gemsdoe80-h80g-choquet-tworegime-20261022T000000Z-zeros:0.0943

....

[https://buffedlizard55-lab.github.io/GEMSDOE81/](https://buffedlizard55-lab.github.io/GEMSDOE81/)

gems81-cont-poisson44090-buf2-20261021T233115Z-42223e10-zeros:0.0041

....

[https://buffedlizard55-lab.github.io/GEMSDOE82/](https://buffedlizard55-lab.github.io/GEMSDOE82/)

gemsdoe82-h82-submodular-punoisyor-20261021T235456Z-fe137199-zeros:0.1886

....

[https://buffedlizard55-lab.github.io/GEMSDOE83/](https://buffedlizard55-lab.github.io/GEMSDOE83/)

gems83-h83-gvcd-dink300-37654dots-20261021-1a373694-zeros:0.0573

....

[https://buffedlizard55-lab.github.io/GEMSDOE84/](https://buffedlizard55-lab.github.io/GEMSDOE84/)

gems84-h84-kthm-tworegime-58000px-20261022T235900Z-zeros:0.0132

....

[https://buffedlizard55-lab.github.io/GEMSDOE85/](https://buffedlizard55-lab.github.io/GEMSDOE85/)

gemsdoe85-hjcd-ventbridge-submod-zeros: 0.1110

....

[https://buffedlizard55-lab.github.io/GEMSDOE86/](https://buffedlizard55-lab.github.io/GEMSDOE86/)

:

....

[https://buffedlizard55-lab.github.io/GEMSDOE87/](https://buffedlizard55-lab.github.io/GEMSDOE87/)

h87-h87-cmgep-20261022T060000Z-8f394f43:0.0500

....

[https://buffedlizard55-lab.github.io/GEMSDOE88/](https://buffedlizard55-lab.github.io/GEMSDOE88/)

:

....

[https://buffedlizard55-lab.github.io/GEMSDOE89/](https://buffedlizard55-lab.github.io/GEMSDOE89/)

gemsdoe89-bh-rtp-habc-20261024-d7e1507c-zeros:0.0301

....

[https://buffedlizard55-lab.github.io/GEMSDOE90/](https://buffedlizard55-lab.github.io/GEMSDOE90/)

gems90-cnc-35000dots-20261024T084324Z:0.0749

....

[https://buffedlizard55-lab.github.io/GEMSDOE91/](https://buffedlizard55-lab.github.io/GEMSDOE91/)

gems91-s17-cwpc-e3-37654dots-20261025T150000Z-4d124f1d-zeros:0.1367

gems91-s17-lftg-20261025T160014Z-7b6bf90844-zeros:0.1823

gems91-S18-UNIQUE-curvtilt-20000dots-20261025T182858Z-29db2405:0.0435

gems91-s22-omtj-e1-20261026-a99b8923f0-zeros:0.0298

....

[https://buffedlizard55-lab.github.io/GEMSDOE92/](https://buffedlizard55-lab.github.io/GEMSDOE92/)

gemsdoe92-listricdip-updip50-37654-20261025T190000Z-zeros:0.0255

lbmc1-35801dots-20261027-89a660f6:

....

[https://buffedlizard55-lab.github.io/GEMSDOE24/](https://buffedlizard55-lab.github.io/GEMSDOE24/)

h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan: 0.2477

gems24-gvc1-negative-geothermal-lineament-submod-20261025-abe8e51c719d-zeros:0.0859

....

[https://buffedlizard55-lab.github.io/GEMSDOE25/](https://buffedlizard55-lab.github.io/GEMSDOE25/)

dotted-h19-5-d2-8-20261002-e56ea318af89-nan: 0.2600

gems25-h66-mgd-flank-sapd3-0-k3p5-20261025-da617550a0e9-zeros:0.0742

....

[https://buffedlizard55-lab.github.io/GEMSDOE27/](https://buffedlizard55-lab.github.io/GEMSDOE27/)

topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan: 0.2449

gems27-h29-hydrothermal-piedmont-celf-20261025-511898747886-allfinite:0.2190

gems27-h31-drcg-wl-celf28-20261026-cf8e1bbef244-allfinite:0.2250

....

[https://buffedlizard55-lab.github.io/GEMSDOE28/](https://buffedlizard55-lab.github.io/GEMSDOE28/)

h27-4-r1-solo-d2-8-20261003-8acb75e1f2cc-nan: 0.2708

h32-1-prethin-tip-euler-d2-8-20261003-31e35eee884e-nan: 0.2649

h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan: 0.2710

h38-1-hf-euler-r30-r1-20261003-56a9f473edc7-nan: 0.2707

gems28-s18-mxtp-20261025-3e95505c011a-allfinite:0.0217

gems28-s21-puhgb-20261026-16bbf281ba9b-allfinite:0.0206

....

[https://buffedlizard55-lab.github.io/GEMSDOE30/](https://buffedlizard55-lab.github.io/GEMSDOE30/)

d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca: 0.2600

gems30-MSDB1-edge44090-20261025-e7856ec3f14a:0.1462

....

[https://buffedlizard55-lab.github.io/GEMSDOE31/docs/](https://buffedlizard55-lab.github.io/GEMSDOE31/docs/)

h27-4-solo-d28-20261004-8acb75e1-nan:0.2708

....

[https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html)

h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros: 0.2778

....

[https://buffedlizard55-lab.github.io/GEMSDOE33/](https://buffedlizard55-lab.github.io/GEMSDOE33/)

h33d-analog-tip-stepover-r30-20261004-cb490425926e: 0.2632

gemsdoe33-s33-seisdil-strain-seismicity-37654-20261026-3463540a7e02-zeros:0.0963

....

[https://buffedlizard55-lab.github.io/GEMSDOE36/docs/](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/)

anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros: 0.2750

gemsdoe36-kpl36-exp3-20261026-fc869911e88c-zeros: 0.1647

....

[https://kanlerxz87-cyber.github.io/KANLERGEMSDOE3/docs/index.html](https://kanlerxz87-cyber.github.io/KANLERGEMSDOE3/docs/index.html)

kanlergemsdoe3-h-k3-1-cadg-submod-exp-k3-3-oof8f-37654-20261026-f0565e6d10f9-zeros:

....

[https://kanlerxz87-cyber.github.io/KANLERGEMSDOE1/](https://kanlerxz87-cyber.github.io/KANLERGEMSDOE1/)

:

....

[https://kanlerxz87-cyber.github.io/KANLERGEMSDOE2/](https://kanlerxz87-cyber.github.io/KANLERGEMSDOE2/)

kanlergems2-htcads-exp-2-37654dots-20261026T235227Z-11a2f251-zeros:0.1218

....

[https://eugboogieman123-ops.github.io/EUGGEMSDOE3/](https://eugboogieman123-ops.github.io/EUGGEMSDOE3/)

:

....

[https://eugboogieman123-ops.github.io/EUGGEMSDOE2/](https://eugboogieman123-ops.github.io/EUGGEMSDOE2/)

:

....

[https://eugboogieman123-ops.github.io/EUGGEMSDOE1/](https://eugboogieman123-ops.github.io/EUGGEMSDOE1/)

:

....

[https://wingbangboozle1-lang.github.io/WBGGEMSDOE3/docs/index.html](https://wingbangboozle1-lang.github.io/WBGGEMSDOE3/docs/index.html)

wbg3-h3pack-34k-20261027T174337Z-zeros:0.0443

wbggemsdoe3-skarpline-union-20261027-610acf58-zeros:

....

[https://wingbangboozle1-lang.github.io/WBGGEMSDOE2/docs/](https://wingbangboozle1-lang.github.io/WBGGEMSDOE2/docs/)

wbg2-offcatalogue-density-36k-20261027:0.0262

....

[https://wingbangboozle1-lang.github.io/WBGGEMSDOE1/docs/index.html](https://wingbangboozle1-lang.github.io/WBGGEMSDOE1/docs/index.html)

:

....

[https://ginnymcfiner23-ux.github.io/GINNYGEMSDOE3/](https://ginnymcfiner23-ux.github.io/GINNYGEMSDOE3/)

:

....

[https://ginnymcfiner23-ux.github.io/GINNYGEMSDOE2/](https://ginnymcfiner23-ux.github.io/GINNYGEMSDOE2/)

:

....

[https://ginnymcfiner23-ux.github.io/GINNYGEMSDOE1/](https://ginnymcfiner23-ux.github.io/GINNYGEMSDOE1/)

:

....

[https://karagemop466-tech.github.io/GEMSDOEkarage3/](https://karagemop466-tech.github.io/GEMSDOEkarage3/)

:

….

[https://karagemop466-tech.github.io/GEMSDOEkarage2](https://karagemop466-tech.github.io/GEMSDOEkarage2)

:

….

[https://karagemop466-tech.github.io/GEMSDOEkarage1](https://karagemop466-tech.github.io/GEMSDOEkarage1)

hmas-sinter-dualcover-sep29-20261027T220000Z:

….

[https://apartanish22-droid.github.io/ApartGEMSDOE2/](https://apartanish22-droid.github.io/ApartGEMSDOE2/)

:

….

[https://apartanish22-droid.github.io/ApartGEMSDOE3](https://apartanish22-droid.github.io/ApartGEMSDOE3)

cfkc-dhc-37654-20261027T215000Z-9dedadfc:

….

[https://apartanish22-droid.github.io/ApartGEMSDOE1](https://apartanish22-droid.github.io/ApartGEMSDOE1)

udth-submod-e3-20261027-50e7b334:0.0525

….

[https://sassnarep3-star.github.io/GEMSDOESASS3](https://sassnarep3-star.github.io/GEMSDOESASS3)

lwst-geoconduit-dual37654-20261027T120000Z-a9ad3386:

….

[https://sassnarep3-star.github.io/GEMSDOESASS2](https://sassnarep3-star.github.io/GEMSDOESASS2)

:

….

[https://sassnarep3-star.github.io/GEMSDOESASS1](https://sassnarep3-star.github.io/GEMSDOESASS1)

swgb-hrv2-44090dots-20261027T122104Z-f9b3f764:

….


I think it makes sense that in order for a submission to be validated that it needs to pass certain high scoring validation gates before confirming whether a file is unique and can be submitted for scoring.

The following is the leaderboard for the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)

See below for more links and information related to the competition:

[https://github.com/drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution)

[https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)

[https://gbcge.org/current-projects/ingenious/](https://gbcge.org/current-projects/ingenious/)

[https://epsg.io/32611](https://epsg.io/32611)

[https://en.wikipedia.org/wiki/Tversky_index](https://en.wikipedia.org/wiki/Tversky_index)

We need to quickly look at the results and results from the GEMSDOE websites above.

Before implementing, generate 3–5 candidate geological hypotheses we haven't tried yet, each naming: the specific layer(s) involved, the physical signature being targeted (e.g., an edge-detection or curvature transform), why it should catch a fault missing from the USGS/INGENIOUS catalogue rather than one already in it, and how it differs from anything already implemented in this repo. Rank them by expected DTI improvement and implementation cost. Validate the top candidate on our spatially-blocked holdout set before touching a weekly submission slot — do not spend a submission slot on an idea that hasn't beaten the current holdout best. If a candidate can't be validated without new external data, name the specific free, official source needed and check it's obtainable before proposing the idea as viable.

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.

Verify no hallucinations.

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

We have a good understanding of how our hypothesis, methodology, calculations, analysis are done so we should be able to figure out a way to score higher on the leaderboard using previous results and scoring that we have across the sites listed above.  We need to come up with distinct and unique strategies to score higher in this competition leaderboard.  We need to start doing heavy and deep research into the part of the project that matters the most, which is the scientific discovery of geothermal vents.  We should store all of our information and knowledge that we can gather from official verified sources.  This will serve as a starting point for other projects as well.  We need to think outside the box but still be grounded in proper scientific research, we are ultimately aiming for a top prize that many others are competing for.  So it's important to be contrarian but be smart about it.  We need to find sources of data that others are over looking or areas of the project when it comes to geothermal vents.  We need to do deep research and critical thinking and come up with new hypothesis to test.

0.3195	is the highest score right now so we need to design a new strategy, research, testing, analyzing, and generating submission system than the current website.  It should be unique, take unique approaches to generating a submission that can score higher than 0.3195.

Put this prompt into the repo readme and read it everytime we work on the project as a starting point to make sure we are building what we are aiming for and have a strong base to continue building and improving on making something useful for everyday use.  It should solve the problem of having to manually check everything ourselves and having an up to date current feed.

Review the repo.

The following is taken from the Arena AI team and I think it makes a good point on building a successful project, so let's keep the Core Values and Own the Outcome as a focal point when building, developing, researching, suggesting upgrades, and implementing the work.

Our Core Values

Maximize P(Win)

“Maximize the Probability of Winning”: our decision making framework. In every decision, we weigh tradeoffs, assess risk, and choose the path that maximizes the probability that Arena succeeds. We set aside our emotions and make tough decisions in order to maximize P(Win). “Maximize P(Win)” frees us from constraints and clarifies that we must put Arena first.

Own the Outcome

We own results end to end — not just our individual slice of the work. When problems arise and we have the means to act, we do so without waiting for permission or assignment. We treat failure and success as signals and use them to improve. At Arena, we stay accountable to the final outcome.

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.



Verify no hallucinations.

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

We need to focus on being able to generate a submission into the competition.

The site should be able to generate a TIF file that is required for submission.  It should be as easy as download to click a File to submit into the competition.  This needs to be in the executive summary or the very beginning of the site.  it should be obvious when you visit the site.

I tried to submit the document that i downloaded from the site but it returned this error on the submission form:

"Predicted values must be in range [0, 1]"

Also we need to give it a unique name and A short comment to help you or your team tell submissions apart later e.g. clustering with k=25

Here is the submission page when i click submit file

New submission

File to submitNo file chosen

You can submit a single-band GeoTIFF (.tif) file, or a .zip file containing a single GeoTIFF, with your predictions. It must match the submission format's CRS, shape, and geotransform. You may wish to review the competition rules first.

Note (optional)

A short comment to help you or your team tell submissions apart later e.g. clustering with k=25

Create a executive summary subpage that explains exactly how to make a submission into the contest.

Work on the next steps from the previous sessions first.

The goal of this project is to place top of the leaderboard in this competition.  The following is the competition:

[https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)

We need to create a project that can compete and place top of the leaderboard.  We need to understand the problem, collect all the data and organize it into a clean easily auditable table with official verified links for manual verification.

This is the guidelines we need to follow.[https://www.drivendata.org/competitions/306/competition-doe-gems/](https://www.drivendata.org/competitions/306/competition-doe-gems/)

Get familiar with the problem through the overview and problem description,[https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/). You might also want to reference additional resources available on the about page,[https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/).

Download the data from the data,[https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/), tab.

Create and train your own model. This reference solution,[https://github.com/drivendataorg/gems-prize-reference-solution](https://github.com/drivendataorg/gems-prize-reference-solution) implements a simple approach.

Use your model to generate predictions that match the submission format.

Tell me what are you limitations and what you need access to during this project.  We will need to find free publicly available sources and data from official and verified sources if we are to use 3rd party or external data.

this pdf outlines how submissions must be entered into the competition.

[https://docs.nlr.gov/docs/fy26osti/96647.pdf](https://docs.nlr.gov/docs/fy26osti/96647.pdf)

You must be able to do your own research, deep research, scientific literature research and organize the knowledge so that we can critically think through the problem and generate a solution through scientific and free publicly available information.  this must be done autonomously and must be constantly reviewed and improved upon.  Provide suggestions and improvements and implement them.

❌ No DrivenData auth → cannot auto-download training_features.tif, labels.tif, sample_submission.tif, 1m_DEM_links.csv from [https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (verified redirect to login)

See below for links from the above site.  See attached files for links from the above site.

[https://gdr.openei.org/submissions/1391](https://gdr.openei.org/submissions/1391)

Download competition data from [https://www.drivendata.org/competitions/306/competition-doe-gems/data/](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (requires login) to data/

See links below for competition data:

[https://www.dropbox.com/scl/fi/aemhtutjgcp6tr3tint94/GEMS_96647.pdf?rlkey=rek210cj2smnmzb8n0sla1vmd&amp;st=wz4kofki&amp;dl=0](https://www.dropbox.com/scl/fi/aemhtutjgcp6tr3tint94/GEMS_96647.pdf?rlkey=rek210cj2smnmzb8n0sla1vmd&st=wz4kofki&dl=0)

[https://www.dropbox.com/scl/fi/6rgvnuady818ol8yqgis4/example_submission.tif?rlkey=kbykilvau066xuogoosbf4cq8&amp;st=8junzdyw&amp;dl=0](https://www.dropbox.com/scl/fi/6rgvnuady818ol8yqgis4/example_submission.tif?rlkey=kbykilvau066xuogoosbf4cq8&st=8junzdyw&dl=0)

[https://www.dropbox.com/scl/fi/t7fyt03qdh9egyme0itwo/existing_faults.tif?rlkey=yiao96uluqdkipf0h5vju71jf&amp;st=rnino7ya&amp;dl=0](https://www.dropbox.com/scl/fi/t7fyt03qdh9egyme0itwo/existing_faults.tif?rlkey=yiao96uluqdkipf0h5vju71jf&st=rnino7ya&dl=0)

[https://www.dropbox.com/scl/fi/3vz9o0wwavi26xaeoxlwr/gems-geodawn-numerical-features.tif?rlkey=je8d8fepqfbst9lnwsq9rkplu&amp;st=zj1lag1r&amp;dl=0](https://www.dropbox.com/scl/fi/3vz9o0wwavi26xaeoxlwr/gems-geodawn-numerical-features.tif?rlkey=je8d8fepqfbst9lnwsq9rkplu&st=zj1lag1r&dl=0)

[https://www.dropbox.com/scl/fi/ig0mban712ns1atphgphe/Digital-elevation-model-links-JSON.pdf?rlkey=zm77f1vbtt2if8hlruymptnu3&amp;st=srhhir10&amp;dl=0](https://www.dropbox.com/scl/fi/ig0mban712ns1atphgphe/Digital-elevation-model-links-JSON.pdf?rlkey=zm77f1vbtt2if8hlruymptnu3&st=srhhir10&dl=0)

Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.

Verify no hallucinations.

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

Site creation

Create a github page for this repo that has clean ui, user friendly, simple and easy to use.  It should be organized and clean.

It should include all relevant information in an easy to read format with official verified links as sources for review.  Work line by line verify everything no hallucinations.

**The single remaining blocker to training is data placement**: run `bash scripts/download_competition_data.sh` on any unrestricted machine into `data/`, then `python scripts/prepare_data.py` — after that the full train→inference→validate pipeline is ready to run (GPU needed for training; metric/losses/validation all verified working here on CPU).

you need to complete the above task by yourself.  Work line by line verifying from official verified trusted sources, provide links for manual review.  There should be no manual input, work on your own to complete tasks.  Flag any irregularities for review.  No hallucinations.

Verify no hallucinations.

The goal of this project is to get a full list that follow our requirements.  No hallucinations.  Verify line by line.

Run this task through multiple passes.

Pass 1: Implement the task completely and verify the result.

Pass 2: Review your work for bugs, missing requirements, incorrect assumptions, and edge cases. Fix everything you find.

Pass 3: Re-check the entire implementation against the original request. Improve accuracy, reliability, completeness, and code quality. Fix any remaining issues.

Do not stop after the first pass. Each pass must build on the previous one. Before finishing, verify that the final result fully satisfies the original request.  Work line by line verify everything no hallucinations.

Go ahead and create a pull request and then merge the pull request onto the main. Make suggestions for what work still needs to be done and any limitations that is in the way of a successful project.  It should be worked on in this next session or the next session.  Work line by line verify everything no hallucinations.
````
</details>
