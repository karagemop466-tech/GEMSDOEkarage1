#!/usr/bin/env python3
"""Software check of the vendored DTI oracle and the marginal-dot rule.

Verifies, on random small grids (no competition data used):
  1. dti_exact (fast, EDT-based) == dti_bruteforce (literal equations) for soft p in [0,1].
  2. dti_binary agrees with dti_exact on binary fields.
  3. Adding one dot raises DTI  <=>  marginal_accept() is True (exact two-sided test).
  4. For a non-redundant dot, the bar is k > alpha * DTI (k = its kernel self-credit).

Writes evidence/dti_threshold_check_20261031.json. This is software verification
of the metric transcription only; it is NOT a holdout or leaderboard estimate.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
from gems57 import metric  # noqa: E402


def main() -> int:
    rng = np.random.default_rng(20261031)
    max_abs_err = 0.0
    n_soft = 0
    for _ in range(40):
        h, w = rng.integers(8, 16, size=2)
        truth = rng.random((h, w)) < 0.05
        if not truth.any():
            truth[h // 2, w // 2] = True
        p = np.where(rng.random((h, w)) < 0.3, rng.random((h, w)), 0.0)
        a = metric.dti_exact(p, truth)["dti"]
        b = metric.dti_bruteforce(p, truth)["dti"]
        max_abs_err = max(max_abs_err, abs(a - b))
        n_soft += 1

    max_bin_err = 0.0
    for _ in range(40):
        h, w = rng.integers(8, 16, size=2)
        truth = rng.random((h, w)) < 0.05
        if not truth.any():
            truth[0, 0] = True
        pb = rng.random((h, w)) < 0.2
        if not pb.any():
            pb[1, 1] = True
        a = metric.dti_binary(pb, truth)["dti"]
        b = metric.dti_exact(pb.astype(float), truth)["dti"]
        max_bin_err = max(max_bin_err, abs(a - b))

    # Marginal-dot rule: compare brute-force DTI before/after adding one dot.
    agree = 0
    total = 0
    bar_violations = 0
    for _ in range(300):
        h, w = rng.integers(10, 18, size=2)
        truth = rng.random((h, w)) < 0.06
        if not truth.any():
            truth[h // 2, w // 2] = True
        pb = rng.random((h, w)) < 0.12
        if not pb.any():
            pb[0, 0] = True
        free = np.argwhere(~pb)
        y, x = free[rng.integers(len(free))]
        before = metric.dti_binary(pb, truth)
        pb2 = pb.copy()
        pb2[y, x] = True
        after = metric.dti_binary(pb2, truth)
        improves = after["dti"] > before["dti"] + 1e-12
        # self-credit of the new dot = max kernel to any truth pixel
        g = np.argwhere(truth)
        d = np.min(np.hypot(g[:, 0] - y, g[:, 1] - x))
        k_self = float(metric.kernel(d))
        T = before["tp"]
        n = int(pb.sum())
        M = float(sum(metric.kernel(np.min(np.hypot(g[:, 0] - py, g[:, 1] - px)))
                      for py, px in np.argwhere(pb)))
        K = float(truth.sum())
        pred_rule = metric.marginal_accept(after["tp"] - T, k_self, T, M, n, K)
        total += 1
        agree += int(pred_rule == improves)
        # Non-redundant case: new dot adds credit equal to its self-credit.
        if abs((after["tp"] - T) - k_self) < 1e-9 and k_self > 0:
            bar_violations += int((k_self > metric.marginal_inclusion_threshold(before["dti"])) != improves)

    result = {
        "date": "2026-10-31",
        "scope": "software verification of vendor/gems57/metric.py on random grids; no competition data",
        "soft_grids": n_soft,
        "max_abs_err_exact_vs_bruteforce": max_abs_err,
        "max_abs_err_binary_vs_exact": max_bin_err,
        "marginal_rule_agreement": f"{agree}/{total}",
        "nonredundant_bar_violations": bar_violations,
        "pass": bool(max_abs_err < 1e-9 and max_bin_err < 1e-9 and agree == total and bar_violations == 0),
    }
    out = ROOT / "evidence" / "dti_threshold_check_20261031.json"
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
