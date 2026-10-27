#!/usr/bin/env python
"""
Generate the ONE file in this repo that is honestly safe to upload today:
a format-perfect, all-zero "no fault predicted anywhere" baseline, built on
the cross-replicated reference grid (src/gems/grid.py).

What this IS:
  - A literal reproduction of the pattern the organizer itself describes:
    "A sample submission that predicts total fault absence is provided for
    your reference on the data download page. You can use this as a
    template to ensure that your submission is correctly formatted."
    (https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#submission-format)
  - Guaranteed to pass every automated format gate in src/gems/validator.py:
    single band, float32, EPSG:32611, exact shape/transform, fully finite,
    every value in [0, 1] (all exactly 0.0).
  - A correct fix for the reported upload error "Predicted values must be
    in range [0, 1]": this file cannot trigger that error because it has no
    pixel outside [0, 1] anywhere, full stop.
  - By the official DTI formula, this file scores DTI = 0 against any
    nonempty ground truth (TPw=0, FPw=0, FNw=|G|, so DTI = 0/(0+0+beta|G|+eps)
    = 0). It is a PLUMBING / FORMAT TEST, not a competitive entry. Submitting
    it tells you your upload pipeline works; it will not move you up the
    leaderboard.

What this is NOT:
  - It is NOT a scientifically informed candidate. We do not have access to
    the real training_features.tif/labels.tif in this environment (see
    docs/LIMITATIONS.md), so we cannot compute real fault probabilities.
  - It is NOT one of the sibling "GEMSDOE" sites' sparse-dot rasters; it
    shares zero bytes, zero dot pattern, and zero methodology with any of
    them (see research/sibling_site_audit.md), so uniqueness is trivially
    satisfied -- but that uniqueness is scientifically unimportant given the
    file predicts nothing.

Run `python scripts/run_real_pipeline.py` instead once real data is placed
in ./data/ (see scripts/download_competition_data.sh) to produce an actual
scientific candidate.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np

from gems.grid import GEMS_GRID
from gems.submission_writer import SubmissionMeta, write_run_card, write_submission
from gems.validator import validate_submission

OUT_DIR = Path(__file__).resolve().parents[1] / "outputs" / "baseline"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tif_path = OUT_DIR / "gems-karage1-format-baseline-zero-v1.tif"

    arr = np.zeros(GEMS_GRID.shape, dtype=np.float32)
    write_submission(tif_path, arr)

    report = validate_submission(tif_path)
    assert report.all_checks_passed, report.checks

    meta = SubmissionMeta(
        unique_name="gems-karage1-format-baseline-zero-v1",
        note="Format-only zero baseline (predicts no fault); validates the "
        "upload pipeline. True DTI=0. Not a scientific candidate.",
    )
    run_card_path = write_run_card(
        OUT_DIR / "run_card.json",
        meta=meta,
        hypothesis="N/A -- this is a format/plumbing baseline, not a geological hypothesis.",
        mechanism="Writes an all-zero array at the cross-replicated reference grid "
        "(src/gems/grid.py), clipped and dtype-enforced to guarantee [0,1] float32.",
        named_non_fault_mimic="N/A",
        holdout_dti={
            "label": "ANALYTIC (not an evaluator run)",
            "value": 0.0,
            "derivation": "TPw=0, FPw=0, FNw=|G| for any nonempty ground truth G "
            "=> DTI = 0/(0 + alpha*0 + beta*|G| + eps) = 0 exactly.",
        },
        correlation_vs_registry={
            "note": "Not applicable -- an all-zero raster is byte-identical to "
            "the organizer's own described 'total fault absence' sample "
            "submission by construction, not a competing research artifact."
        },
        raster_sha256=report.sha256,
        validator_output=report.checks,
        verdict="negative",
    )

    print(f"Wrote {tif_path} (sha256={report.sha256})")
    print(f"Wrote {run_card_path}")
    print(json.dumps(report.checks, indent=2))


if __name__ == "__main__":
    main()
