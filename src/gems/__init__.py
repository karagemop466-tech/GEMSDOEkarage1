"""
gems: Reference implementation of the DOE GEMS Prize Challenge grid, metric,
submission writer, and validator.

Competition: "The Geologic Enhanced Mapping System (GEMS) Prize Challenge"
https://www.drivendata.org/competitions/306/competition-doe-gems/

Every numeric constant in this package is sourced from one of:
  (a) the official DrivenData problem-description page (page/967/), fetched
      and quoted verbatim in docs/SOURCES.md, or
  (b) cross-replication across >=3 independent, mutually unaffiliated
      GitHub Pages research logs (the "GEMSDOE" sibling sites) that all
      independently report identical byte-for-byte grid parameters sourced
      from their locally cached copy of the organizer's sample_submission.tif.

Anything in category (b) is marked UNVERIFIED-BY-US in comments: we have not
ourselves opened the organizer's original file (no DrivenData account is
configured in this environment), so we cannot promote it past
"cross-replicated, plausible, not independently confirmed."
See docs/SOURCES.md for the full citation trail.
"""
