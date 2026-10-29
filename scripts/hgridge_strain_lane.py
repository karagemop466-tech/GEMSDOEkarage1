#!/usr/bin/env python3
"""Lane K1-HGRID-STRAIN: magnetic horizontal-gradient crest gated by geodetic strain coherence.

Hypothesis (pre-registered in this file before any score was computed)
----------------------------------------------------------------------
Mapped-but-unrecorded fault traces in the GeoDAWN area are expected to produce
(i) a crest of the total-magnetic-intensity horizontal gradient (the Blakely &
Simpson 1986 edge estimator) and (ii) above-median geodetic second-invariant
strain rate.  The score is ``pct(crest_hgm) * (0.5 + 0.5 * pct(strain))`` and the
emission is the top-K crest pixels by that score.  Crest candidates are
label-blind: no mapped-catalogue quantity enters the ranking, so every scored
number here is free of catalogue leakage by construction.

Stages (budget: 3 experiments)
------------------------------
* ``e1`` -- feature stack and single-feature leakage canary on the holdout.
* ``e2`` -- K sweep and controls (random dots, crest-only) on the shared
  hide-and-recover holdout (``vendor/gems57``), pooled DTI with cell-bootstrap CI.
* ``e3`` -- build the deliverable (K fixed by the pre-registered rule), write
  the GeoTIFF through the shared writer, re-read it from disk, run the
  uniqueness gates against the pinned registry rasters, and write a run card.

Nothing here selects a weekly submission slot.  Verdicts are written as data.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "vendor"), str(ROOT / "src")]

import rasterio  # noqa: E402
from affine import Affine  # noqa: E402
from scipy import ndimage as ndi  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402

from gems57 import evaluate_holdout as EH  # noqa: E402
from gems57 import grid as GRID  # noqa: E402
from gems57 import holdout as HO  # noqa: E402
from gems57 import metric as M  # noqa: E402
from gems57 import submission_writer as SW  # noqa: E402
from gems57 import uniqueness as UQ  # noqa: E402
from gems57 import gates as GATES  # noqa: E402
from gems57 import validate as VAL  # noqa: E402

DATA = ROOT / ".cache" / "gems_data"
EVID = ROOT / "evidence"
DOWN = ROOT / "docs" / "downloads"
REGISTRY_DIR = DATA / "registry"
LATTICE_NAME = "13GEMSDOE_r13-lattice-s5_v2_nan-outside.tif"
SEED = 20261029
# Crest-pool threshold. Started at the 80th percentile; E1 found only 17,751 crest pixels,
# which cannot fill K=37,654. Lowered to the median, then to 0 (all 3x3 maxima compete on the score; both changes disclosed in the run card; E1 re-run each time).
CREST_PCT = 0.0
K_SWEEP = (10_000, 20_000, 37_654, 60_000)
K_PREREGISTERED = 37_654          # dot-count class used by the focus-site rasters
BOOT_DRAWS = 2000
CANARY_NEG_MAX = 200_000
LANE = "K1-HGRID-STRAIN"
HYPOTHESIS = (
    "Magnetic horizontal-gradient crests (Blakely & Simpson 1986 edge estimator on TMI) that also "
    "sit in above-median geodetic second-invariant strain rate mark buried or unmapped fault traces "
    "that are absent from the USGS/INGENIOUS catalogue."
)
MECHANISM = (
    "A fault with vertical or steep offset juxtaposes magnetically contrasting blocks, producing a "
    "narrow horizontal-gradient crest; active slip concentrates geodetic strain in the same corridor."
)
MIMIC = (
    "Lithologic or intrusive contacts (magnetic crests without slip) and GPS/InSAR network-geometry "
    "strain artefacts near survey edges."
)
TIMESTAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, allow_nan=False) + "\n", encoding="utf-8")


# ----------------------------------------------------------------------------- data
def load_inputs() -> dict:
    """Load the restored competition inputs.  All values are read from disk, none hard-coded."""
    with rasterio.open(DATA / "sample_submission.tif") as s:
        sample = s.read(1)
        crs, transform = s.crs, s.transform
        height, width = s.height, s.width
    footprint = np.isfinite(sample)
    with rasterio.open(DATA / "labels.tif") as s:
        lab = s.read(1)
    catalogue = (lab == 1) & footprint
    with rasterio.open(DATA / "training_features.tif") as s:
        feats = s.read().astype(np.float32)
        names = _band_names()
    feats[feats < -1e38] = np.nan
    grid = GRID.Grid(footprint=footprint, catalogue=catalogue, crs=crs,
                     transform=transform, height=height, width=width)
    return dict(grid=grid, feats=feats, names=names, sample_path=DATA / "sample_submission.tif",
                footprint=footprint, catalogue=catalogue, crs=crs, transform=transform)


def _band_names() -> list[str]:
    audit = json.loads((EVID / "training_features_band_audit_20261028.json").read_text())
    names = [b["name"] for b in audit["bands"]]
    if len(names) != 19:
        raise RuntimeError(f"expected 19 bands in the restored audit, found {len(names)}")
    return names


def fill_in(a: np.ndarray, footprint: np.ndarray) -> np.ndarray:
    """Replace missing values inside the footprint by the footprint median (for filtering only)."""
    out = np.array(a, dtype=np.float64)
    ok = np.isfinite(out) & footprint
    med = float(np.median(out[ok])) if ok.any() else 0.0
    out[~ok] = med
    out[~footprint] = med
    return out


def pct_rank(values: np.ndarray, mask: np.ndarray) -> np.ndarray:
    out = np.zeros(values.shape, np.float64)
    v = values[mask]
    order = np.argsort(v, kind="stable")
    r = np.empty(v.size, np.float64)
    r[order] = np.arange(1, v.size + 1)
    out[mask] = r / v.size
    return out


def candidate_scores(inp: dict) -> dict:
    names, feats, fp = inp["names"], inp["feats"], inp["footprint"]
    a = fill_in(feats[names.index("tmi_hg")], fp)
    b = fill_in(feats[names.index("geod_2ndinv")], fp)
    a_s = ndi.gaussian_filter(a, sigma=1.0)
    crest = (ndi.maximum_filter(a_s, size=3, mode="nearest") == a_s) & fp
    thr = float(np.percentile(a_s[fp], CREST_PCT))
    crest &= a_s >= thr
    pa = pct_rank(a_s, fp)
    pb = pct_rank(b, fp)
    return dict(
        crest=crest,
        score_gate=pa * (0.5 + 0.5 * pb),
        score_crest_only=pa,
        n_crest=int(crest.sum()),
        crest_threshold_pct=CREST_PCT,
        crest_threshold_value=thr,
    )


def top_k(score: np.ndarray, crest: np.ndarray, k: int, allowed: np.ndarray) -> np.ndarray:
    idx = np.flatnonzero(crest & allowed)
    k = min(k, idx.size)
    sel = idx[np.argpartition(-score.ravel()[idx], k - 1)[:k]] if k > 0 else np.array([], int)
    out = np.zeros(score.shape, bool)
    out.ravel()[sel] = True
    return out


def random_control(fp: np.ndarray, k: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    idx = np.flatnonzero(fp)
    sel = rng.choice(idx, size=min(k, idx.size), replace=False)
    out = np.zeros(fp.shape, bool)
    out.ravel()[sel] = True
    return out


# ----------------------------------------------------------------------------- holdout
def holdout_block(emitted: np.ndarray, ctx, mode: str) -> dict:
    r = HO.evaluate(emitted, ctx, cell_mode=mode)
    cells = [v for k, v in r["folds"].items() if k.split("_")[2] == mode]
    return dict(
        mode=mode,
        evaluator=f"{EH.VERSION} (vendor/gems57 holdout.py, hide-and-recover, pixel-exact visible mask)",
        emitted_pixels=r["emitted_pixels"],
        on_visible_catalogue=r["on_visible_catalogue"],
        withheld_positives=r["pooled_n_truth"],
        pooled_dti=r["pooled_dti"],
        pooled_coverage=r["pooled_coverage"],
        dti_ci95=bootstrap_ci(cells),
        n_cells=len(cells),
    )


def bootstrap_ci(cells: list[dict]) -> list[float]:
    """Percentile 95% CI: resample the holdout cells with replacement, recompute pooled DTI."""
    tp = np.array([c["tp"] for c in cells])
    fp = np.array([c["fp"] for c in cells])
    fn = np.array([c["fn"] for c in cells])
    rng = np.random.default_rng(SEED)
    draws = np.empty(BOOT_DRAWS)
    n = len(cells)
    for i in range(BOOT_DRAWS):
        j = rng.integers(0, n, n)
        t, f, g = tp[j].sum(), fp[j].sum(), fn[j].sum()
        draws[i] = t / (t + M.ALPHA * f + M.BETA * g + M.EPS)
    return [float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))]


# ----------------------------------------------------------------------------- canary
def canary(inp: dict, ctx, scores: dict) -> dict:
    """AUC of each feature (and of the candidate score) alone, truth vs active background.

    Pooled over all holdout cells, in each cell's own active domain (visible faults and
    the 1.2 km boundary erosion are already excluded from ``cell.active``).  A value of
    max(AUC, 1-AUC) above 0.90 is leakage until proven otherwise (parallel-run protocol rule 4).
    """
    rng = np.random.default_rng(SEED)
    names = inp["names"]
    stacks = {n: [] for n in names}
    stacks["candidate_score_gate"] = []
    labels = []
    for cell in ctx.cells:
        active = cell.active
        truth = np.zeros(active.shape, bool)
        truth[cell.truth_yx] = True
        crop = (slice(cell.bbox[0].start, cell.bbox[0].stop), slice(cell.bbox[1].start, cell.bbox[1].stop))
        mask = active.copy()
        for i, n in enumerate(names):
            v = inp["feats"][i][crop]
            mask &= np.isfinite(v)
        sg = scores["score_gate"][crop]
        mask &= np.isfinite(sg)
        pos = np.flatnonzero(mask & truth)
        neg = np.flatnonzero(mask & ~truth)
        neg = rng.choice(neg, size=min(neg.size, CANARY_NEG_MAX // max(1, len(ctx.cells))), replace=False)
        for idx_arr, lab in ((pos, 1), (neg, 0)):
            labels.append(np.full(idx_arr.size, lab, np.int8))
            for i, n in enumerate(names):
                stacks[n].append(inp["feats"][i][crop].ravel()[idx_arr])
            stacks["candidate_score_gate"].append(sg.ravel()[idx_arr])
    y = np.concatenate(labels)
    out = {}
    for n, parts in stacks.items():
        x = np.concatenate(parts).astype(np.float64)
        auc = float(roc_auc_score(y, x))
        out[n] = dict(auc=auc, symmetric_auc=max(auc, 1 - auc), leakage_flag=bool(max(auc, 1 - auc) > 0.90))
    return dict(
        n_positive=int(y.sum()), n_negative=int((y == 0).sum()),
        max_symmetric_auc=max(v["symmetric_auc"] for v in out.values()),
        any_leakage_flag=any(v["leakage_flag"] for v in out.values()),
        per_feature=out,
    )


# ----------------------------------------------------------------------------- stages
def stage_e1(inp: dict, ctx) -> dict:
    t0 = time.time()
    scores = candidate_scores(inp)
    res = dict(
        schema="karage1-hgridge-e1-canary-v1",
        created_utc=datetime.now(timezone.utc).isoformat(),
        lane=LANE,
        evaluator=EH.VERSION,
        evaluator_implementation_sha256=EH.implementation_hashes(),
        n_crest_candidates=scores["n_crest"],
        crest_threshold_pct=scores["crest_threshold_pct"],
        crest_threshold_value=scores["crest_threshold_value"],
        canary=canary(inp, ctx, scores),
        catalogue_used_in_ranking=False,
        elapsed_seconds=round(time.time() - t0, 1),
    )
    write_json(EVID / "hgridge_e1_canary.json", res)
    return res


def stage_e2(inp: dict, ctx) -> dict:
    t0 = time.time()
    scores = candidate_scores(inp)
    fp = inp["footprint"]
    allowed = fp  # label-blind holdout candidate: no catalogue pruning (catalogue-free ranking)
    rows = []
    for k in K_SWEEP:
        em = top_k(scores["score_gate"], scores["crest"], k, allowed)
        rows.append(dict(arm=f"gate_top{k}", k=k, all=holdout_block(em, ctx, "all"),
                         detached=holdout_block(em, ctx, "detached")))
    for k in (K_PREREGISTERED,):
        em = top_k(scores["score_crest_only"], scores["crest"], k, allowed)
        rows.append(dict(arm=f"crest_only_top{k}", k=k, all=holdout_block(em, ctx, "all"),
                         detached=holdout_block(em, ctx, "detached")))
        em = random_control(fp, k, SEED)
        rows.append(dict(arm=f"random_control_{k}", k=k, all=holdout_block(em, ctx, "all"),
                         detached=holdout_block(em, ctx, "detached")))
    best = max((r for r in rows if r["arm"].startswith("gate_top")), key=lambda r: r["all"]["pooled_dti"])
    res = dict(
        schema="karage1-hgridge-e2-holdout-v1",
        created_utc=datetime.now(timezone.utc).isoformat(),
        lane=LANE,
        evaluator=EH.VERSION,
        evaluator_implementation_sha256=EH.implementation_hashes(),
        preregistered_rule="deliverable K = K_PREREGISTERED (37,654); the sweep is reported, not used to re-pick K",
        best_gate_arm_on_all_mode=best["arm"],
        rows=rows,
        note=("HOLDOUT-DTI on a catalogue hide-and-recover split, NOT the organizer's new-fault test set. "
              "A holdout number is a proxy for relative ranking only."),
        elapsed_seconds=round(time.time() - t0, 1),
    )
    write_json(EVID / "hgridge_e2_holdout.json", res)
    return res


def registry_rasters() -> list[tuple[str, Path]]:
    """Pinned focus-site and lattice rasters restored by scripts/restore_data.py --group registry."""
    out = []
    for p in sorted(REGISTRY_DIR.glob("*.tif")):
        out.append((p.name, p))
    return out


def uniqueness(mine: np.ndarray, fp: np.ndarray) -> dict:
    rows = []
    for name, path in registry_rasters():
        with rasterio.open(path) as s:
            theirs = s.read(1)
        if theirs.shape != mine.shape:
            raise RuntimeError(f"registry raster shape mismatch: {name}")
        fwd = UQ.dot_overlap(mine, theirs)
        rev = UQ.dot_overlap(theirs, mine)
        sr = UQ.surface_rho(mine.astype(np.float32), np.where(np.isfinite(theirs), theirs, 0), fp)
        rows.append(dict(
            file=name,
            their_dots=int(UQ._dots(theirs).sum()),
            forward_3px_overlap=fwd,
            reverse_3px_overlap=rev,
            spearman_full_footprint=sr["spearman_full_footprint"],
            spearman_on_dot_union=sr["spearman_on_dot_union"],
            jaccard_dot_sets=sr["jaccard_dot_sets"],
            is_lattice_calibration_probe=(name == LATTICE_NAME),
        ))
    return dict(rows=rows)


def stage_e3(inp: dict, ctx) -> dict:
    t0 = time.time()
    scores = candidate_scores(inp)
    fp, cat = inp["footprint"], inp["catalogue"]
    # Deliverable: same K-rule as E2, plus the physical veto that the organizer's mask makes free
    # (dots on mapped traces are neither rewarded nor penalised; the shared writer forbids them).
    allowed = fp & ~cat
    em = top_k(scores["score_gate"], scores["crest"], K_PREREGISTERED, allowed)
    n = int(em.sum())
    prediction = np.where(em, 1.0, 0.0).astype(np.float32)
    prediction[~fp] = 0.0
    name = f"karage1-hgridge-strain-K{n}-{TIMESTAMP}"
    down_name = f"{name}-zeros.tif"
    out_path = DOWN / down_name
    note = f"{LANE} label-blind TMI-crest x strain, {n} dots. Format-valid; holdout ~ random. NOT CLEARED."
    if len(note) > 140:
        raise RuntimeError("note exceeds 140 characters")
    receipt = SW.write_submission(
        out_path, prediction, inp["sample_path"], fp, note=note, name=name, catalogue=cat,
        metadata=dict(lane=LANE, k_prereg=K_PREREGISTERED, dots=n, timestamp=TIMESTAMP),
    )
    # Independent re-read of the bytes on disk (the file is the contract).
    with rasterio.open(out_path) as s:
        a = s.read(1)
        meta = dict(crs=str(s.crs), shape=[s.height, s.width], dtype=s.dtypes[0], count=s.count,
                    nodata=s.nodata, transform=list(s.transform)[:6])
    reread = dict(
        finite_everywhere=bool(np.isfinite(a).all()),
        min=float(a.min()), max=float(a.max()),
        in_unit_interval=bool((a >= 0).all() and (a <= 1).all()),
        positive_outside_footprint=int(((a > 0) & ~fp).sum()),
        positive_on_mapped_catalogue=int(((a > 0) & cat).sum()),
        positive_count=int((a > 0).sum()),
        meta=meta,
        crs_match=meta["crs"] == str(inp["crs"]),
        shape_match=meta["shape"] == [inp["grid"].height, inp["grid"].width],
        transform_match=tuple(meta["transform"]) == tuple(inp["transform"])[:6],
    )
    sample_check = dict(
        sample_nan_count_outside=int((~fp).sum()),
        submission_outside_is_zero=bool((a[~fp] == 0).all()),
    )
    hold = holdout_block(em, ctx, "all")
    hold_det = holdout_block(em, ctx, "detached")
    uq = uniqueness(a, fp)
    lattice = next(r for r in uq["rows"] if r["is_lattice_calibration_probe"])
    focus = [r for r in uq["rows"] if not r["is_lattice_calibration_probe"]]
    max_focus_fwd = max(r["forward_3px_overlap"] for r in focus)
    max_abs_rho = max(abs(r["spearman_full_footprint"]) for r in focus if np.isfinite(r["spearman_full_footprint"]))
    uncovered = int((fp & _lattice_uncovered()).sum())
    lattice_floor = max(0.0, (n - uncovered) / n) if n else 1.0
    gates = dict(
        format_valid=bool(receipt.get("validator") is not None and reread["in_unit_interval"]
                          and reread["finite_everywhere"] and reread["crs_match"]
                          and reread["shape_match"] and reread["transform_match"]),
        no_positives_outside_footprint=reread["positive_outside_footprint"] == 0,
        no_positives_on_mapped_catalogue=reread["positive_on_mapped_catalogue"] == 0,
        canary_no_leakage=not e1_flag(),
        registry_focus_forward_overlap_le_0_70=max_focus_fwd <= 0.70,
        registry_focus_abs_spearman_le_0_90=max_abs_rho <= 0.90,
        lattice_literal_forward_overlap_le_0_70=lattice["forward_3px_overlap"] <= 0.70,
    )
    gates["literal_protocol_all_pass"] = all(gates.values())
    res = dict(
        schema="karage1-hgridge-e3-build-v1",
        created_utc=datetime.now(timezone.utc).isoformat(),
        lane=LANE,
        file=str(out_path.relative_to(ROOT)),
        sha256=sha256(out_path),
        zip=str(out_path.with_suffix(".zip").relative_to(ROOT)),
        receipt=str(out_path.with_suffix(".json").relative_to(ROOT)),
        dots=n,
        crest_candidates=scores["n_crest"],
        allowed_pixels=int(allowed.sum()),
        crest_pixels_on_mapped_catalogue_excluded=int((scores["crest"] & fp & cat).sum()),
        lattice_footprint_cells_uncovered_within_3px=uncovered,
        submission_name=name,
        submission_note=note,
        note_chars=len(note),
        reread=reread,
        sample_check=sample_check,
        writer_validator_ok=bool(receipt.get("validator") is not None),
        holdout_all=hold,
        holdout_detached=hold_det,
        uniqueness=uq,
        lattice_floor_forward_overlap=lattice_floor,
        gates=gates,
        elapsed_seconds=round(time.time() - t0, 1),
    )
    write_json(out_path.with_suffix(".validate.json"), dict(reread=reread, gates=gates, sample_check=sample_check))
    write_json(EVID / f"hgridge_e3_build_{TIMESTAMP}.json", res)
    write_json(EVID / f"hgridge_run_card_{TIMESTAMP}.json", run_card(res, gates))
    return res


def run_card(res: dict, gates: dict) -> dict:
    """Parallel-run protocol rule 5 card, built only from measured fields in this run."""
    e2 = json.loads((EVID / "hgridge_e2_holdout.json").read_text())
    arm = {r["arm"]: r for r in e2["rows"]}
    gate_arm = arm[f"gate_top{K_PREREGISTERED}"]["all"]
    rand_arm = arm[f"random_control_{K_PREREGISTERED}"]["all"]
    lat = next(r for r in res["uniqueness"]["rows"] if r["is_lattice_calibration_probe"])
    focus = [r for r in res["uniqueness"]["rows"] if not r["is_lattice_calibration_probe"]]
    worst = max(focus, key=lambda r: r["forward_3px_overlap"])
    return dict(
        schema="karage1-run-card-v1",
        lane=LANE,
        session_branch="arena/1d15747e-gemsdoekarage1",
        created_utc=datetime.now(timezone.utc).isoformat(),
        hypothesis=HYPOTHESIS,
        mechanism=MECHANISM,
        named_non_fault_mimic=MIMIC,
        holdout=dict(
            label="HOLDOUT-DTI",
            evaluator_version=EH.VERSION,
            evaluator_implementation_sha256=EH.implementation_hashes(),
            deliverable_catalogue_pruned=dict(
                pooled_dti=res["holdout_all"]["pooled_dti"],
                ci95=res["holdout_all"]["dti_ci95"],
                withheld_positives=res["holdout_all"]["withheld_positives"],
                note="Dots on the full mapped catalogue removed before scoring; conservative, because removal also drops withheld truth."),
            label_blind_same_K=dict(
                pooled_dti=gate_arm["pooled_dti"], ci95=gate_arm["dti_ci95"],
                withheld_positives=gate_arm["withheld_positives"]),
            random_control_same_K=dict(
                pooled_dti=rand_arm["pooled_dti"], ci95=rand_arm["dti_ci95"]),
            paired_gate_minus_random_note="CIs overlap; no measurable skill over random placement at this K.",
        ),
        correlation_and_overlap_vs_registry=dict(
            registry_rasters_checked=len(res["uniqueness"]["rows"]),
            worst_focus_site_file=worst["file"],
            worst_focus_forward_3px_overlap=worst["forward_3px_overlap"],
            worst_focus_abs_spearman=max(abs(r["spearman_full_footprint"]) for r in focus),
            lattice_forward_3px_overlap=lat["forward_3px_overlap"],
            lattice_floor_forward_overlap=res["lattice_floor_forward_overlap"],
            lattice_uncovered_footprint_cells=res["lattice_footprint_cells_uncovered_within_3px"],
        ),
        raster_sha256=res["sha256"],
        validator=dict(reread=res["reread"], gates=gates, sample_check=res["sample_check"]),
        submission_name=res["submission_name"],
        submission_note=res["submission_note"],
        verdict="negative",
        ok_to_submit=False,
        selector_required=True,
        slot_selected_or_spent=False,
        experiments_used=dict(E1_runs=3, E2=1, E3=1, budget=3,
            disclosure="E1 was re-run after two crest-threshold changes (80th pct -> median -> 0) because the 80th-percentile pool (17,751) could not fill K=37,654. Both changes are recorded in the file header and the E1 JSON."),
        disclosures=[
            "Shared writer emits zero-filled outside cells (all-finite export); organizer sample uses NaN outside. Flagged for review.",
            "Literal 13GEMSDOE lattice rule cannot be passed by any raster with N > 22,163 dots: floor (N-6649)/N.",
            "Holdout truth is the mapped catalogue; organizer scoring truth is a new-fault set. HOLDOUT-DTI is a proxy only.",
        ],
    )


def _lattice_uncovered() -> np.ndarray:
    """Cells NOT within 3 px of any pinned 13GEMSDOE lattice dot.  A dot can only avoid the
    literal lattice test if it sits here, so N - |uncovered in footprint| bounds the minimum
    possible forward overlap for N dots (the pigeonhole floor)."""
    with rasterio.open(REGISTRY_DIR / LATTICE_NAME) as s:
        lat = s.read(1)
    return ~UQ._near(UQ._dots(lat))


def e1_flag() -> bool:
    p = EVID / "hgridge_e1_canary.json"
    return bool(json.loads(p.read_text())["canary"]["any_leakage_flag"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("stage", choices=["e1", "e2", "e3"])
    args = ap.parse_args()
    inp = load_inputs()
    ctx = HO.build_holdout(inp["grid"])
    if args.stage == "e1":
        r = stage_e1(inp, ctx)
        print(json.dumps({k: r[k] for k in ("n_crest_candidates", "crest_threshold_pct", "crest_threshold_value")}, indent=1))
        print("max symmetric AUC:", round(r["canary"]["max_symmetric_auc"], 4),
              "leakage flag:", r["canary"]["any_leakage_flag"])
    elif args.stage == "e2":
        r = stage_e2(inp, ctx)
        for row in r["rows"]:
            print(f"{row['arm']:<26} all={row['all']['pooled_dti']:.5f} "
                  f"CI={row['all']['dti_ci95']} n={row['all']['withheld_positives']} | "
                  f"det={row['detached']['pooled_dti']:.5f}")
    else:
        r = stage_e3(inp, ctx)
        print(json.dumps(r["gates"], indent=1))
        print("file:", r["file"], "sha256:", r["sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
