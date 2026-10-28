# Why GEMSDOE32 B2 was reported at 0.2778 — evidence-limited forensic note

**Status: `0.2778 USER-REPORTED / UNVERIFIED`.** No organizer submission-page receipt tied to the saved GeoTIFF SHA-256 is present in this workspace. The analysis below separates measured binary-mask geometry from an untested causal explanation. It is not a new score, a score estimate, a promotion decision, or submission authorization.

## What is directly verified from the pinned mirror rasters

On the owner-mirrored competition grid, exact in-footprint binary-set comparisons establish the following lineage:

| Raster | Measured mask relationship | Dot count | Score status |
|---|---|---:|---|
| GEMSDOE25 `dotted-h19-5-d2-8` | Parent mask; exactly equal to GEMSDOE30 positive support | 44,090 | `0.2600 USER-REPORTED / UNVERIFIED` |
| GEMSDOE31 `h27-4-solo-d28` and GEMSDOE28 secondary `h27-4-r1` | Both equal the parent after removing all dots within the closed 1-pixel disk of mirrored known labels | 40,199; 3,891 removed; zero added | `0.2708 USER-REPORTED / UNVERIFIED` |
| GEMSDOE32 B2 `h33-h33-2-b2` | Parent after removing all dots within the closed 2-pixel disk of mirrored known labels | 37,654; 6,436 removed; zero added | `0.2778 USER-REPORTED / UNVERIFIED` |
| GEMSDOE36 `anderson-geothermal-pinn` | Exact strict superset of B2, with 1,200 additional dots | 38,854 | `0.2750 USER-REPORTED / UNVERIFIED` |

The source rasters and template are SHA-pinned third-party GitHub mirrors, **not** organizer-authenticated downloads. These counts establish support-set identities only; they do not establish hidden-label performance or causal effects. Machine-readable details are in [`evidence/nine_sites_secondary_audit_20261028.json`](../evidence/nine_sites_secondary_audit_20261028.json) and [`docs/data/reference-audit.json`](../docs/data/reference-audit.json).

## Why thinning could help, without proving that it did

The [official DrivenData metric specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric) defines a distance-weighted Tversky objective with α = 0.2, β = 0.8, and a 300 m triangular kernel. In pooled notation, let `T` be weighted true-positive coverage, `F` weighted false-positive mass, `G` the number of hidden positive pixels, and `ε` the numerical stabilizer. The score has the form

```text
DTI = T / (T + αF + β(G − T) + ε)
```

Consider a deletion that loses `L ≥ 0` units of true-positive coverage and removes `c ≥ 0` units of weighted false-positive mass. Provided denominators remain positive, the deletion improves the ratio only when

```text
α T c > L [α F + β G + ε]
```

This explains why a collar can be a useful ablation: it may remove low-yield predictions and reduce false-positive cost. It does **not** show that the removed dots were false positives, that all near-catalogue pixels are unscored, or that another collar radius would improve performance. The [DrivenData staff clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) says known fault pixels are masked; it does not make a surrounding 100–300 m buffer a free region. New faults can occur close to mapped faults.

The reported sequence (parent, 1-pixel collar, 2-pixel collar, then 1,200-dot addition) is suggestive but not a controlled causal experiment: the score/file receipts are absent, and only the raster masks have been independently compared here. It would require the exact common evaluator, identical fold assignments and a paired buffered holdout to estimate an effect. Never treat a USER-REPORTED leaderboard value as `HOLDOUT-DTI`.

## Can a new result beat the reported 0.2778?

**Possible in principle; not established or forecast here.** The largest scientific opportunity is not to tune a collar solely on these reported results, but to test distinct, physically motivated signals for buried structures, with named non-fault mimics, fold-local features, leakage canaries, and the same evaluator/baseline. The current parallel protocol also imposes a strict duplicate gate against every registry raster, including the pinned lattice. The [current session review](session-review-arena-9ca08e2e.md) finds that all 21 primary/secondary focus-site files audited overlap the lattice by more than 70%; the prior BB-STEP research raster is unique versus those nine historical sites but fails the literal lattice gate. It is therefore **DO NOT SUBMIT**.

No leaderboard estimate is defensible from this mask algebra. A holdout result and an organizer score are different evidence classes and are not interchangeable.

## Trusted source pointers

- [DrivenData problem, metric, feature and submission specification](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/)
- [DrivenData staff clarification on masking known faults](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)
- [Official DOE/NLR competition rules (96647 PDF)](https://docs.nlr.gov/docs/fy26osti/96647.pdf)
- [USGS GeoDAWN data release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and)
- [GDR INGENIOUS compilation](https://gdr.openei.org/submissions/1391)

These are source pointers for review. External data payloads and the user's private submission receipts were not obtained or verified in this note.
