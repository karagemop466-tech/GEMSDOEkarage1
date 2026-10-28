#!/usr/bin/env python3
"""Rebuild every current review entry point from the negative evidence.

Compatibility entry point introduced by a parallel review; it delegates to the
same generators rather than overwriting them with a separate release claim.
"""
from build_site import main as build_site
from generate_pages import build_lanes
from render_site import main as render_site


def main():
    build_site()
    build_lanes()
    render_site()


if __name__ == '__main__':
    main()
