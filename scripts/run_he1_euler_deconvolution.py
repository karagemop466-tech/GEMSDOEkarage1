#!/usr/bin/env python3
"""H-E1 (ranked #2 in knowledge/hypotheses-20261030.md): window Euler deconvolution.

Pre-registered decision rule: DECISION_RULE below, fixed before the run.  Do not edit
after a result is seen.  Every holdout number is HOLDOUT-DTI (evaluator
`gems57-pooled-hide-v2`, 16 hide-and-recover cells); the uniqueness numbers come from
the literal gate re-implemented here (see `literal_registry_rows`), not from the
vendored `gems57/uniqueness.py`, whose bytes do not match its recorded pin.

Method (label-free: the mapped catalogue never enters the surface):
  1. Official band 14 `tmi` is the field T.  x/y gradients come from np.gradient on the
     100 m grid (northing = -row).  Official band 9 `tmi_vg` is taken as Tz.  The
     band's unit is not stated in its description, so the depth scale is UNVERIFIED and
     is reported, not assumed.
  2. Euler's homogeneity equation (x-x0)Tx + (y-y0)Ty + (z-z0)Tz = N(B-T) is solved by
     least squares in every W x W window (W = 11 px = 1.1 km), observation datum z = 0.
     N = structural index.  Primary arm N = 0 (contact of infinite depth extent; Thompson
     1982 / Reid et al. 1990, Reid et al. 2013 Table 1).  Secondary arm N = 1 (thin
     sheet / dyke; disclosed, cannot promote on its own).
  3. Solutions kept if the source lies inside its window and 50 m <= z0 <= 2000 m.
  4. Surface S = Gaussian(sigma 1 px) density of kept solutions, masked to the footprint,
     max-normalised.  Dots = local maxima of S, strongest first, spacing >= 2.8 px,
     budget 37,654 (the budget used by the other lanes).

Controls on the same cells: 3 matched-count random null seeds, the registry raster
GEMSDOE32_B2 (labelled registry-champion, not an organizer score), and a non-Euler
baseline that places the same number of dots at local maxima of tmi_hg (band 3).
Leakage canary: each feature alone, per-cell direction-invariant AUC on the holdout cells.

Usage:  GEMS_DATA_DIR=/tmp/gems_data .venv/bin/python scripts/run_he1_euler_deconvolution.py
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import ndimage as ndi
from scipy.stats import rankdata
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "vendor"))
sys.path.insert(0, str(ROOT / "scripts"))

from gems57 import evaluate_holdout as EH57  # noqa: E402
from gems57 import grid as G57  # noqa: E402
from gems57 import holdout as H57  # noqa: E402
from gems57.validate import validate  # noqa: E402
from gems57.metric import RADIUS_PX  # noqa: E402

import run_h_r1_kth_magedge as HR1  # noqa: E402  (shared helpers: score, paired_ci, place_dots, ...)

DATA = Path(os.environ.get("GEMS_DATA_DIR", "/tmp/gems_data"))
SESSION = "arena/he1-euler-gemsdoe-20261031"
DATE = "2026-10-31"
NAME_PRIMARY = "karage1-he1-euler-contact-si0-37654-20261031-zeros"
NAME_NAN = "karage1-he1-euler-contact-si0-37654-20261031-nan"
ARCHIVE = ROOT / "archive" / "research-he1-20261031"
EVIDENCE = ROOT / "evidence" / "exp_h_e1_euler_20261031.json"

CELL_M = 100.0
WIN = 11                 # window side, px (1.1 km)
DEPTH_MIN_M, DEPTH_MAX_M = 50.0, 2000.0
BUDGET = 37654
SPACING_PX = 2.8
SIGMA_DENSITY_PX = 1.0
SEEDS = (101, 202, 303)
TMI_BAND, TMIVG_BAND, TMIHG_BAND = 14, 9, 3   # 1-based band indices (official descriptions)
TMI_NAME, TMIVG_NAME, TMIHG_NAME = "tmi", "tmi_vg", "tmi_hg"
ARMS = {"primary_SI0_contact": 0, "secondary_SI1_sheet": 1}

# Fixed BEFORE the run.  Not edited after the result is seen.
DECISION_RULE = dict(
    primary_arm="primary_SI0_contact",
    primary_metric="HOLDOUT-DTI pooled, gems57-pooled-hide-v2, 16 cells",
    promote_requires=[
        "primary arm pooled DTI > matched-random-null pooled DTI (mean of 3 seeds)",
        "primary arm pooled DTI > non-Euler tmi_hg baseline pooled DTI",
        "paired per-cell bootstrap 95% CI lower bound of (candidate - null) > 0",
        "leakage canary: every single feature's per-cell direction-invariant AUC < 0.90",
        "shared validator passes on the zeros-outside primary bytes",
        "literal registry gate: surface Spearman <= 0.90 AND final-dot 3 px overlap <= 0.70 vs every local TIF",
    ],
    secondary_arm="SI=1 is reported with the same metrics; it cannot promote on its own",
    note="Even a promote verdict does not clear a weekly slot; a separate selector step is required.",
)


def sha256(p: Path) -> str:
    h = hashlib.sha256()
    with Path(p).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def read_band(path: Path, index: int, expected_prefix: str) -> np.ndarray:
    with rasterio.open(path) as ds:
        desc = ds.descriptions[index - 1]
        assert desc is not None and desc.startswith(expected_prefix + " "), (index, desc)
        return ds.read(index).astype(np.float64)


def euler_solutions(T: np.ndarray, Tz: np.ndarray, core: np.ndarray, N: int,
                    win: int = WIN, chunk: int = 256):
    """Window Euler deconvolution in row chunks.

    ``core`` marks pixels whose full window and gradient stencil are valid.  Coordinates
    are in km (centred), T and derivatives are normalised by a single scalar, which
    leaves the solved positions and depths unchanged (Euler's equation is homogeneous).
    Returns (accepted_mask, row0, col0, z0_m) on the full grid.
    """
    H, Wd = T.shape
    half = win // 2
    scale = float(np.std(T[core])) or 1.0
    Tn = np.where(core, T, 0.0) / scale
    # Tz is taken as nT/m (UNVERIFIED band unit) and converted to per-km like Tx, Ty
    Tzn = np.where(core, Tz * 1000.0, 0.0) / scale
    Tx = np.zeros_like(Tn)
    Ty = np.zeros_like(Tn)
    Tx[:, 1:-1] = (Tn[:, 2:] - Tn[:, :-2]) / 2.0 / (CELL_M / 1000.0)
    Ty[1:-1, :] = -(Tn[2:, :] - Tn[:-2, :]) / 2.0 / (CELL_M / 1000.0)  # northing = -row
    cols = np.arange(Wd, dtype=np.float64)[None, :].repeat(H, 0)
    rows = np.arange(H, dtype=np.float64)[:, None].repeat(Wd, 1)
    X = (cols - Wd / 2.0) * (CELL_M / 1000.0)      # km, easting
    Y = -(rows - H / 2.0) * (CELL_M / 1000.0)      # km, northing
    coref = core.astype(np.float64)

    acc = np.zeros((H, Wd), bool)
    r0_out = np.full((H, Wd), np.nan)
    c0_out = np.full((H, Wd), np.nan)
    z0_out = np.full((H, Wd), np.nan)
    box = lambda a: ndi.uniform_filter(a, size=win, mode="constant", cval=0.0) * (win * win)  # noqa: E731

    for r0 in range(0, H, chunk):
        r1 = min(H, r0 + chunk)
        s0, s1 = max(0, r0 - half), min(H, r1 + half)
        sl = slice(s0, s1)
        Ts, Txs, Tys, Tzs = Tn[sl], Tx[sl], Ty[sl], Tzn[sl]
        Xs, Ys, cs = X[sl], Y[sl], coref[sl]
        comps = [Txs, Tys, Tzs] + ([np.full_like(Ts, float(N))] if N != 0 else [])
        b = Xs * Txs + Ys * Tys + N * Ts
        k = len(comps)
        M = np.zeros(Ts.shape + (k, k))
        v = np.zeros(Ts.shape + (k,))
        for i in range(k):
            for j in range(k):
                M[..., i, j] = box(comps[i] * comps[j] * cs)
            v[..., i] = box(comps[i] * b * cs)
        count = box(cs)
        # output rows only
        o0, o1 = r0 - s0, r1 - s0
        Mo = M[o0:o1]
        vo = v[o0:o1]
        full = (count[o0:o1] >= win * win - 0.5) & (core[r0:r1])
        Msafe = np.where(full[..., None, None], Mo, np.eye(k))
        cnd = np.linalg.cond(Msafe)
        ok = full & np.isfinite(cnd) & (cnd < 1e10)
        theta = np.zeros(vo.shape)
        if ok.any():
            theta[ok] = np.linalg.solve(Mo[ok], vo[ok][..., None])[..., 0]
        x0, y0, z0 = theta[..., 0], theta[..., 1], theta[..., 2]
        # window centre
        rc = np.arange(r0, r1, dtype=np.float64)[:, None].repeat(Wd, 1)
        cc = np.arange(Wd, dtype=np.float64)[None, :].repeat(r1 - r0, 0)
        row0 = H / 2.0 - y0 / (CELL_M / 1000.0)
        col0 = Wd / 2.0 + x0 / (CELL_M / 1000.0)
        z0_m = z0 * 1000.0
        inside = (np.abs(row0 - rc) <= half) & (np.abs(col0 - cc) <= half)
        keep = ok & inside & (z0_m >= DEPTH_MIN_M) & (z0_m <= DEPTH_MAX_M)
        acc[r0:r1] = keep
        r0_out[r0:r1] = row0
        c0_out[r0:r1] = col0
        z0_out[r0:r1] = z0_m
    return acc, r0_out, c0_out, z0_out


def solution_surface(acc, row0, col0, z0, foot):
    H, Wd = foot.shape
    dens = np.zeros((H, Wd))
    depth_sum = np.zeros((H, Wd))
    r = np.rint(row0[acc]).astype(int)
    c = np.rint(col0[acc]).astype(int)
    inb = (r >= 0) & (r < H) & (c >= 0) & (c < Wd)
    r, c, zz = r[inb], c[inb], z0[acc][inb]
    np.add.at(dens, (r, c), 1.0)
    np.add.at(depth_sum, (r, c), zz)
    sm = ndi.gaussian_filter(dens, SIGMA_DENSITY_PX, mode="constant")
    S = np.where(foot, sm, 0.0)
    mx = float(S.max())
    S_norm = (S / mx).astype(np.float32) if mx > 0 else S.astype(np.float32)
    depth_mean = np.where(dens > 0, depth_sum / np.maximum(dens, 1), np.nan)
    return S_norm, depth_mean.astype(np.float32), dict(solutions_in_grid=int(inb.sum()),
                                                      cells_with_solution=int((dens > 0).sum()))


def canary(features: dict, ctx) -> dict:
    out = {}
    for name, arr in features.items():
        per = {}
        for c in ctx.cells:
            a = arr[c.bbox]
            act = c.active & np.isfinite(a)
            truth = np.zeros(c.active.shape, bool)
            truth[c.truth_yx] = True
            y = truth[act]
            if y.sum() == 0 or y.sum() == y.size:
                continue
            auc = float(roc_auc_score(y, a[act]))
            per[c.key] = dict(auc=auc, direction_invariant=max(auc, 1.0 - auc))
        di = [v["direction_invariant"] for v in per.values()]
        out[name] = dict(cells=len(per), max_direction_invariant_auc=float(np.max(di)) if di else None,
                         mean_direction_invariant_auc=float(np.mean(di)) if di else None,
                         passed=bool(di and max(di) < 0.90), per_cell=per)
    return out


def literal_rows(mine_dots: np.ndarray, mine_surface: np.ndarray, paths: list[Path],
                 foot: np.ndarray) -> list[dict]:
    """Literal gate re-implemented from the protocol (not the vendored module).

    Dot overlap = fraction of MY dots within 3 px (disk, radius 3) of THEIR positive
    pixels.  Surface Spearman = rank correlation over the footprint, NaN outside treated
    as 0 in their raster.  Pixel positives are finite & > 0.
    """
    yy, xx = np.mgrid[-3:4, -3:4]
    disk = yy * yy + xx * xx <= RADIUS_PX * RADIUS_PX
    my = mine_dots.astype(bool)
    rows = []
    rank_mine = rankdata(mine_surface[foot].astype(np.float64))
    for p in paths:
        try:
            with rasterio.open(p) as ds:
                if (ds.height, ds.width) != foot.shape:
                    rows.append(dict(file=str(p), error="grid shape mismatch"))
                    continue
                a = ds.read(1).astype(np.float64)
        except Exception as exc:  # noqa: BLE001 - recorded, not hidden
            rows.append(dict(file=str(p), error=repr(exc)))
            continue
        theirs_pos = np.isfinite(a) & (a > 0)
        near_theirs = ndi.binary_dilation(theirs_pos, structure=disk)
        near_mine = ndi.binary_dilation(my, structure=disk)
        n_my = int(my.sum())
        ov = float(near_theirs[my].mean()) if n_my and theirs_pos.any() else 0.0
        rev = float(near_mine[theirs_pos].mean()) if theirs_pos.any() and n_my else 0.0
        inter = int((my & theirs_pos).sum())
        union = int((my | theirs_pos).sum())
        rho = None
        vals = np.where(np.isfinite(a), a, 0.0)[foot]
        if vals.std() > 0 and mine_surface[foot].std() > 0:
            rank_t = rankdata(vals)
            rho = float(np.corrcoef(rank_mine, rank_t)[0, 1])
        rows.append(dict(file=str(p), name=p.name, their_positive_cells=int(theirs_pos.sum()),
                         my_dots_within_3px_of_theirs=ov, their_dots_within_3px_of_mine=rev,
                         jaccard_dot_sets=(inter / union) if union else 0.0,
                         spearman_full_footprint=rho))
    return rows


def registry_paths() -> list[Path]:
    """Every local TIF a submission could duplicate, including earlier research archives.

    Excludes only this run's own outputs (they cannot be their own registry witness).
    """
    pats = [ROOT / "registry" / "*.tif", ROOT / "docs" / "downloads" / "*.tif",
            ROOT / "docs" / "candidates" / "*.tif", ROOT / "archive" / "**" / "*.tif",
            DATA / "scored" / "*.tif"]
    seen, out = set(), []
    for pat in pats:
        for f in sorted(Path(x) for x in __import__("glob").glob(str(pat), recursive=True)):
            p = f.resolve()
            if p in seen or ARCHIVE.resolve() in p.parents:
                continue
            seen.add(p)
            out.append(p)
    return out


def main() -> None:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    grid = G57.load_grid(DATA)
    foot = grid.footprint
    ctx = H57.build_holdout(grid)
    withheld = int(sum(c.n_truth for c in ctx.cells))
    print(f"holdout cells={len(ctx.cells)} withheld={withheld}", flush=True)

    tmi = read_band(DATA / "training_features.tif", TMI_BAND, TMI_NAME)
    tmivg = read_band(DATA / "training_features.tif", TMIVG_BAND, TMIVG_NAME)
    tmihg = read_band(DATA / "training_features.tif", TMIHG_BAND, TMIHG_NAME)
    valid = foot & np.isfinite(tmi) & (tmi > -1e30) & np.isfinite(tmivg) & (tmivg > -1e30)
    core = ndi.binary_erosion(valid, iterations=WIN // 2 + 2)
    print(f"valid={int(valid.sum())} core={int(core.sum())}", flush=True)

    # Unit diagnostic: horizontal gradient magnitude vs official tmi_hg (no scaling applied)
    gx = np.gradient(np.where(valid, tmi, 0.0), axis=1) / CELL_M
    gy = -np.gradient(np.where(valid, tmi, 0.0), axis=0) / CELL_M
    hyp = np.hypot(gx, gy)
    sel = core & (tmihg > -1e30)
    unit_diag = dict(corr_hypot_grad_vs_tmi_hg=float(np.corrcoef(hyp[sel], tmihg[sel])[0, 1]),
                     std_tmi_vg=float(np.std(tmivg[core])), std_hypot_grad_tmi=float(np.std(hyp[core])),
                     note="tmi_vg units are not stated in the band description; depth scale is UNVERIFIED")

    arms, surfaces = {}, {}
    for name, N in ARMS.items():
        acc, r0, c0, z0 = euler_solutions(tmi, tmivg, core, N)
        S, depth_mean, sstats = solution_surface(acc, r0, c0, z0, foot)
        surfaces[name] = (S, depth_mean)
        dots = HR1.place_dots(S, foot, BUDGET, SPACING_PX)
        n_dots = int(dots.sum())
        print(f"{name}: accepted={int(acc.sum())} dots={n_dots}", flush=True)

        cand = HR1.score(dots, ctx)
        keys = [c.key for c in ctx.cells]
        foot_idx = np.flatnonzero(foot.ravel())
        nulls = []
        for seed in SEEDS:
            rng = np.random.default_rng(seed)
            pick = rng.choice(foot_idx, size=n_dots, replace=False)
            nd = np.zeros(foot.size, bool)
            nd[pick] = True
            nulls.append(HR1.score(nd.reshape(foot.shape), ctx))
        null_pooled = float(np.mean([r["pooled_dti"] for r in nulls]))
        null_cell = np.mean([[r["per_cell_dti"][k] for k in keys] for r in nulls], axis=0)
        cand_cell = np.array([cand["per_cell_dti"][k] for k in keys])
        delta = cand_cell - null_cell
        d_lo, d_hi = HR1.paired_ci(delta)

        hg_pref = np.where(valid, tmihg, 0.0)
        hg_pref = np.clip(hg_pref / np.percentile(tmihg[valid], 98), 0, 1).astype(np.float32)
        hg_dots = HR1.place_dots(hg_pref, foot, n_dots, SPACING_PX)
        hg_score = HR1.score(hg_dots, ctx)

        arms[name] = dict(N=N, n_dots=n_dots, accepted_solutions=int(acc.sum()), surface_stats=sstats,
                          candidate=cand, nulls=dict(seeds=list(SEEDS),
                                                     pooled_dti=[r["pooled_dti"] for r in nulls],
                                                     pooled_mean=null_pooled),
                          paired_vs_null=dict(mean_delta=float(delta.mean()), ci95=[d_lo, d_hi]),
                          tmi_hg_baseline=dict(n_dots=int(hg_dots.sum()), holdout=hg_score),
                          dots=dots, surface=S, depth=depth_mean)
        print(f"  pooled DTI={cand['pooled_dti']:.5f} null={null_pooled:.5f} "
              f"tmi_hg={hg_score['pooled_dti']:.5f} CI_delta=({d_lo:.5f},{d_hi:.5f})", flush=True)

    # champion control and the SGMC proxy
    with rasterio.open(ROOT / "registry" / "GEMSDOE32_B2.tif") as ds:
        champ = np.nan_to_num(ds.read(1), nan=0.0) > 0
    champ_score = HR1.score(champ & foot, ctx)

    primary = arms["primary_SI0_contact"]
    S_p, depth_p = surfaces["primary_SI0_contact"]
    feats = {"tmi": np.where(valid, tmi, np.nan), "tmi_vg": np.where(valid, tmivg, np.nan),
             "tmi_hg": np.where(valid & (tmihg > -1e30), tmihg, np.nan),
             "horiz_grad_mag": np.where(core, hyp, np.nan),
             "euler_density_S": S_p.astype(np.float64), "euler_depth_mean": depth_p.astype(np.float64)}
    can = canary(feats, ctx)
    for k, v in can.items():
        print(f"canary {k}: max DI-AUC={v['max_direction_invariant_auc']}", flush=True)

    sgmc_path = DATA / "external" / "derived_sgmc_faults_100m_u8.tif"
    with rasterio.open(sgmc_path) as ds:
        sgmc = (ds.read(1) > 0) & foot
    cat = grid.catalogue
    d_cat = ndi.distance_transform_edt(~cat)
    sgmc_off = sgmc & (d_cat > 3.0)
    proxy = {name: HR1.proxy_recall(arms[name]["dots"], sgmc_off) for name in arms}
    proxy["champion"] = HR1.proxy_recall(champ & foot, sgmc_off)

    # --- artefacts (primary arm) through the matching grid writer, zeros-outside and NaN twin
    values = primary["dots"].astype(np.float32)
    tif_path = ARCHIVE / f"{NAME_PRIMARY}.tif"
    receipt = G57.write_submission(tif_path, values, mode="zeros")
    v_zero = validate(tif_path, foot, None)
    nan_vals = np.where(foot, values, np.float32("nan")).astype(np.float32)
    nan_path = ARCHIVE / f"{NAME_NAN}.tif"
    G57.write_submission(nan_path, nan_vals, mode="nan")
    with rasterio.open(nan_path) as ds:
        a = ds.read(1)
        nan_checks = dict(single_band=ds.count == 1, float32=ds.dtypes[0] == "float32",
                          shape_3730x3292=(ds.height, ds.width) == (3730, 3292),
                          crs_32611=str(ds.crs) == "EPSG:32611",
                          transform_matches=list(tuple(ds.transform)[:6]) == list(tuple(G57.TRANSFORM)[:6]),
                          nan_exactly_outside_footprint=bool(np.array_equal(np.isnan(a), ~foot)),
                          finite_in_footprint_in_0_1=bool(np.isfinite(a[foot]).all() and (a[foot] >= 0).all()
                                                          and (a[foot] <= 1).all()))
    nan_checks["all_passed"] = all(nan_checks.values())

    # --- literal uniqueness gate, surface (pre-placement) and final dots
    paths = registry_paths()
    print(f"registry rasters scanned={len(paths)}", flush=True)
    surf_rows = literal_rows(np.zeros_like(primary["dots"]), S_p, paths, foot)
    dot_rows = literal_rows(primary["dots"], primary["dots"].astype(np.float32), paths, foot)
    ok_rows = [r for r in dot_rows if "error" not in r]
    surf_ok = [r for r in surf_rows if "error" not in r]
    max_rho = max((r["spearman_full_footprint"] for r in surf_ok if r["spearman_full_footprint"] is not None),
                  default=None)
    max_ov = max((r["my_dots_within_3px_of_theirs"] for r in ok_rows), default=None)
    trips = [dict(file=r["name"], my_dots_within_3px=r["my_dots_within_3px_of_theirs"],
                  their_positive_cells=r["their_positive_cells"]) for r in ok_rows
             if r["my_dots_within_3px_of_theirs"] > 0.70]

    crit = dict(
        candidate_beats_null_pooled=bool(primary["candidate"]["pooled_dti"] > primary["nulls"]["pooled_mean"]),
        candidate_beats_tmi_hg_baseline=bool(primary["candidate"]["pooled_dti"]
                                             > primary["tmi_hg_baseline"]["holdout"]["pooled_dti"]),
        paired_ci_lower_bound_gt_zero=bool(primary["paired_vs_null"]["ci95"][0] > 0),
        canary_all_below_0_90=all(v["passed"] for v in can.values()),
        validator_passed=bool(v_zero["all_checks_passed"]),
        registry_surface_rho_le_0_90=bool(max_rho is not None and max_rho <= 0.90),
        registry_dot_overlap_le_0_70=bool(max_ov is not None and max_ov <= 0.70),
    )
    verdict = "promote-to-selector" if all(crit.values()) else "negative"

    def strip(a):
        return {k: v for k, v in a.items() if k not in ("dots", "surface", "depth")}

    out = dict(
        schema="karage1-exp-he1-euler-v1", session=SESSION, date_utc=DATE,
        hypothesis="H-E1 window Euler deconvolution of TMI (SI 0 contact primary, SI 1 sheet secondary)",
        evaluator=dict(module="vendor/gems57 holdout/evaluate_holdout (unmodified; hashes match pins)",
                       version=EH57.VERSION, label="HOLDOUT-DTI", alpha=0.2, beta=0.8, kernel_px=3.0,
                       cells=len(ctx.cells), withheld_positives=withheld,
                       truth_is="withheld MAPPED catalogue segments (not the competition's new-fault set)",
                       implementation_hashes=EH57.implementation_hashes()),
        decision_rule=DECISION_RULE,
        inputs=dict(data_dir=str(DATA), data_status="pinned third-party GitHub mirrors; organizer authenticity NOT established",
                    training_features_sha256=sha256(DATA / "training_features.tif"),
                    sample_submission_sha256=sha256(DATA / "sample_submission.tif"),
                    existing_faults_sha256=sha256(DATA / "existing_faults.tif"),
                    derived_sgmc_sha256=sha256(sgmc_path), valid_cells=int(valid.sum()),
                    core_cells=int(core.sum()), unit_diagnostic=unit_diag,
                    window_px=WIN, depth_band_m=[DEPTH_MIN_M, DEPTH_MAX_M]),
        arms={k: strip(v) for k, v in arms.items()},
        controls=dict(champion_GEMSDOE32_B2=dict(holdout=champ_score,
                                                 label="HOLDOUT-DTI; registry raster; owner-reported 0.2778 unverified")),
        leakage_canary=can,
        proxy_sgmc_offcatalogue=dict(**proxy, label="PROXY (owner-derived USGS SGMC mirror), not competition truth"),
        artefacts=dict(zeros_primary=dict(file=str(tif_path.relative_to(ROOT)), sha256=sha256(tif_path),
                                          bytes=receipt.get("bytes", tif_path.stat().st_size), name=NAME_PRIMARY,
                                          validator_checks=v_zero["checks"],
                                          validator_all_passed=v_zero["all_checks_passed"],
                                          submission_slots_used=0, approved_for_weekly_slot=False),
                       nan_outside_twin=dict(file=str(nan_path.relative_to(ROOT)), sha256=sha256(nan_path),
                                             checks=nan_checks)),
        uniqueness=dict(registry_rasters_scanned=len(paths), surface_max_spearman=max_rho,
                        final_dots_max_my_dots_within_3px=max_ov, dot_gate_trips_70pct=trips,
                        rows_surface=surf_rows, rows_dots=dot_rows,
                        implementation="literal gate re-implemented in this script; vendored gems57/uniqueness.py NOT used (pin mismatch)"),
        criteria=crit,
        verdict=verdict,
        ok_to_submit=False,
        slot_selected_or_spent=False,
    )
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps(out, indent=2, sort_keys=True, default=float) + "\n")
    print(f"verdict={verdict}; wrote {EVIDENCE.relative_to(ROOT)}", flush=True)


if __name__ == "__main__":
    main()
