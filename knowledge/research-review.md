# Research review and preregistration slate

Reviewed 2026-10-27 UTC. This is a **planning slate, not an assigned method
lane, a geological experiment, a finding of a vent, or a forecast**. The
initial checkout contained no previous implementations; several related ideas
exist in peer repositories. Novelty across the whole fleet has **not** been
established. No experiment was run because the requested lane was not supplied
and the literal registry rule fails at the historical dot budget.

## What can the B2 result actually tell us?

The supplied **0.2778 is USER-REPORTED / UNVERIFIED**, not an organizer receipt.
The independent [raster audit](../docs/data/reference-audit.json) establishes
that, on the mirrored grid, the exact binary support of GEMSDOE32 B2 equals the
GEMSDOE25 d2.8 support with every pixel at distance ≤2 pixels from the mirrored
fault catalogue removed. It reduces 44,090 parent dots by 6,436 to 37,654;
there are no added dots. GEMSDOE25 and GEMSDOE30 have identical prediction
support in the footprint even though their GeoTIFF hashes and outside encoding
are different. The audited record is one historical artifact per site, not an
exhaustive peer comparison.

The [organizer's metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#performance-metric)
uses `k(d) = max(1-d/300m, 0)`, α=0.2, β=0.8, and nearest *weighted* prediction
coverage for each ground-truth pixel. Let `T=TPw`, `F=FPw`, `G=number of
positive ground-truth pixels` and `D=T+αF+β(G-T)+ε`, where ε is the
organizer's numerical stabilizer. If deleting dots decreases coverage by
`L≥0` and removes false-positive mass `c≥0`, the changed score is
`(T-L)/(D-(1-β)L-αc)`. It improves exactly when

```
α T c > L [α F + β G + ε]
```

assuming positive denominators. Thus thinning and deleting low-yield catalogue
collar dots **could** increase DTI by saving redundant false-positive cost, but
it can also reduce coverage. The score and hidden labels cannot be inferred
from this geometric identity. Critically, the [DrivenData staff forum clarification](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516)
says known fault pixels are masked, not an automatically free buffer. It also
says new faults can lie within 300 m of known faults. A blanket assertion that
all near-catalogue predictions are false positives is wrong. Neither a score
above 0.2778 nor a leadership position is established by this repository.

## Ranked candidate hypotheses (qualitative only)

Ranking is a scientific prioritization, not measured improvement. Each starts
from the competition feature names in the [official problem description](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/#provided-features);
actual units, orientation and provenance must be checked against the official
metadata before use. “Different” means different from the *empty initial
checkout* and the cited peer implementation; it does not guarantee uniqueness
in all peer sites.

| Rank / relative cost | Specific layers and proposed physical signature | Why it could expose a missing trace / named non-fault mimic | Prior-art difference and data status |
| --- | --- | --- | --- |
| **1 · medium** | `rtp` magnetic anomaly and isostatic gravity anomaly, plus detrended-elevation slope: estimate oriented, **signed** cross-profile changes at two wavelengths; rank margin locations where the direction and relative displacement of both gradients are stable across scale. Normalize orientation consistently rather than assuming a universal sign. | A fault buried by basin fill can juxtapose rocks with differing magnetic susceptibility and density where a surface trace was missed. Volcanic flow margins, lithologic contacts and survey-leveling artifacts can create the same signal. | More specific than a single unsigned gradient or simple cross-gradient ridge; compare with prior [GEMSDOE24 cross-front / pair experiments](https://github.com/buffedlizard55-lab/GEMSDOE24/tree/main/docs/downloads). No such method existed in this checkout. Uses organizer-specified layers; their owner mirror is listed as five pinned GitHub parts in the [peer manifest](https://github.com/buffedlizard55-lab/GEMSDOE32/blob/main/registry/data_manifest.json). Parts exist in a [pinned tree](https://github.com/buffedlizard55-lab/GEMSDOE/tree/c0c06ac82178f26b94fce3397036ef8f12a2f3a0/data/bridge), but were not downloaded or organizer-authenticated here. Prepared template cache absent. **Not ready to run.** |
| **2 · medium** | GeoDAWN radiometric K, eTh and RTP magnetics: a robust local K/eTh residual against nearby terrain, with directional alignment of the alteration boundary to a persistent magnetic edge. Test a mask of low signal and flight-block edges explicitly. | A mineralized or altered margin associated with an unmapped fault might be visible where the catalogue is incomplete; unaltered potassium-rich intrusive lithology, soil/weathering and flight-height changes can mimic it. USGS observed elevated K/Th in some altered ore rocks, **not proof** of a Nevada geothermal fault. | Unlike [GEMSDOE33 R5's Th/K × conductivity](https://buffedlizard55-lab.github.io/GEMSDOE33/), this tests an oriented boundary and local residual. The [official USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) advertises GeoTIFF grids and CC0; the actual official bytes were not downloaded here. An [owner-derived cache](https://github.com/buffedlizard55-lab/GEMSDOE24/tree/07345ea0604953d7efb858d9cfbc21e20c7aca0b/data/external) exists but is not official-source authentication. **Not ready to run.** |
| **3 · high** | [USGS 3DEP 1/3 arc-second DEM](https://data.usgs.gov/datacatalog/data/USGS:3a81321b-c153-416f-98b7-cc8e5f0e17c3): directional consistency of small tributary cross-valley slope/asymmetry across adjacent catchments, conditioned on drainage-area and elevation. | Repeated drainage deflection across a range front might retain a degraded trace that is no longer visibly sharp; stream piracy, fan deposition and erosion also produce bends. A high score would not by itself demonstrate faulting. | Different from a single scarp or a pure fluvial-χ detector such as [GEMSDOE36 TCD-36](https://buffedlizard55-lab.github.io/GEMSDOE36/docs/); exact fleet novelty unverified. USGS says 3DEP products are free and unrestricted and advertises conterminous coverage; **tile bytes, provenance, and local coverage were not verified here**, and the sandbox cannot download from USGS. Deferred until data is actually accessible. |
| **4 · high** | [GDR INGENIOUS 2 m temperature probes](https://gdr.openei.org/submissions/1391) with a road-distance sampling layer and competition gravity: spatially cross-fit a background model of sampling access and elevation, then test persistent residual probe anomalies near potential-field boundaries. No label-derived distances in features. | A clustered shallow thermal anomaly could point to a concealed fluid pathway missed by fault mapping. Solar heating, groundwater, cultural heat and access-biased sampling are alternatives; well/probe density is not fault evidence. | Unlike a raw hotspot-distance layer, explicit cross-fitted sampling-bias correction is proposed. Related geothermal/road methods exist in peer work; fleet novelty unverified. The GDR page lists the probes and CC BY 4.0. A GitHub owner mirror is [listed](https://github.com/buffedlizard55-lab/GEMSDOE24/tree/07345ea0604953d7efb858d9cfbc21e20c7aca0b/data/external); official ZIP and road data were **not downloaded or checked for local coverage**. Deferred. |

## Validation design once a lane is explicitly assigned

1. Identify one common, unmodified shared template/evaluator and a frozen
   comparable baseline. GEMSDOE24 and GEMSDOE31/32 currently identify different
   template families, so silently choosing one would be misleading.
2. Preregister the selected mechanism, masks, allowed feature inputs, controls,
   dot budget, source hashes, spatial folds and stop rule. Do not alter placement
   merely to dodge a registered raster.
3. Hide whole mapped-fault segments in geographically blocked folds with a
   buffer. Derive **every** catalogue-based feature and training exclusion from
   only the visible faults for that fold; mask visible fault pixels exactly.
4. Test every source and derived feature alone; an AUC above 0.90 is leakage
   until proven otherwise. Run both directions when measuring discriminatory
   ability; never treat missing/constant features as a passing canary.
5. Compare the candidate and frozen baseline under the *same* pooled DTI
   evaluator, same hidden positives and paired spatial-block 95% intervals.
   Test a separate confirmation split. A bootstrap is conditional on labels,
   folds and modeling choices; it is not a private leaderboard interval.
6. Compare surface rank correlation **before placement** and directed dot
   overlap **after placement** against every applicable registry raster.
   Stop on either threshold. The measured lattice witness blocks the historical
   budget regardless of score. It does not establish that every smaller raster
   is impossible, nor that a small one would be valid or useful.
7. Use the agreed shared writer, then reopen exact saved bytes and audit grid,
   dtype, finite range, footprint, nodata and hash. Only an independent selector
   may consider a submission slot after all evidence gates pass. Never submit
   this session's historical or negative files as a new candidate.

## Trusted sources and scope

| Source | Verified statement | Limit in this session |
| --- | --- | --- |
| [DrivenData problem and metric](https://www.drivendata.org/competitions/306/competition-doe-gems/page/967/) | Fault confidence raster, grid contract and triangular distance-weighted Tversky formula. | Hidden labels and personal submission receipts unavailable. |
| [DrivenData staff on masking](https://community.drivendata.org/t/scoring-clarification-are-known-usgs-ingenious-faults-masked-when-scoring-and-are-they-in-the-final-round-label-set/11516) | Existing fault pixels are excluded; near-trace new faults remain possible. | This is metric clarification, not proof any hypothesized feature is a fault. |
| [USGS GeoDAWN release](https://www.usgs.gov/data/geodawn-airborne-magnetic-and-radiometric-surveys-northwestern-great-basin-nevada-and) | Magnetic, radiometric and coordinated lidar survey data; geographic and flight-height caveats; CC0. | Derived owner mirrors are not independently authenticated. |
| [USGS radiometric alteration study](https://www.usgs.gov/publications/gamma-ray-spectrometer-studies-hydro-thermally-altered-rocks) | Some studied hydrothermally altered rocks have higher K/Th. | A different geological context; not a direct validation for this area. |
| [USGS 3DEP products](https://www.usgs.gov/3d-elevation-program/about-3dep-products-services) | DEM products free and without use restrictions. | Appropriate tiles/coverage not downloaded. |
| [GDR INGENIOUS compilation](https://gdr.openei.org/submissions/1391) | Regional probes, springs and other layers are listed with CC BY 4.0. | Data must be attributed; sampling bias and actual local coverage need checking. |
| [Official prize rules](https://docs.nlr.gov/docs/fy26osti/96647.pdf) | Eligibility, deadlines and prize rules are official. | Account status, current quota and private test labels are not available here. |
| [DrivenData Terms of Use](https://www.drivendata.org/termsofuse/) | Terms prohibit automated monitoring/copying of their site without the applicable authorization. | This project does not implement an automated DrivenData leaderboard scraper. |
