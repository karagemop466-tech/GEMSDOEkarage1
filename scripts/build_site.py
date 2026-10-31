#!/usr/bin/env python3
"""Compatibility entry point for the single, fail-closed site renderer."""
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.render_site import main
from scripts import build_kp1_site

if __name__ == '__main__':
    main()
    build_kp1_site.main()
    from scripts.build_current_review_fd3e38cf import main as build_current_review
    build_current_review()
