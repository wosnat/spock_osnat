"""Display-only overrides (researcher decisions A.3-A.6, decisions_log.md). Labels and grouping only:
no test, p-value or call changes, and the analysis data CSVs on disk are not rewritten.

- Coculture HOT1A3 vs axenic (2025) is split by time point for display and grouping:
    day 11: both arms exponential -> non-stress, type "coculture, both exponential";
    day 18: the axenic control is N-starving and dying -> stress family, type "N stress, control side"
            (group nonlight_stress, stress_type nitrogen for scope grouping).
- PRO99-lowN starvation series (axenic day 14; coculture days 18-89): label adds the reference sample.
- Experiment-level rows (no time point) of the 2025 coculture keep one row with an annotation.

apply(df) works on any frame with experiment_id (+ timepoint for per-time-point rows) and returns a copy.
"""
import pandas as pd

COCULT25 = "10.1101/2025.11.24.690089_coculture_alteromonas_hot1a3_med4_rnaseq"
LOWN = {"10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_axenic",
        "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture"}
LOWN_SUFFIX = ", vs the same culture in exponential growth (day 11), PRO99-lowN"
TP = {
    (COCULT25, "day 11"): dict(group="nonstress_possible_relief", stress_type="coculture",
                               family="non-stress", type="coculture, both exponential",
                               label_detailed="Coculture HOT1A3 vs axenic, both exponential (day 11), PRO99-lowN"),
    (COCULT25, "day 18"): dict(group="nonlight_stress", stress_type="nitrogen",
                               family="stress", type="N stress, control side",
                               label_detailed=("Coculture vs N-starving, dying axenic (day 18), PRO99-lowN. "
                                               "Down = higher in the starving control")),
}
EXP_NOTE = {COCULT25: "day 11 non-stress; day 18 N stress from the control side; see A.3–A.6"}


def override_for(experiment_id, timepoint):
    return TP.get((experiment_id, str(timepoint)))


def apply(df: pd.DataFrame) -> pd.DataFrame:
    if "experiment_id" not in df.columns:
        return df
    d = df.copy()
    has_tp = "timepoint" in d.columns
    if "label_detailed" in d.columns:
        d["label_detailed"] = d["label_detailed"].astype(object)
    if has_tp:
        for (e, tp), o in TP.items():
            m = (d.experiment_id == e) & (d.timepoint.astype(str) == tp)
            if not m.any():
                continue
            for col in ("group", "stress_type", "label_detailed"):
                if col in d.columns:
                    d.loc[m, col] = o[col]
    if "label_detailed" in d.columns:
        m = d.experiment_id.isin(LOWN)
        d.loc[m, "label_detailed"] = [x if str(x).endswith(LOWN_SUFFIX) else f"{x}{LOWN_SUFFIX}" for x in d.loc[m, "label_detailed"]]
        if not has_tp:
            for e, note in EXP_NOTE.items():
                m = d.experiment_id == e
                d.loc[m, "label_detailed"] = [f"{x} [{note}]" for x in d.loc[m, "label_detailed"]]
    if not has_tp:
        d["display_note"] = d.experiment_id.map(EXP_NOTE).fillna("")
    return d
