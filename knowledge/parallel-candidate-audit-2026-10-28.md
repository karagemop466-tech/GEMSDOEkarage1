# Parallel-candidate independent saved-byte audit — 28 October 2026

**Decision: DO NOT SUBMIT either pinned parallel candidate.** No geological
experiment, new prediction, holdout run, weekly-slot decision, or competition
upload was performed in this review. These findings concern the immutable PR
heads below, not future changes to those pull requests.

| Parallel proposal | SHA-256 of saved TIFF | Dots within 3 px of lattice / dots inside mirror footprint | Literal protocol decision |
|---|---|---:|---|
| [PR 20 · TD-KSCK](https://github.com/karagemop466-tech/GEMSDOEkarage1/pull/20), [pinned source](https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/722d7f1ef1d051e835dc00974a2dfbf04df1d600/docs/downloads/karage1-td-ksck-chi10m-stage2-37654d-20261028T061500Z-zeros.tif) | `20be4c631571ffb62b27f4c36ce518bf240a478f349e97242c147b763b5250ee` | 37,584 / 37,654 = 99.8141% | Duplicate; do not submit |
| [PR 19 · CTWS-2D](https://github.com/karagemop466-tech/GEMSDOEkarage1/pull/19), [pinned source](https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/cd981a202ffe0a4bda10218f14e54348499f67e2/docs/downloads/karage1-ctws2d-tiltworm-ptcf-relay-sep29-20261028T073640Z-zeros.tif) | `f33bc5cfccc917c3d241932253706a9b685db1dced0a95ed4b915d8c2fa5263f` | 37,999 / 38,200 = 99.4738% | Duplicate; do not submit |

[Machine-readable results](../evidence/parallel_candidates_audit_20261028.json) · [Audit script](../scripts/audit_parallel_candidates.py) · [Pinned sample and lattice sources](../registry/reference_assets.json)

The two PR reports themselves recorded the same approximate lattice overlap,
but placed the lattice in a `non_competing_lattice_or_continuous_rasters_gt_70pct_cov`
list rather than treating it as a failing registry witness. See the pinned
[TD-KSCK report](https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/722d7f1ef1d051e835dc00974a2dfbf04df1d600/evidence/fleet_uniqueness_td_ksck.json)
and [CTWS-2D report](https://github.com/karagemop466-tech/GEMSDOEkarage1/blob/cd981a202ffe0a4bda10218f14e54348499f67e2/evidence/fleet_uniqueness_ctws2d.json).
That exclusion is incompatible with the requested rule applying to **any**
registry raster. A different hash, or low correlation with the witness, does
not negate the independent proximity failure. This is a protocol decision, not
a claim that the candidates are byte copies or lack scientific value.

## Reproduction and scope

Fetch the four inputs from the immutable source commits and paths and reproduce
the result in an ignored local directory (GitHub access and `gh` required):

```sh
python scripts/audit_parallel_candidates.py .cache/parallel-audit --fetch \
  --out .cache/parallel-audit/reproduced.json
```

Omit `--fetch` to audit files already placed there as `template.tif`,
`lattice.tif`, `td.tif`, and `ctws.tif`.

The script verifies all four SHA-256 pins; checks one-band TIFFs and matching
shape, CRS and affine; defines the footprint from the sample mask and finite
values; demands finite unmasked binary candidate values inside it; dilates
positive lattice cells by a closed Euclidean disk of radius three pixels; and
counts the candidate's positive cells within that disk. It fails on changed
bytes, mismatched grids, invalid inside values or no candidate dots. It reports
binary Spearman on that footprint as a separate diagnostic. The PR reports'
rounded Spearman values differ from this footprint-specific computation; the
reason has not been verified. The overlap evidence alone resolves the negative
verdict. A successful script exit means only the audit ran; **not** a pass.

This one-witness check does not audit all registry rasters, pre-placement
surfaces, fold construction, reported holdout scores, outside-footprint
encoding or portal acceptance. The sample and lattice are pinned third-party
mirrors, not organizer-authenticated. PRs 19 and 20 contain reported
HOLDOUT-DTI values, but those holdouts have not been independently replayed in
this session and must not be treated as leaderboard projections. Their presence
cannot override the duplicate stop. The full current registry remains unknown.

## Three passes

1. **Review and measure:** Read the starting documents, the current run card,
   shared preflight and release policy; fetched both PR-head rasters and the
   two pinned witness rasters from GitHub and independently measured overlap.
2. **Adversarial review:** Checked hashes, grid equality, footprint, input masks,
   in-footprint binary support and the PRs' own explicit excluded-witness lists.
   Added fail-closed checks and regression tests for wrong pins, grids and values.
3. **Recheck:** Reproduced the machine-readable audit from the saved bytes,
   ran the test suite and regenerated the static decision pages. No candidate
   passed and no scientific or organizer score was inferred.

Next: the prompt contains no single assigned method paragraph; identify the
lane and canonical template, resolve the literal lattice protocol without
silently excluding it, and obtain authenticated data and a complete inventory.
The externally imposed network restrictions and absent DrivenData login prevent
verifying the organizer template or portal behavior in this session.
