"""A.8 check: would any call flip if the BH families were recomputed without the dropped 2016 coculture?

Test level: per gene set, BH over testable tests (as part A) with the dropped experiment's tests removed; compare
padj < 0.05 with hli_tests.csv. Experiment level: methods hli_scoring.experiment_aggregate (per-experiment Bonferroni,
then BH across experiments per set) on the reduced tests; compare experiment_call with experiment_calls.csv.
Nothing on disk is changed except the check output analysis/data/qc_A8_bh_recompute.csv.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/18_check_A8_bh.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS.parent / "methods"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hli_scoring as hs  # noqa: E402
import display_overrides as dov  # noqa: E402

DATA = ANALYSIS / "data"


def main():
    t = pd.read_csv(DATA / "hli_tests.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    r = dov.drop(t)
    r["padj_bh_A8"] = np.nan
    for s, g in r[r.testable].groupby("set"):
        r.loc[g.index, "padj_bh_A8"] = hs.bh(g.pvalue.values)
    r["sig_orig"] = r.testable & (r.padj_bh < 0.05)
    r["sig_A8"] = r.testable & (r.padj_bh_A8 < 0.05)
    flips = r[r.sig_orig != r.sig_A8]
    agg = hs.experiment_aggregate(r[["experiment_id", "set", "direction", "pvalue", "padj_bh_A8", "testable"]]
                                  .rename(columns={"padj_bh_A8": "padj_bh"}))
    calls = {}
    for (e, s), g in agg.groupby(["experiment_id", "set"]):
        p = g.set_index("direction")["padj_exp_bh"]
        calls[(e, s)] = hs.call_from_padj(p.get("up", np.nan), p.get("down", np.nan))
    oc = dov.drop(pd.read_csv(DATA / "experiment_calls.csv", encoding="utf-8", keep_default_na=False, na_values=[""]))
    oc = oc.drop_duplicates(["experiment_id", "set"])
    oc["experiment_call_A8"] = [calls.get((e, s), "not_tested") for e, s in zip(oc.experiment_id, oc.set)]
    eflips = oc[oc.experiment_call != oc.experiment_call_A8]
    out = pd.DataFrame([
        dict(check="test-level calls (all 13 sets), BH without dropped experiments (A.8, A.13)", n_compared=int(r.testable.sum()), n_flips=len(flips),
             max_abs_delta_padj=float(np.nanmax(np.abs(r.padj_bh_A8 - r.padj_bh)))),
        dict(check="test-level calls, hli only", n_compared=int(r[r.set == "hli"].testable.sum()),
             n_flips=int((flips.set == "hli").sum()),
             max_abs_delta_padj=float(np.nanmax(np.abs((r.padj_bh_A8 - r.padj_bh)[r.set == "hli"])))),
        dict(check="experiment calls (all sets), recomputed without dropped experiments (A.8, A.13)", n_compared=len(oc), n_flips=len(eflips),
             max_abs_delta_padj=np.nan)])
    out.to_csv(DATA / "qc_A8_bh_recompute.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    print(out.to_string(index=False))
    if len(flips):
        print(flips[["set", "label", "timepoint", "direction", "padj_bh", "padj_bh_A8"]].to_string(index=False))
    if len(eflips):
        print(eflips[["set", "label", "experiment_call", "experiment_call_A8"]].to_string(index=False))


if __name__ == "__main__":
    main()
