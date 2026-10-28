#!/usr/bin/env python3
"""Compatibility builder; preserved archives and current pages stay fail-closed."""
from build_detail_pages import main as build_detail_pages
from generate_pages import build_lanes


def build():
    build_detail_pages()
    build_lanes()


if __name__ == '__main__':
    build()
