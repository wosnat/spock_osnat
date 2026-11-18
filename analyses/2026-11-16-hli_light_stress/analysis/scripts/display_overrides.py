"""Display-only overrides (researcher decisions A.3-A.6, decisions_log.md). Labels and grouping only:
no test, p-value or call changes, and the analysis data CSVs on disk are not rewritten.

- Coculture HOT1A3 vs axenic (2025) is split by time point for display and grouping:
    day 11 (vs axenic day 7, separate repeat run; A.12): both arms exponential -> non-stress, type "coculture, both exponential";
    day 18 (vs axenic day 14): the axenic control is N-starving and dying -> stress family, type "N stress, control side"
            (group nonlight_stress, stress_type nitrogen for scope grouping).
- PRO99-lowN starvation series (axenic day 14 vs day 7; coculture days 18-89 vs day 11): label adds the reference sample (A.12).
- Experiment-level rows (no time point) of the 2025 coculture keep one row with an annotation.

apply(df) works on any frame with experiment_id (+ timepoint for per-time-point rows) and returns a copy.
"""
import pandas as pd

COCULT25 = "10.1101/2025.11.24.690089_coculture_alteromonas_hot1a3_med4_rnaseq"
# Reference samples from the KG design_notes (A.12): the coculture series is compared with itself on day 11;
# the axenic series (a separate repeat run) with itself on day 7.
LOWN = {"10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_axenic":
            ", vs the same axenic series in exponential growth (day 7, separate repeat run), PRO99-lowN",
        "10.1101/2025.11.24.690089_growth_state_pro99lown_nutrient_starvation_med4_rnaseq_coculture":
            ", vs the same culture in exponential growth (day 11), PRO99-lowN"}
TP = {
    (COCULT25, "day 11"): dict(group="nonstress_possible_relief", stress_type="coculture",
                               family="non-stress", type="coculture, both exponential",
                               label_detailed="Coculture HOT1A3 day 11 vs axenic day 7, both exponential, PRO99-lowN"),
    (COCULT25, "day 18"): dict(group="nonlight_stress", stress_type="nitrogen",
                               family="stress", type="N stress, control side",
                               label_detailed=("Coculture day 18 vs N-starving, dying axenic day 14, PRO99-lowN. "
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
        for e, suf in LOWN.items():
            m = d.experiment_id == e
            d.loc[m, "label_detailed"] = [x if str(x).endswith(suf) else f"{x}{suf}" for x in d.loc[m, "label_detailed"]]
        if not has_tp:
            for e, note in EXP_NOTE.items():
                m = d.experiment_id == e
                d.loc[m, "label_detailed"] = [f"{x} [{note}]" for x in d.loc[m, "label_detailed"]]
    if not has_tp:
        d["display_note"] = d.experiment_id.map(EXP_NOTE).fillna("")
    return d


# ---- A.8: Coculture HOT1A3 (2016) is dropped from every exploration display and computation and from the
# part A heatmaps / set bands / per-experiment call figures. Part A tables keep its rows, marked with DROPPED_NOTE.
COCULT16 = "10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_med4_rnaseq"
DROPPED_NOTE = "dropped: unreliable table (A.8)"
# A.13: phosphate starvation (Martiny 2006) is dropped too: the KG table is a 34-gene subset (q < 0.05 at 48 h);
# 22 of 23 hli genes are absent, so hli is undefined at 0-24 h and only weakly defined at 48 h.
PHOSPHATE = "10.1073/pnas.0601301103_phosphorus_phosphate_starvation_med4_microarray"
DROPPED = {COCULT16: DROPPED_NOTE, PHOSPHATE: "dropped: 34-gene filtered table, hli not assessable (A.13)"}


def drop(df: pd.DataFrame) -> pd.DataFrame:
    """Rows of DROPPED experiments removed (A.8). Frames without experiment_id are returned unchanged."""
    if "experiment_id" not in df.columns:
        return df
    return df[~df.experiment_id.isin(DROPPED)].copy()


def mark(df: pd.DataFrame) -> pd.DataFrame:
    """Adds column 'dropped' = DROPPED_NOTE for DROPPED experiments, '' otherwise (part A tables keep the rows)."""
    if "experiment_id" not in df.columns:
        return df
    d = df.copy()
    d["dropped"] = d.experiment_id.map(DROPPED).fillna("")
    return d


def resemblance_without_dropped(data_dir, alpha=0.05):
    """resemblance.csv recounted in memory without DROPPED experiments (A.8), using the same scope rules as
    02_light_readings.py on the raw hli_tests.csv (no display overrides, so only A.8 changes the counts).
    resemblance.csv on disk is not rewritten. Returns (new, old) frames with identical keys."""
    import numpy as np
    from pathlib import Path
    data_dir = Path(data_dir)
    old = pd.read_csv(data_dir / "resemblance.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    t = pd.read_csv(data_dir / "hli_tests.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    t = t[~t.experiment_id.isin(DROPPED)]
    tt = t[t.testable == True]  # noqa: E712
    rows = []
    for r in old.itertuples():
        if r.scope_type == "light_reading_group":
            m = tt.light_reading_group == r.scope
        elif r.scope_type == "nonlight_stress_type":
            m = (tt.group == "nonlight_stress") & (tt.stress_type == r.scope)
        else:
            m = tt.group == r.scope
        g = tt[m & (tt.set == r.set)]
        sig = g[g.padj_bh < alpha]
        n = len(g)
        nu, nd = int((sig.direction == "up").sum()), int((sig.direction == "down").sum())
        rows.append(dict(set=r.set, set_role=r.set_role, scope_type=r.scope_type, scope=r.scope, n_testable=n,
                         n_sig_up=nu, n_sig_down=nd, frac_sig_any=(nu + nd) / n if n else np.nan,
                         frac_sig_up=nu / n if n else np.nan, frac_sig_down=nd / n if n else np.nan,
                         n_experiments=g.experiment_id.nunique()))
    return pd.DataFrame(rows), old
