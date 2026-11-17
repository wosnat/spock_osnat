"""Shared definitions for exploration D (09, 10, 07): categories, colours, markers, short labels, time parsing, call coding.

Three families, each one hue family (no orange or blue, which mean up / down):
  light / dark (violet): light onset, schedule extension, constant dark vs light, DCMU, phage in the dark
  stress (green / teal):  nitrogen, carbon (CO2), iron, phosphorus, salt, phage (in the light)
  non-stress (brown):     coculture, alternative N source (urea / cyanate), iron re-added, air vs time 0
Assignment uses methods/data/experiments.csv: light_reading_group != none -> light / dark (type = light_reading_group);
group nonlight_stress -> stress (type = stress_type); group nonstress_possible_relief -> non-stress (type from the
experiment). Within a family, types differ by shade and marker shape. Gene clusters are shown with neutral ink
(black border / line styles + "C1".."C4" labels), never with a hue.
"""
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import display_overrides as dov  # noqa: E402

FAMILY_ORDER = ["light / dark", "stress", "non-stress"]
FAMILY_ANCHOR = {"light / dark": "#5b3fd1", "stress": "#1baf7a", "non-stress": "#9a5b2a"}
# (family, type) -> (colour, marker); order = display order
TYPES = {
    ("light / dark", "light onset"): ("#5b3fd1", "o"),
    ("light / dark", "schedule extension"): ("#8e7cf0", "s"),
    ("light / dark", "constant dark vs light"): ("#a24fc2", "^"),
    ("light / dark", "DCMU"): ("#7a2fa8", "D"),
    ("light / dark", "phage in the dark"): ("#c79cf2", "v"),
    ("stress", "nitrogen"): ("#1baf7a", "o"),
    ("stress", "N stress, control side"): ("#7ad6b0", "X"),   # A.3-A.6: coculture 2025 day 18
    ("stress", "carbon (CO2)"): ("#007a3d", "s"),
    ("stress", "iron"): ("#5c9a1b", "^"),
    ("stress", "phosphorus"): ("#8fc65a", "D"),
    ("stress", "salt"): ("#00a087", "v"),
    ("stress", "phage"): ("#3d7a00", "P"),
    ("non-stress", "coculture"): ("#9a5b2a", "o"),
    ("non-stress", "coculture, both exponential"): ("#d4a373", "v"),   # A.3-A.6: coculture 2025 day 11
    ("non-stress", "alternative N source"): ("#c08a52", "s"),
    ("non-stress", "iron re-added"): ("#7d4a22", "^"),
    ("non-stress", "air vs time 0"): ("#b3713a", "D"),
}
LIGHT_TYPE = {"light_onset": "light onset", "schedule_extension": "schedule extension",
              "constant_dark_vs_light": "constant dark vs light", "electron_transport_DCMU": "DCMU",
              "phage_dark": "phage in the dark"}
STRESS_TYPE = {"nitrogen": "nitrogen", "carbon": "carbon (CO2)", "iron": "iron", "phosphorus": "phosphorus",
               "salt": "salt", "viral": "phage"}
NONSTRESS_TYPE = {"coculture": "coculture", "nitrogen": "alternative N source", "iron": "iron re-added",
                  "carbon": "air vs time 0"}
CLUSTER_STYLE = {1: ("-", "o"), 2: ("--", "s"), 3: (":", "^"), 4: ("-.", "D"), 5: ((0, (5, 1, 1, 1)), "v")}
CLUSTER_DASH = {1: "", 2: "6,3", 3: "1.5,2.5", 4: "6,2,1.5,2", 5: "8,2,2,2"}
SHORT = {  # short column labels (full label in hover)
    "Extended darkness": "Ext dark", "Extended light": "Ext light", "Blue 13 vs dark": "Blue 13",
    "Green 13 vs dark": "Green 13", "High white 55 vs dark": "Hi white 55", "Red 13 vs dark": "Red 13",
    "White 13 vs dark": "White 13", "Const dark vs light (no phage)": "Const dark", "Const dark vs light (phage)":
    "Const dark+ph", "DCMU + white 13 vs white 13": "DCMU", "Phage lysate (dark)": "Phage dark",
    "CO2: ambient, no O2": "CO2 amb noO2", "CO2: low": "CO2 low", "CO2: low, no O2": "CO2 low noO2",
    "Iron starvation": "Fe starv", "N deprivation (array)": "N depr arr", "N starvation lowN (axenic)": "lowN ax",
    "N starvation lowN (coculture)": "lowN cocult", "N-depleted (RNA-seq, top 50%)": "N-depl top50",
    "Phosphate starvation": "P starv", "Low salinity 28 psu": "Low salt", "Phage infection (array, up-only)":
    "Phage arr", "Phage lysate (light)": "Phage light", "Air vs time 0": "Air vs t0", "Coculture HOT1A3 (2016)":
    "Cocult 2016", "Coculture HOT1A3 vs axenic (2025)": "Cocult 2025", "Iron re-added": "Fe re-added",
    "Cyanate as N source": "Cyanate", "Urea as N source": "Urea",
}
PHOSPHATE = "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray"
POOLED = ("10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture", "days 60+89")


def category(r) -> tuple[str, str]:
    """(family, type) for an experiment row (dict-like with light_reading_group, group, stress_type).
    Per-time-point display overrides (display_overrides.TP, decisions A.3-A.6) win when the row has a time point."""
    if "experiment_id" in r and "timepoint" in r:
        o = dov.override_for(r["experiment_id"], r["timepoint"])
        if o:
            return o["family"], o["type"]
    if r["light_reading_group"] != "none":
        return "light / dark", LIGHT_TYPE[r["light_reading_group"]]
    if r["group"] == "nonstress_possible_relief":
        return "non-stress", NONSTRESS_TYPE[r["stress_type"]]
    return "stress", STRESS_TYPE[r["stress_type"]]


def type_rank(fam, typ):
    return list(TYPES).index((fam, typ))


def short_tp(tp: str) -> str:
    s = str(tp).replace(" post-inoculation", "").replace("max across 70min-24h", "max").replace(
        "steady state", "ss").replace("R (rescue: 70h vs 48h)", "R").replace("acclimated", "accl")
    return s.replace("day ", "d")


def short_label(label, tp):
    return f"{SHORT.get(label, label)} {short_tp(tp)}"


def parse_hours(label):
    s = str(label).strip()
    m = re.match(r"^(\d+(?:\.\d+)?)\s*h\b", s)
    if m:
        return float(m.group(1))
    m = re.match(r"^(\d+(?:\.\d+)?)\s*min\b", s)
    if m:
        return float(m.group(1)) / 60
    m = re.match(r"^day\s*(\d+(?:\.\d+)?)$", s, re.I)
    if m:
        return float(m.group(1)) * 24
    return np.nan


def up_defined(r) -> bool:
    """Is 'up or not' known for this gene cell? (not measured, or phosphate 0-24 h absent -> no)."""
    if r["call"] in ("not_measured", "not_defined"):   # not_defined = twin rule (twin_rule.py)
        return False
    if r["experiment_id"] == PHOSPHATE and r["test_type"] == "descriptive" and r["call_source"] == "absent_from_significant_only_table":
        return False
    return True


def down_defined(r) -> bool:
    """Is 'down or not' known? Also no in the up-only phage array (a non-significant gene could be down)."""
    return up_defined(r) and not (str(r["up_only"]) == "True")
