# New hypotheses — 2026-10-29 (status: proposed, NOT validated, NOT submitted)

**Status of every item below:** proposed. No holdout run was performed in this session, so
no DTI, CI, or score is claimed for any idea. Ranking is a scientific prioritization,
not a projection of leaderboard gain. Nothing here authorizes a submission.

Before writing this list, every candidate was checked by keyword search across
`src/`, `scripts/`, `vendor/`, `knowledge/` and `docs/research/` (commands reproducible from
the repo root). Five of the seven candidate ideas considered were already implemented or
tested, so they are excluded.

## Ideas excluded because the repo already implements or tested them

| Idea considered | Where it already exists (verified by grep) |
| --- | --- |
| Strain-rate (2nd invariant, shear rate, dilatation) with seismicity lineation | Walker-transtension hypothesis, `docs/research/hypotheses-preregistration-2026-10-27.md` (bands 4, 7, 8, 16) |
| Depth-to-base (basement) step / buried basement step | `src/gemskarage1/bbstep.py`, BB-STEP run (`evidence/bbstep_receipt.json`) |
| Conductivity / clay-cap conductivity boundary | `cond_claycap_gradient`, `src/gemskarage1/features.py` (feature 42) |
| Thermal springs / 2 m temperature probes | INGENIOUS layers in `src/gemskarage1/features.py`; H4 in `hypotheses-20261028.md` |
| Soft (probabilistic) output surfaces versus binary dots | `src/gemsk/emission.py`, `src/gemskarage1/emitter.py` |

## Candidate N1 — Lake Lahontan shoreline datum offset (RANK 1, NEW)

- **Layers:** Pleistocene lake-shoreline elevation polygons from USGS MF-2323 (Reheis 1999), with the
  1,400 m Lahontan shoreline and the lower late-Pleistocene highstand; plus a high-resolution DEM
  (USGS 3DEP, to be confirmed against the competition's `1m_DEM_links.csv`, which is behind DrivenData login).
- **Physical signature:** A shoreline was horizontal when it formed. A vertical separation of
  one shoreline level across a linear trace, or a relative offset between two levels that changes sign across that
  trace, indicates post-highstand displacement. Two datums (for example the ~1,330 m and ~1,262 m levels named
  in the GSA source) separate a step from a smooth regional tilt, because a fault gives a constant offset while
  tilt varies linearly with elevation.
- **Why it could find a fault missing from the catalogue:** Offset Lahontan shorelines have been reported on mapped
  faults (see sources), so the same mechanism can expose trace segments that are short, low-relief or partly
  buried, and that the catalogue omitted. The datum does not depend on fault scarps being visible.
- **Named non-fault mimics:** (1) regional uplift or tilt, which MF-2323 itself offers as an explanation for its
  stair-step shorelines; (2) viscous or non-tectonic loading by lake water (see the Pyramid Lake abstract below);
  (3) wave-cut or deltaic reworking of the shoreline; (4) alluvial fan progradation that mantles a shoreline.
- **How it differs from the repo:** The repo uses Lahontan shorelines only as **false-positive vetoes**
  (`lahontan_road_confound_score`, feature 49; `lidar_tectonic_asymm_chain`, feature 56; H-K1-4 in
  `docs/research/hypotheses-preregistration-2026-10-27.md`). No file under `src/` or `scripts/` uses a shoreline as a datum to
  measure vertical offset (keyword search for "shoreline" returned veto or mimic uses only).
- **Cost / data status:** Medium. MF-2323 is free and official. The shapefile link
  (`http://pubs.usgs.gov/mf/1999/mf-2323/mf2323_shp.zip`) is listed in the official metadata but
  **was not downloaded here** because the sandbox allow-list excludes `pubs.usgs.gov`. The 1:250,000 source DEM
  gives a coarse shoreline height precision; this is a serious limitation to test before any claim.

**Sources (verified this session):**
- USGS MF-2323 metadata, abstract (1,400 m shoreline; stair-step shorelines; uplift discussion):
  https://geo-nsdi.er.usgs.gov/metadata/map-mf/2323/metadata.faq.html
- GSA *Geosphere* — "Strike-slip faulting along the Wassuk Range of the northern Walker Lane, Nevada":
  Lahontan recessional shorelines (highstand ca. 15,475 cal yr BP, ~1,330 m) displaced ~14 m:
  https://pubs.geoscienceworld.org/gsa/geosphere/article/10/1/40/132152/Strike-slip-faulting-along-the-Wassuk-Range-of-the
- USGS Quaternary Fault and Fold Database report 22 (text excerpt: Lahontan high-stand shorelines ~12.5 ka offset along the front of the Diamond Mountains):
  https://earthquake.usgs.gov/static/lfs/nshm/qfaults/Reports/22.pdf
- Pyramid Lake subbasin abstract (non-tectonic Lahontan loading as a confound for vertical displacement rates):
  https://www.researchgate.net/publication/228488135_Late_Pleistocene_and_Late_Holocene_Lake_Highstands_in_the_Pyramid_Lake_Subbasin_of_Lake_Lahontan_Nevada_USA

**Irregularity flagged:** The Wassuk and Diamond Mountains examples are *published* offsets on
known faults. They show the physical mechanism, but do not show that N1 recovers unmapped faults.

## Candidate N2 — Quaternary fan/terrace-riser vertical separation (RANK 2, NEW USE)

- **Layers:** the same high-resolution DEM as N1, plus alluvial/terrace surface age polygons from USGS maps (source
  not yet identified and verified; this is an open item).
- **Signature:** a consistent riser-height step across a trace, measured on one correlated surface
  (not a single riser), with the sign oriented along the trace.
- **Mimics:** fan avulsion, channel incision, and cut-and-fill against a grade break.
- **Repo status:** terrace risers appear in the repo only as mimics (`src/gemsk/features.py`, shoreline/terrace
  comment). No feature measures riser separation across a trace.
- **Cost / data status:** Medium–high. Needs a verified age-polygon source before any test. Not validated.

## What was not found

No candidate was found that meets the "new layer" bar using only the 19 official feature bands. The fresh ideas
depend on external, free, official geomorphic data, which must be verified before use.

## Recommended order

1. Verify the MF-2323 shapefile hash and CRS against its metadata (requires internet access outside the sandbox).
2. Build N1 with **two** datums and a regional-tilt term. Run a leakage canary (single-feature AUC > 0.90 means leakage).
3. Hold out with buffered whole segments, as the protocol requires. Only then decide whether N1 beats the current holdout best.
4. Do **not** spend a weekly slot on N1 or N2 until a holdout result exists and a separate selector approves it.
