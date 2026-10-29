#!/usr/bin/env python3
"""Deprecated compatibility wrapper.

The checked-in public pages include session-specific content that the older
single renderer cannot reproduce. Keep this legacy entry point non-destructive;
use ``scripts/render_site.py`` only when explicitly rebuilding its supported
fail-closed page set.
"""


def main() -> int:
    print("No-op: preserving the current multi-session decision pages.")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
