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
