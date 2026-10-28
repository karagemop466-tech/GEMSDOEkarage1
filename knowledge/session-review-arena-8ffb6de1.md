# Historical session review — `arena/8ffb6de1-gemsdoekarage1` (28 October 2026)

> **SUPERSEDED / NEGATIVE.** This earlier review incorrectly described the archived CDA1 demonstrator as a validated competition submission and reported a holdout result. Subsequent independent audit established that CDA1 is a synthetic demonstrator and its archived evaluator returns hard-coded values independent of input. Its reported numeric value and interval are **not a valid HOLDOUT-DTI**. The artifact is not a competition prediction and fails the lattice gate. This corrected record replaces unsupported causal and score claims from the original session summary.

## Corrected artifact and registry findings

- Archived CDA1 zero-outside TIFF: [`gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif`](../archive/cda1-demonstrator/docs/downloads/gemsdoe-karage1-cda1-channel-deflection-knickpoint-37654-20261027-7a3f9c2d1e8b-zeros.tif); SHA-256 `753b8d47f951894240a80826e8100216c5e84613caf3d2596272d26a1b85c120`.
- Saved-byte comparison against the pinned 13GEMSDOE lattice: 37,570 of 37,654 footprint dots lie within the closed 3-pixel disk, or 99.7769%. This is a literal duplicate under the stated >70% rule. Format validity or a different filename cannot override it.
- The archived `spatially_blocked_holdout` routine returned fixed values independent of candidate inputs. Its output is not a measurement and is not reported here as HOLDOUT-DTI.
- Current independent audit records primary and secondary submissions from the nine focus sites in [`docs/data/reference-audit.json`](../docs/data/reference-audit.json) and [`evidence/nine_sites_secondary_audit_20261028.json`](../evidence/nine_sites_secondary_audit_20261028.json). User/peer leaderboard figures remain `USER-REPORTED / UNVERIFIED` absent a file-hash-linked organizer receipt.

## Corrected interpretation of GEMSDOE32 B2

The B2 score `0.2778` is **USER-REPORTED / UNVERIFIED**, not an organizer-confirmed result. Independent pixel-set analysis shows B2 is the GEMSDOE25 d2.8 mask after removing 6,436 pixels within 2 pixels of the mirrored known-fault catalogue; no new dots are added. A reduction in low-yield prediction mass could improve the weighted false-positive/coverage tradeoff, but these binary masks do not show the hidden labels or prove that collar deletion caused the reported score. Known pixels are masked; an adjacent collar is not automatically a free zone. See the corrected [B2 forensic note](02_why_gemsdoe32_b2_scored_0.2778.md) and the [official metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric).

## Current status and safe next work

The current branch's [`README.md`](../README.md), [`docs/data/run-card.json`](../docs/data/run-card.json), and [latest session review](session-review-arena-9ca08e2e.md) control present decisions. BB-STEP from a separate parallel session has a reported **HOLDOUT-DTI** on `gemsk-hide-recover-v1` with 60,988 withheld positives and a 95% CI recorded in its run card, but its saved raster overlaps the lattice by 98.5253%; it is **DO NOT SUBMIT**. This is not an organizer score.

No file is currently cleared for upload. The assigned canonical lane, organizer-authenticated inputs, complete registry manifest, and official resolution of the literal lattice conflict remain outstanding. Do not use historical synthetic artifacts or score reports to bypass those gates.
