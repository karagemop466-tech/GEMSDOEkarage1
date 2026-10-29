#!/usr/bin/env python3
"""Quarantined legacy K/Th + thermal masked experiment entry point.

The former implementation assigned ``gate_res['passed'] = True`` after the
uniqueness gate, masking the actual gate result. It also used a single HMAS
proxy halo instead of a complete registry and wrote output before a valid
pre-placement audit. Its existing GeoTIFF is retained as a research artifact
only and independently fails the literal lattice overlap rule. This wrapper
intentionally has no geospatial imports or writes.
"""
from __future__ import annotations

import sys

REASON = (
    "BLOCKED: legacy masked K/Th + thermal runner is quarantined. Its old "
    "gate override forced passed=True; saved bytes have 99.9017% 3-px overlap "
    "with the pinned lattice. No experiment, cache, or TIFF was written."
)


def main() -> int:
    print(REASON, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
