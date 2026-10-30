# Repository review — `arena/f077a66c-gemsdoekarage1` — 30 October 2026

## Executive decision

**NEGATIVE / DO NOT SUBMIT.** This session made a repository/CI and public-status review only. It generated no candidate TIFF, ran no geological experiment or holdout, made no leaderboard estimate, and selected or spent no weekly slot. No file is cleared for submission.

That is a deliberate fail-closed result, not completion of the user's scientific objective. `registry/template.json` still has no assigned method lane or canonical shared-template assignment. The shared-tool preflight fails: required competition inputs and the authorized feature cache are absent, and two vendored files do not match their recorded source hashes. Do not invent a lane, rebuild or privately fork the shared writer/evaluator, repin those files, restore a large mirror bundle just to satisfy one test, or generate a purported submission around these gates.

**Current source of truth:** [`evidence/session_f077a66c_run_card.json`](../evidence/session_f077a66c_run_card.json), mirrored for the published site at [`docs/data/current-review.json`](../docs/data/current-review.json). Historical cards and TIFFs remain research/audit artifacts. A historical run card named `docs/data/latest-run-card.json` is not this session's latest review and is now labeled as an archived run card in the site.

## Pass 1 — inspect and verify

- Reviewed `AGENTS.md`, the README and standing brief, current session/run-card records, `registry/template.json`, preflight output, relevant site generators, generated home/submission pages, CI, the failing raster test, and the hash-pinned data-restoration policy.
- `python scripts/shared_tools.py preflight` exited **1** and returned `execution_authorized: false`, `ready_for_shared_tools: false`, and `ok_to_submit: false`.
- Preflight identifies no method-lane or canonical-template assignment; absent `.cache/gems_work/feature_stack.npy` and four inputs (`existing_faults.tif`, `training_features.tif`, `sample_submission.tif`, `labels.tif`); and a vendored-source/execution-template identity mismatch. It also reports:
  - `vendor/gems57/submission_writer.py`: expected SHA-256 `41220185ac2823fe5358603d38f2a915ea3e5f1ab1f94f0b237295b38b4a2565`; actual `73b8d88f4e49f039a70254ce5a22dfe9729a8d0cae607a74c4416ace9e12039d`.
  - `vendor/gems57/uniqueness.py`: expected `1c5094b814277ae801ccea6a47cf744429cffcdc10f9cc79f229d5fc44a8df95`; actual `415a90b9fadc8308c9c9f6fd44b57ca73ffc1b32667187bea16b0f30a6b263bc`.
- Before edits, the test suite was **431 passed, 1 failed, 1 skipped**. The only failure tried to load `data/bridge/existing_faults.tif`, absent in a clean checkout. CI installs requirements and runs pytest without restoring that data.
- A direct fetch of the official DrivenData data tab redirected to login; no authenticated challenge files were obtained. The pinned-mirror restore utility documents that hashes prove mirror consistency, not organizer provenance. No data were restored.
- Fresh direct reads of the public leaderboard show **0.4544 at rank 1** and **0.3195 at rank 48**; the latter had been rank 47 in an earlier 29 October snapshot. The shown top-50 rows do not include 0.4413. These are **ORGANIZER-PUBLISHED / PUBLIC LEADERBOARD SNAPSHOT** values, not scores for this repository.
- The nine focus-site value **0.2778 for GEMSDOE32 B2** remains **USER-REPORTED / UNVERIFIED**. No artifact-linked organizer receipt was found or created.

## Pass 2 — changes and adversarial review

### Hermetic raster regression

The offline test now checks the candidate and its zeros twin from their saved bytes alone (single-band float32, pinned grid metadata, value range, NaN/zero twin consistency, and expected positive-pixel count). The separate geometric assertion against the mapped-fault catalogue explicitly skips when its two required rasters are not present. If the data are present, the test still loads and validates the grid and runs the catalogue-distance check; it does not swallow bad data or treat a skip as a scientific result.

No challenge data were downloaded for this fix. No fixture, mirror, or private tool fork was introduced.

### Status freshness

The existing public “current/latest” labels had four different historical sources: an HGRID card, the `fb1e3550` session panel, an older Tiltgrav hub, and the Conduitcrest card `6c48ab7e`. `AGENTS.md` already identified `5ee7ef4b` as a later historical review. All of those artifacts were negative, but the conflicting “newest/latest” wording could send a reader to the wrong file.

The site now reads its current decision from the 30 October review card, and its leading status says there is no current candidate TIFF and no cleared file. The old experiment pages/cards remain available for provenance but are explicitly historical. The home and submission hub do not present an old raster as a newly generated candidate. Current links point to the 30 October status page/card. This changes presentation, not scientific results or prior evidence.

### No clearance by implication

- The new card has null candidate hash/name, null HOLDOUT-DTI, null uniqueness measurements, `ok_to_submit: false`, and `slot_selected_or_spent: false`.
- The two provenance hashes were **not** updated to match local bytes. That needs upstream ownership/review.
- No raster was moved, copied, promoted, or added to the download directory.
- The internal 70% / 3-pixel and absolute Spearman 0.90 duplicate stops remain in force. They are project protocol, not official contest rules. No jittering, hole-filling, exemption, or slot selection was attempted.

## Pass 3 — scientific requirement and source recheck

### GEMSDOE32 B2: what is and is not established

The pinned third-party mirror audit records this support-set lineage: GEMSDOE25 and GEMSDOE30 share a 44,090-dot mask; GEMSDOE32 B2 is that parent support after deleting 6,436 dots within a two-pixel neighbourhood of the mirrored visible-fault raster, leaving 37,654 dots. The 0.2778 value is still **USER-REPORTED / UNVERIFIED**; the mirrored rasters establish geometry, not hidden-label performance or organizer provenance.

For the documented distance-weighted Tversky form, write the hidden-truth weighted true-positive coverage as `T`, weighted false-positive mass as `F`, number of hidden positive pixels as `G`, and the stabilizer as `ε`:

```text
DTI = T / (T + αF + β(G − T) + ε),   α = 0.2, β = 0.8.
```

If an ablation removes weighted false-positive mass `c` while losing true-positive coverage `L`, it raises that ratio only when

```text
α T c > L (α F + β G + ε).
```

That condition explains a plausible precision–recall tradeoff; it does **not** show that B2's removed pixels were false positives or that a two-pixel collar caused the reported value. The organiser staff clarification says the known-fault mask is pixel-exact and identical to the supplied training-label raster. It also says a prediction near a known trace but far from new-fault truth is penalized normally, and a new-fault label can lie within 300 m of a known trace. Therefore a 200 m catalogue collar is not a free-prediction zone; it can remove useful recall as well as false-positive mass.

A causal test would need the authorized common evaluator, whole fault-segment buffered folds, fold-local catalogue-derived features, exact masking of visible fault pixels, an identical baseline, and paired uncertainty intervals. Those inputs/tools are not authorized/available in this checkout. No causal explanation or leaderboard projection is claimed. The fuller existing evidence note is [`knowledge/02_why_gemsdoe32_b2_scored_0.2778.md`](02_why_gemsdoe32_b2_scored_0.2778.md).

### Ranked research queue — proposals only

This is a carried-forward, qualitative queue, not a claim of fleet-wide novelty and not an authorization to run. Similar proposals already appear in prior repository reviews; the full parallel-site registry and literature novelty are not verified. No numerical DTI gain is estimated. Rank indicates research priority by plausible incremental signal versus cost, not measured performance.

| Priority | Hypothesis and layers | Physical argument for off-catalogue faults | Difference and principal mimic | Cost / availability |
|---|---|---|---|---|
| 1 | **Sub-alluvial signed phase/step concordance** — `depth_to_base_surf`, `iso_grav_anom` and derivatives, `rtp`, `tmi_hg`/`tmi_vg`, conditioned on `det_elev` and `det_elev_slope`. | Buried normal-fault displacement can juxtapose basement and basin fill, leaving co-oriented gravity, magnetic, and basement-depth steps under low-relief alluvium after a surface scarp is obscured. | Tests cross-scale signed phase/throw concordance rather than unsigned ridge strength alone. Mimics: paleochannels, intrusive/pediment contacts, basalt margins, and survey seams. | Low–medium compute; competition rasters/cache and assigned lane are missing and their mirror provenance is not organizer-authenticated. Proposal only. |
| 2 | **Magnetic texture change point across paired windows** — `rtp`, `tmi`, `tmi_hg`, with `det_elev_slope` as context. | A concealed discontinuity may juxtapose magnetic fabrics with different directional correlation lengths even if anomaly amplitude and topographic relief are weak. | Uses second-order semivariogram/correlation anisotropy rather than an edge-amplitude/ridge maximum. Mimics: unfaulted lithologic contacts, volcanic texture boundaries, interpolation seams, flight-line artifacts. | Medium compute; same missing/unauthenticated input and lane blockers. Proposal only. |
| 3 | **Cross-cutting magnetic-marker termination network** — `rtp`, `tmi_hg`, `tmi_vg`, `iso_grav_anom_hg`. | Repeated truncation or offset of independent magnetic marker edges along a gravity-supported corridor could expose a concealed structure whose own lineament is weak. | Tests graph-level termination topology against rotated-network nulls rather than edge intensity or mapped-tip extrapolation. Mimics: acquisition seams, intrusive contacts, lava-flow boundaries, interpolation gaps. | Medium–high compute; requires seam controls, a null model, and authorized blocked holdout. Proposal only. |
| 4 | **Destriped K/eTh–magnetic trough boundary** — GeoDAWN `K`/`eTh` radiometry plus `rtp`, `tmi_hg`, `cond_surf`, terrain, and flight-line metadata. | Hydrothermal alteration may alter potassium/thorium ratios and magnetite along buried or degraded fault conduits where scarps are absent. | Tests a local mixture residual and magnetic trough after directional flight-line destriping, not a broad raw radiometric plume. Mimics: potassic intrusions, tuffs, playa sediment/moisture, acquisition stripes. | Medium–high; USGS GeoDAWN source metadata and public CC0 rights were verified, but this sandbox did not download/authenticate the raster bytes or verify full grid coverage. **Not execution-ready.** |

The ordering is deliberately qualitative. Every candidate needs per-feature leakage canaries; any AUC above 0.90 is an unresolved leakage alarm. The chosen hypothesis must be assigned to one lane by the owner, then tested on buffered whole-segment hide-and-recover folds before a separate selector considers a weekly slot. No candidate in this table was run this session.

### Official-source checks (30 October 2026)

- [DrivenData problem and metric page](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/): target is geological faults, not geothermal vents; documents the distance-weighted Tversky metric (`α=0.2`, `β=0.8`, triangular kernel `R=300 m`) and single-band float32 GeoTIFF format, UTM 11N / EPSG:32611, 100 m, values in `[0,1]`, null/NaN outside the study bounds.
- [DrivenData public leaderboard](https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/): fetched all visible rows on 30 October; rank 1 = 0.4544, rank 48 = 0.3195. Rank 47 is 0.3217 on this snapshot. 0.4413 is not among the visible top-50 rows. These describe the public page only; they are not this team's scores.
- [DrivenData data page](https://www.drivendata.org/competitions/306/competition-doe-gems/data/): unauthenticated fetch redirects to the login page; challenge-file availability to this sandbox is not established.
- [September 2026 DOE/NLR official rules PDF](https://docs.nlr.gov/docs/fy26osti/96647.pdf): current fetched copy describes two prize phases, one final submission selected for both, the three-per-week feedback limit as specified on the competition site, and disclosure of generative-AI use in the submission narrative.
- [DrivenData staff scoring clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516/2): staff says the mask is pixel-exact, predictions near known faults but far from new-fault truth are fully penalized, and new-fault truth can lie within 300 m of a known trace.
- [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and): official USGS/DOE release describes airborne magnetic/radiometric deliverables and identifies CC0 rights. The release metadata is publicly viewable; the data bytes were not downloaded in this review.
- [GDR INGENIOUS regional compilation](https://gdr.openei.org/submissions/1391): page says publicly accessible and CC BY 4.0, lists 9 resources (116.98 MB total), including temperature, geophysics, paleo-geothermal features, earthquakes, and well/spring chemistry. The direct resource links are visible; no raw archive was downloaded here.
- [USGS ScienceBase electrical-conductance release](https://doi.org/10.5066/P9TWT2LU): public record describes five conductance layers spanning 2–200 km and linked downloadable GeoTIFF/ZIP attachments. It is a candidate source lead, not data retrieved for this session; inspect its metadata/licensing and spatial resolution before use.
- [EPSG:32611](https://epsg.io/32611): WGS 84 / UTM zone 11N, metres.

## Test and publication outcome

Final verification after the edits: **436 passed, 2 skipped, 126 warnings**. The warnings are Rasterio `Affine` multiplication pending-deprecation warnings. The catalogue-distance assertion skipped because `data/bridge/existing_faults.tif` and `sample_submission.tif` are absent; a separate ridge-candidate check skipped because the competition sample grid was not restored. Saved-byte checks remain offline and passed. Skips are not scientific validation.

`python scripts/build_site.py` rendered 34 decision pages. A second consecutive build left **66 generated HTML/data outputs byte-identical**. The suite also checked local HTML links/fragments and current-card/status-copy consistency. This verifies reproducible rendering, not organizer acceptance or scientific validity. Neither a green software suite nor public-source pages authorizes an experiment or competition upload.

## Remaining work, dependency order

1. Owner supplies the exact method paragraph, one assigned lane, canonical shared-template commit, and the upstream owner for any template correction.
2. Resolve the source provenance/hash mismatches upstream; do not repin local files without review.
3. Obtain authenticated organizer inputs and approved shared feature cache; compare hash/grid/roles before use. Do not treat the peer mirrors or GDR sources as organizer data.
4. Obtain/confirm a complete immutable registry and the protocol's frozen same-evaluator baseline.
5. Only then preregister one assigned-lane hypothesis, apply per-feature leakage checks and buffered whole-segment holdout, and check surface correlation before placement and final dots afterward. Stop on either duplicate rule; preserve the 3-experiment / 2-hour cap.
6. Generate a unique TIFF only after the scientific gates pass; reopen and validate saved bytes, record the hash and run card, then leave slot selection to the separate selector. No file is currently eligible.
