"""Collapsed-ORA sensitivity (critic #2): the hli set test with each identical-signal pair counted once.

For each hli test, every detected pair (explore_twin_pairs.csv) with both members in the test's main background is
merged into one unit (the first member): the second member leaves the background (N - 1) and the hli set (K - 1);
the unit is significant in a direction if either member is (so n and k drop by 1 where both members were significant).
Same backgrounds, same tests and flags as part A (testable = as in hli_tests.csv), same Fisher (methods hli_scoring.run_fisher
-> package fisher_ora), same BH per set across testable tests, same per-experiment Bonferroni -> BH.

Delta critic fix: pairs are collapsed in MICROARRAY tables only (where the pair members share array probes);
RNA-seq tests are rerun unchanged (n_pairs_collapsed = 0). BH family as in part A (all testable tests, including the
A.8-dropped 2016 coculture, whose rows are kept in hli_tests_twin_collapsed.csv with dropped = A.8 note and left out
of the two comparison files and the printed counts).

Writes analysis/data/hli_tests_twin_collapsed.csv, experiment_calls_twin_collapsed.csv and
twin_collapsed_comparison.csv (test level) / twin_collapsed_comparison_experiments.csv.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/13_twin_collapsed_ora.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from multiomics_explorer import EnrichmentInputs, GraphConnection, fisher_ora

ANALYSIS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ANALYSIS.parent / "methods"))
import hli_scoring as hs  # noqa: E402
import kg_io  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import display_overrides as dov  # noqa: E402

DATA = ANALYSIS / "data"


def main():
    sets = kg_io.load_gene_sets()
    hli = set(sets["hli"])
    ex = kg_io.load_experiments()
    pairs = pd.read_csv(DATA / "explore_twin_pairs.csv", encoding="utf-8")
    P = list(zip(pairs.gene_a, pairs.gene_b))
    orig = pd.read_csv(DATA / "hli_tests.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    oh = orig[orig.set == "hli"].copy()
    oh["test_id"] = oh.experiment_id + "|" + oh.timepoint + "|" + oh.direction
    meta = oh.set_index("test_id")
    with GraphConnection() as conn:
        genome = kg_io.fetch_genome(conn)
        de_all = {e: kg_io.fetch_de(e, conn) for e in ex.experiment_id}
    rows = []
    for exp in ex.to_dict("records"):
        eid = exp["experiment_id"]
        grid = hs.build_test_grid(de_all[eid])
        for r in grid.itertuples():
            tid = f"{eid}|{r.timepoint}|{r.direction}"
            m = meta.loc[tid]
            if ("descriptive" in str(m.flags)) or ("not_testable" in str(m.flags)):
                continue
            bg, _ = hs.main_background(exp["test_type"] if exp["test_type"] != "descriptive" else "sound", r.measured_genes, genome)
            bg, sig, tgt = set(bg), set(r.sig_genes), set(hli)
            n_collapsed = 0
            for a, b in (P if exp["omics"] == "MICROARRAY" else []):   # delta critic: microarray only
                if a in bg and b in bg:
                    n_collapsed += 1
                    bg.discard(b)
                    tgt.discard(b)
                    if b in sig:
                        sig.discard(b)
                        sig.add(a)
            res = hs.run_fisher({tid: sorted(sig & bg)}, {tid: sorted(bg)}, {"hli": sorted(tgt)}, fisher_ora, EnrichmentInputs)
            q = res.iloc[0]
            rows.append(dict(test_id=tid, experiment_id=eid, label=exp["label"], timepoint=r.timepoint, direction=r.direction,
                             omics=exp["omics"], n_pairs_collapsed=n_collapsed, background_size=int(q.background_size), n_sig_total=int(q.n_sig_in_bg),
                             n_measured_in_background=int(q.bg_count), n_sig_in_set=int(q["count"]), pvalue=float(q.pvalue),
                             testable=bool(m.testable), flags=m.flags,
                             orig_background_size=int(m.background_size), orig_n_measured=int(m.n_measured_in_background),
                             orig_n_sig_in_set=m.n_sig_in_set, orig_pvalue=m.pvalue, orig_padj=m.padj_bh))
    t = pd.DataFrame(rows)
    t["padj_bh"] = np.nan
    msk = t.testable
    t.loc[msk, "padj_bh"] = hs.bh(t.loc[msk, "pvalue"].values)
    t["sig"] = msk & (t.padj_bh < 0.05)
    t["orig_sig"] = msk & (t.orig_padj < 0.05)
    t["call_changed"] = t.sig != t.orig_sig
    t["dropped"] = t.experiment_id.map(dov.DROPPED).fillna("")
    t.to_csv(DATA / "hli_tests_twin_collapsed.csv", index=False, encoding="utf-8")
    t_all = t
    t = dov.drop(t)   # A.8: comparison outputs and counts without the 2016 coculture
    t[["experiment_id", "omics", "label", "timepoint", "direction", "n_pairs_collapsed", "orig_n_sig_in_set", "orig_n_measured",
       "n_sig_in_set", "n_measured_in_background", "orig_pvalue", "pvalue", "orig_padj", "padj_bh", "orig_sig", "sig",
       "call_changed", "flags"]].to_csv(DATA / "twin_collapsed_comparison.csv", index=False, encoding="utf-8")

    agg = hs.experiment_aggregate(t_all.assign(set="hli")[["experiment_id", "set", "direction", "pvalue", "padj_bh", "testable"]])
    calls = {}
    for eid, g in agg.groupby("experiment_id"):
        p = g.set_index("direction")["padj_exp_bh"]
        calls[eid] = hs.call_from_padj(p.get("up", np.nan), p.get("down", np.nan))
    agg["experiment_call"] = agg.experiment_id.map(calls)
    agg["dropped"] = agg.experiment_id.map(dov.DROPPED).fillna("")
    agg.to_csv(DATA / "experiment_calls_twin_collapsed.csv", index=False, encoding="utf-8")
    oc = pd.read_csv(DATA / "experiment_calls.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    oc = dov.drop(oc[oc.set == "hli"])
    cmp = (oc[["experiment_id", "label", "direction", "padj_exp_bh", "experiment_call"]]
           .merge(agg[["experiment_id", "direction", "padj_exp_bh", "experiment_call"]], on=["experiment_id", "direction"],
                  how="left", suffixes=("_orig", "_collapsed")))
    cmp["experiment_call_collapsed"] = cmp.experiment_call_collapsed.fillna("not_tested")
    cmp["call_changed"] = cmp.experiment_call_orig != cmp.experiment_call_collapsed
    cmp.to_csv(DATA / "twin_collapsed_comparison_experiments.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 250)
    print("A.8 rows excluded from comparison:", len(t_all) - len(t), "| collapsed tests by omics:",
          t.groupby("omics").n_pairs_collapsed.apply(lambda x: int((x > 0).sum())).to_dict())
    print("tests run:", len(t), "testable:", int(t.testable.sum()), "| sig orig:", int(t.orig_sig.sum()), "collapsed:", int(t.sig.sum()))
    print("test calls changed:")
    print(t[t.call_changed][["label", "timepoint", "direction", "orig_n_sig_in_set", "orig_n_measured", "n_sig_in_set",
                             "n_measured_in_background", "orig_padj", "padj_bh"]].to_string(index=False))
    print("experiment calls changed:")
    print(cmp[cmp.call_changed].to_string(index=False))
    s = t[t.orig_sig | t.sig][["label", "timepoint", "direction", "n_pairs_collapsed", "orig_n_sig_in_set", "orig_n_measured",
                               "n_sig_in_set", "n_measured_in_background", "orig_padj", "padj_bh"]]
    print(s.to_string(index=False))


if __name__ == "__main__":
    main()
