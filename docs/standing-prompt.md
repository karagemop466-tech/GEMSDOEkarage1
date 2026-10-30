# Standing project brief — read at the start of every session

**Provenance:** This is a normalized, consolidated record of the user's standing requirements, not a verbatim transcript of the full chat prompt. The README preserves this brief and points here for the complete project checklist. Apply newer explicit user instructions when they supersede this record; never claim that a historical reconstruction is the original wording.

## Goal and values

- Build an evidence-led project for the [DrivenData DOE GEMS Prize](https://www.drivendata.org/competitions/306/competition-doe-gems/) and maximize the probability of winning by finding faults indicative of geothermal resources.
- Core values: **“Maximize P(Win)”** and **“Own the Outcome.”** Report negative results, blocked access, irregularities, and uncertainty directly.
- The requested end product is a genuinely new, unique, valid, submission-eligible single-band float32 GeoTIFF with values in `[0,1]` and the official grid/CRS/transform. Never claim it is ready unless every scientific, provenance, format, and uniqueness gate passes.
- Make download/submission status unmistakable at the top of the site. Preserve old rasters for education/audit only; do not copy or resubmit prior predictions.
- Do not make a leaderboard projection. A user-reported result is not an organizer receipt or a HOLDOUT-DTI measurement.

## Nine focus sites and score labels

GEMSDOE24, GEMSDOE25, GEMSDOE27, GEMSDOE28, GEMSDOE30, GEMSDOE31, GEMSDOE32, GEMSDOE33, and GEMSDOE36 are the comparison sites. The reported GEMSDOE32 B2 value `0.2778` is **USER-REPORTED / UNVERIFIED** until tied to an organizer receipt. Use `registry/user_reported_scores_20261029.json` for the preserved historical list; do not infer that any listed file is eligible, unique against the full fleet, or scoreable by our proxy.

As directly observed on the public leaderboard on 30 October 2026, rank 1 was `0.4544`, rank 48 was `0.3195`, and `0.4413` did not appear in the visible top 50. Label these only **ORGANIZER-PUBLISHED / PUBLIC LEADERBOARD SNAPSHOT (2026-10-30)**. The page can change; recheck before making a current claim. The public board is not the private/final prize score.

## Required science and evidence

- Explain GEMSDOE32 B2 at PhD level using verified geometry, the official metric, and clearly separated hypotheses. Do not claim that its reported score is causal or confirmed without the artifact-linked organizer receipt and a controlled test.
- Before any geological implementation, produce 3–5 specific geological hypotheses. Each must state exact layers, a physical signature, why it can reveal faults missed by the catalogue, how it differs from work already implemented, named non-fault mimics, data source/availability, and relative expected improvement versus implementation cost. Rank qualitatively unless a valid experiment supports numbers; a rank is not a score estimate.
- Choose only the top candidate for the assigned lane and validate it on a spatially blocked hide-and-recover holdout before any slot is considered. Hold out whole fault segments with a buffer. Derive catalogue features only from visible training faults; mask visible known-fault pixels exactly. AUC above `0.90` for any feature alone is a leakage alarm until resolved.
- Pool DTI with `α=0.2`, `β=0.8`, and a 300 m triangular kernel. Every holdout result must name its evaluator, withheld-positive count, and 95% CI. Keep HOLDOUT-DTI, USER-REPORTED, and ORGANIZER-CONFIRMED / ORGANIZER-PUBLISHED classes distinct. Never translate holdout DTI into a leaderboard estimate.
- Verify the continuous surface against registry rank correlation before placement and final dots against the registry afterward. Stop and log a duplicate if `|Spearman ρ| > 0.90` or more than `70%` of dots fall within 3 pixels of any registry raster. Do not jitter, hole-fill, or exempt an inconvenient witness.
- Respect one owner-assigned method lane; never invent a lane. Reuse the canonical shared template's cached feature stack, `evaluate_holdout.py`, and `submission_writer.py`. Fix shared tools in their owning template; do not create a private fork or repin mismatched files without upstream review.
- Maximum `3` experiments or `2` hours. Do not select or spend a weekly competition slot. Promotion and slot selection are separate steps after every gate passes.
- End experiment/review work with one machine-readable JSON run card: hypothesis, mechanism, named non-fault mimic, HOLDOUT-DTI plus evaluator/count/95% CI or `NOT RUN`, registry correlation/overlap or `NOT RUN`, raster SHA-256 or `null`, validator output, submission name/note (each ≤140 characters, or `null`), verdict, and slot status. A negative card is a valid deliverable.

## Official format and source discipline

- Official problem page: EPSG:32611 (WGS 84 / UTM zone 11N), 100 m, same study bounds, one float32 band, values in `[0,1]`, null/NaN outside bounds.
- Verify every competition claim against an official source and link it. External data must be free, official/verified, licensed for the intended use and sharing, and checked for actual availability and spatial coverage before being treated as viable. A public metadata page or a byte-identical mirror alone does not establish organizer provenance.
- The official DrivenData data page redirected to login in the 30 October 2026 sandbox check. No authenticated challenge inputs were available in that session.
- The [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) reports CC0 rights. The [GDR INGENIOUS compilation](https://gdr.openei.org/submissions/1391) reports public access and CC BY 4.0. A source link is not proof that its payload was downloaded or its coverage validated.
- Read the current [DOE/NLR official rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf), including the single final submission used across prize rounds, weekly feedback limit, and disclosure of generative-AI use where applicable.

## Delivery and review workflow

- At every session start, read `AGENTS.md`, `README.md`, this file, and the latest dated review/run card. Update current-status artifacts and visible pages together; explicitly label older reviews as historical.
- Work in three passes: (1) implement and verify, (2) adversarial review and fix, (3) recheck requirements, tests, site links, and deterministic output.
- Flag irregularities and limitations. Do not claim portal acceptance without an organizer result/receipt. If data or protocol gates fail, stop and report the block rather than fabricating a candidate.
- Preserve the standing prompt in README, create a PR from the assigned Arena branch, and merge only after local/CI verification when the task requests it.

## Current repository status snapshot (30 October 2026)

The current review is `knowledge/repository-review-2026-10-30.md` with run card `evidence/session_f077a66c_run_card.json`. Its result is negative: lane/template assignment is absent, required input/cache files are missing, two vendored hashes mismatch their recorded provenance, no experiment or TIFF was produced, and no file is cleared. The official-source register is `knowledge/official-sources-verified-2026-10-30.md`.
