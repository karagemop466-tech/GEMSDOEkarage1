#!/usr/bin/env python3
"""Fail-closed compatibility guard for the retired private feature builder.

The old 58-channel local stack is not the assigned shared template cache. The
parallel-run protocol requires a recorded lane and canonical template, and the
legacy candidate failed the literal registry-lattice stop. Do not build a
private stack, write a canary, or imply that restored mirrors are organizer
inputs. Once the owner assigns a lane and repairs the shared-template
provenance, invoke the shared template's own preparation tool instead.
"""
from __future__ import annotations

import argparse
import sys


BLOCKED_REASON = (
    "BLOCKED: scripts/prepare_data.py is a quarantined private feature builder. "
    "No assigned method lane or canonical shared-template assignment is recorded, "
    "the shared-template integrity check fails, and the historical candidate "
    "fails the literal lattice gate. No cache, features, or canary receipts were written. "
    "Use the assigned shared template only after those gates are resolved."
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # Keep the historical flag parseable so old invocations fail with the same
    # explicit safety message rather than an argparse error that looks actionable.
    parser.add_argument("--force", action="store_true", help=argparse.SUPPRESS)
    parser.parse_args()
    print(BLOCKED_REASON, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
