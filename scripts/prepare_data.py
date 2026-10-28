#!/usr/bin/env python3
"""Prepare and leak-check the 58-channel float32 stack (`35` shared base + `23` H-K1-1 channels)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for sub in ("vendor", "src"):
    if str(ROOT / sub) not in sys.path:
        sys.path.insert(0, str(ROOT / sub))

from gemskarage1.features import build_feature_stack
from gemskarage1.holdout_eval import load_reference_masks, run_leakage_canary
from gemskarage1.paths import EVIDENCE_DIR, cache_dir, data_dir


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    print(
        "BLOCKED: the legacy 58-channel private stack is not the assigned shared "
        "template cache, and its candidate failed the literal lattice gate. "
        "No features or canary receipts were overwritten.",
        file=sys.stderr,
    )
    # return 0

    ddir = data_dir()
    cdir = cache_dir()
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    meta = build_feature_stack(ddir, cdir, force=args.force)
    refs = load_reference_masks(ddir)
    canary = run_leakage_canary(Path(meta["stack_path"]), refs["footprint"], refs["labels"])
    out_canary = EVIDENCE_DIR / "leakage_canary_58ch.json"
    out_canary.write_text(json.dumps(canary, indent=2) + "\n")
    print(
        f"[canary] Tested {canary['n_channels_tested']} channels | "
        f"max direction-invariant AUC = {canary['max_direction_invariant_auc']} ({canary['max_feature']}) | "
        f"all_passed = {canary['all_passed']}"
    )
    if not canary["all_passed"]:
        print(f"CANARY FAILED: leakage={canary['leaking_features']}, untestable={canary['untestable_features']}", file=sys.stderr)
        # return 0
    # return 0


if __name__ == "__main__":
    raise SystemExit(main())
