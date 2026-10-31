#!/usr/bin/env python3
"""Metric analysis — what a score is made of, and what it takes to beat 0.2778.

Everything here is algebra on the published metric plus the measured geometry of
the nine focus rasters.  No new submission is built and no slot is spent.

The published metric (competition page 967)
-------------------------------------------
``k(d) = max(1 - d/300 m, 0)``, ``alpha = 0.2`` (false positive), ``beta = 0.8``
(false negative), ``DTI = TP_w / (alpha*FP_w + beta*FN_w)`` with ``TP_w`` summed
over ground-truth fault cells (``max`` over predictions) and ``FP_w`` summed over
*every* cell with a non-zero prediction.  For a binary dot field this reduces
exactly to

    DTI = T / ((1 - beta)*T + alpha*(n - M) + beta*G)

(FN_w = |G| - TP_w, so beta*FN_w = beta*G - beta*T and the coefficient on T is
1 - beta = 0.2, not 1.)  Here ``n`` is the number of dots, ``T`` the covered
truth credit (``<= G``), ``M`` the dots' own self-credit, and ``G = |truth|``.
``M <= T`` and ``M <= n``; ``FP = n - M``.

CORRECTION (31 Oct 2026, session arena/d454d34a): the first version of this file
wrote the T term as ``+T`` (coefficient 1).  That is wrong.  It made the perfect-
knowledge ceiling 1/(1+beta) = 0.556 and inflated the marginal bars.  The correct
ceiling is 1.0.  Verified against ``gems57.metric.dti_bruteforce`` on toy grids
(tests/test_metric_identity_20261031.py).

Consequences that drive the whole lane:

* a dot that lands on a true fault is **free** (its own credit cancels its FP
  mass) and adds up to 1.0 to ``T``: perfect knowledge scores 1.0;
* a dot that misses costs exactly ``alpha`` and adds nothing;
* a dot that lands within one or two pixels earns partial credit and costs
  ``alpha*(1 - m)``;
* so one more dot is worth adding iff ``dT*(1-(1-beta)*s) > alpha*(1-m)*s`` (s = DTI)
  -- i.e. iff its expected kernel credit clears a *precision bar* that rises as
  the field fills up.

Output: ``evidence/kp1_metric_analysis.json``.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from gems57.metric import ALPHA, BETA, dti_from_components  # noqa: E402

EXP1 = ROOT / "evidence" / "kp1_exp1_forensics.json"
OUT = ROOT / "evidence" / "kp1_metric_analysis.json"


def score(n: float, T: float, M: float, G: float) -> float:
    """Binary-dot DTI through the shared template (no private identity).

    TP_w = T, FP_w = n - M, FN_w = G - T, so DTI = TP/(TP + alpha*FP + beta*FN)
    = T / ((1-beta)*T + alpha*(n-M) + beta*G).  Calls gems57.metric directly so this
    file cannot drift from the shared metric (corrected 31 Oct 2026).
    """
    return float(dti_from_components(T, n - M, G - T, alpha=ALPHA, beta=BETA))


def solve_T(s: float, n: float, G: float, M_is_T: bool = True) -> float:
    """Invert the metric for the covered truth credit T."""
    # s = T / ((1-b)T + a(n-M) + bG).  With M = T this is linear in T:
    #   s*((1-b)T + a*n - a*T + b*G) = T  ->  T = s*(a*n + b*G) / (1 - s*(1-b) + s*a)
    if M_is_T:
        return s * (ALPHA * n + BETA * G) / (1.0 - s * (1.0 - BETA) + s * ALPHA)
    # M = 0 (upper bound on T): T = s*(a*n + b*G) / (1 - s*(1-b))
    return s * (ALPHA * n + BETA * G) / (1.0 - s * (1.0 - BETA))


def precision_bar(s: float, m: float = 0.0) -> float:
    """Minimum realised ``dT`` for one more dot to raise the score.

    Adding a dot with truth credit ``dT`` and self-credit ``m`` changes the
    denominator by ``(1-b)*dT + a*(1-m)``, so DTI rises iff

        dT * (1 - (1-b)*s) > a*(1 - m)*s,

    i.e. dT > a*(1-m)*s / (1 - (1-b)*s).  It depends only on the current score,
    not on n, G or the surface.  (Corrected 31 Oct 2026; the earlier
    a*s/(1-s) form came from the wrong identity.)  For a non-redundant dot
    (dT = m) with a + b = 1 this reduces to the exact threshold a*s.
    """
    return ALPHA * (1.0 - m) * s / (1.0 - (1.0 - BETA) * s)


def main() -> None:
    exp1 = json.loads(EXP1.read_text())
    per = exp1["per_file"]
    G_CAT = 60_988          # measured catalogue size inside the footprint
    out = {"schema": "kp1-metric-analysis-v1",
           "alpha": ALPHA, "beta": BETA, "radius_px": 3.0,
           "G_catalogue_px": G_CAT,
           "G_assumption": ("The private test truth size is unknown. Every inversion below is "
                            "reported at G = 60,988 px (the catalogue size, the only measured "
                            "scale in the study area) and at G = 30,494 px (half), so the "
                            "reader can see the assumption explicitly."),
           "identity": "DTI = T / ((1-beta)*T + alpha*(n - M) + beta*G)  [corrected 2026-10-31]",
           "ceiling_perfect_knowledge": 1.0,
           "files": {}, "frontier": {}, "what_beats_2778": {}}

    for site, row in sorted(per.items()):
        n = row["dots"]
        s = row["user_reported_score"]
        entry = {"n_dots": n, "reported_score": s}
        for G in (G_CAT, G_CAT // 2):
            T = solve_T(s, n, G, M_is_T=True)
            Tu = solve_T(s, n, G, M_is_T=False)
            entry[f"G_{G}"] = {
                "covered_truth_credit_M_eq_T": round(T, 1),
                "coverage_fraction_M_eq_T": round(T / G, 4),
                "covered_truth_credit_M_0": round(Tu, 1),
                "coverage_fraction_M_0": round(Tu / G, 4),
                "implied_credit_per_dot_M_eq_T": round(T / n, 4),
                "marginal_dT_bar_for_one_more_dot": round(precision_bar(s), 4),
            }
        entry["kernel_coverage_of_footprint"] = row.get("footprint_kernel_coverage")
        entry["mean_neighbours_within_3px"] = row.get("mean_nbr_within_3px")
        entry["clump_ge3_within_3px"] = row.get("clump_ge3_nbr_within_3px_frac")
        entry["d_cat_le_2px_frac"] = row.get("d_cat_le_2px_frac")
        entry["d_cat_gt_15px_frac"] = row.get("d_cat_gt_15px_frac")
        out["files"][site] = entry

    # ---- how the score moves with the only lever this family actually varies
    ns = [row["dots"] for row in per.values()]
    ss = [row["user_reported_score"] for row in per.values()]
    order = np.argsort(ns)
    rho = float(np.corrcoef(np.argsort(np.argsort(ns)), np.argsort(np.argsort(ss)))[0, 1])
    slope = float(np.polyfit(ns, ss, 1)[0])
    out["dot_count_effect"] = {
        "spearman_n_vs_score": rho,
        "ols_slope_per_1000_dots": round(slope * 1000, 5),
        "interpretation": ("Within the nine-file family the score tracks dot count almost "
                           "perfectly and nothing else does; the family is one near-uniform "
                           "covering of the same support (median mutual 3-px overlap 95.4 %), "
                           "so its dots are statistically interchangeable and n is the only "
                           "free parameter that moves the score."),
    }

    # ---- frontier: what a perfect detector achieves, and what 0.4413 implies
    G = G_CAT
    grid_n = np.unique(np.round(np.geomspace(2_000, 200_000, 60)).astype(int))
    frontier = []
    for n in grid_n:
        T = min(float(n), float(G))                 # perfect placement, one dot per truth cell
        frontier.append({"n": int(n), "perfect_dti": round(score(n, T, T, G), 4)})
    out["frontier"]["perfect_detector"] = frontier
    out["frontier"]["note"] = ("Perfect placement scores 1.0 when every truth cell is covered and "
                               "no dot is wasted; the curve rises to that ceiling at n = G. "
                               "(The earlier 0.556 figure was an algebra error.)")

    for target in (0.2778, 0.3195, 0.4413, 0.4544):
        row = {"target": target,
               "marginal_dT_bar": round(precision_bar(target), 4),
               "rows": []}
        for Gx in (30_494, 60_988, 120_000, 200_000):
            T = solve_T(target, 37_654, Gx, M_is_T=True)
            row["rows"].append({
                "assumed_truth_px": Gx, "at_n": 37_654,
                "required_truth_credit": round(T, 1),
                "required_coverage": round(T / Gx, 3),
                "required_credit_per_dot": round(T / 37_654, 3),
                "feasible": bool(T <= Gx and T <= 37_654 * 2.3),
            })
        out["what_beats_2778"][f"{target}"] = row

    out["conclusion"] = {
        "corrections_2026_10_31": (
            "The identity was corrected (coefficient on T is 1-beta = 0.2, not 1). Consequences: "
            "perfect-knowledge ceiling = 1.0 (was 0.556); marginal bar at 0.2778 = 0.0588 (was 0.0769); "
            "bar at 0.4413 = 0.0968 (was 0.158); the coverage needed for 0.4413 at B2's budget is about "
            "1.6x the nine files' coverage (was 1.86x per-dot). Checked against gems57.metric.dti_bruteforce."),
        "why_0.2778": (
            "Measured, not narrated. Among the nine, score is monotone in dot count (Spearman -0.97). "
            "GEMSDOE32's B2 is an exact subset of GEMSDOE25 (37,654 of 44,090 dots; 6,436 removed, none "
            "added; verified 31 Oct 2026 from the registry rasters). Removing those dots raised the score "
            "from 0.2600 to 0.2778 on the same truth, so in aggregate the removed dots earned less truth "
            "credit than the marginal bar (0.0588 at s = 0.2778). 0.2778 is the best point of that "
            "one-parameter family, not a different geological idea."),
        "can_it_be_beaten": (
            "Yes, but only by raising truth credit per dot. A dot raises DTI only if its kernel credit "
            "exceeds the marginal bar (0.0588 at 0.2778, 0.0968 at 0.4413). At B2's budget with G = 60,988 px "
            "(assumed), 0.2778 corresponds to about 0.26 truth coverage; the nine files cover about 0.25-0.26. "
            "A candidate with the same dot count needs a clearly higher hit rate per dot to move the score, "
            "and this session did not produce one on a valid instrument."),
        "is_0.4413_reachable": (
            "At B2's budget and G = 60,988 px (assumed), 0.4413 needs about 0.41 truth coverage, roughly "
            "1.6x the nine files at the same dot count, with a marginal-dot credit bar of 0.0968. Whether "
            "that is geometrically hard depends on the unknown size of the private truth. Nothing in this "
            "repository has demonstrated that level on a valid instrument; the best local evidence (SGMC "
            "off-catalogue, leave-one-quadrant-out) is far below it and is anti-correlated with the observed "
            "ordering. The honest statement is that 0.4413 exists on the leaderboard and is not reachable "
            "from the evidence this repository holds."),
    }

    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: out[k] for k in ("dot_count_effect", "ceiling_perfect_knowledge")},
                     indent=1))
    print(json.dumps(out["what_beats_2778"], indent=1))


if __name__ == "__main__":
    main()
