#!/usr/bin/env python3
"""Quarantined synthetic Gaussian generator from PR #42.

This script generated ``docs/downloads/karage1-unique-alteration-dots-20261028-zeros.tif``
(``sha256=8bc4dae02a99da68ac0e895b7a5c4b5c72b60de11a91efb7ddef3f2b626ee1d2``)
from pseudo-random ``sigma_px=10`` Gaussian pixel-coordinate blobs with zero
geophysical or DEM feature input and hard-coded a fabricated ``0.0912``
holdout number on non-existent evaluator ``karage1-spatial-block-v1``.

Direct saved-byte re-audit against ``sample_submission.tif`` and the pinned
``13GEMSDOE`` lattice (``b4570b40...``) established two independent failures:
  1. 2,113 of its 3,500 positive pixels (60.3714%) lie OUTSIDE the active
     competition footprint (violating both NaN-outside and zero-outside formats).
  2. 1,385 of its 1,387 in-footprint positive pixels (99.855804%) fall within
     3 px of the pinned ``13GEMSDOE`` lattice (exceeding the literal 70% gate).

Do not re-enable this generator.
"""
from __future__ import annotations

import sys

QUARANTINED_REASON = (
    "QUARANTINED: scripts/generate_unique_submission.py generated synthetic "
    "Gaussian dots without geophysical input, placed 2,113/3,500 positive "
    "pixels outside the study footprint, overlapped 99.8558% within 3 px of "
    "the 13GEMSDOE lattice, and emitted unmeasured holdout numbers. "
    "See evidence/local_downloads_and_peer_audit_20261028.json."
)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    print(QUARANTINED_REASON, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
