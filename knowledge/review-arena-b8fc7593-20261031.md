# Repository review — `arena/b8fc7593-gemsdoekarage1` — 31 October 2026

## Executive decision

**NEGATIVE / DO NOT SUBMIT.** The current branch has no assigned method lane, no verified canonical shared evaluator/writer assignment, and no cached competition inputs. No geological experiment or holdout ran; no TIFF was generated or cleared; no leaderboard score was estimated; and no weekly slot was selected or spent. The user's supplied 0.2778 for GEMSDOE32 B2 is **USER-REPORTED / UNVERIFIED**, not an organizer receipt.

The best-ranked historical reference among GEMSDOE24/25/27/28/30/31/32/33/36 is GEMSDOE32 B2 *according to the supplied score ledger*. It cannot responsibly be called the best submission to upload: it is third-party historical data and locally fails the novelty gates. An estimate for any focus-site file is **not estimable** from this repository.

## Three-pass review

### Pass 1 — inspect and reproduce current state

- Read the starting-point instructions in `AGENTS.md` and the README's top review block; inspected the existing three-pass review, focus-site evidence, lane/template pin, cached-input expectations, validators, release gates, generated decision pages, and test configuration.
- Local lineage records show B2's 37,654-positive mask is the GEMSDOE25/30 44,090-positive mask after removing 6,436 locations, with no additions. The local GEMSDOE31/GEMSDOE28 H27-4 mask similarly removes 3,891 locations from the parent. These are mask-geometry observations against pinned third-party mirrors, not proof of private labels or organizer-confirmed scores.
- A plausible explanation for B2's reported gain is a better precision/recall trade-off after deleting low-yield or redundant marks under the asymmetric distance-weighted Tversky metric. This is only a hypothesis: absent hash-linked organizer receipts and private truth, the repository cannot establish that the deleted points were false positives or explain the reported score causally. The competing possibility is ordinary variation across submissions or differing raster/receipt lineage.
- Installed the declared test dependencies into ignored `.venv/`; this did not add generated artifacts to Git.
- Executed `.venv/bin/python -m pytest -q -rs`: **446 passed, 0 failed, 2 skipped, 126 warnings**. Skips require ignored bridge rasters and the missing competition sample grid. The warnings are Rasterio `PendingDeprecationWarning`s. This verifies software behavior only, not geological skill or leaderboard performance.
- Executed `.venv/bin/python scripts/shared_tools.py preflight`: **exit 1; not ready**. It found a null method lane and no canonical assignment; it lists missing `feature_stack.npy`, `existing_faults.tif`, `training_features.tif`, `sample_submission.tif`, and `labels.tif`; writer/uniqueness source hashes do not match recorded pins. Execution authorization is false.

### Pass 2 — adversarial review and user-facing improvement

- Confirmed the locally pinned submission registry is not a complete, organizer-authenticated registry. No local uniqueness finding can establish global uniqueness across the full fleet.
- Confirmed the literal protocol thresholds are stricter than mere byte uniqueness. The existing focus-site masks have very high local overlap with siblings/lattice; no item is safe to resubmit. Historical local overlap results are bounded to the files pinned by the repository.
- Updated the generated nine-site decision table to include an explicit **Leaderboard estimate** column. Each of the nine historical entries reads “Not estimable”; it now distinguishes user-reported scores from forecasts and explains that no calibrated map from catalogue holdout to private leaderboard truth exists. This is a clarity improvement, not a new scoring result.
- Rebuilt the static pages with `.venv/bin/python scripts/build_site.py`; the build reports “no submission authorized.”
- Verified the generated table shows nine “Not estimable” rows and is present on both the site index and executive summary. The top-level status remains DO NOT SUBMIT.

### Pass 3 — original-request and protocol check

- The detailed prior review [`review-arena-946f7668-20261031.md`](review-arena-946f7668-20261031.md) contains the focus-site table and four physically motivated candidate hypotheses, including target layers, mechanisms, counter-explanations, novelty caveats, and qualitative cost ranking. They remain proposals, not validated discoveries.
- The prompt's required single method paragraph is not present in the branch's `registry/template.json` (`method_lane: null`). Therefore there is no legitimate “top candidate” to execute in this session. Running a private evaluator, inventing a lane, using the absent feature stack, or creating a TIFF would violate the reuse/lane rules. The experiment budget remains unspent (0/3); no slot is involved.
- No feature-alone AUC canary, holdout DTI or 95% interval, pre-placement correlation, final-dot overlap, or candidate-raster format validation was computed in this review. Accordingly the required leakage/registry/validation gates are **unknown, not passed**.
- The candidate hypotheses in the prior review need to be reconsidered against the full local experiment history and registry before any lane is assigned; novelty against every user-listed GEMSDOE repository is not established.
- Checked page output and ran `git diff --check`; no generated TIF was added. The full original science/submission objective remains blocked, and no download from this checkout is approved.

## Focus-site executive table

The full file names, user-reported values, local uniqueness statuses, and explicit “Not estimable” column are rendered at the top of [`docs/index.html`](../docs/index.html) and [`docs/executive-summary.html`](../docs/executive-summary.html). The source data are `registry/user_reported_scores_20261029.json` and the pinned-lineage audit `evidence/site_lineage_verification_20261029.json`; the entries are **USER-REPORTED / UNVERIFIED**, not organizer-confirmed values. The highest listed user value is GEMSDOE32 B2 at 0.2778; that is not a forecast or download recommendation.

## Candidate strategy status

No new official third-party data source was needed for the proposals recorded in the prior review: they use layers in the competition feature stack. In this checkout, however, the actual training-feature raster and cached feature stack are absent, so none can be executed. The exact top-priority proposal cannot be selected until a coordinator records the one assigned method lane and confirms the shared template/evaluator/writer commit. Do not spend a submission slot based on a proposal or file name.

## Official and reproducible review links

These are manual-review links recorded in the project; this session did not fetch the pages, so their contents are not represented as newly reverified here:

- [DrivenData problem description and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData data tab (sign-in may be required)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [Official reference solution repository](https://github.com/drivendataorg/gems-prize-reference-solution)
- [DOE/NLR competition rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [EPSG:32611](https://epsg.io/32611)

## End-of-session run card

The machine-readable card is [`evidence/run_card_arena_b8fc7593_20261031.json`](../evidence/run_card_arena_b8fc7593_20261031.json). Its verdict is negative. The next useful work is to resolve the assigned lane/template and provenance, obtain organizer-authenticated data through the allowed channel, reconcile the complete registry/duplicate-gate rule, and repair the holdout so off-catalogue hypotheses are not judged against known-catalogue truth alone. Only then can a preregistered experiment be run and its output considered for a separate weekly selector.
