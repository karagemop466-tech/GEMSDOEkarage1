# Repository review — `arena/b2b18800-gemsdoekarage1` — 29 October 2026

## Executive decision

**NEGATIVE / DO NOT SUBMIT.** No new GeoTIFF was generated, no geological experiment or holdout ran, no score estimate is available, and no weekly submission slot was selected or spent. The website's current green-free status is correct: no approved download exists. The historical site scores below are **USER-REPORTED / UNVERIFIED**, not organizer-confirmed receipts.

The requested priority file cannot responsibly be produced in this turn. The binding parallel-run protocol says to stay in one assigned method lane, but `registry/template.json` has both `method_lane` and `canonical_template_assignment` set to `null`. The data directory/cached feature stack are absent. Creating a lane or building a new evaluator would violate the request to reuse the canonical shared template. In addition, the literal internal 70%/3-pixel uniqueness test is known to reject the audited lattice-like rasters; no protocol-owner resolution or complete authenticated registry is available. Existing TIFs remain research/audit artifacts, not cleared submissions.

## Nine-site executive table

The scores and names in this table are transcribed from the user's supplied results and the repository's `registry/historical_claims.json`; they are not authenticated by DrivenData receipts. The candidate filenames link from the existing rendered executive summary and site pages. “Unique” is **No under the literal in-repo lattice test**, and “new score” is not estimated. See `docs/executive-summary.html`, `evidence/nine_sites_secondary_audit_20261028.json`, and `evidence/reference-audit.json` (mirrored, pinned inputs; not organizer-authenticated).

| Site | Best supplied submission | Reported score | Score evidence | Unique under literal 70% / 3-px gate? | Action |
|---|---|---:|---|---|---|
| GEMSDOE24 | `h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan` | 0.2477 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Research baseline only |
| GEMSDOE25 | `dotted-h19-5-d2-8-20261002-e56ea318af89-nan` | 0.2600 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Research baseline only |
| GEMSDOE27 | `topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan` | 0.2449 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Research baseline only |
| GEMSDOE28 | `h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan` | 0.2710 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Research baseline only |
| GEMSDOE30 | `d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca` | 0.2600 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Research baseline only |
| GEMSDOE31 | `h27-4-solo-d28-20261004-8acb75e1-nan` | 0.2708 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Research baseline only |
| GEMSDOE32 | `h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros` | 0.2778 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Best supplied nine-site reference; do not resubmit |
| GEMSDOE33 | `h33d-analog-tip-stepover-r30-20261004-cb490425926e` | 0.2632 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Research baseline only |
| GEMSDOE36 | `anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros` | 0.2750 | USER-REPORTED / UNVERIFIED | No; audited lattice overlap exceeds threshold | Research baseline only |

The uniqueness statement is only against the pinned local lattice mirror and audited historical file set—not against a complete, authenticated competition registry. The 70%/3-pixel rule is an internal protocol gate, not represented here as an official contest rule. The largest supplied site value (`0.2778`) is not a defensible estimate for a new submission.

## Why the supplied GEMSDOE32 B2 value may be high — and what is not known

The official metric is distance-weighted Tversky: it penalizes missed labelled faults more heavily than false-positive prediction mass (`alpha=0.2`, `beta=0.8`, 300 m triangular kernel; see the [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric)). The repository's pinned-mirror mask audit records GEMSDOE32 B2 as a thinning of the GEMSDOE25/30 support set, removing dots near the mirrored catalogue. If the user-reported scores are accurate, a plausible mechanism is that removed near-catalogue mass had low useful coverage of hidden faults, while retained off-catalogue predictions preserved enough recall. That is a *conditional interpretation*, not a causal finding: there is no organizer receipt tied to the score and raster hash, no controlled organizer-label ablation, and catalogue proximity does not mean nearby unmapped faults are false positives. It is possible in principle to beat 0.2778; evidence here cannot estimate the odds or support any numeric projection.

## Hypotheses requested before implementation

**This session did not claim to produce a new, untried 3–5-item slate or rank likely DTI gains.** The single assigned lane is missing, and the repository contains many earlier hypothesis families and competing parallel runs. Claiming a method is “not tried” or choosing its place in the ranking without reconciling those records would be unverifiable. `knowledge/hypotheses-20261028.md` already contains a proposal-only five-item slate (signed potential-field edges; radiometric alteration residuals; catchment drainage asymmetry; sampling-aware thermal residuals; magnetic-lineation relay ramps). Those are historical proposals, not assigned methods, not newly established as untried, and not validated. No one was selected or implemented here.

Before the next candidate slate can be compliant, the protocol owner must supply the exact method paragraph and canonical shared-template assignment. Then generate 3–5 candidates *inside that lane*, record each layer, physical signature, off-catalogue logic, repo novelty, named non-fault mimic, official-source payload availability, and qualitative cost/gain ordering. A numerical score must not be forecast. Validate one preregistered candidate using the template's blocked hide-and-recover evaluator before any selector/slot action.

## Three verification passes

### Pass 1 — repository and tool review

- Read `AGENTS.md`, the standing brief, README, current/prior run cards, current review, site pages, registry metadata, runners, writer/validator, and tests.
- Verified working branch: `arena/b2b18800-gemsdoekarage1`. It starts at `5a6a5fb`, the same commit as local `main`/`origin/main`; work remained on the session branch.
- Verified `registry/template.json` has no assigned method lane or canonical template.
- Verified no local `data/` or cached feature stack is present. Existing `docs/downloads/*.tif` files are previous research artifacts; no new file was made.
- Installed the declared requirements into an ephemeral `/tmp` virtual environment (not tracked) and ran `/tmp/gems-review-venv/bin/python -m pytest -q`: **365 passed, 0 failed, 0 skipped**, with 119 Rasterio/Affine pending-deprecation warnings. This is software verification only.
- Ran the guarded entry points. `scripts/run_karage1_experiments.py --stage all` and `scripts/my_unique_experiment2.py` both exited 2 with `BLOCKED`; no experiment or raster was produced.
- After remote `main` advanced during PR review, I incorporated its separate GSE research artifact, independently audited its two saved TIFF variants against the pinned lattice and nine focus-site mirrors, added an automated renderer guard, and reran the complete suite: **368 passed, 0 failed, 0 skipped**, 119 Rasterio/Affine warnings. This was a saved-byte uniqueness audit, not a geological experiment or HOLDOUT-DTI.

### Pass 2 — adversarial review

- The published pages had stale session messaging: the top decision still described session `1668dda0` as current even though later reviews/cards were present. The page builder now adds this review explicitly and labels the older item as a prior audit; this prevents a stale current-status assertion.
- No attempt was made to bypass the quarantined generation scripts, duplicate stop, missing data, or lane assignment.
- The portal's actual cause for the earlier “Predicted values must be in range [0, 1]” rejection remains unverified; a local format check is not proof of portal acceptance.
- The repo's historic site values remain user-supplied/unverified; none is re-labelled as HOLDOUT-DTI or ORGANIZER-CONFIRMED.

### Pass 3 — requirements recheck

- The top-level site says DO NOT SUBMIT and offers no approved TIF. Historical downloads are clearly research only.
- The nine focus-site table identifies the reported best references and labels the evidence status. There is no projected score and no candidate claiming to beat the supplied 0.2778.
- No new unique TIFF was generated because a new output would be knowingly outside an assigned lane, unsupported by the missing cached stack, and not capable of passing its required pre-placement/holdout/registry checks.
- The requested holdout, per-feature canary, raster hash, final saved-byte validator output, and score confidence interval are therefore not applicable; the run card records nulls rather than fabricated values.

## Concurrent mainline artifact found while this PR was open

After this session's initial review and commits, `origin/main` advanced with a separate artifact from another parallel session. Its saved GeoTIFF is `docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif`. I verified the local Git blob SHA-256 is `f5879e1902e6c15407582a67e210bacfd0b2425570c4aefbdf5c585a4579c37b`, matching `evidence/run_card_gse_exp1.json`. It is a separate run, not generated by this session and **not approved for submission**.

Its own run card says `ok_to_submit: false`, `verdict: negative`, and `holdout_dti.value: null`. The `evidence/uniqueness_gse_exp1.json` receipt reports a maximum overlap of 31.04% and maximum absolute Spearman of 0.0104, but it covers only 11 listed rasters and does not include the pinned lattice or a complete set of the nine focus-site rasters. Thus its `unique: true` conclusion is scoped, not fleet-wide. More importantly, I restored the 12 hash-pinned reference rasters via the existing GitHub API audit tool and independently re-audited both saved GSE variants (`-zeros.tif` and `-nan.tif`) against the nine focus-site mirrors plus the lattice. [`evidence/gse_saved_byte_audit_20261029.json`](../evidence/gse_saved_byte_audit_20261029.json) binds the candidate hashes and full comparison rows. For the zeros submission TIF, **23,979 / 24,000 = 99.9125%** of positive pixels lie within 3 px of the lattice; binary-mask Spearman is -0.0000425. For the NaN-outside diagnostic twin, the same 23,979 / 24,000 and 99.9125% overlap is measured. Either one independently trips the internal overlap stop. The pinned-lattice geometric lower bound is also 72.2958% (at most 6,649 in-footprint dots could occupy cells outside the 3-px neighborhood), consistent with the exact comparison.

The separate `scripts/build_gse_submission.py` CLI is now quarantined at its entry point and returns `BLOCKED` without rewriting any saved bytes; its artifact helpers remain only for audit/research. Other unmet gates: the run card's “leakage canary” is a component correlation against near-catalogue membership, not per-feature AUC against withheld fault truth; a pre-placement surface-to-registry comparison is not recorded; no HOLDOUT-DTI or 95% CI exists; and the zeros-outside TIF fails the separate local `outside_all_null_or_nan` check (the NaN twin passes that outside check). The zeros file's strict whole-array finite `[0,1]` check passes locally. Neither diagnostic establishes portal acceptance, and the official sample provenance is still mirror-based. I updated the generated Pages to show the file as an easy-to-find **research-only download / DO NOT SUBMIT**, with the file hash, measured lattice comparison, holdout status, and evidence links. Do not upload it unless an assigned lane, shared evaluator holdout, complete registry audit, format interpretation and separate selector all pass.

## Official source links for review

These are source pointers already recorded in the repository; they were **not freshly fetched from those hosts in this session**. Source descriptions are not evidence that a local mirror is organizer-authenticated or that a specific tile is obtainable today.

- [DrivenData problem, metric and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData competition data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) (login required according to existing repository records)
- [Organizer reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GDR INGENIOUS compilation](https://gdr.openei.org/submissions/1391)
- [DOE/NLR official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [EPSG:32611](https://epsg.io/32611)

## Handoff / limitations

1. Obtain the explicit method-lane paragraph and canonical shared-template owner/commit.
2. Restore competition data through authorized access; validate provenance and hashes against organizer-provided bytes. The Dropbox/community mirrors are not a substitute for provenance.
3. Resolve the internal lattice threshold with its protocol owner and obtain a complete pinned registry; do not silently exempt a witness.
4. Use the assigned shared evaluator and submission writer only. Run the feature-by-feature leakage canaries, then the whole-segment buffered spatial holdout (visible-only catalogue-derived features and exact visible-fault masking) for a preregistered idea; stop by 3 experiments or 2 hours.
5. Require a HOLDOUT-DTI report with evaluator version, withheld-positive count and 95% CI before any separate selector action. It is not a leaderboard projection.
6. Re-open and validate the exact candidate bytes against the official sample grid, footprint values/range, CRS/shape/transform, no NaN within footprint, and literal surface + final-dot registry comparisons. Portal acceptance needs an organizer receipt.
7. Only a separate selector may check the live submission cap and choose a real slot. None was selected here.

## Run card

See [`evidence/session_b2b18800_run_card.json`](../evidence/session_b2b18800_run_card.json). Verdict: `negative`.
