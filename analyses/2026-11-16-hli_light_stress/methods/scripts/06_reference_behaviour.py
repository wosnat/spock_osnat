"""Methods iteration 2: how each reference set behaves, per experiment group and per stress type.

Counts testable tests and tests with BH padj < 0.05 (oriented direction) per set x scope.
Facts only; no pass/fail. Reads methods/data/control_tests.csv; writes
methods/data/reference_behaviour.csv.

Scopes (scope_type):
  group                 each experiment group
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
ROLE_ORDER = ["broad_stress_growth", "broad_stress", "specific_N", "specific_P", "specific_Fe", "light_specific",
              "photosynthesis", "failed_reference"]


def summarise(g: pd.DataFrame) -> dict:
    n = len(g)
    sig = g[g.padj_bh < 0.05]
    up = int((sig.direction_oriented == "up").sum())
    down = int((sig.direction_oriented == "down").sum())
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
    out["role_rank"] = out.set_role.map({r: i for i, r in enumerate(ROLE_ORDER)})
    out = out.sort_values(["role_rank", "set", "scope_type", "scope"]).drop(columns="role_rank")
    out.to_csv(DATA / "reference_behaviour.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 260)
    pd.set_option("display.max_rows", 500)
    print(out.to_string(index=False, float_format=lambda v: f"{v:.3f}"))


if __name__ == "__main__":
    main()
