# Three-pass review — 28 October 2026, arena/3bbd3469

**Decision: DO NOT SUBMIT.** No new raster, geological experiment, holdout estimate, leakage test, organizer receipt, or slot selection was produced. The request promises one assigned method-lane paragraph but does not identify one. The cached features and official template are absent, the shared template's authority is unresolved, the registry is not complete, and no verified same-fold baseline is available. The inherited negative lattice audit is not a substitute for a new pre-placement/final comparison. Do not bypass the lattice or reset another lane's budget.

## Pass 1: repository and next steps

Read the standing brief, source and research reviews, prior session reviews, preflight, local format diagnostic, release gate and tests. The existing [four ranked proposals](research-review.md#ranked-candidate-hypotheses-qualitative-only) have named layers, physical mechanisms, mimics, novelty limitations and data status; none is assigned to this session or experimentally validated. The nine-site evidence is in the [executive summary](../docs/executive-summary.html). User-supplied historical scores are unverified claims, not organizer-confirmed receipts or a new prediction. A possible DTI coverage/precision explanation for B2 is not a demonstrated cause, and improvement on its historical result is not established. Two conflicting leaderboard numbers in the prompt cannot be resolved from the accessible evidence.

The shared-tool preflight reported no assigned lane and missing feature stack, existing faults, training features, sample submission, and labels. Earlier sessions restored pinned third-party mirrors, but those files are absent in this checkout and are not independently authenticated official data. The data-placement-only claim is not sufficient. Direct access to DrivenData, Dropbox, USGS and GDR hosts is outside this environment's outbound allowlist; the organizer [reference repository](https://github.com/drivendataorg/gems-prize-reference-solution) and the pinned [peer site](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/73485f27cf230af770167397c2b72cb9ce3b3f25/docs/index.html) were reachable through GitHub. That establishes repository/page existence, not score, current leaderboard, source authenticity or rules verification. The rejected TIFF is unavailable; the cause of the reported range error remains unknown.

## Pass 2: fix and adversarial tests

Found the format diagnostic CLI previously returned success if only the inside-footprint check passed, even if NaN, infinities or range violations elsewhere made the strict whole-array diagnostic fail. Automation could mistake this exit code for a whole-file check. The default exit status now requires `strict_whole_array_variant_pass`. The weaker inside-only exit criterion is available explicitly through `--require-inside-only`, marked research-only in help and in the report's `cli_exit_check`. Neither success proves portal acceptance, template authenticity, novelty, holdout improvement, or upload authorization. Outside-footprint encoding remains unresolved and the strict policy is conservative rather than an asserted organizer rule. Tests cover outside NaNs, explicit weaker opt-in, and a zero-filled synthetic raster.

## Pass 3: recheck

Rebuilt the site: 32 deterministic pages and no tracked page changes. Full local suite: **241 passed**, with 90 Rasterio pending-deprecation warnings. `git diff --check` passed. These are software checks, not a score or geological validation. The full user prompt was not stored verbatim in the inherited checkout; [standing-prompt.md](../docs/standing-prompt.md) clearly labels itself a reconstruction. We did not fabricate a full transcription. No current leaderboard feed or complete verified registry was established.

## Next safe actions

1. Obtain the explicitly assigned parallel method lane and identify the canonical shared template; repair any shared evaluator/writer defects in its owning template, not a local fork.
2. Obtain organizer-authenticated source/template bytes in an environment authorized and able to access the competition data; prepare the shared feature cache and verify provenance, grid, and outside-footprint policy. Confirm the live weekly allowance separately.
3. Establish a complete immutable registry and frozen comparable holdout best. Resolve the literal lattice-stop conflict without silently exempting it.
4. Only then run up to the protocol's experiment/time budget, with buffered whole-segment hides, fold-visible catalogue features, pixel-exact visible masks, individual canaries, pre-placement and final registry checks, and a paired holdout comparison with uncertainty. Stop on a duplicate. A separate selector decides any slot.

[Session run card](../evidence/session_3bbd3469_run_card.json).
