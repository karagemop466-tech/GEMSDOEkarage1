#!/usr/bin/env python3
"""Fail-closed compatibility entry point for the retired private feature stack.

The active protocol requires an owner-assigned lane and an agreed, unmodified
shared-template cache. This script previously printed a BLOCKED warning and
then fell through to build a private 58-channel stack. Keep it as a clear stop
until that shared-template assignment is resolved; --force must not bypass it.
"""
from __future__ import annotations

import argparse
import sys


BLOCKED_MESSAGE = (
    "BLOCKED: the legacy 58-channel private stack is not the assigned shared "
    "template cache, and its candidate failed the literal lattice gate. "
    "No features or canary receipts were generated or overwritten."
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--force",
        action="store_true",
        help="retained for command-line compatibility; cannot bypass the safety stop",
    )
    parser.parse_args(argv)
    print(BLOCKED_MESSAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
