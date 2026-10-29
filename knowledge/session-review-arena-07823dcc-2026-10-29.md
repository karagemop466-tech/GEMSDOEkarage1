# Repository review — `arena/07823dcc-gemsdoekarage1` — 29 October 2026

## Decision

**NEGATIVE / DO NOT SUBMIT.** This review generated no GeoTIFF, ran no geological experiment or HOLDOUT-DTI, made no leaderboard estimate, and selected or spent no competition slot. There is no file in this checkout cleared for download and submission. The requested new high-scoring TIF cannot be responsibly certified from the evidence/access available in this session.

The reason is procedural as well as scientific: the prompt's “single method paragraph” assigning the lane is absent, and `registry/template.json` has both `method_lane` and `canonical_template_assignment` set to `null`. The competition data and cached feature stack are also absent. Choosing an experiment or privately rebuilding the shared evaluator/writer would violate the supplied parallel-run protocol.

## Pass 1 — inspect and verify

- Read `README.md`, `AGENTS.md`, `docs/standing-prompt.md`, current site renderer, prior session review/run-card, registry/template declaration, evidence inventory, and the relevant test suite.
- Current branch: `arena/07823dcc-gemsdoekarage1`; worktree was clean before review changes. The source tree has no `data/` or `.cache/gems_work/feature_stack.npy`; there is no authenticated DrivenData data access in this session.
- The current template assignment is unresolved (`registry/template.json`: `method_lane: null`, `canonical_template_assignment: null`). Prior candidate and holdout receipts are historical and do not assign this session a lane.
- Historical mirrored rasters and candidate outputs exist under `docs/downloads/`, but historical reports establish neither organizer-authenticated data provenance nor a current release clearance. The highest supplied focus-site value, `0.2778` for GEMSDOE32 B2, remains `USER-REPORTED / UNVERIFIED`; no receipt tied to its raster hash is in this workspace.
- Installed the declared runtime/test requirements into ignored `.venv/` and ran `.venv/bin/python -m pytest -q`: **365 passed, 0 failed, 119 Rasterio/Affine PendingDeprecationWarnings**. This is software verification only, not geological evidence or a score.
- Repaired the public renderer's stale status copy: it now names this review as current, links the current negative JSON card, and calls the prior 1668dda0 byte audit historical. A previously generated BB-STEP artifact is no longer described as “Generated this session.”

## Pass 2 — adversarial review

1. **No unique TIF claim.** The user requires a new TIF but also requires the assigned lane, pre-placement surface correlation, final-dot overlap against every registry raster, leakage canaries, and a properly buffered holdout. No assigned lane, feature cache, authenticated data, or complete current registry is available. A format-valid historical file is not a substitute. No new file was fabricated or exposed as submit-ready.
2. **No score projection.** The historical `0.2778` is neither an artifact-linked organizer receipt nor a local HOLDOUT-DTI. The current `0.3195`/other leaderboard statements in earlier prompt text are not adopted as current facts; the official-source register saved in the repository records a 2026-10-29 public snapshot and identifies the discrepancy. No fresh access to DrivenData is claimed here.
3. **No false novelty.** The repository already contains multiple candidate slates (including SBPF-PC, TRDS-Bridge, GD-MAD, 3DEP-DFA, CP-DPCS, BERB-STC, WD-KRMT, CF-DIKA, magnetic texture change points, and edge-network severance). Some adjacent mechanisms are implemented in local feature code. The complete parallel-site/registry inventory is unavailable, so none can honestly be labelled “not tried anywhere” merely by renaming it. A shortlist is provided below as proposal-only; its novelty is explicitly unverified.
4. **External-source gate.** The established sources are official source leads (DrivenData specification/data page; USGS GeoDAWN and 3DEP; GDR INGENIOUS; NLR rules PDF). Data-tab access is login-gated, and this environment did not freshly fetch USGS/NLR/GDR. A source URL is not evidence that the payload is obtainable, correctly covered, or organizer-authenticated. No external-data-dependent candidate is called ready.
5. **Portal acceptance remains unknown.** The exact rejected TIF that caused “Predicted values must be in range [0, 1]” is not retained. Historical validators cannot identify that incident's cause or guarantee DrivenData will accept another artifact. No live submission form/quota was available to this review.

## Pass 3 — candidate hypotheses and requirement recheck

The following are **research proposals / re-ranked prior ideas**, not newly verified discoveries, lane assignments, score forecasts, or permission to implement. Their existence in earlier repository sessions means “not tried in this whole parallel project” cannot be certified. All could be tested only after the owner supplies a method paragraph, the authoritative shared template/cache, and a complete registry. Ranking is qualitative expected upside relative to cost; no numerical DTI gain is predicted.

| Rank | Candidate and layers | Targeted signature and off-catalogue rationale | Difference from prior local approaches | Named non-fault mimic | Cost / source and readiness |
|---|---|---|---|---|---|
| 1 | **Sub-alluvial signed phase/step concordance** — existing mirror stack: `depth_to_base_surf`, `iso_grav_anom` and its horizontal/vertical gradients, `rtp`, `tmi_hg`/`tmi_vg`, conditioned on `det_elev_slope` and `det_elev`. | A persistent, cross-scale magnetic/gravity edge paired with a consistent basement-depth step under low-relief basin fill may identify buried displacement where surface scarps are absent. | Tests signed, cross-scale phase and throw-polarity agreement rather than unsigned NMS ridge strength or a simple catalogue-distance mask. It is adjacent to the existing SBPF-PC proposal, not a certified novel family. | Buried paleochannels, unfaulted intrusive/pediment contacts, basalt-flow margins, survey tie-line seams. | Low–medium compute, but depends on absent/authentication-unverified feature stack and lane. No external data source needed if the official stack is restored. **Proposal-only; unvalidated.** |
| 2 | **Magnetic texture change-point across paired windows** — `rtp`, `tmi`, `tmi_hg`, `det_elev_slope`. | A discontinuous change in directional semivariogram/correlation length across a candidate boundary could reveal juxtaposed magnetic fabrics without requiring a strong anomaly peak or scarp. | Measures second-order texture statistics rather than gradient magnitude or local ridge scores. This was previously proposed in session a1ef4ce0, so it is not new to the repo. | Lithologic contacts, volcanic texture boundaries, interpolation seams and flight-line artifacts. | Medium compute; internal layers only. Data authenticity unresolved. **Proposal-only; not validated here.** |
| 3 | **Cross-cutting magnetic marker termination network** — `rtp`, `tmi_hg`, `tmi_vg`, `iso_grav_anom_hg`. | Repeated terminations/offsets of independent magnetic marker edges aligned along a gravity-supported corridor could indicate a buried fault that offsets markers but has weak expression of its own. | Uses graph-level cross-cutting/termination topology and a rotated-network null, not just edge intensity or an extrapolated mapped-fault tip. This mechanism was previously proposed; not novel to the repo. | Airborne survey seams, intrusive contacts, lava-flow boundaries, interpolation gaps. | Medium–high compute; internal layers. Requires seam controls and an authorized holdout. **Proposal-only; not validated here.** |
| 4 | **Destriped K/eTh–magnetic trough boundary** — `rtp`, `tmi_hg`, `cond_surf`, `det_elev_slope`, plus official GeoDAWN K/eTh grids and flight-line metadata. | A narrow magnetic trough co-located with a destriped K/eTh alteration boundary could target hydrothermal alteration on degraded or buried fault zones. | Explicitly removes directional acquisition stripes and targets a narrow boundary, rather than a broad radiometric plume. Related GD-MAD/WD-KRMT work is already proposed in the repository. | Potassic intrusions, ash-flow tuff contacts, playa evaporites, flight-line leveling stripes. | Medium–high and **data-blocked** here. Official source lead: [USGS GeoDAWN](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and); current payload acquisition/coverage was not checked in this session. **Not viable until source bytes and coverage are verified.** |

### Why the reported GEMSDOE32 B2 value may have been higher

The repository's pinned-mirror mask audit reports a lineage: B2 has the same positive-pixel support as the GEMSDOE25/30 dotted parent after removing a 2-pixel neighborhood around the mirrored known-fault raster. The cited `0.2778` remains **USER-REPORTED / UNVERIFIED**, and the sources are owner mirrors rather than authenticated organizer bytes. This is an observed geometry relationship, not a causal explanation.

Under the competition's documented distance-weighted Tversky metric, deletion can improve the score only if the removed predictions' weighted false-positive contribution exceeds the true-positive coverage they supplied. Exact mask counts cannot reveal hidden-label false positives/recall. The plausible interpretation is a precision–recall tradeoff that may have favored a less dense map; it cannot be established without a paired common-fold holdout and a file-linked organizer receipt. It is scientifically possible to beat 0.2778, but no defensible leaderboard estimate or result is available now.

## Concurrent mainline artifact found during PR synchronization

A separate mainline change introduced `karage1-gse-geothermal-surface-24000dots-20261029T181229Z-798b0455-zeros.tif`. This was **not generated by the review above**, and it is not cleared for submission. I audited the saved bytes after discovering it:

- SHA-256 `f5879e1902e6c15407582a67e210bacfd0b2425570c4aefbdf5c585a4579c37b`; one-band float32 GeoTIFF; shape 3730×3292; EPSG:32611; 100 m transform matching the two newly tracked mirrored reference rasters; all raster values finite in [0,1]; 24,000 positive pixels. These are local byte facts, not organizer template/footprint verification.
- Its `-zeros.tif` outside encoding cannot be compared to the real footprint because `sample_submission.tif` is absent. The official-format source describes outside-bound values as null/NaN; the candidate has no nodata value and is all-finite, so the outside-format gate is unresolved.
- Against the two newly tracked mirrors, directed 3-px overlaps are 17.60% vs `GEMSDOE25_d28.tif` and 17.15% vs `GEMSDOE32_B2.tif`; absolute binary-support rank correlations are 0.0048 and 0.0056. This two-file measurement is not a complete registry check and does not validate uniqueness.
- The inherited `evidence/uniqueness_gse_exp1.json` names a candidate ending `181134Z`, while the saved file and sidecar name it `181229Z`; their SHA-256 values match, but the name discrepancy is a provenance irregularity. The receipt compares only 11 local Karage1 candidate rasters; it does not include the nine focus-site GEMSDOE rasters or the pinned lattice, and has no pre-placement surface-correlation result.
- The inherited experiment card has no HOLDOUT-DTI, evaluator, withheld-positive count, or CI. Its “leakage canary” reports point-biserial correlations, not the required per-feature AUC. External input payloads are absent, so the named layer provenance cannot be reproduced in this checkout.

Full measurements and limits: [`evidence/gse_concurrent_artifact_reaudit_20261029.json`](../evidence/gse_concurrent_artifact_reaudit_20261029.json). The file is linked on the site for audit only with an adjacent **DO NOT SUBMIT / uniqueness unproven** status. No new holdout run or release decision was made.

## Follow-up blockers (in order)

1. Provide the exact assigned method paragraph and identify the canonical shared template/evaluator/writer owner. Do not infer a lane.
2. Restore and authenticate official `training_features.tif`, `labels.tif`, `existing_faults.tif`, and `sample_submission.tif`; compare saved hashes and geometry with any third-party mirror. The data tab is [DrivenData login-gated](https://www.drivendata.org/competitions/306/competition-doe-gems/data/).
3. Reconcile the internal literal 70%/3-px threshold with the dense lattice witness. It is a user-provided internal protocol gate, not an official organizer requirement. Do not evade it by jittering or relabelling the witness.
4. Obtain a complete, immutable registry inventory and frozen same-evaluator holdout baseline.
5. Only then preregister one assigned-lane candidate; test each feature alone for leakage; run whole-segment buffered hide-and-recover with fold-local catalogue features, exact visible-fault masking, pooled DTI (α=0.2, β=0.8, 300 m triangular kernel), and a 95% CI. Stop by the 3-experiment/2-hour cap.
6. Compare continuous surfaces before placement and final dots after placement against every registry raster; validate reopened GeoTIFF bytes (footprint range [0,1], no NaN/mask inside, CRS/shape/transform, outside encoding) and record SHA-256. A separate selector may check weekly quota only after every gate passes.

## Source links for review

- [Competition problem, metric and submission format](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [Competition data tab (login-gated)](https://www.drivendata.org/competitions/306/competition-doe-gems/data/)
- [Official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [DrivenData reference solution](https://github.com/drivendataorg/gems-prize-reference-solution)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [USGS 3DEP program](https://www.usgs.gov/3d-elevation-program)
- [GDR INGENIOUS compilation](https://gdr.openei.org/submissions/1391)
- Repository's dated source audit (prior session; not a fresh fetch): [`knowledge/official-sources-verified-2026-10-29.md`](official-sources-verified-2026-10-29.md)

## Run card interpretation

The companion JSON card deliberately records null values for HOLDOUT-DTI, raster SHA-256, registry correlation/overlap, and raster validation: none were computed in this review. Its negative verdict is a workflow decision, not a negative score. Software tests are not model performance.

Final pass: after updating the fail-closed renderer and adding a regression assertion for the current review links, `.venv/bin/python -m pytest -q` passed **366 tests** (119 pending-deprecation warnings), `git diff --check` passed, the site was regenerated deterministically, and JSON/HTML assertions confirmed that the current decision pages say **DO NOT SUBMIT** and link to this review/card.
