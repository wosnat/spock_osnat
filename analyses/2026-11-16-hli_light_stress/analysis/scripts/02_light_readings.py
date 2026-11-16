"""Analysis part A, step 2: light readings (fixed rules, applied mechanically) and the resemblance table.

Rules (methods/notebook.md, "Decisions after the methods review" and "Corrections after the delta review"):
  light onset (Steglich, treatment lit):      up = up with light
  constant dark vs light (control lit):       down = up with light
  schedule extension:                         raw hli direction in extended darkness 2 h vs extended light 14 h
                                              (the unflagged pair): same = "schedule response",
                                              opposite = "light response", otherwise "unclear";
                                              the 4 h / 16 h pair is shown as context only
  DCMU, phage dark:                           gene-level counts only

Set-level direction of a timepoint = which direction(s) have a testable hli test with BH padj < 0.05.

Reads analysis/data/hli_tests.csv and hli_gene_calls.csv. Writes analysis/data/light_readings.csv and
analysis/data/resemblance.csv.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/02_light_readings.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
ALPHA = 0.05
RULES = {
    "light_onset": "light onset (treatment lit): up = up with light",
    "constant_dark_vs_light": "constant dark vs light (control lit): down = up with light",
    "schedule_extension": ("schedule extension: raw hli direction, extended darkness 2 h vs extended light 14 h; "
                           "same = schedule response, opposite = light response, otherwise unclear"),
    "electron_transport_DCMU": "DCMU: gene-level counts only",
    "phage_dark": "phage in the dark: gene-level counts only",
}
EXT_DARK = "10.64898/2026.04.15.718746_extended_darkness_med4"
EXT_LIGHT = "10.64898/2026.04.15.718746_extended_light_med4"
SCOPES_LIGHT = ["light_onset", "constant_dark_vs_light", "schedule_extension", "electron_transport_DCMU", "phage_dark"]


def read(name):
    return pd.read_csv(DATA / name, encoding="utf-8", keep_default_na=False, na_values=[""])


def set_direction(up: pd.Series, down: pd.Series) -> str:
    """up / down / both / neither from the two hli test rows; 'not_testable' if neither row is testable."""
    tu, td = bool(up["testable"]), bool(down["testable"])
    if not tu and not td:
        return "not_testable"
    su = tu and up["padj_bh"] < ALPHA
    sd = td and down["padj_bh"] < ALPHA
    return {(True, True): "both", (True, False): "up", (False, True): "down"}.get((su, sd), "neither")


def main():
    t = read("hli_tests.csv")
    gc = read("hli_gene_calls.csv")
    h = t[t.set == "hli"]
    rows = []
    for (eid, tp), g in h[h.light_reading_group != "none"].groupby(["experiment_id", "timepoint"], sort=False):
        up = g[g.direction == "up"].iloc[0]
        dn = g[g.direction == "down"].iloc[0]
        lr = up["light_reading_group"]
        genes = gc[(gc.experiment_id == eid) & (gc.timepoint == tp)]
        cnt = genes.call.value_counts()
        d = set_direction(up, dn)
        if lr == "light_onset":
            reading = {"up": "up with light", "down": "down with light", "both": "both directions",
                       "neither": "no set-level change", "not_testable": "too few changed genes (gene level only)"}[d]
        elif lr == "constant_dark_vs_light":
            reading = {"down": "up with light", "up": "down with light", "both": "both directions",
                       "neither": "no set-level change", "not_testable": "too few changed genes (gene level only)"}[d]
        elif lr == "schedule_extension":
            reading = "see schedule_extension pair rows"
        else:
            reading = "gene-level counts only"
        rows.append(dict(
            row_type="timepoint", light_reading_group=lr, experiment_id=eid, label=up["label"],
            label_detailed=up["label_detailed"], more_light_arm=up["more_light_arm"], timepoint=tp,
            timepoint_order=up["timepoint_order"],
            hli_up_n_sig=up["n_sig_in_set"], hli_up_padj=up["padj_bh"], hli_up_flags=up["flags"],
            hli_down_n_sig=dn["n_sig_in_set"], hli_down_padj=dn["padj_bh"], hli_down_flags=dn["flags"],
            hli_measured=up["n_measured_in_background"], set_direction_raw=d,
            genes_up=int(cnt.get("up", 0)), genes_down=int(cnt.get("down", 0)), genes_ns=int(cnt.get("ns", 0)),
            genes_not_measured=int(cnt.get("not_measured", 0)),
            groups_measured=up["n_groups_measured"], groups_up=up["n_groups_up"],
            groups_down=up["n_groups_down_reported"],
            reading=reading, rule=RULES[lr]))
    lrd = pd.DataFrame(rows)

    def pair(dark_tp, light_tp, kind):
        a = lrd[(lrd.experiment_id == EXT_DARK) & (lrd.timepoint == dark_tp)].iloc[0]
        b = lrd[(lrd.experiment_id == EXT_LIGHT) & (lrd.timepoint == light_tp)].iloc[0]
        da, db = a.set_direction_raw, b.set_direction_raw
        if da in ("up", "down") and db in ("up", "down"):
            reading = "schedule response" if da == db else "light response"
        else:
            reading = "unclear"
        return dict(row_type=kind, light_reading_group="schedule_extension", experiment_id=f"{EXT_DARK} + {EXT_LIGHT}",
                    label=f"Extended darkness {dark_tp} vs extended light {light_tp}",
                    label_detailed=f"{a.label_detailed} [{dark_tp}] / {b.label_detailed} [{light_tp}]",
                    more_light_arm="control / treatment", timepoint=f"{dark_tp} / {light_tp}",
                    set_direction_raw=f"{da} / {db}",
                    genes_up=f"{a.genes_up} / {b.genes_up}", genes_down=f"{a.genes_down} / {b.genes_down}",
                    hli_up_padj=np.nan, hli_down_padj=np.nan,
                    hli_up_flags=f"{a.hli_up_flags or 'none'} / {b.hli_up_flags or 'none'}",
                    hli_down_flags=f"{a.hli_down_flags or 'none'} / {b.hli_down_flags or 'none'}",
                    reading=reading if kind == "schedule_pair_reading" else f"context: {reading}",
                    rule=RULES["schedule_extension"] + (" (reading pair)" if kind == "schedule_pair_reading"
                                                         else " (flagged pair, context only)"))
    lrd = pd.concat([lrd, pd.DataFrame([pair("2h", "14h", "schedule_pair_reading"),
                                        pair("4h", "16h", "schedule_pair_context")])], ignore_index=True)
    order = {g: i for i, g in enumerate(SCOPES_LIGHT)}
    lrd["o"] = lrd.light_reading_group.map(order)
    lrd = lrd.sort_values(["o", "row_type", "label", "timepoint_order"]).drop(columns="o")
    lrd.to_csv(DATA / "light_readings.csv", index=False, encoding="utf-8")

    # ---- resemblance: per set x reading scope, testable tests, padj < 0.05, treatment vs control
    tt = t[t.testable]
    res = []
    scopes = [("light_reading_group", s, tt.light_reading_group == s) for s in SCOPES_LIGHT]
    scopes += [("nonlight_stress_type", st, (tt.group == "nonlight_stress") & (tt.stress_type == st))
               for st in sorted(t[t.group == "nonlight_stress"].stress_type.unique())]
    scopes += [("group", "nonstress_possible_relief", tt.group == "nonstress_possible_relief")]
    for s in ["hli"] + [x for x in t.set.unique() if x != "hli"]:
        for st, sc, mask in scopes:
            g = tt[mask & (tt.set == s)]
            sig = g[g.padj_bh < ALPHA]
            n = len(g)
            nu, nd = int((sig.direction == "up").sum()), int((sig.direction == "down").sum())
            res.append(dict(set=s, set_role=(g.set_role.iloc[0] if n else t[t.set == s].set_role.iloc[0]),
                            scope_type=st, scope=sc, n_testable=n, n_sig_up=nu, n_sig_down=nd,
                            frac_sig_any=(nu + nd) / n if n else np.nan, frac_sig_up=nu / n if n else np.nan,
                            frac_sig_down=nd / n if n else np.nan, n_experiments=g.experiment_id.nunique()))
    pd.DataFrame(res).to_csv(DATA / "resemblance.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_colwidth", 60)
    print(lrd[["light_reading_group", "label", "timepoint", "set_direction_raw", "hli_up_padj", "hli_down_padj",
               "genes_up", "genes_down", "reading"]].to_string(index=False))


if __name__ == "__main__":
    main()
