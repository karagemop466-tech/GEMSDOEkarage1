# Session accf3693 — repository review and evidence preservation

## Executive decision

**NEGATIVE / DO NOT SUBMIT.** No new TIFF, geological experiment, holdout score,
leaderboard estimate, slot selection, or competition upload was made. The goal
of a unique, high-performing, cleared TIFF remains unmet; generating a renamed,
jittered, synthetic, or known-duplicate artifact would not satisfy it.

Read the [nine-site executive summary](../docs/executive-summary.html),
[ranked four-hypothesis preregistration](../README.md#new-geological-hypotheses--research-proposals-not-results-or-lane-assignments),
[shared-tool preflight](../evidence/session_accf3693_shared_preflight.json), and
[this session's run card](../evidence/session_accf3693_run_card.json).

## What was checked now versus inherited

- Ran the complete test suite in a new ignored virtual environment: baseline
  **305 tests passed**, final **314 tests passed**, with 119 existing
  Rasterio/Affine pending-deprecation warnings. These are software checks,
  not HOLDOUT-DTI or competition performance measurements.
- Ran `scripts/shared_tools.py preflight`: exit 1; lane and canonical-template
  assignment unresolved, required caches absent in this fresh checkout.
  Committed evidence records these current checks. Previously restored cache
  files do not persist merely because their historical receipts are committed.
- Ran `scripts/preflight.py`: exit 1 and a negative report, as designed.
- Checked the organizer reference repository's HEAD using GitHub's API:
  `aebe92f7c8a990f0e3443451b7a825d9afd6336b`, unchanged from the
  [pinned source review](repository-review-2026-10-28.md).
- GitHub Pages API reports an existing legacy deployment from `main:/` at
  <https://karagemop466-tech.github.io/GEMSDOEkarage1/>. This establishes
  configuration, not successful deployment of this branch or portal acceptance.
- Did not re-download nine-site raster mirrors or independently rerun their
  historical audits. Their committed evidence is explicitly prior evidence.
  No live leaderboard, receipt, weekly allowance, external science payload, or
  authenticated organizer data was verified in this session. This environment's
  outbound allowlist excludes DrivenData, Dropbox, USGS and NLR hosts.

## Three passes

### Pass 1 — audit and implementation

Reviewed current instructions, README, standing brief, prior review findings,
registry/template pin, shared preflight, release logic, existing tests and site
build entry points. Baseline tests reproduced. Found that reporting commands
could replace the audit/card they were asked to assess through `--out`.
Protected both commands against direct, symlink and hardlink input aliases.
This is local orchestration hardening; no shared evaluator/writer was forked.

### Pass 2 — edge cases and regressions

Added regression coverage for all three aliases in both commands. Rejected
non-standard JSON constants in preflight even when outside fields otherwise
used by the report. Replaced the fixed `.tmp` filename with a unique temporary
file and guaranteed cleanup. Updated preflight wording to acknowledge historical
rasters and reports instead of falsely claiming none exists in the repository.
All 314 tests passed.

### Pass 3 — requirements reconciliation

Regenerated the site through the existing tested renderer, checked that no
tracked rendered pages drifted, and retained the negative download decision.
The current nine-site table and four ranked proposals already exist; duplicating
these proposals as newly untried would be misleading. No candidate may be
executed before a lane is assigned and canonical shared tools resolved.
No current evidence justifies estimating that a new file will exceed any of the
conflicting user-supplied leaderboard figures.

## Interpretation of GEMSDOE32

The earlier hash-pinned audits establish B2's mask is the GEMSDOE25/30 parent
minus 6,436 dots within two pixels of the mirrored catalogue. Its historical
`0.2778` is **USER-REPORTED / UNVERIFIED**, not ORGANIZER-CONFIRMED.
Removing redundant predictions could reduce false-positive costs, but geometry
alone cannot demonstrate that causal explanation or quantify hidden-label
performance. The existing README explains the metric mechanism and caveats.
The claim that the highest score must come from a particular physical model is
not supported by the available evidence.

## Next work in dependency order

1. Resolve assigned lane and authoritative shared-template ownership. Do not
   fabricate an assignment or silently exempt the lattice registry witness.
2. Authenticate organizer input bytes and distinguish template, visible catalogue,
   and evaluation truth; restore the shared cached feature stack from that source.
3. Resolve the lattice/proximity protocol conflict with its owner and obtain the
   complete registry. Partial uniqueness checks cannot certify novelty.
4. Establish a frozen, comparable spatial holdout best; then run at most three
   preregistered experiments, per-feature canaries, buffered whole-segment
   hide-and-recover and pooled HOLDOUT-DTI with evaluator/version/count/95% CI.
5. Reopen and automatically validate the saved candidate, compare the continuous
   surface and final dots against the registry, and publish a download only with
   truthful gate status. The separate selector must verify the live weekly cap.

This repository cannot update the other eight owners' websites through changes
to this checkout. The local dashboard summarizes all nine. Official source links
are retained for review in [the source register](sources-2026-10-28.md); historical
access claims there were not freshly reverified on non-allowlisted hosts here.

## Concurrent-main integration

The first merge attempt was blocked by concurrent mainline edits. Merged
`origin/main` at `71eac67` into this session branch, retained its equivalent
release-gate input-preservation implementation and duplicate-key JSON checks,
and adjusted our regression to its established exit-1 contract. Integrated
suite: **318 tests passed**, 119 existing warnings. This supersedes the
pre-integration final count above; no scientific result changed.
