#!/usr/bin/env python3
"""Quarantined legacy K/Th + thermal experiment entry point.

The former implementation wrote a raster before checking the full registry,
used a private feature/evaluation stack, and did not establish an assigned lane
or authenticated data provenance. Its saved artifact and unverified sidecar
claim are retained for audit only. Use the fail-closed release gates, not this
legacy runner. This wrapper intentionally has no geospatial imports or writes.
"""
from __future__ import annotations

import sys

REASON = (
    "BLOCKED: legacy K/Th + thermal runner is quarantined. It used a private "
    "stack, has no authorized lane/template assignment, and lacks a complete "
    "pre-placement registry audit. No experiment, feature cache, or TIFF was written."
)


def main() -> int:
    print(REASON, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
