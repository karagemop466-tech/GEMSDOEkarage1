# GEMSDOEkarage1 — fault-prospectivity research and submission desk

> **Submission decision (2026-10-27 UTC): DO NOT SUBMIT.** This checkout contains no competition rasters, cached feature stack, holdout evaluator, submission writer, registry rasters, or GeoTIFF candidate. No valid or unique submission can be produced or certified from the files currently present.

## Start here on every project session

Read this README first, then the [Executive Summary](executive-summary.html) and [`run-card.json`](run-card.json). This README is the durable project charter: it preserves the mission, Core Values, every distinct protocol gate, provenance caveats, current source findings, and unresolved blockers so later work does not rely on chat history.

## Mission and decision principles

Build an auditable workflow for discovering faults that may be relevant to geothermal prospectivity, evaluating hypotheses without leakage, and producing a competition-format probability GeoTIFF **only after** validation. Fault detection is not the same task as directly predicting geothermal vents; a fault-prospectivity score must not be described as vent probability.

- **Maximize P(Win):** prefer measured, spatially independent improvement over a plausible story or a leaderboard projection.
- **Own the Outcome:** report negative results and blockers plainly; do not hide missing evidence or submit an unvalidated artifact.
- Never copy a prior raster as a candidate. A file name, a different timestamp, or a different nodata encoding does not establish raster uniqueness.
- Keep the parallel-run method lane, holdout, leakage, novelty, and experiment-budget gates. No submission slot is used here.

### Required experiment and release gates

1. Fix the experiment method lane and evaluator version before an experiment. The supplied prompt refers to a “single method paragraph,” but does not identify one; this ambiguity is logged rather than guessed.
2. Use the shared cached feature stack, `evaluate_holdout.py`, and `submission_writer.py`. Do not create a private replacement. None of those files exists in this checkout.
3. Use hide-and-recover validation that withholds whole fault segments and a buffer; derive catalogue-based features only from visible faults and mask visible faults pixel-exactly. The requested pooled DTI settings are **user-specified protocol parameters**, not independently verified official rules: alpha 0.2, beta 0.8, a 300 m triangular kernel.
4. Test each feature alone as a leakage canary; treat AUC above 0.90 as leakage until demonstrated otherwise. These are protocol thresholds, not score results.
5. Report every actual score as either `HOLDOUT-DTI` with evaluator version, withheld-positive count, and 95% CI, or `ORGANIZER-CONFIRMED` with a submission-page receipt. Do not present a projection as a score.
6. Check uniqueness against every available registry raster both before placement and on the final dots: rank-correlation threshold 0.90; dot overlap threshold 70% within 3 px. If a threshold is exceeded, record a duplicate and stop. The registry rasters are not present here.
7. Do not promote to a competition slot in this research lane. Promotion is a separate selector decision subject to the competition's weekly cap.
8. Stop at the supplied limit of 3 experiments or 2 hours. No experiment was run in this checkout because its data and shared tools are absent.
9. End any experiment report with exactly one JSON run card containing the hypothesis and mechanism, named non-fault mimic, versioned HOLDOUT-DTI plus 95% CI (or null if not run), registry correlation and 3-px overlap, raster SHA-256, automated validator output (footprint NaN status, [0,1] status, single-band and CRS/shape/transform match), submission filename, submission note of at most 140 characters, and `promote` or `negative` verdict. Do not make validation depend on human inspection; report automated irregularities. A negative/no-run card is valid and must not be dressed up as a score.

## Repository review — verified local state

At the start of this review, `git ls-tree -r HEAD` contained only `README.md`, a one-line project title. There was no `data/` directory, code, tests, site, `sample_submission.tif`, feature raster, label raster, cached stack, `evaluate_holdout.py`, `submission_writer.py`, submission registry, or prior TIF. Thus the earlier statement that data placement is the single remaining blocker is **not supported by this checkout**: even after data placement, the shared code and validation artifacts would still need to be supplied or restored.

This review adds a static status page and an executive summary with a client-side source feed. On page load (or explicit refresh), `site-feed.js` queries the public GitHub API, follows the latest nine-site report linked from the GEMSDOE32 README, requires exactly nine parsed site rows, and shows artifact identifiers plus score-free source-reported novelty/decision summaries. It deliberately suppresses historical score values and never links a prior TIFF. This is an owner-maintained project-status feed, not an organizer feed or leaderboard poll; API/parser failures are shown rather than silently presenting old data as current. The GitHub API CORS/raw response and nine-row, score-suppression parser were smoke-tested in this sandbox; browser execution after Pages publication remains to be confirmed. The download control remains disabled and no synthetic GeoTIFF is presented as a competition submission.

## What is known about the reported H33 result

The public [`GEMSDOE32` source repository](https://github.com/buffedlizard55-lab/GEMSDOE32) was inspected through GitHub. Its [`why-02778` forensic note](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/research/why-02778-analysis-20261025.md) explicitly classifies the historical H33 portfolio value as **OWNER-REPORT**, not `ORGANIZER-CONFIRMED`; it says there is no saved submission-page receipt binding that score to the submitted raster bytes. The note describes H33 as the endpoint of a nested H19-5 lineament-thinning/pruning family: thinning and a known-fault-distance exclusion could plausibly remove redundant or low-credit dots, lowering false-positive mass while preserving kernel coverage. This is a metric-based mechanism hypothesis, not proof of causality or geological generalization. The [`H33 hypothesis audit`](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/research/h33-hypotheses.md) also records that several H33 candidate families were already implemented and measured.

The same repository's [refreshed nine-site review](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/research/h48-fbgr-results-and-nine-site-executive-summary-20261027.md) reports that the nine historical site highs are one nested H19-5 family and fail the requested dot-overlap novelty gate. Its H33 forensic note says the reported H33 value is not a HOLDOUT-DTI result and supplies no organizer receipt; this is an evidence gap and does not establish the cause or validate the historical result. These are owner-maintained audit findings; this checkout did not download or independently recompute those site rasters. Therefore no prior H33 file is endorsed for submission, and no new leaderboard score can be estimated from this evidence.

The latest `GEMSDOE32` source run card (`H48-1-FBGR`, [JSON](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/docs/data/latest-run-card.json)) is a separate, existing research experiment—not this session's result. It reports **HOLDOUT-DTI** on `GEMSDOE32-HIDE-RECOVER-v3.0` (22,232 withheld positives; 95% CI) of `0.115341 [0.100168, 0.130524]`; its prevalence-calibrated off-catalogue **HOLDOUT-DTI** on `GEMSDOE32-SGMC-CAL-v3.0` (62,703 positives; 95% CI) is `0.056798 [0.050345, 0.063015]`, below the source incumbent. The report records a leakage-canary pass and a GeoTIFF format pass, but the literal unexempted registry comparison fails and the source verdict is negative / DO NOT SUBMIT. The source session used its three-experiment budget. These values are quoted from that source card, not reproduced here; no file from that repository is copied or offered.

The prompt gives conflicting descriptions of the current competition high score. The live leaderboard was not refreshed in this checkout; the source repository contains an older timestamped snapshot, which is not current evidence. Historical score values are intentionally not presented as verified scores: source records classify them as OWNER-REPORT, and no receipt was supplied here.

## Verified reference material and source status

The official [DrivenData reference-solution repository](https://github.com/drivendataorg/gems-prize-reference-solution) was inspected. Its README says to download competition data from DrivenData into `data/` and run its notebook. The reference [U-Net / Monte Carlo cross-validation notebook](https://raw.githubusercontent.com/drivendataorg/gems-prize-reference-solution/main/unet-mc-cv-reference-solution.ipynb) describes a multi-channel fault-detection baseline and, in saved notebook output, reports 19 feature bands including magnetic, gravity, topographic, geodetic-strain, seismic, and subsurface layers. The notebook output is not a substitute for the actual raster metadata in this checkout.

The competition, USGS, INGENIOUS, PDF, and third-party site links below were supplied in the request but were not independently fetched in this review. They are listed for source review, not as claims that their current contents or scores were verified:

- [DrivenData competition overview and rules](https://www.drivendata.org/competitions/306/competition-doe-gems/)
- [DrivenData problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData about page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/)
- [DrivenData data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [DrivenData leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/)
- [USGS GeoDawn survey data page](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GBCGE INGENIOUS project](https://gbcge.org/current-projects/ingenious/)
- [Competition submission PDF URL supplied in the request](https://docs.nlr.gov/docs/fy26osti/96647.pdf) — its current redirect/status was not checked; host spelling should be reviewed.
- [EPSG:32611 reference](https://epsg.io/32611) — linked by the request; confirm the exact CRS against the competition sample raster.

## Next work, in safe order

1. Restore the shared template files and a documented provenance manifest; do not rebuild holdout/evaluator/writer tools in this repository.
2. Place the authorized competition inputs (`training_features.tif`, `labels.tif`, `sample_submission.tif`, and, if required by the current dataset release, `1m_DEM_links.csv`) in the documented data location. The user reports that DrivenData access requires sign-in; this checkout has no credentials or competition files.
3. Verify feature descriptions, CRS, shape, transform, footprint, nodata, and labels from the actual files—not from old notebook output or a web-page screenshot.
4. Resolve the missing method-lane paragraph, audit the cross-site prior art, and restore the registry. Only then choose one genuinely eligible hypothesis and run it with the shared, version-pinned holdout, per-feature canaries, CI, and novelty checks. The current candidate screen contains blocked or overlap-risk ideas and is not authorization to experiment.
5. Only after a candidate beats the current holdout best and passes all format/uniqueness checks should the separate selector consider a weekly submission slot. Record any organizer score only from its receipt.

The GitHub Pages repository setting is already configured to publish the `main` branch root (`https://karagemop466-tech.github.io/GEMSDOEkarage1/`); the new static pages are designed for that source. Publishing depends on the PR landing on `main` and GitHub Pages completing its build.
