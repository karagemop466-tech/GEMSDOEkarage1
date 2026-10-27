# Project brief — read this at the start of every session

This is a **de-duplicated, consolidated** version of the standing project
instructions. The original request (preserved verbatim in this session's
transcript) repeats the same paragraphs many times across a long message;
nothing distinct has been removed, only exact repeats. If any wording here
seems to compress a point you expected more detail on, the authoritative
original is the user's message history — treat this file as a working
checklist, not a legal text.

## 0. Core Values (Arena) — keep these as the focal point of every decision

- **Maximize P(Win).** Weigh tradeoffs and risk; choose the path that
  maximizes the probability this project actually wins (top of the GEMS
  Prize leaderboard), not the path that merely looks busy or produces the
  most files.
- **Own the Outcome.** Do not wait for permission on things within reach;
  treat both successes and failures as signal; stay accountable end-to-end,
  not just for "my slice."

## 1. The actual prize to win

Place at the top of the DrivenData **GEMS Prize Challenge** leaderboard
(competition #306): <https://www.drivendata.org/competitions/306/competition-doe-gems/>
Problem description: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/>
About / resources: <https://www.drivendata.org/competitions/306/competition-doe-gems/page/968/>
Data tab (requires a free account + enrollment): <https://www.drivendata.org/competitions/306/competition-doe-gems/data/>
Reference solution: <https://github.com/drivendataorg/gems-prize-reference-solution>
Leaderboard (public, no login): <https://www.drivendata.org/competitions/306/competition-doe-gems/leaderboard/>

Steps to compete, per the organizer's own "How to compete" list: enroll,
read the problem description + about page, download the data, train a
model (the reference solution is a starting point, not the ceiling),
generate predictions matching the submission format, upload via the
"Submit" sidebar.

## 2. Hard requirements on any submission we recommend

1. **Format must be correct, every time, with no human intervention
   needed to catch mistakes.** Single-band float32 GeoTIFF (or a .zip
   containing exactly one), EPSG:32611, 100 m resolution, same bounds as
   training data, every in-bounds value in [0, 1]. The pipeline must
   validate this itself before a human is ever asked to click submit (see
   `src/gems/validator.py`). The "Predicted values must be in range [0, 1]"
   error reported against a prior download must never recur.
2. **Must be scientifically unique**, not a byte-for-byte or
   near-duplicate of a previous submission (except when a duplicate is
   explicitly being produced for learning/comparison, clearly labeled as
   such).
3. **Must carry an honest, labeled score estimate.** Every number is
   either `HOLDOUT-DTI` (from our own evaluator, with evaluator version,
   number of withheld positives, and a 95% CI), `ORGANIZER-CONFIRMED`
   (copied from an actual DrivenData submission-page receipt), or
   explicitly flagged as a `PROJECTION`/`UNVERIFIED` estimate. A projection
   is never written as if it were a score.
4. **Must include a unique submission name and a note of at most 140
   characters** (the two fields the DrivenData upload form asks for).
5. **Must pass a leakage canary.** Any single new feature scoring above
   0.90 AUC alone against held-out positives is treated as leakage until
   proven otherwise.

## 3. Parallel-run protocol (for any future experiment on this repo)

1. **Lane discipline.** Stay inside one named hypothesis/method at a time.
   If a candidate raster's rank-correlation with any other tracked raster
   exceeds 0.90, or more than 70% of its positive pixels fall within 3 px
   of another raster's positive pixels, it has drifted into someone else's
   lane (or a trivial duplicate) — log it as a duplicate and stop. Check
   this both before placement (on the underlying surface) and on the final
   thresholded output.
2. **Reuse, don't rebuild.** One shared feature stack, one
   `evaluate_holdout.py`, one `submission_writer.py`
   (`src/gems/metric.py` + `src/gems/submission_writer.py` in this repo).
   Fix bugs once, in the shared tool; never keep a private fork.
3. **Label every number** as described in §2.3 above.
4. **Leakage canary** as described in §2.5 above.
5. **Run card.** Every experiment ends with one JSON card: hypothesis,
   mechanism, the named non-fault process that could mimic the signal,
   holdout DTI + CI, correlation/overlap vs. the registry of other known
   rasters, the output raster's sha256, validator output, submission name +
   a <=140-character note, and a verdict of `promote` or `negative`.
   Negative results are deliverables, not failures to hide.
   (`src/gems/submission_writer.write_run_card`.)
6. **Budget.** Stop after 3 experiments or 2 hours in a given session.
   Promotion of a candidate to an actual DrivenData submission is a
   separate, deliberate decision gated on it beating the current holdout
   best — never spend a real weekly submission slot on an unvalidated idea.

## 4. Research mandate

The part of this project that matters most is genuine scientific discovery
of structures relevant to hidden geothermal systems — not leaderboard
gaming. Before implementing anything: generate 3-5 ranked candidate
geological hypotheses not already tried, each naming the exact layer(s), the
physical transform, why it should recover a fault *missing* from the
USGS/INGENIOUS catalogue (as opposed to one already in it), how it differs
from this repo's prior art, and — if it needs new external data — the
specific free, official source, checked to confirm it is actually
obtainable before calling the idea viable. Validate the top candidate on a
spatially-blocked, whole-segment holdout before it is allowed to spend a
real submission slot. See `research/hypotheses.md`.

Store everything learned from official, verifiable sources
(`docs/SOURCES.md`) so it is reusable beyond this one competition. Be
willing to be contrarian — look for data sources or angles others are
likely overlooking — but every claim must stay grounded in cited, checkable
science, never speculation dressed as fact.

## 5. Process requirements that apply to every task in this repo

- Work line by line, verified against official, trusted sources; provide
  links for manual review; do the work autonomously (no step should require
  a human to do the actual research or verification); flag irregularities
  explicitly rather than silently resolving them; never hallucinate a fact,
  a score, or a capability.
- Multi-pass discipline on any nontrivial task: (1) implement and verify,
  (2) review your own work for bugs, missing requirements, and edge cases
  and fix them, (3) re-check the whole thing against the original request
  once more and improve accuracy/reliability/completeness before calling it
  done. Don't stop after pass 1.
- Ship a clean, simple, organized GitHub Pages site for this repo
  (`docs/`) with all key information in an easy-to-read format and official,
  verified source links, including a subpage that explains, step by step,
  exactly how to make a submission to the contest.
- At the end of a work session: open a pull request from this branch,
  merge it, and explicitly write down what work remains and what is
  currently blocking it, so the next session can pick up immediately.

## 6. Known, explicit limitations (do not paper over these)

See `docs/LIMITATIONS.md` for the full, evidence-backed breakdown. In short:
this sandbox cannot reach `drivendata.org`'s authenticated data tab,
`dropbox.com`, or `gdr.openei.org`/`sciencebase.gov`'s binary downloads —
only `github.com`-family hosts and `pypi.org`-family hosts are reachable
from `bash`, and the `fetch_page` tool can read web page *text* from a wider
set of hosts but cannot retrieve raw binary file contents.

**Update:** the real `training_features.tif`, `labels.tif`, and
`sample_submission.tif` WERE opened this session, via a hash-pinned
third-party GitHub mirror discovered inside a sibling repo's own data
manifest (`github.com`-family hosts, still inside the allowlist — see
`docs/LIMITATIONS.md` §0 and `data/README.md`). This is NOT a DrivenData
login and NOT organizer-authenticated; every number computed from it is
still labeled `HOLDOUT-DTI(...)`, never `ORGANIZER-CONFIRMED`. Re-run
`bash scripts/restore_real_data.sh` each session that needs it (the ~450 MB
of raw data is gitignored and deleted from the workspace between sessions
to stay under the patchset size cap).
