# GEMSDOEkarage1 — GEMS Prize Research and Submission Gates

> ## CURRENT FEED · 29 OCT 2026 · NEGATIVE / DO NOT SUBMIT
> **No current TIFF is cleared for competition submission.** This review generated no TIFF, ran no geological experiment or holdout, estimated no score, and selected or spent no upload slot. Existing files under `docs/downloads/` are historical research artifacts, not approvals.
>
> **Why execution is blocked:** no method lane or authoritative canonical-template assignment is recorded; the five required feature/data cache inputs are absent; and the shared-tool integrity audit finds two vendored hash mismatches and a template/source pin mismatch. The shared evaluator and writer are therefore unauthorized. Do not replace them with a private fork.
>
> **Current records:** [three-pass review](knowledge/session-review-arena-f40ee5b6.md) · [JSON run card](evidence/session_f40ee5b6_run_card.json) · [shared preflight](evidence/session_f40ee5b6_shared_preflight.json) · [template integrity audit](evidence/session_f40ee5b6_template_integrity.json).

## Start here

- [Decision dashboard](docs/index.html) — current status at the top.
- [Executive summary](docs/executive-summary.html) — nine focus sites, highest peer-reported file, source link, peer overlap and download/submit status.
- [Research slate](docs/research.html) — four ranked, unexecuted geological hypotheses and source-readiness caveats.
- [Submission guide](docs/how-to-submit.html) — future upload steps, only after every release gate passes.
- [Official-source register](knowledge/official-sources-verified-2026-10-29.md) — official claims, live-source checks, access limits, and what remains unverified.
- [Reconstructed standing brief](docs/standing-prompt.md) — not a verbatim transcript; apply it with the newer explicit instructions in the active conversation.

## Project brief and hard rules

The project studies fault prediction for the [DOE GEMS Prize](https://www.drivendata.org/competitions/306/competition-doe-gems/). The target is mapped geological faults, not proof of a geothermal vent. The official problem page specifies a single-layer float32 GeoTIFF at 100 m in EPSG:32611, on the contest bounds, with probabilities in [0, 1] and null/NaN outside the bounds. The metric is distance-weighted Tversky with α=0.2, β=0.8 and a 300 m (3-pixel) triangular kernel. See the [official specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) and [official DOE/NLR rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf).

Before any candidate can be considered:

1. Record the single assigned method lane and an authoritative canonical-template assignment. A suggested peer template is not an assignment.
2. Restore and authenticate the permitted competition data and exact data roles. The current DrivenData data route redirects to login; do not treat third-party mirrors as organizer-authenticated.
3. Reuse the canonical shared feature stack, spatial holdout evaluator, and submission writer. Do not maintain private forks. Derive catalogue features from visible faults only, mask visible-fault pixels exactly, and withhold whole buffered fault segments.
4. Use the prescribed pooled DTI (α=0.2, β=0.8, 300 m triangular kernel); test each feature alone for leakage. AUC >0.90 is a leakage stop unless explained.
5. Compare continuous surfaces against the complete registry before placement and final dots against registry rasters. Under the user's protocol, |Spearman| >0.90 or >70% of dots within 3 px means record a duplicate and stop. These are internal gates, not organizer rules.
6. Stop after at most 3 experiments or 2 hours. Every run ends with a JSON card: hypothesis, mechanism, named non-fault mimic, evaluator / withheld-positive count / 95% CI, uniqueness measures, raster SHA-256, validator results, submission name and note ≤140 characters, and promote/negative verdict. A negative result is a deliverable.
7. Do not choose a submission or spend a weekly slot. Promotion and slot selection are a separate selector step. A projection is never a score; score labels are HOLDOUT-DTI, ORGANIZER-CONFIRMED (receipt), or USER-REPORTED / UNVERIFIED.

## Executive summary — nine focus sites

The maximum numbers below were supplied by the user and are **USER-REPORTED / UNVERIFIED**, not organizer-confirmed. Each pinned peer TIFF is available for **research download only**; none is cleared to submit. “Peer overlap” is the highest directional share of a site's positive pixels within 3 px of one of the other eight pinned peer rasters. It is a discrete-dot comparison, not a continuous-surface correlation or a score. Every result exceeds the project's internal 70% stop.

| Site | Highest supplied score | Pinned peer TIFF (research download only) | Closest peer / dots within 3 px | Decision |
|---|---:|---|---|---|
| **GEMSDOE32** | **0.2778 USER-REPORTED / UNVERIFIED** | [gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE32/73485f27cf230af770167397c2b72cb9ce3b3f25/docs/downloads/gemsdoe32-h33-h33-2-b2-20261004T220000Z-e5eb6e7e-zeros.tif) | GEMSDOE24 · 100.00% | **DO NOT SUBMIT** |
| **GEMSDOE36** | 0.2750 USER-REPORTED / UNVERIFIED | [gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE36/7edcc9b58e6ad0f88c6e6f5ee9218761a391769d/docs/downloads/gemsdoe36-anderson-geothermal-pinn-38854-20261004T230000Z-9b9ea4e6-zeros.tif) | GEMSDOE27 · 97.58% | **DO NOT SUBMIT** |
| **GEMSDOE28** | 0.2710 USER-REPORTED / UNVERIFIED | [gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE28/4955e29c7b66503ba2178b25d356d713dc1bc534/docs/downloads/gems28-h36-1-rung30-blind-r1-20261003-b531dae0a36f-nan.tif) | GEMSDOE24 · 100.00% | **DO NOT SUBMIT** |
| **GEMSDOE31** | 0.2708 USER-REPORTED / UNVERIFIED | [gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE31/88ec212955353f7590e94b8ef2a9763ffa035d45/docs/downloads/gemsdoe31-h27-4-solo-d28-20261004-8acb75e1-nan.tif) | GEMSDOE24 · 100.00% | **DO NOT SUBMIT** |
| **GEMSDOE33** | 0.2632 USER-REPORTED / UNVERIFIED | [GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE33/844f514819041c7be9efd345a24cf5cd70263f00/docs/downloads/GEMSDOE33-h33d-analog-tip-stepover-r30-20261004-cb490425926e.tif) | GEMSDOE27 · 99.71% | **DO NOT SUBMIT** |
| **GEMSDOE25** | 0.2600 USER-REPORTED / UNVERIFIED | [gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE25/b13ccabae15d4951854d47cb35e17322e7537b64/docs/downloads/gems25-dotted-h19-5-d2-8-20261002-e56ea318af89-nan.tif) | GEMSDOE24 · 100.00% | **DO NOT SUBMIT** |
| **GEMSDOE30** | 0.2600 USER-REPORTED / UNVERIFIED | [gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE30/d21ddd9502f3c3911e8d77b8f1e6abfaadffc876/docs/downloads/gemsdoe30-d28-poisson300m-offcat-44090-20261003T233156Z-91eae1ca.tif) | GEMSDOE24 · 100.00% | **DO NOT SUBMIT** |
| **GEMSDOE24** | 0.2477 USER-REPORTED / UNVERIFIED | [gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE24/a73f9ffba29260cc7708e8e0557c84c5bea7d47b/docs/downloads/gems24-h25-1-dotted-h19-5-d1-5-20261002-989f59505db1-nan.tif) | GEMSDOE25 · 100.00% | **DO NOT SUBMIT** |
| **GEMSDOE27** | 0.2449 USER-REPORTED / UNVERIFIED | [gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif](https://raw.githubusercontent.com/buffedlizard55-lab/GEMSDOE27/4f34228a9f39e99da592aa34fd835c96d1b693f5/docs/downloads/gems27-topo-gap-closure-t-v2-on-d1-5-20261002-5512495c6bd1-nan.tif) | GEMSDOE24 · 98.02% | **DO NOT SUBMIT** |

**Download distinction:** the links above fetch peer-owned files for research; they are not this project's TIFFs and are not submission recommendations. The project has **zero currently cleared files**. No organizer receipt tied to the GEMSDOE32 hash is in this checkout; the [GEMSDOE32 peer page](https://buffedlizard55-lab.github.io/GEMSDOE32/docs/index.html) labels 0.2778 `OWNER-REPORT` and says no receipt links the score to the raster hash.

## GEMSDOE32 B2 — what the evidence supports

- GEMSDOE25 and GEMSDOE30 have identical 44,090-dot masks on the pinned peer rasters.
- GEMSDOE32 B2 has 37,654 dots: GEMSDOE25 minus 6,436 dots within 2 px of the mirrored catalogue; no dots were added.
- GEMSDOE36 is a strict superset of B2, adding 1,200 dots.
- These are geometry facts, not a controlled ablation. Under the official metric, removing low-yield predictions could reduce weighted false-positive cost, but could also remove withheld-fault coverage. The exact score cause and any chance to beat 0.2778 cannot be inferred from dot counts or user reports.

## Ranked pre-implementation hypotheses

Ranking is **qualitative only** (mechanistic plausibility relative to cost); no expected DTI gain or score is stated. The exact layer/contrast, mechanism, confounders and data readiness are on the [research page](docs/research.html) and in the [current review](knowledge/session-review-arena-f40ee5b6.md).

1. **CP-DPCS — Cross-Potential Dip-Polarity Co-Gradient Step** (medium): compare signed RTP magnetic phase to isostatic-gravity gradients across continuation scales beneath low-relief cover. Mimics: intrusive contacts, caldera margins, basalt edges, buried channels, survey seams. Only proposed contest-stack features; no authenticated local data or assigned lane.
2. **BERB-STC — Biharmonic Elastic Relay-Bridge Stress-Transfer Corridor** (medium–high): use fold-local visible segment endpoints with strain/seismicity, conductivity and gravity contrasts to test a relay corridor. Mimics: induced seismicity, conductive playa brines, interpolation bullseyes. The needed contest stack is login-gated; no local fold graph or holdout.
3. **WD-KRMT — Wavelet-Destriped Potassium-Residual Magnetics Trough** (medium–high): flight-line-corrected GeoDAWN radiometric residual boundary paired with a magnetic trough. Mimics: potassic intrusions, weathering, volcanic units, evaporites, survey stripes. The official [USGS GeoDAWN catalog](https://doi.org/10.5066/P93LGLVQ) lists downloadable GeoTIFF bundles (Area 1 43.57 MB; Area 2 230.54 MB); bytes, exact footprint/projection and feature overlap were not checked locally.
4. **CF-DIKA — Cross-Fan Drainage-Incision Knickzone Alignment** (high): test replicated knickzones/channel deflection across at least three adjacent catchments at a gravity step using a 3DEP DEM. Mimics: Lake Lahontan benches, fan avulsion, stream piracy, lithologic ledges. USGS lists public 1/3-arc-second CONUS coverage; tile alignment/useful resolution remains unchecked.

None is assigned as the required method lane or validated. Do not implement before data/template authorization and the full prescribed holdout/leakage/uniqueness sequence.

## Official source and access notes

- [DrivenData problem page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) — target, metric, input description and output format.
- [DrivenData data tab](https://www.drivendata.org/competitions/306/competition-doe-gems/data/) — redirects to account login in this review; official feature/label/template bytes were not obtained.
- [DrivenData public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/) — 29 Oct 2026 snapshot: #1 0.4544, #47 0.3195. The public top 50 does not verify these nine peer reports and is not the private/final score.
- [DOE/NLR rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf) — three submissions per week, one final set selected, original work, and generative-AI disclosure where applicable.
- [USGS GeoDAWN ScienceBase release](https://doi.org/10.5066/P93LGLVQ) — official catalog lists public airborne magnetic/radiometric grids, line data and GeoTIFF bundles; USGS states CC0 rights. File payload and local suitability are not tested here.
- [USGS 3DEP products/services](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) — product coverage varies; seamless 1/3-arc-second coverage is listed for the lower 48, while 1 m coverage is limited/expanding.

See [line-by-line source notes](knowledge/official-sources-verified-2026-10-29.md). No contest or USGS payload was downloaded in this review.

## Validation and submission status

The current shared preflight reports `ready_for_shared_tools: false` and `ok_to_submit: false`. Missing inputs: `feature_stack.npy`, `existing_faults.tif`, `training_features.tif`, `sample_submission.tif`, `labels.tif`. Method lane and canonical-template assignment are absent. Two vendored files do not match their recorded SHA-256 pins; do not silently repin or fork them. No holdout, validator output, candidate raster/hash, or organizer receipt exists for this review.

The submission subpage is [`docs/how-to-submit.html`](docs/how-to-submit.html). It is for future use only: do not upload a historical or research raster, do not spend a weekly slot, and do not call a local format check organizer acceptance.

## Preserved mainline research TIFFs — not submission approvals

The mainline sync added several prior-session research rasters and their receipts. They are **not** products of this review, and this review did not rerun or promote them. The renderer verifies each selected file’s SHA-256 against its linked run card; that byte match is not scientific validation or permission to upload. All linked cards are negative / `ok_to_submit: false`.

- **Novel-territory dots:** [research TIFF](docs/downloads/gems-karage1-unique-novelterritory-20261029T120000Z-5a6b7c8d-zeros.tif) · [run card](evidence/run_card_gems-karage1-unique-novelterritory-20261029T120000Z-5a6b7c8d.json). Its literal dot-overlap scan is limited to the references in that card; no HOLDOUT-DTI or pre-placement continuous-surface check was run, no method lane was assigned, and the scan is not a complete organizer registry.
- **HGRID strain:** [research TIFF](docs/downloads/karage1-hgridge-strain-K37654-20261029T181321Z-zeros.tif) · [run card](evidence/hgridge_run_card_20261029T181321Z.json). The `HOLDOUT-DTI` intervals from `gems57-pooled-hide-v2` overlap the random control; no measurable skill over random is reported. The same card records a literal lattice-overlap stop. See the card for both arms, withheld-positive count and 95% CIs; these are not organizer scores.
- **Damage-zone halo:** [research TIFF](docs/downloads/karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.tif) · [run card](evidence/run_card_karage1-halo-damagezone-d2p0-20261029T181947Z-zeros.json). Format checks pass, but HOLDOUT-DTI and measured registry uniqueness are absent; “structurally unique by design” is not a measured clearance.
- **Convection-cell upflow:** [research TIFF](docs/downloads/karage1-convect-cell-upflow-20261029-zeros.tif) · [run card](evidence/session_convect_20261029_run_card.json). Format-valid; no HOLDOUT-DTI, assigned lane or registry-clearance result.
- **Geothermal surface (GSE):** [research TIFF](docs/downloads/karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif) · [run card](evidence/run_card_gse_exp1.json). No HOLDOUT-DTI, assigned lane or completed uniqueness gate.
- **Conduitcrest:** [research TIFF](docs/downloads/gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4-zeros.tif) · [run card](evidence/run_card_gems-karage1-novelterr-potentialfield-conduitcrest-20261028T000000Z-a1b2c3d4.json) · [superseding lattice audit](evidence/conduitcrest_lattice_reaudit_20261028.json). The saved-byte audit finds a lattice duplicate; the earlier HOLDOUT-DTI claim has no 95% CI and is not release-grade.

These are selected recent examples, not an exhaustive inventory. Other historical TIFFs remain under [`docs/downloads/`](docs/downloads/). **DO NOT SUBMIT any of them.** A research download is not a submission-ready file, an organizer receipt, or a slot decision.

## Recent review history

- **Current:** [29 Oct 2026 review `arena/f40ee5b6`](knowledge/session-review-arena-f40ee5b6.md) and [run card](evidence/session_f40ee5b6_run_card.json).
- **Previous:** [four-hypothesis / preflight review `arena/4711a029`](knowledge/session-review-arena-4711a029.md) and [run card](evidence/session_4711a029_run_card.json).
- **Historical candidate audits:** [nine-site/B2 review `arena/1668dda0`](knowledge/session-review-arena-1668dda0.md); [DIPDUAL negative experiment `arena/147b0f11`](knowledge/session-review-arena-147b0f11.md); [forensic/site audit `arena/9ca08e2e`](knowledge/session-review-arena-9ca08e2e.md). These records may contain prior claims and are not a current approval.
