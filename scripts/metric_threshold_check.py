#!/usr/bin/env python3
"""Synthetic check of the inclusion rule for a binary Tversky-type score.

Derivation (no kernel, binary predictions, alpha + beta = 1):
  DTI = TP / (TP + a*FP + b*FN).  Adding one pixel with hit-probability q changes
  TP by +q, FP by +(1-q), FN by -q, so the denominator changes by a (for a+b=1).
  Including it therefore increases DTI iff q > a * DTI.

This script only tests that rule on synthetic posteriors. It uses NO competition
data and produces NO leaderboard estimate. Output: evidence/metric_threshold_check_23ef16f9.json
"""
import json
from pathlib import Path

import numpy as np

ALPHA, BETA = 0.2, 0.8
ROOT = Path(__file__).resolve().parents[1]


def dti(selected, g):
    tp = float(np.sum(selected & g))
    fp = float(np.sum(selected & ~g))
    fn = float(np.sum(~selected & g))
    den = tp + ALPHA * fp + BETA * fn
    return tp / den if den > 0 else 0.0


def run(seed, n=400_000, mean_q=0.02):
    rng = np.random.default_rng(seed)
    # heavy-tailed posterior: most pixels near 0, a minority with real hit probability
    q = rng.beta(0.3, 0.3 * (1 - mean_q) / mean_q, size=n)
    g = rng.random(n) < q          # realised labels drawn from the posterior
    thresholds = np.linspace(0.005, 0.5, 100)
    scores = [dti(q > t, g) for t in thresholds]
    k = int(np.argmax(scores))
    t_star, s_star = thresholds[k], scores[k]
    return dict(seed=seed, best_threshold=round(float(t_star), 4),
                best_dti=round(float(s_star), 5),
                rule_threshold_alpha_x_dti=round(ALPHA * float(s_star), 5),
                abs_gap=round(abs(float(t_star) - ALPHA * float(s_star)), 5),
                n_selected_at_best=int(np.sum(q > t_star)))


if __name__ == "__main__":
    runs = [run(s) for s in range(5)]
    out = dict(
        schema="karage1-metric-threshold-check-v1",
        session="arena/23ef16f9",
        note="Synthetic posteriors only. Not a holdout result and not a leaderboard estimate.",
        alpha=ALPHA, beta=BETA, runs=runs,
        max_abs_gap=max(r["abs_gap"] for r in runs),
    )
    path = ROOT / "evidence" / "metric_threshold_check_23ef16f9.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
