# Three-pass implementation and review

## Pass 1 — establish evidence and a usable decision surface

- Inspected the actual starting checkout: only the initial README was present.
- Retrieved twelve pinned reference inputs through the GitHub API into an
  ignored local cache, checked their recorded sizes and SHA-256 hashes, and
  independently re-opened the rasters. The review has one historical raster
  per focus site plus a sample mirror, label mirror, and lattice witness.
- Built the nine-site static decision site, the submission guide, ranked
  unexecuted hypotheses, exact-byte audit and negative run card. No holdout,
  model, scientific experiment, upload or new prediction TIFF was made.

## Pass 2 — find and repair bugs and omissions

- Fixed JSON serialization of a NumPy boolean in the initial audit.
- Re-fetched every input into an empty cache and reproduced every measurement
  in the first audit (except its timestamp). Added tests for exact 70% boundary,
  Euclidean radius, paired binary rank with ties, malformed manifests,
  NaN/range behavior, and altered bytes.
- Inspected a real desktop and mobile browser rendering. Fixed horizontal
  table clipping on desktop and added a keyboard-focusable scroll region and a
  mobile scroll hint. Tested the GitHub monitor against mocked unchanged,
  changed and inaccessible source responses; it never changes release status.
- Changed the negative preflight to exit 1 so a successful report write cannot
  be mistaken by automation for an upload authorization. Invalid or missing
  audit inputs still yield a negative card.

## Pass 3 — reconcile with the owner brief

- Followed a source-monitor alert to a later GEMSDOE25 H79 research file; independently re-opened it, verified its SHA-256, and confirmed 100% literal lattice overlap. The peer also says DO NOT SUBMIT; its holdout was not replayed.
- Corrected pytest import discovery so both `pytest` and `python -m pytest` work from a fresh environment.
- Verified local links, table-to-audit consistency, score evidence labels,
  absence of a candidate download, explicit limits and the separate selector.
- Corrected the algebraic B2 deletion condition to include the organizer's ε.
- Recorded the independently observed 200-character note limit in one pinned
  [GEMSDOE24 helper](../docs/data/template-review.json), which conflicts with
  the owner's 140-character requirement. The 57 writer already checks 140,
  but peers disagree which template is authoritative. Neither template was
  modified or privately forked; the helper must be fixed once in the agreed
  upstream template before use. We cannot update that other repository from
  this branch.
- Integrated parallel main-branch reviews and quarantined synthetic archives. The inherited CDA1 holdout function returns fixed values; its reported HOLDOUT-DTI is not a measurement. Independently found 99.7769% lattice overlap, not its archived 99.99% claim. Both H-UNQ-1 TIFF transforms differ from the mirrored grid. Retained previous detailed pages, data, release gates and workflows without treating archived figures as real.
- Final automated tests and browser checks are reported in the session/PR.
  They test software and reference geometry only—not scientific merit,
  organizer acceptance or a current weekly allowance.

## Remaining limits

There is no assigned lane, complete shared registry, agreed shared template,
prepared feature cache, paired current-best holdout, candidate SHA-256, or
organizer-authenticated sample and score receipt. The lattice stop applies to
the documented historical budget, not every imaginable sparse candidate. This
review does not claim the original user's full repeated message was preserved
verbatim; the README records the actionable owner brief and protocol for future
sessions.

---

# Session review — 28 October 2026 UTC

This section records the present session, not the earlier historical passes above.
The review is not a geological experiment and does not authorize an upload.

## Pass 1 — implement and verify

- Reopened both previously committed candidate TIFFs and compared each saved
  binary support with a SHA-pinned lattice and one historical TIFF per focus
  site. The lattice exceeds 70% for both. Added the full results in
  `evidence/candidate_audit_20261028.json` and a negative current run card.
- Restored 31 hash/size-pinned GitHub mirrors into ignored `.cache/gems_data`
  and recorded verification in `evidence/data_restore_verification_20261028.json`.
  Mirrors are not organizer authentication; no feature stack was generated.
- Replaced the unsafe summary-only gate with row-level fail-closed comparison,
  pinned lattice witness, holdout provenance, canary and saved-byte checks. A
  technical promotion never selects a weekly slot.

## Pass 2 — adversarial review and repairs

- Superseded historical promotion, uniqueness and canary claims in cards,
  receipts, run summaries and the dashboard; corrected owner-reported ledger
  labels. Quarantined historical experiment, private-stack, scanner and stale
  page-generation entry points.
- Made every public decision/guide page deterministic and negative. Research
  TIFF links explicitly say DO NOT SUBMIT. Added tests for local links, disabled
  primary downloads, stale evidence, invalid counts, leakage inputs, pin
  mismatches and research-only ZIP/byte identity.
- Separately disclosed official null/NaN-outside wording, unknown portal error
  cause, missing complete registry, surface evidence and selector. No exact-file
  organizer receipt or current allowance was asserted.

## Pass 3 — request and reproducibility recheck

- Ran the saved-byte audit a second time into an ignored file and compared every
  field other than its timestamp; results matched. Re-verified all 31 cached
  mirrors. Rebuilt the pages and verified decision synchronization idempotence.
- After integrating concurrent main changes, the local suite passed **205 tests**;
  these are software checks, not evidence of organizer acceptance or scientific
  success.
- Four ranked geological ideas, data-source provenance, conditional B2
  interpretation, reconstructed standing requirements and separate selector
  instructions are recorded. No assigned lane was supplied; no new experiment,
  new candidate TIFF or competition slot was created. The central unique-TIFF
  goal remains unmet and must not be relabeled as completed.
- Main advanced concurrently through PRs #13–#17. Two independent saved-byte
  reassessments and prior review/canary safeguards were retained; all page
  builders now delegate to one fail-closed renderer. Its
  added historical snapshot was marked superseded, and the whole suite was
  rerun. A concurrent-build check exposed transient empty HTML caused by
  non-atomic writes; pages and restoration staging now use unique temporary
  files and atomic replacement. PR checks and any permitted merge are separate
  from TIFF authorization.

The independent peer review and ours agree on both saved-byte lattice counts.
The locally added shared-comparator adapter requires a pinned lattice but still
cannot authenticate inventory completeness or prove temporal ordering; it is
not an upstream fix, and no current production lane is authorized.

A third, independent shared-comparator reassessment was replayed from the
restored bytes and exactly matched `evidence/release_reassessment_20261028.json`.
The legacy 58-channel canary itself is now blocked; its strict single-feature
helper is only a local safeguard, not an upstream-template clearance.
