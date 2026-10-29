# GEMSDOEkarage1 — Fault Discovery, Evidence First

**Latest review (29 October 2026):** [repository review, three-pass verification, and run card](knowledge/review-arena-291ca728-2026-10-29.md). No candidate is cleared; this review fixed a syntax error in a quarantined runner, but the assigned lane/template, authenticated data, and duplicate gates remain blockers. Local pytest: 352 passed, 5 failed; CI checks failed. See review for exact failures.

**Latest mainline session:** [Three-pass review and release-gate hardening](knowledge/session-review-arena-400355af.md). No new submission is cleared; the assigned lane, authoritative template, data and complete registry remain unresolved.
> **Session `arena/cf677bd7`: NEGATIVE / DO NOT SUBMIT** — see [session review](knowledge/session-review-arena-cf677bd7.md) and [run card](evidence/session_cf677bd7_run_card.json). 305 tests pass; no new TIF (lane unassigned, lattice gate blocks champion-sized rasters); nine-site table in the review.
>
> **DO NOT SUBMIT — no candidate has been cleared for competition upload.**
> **New this session (`147b0f11`): a unique, format-valid DIPDUAL GeoTIFF was generated**
> (`karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif`, discrete-unique vs 24 audited rasters)
> **but failed its preregistered holdout gates — research download only, do not submit it.**
> The separately generated BB-STEP research GeoTIFF is unique versus the nine focus-site rasters but fails the literal 3-pixel lattice-overlap rule (98.5253%). Do not submit it. The older CDA1 archive is a synthetic demonstrator whose holdout routine returned hard-coded numbers; its reported DTI is invalid and is not a measurement. All 21 primary and secondary focus-site files audited in this repository also fail the literal lattice gate. Format validation is necessary but not submission approval.

## Standing prompt (read at the start of every session)

**Competition.** DrivenData DOE GEMS prize — https://www.drivendata.org/competitions/306/competition-doe-gems/ — single-band GeoTIFF, values in [0, 1], CRS/shape/geotransform identical to the submission format (EPSG:32611).

**Core values.** Maximize P(Win); Own the Outcome. Report negative results, blocked data, and unprovable claims honestly; nothing is projected as a score; irregularities are flagged, not hidden.

**Requirements (full reconstruction in `docs/standing-prompt.md`):**
1. Build an auditable workflow that generates a **unique, valid** single-band GeoTIFF; prior GEMSDOE submissions (24, 25, 27, 28, 30, 31, 32, 33, 36 and the wider series) are for learning only — never copied.
2. **Highest urgency: a UNIQUE TIF.** It must be **obvious** whether a TIF is OK to download and submit. The site top shows the download link and the OK / NOT-OK-to-submit status.
3. Executive summary table per focus site: file to download, labeled number, uniqueness versus all listed GEMSDOE submissions; a how-to-submit subpage (file, unique name, note ≤ 140 characters).
4. Every number labeled **HOLDOUT-DTI** (evaluator, withheld positives, 95% CI) or **ORGANIZER-CONFIRMED**. A projection is never written as a score.
5. Autonomous validation (no human inspector): values in [0, 1], no NaN inside the footprint — addresses the earlier "Predicted values must be in range [0, 1]" rejection.
6. PhD-level explanation of how `GEMSDOE32 h33-h33-2-b2` reported 0.2778 and whether it can be beaten; use that to generate the unique TIF.
7. Propose 3–5 new geological hypotheses (layers, physical signature, why off-catalogue, how it differs), ranked by expected DTI gain and cost; validate the top candidate on a spatially-blocked hide-and-recover holdout before any slot; free official sources only.
8. **PARALLEL-RUN PROTOCOL:** one assigned lane; registry duplicate check (|Spearman| > 0.90 or > 70% of dots within 3 px → log and stop); reuse shared `evaluate_holdout.py` / `submission_writer.py` (fix once, never private-fork); label every number; leakage canary (single feature AUC > 0.90 → leakage); budget ≤ 3 experiments or 2 hours; no slot selection (separate selector, weekly cap); end with a JSON run card and promote/negative verdict.
9. No hallucinations: verify line by line from official sources; collect data/knowledge into auditable tables; state limitations and access needs (no DrivenData login; the data tab is login-walled).
10. Clean GitHub Pages site under `docs/`; three passes then a PR merged to `main`, listing remaining work and limitations.

## Current session review (`arena/accf3693-gemsdoekarage1`)

**DO NOT SUBMIT — no new candidate generated or cleared.**
[Three-pass review and next steps](knowledge/session-accf3693-review.md) ·
[Current shared preflight](evidence/session_accf3693_shared_preflight.json) ·
[Session run card](evidence/session_accf3693_run_card.json).
The fresh checkout has no restored shared cache and no assigned method lane or
canonical-template assignment. Historical evidence below is not a fresh model run.
This session hardened report input preservation and strict JSON handling;
**314 software tests pass** (not a performance score). The existing nine-site
summary and four ranked research proposals remain below; no leaderboard estimate
or new uniqueness certificate is asserted.

[Latest forensic & 9-site review (`9ca08e2e`)](knowledge/session-review-arena-9ca08e2e.md) · [Latest session run card (`9ca08e2e`)](evidence/session_9ca08e2e_run_card.json) · [19-band `training_features.tif` audit](evidence/training_features_band_audit_20261028.json) · [Secondary 9-site audit (12 files)](evidence/nine_sites_secondary_audit_20261028.json) · [Decision Dashboard](docs/index.html) · [Executive Summary & Submission Guide](docs/executive-summary.html) · [Nine-Site Audit Data](docs/data/reference-audit.json) · [Two-Candidate Saved-Byte Audit](evidence/candidate_audit_20261028.json) · [Independent repository and BB-STEP/CDA1 saved-byte review](knowledge/repository-review-2026-10-28.md) · [Session Review (`0a62cb67`)](knowledge/session-0a62cb67-review.md) · [Session Review (`8ffb6de1`)](knowledge/session-review-arena-8ffb6de1.md) · [Research Hypotheses](docs/research.html) · [Official Source Register](knowledge/sources-2026-10-28.md)

## Latest session (`arena/147b0f11-gemsdoekarage1`): NEW unique DIPDUAL TIF — preregistered, holdout-negative

- **Verdict remains `NEGATIVE / DO NOT SUBMIT`** ([session review](knowledge/session-review-arena-147b0f11.md) · [run card](evidence/run_card_dipdual_20261028.json) · [preregistration](docs/research/preregistration-dipdual-20261028.md) · [executive summary](docs/dipdual-20261028/index.html) · [how to submit](docs/dipdual-20261028/how-to-submit.html)): 0 slots spent; promotion remains the separate selector step.
- **New unique TIF generated** (urgency item): `karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif` in [docs/downloads/](docs/downloads/karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif) (+ single-TIF ZIP + writer receipt), SHA-256 `7b2a58eb1c3fb49cdd65f317c57d5552fe019c9be215aa2864533c2a50873cae`, 37,654 dots — **not copied from any prior submission** (new exposed/buried surfaces; worst discrete forward overlap 23.75%, vs B2 11.96%, pre-placement |Spearman| ≤0.058) and **format-valid** (shared writer + two independent saved-byte re-reads: finite [0,1] everywhere, EPSG:32611/shape/transform match, 0 on-catalogue). It is **NOT cleared**: blocked `HOLDOUT-DTI 0.040056 [0.034544, 0.046131]` (`gemsk-hide-recover-v1`, 60,988 withheld) < GPC control `0.073394` and BB-STEP control `0.046742`; `SGMC-DIAGNOSTIC-DTI 0.090244 [0.077331, 0.102597]` < GPC `0.126149`. Suggested note (`76` chars): `DIPDUAL dual-regime dip-shifted research raster; gates failed; DO NOT SUBMIT`.
- **Diagnosis:** contour-obliquity gate is anti-signal (AUC 0.42 — catalogue range fronts *are* contour-parallel; `IR-DIPDUAL-OBLIQUE-01`, not sign-flipped post-hoc); buried-basin allocation is unvalidatable on either local truth (catalogue + SGMC are surface compilations) and dilutes precision on both; dip-projection effect ≈0 at 100 m/300 m scales. **Positive control result:** label-free GPC physics beats static B2 on off-catalogue SGMC (`+0.0308 [+0.0082, +0.0519]`) and is the repo's best label-free blocked surface — next preregistered lane: exposed-only GPC refinement (+ LOO damage-zone prior, LiDAR polarity, no obliquity, no buried quota).
- **Lattice resolved by role separation** (`registry/registry_roles.json`, `IR-DIPDUAL-LATTICE-01`): lattice covers 99.8713% of footprint within 3 px (lower bound 82.34% at N=37,654; B2: 99.915% fwd / 15.06% rev). Duplicate gate now applies to `discrete_submission` rasters; literal lattice overlap (DIPDUAL 99.89%) is published in the card and needs selector acknowledgment.
- **Local candidates re-scored on SGMC** ([evidence/local_candidates_sgmc_audit_20261028.json](evidence/local_candidates_sgmc_audit_20261028.json)): HMAS `0.112595` > DIPDUAL `0.090244` > GPC-Z `0.077928` — HMAS stays selector-shortlist **only**, needs end-to-end re-validation; the older `karage1-unique-alteration` TIF **fails current format re-read** (`SGMC 0.003446`) — do not use.

## Earlier session (`arena/1668dda0-gemsdoekarage1`): 9-file local download audit, PR #42 retraction, validator hardening & 22-repo peer ecosystem review

**NEGATIVE / DO NOT SUBMIT — zero GeoTIFFs in `docs/downloads/` or across audited peer repositories are cleared for competition upload.** No new GeoTIFF was generated and no weekly slot was selected or spent.

- **Deliverables:** [Session review, B2 analysis & 4 preregistered hypotheses](knowledge/session-review-arena-1668dda0.md) · [Session JSON run card](evidence/session_1668dda0_run_card.json) · [9-local + 9-peer saved-byte audit receipt (`22` pinned repos)](evidence/local_downloads_and_peer_audit_20261028.json) · [Immutable peer ecosystem pins](registry/peer_ecosystem_pins.json).
- **Retracted defective PR #42 artifact & sidecars:** Direct saved-byte inspection of [`docs/downloads/karage1-unique-alteration-dots-20261028-zeros.tif`](docs/downloads/karage1-unique-alteration-dots-20261028-zeros.tif) (`8bc4dae0…`) against the pinned mirror template and `13GEMSDOE` lattice proved **`2,113` of `3,500` positive pixels (`60.37%`) lie OUTSIDE the active footprint** (`outside_encoding_accepted = false`) and **`1,385 / 1,387` (`99.8558%`) of in-footprint positives fall within `3 px` of the lattice**. Superseded false `"ok_to_submit": true` / `"verdict": "promote"` sidecars (`docs/downloads/karage1-unique-alteration-dots-20261028-zeros.{json,validate.json}`, `evidence/run_card_unique_tif_20261028.json`) and quarantined both `scripts/generate_unique_submission.py` and `scripts/run_bbstep_experiments.py`.
- **Closed three format-validator loopholes:** `scripts/validate_geotiff.py` now rejects all-finite bogus templates (`footprint.all()`), computes explicit `diagnostics.outside_encoding_accepted`, and exits `1` whenever outside-footprint validation fails; `scripts/audit_references.py` `raster_checks` requires `outside.size > 0` for `outside_all_nan` and blocks `--out` overwrites of `--manifest`.
- **Audited sibling `karage` & broader peer ecosystem (`GEMSDOE91/92`, `KANLER`, `EUG`, `WBG`, `GINNY`, `karage2/3`, `Apart`, `SASS`):** Every audited sibling/peer GeoTIFF (`GEMSDOEkarage2` `hk3-edgecentrality`: `99.86%`; `GEMSDOEkarage3` `k3c-csst-bghf`: `99.35%`; `GEMSDOE91` `S18-UNIQUE` `20,000` dots / `0.0435` user-reported: `99.61%`; `KANLERGEMSDOE3`, `WBGGEMSDOE1`, `ApartGEMSDOE1/2`, `GEMSDOESASS1`) overlaps `99.35%–99.95%` within `3 px` of the `13GEMSDOE` lattice. Documented two holdout-control defects in historical `src/gemsk/holdout.py` (`3 px` visible-collar dilation erasing `363` withheld truth pixels + static full-catalogue-pruned `B2` baseline). **354 software tests pass** (not a model performance score).

## Earlier session (`arena/a1ef4ce0-gemsdoekarage1`): independent replay and mandatory evidence gates

**NEGATIVE / DO NOT SUBMIT. The requested unique, high-scoring, cleared TIFF remains undelivered.** No geological experiment or slot was used. The assigned single method paragraph is still missing; inventing a lane or exempting the dense lattice is not permitted.

- [Current review and three proposed geological tests](knowledge/session-review-arena-a1ef4ce0.md) · [Session JSON card](evidence/session_a1ef4ce0_run_card.json) · [Organizer code-source receipt](evidence/official_code_receipt_a1ef4ce0.json).
- Independently re-fetched and SHA-256-verified all twelve pinned nine-site audit assets; the audit exactly reproduces the saved evidence except timestamps/software metadata. These are mirror-byte measurements, not organizer authentication or a full registry.
- Fixed two **promotion-by-omission** gaps: baseline withheld-positive counts must be explicit matching integers; pixel-mask validation must explicitly report `unmasked_inside: true` and integer `masked_inside_count: 0`. Finite values alone cannot establish an unmasked footprint.
- Source-card overwrite tests now cover valid/malformed JSON, same/relative paths, symlinks and hardlinks. Concurrent mainline duplicate-key rejection and preservation safeguards were retained. No shared evaluator/writer was changed or repinned.
- Directly inspected the organizer's pinned reference code: CPU-only training is supported, and its random-patch Tversky-loss baseline is not the requested buffered whole-segment DTI holdout. The earlier GPU-only prerequisite is inaccurate.
- B2's collar-removal geometry was independently reproduced, but a causal improvement on hidden organizer labels is **not proven**. The current leaderboard and weekly cap were not verified. No numerical leaderboard estimate is justified.

Read this README, `docs/standing-prompt.md`, `AGENTS.md`, and the current session review at the start of future work. The long original request remains represented by the explicitly normalized standing brief, not falsely described as a verbatim transcript. Its highest-priority unique-TIFF requirement and the binding lane/duplicate/holdout/budget/selector controls remain in force together.

## Earlier session (`arena/9ca08e2e-gemsdoekarage1`): 21-file nine-site audit, 19-band nodata forensics & fail-closed hardening

- **Verdict remains `NEGATIVE / DO NOT SUBMIT`** ([session review](knowledge/session-review-arena-9ca08e2e.md) · [session run card](evidence/session_9ca08e2e_run_card.json)): `0` new competition uploads or weekly-slot selections were made.
- **All 21 prompt-listed focus-site submissions audited** (`9` primary leaders in [docs/data/reference-audit.json](docs/data/reference-audit.json) + `12` secondary runs in [evidence/nine_sites_secondary_audit_20261028.json](evidence/nine_sites_secondary_audit_20261028.json), plus concurrent `GEMSDOE25` H79 in [docs/data/concurrent-review.json](docs/data/concurrent-review.json)): **every single file overlaps `99.1687%–100.0000%`** within 3 px of the pinned `13GEMSDOE` lattice (even `11,082`-dot `gems28-s18-mxtp` overlaps `100.0000%`).
- **Exact 4-point B2 collar-ablation ladder proven on pixel masks:** on the mirrored footprint, `GEMSDOE25` $\equiv$ `GEMSDOE30` (`44,090` dots, `0.2600` `USER-REPORTED / UNVERIFIED`) is the $r = 0$ parent; removing `3,891` dots within $r \le 1$ px (`100 m`) of `labels.tif` yields `GEMSDOE31` $\equiv$ `GEMSDOE28` `h27-4-r1` (`40,199` dots, `0.2708` `USER-REPORTED / UNVERIFIED`); removing `6,436` dots within $r \le 2$ px (`200 m`) yields `GEMSDOE32` `h33-h33-2-b2` (`37,654` dots, `0.2778` `USER-REPORTED / UNVERIFIED`); and `GEMSDOE36` (`38,854` dots, `0.2750` `USER-REPORTED / UNVERIFIED`) is `B2` $\cup$ `1,200` off-catalogue dots.
- **19-band `training_features.tif` forensic discovery** ([evidence/training_features_band_audit_20261028.json](evidence/training_features_band_audit_20261028.json)): **3,073 pixels inside `sample_submission.tif`'s active footprint** contain raw float32 `-3.4028235e+38` `nodata` (`3,061` across 18 bands + `12` extra interior pixels on Band 6 `tc`), providing a direct mechanism for `[0, 1]` portal range errors if unmasked; Band 6 `tc` is also strictly positive (`[2.9534, 88.5665]`) rather than a zero-crossing signed tilt angle.
- **Later mainline candidate re-audit:** the newer Conduitcrest TIF in main (`65c9432b…`, 17,415 dots) is **99.3454% within 3 px of the lattice** (17,301/17,415), so the literal rule says duplicate/stop despite its reported 0% overlap versus the nine focus sites. Its prior card omitted the lattice, a pre-placement lattice check, a per-feature canary, and a 95% CI for its HOLDOUT-DTI claim; it is **DO NOT SUBMIT**. Details: [`evidence/conduitcrest_lattice_reaudit_20261028.json`](evidence/conduitcrest_lattice_reaudit_20261028.json).
- **Shared validator & audit hardening:** hardened `src/gemskarage1/registry_audit.py` (GDAL mask + DrivenData `NaN`-outside support + `equal_nan=True`), `scripts/release_gate.py` (fail-closed CLI with strict `NaN`/`Infinity` rejection + atomic `--out`), `scripts/audit_references.py` / `audit_concurrent.py` / `audit_archives.py` / `audit_rasters.py` (GDAL mask + `abs(spearman) > 0.90` + `None`-metric guard), `scripts/collect_sources.py` (40-hex commit SHA enforcement + atomic writes), and `scripts/render_site.py` (fail-closed secondary 9-site audit rendering). This branch's direct test run before integrating current `main` had 230 passing tests; after merging the concurrent mainline regression suite, the current integrated suite passes **305 tests** (119 Rasterio/Affine pending-deprecation warnings).

## Earlier review — 28 October 2026, session `arena/0a62cb67-gemsdoekarage1`

All 12 pinned reference assets, the 2 committed candidates, the 2 parallel PR
candidates, the 3 archived demonstrators, and the concurrent peer raster were
freshly fetched from pinned GitHub mirrors into ignored `.cache/` and re-audited:
every reproduced report matched the committed JSON evidence byte-for-byte
(excluding execution timestamps and runtime package metadata). Additional
fail-closed safeguards were added and covered by regression tests: rejecting
duplicate registry SHA-256 digests, whitespace-only registry IDs, and
self-template digests in `scripts/release_gate.py`; blocking self-template
validation in `scripts/validate_geotiff.py` and `scripts/validate_artifact.py`;
blocking masked/nodata in-footprint candidate pixels in
`src/gemskarage1/registry_audit.py`; and hardening
`scripts/audit_parallel_candidates.py` against non-float32 rasters, undefined
footprint correlations, and `--out` input overwrites. See the
[session review](knowledge/session-0a62cb67-review.md) and
[negative session run card](evidence/session_0a62cb67_run_card.json). No new
portal upload or weekly-slot selection was made.

---

## Executive Summary: Nine Focus Sites

The table below summarizes the highest scoring submissions across the nine focus sites (`GEMSDOE24`, `GEMSDOE25`, `GEMSDOE27`, `GEMSDOE28`, `GEMSDOE30`, `GEMSDOE31`, `GEMSDOE32`, `GEMSDOE33`, `GEMSDOE36`), along with our new candidate:

| Site | Recommended Download File | Reported / Estimated Score | Evidence Class | Uniqueness vs Peer Sites & Lattice | Recommended Action |
|---|---|---|---|---|---|
| **GEMSDOE32** | `gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif` | 0.2778 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; subset of GEMSDOE25 (-6,436 dots) | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE36** | `gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif` | 0.2750 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; superset of B2 (+1,200 dots) | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE28** | `gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif` | 0.2710 | USER-REPORTED / UNVERIFIED | 99.91% vs lattice; 72 directional comparisons > 70% | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE31** | `gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif` | 0.2708 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; 59.09% vs B2 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE33** | `GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif` | 0.2632 | USER-REPORTED / UNVERIFIED | 99.91% vs lattice; 58.97% vs B2 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE25** | `gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif` | 0.2600 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; identical mask to GEMSDOE30 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE30** | `gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif` | 0.2600 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; identical mask to GEMSDOE25 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOE24** | `gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif` | 0.2477 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; D1.5 crowded spacing | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOEkarage1 (NEW)** | `karage1-dipdual-dualregime-dipshift-20261028T225112Z-zeros.tif` | HOLDOUT-DTI 0.040056 | LABELLED LOCAL INSTRUMENT (live unknown) | YES vs discrete registry (worst 23.75%); lattice literal 99.89% | **DO NOT SUBMIT** (holdout gates failed; research download) |
| **GEMSDOE27** | `gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif` | 0.2449 | USER-REPORTED / UNVERIFIED | 99.92% vs lattice; 61.20% vs GEMSDOE24 | **DO NOT RESUBMIT** (Research baseline) |
| **GEMSDOEkarage1 (BB-STEP, prior parallel session)** | `karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif` | 0.031790 [0.027138, 0.036271] | **HOLDOUT-DTI** (`gemsk-hide-recover-v1`; 60,988 withheld positives; 95% CI shown; not organizer-confirmed) | Unique vs nine focus sites (max overlap 12.6252%); **duplicate vs lattice (98.5253%)** | **DO NOT SUBMIT** (literal stop rule) |
| **GEMSDOEkarage1 (Conduitcrest, later mainline candidate)** | `gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4-zeros.tif` | Incomplete report: 0.017415; 95% CI missing | Reported `HOLDOUT-DTI` (`gems57-pooled-hide-v2`; 45,260 withheld positives; not independently rerun; no CI) | 0.0% vs nine focus sites, but **duplicate vs lattice (99.3454%)** | **DO NOT SUBMIT** (literal stop rule) |
| **CDA1 archive demonstrator (quarantined)** | `gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif` | **No valid score** | **Not a valid HOLDOUT-DTI** (archived evaluator returns hard-coded values; see `docs/data/archive-review.json`) | 99.7769% of 37,654 dots within 3 px of the lattice | **DO NOT SUBMIT** (synthetic research artifact) |
| **PR #42 synthetic artifact (retracted & quarantined)** | `karage1-unique-alteration-dots-20261028-zeros.tif` | **No valid score** | **Retracted synthetic placeholder** (pseudo-random Gaussian blobs; zero geophysical input) | **2,113 outside-footprint positives** + **99.8558%** (1,385/1,387) within 3 px of lattice | **DO NOT SUBMIT** (format-invalid & lattice duplicate) |
| **Sibling & peer ecosystem (`GEMSDOEkarage2/3`, `GEMSDOE91`, `KANLER3`, `WBG1`, `Apart1/2`, `SASS1`)** | 9 pinned GeoTIFFs across 22 commit-pinned repos ([audit JSON](evidence/local_downloads_and_peer_audit_20261028.json)) | `0.0435`–`0.2747` (where supplied; leaderboard `#1 0.4413`, `#2 0.3195` have no public TIFs) | `USER-REPORTED / UNVERIFIED` | **99.3520%–99.9523%** within 3 px of the `13GEMSDOE` lattice | **DO NOT COPY / DO NOT RESUBMIT** (learning only) |

### Per-Site Summary Findings
All parenthesized historical values below are **USER-REPORTED / UNVERIFIED**, not organizer-confirmed scores. The mask identities and dot counts are independent measurements on hash-pinned owner mirrors; they do not prove why the reported values changed.
- **GEMSDOE24 (0.2477 USER-REPORTED / UNVERIFIED):** A 60,069-dot d1.5 emission; the measured mask is 99.9218% within 3 px of the pinned lattice.
- **GEMSDOE25 (0.2600 USER-REPORTED / UNVERIFIED):** The 44,090-dot d2.8 parent; its footprint mask is pixel-identical to GEMSDOE30.
- **GEMSDOE27 (0.2449 USER-REPORTED / UNVERIFIED):** 61,328-dot topographic-gap-closure submission; 99.9234% within 3 px of the lattice.
- **GEMSDOE28 (0.2710 USER-REPORTED / UNVERIFIED):** Highest supplied GEMSDOE28 value in the prompt. A separate r1 file has a 40,199-dot mask identical to GEMSDOE31; these are distinct runs and scores.
- **GEMSDOE30 (0.2600 USER-REPORTED / UNVERIFIED):** Its 44,090-dot mask is identical to GEMSDOE25 despite a different filename/container hash.
- **GEMSDOE31 (0.2708 USER-REPORTED / UNVERIFIED):** The 40,199-dot r1 mask is pixel-identical to GEMSDOE28 h27-4-r1.
- **GEMSDOE32 (0.2778 USER-REPORTED / UNVERIFIED):** Highest value supplied for the nine focus sites. Its mask equals GEMSDOE25's mask with 6,436 dots within 2 px of the mirrored catalogue removed; no dots were added. This geometry does not establish causal score improvement.
- **GEMSDOE33 (0.2632 USER-REPORTED / UNVERIFIED):** The primary h33d historical mask has 41,865 dots; no organizer receipt ties the score to its audited hash.
- **GEMSDOE36 (0.2750 USER-REPORTED / UNVERIFIED):** Its primary 38,854-dot mask is a strict superset of B2, preserving its 37,654 dots and adding 1,200. The causal reason for the reported change is not established.

---

## Evidence-Limited Forensics: GEMSDOE32 B2 and What Can Be Concluded

**`0.2778` is USER-REPORTED / UNVERIFIED** (no organizer receipt tied to the audited file hash is available here). The following are measured raster-mask relationships on pinned owner mirrors; they are not performance measurements or causal attribution.

### Pixel-mask lineage

- The `GEMSDOE25` / `GEMSDOE30` d2.8 masks are pixel-identical on the mirrored footprint: `44,090` dots.
- `GEMSDOE31` and secondary `GEMSDOE28 h27-4-r1` share an exact `40,199`-dot mask, equal to the d2.8 parent with `3,891` dots within 1 pixel (`100 m`) of the mirrored catalogue removed.
- `GEMSDOE32` B2 has `37,654` dots and equals the d2.8 parent with `6,436` dots within 2 pixels (`200 m`) of the mirrored catalogue removed; no dots were added.
- The primary `GEMSDOE36` mask is a strict superset of B2: it preserves the `37,654` B2 pixels and adds `1,200` pixels, for `38,854` total.

The associated historical values `0.2600`, `0.2708`, `0.2778`, and `0.2750` are all **USER-REPORTED / UNVERIFIED**, not organizer-confirmed results. The apparent trend is consistent with a precision/coverage tradeoff, but these cross-site owner reports are not a controlled ablation, and exact pixel inclusion cannot identify why a hidden-label score changed.

### Metric mechanism and limits

The [official metric specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) uses a distance-weighted Tversky objective. In pooled notation, `DTI = TPw / (TPw + 0.2·FPw + 0.8·FNw)`. Predictions close to a hidden fault receive more kernel-weighted coverage; prediction mass not near hidden truth contributes weighted false-positive cost. Therefore, deleting low-yield predictions can improve DTI **only if** the saved false-positive contribution exceeds any lost true-positive coverage. The mask counts alone cannot measure either quantity.

The [organizer staff clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) says known-catalogue pixels are masked, not that an arbitrary surrounding collar is a free scoring buffer; nearby unmapped faults can still be meaningful. Thus the 1-pixel and 2-pixel deletion rings are hypotheses about redundancy, not guaranteed false-positive regions.

### Can a future submission beat the reported value?

It is scientifically possible but **not established or numerically estimable** from the evidence here. A prior parallel session recorded `BB-STEP` **HOLDOUT-DTI 0.031790** (evaluator `gemsk-hide-recover-v1`, `60,988` withheld positives, 95% CI `[0.027138, 0.036271]`) and a B2 control **HOLDOUT-DTI 0.004845** (same evaluator and withheld-positive count, 95% CI `[0.004322, 0.005346]`). These are prior-session holdout reports, not organizer scores, were not independently rerun in this session, and are not directly comparable to the separate USER-REPORTED `0.2778` competition value. The BB-STEP raster also fails the literal lattice duplicate gate (98.5253% of its dots within 3 pixels), so it is **DO NOT SUBMIT** regardless of holdout results.

The current status and limitations are recorded in the [BB-STEP review](knowledge/review-bbstep-2026-10-28.md), [session forensic audit](knowledge/session-review-arena-9ca08e2e.md), and [run card](docs/data/run-card.json). Do not treat a holdout difference, a user-supplied leaderboard figure, or a geological narrative as an organizer-confirmed score or submission clearance.

---

## New Geological Hypotheses — Research Proposals, Not Results or Lane Assignments

The ordering below is **qualitative prioritization only**; no expected score or DTI gain is asserted. No new experiment was run in this session. The current `registry/template.json` still has `method_lane: null`; the four proposals do not assign this session to a lane. See the [complete forensic preregistration and source caveats](knowledge/session-review-arena-9ca08e2e.md#4-four-untried-band-verified-geological-hypotheses-pre-implementation-ranking).

| Rank / effort | Layers & targeted physical signature | Why it may expose off-catalogue structure | Named non-fault mimic | Difference / data readiness |
|---|---|---|---|---|
| **1 · low–medium** | Existing 19-band stack: `depth_to_base_surf`, `iso_grav_anom`, `iso_grav_anom_hg/vg`, `rtp`, `tmi_hg/vg`; condition on `det_elev_slope`. Detect multi-scale potential-field phase alignment plus a basement step beneath low-slope basin fill. | Concealed buried structure may lack a surface scarp while preserving density/susceptibility discontinuities. | Buried paleochannels, pediment/pluton contacts, basalt-flow edges, or survey seams. | Different from unsigned NMS ridges by testing multi-scale signed phase congruency and coincident basement throw. In-stack proposal only; stack is a third-party mirror, not organizer-authenticated; lane and shared cache unresolved. |
| **2 · medium** | `geod_shearrate`, `geod_dilaterate`, `geod_2ndinv`, `deq_n100a15`, `ieq_n100a15`, `cond_surf`, `rtp`, and fold-visible fault-tip orientations. Test a low-frequency strain/seismic corridor that links sharp 100-m geophysical ridges across relay zones. | Distributed relay faults can be missed when mappers split traces at fault-segment tips. | Mining/injection seismicity, conductive playa clay, and smoothed GPS fields. | Differs from direct high-resolution placement on smooth strain fields by using strain only as a corridor prior; requires strict fold-local catalogue handling. In-stack proposal; not validated. |
| **3 · medium–high** | RTP magnetics, magnetic horizontal/vertical gradients, conductivity and local K/eTh radiometric boundaries. Test a destriped, narrow alteration-boundary discontinuity aligned with a magnetic trough. | Hydrothermal alteration may persist where erosion or burial removes a recognizable scarp. | Lithologic contacts, potassic intrusions, weathering, playa evaporites, and flight-line seams. | Different from a raw broad radiometric plume: targets a local boundary after survey-stripe control. Official source: [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and). Derived mirror layers exist; official source bytes were not authenticated in this sandbox. |
| **4 · high** | `det_elev`, `det_elev_slope`, positive-curvature-magnitude `tc`, `iso_grav_anom_hg`, plus official [USGS 3DEP](https://www.usgs.gov/3d-elevation-program) DEMs if independently obtained. Test multi-catchment drainage asymmetry and fan-apex alignment against a conditioned null. | Repeated drainage deflection can persist after a low-relief scarp is degraded. | Lake Lahontan shoreline benches, fan terraces, resistant strata, and stream piracy. | Different from pixel-level scarp scores; requires hydrologic-network extraction. USGS describes free 3DEP products, but exact study-area coverage and official tile bytes were not verified here. Not data-ready. |

The target is mapped fault traces, not direct proof of an active geothermal vent. All four mechanisms are hypotheses with plausible confounders; none is a validated detection or score projection.

---

## Range-Error Triage & Download Status — DO NOT SUBMIT

The exact file that produced DrivenData's reported `Predicted values must be in range [0, 1]` error was not retained in this repository. Therefore its cause is **unknown**; a local format check cannot establish portal acceptance. A firsthand audit of the restored, third-party-mirrored `training_features.tif` found 3,073 raw float32 nodata values (`-3.4028234663852886e+38`) in pixels that are finite in the mirrored `sample_submission.tif` footprint. If any inference pipeline consumes those sentinels without an explicit per-band validity mask, invalid or out-of-range predictions are a plausible failure mechanism—but this is not proof of what caused the earlier portal error. See [the 19-band audit](evidence/training_features_band_audit_20261028.json).

The [official submission-format page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format) describes null/NaN values outside the bounds. Local reports separately test in-footprint range/masks, NaN-outside, and strict whole-array finite range. Neither encoding has been portal-tested here. Do not convert an artifact to zeros or NaNs and assume that fixes the previous rejection.

### Research artifact currently in the repository (generated by a prior parallel session)

- **BB-STEP GeoTIFF:** [`docs/downloads/karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif`](docs/downloads/karage1-bbstep-buried-basement-20261028T180000Z-zeros.tif), SHA-256 `72312302675d65cd1983239dd436412b5db1118a7c08f2a5807ef436b5536d6a`.
- **Prior-session HOLDOUT-DTI:** `0.031790` (evaluator `gemsk-hide-recover-v1`, 60,988 withheld positives, 95% CI `[0.027138, 0.036271]`). This is a run-card report, not ORGANIZER-CONFIRMED and was not independently rerun in this session.
- **Uniqueness:** 12.6252% maximum 3-px overlap versus the nine focus-site rasters, but **98.5253%** of dots are within 3 px of the pinned lattice; literal protocol duplicate. The registry inventory is incomplete.
- **Decision: `DO NOT SUBMIT`.** It is exposed as a research/audit artifact only. It is not a cleared submission and is not an estimate of the leaderboard score.

### Quarantined CDA1 demonstrator

The older [`CDA1` TIFF](docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif) is explicitly a **synthetic demonstrator, not a competition prediction**. Its archived evaluator returned hard-coded values independent of input, so a previously reported `0.1473` is **not a valid HOLDOUT-DTI measurement** and must not be used as a score. The saved bytes also have 37,570 of 37,654 dots within 3 px of the lattice (99.7769%): duplicate. The file is retained for audit only; **DO NOT SUBMIT**. Source: [`docs/data/archive-review.json`](docs/data/archive-review.json).

No file in this repository is marked `OK TO SUBMIT`. The selector step remains separate and no competition slot was selected or spent in the current session.

---

## Standing Task Brief — Normalized, Not a Verbatim Transcript

The original, very long user message is available in the conversation replay but was not saved as a raw transcript in this checkout. This repository therefore does **not** claim that the following normalized task brief is a verbatim or complete copy. Read [`docs/standing-prompt.md`](docs/standing-prompt.md), this README, and [`AGENTS.md`](AGENTS.md) at the start of each session; newer explicit user instructions take precedence.

### Core requirements

- **Maximize P(Win) / Own the Outcome:** prefer reproducible, scientifically defensible evidence; report negative results, missing access, and uncertainty honestly.
- Build an automated, auditable DrivenData DOE GEMS fault-mapping workflow and clean GitHub Pages site. Make a genuinely new, unique GeoTIFF only when every assigned-lane, evidence, novelty, holdout, format, and selector gate permits it. The current site and all generated research files must plainly say **DO NOT SUBMIT** until then.
- For GEMSDOE24, 25, 27, 28, 30, 31, 32, 33, and 36, distinguish `USER-REPORTED / UNVERIFIED` results from artifact-linked `ORGANIZER-CONFIRMED` receipts. Never invent a leaderboard estimate. A `HOLDOUT-DTI` must state evaluator, withheld-positive count, and 95% CI.
- Follow the literal parallel-run protocol: use one explicitly assigned lane; compare continuous surfaces before placement and final dots against every registry raster; stop if rank correlation exceeds 0.90 or more than 70% of candidate dots fall within 3 pixels. Do not jitter, rename, or exempt a lattice to evade the rule.
- Reuse the agreed shared evaluator/writer; whole-segment buffered hide-and-recover; recompute catalogue features from visible faults only; mask visible faults pixel-exactly; pooled DTI with α=0.2, β=0.8 and a 300 m triangular kernel; test each feature alone for leakage; stop after three experiments or two hours. No weekly slot selection in the experiment workflow.
- Validate reopened saved GeoTIFF bytes automatically (one float32 band; correct CRS, shape, and transform; no nonfinite or masked values inside footprint; values in [0,1]; explicit outside-footprint diagnostics). Local validation is not portal approval.
- End each run with a JSON card containing hypothesis, mechanism, named non-fault mimic, holdout result/CI, registry checks, raster hash, validator output, name/note (≤140 characters), and promote/negative verdict.
- Research only free, official sources and keep data provenance auditable. Distinguish fault mapping from proof of active geothermal vents. Follow the official [competition specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/), [reference solution](https://github.com/drivendataorg/gems-prize-reference-solution), [DOE/NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf), [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and), and [GDR INGENIOUS](https://gdr.openei.org/submissions/1391). Source links do not prove payload availability or organizer authentication.

## Remaining Work and Limitations

1. **Assigned lane and canonical shared template are unresolved.** `registry/template.json` still records `method_lane: null` and no canonical-template assignment. Do not invent a lane or run a local/private fork. Reconcile the recorded template-integrity failures with the upstream owner before shared execution.
2. **The lattice gate blocks the extant candidates.** The pinned lattice covers 99.8713% of the mirrored footprint within the 3-pixel disk. The prior parallel-session BB-STEP TIFF is distinct from the nine focus-site dot masks, but 98.5253% of its dots are within 3 pixels of the lattice. It is a duplicate under the literal rule. Clarify the apparent calibration-lattice/registry conflict with the protocol owner; do not alter the threshold, stuff holes, or treat a unique filename as clearance.
3. **Official data provenance remains unresolved.** All 31 restored inputs are hash-pinned third-party GitHub mirrors, not authenticated organizer downloads. The mirrored `labels.tif` and `existing_faults.tif` are byte-identical, and the mirrored sample contains positive cells despite the public description of an all-absence template. The mirror-only finding of 3,073 interior feature nodata pixels is documented; mask them explicitly in any future authorized pipeline.
4. **The complete submission registry and current selector state are unavailable.** Auditing one lattice witness can disqualify a file; passing a partial audit cannot certify uniqueness. No competition slot was selected or spent here.
5. **CDA1 is quarantined.** Its archived evaluator returned hard-coded values; `0.1473` is not a valid `HOLDOUT-DTI`. Do not cite it as a measured score or recommend its TIFF for upload.
6. **Prior BB-STEP holdout is not a leaderboard result.** The previous session reports `HOLDOUT-DTI 0.031790` (evaluator `gemsk-hide-recover-v1`, 60,988 withheld positives, 95% CI `[0.027138, 0.036271]`), but the saved raster fails the literal lattice stop. This session did not rerun it, produce another TIFF, estimate leaderboard performance, or select a slot.
7. **Three-pass follow-up order:** obtain an assigned lane and authoritative template; authenticate organizer data and template geometry; resolve the lattice interpretation without evasion; establish a complete inventory and comparable baseline; only then preregister and run at most three properly buffered, fold-local experiments and the automated validator. A separate selector checks a live weekly allowance only after every gate passes.

The current active session review is [`knowledge/session-review-arena-1668dda0.md`](knowledge/session-review-arena-1668dda0.md), with its exact session card at [`evidence/session_1668dda0_run_card.json`](evidence/session_1668dda0_run_card.json) and saved-byte ecosystem receipt at [`evidence/local_downloads_and_peer_audit_20261028.json`](evidence/local_downloads_and_peer_audit_20261028.json). Prior session records, including [`knowledge/session-review-arena-a1ef4ce0.md`](knowledge/session-review-arena-a1ef4ce0.md) and [`knowledge/session-review-arena-8ffb6de1.md`](knowledge/session-review-arena-8ffb6de1.md), are historical evidence to inspect—not certificates of current validity.
