"""Methods iteration 2: how each reference set behaves, per experiment group and per stress type.

Counts testable tests and tests with BH padj < 0.05 (treatment vs control, as stored) per set x scope.
Also writes methods/data/schedule_extension_concordance.csv: per reference set, n_sig_in_set
up / down per timepoint in extended light and extended darkness (raw direction).
Facts only; no pass/fail. Reads methods/data/control_tests.csv; writes
methods/data/reference_behaviour.csv.

Scopes (scope_type):
  group                 each experiment group (direction_meaning flags light_onset_photoperiod: mixed lit arms)
  light_reading_group   each light reading (light_onset, constant_dark_vs_light, schedule_extension,
                        electron_transport_DCMU, phage_dark)
  nonlight_stress_type  each stress type inside the non-light stress group
  own_stress            specific sets only: non-light stress tests of the set's own stress type
  other_nonlight_stress specific sets only: non-light stress tests of every other stress type
  all_other_tests       specific sets only: every testable test outside the set's own non-light stress type
  K2_nonlight_down      ribosomal proteins: non-light stress tests (fraction significant down is frac_sig_down)

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/methods/scripts/06_reference_behaviour.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
OWN = {"adaptation_N": "nitrogen", "adaptation_P": "phosphorus", "adaptation_Fe": "iron"}
LIGHT_READING_GROUPS = ["light_onset", "constant_dark_vs_light", "schedule_extension", "electron_transport_DCMU",
                        "phage_dark"]
ROLE_ORDER = ["broad_stress_growth", "broad_stress", "specific_N", "specific_P", "specific_Fe", "light_specific",
              "photosynthesis", "failed_reference"]


def summarise(g: pd.DataFrame) -> dict:
    n = len(g)
    sig = g[g.padj_bh < 0.05]
    up = int((sig.direction == "up").sum())
    down = int((sig.direction == "down").sum())
    return dict(n_testable=n, n_sig_up=up, n_sig_down=down,
                frac_sig_any=(up + down) / n if n else float("nan"),
                frac_sig_up=up / n if n else float("nan"), frac_sig_down=down / n if n else float("nan"),
                n_experiments=g.experiment_id.nunique())


def main():
    t = pd.read_csv(DATA / "control_tests.csv", encoding="utf-8")
    t = t[t.testable]
    rows = []
    for s, gs in t.groupby("set"):
        role = gs.set_role.iloc[0]
        base = dict(set=s, set_role=role)
        for grp, g in gs.groupby("group"):
            rows.append({**base, "scope_type": "group", "scope": grp, **summarise(g)})
        for lr in LIGHT_READING_GROUPS:   # one row per light reading, even with no testable test
            rows.append({**base, "scope_type": "light_reading_group", "scope": lr,
                         **summarise(gs[gs.light_reading_group == lr])})
        nl = gs[gs.group == "nonlight_stress"]
        for st, g in nl.groupby("stress_type"):
            rows.append({**base, "scope_type": "nonlight_stress_type", "scope": st, **summarise(g)})
        if s in OWN:
            own = OWN[s]
            rows.append({**base, "scope_type": "own_stress", "scope": f"nonlight_stress:{own}",
                         **summarise(nl[nl.stress_type == own])})
            rows.append({**base, "scope_type": "other_nonlight_stress", "scope": f"nonlight_stress:not {own}",
                         **summarise(nl[nl.stress_type != own])})
            rows.append({**base, "scope_type": "all_other_tests", "scope": f"all testable tests except nonlight_stress:{own}",
                         **summarise(gs[~((gs.group == "nonlight_stress") & (gs.stress_type == own))])})
        if s == "ribosomal_proteins":
            rows.append({**base, "scope_type": "K2_nonlight_down", "scope": "nonlight_stress", **summarise(nl)})
    out = pd.DataFrame(rows)
    # the light_onset_photoperiod group mixes experiments whose lit arm is the treatment and the control
    out.insert(4, "direction_meaning", ["mixed lit arms - do not read direction"
                                        if (st == "group" and sc == "light_onset_photoperiod") else "treatment vs control"
                                        for st, sc in zip(out.scope_type, out.scope)])
    out["role_rank"] = out.set_role.map({r: i for i, r in enumerate(ROLE_ORDER)})
    out = out.sort_values(["role_rank", "set", "scope_type", "scope"]).drop(columns="role_rank")
    out.to_csv(DATA / "reference_behaviour.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_rows", 500)
    print(out.to_string(index=False, float_format=lambda v: f"{v:.3f}"))

    # schedule-extension concordance (critic finding 1): raw counts, all tests (incl. flagged)
    allt = pd.read_csv(DATA / "control_tests.csv", encoding="utf-8")
    se = allt[allt.light_reading_group == "schedule_extension"].copy()
    se["flags"] = se["flags"].fillna("").replace("", "none")
    piv = se.pivot_table(index=["set", "set_role", "label", "timepoint"], columns="direction",
                         values=["n_sig_in_set", "padj_bh", "flags", "testable"], aggfunc="first")
    piv.columns = [f"{a}_{b}" for a, b in piv.columns]
    meas = se.drop_duplicates(["set", "label", "timepoint"]).set_index(["set", "set_role", "label", "timepoint"])[
        ["n_measured_in_background", "more_light_arm", "share_sig_both_directions"]]
    conc = piv.join(meas).reset_index()
    conc["role_rank"] = conc.set_role.map({r: i for i, r in enumerate(ROLE_ORDER)})
    conc = conc.sort_values(["role_rank", "set", "label", "timepoint"]).drop(columns="role_rank")
    conc = conc[["set", "set_role", "label", "more_light_arm", "timepoint", "n_measured_in_background",
                 "n_sig_in_set_up", "n_sig_in_set_down", "padj_bh_up", "padj_bh_down", "flags_up", "flags_down",
                 "testable_up", "testable_down", "share_sig_both_directions"]]
    conc.to_csv(DATA / "schedule_extension_concordance.csv", index=False, encoding="utf-8")
    print(conc.to_string(index=False, float_format=lambda v: f"{v:.3g}"))


if __name__ == "__main__":
    main()
