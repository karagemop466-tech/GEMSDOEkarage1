"""Experiment E2 (H-E2): the pre-registered H-E1 protocol applied to the isostatic gravity anomaly.

Only the field changes (training_features band 13 ``iso_grav_anom`` instead of band 14 ``tmi``).
Window (21 px, half=10), depth band (300-3000 m), N=0, budget (37,654 dots), spacing (2.8 px),
seeds (101/202/303), holdout cells, canary, league and the decision rule are all inherited unchanged
from ``run_h_e1_euler_contacts.main``. Label-blind: no catalogue or label raster enters the field.
"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
from scripts import run_h_e1_euler_contacts as E1  # noqa: E402

ROOT = E1.ROOT
E1.FIELD = dict(name="iso_grav_anom", band=13)
E1.HYP_ID = "H-E2"
E1.EXP_LABEL = "E2 / H-E2"
E1.NAME = "karage1-he2-euler-gravity-37654-20261031-zeros"
E1.NAME_NAN = "karage1-he2-euler-gravity-37654-20261031-nan"
E1.ARCHIVE = ROOT / "archive" / "research-he2-20261031"
E1.NOTE = "H-E2 Euler on isostatic gravity (N=0, 2.1 km win, 300-3000 m) label-blind; RESEARCH ONLY; holdout-scored"
E1.EVIDENCE = ROOT / "evidence" / "exp_h_e2_euler_gravity_20261031.json"
E1.RUN_CARD = ROOT / "evidence" / "run_card_h_e2_20261031.json"
E1.LEAGUE = ROOT / "evidence" / "holdout_league_h_e2_20261031.json"
E1.CARD_TEXT = dict(
    hypothesis=("Density-contrast contacts in the isostatic gravity anomaly, whose Euler (N=0) depth solutions "
                "agree on a 300-3000 m band, mark fault-bounded density juxtapositions with no mapped trace."),
    mechanism=("Euler homogeneity identity solved on iso_grav_anom in 2.1 km windows; solutions counted per cell "
               "(depth-cluster density). Gravity anomalies are potential fields, so the same Tz filter applies."),
    mimic=("Basin-margin and sediment-basement density steps, intrusive density contacts, and topographic-correction "
           "residuals at high-relief edges produce the same Euler contact geometry."),
)

if __name__ == "__main__":
    E1.main()
