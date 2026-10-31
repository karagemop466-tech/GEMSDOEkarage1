# Starting point for every session

**CURRENT REVIEW (2026-10-31, `arena/d454d34a-gemsdoekarage1`): supersedes the entries below.** Verdict: **ELIGIBLE TO UPLOAD · NOT VALIDATED** for `docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif` (format and literal uniqueness pass; no score is established; 0.2789 is PROJECTED). No slot selected or spent. Corrections: the kp1 metric identity was wrong (ceiling 1.0, not 0.556; marginal bar 0.0588 at 0.2778, not 0.0769; 0.0968 at 0.4413, not 0.158; coverage ratio about 1.6×, not 1.86×). The run-card max |ρ| 0.0076 does not reproduce (0.0115). Read `knowledge/review-arena-d454d34a-20261031.md` and `evidence/run_card_arena_d454d34a_20261031.json`. Older "PROMOTE" and "NEGATIVE" entries below conflict with each other and with this one.

**CURRENT SESSION (2026-10-31, `arena/9a378959-gemsdoekarage1`): read `knowledge/kp1-why-gemsdoe32-scored-02778.md`, `knowledge/kp1-preregistration-20261031.md` and `evidence/kp1_run_card.json` first.** Verdict: **PROMOTE one file** — `docs/downloads/karage1-kp1-ttca-springalter-far-conduit-32000-20261031.tif`. Format-valid on the saved bytes (15/15), unique against all nine focus rasters (max |Spearman| 0.0076, max 3-px overlap 26.5 %), zero mass inside the 2-px catalogue corridor, **PROJECTED** 0.2789 (not a score). No slot was spent.

Three things a new session must not re-litigate, because they are measured:

1. The nine focus submissions are one near-uniform family over one lineament support (all 36 pairs overlap 97.5–100 %; score tracks dot count at ρ = −0.967). Their differences are dot-count, not geology. More passes of the same lattice have ≈0.03 of headroom in total.
2. The exact marginal bar on one more dot is `alpha·s/(1−s)` — 0.0769 at 0.2778, 0.158 at 0.4413 — and the format ceiling is 0.5556. Reaching the leaderboard top needs ~1.86× the champion's per-dot accuracy, or independent expert fault traces that are not in the catalogue. Nothing in this repo has demonstrated either.
3. Both mandated local instruments disagree with the observed ordering (hide-and-recover ρ = −1.0; independent state-compilation inventory ρ = −0.34) and must not be used as promotion gates without an owner ruling. A catalogue-trained detector scores three times worse than random on off-catalogue faults (`evidence/kp1_exp2_external.json`).

Earlier negative reviews below remain historical evidence for the files they examined.



**Current branch review first (2026-10-31, `arena/946f7668-gemsdoekarage1`): read `knowledge/review-arena-946f7668-20261031.md` and `evidence/run_card_arena_946f7668_20261031.json`, then the top CURRENT REVIEW block in `README.md`.** Verdict NEGATIVE / DO NOT SUBMIT; no new TIF, geological experiment, HOLDOUT-DTI, leaderboard estimate, or slot selection. The assigned lane, canonical shared tools, data, and complete authenticated registry remain unresolved. The README and generated public-site banners were refreshed for this review; older session records are historical evidence, not current clearance.

**Parallel review (2026-10-31, `arena/dcf0baf1-gemsdoekarage1`): read `knowledge/session-dcf0baf1-review.md`, `evidence/run_card_karage1-seisprox-c3-w0.55-20261031T012000Z.json`, `docs/data/nine_site_executive_20261031.json` and `docs/executive-20261031.html`.** Verdict NEGATIVE / DO NOT SUBMIT. Added the nine-site executive table from restored raster bytes (all nine sites are one field dotted differently; best reported = GEMSDOE32 B2 0.2778 USER-REPORTED), a new format-valid unique candidate on lane H-K1-SEISMIC-PROX (band 10 `deq_n100a15`, unused by the 58-channel stack; 3 px catalogue collar; 37,654 dots; worst peer 3-px overlap 21.7 %), and an executive-summary page. Catalogue holdout: c3 0.000000 / c2 0.000006 vs champion 0.004845 vs random 0.049063 — mismatched, cannot rank off-catalogue candidates. Suite: 498 passed, 1 skipped.

**Latest review (2026-10-31, `arena/510af7c7-gemsdoekarage1`): read `knowledge/review-arena-510af7c7-20261031.md` and `evidence/run_card_arena_510af7c7_20261031.json` first.** Verdict NEGATIVE / DO NOT SUBMIT. Mechanism for 0.2778: B2 = GEMSDOE25 minus 6,436 catalogue-adjacent dots. The catalogue holdout ranks B2 below random, so it cannot select candidates. Official sources were fetched on 31 Oct 2026 (see the review's §7). Reproduce the mechanism with `GEMS_DATA_DIR=$PWD/data .venv/bin/python scripts/offcat_mechanism_analysis.py`.

**Previous branch review (2026-10-31, `arena/b8fc7593-gemsdoekarage1`): read `knowledge/review-arena-b8fc7593-20261031.md` and `evidence/run_card_arena_b8fc7593_20261031.json`, then the top CURRENT REVIEW block in `README.md`.** Verdict NEGATIVE / DO NOT SUBMIT; no TIF, experiment, holdout, score estimate, or slot selection. Lane/template assignment and required data are unresolved. Focus-site leaderboard estimates are explicitly unavailable.

**Prior mainline review (2026-10-31, `arena/cd6c8044-gemsdoekarage1`): read `knowledge/session-review-arena-cd6c8044.md`, `evidence/session_cd6c8044_run_card.json`, and `knowledge/hypotheses-20261031.md`.** Verdict NEGATIVE / DO NOT SUBMIT; no TIF, experiment, holdout, score estimate, or slot selection. Lane/canonical template, authenticated inputs, and complete registry remain unresolved. Suite: 451 passed, 2 data-dependent skips. Live board snapshot: #1 0.4544, #50 0.3195 (31 Oct, organizer-public only).

**Previous branch review (31 Oct 2026, `arena/946f7668`):** read `knowledge/review-arena-946f7668-20261031.md` and `evidence/run_card_arena_946f7668_20261031.json`. It also ended negative and is historical; current review is above.

**Prior upstream review (31 Oct 2026, `arena/830e1f79`):** read `knowledge/session-review-arena-830e1f79.md` and `evidence/session_830e1f79_run_card.json`. It separately rechecked official format wording and a live leaderboard; those time-sensitive claims are historical and do not supersede this branch review or the internal parallel-run protocol.

**Previous branch review (2026-10-30, `arena/cfabff7e-gemsdoekarage1`):** read `knowledge/session-review-arena-cfabff7e.md` and `evidence/session_cfabff7e_run_card.json` for the earlier safety review and its upstream merge context.

**Latest merged mainline experiment (2026-10-30, `arena/a8e4de2e`): read `knowledge/session-review-arena-a8e4de2e.md`, `knowledge/hypotheses-20261030.md`, `evidence/run_card_h_r1_20261030.json`, and `evidence/exp_h_r1_kth_magedge_20261030.json`.** H-R1 used 1 of 3 experiments and created a research-only TIF; its preregistered verdict is negative, nothing is cleared, and it must not be submitted. This is a separate upstream session, not work from the current review.

**Prior experimental session:** read `knowledge/session-review-arena-5ee7ef4b.md` and `evidence/session_5ee7ef4b_run_card.json`. Result: NEGATIVE, no file cleared. The shared catalogue holdout cannot rank off-catalogue candidates (the champion scores below random); the owner must decide the lattice rule and the holdout design before any slot.

**Latest session (2026-10-29, `arena/c65129cb`): read first** `knowledge/session-review-2026-10-29-thd-ridge.md` and `evidence/session_thd_ridge_run_card_20261029.json`. Verdict NEGATIVE / DO NOT SUBMIT. It records that the literal 70%/3-px gate fails uniform random dot sets (`evidence/lattice_gate_null_check_20261029.json`), so the gate needs an owner decision before any candidate can be cleared.

**Newest session (`arena/9cf124bb`, 31 Oct 2026): read `README.md` (CORE VALUES, then CURRENT REVIEW), `knowledge/review-arena-9cf124bb-20261031.md`, and `evidence/run_card_arena_9cf124bb_20261031.json` first.** Verdict: no file cleared. The per-site executive summary and the candidate download page are generated by `scripts/build_site.py`. The H-O2 candidate is a research download labelled DO-NOT-SUBMIT; its holdout is negative. Read the holdout rules before running any experiment; experiment budget is 3 or 2 hours.

**Newest session (`arena/6275e37e`, 29 Oct 2026): read `knowledge/session-review-arena-6275e37e.md` and `evidence/session_6275e37e_run_card.json` first.** Verdict: negative, no file cleared. It adds the line-level official reference record (`knowledge/official-reference-verification-20261029.md`, including the float64 irregularity), the owner portal-error diagnostic (`scripts/portal_range_check.py`), and the verified marginal inclusion rule (`tests/test_marginal_rule.py`).
**Latest (29 Oct 2026, `arena/fb1e3550`): read first `knowledge/session-review-arena-fb1e3550.md`, `knowledge/hypotheses-20261029.md`, and `evidence/session_fb1e3550_run_card.json`.** Verdict: NOTHING CLEARED. Two lanes (H-K1-STRAINPHASE, H-K1-SIGNEDOFFSET) lost to the reproduced GPC holdout control (0.073394). The site's first panel is the session summary. Shared tools used: `gemsk.holdout`, `gemsk.emission`, `gemskarage1.dipdual.build_surfaces`, `scripts/run_strainphase_experiment.py`, `scripts/surface_registry_overlap.py`. Restore data with `python scripts/restore_karage1_data.py --group core|external|scored`, then `ln -sfn "$PWD/data" .cache/gems_data` (git-ignored).

**Latest session: read `knowledge/session-review-arena-ca9c4488.md` and `evidence/session_ca9c4488_run_card.json` first.** It holds the nine-site duplicate table, the lattice-coverage bound (≤ 22,163 dots can pass the 70 % rule), the identical-mask groups, and the decision the owner must make on the gate.


**Read first: `knowledge/session-review-arena-a409acfe.md` and `evidence/session_a409acfe_run_card.json`.** The page `docs/executive-summary.html` was once a false "CLEARED" page with an unaudited `promote` card; it is retracted and regenerated by `scripts/build_site.py`. Never treat any page or card as clearance without a registry-overlap receipt, a saved-byte audit, and a separate selector.

Read `README.md` ("READ FIRST" brief), then `knowledge/session-review-arena-20261029.md` and `evidence/session_20261029_run_card.json`: no file is cleared; the lattice rule is saturated; owner decisions are listed there.

Read `knowledge/session-review-arena-1668dda0.md`, `evidence/session_1668dda0_run_card.json`, and `evidence/local_downloads_and_peer_audit_20261028.json` first: all 9 committed GeoTIFFs in `docs/downloads/` (including the retracted synthetic `karage1-unique-alteration-dots-20261028-zeros.tif`, which had 2,113 outside-footprint positives and 99.8558% 3-px lattice overlap) and 9 SHA-pinned sibling/peer GeoTIFFs across 22 commit-pinned ecosystem repos fail the literal 70% lattice rule (`ok_to_submit: false`). `scripts/generate_unique_submission.py` and `scripts/run_bbstep_experiments.py` are quarantined; `scripts/validate_geotiff.py` and `scripts/audit_references.py` now reject all-finite bogus templates and require `outside_encoding_accepted` for CLI pass.

Read `knowledge/session-review-arena-a1ef4ce0.md` and its session JSON card as well. Baseline positive-count and unmasked-pixel evidence are mandatory in the promotion policy; omitting them is not a pass. This session independently replayed the nine-site mirror audit but generated no new TIFF or holdout result. No lane is assigned.

Read `knowledge/session-review-arena-cf677bd7.md` (latest session: NEGATIVE, 305 tests pass, no new TIF) and `knowledge/parallel-candidate-audit-2026-10-28.md` as well: the pinned
PR 19 and 20 candidate rasters fail the literal lattice proximity rule even
though their reports exempted that witness. They are not cleared to submit.
Read `knowledge/repository-review-2026-10-28.md` for the pinned organizer
reference-source audit and the latest three-pass checkout review.

Read README.md, docs/standing-prompt.md, knowledge/research-review.md,
knowledge/review-2026-10-28.md, knowledge/review-arena-0fb1-20261028.md,
knowledge/session-review-arena-9ad4a8a0.md, knowledge/session-0a62cb67-review.md,
and knowledge/session-review-arena-9ca08e2e.md (together with
evidence/training_features_band_audit_20261028.json,
evidence/nine_sites_secondary_audit_20261028.json, and
evidence/conduitcrest_lattice_reaudit_20261028.json)
before proposing or implementing work. The
parallel-run protocol is binding: do not invent a lane, bypass any registry
witness, manufacture a score, or upload old predictions. Preserve the budget,
separate technical gates from slot selection, and update current evidence and
visible pages together. Official-data provenance must not be inferred from
peer mirrors.

The historical HMAS and GPC-Z promotion statements are superseded. Their
own recorded overlap with the registry lattice exceeds the literal protocol;
the HMAS canary also treated a constant feature as a passing test. Session
`arena/9d2bc03d` executed lane H-K1-BBSTEP (buried basement-step). The generated
GeoTIFF is unique versus the nine focus sites and still a literal lattice
duplicate (98.53% 3-px overlap). Verdict remains negative; no slot was spent.
Read docs/data/run-card.json, evidence/bbstep_uniqueness.json,
evidence/conduitcrest_lattice_reaudit_20261028.json and
evidence/candidate_audit_20261028.json. The later Conduitcrest candidate is also a literal lattice duplicate (99.3454% overlap); its earlier run card omitted the lattice, lacked a pre-placement lattice check and single-feature canary, and had no 95% CI. `scripts/build_unique_submission.py` is quarantined and must not be re-enabled around these gates. `evidence/review_2026-10-28.json` is an earlier review snapshot. The HMAS pipeline and promotional page
generators are quarantined. Build current entry pages with
scripts/build_current_review.py or scripts/build_site.py. Do not restore old
promotional pages. Shared-template fixes belong in its owning template, not a
private fork.

Thirty-one third-party data mirrors are pinned and restorable, but their hashes
do not establish organizer authenticity. Cached data and the shared feature
stack are not tracked. Research-only downloads are not submission authorization.

Independent peer audits are retained at evidence/prior_candidate_audit.json and
evidence/release_reassessment_20261028.json; the latter has been replayed exactly.
The same-day peer review is knowledge/three-pass-review-2026-10-28.md. The shared
comparison adapter is a conservative check, not proof of a complete registry
or a substitute for fixing the authoritative upstream template.
