# Ranked geological hypotheses — session `arena/a8e4de2e` (30 Oct 2026)

Status key: **TESTED** (run this session on the shared holdout) · **NOT TESTED** (budget or ranking) · **OVERLAP** (already partly in the repo; see column).

Every holdout figure below is **HOLDOUT-DTI** from the unmodified shared evaluator `vendor/gems57` (`holdout.build_holdout` / `holdout.evaluate`, alpha 0.2, beta 0.8, 3 px triangular kernel, 16 hide-and-recover cells). None is an organizer score. The evaluator's truth is **mapped USGS/INGENIOUS catalogue segments withheld whole**, so it rewards re-finding mapped traces and penalises off-catalogue placement by construction (see `knowledge/session-review-arena-5ee7ef4b.md`). A holdout gain is a screen, not a leaderboard estimate.

Official layer names (verified 30 Oct 2026 against https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/ and the band descriptions inside `training_features.tif`): `rtp` (band 2), `tmi_hg` (band 3), `tmi` (band 14), `tmi_vg` (band 9), `iso_grav_anom`, `geod_shearrate`, `geod_dilaterate`, `det_elev`, `depth_to_base_surf`, `cond_surf`. GeoDAWN radiometrics are **not** among the 19 official bands; they come from the USGS GeoDAWN data release https://doi.org/10.5066/P93LGLVQ (CC0), via an owner-derived uint8 mirror `external/geodawn_rad_u8.tif` (not organizer-authenticated).

## Ranking (by expected DTI gain × cost, then novelty)

| Rank | ID | Hypothesis (one line) | Layers | Physical signature targeted | Why it could hit a fault missing from the catalogue | Named non-fault mimic | Overlap with repo (verified by grep) | Cost | Status |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **H-R1** | Potassic (K-high, Th-low) alteration that coincides with a magnetic gradient maximum marks a fault-controlled fluid pathway | GeoDAWN K, Th (`external/geodawn_rad_u8.tif` bands 1–2, block-normalised with `external/acquisition_block_id_100m.tif`); `tmi_hg` (band 3) | Positive block-z K minus block-z Th, smoothed σ 1.5 px, multiplied by normalised `tmi_hg` | Alteration halos can sit under alluvium with no mapped trace; the magnetic gradient supplies the structural co-location | K-rich granite and pluton margins; alluvial K variation; flight-block seams | **OVERLAP (partial).** Channel 44 (`geodawn_blk_kth_alteration`) is already a weighted term of a composite (`src/gemskarage1/features.py:668`, weight 0.22). It has **never been scored standalone on the shared holdout** (GSE run card: `holdout_dti` "not run"). The co-location emitter is new. | Low (inputs restored) | **TESTED** this session (Experiment 1) |
| 2 | **H-E1** | Euler deconvolution (structural index 1) on TMI; keep contacts whose depths cluster in a reservoir-scale band | `tmi` (band 14), `rtp` (band 2) | Depth-consistent source edges, reduced-to-pole | Buried contacts under cover have a magnetic depth signature with no mapped trace | Dikes and lithologic contacts with depths outside the band | **NOT OVERLAPPED.** `grep -ril euler scripts src vendor` returns zero hits (30 Oct 2026). | Medium (window and index sweep needed) | **NOT TESTED** (budget). Next experiment if H-R1 is negative. |
| 3 | H-G1 | Gravity–magnetic joint edge: `iso_grav_anom_hg` ridges that coincide with `tmi_hg` ridges | `iso_grav_anom_hg`, `tmi_hg` | Co-located density and susceptibility contrast | Buried offset shifts both fields | Intrusive contacts; basin edges | **OVERLAP (high).** The SIGNEDOFFSET and BBSTEP lanes (`knowledge/hypotheses-20261029.md`) already combine these fields. Not recommended until those are re-read. | Low | **NOT TESTED**; deprioritised for overlap |

## Notes for review

1. H-R1 was chosen because the previous session (`knowledge/session-review-arena-fb1e3550.md`, item 61) named K/eTh residuals as the recommended next experiment, and no session had run it on the shared holdout.
2. The pre-registered decision rule for H-R1 is in `scripts/run_h_r1_kth_magedge.py` (`DECISION_RULE`). It was fixed before the run and is not edited after the result.
3. H-E1 has no code in the repo. It is not claimed as implemented.
4. Each hypothesis is scored on the same 16 cells, so the numbers are comparable within this session.
