#!/usr/bin/env python3
"""Compatibility entrypoint for the current fail-closed static site.

Previous versions inserted a downloadable candidate labelled "unique" despite
a registered lattice witness. Delegate to the evidence-bound builders instead.
"""
from build_site import main

if __name__ == '__main__':
    main()
