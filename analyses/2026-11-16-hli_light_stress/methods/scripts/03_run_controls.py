"""Methods step 5: comparison sets and random sets across all 29 MED4 experiments.

Scores chaperones, oxidative_stress and photosystem_II (never hli). Random sets are
sized to the number of hli genes inside each timepoint's MAIN background (a
coverage count: full tables = genes measured; significant-only tables = genome).
No hli expression status is read, counted, printed or saved.

Writes (methods/data/):
  control_tests.csv            one row per test x comparison set
  control_experiment_calls.csv per experiment x set x direction aggregate
  random_tests.csv             one row per test x random set (raw p only)
  random_fp_rates.csv          share of random-set tests with p < 0.05
  flag_counts.csv              flags per experiment x timepoint x direction
  de_qc.csv                    per-experiment DE row checks (counts only)

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/methods/scripts/03_run_controls.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from multiomics_explorer import EnrichmentInputs, GraphConnection, fisher_ora

METHODS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(METHODS))
import hli_scoring as hs  # noqa: E402
import kg_io  # noqa: E402
import pipeline  # noqa: E402

DATA = METHODS / "data"
SEED = 20261116
N_RANDOM = 200


def main():
    sets = kg_io.load_gene_sets()
    targets = {s: sets[s] for s in kg_io.COMPARISON_SETS}
    size_ref = sets["hli"]          # used only as a count inside the main background
    ex = kg_io.load_experiments()
    rng = np.random.default_rng(SEED)

    with GraphConnection() as conn:
        genome = kg_io.fetch_genome(conn)
        de_all = {eid: kg_io.fetch_de(eid, conn) for eid in ex.experiment_id}
    print(f"genome genes: {len(genome)}")

    in_table = {}
    for grp, g in ex[ex.in_table_group.fillna("") != ""].groupby("in_table_group"):
        in_table[grp] = sorted(set().union(*[set(de_all[e].locus_tag) for e in g.experiment_id]))
    print("in-table background sizes:", {k: len(v) for k, v in in_table.items()})

    tests, rands, qcs = [], [], []
    for exp in ex.to_dict("records"):
        eid = exp["experiment_id"]
        de = de_all[eid]
        qc = pipeline.de_qc(de) if len(de) else dict(n_rows=0)
        qc.update(experiment_id=eid, label=exp["label"],
                  n_genes_outside_genome=len(set(de.locus_tag) - set(genome)))
        qcs.append(qc)
        if de.empty:
            print("NO DE ROWS:", eid)
            continue
        grp = exp.get("in_table_group")
        t, r = pipeline.score_experiment(
            exp, de, genome, targets, fisher_ora, EnrichmentInputs,
            in_table_bg=in_table.get(grp) if isinstance(grp, str) and grp else None,
            random_size_set=size_ref, n_random=N_RANDOM, rng=rng)
        tests.append(t)
        rands.append(r)
    tests = pd.concat(tests, ignore_index=True)
    rand = pd.concat(rands, ignore_index=True)

    meta = ex.set_index("experiment_id")[["label", "group", "study", "stress_type", "omics", "orientation",
                                          "light_treatment_umol", "light_control_umol"]]
    tests = tests.join(meta, on="experiment_id")
    tests["direction_oriented"] = [hs.orient_direction(d, o) for d, o in zip(tests.direction, tests.orientation)]

    # BH per set across testable tests (main background); separately for the in-table p
    tests["padj_bh"] = np.nan
    tests["padj_in_table_bh"] = np.nan
    for s in targets:
        m = (tests.set == s) & tests.testable
        tests.loc[m, "padj_bh"] = hs.bh(tests.loc[m, "pvalue"].values)
        m2 = m & tests.pvalue_in_table.notna()
        tests.loc[m2, "padj_in_table_bh"] = hs.bh(tests.loc[m2, "pvalue_in_table"].values)
    cols = ["experiment_id", "label", "group", "study", "stress_type", "omics", "timepoint", "timepoint_order",
            "direction", "orientation", "direction_oriented", "set", "test_type", "background_type",
            "background_size", "n_measured_in_background", "n_sig_in_set", "n_sig_total", "genome_share_sig",
            "set_share_sig", "pvalue", "padj_bh", "flags", "testable", "in_table_background_size",
            "n_measured_in_table", "pvalue_in_table", "padj_in_table_bh", "light_treatment_umol",
            "light_control_umol"]
    tests = tests[cols].sort_values(["group", "label", "timepoint_order", "direction", "set"])
    tests.to_csv(DATA / "control_tests.csv", index=False, encoding="utf-8")

    # per-experiment aggregate
    agg = hs.experiment_aggregate(tests[["experiment_id", "set", "direction", "pvalue", "padj_bh", "testable"]])
    agg = agg.join(meta, on="experiment_id")
    agg["direction_oriented"] = [hs.orient_direction(d, o) for d, o in zip(agg.direction, agg.orientation)]
    calls = {}
    for (eid, s), g in agg.groupby(["experiment_id", "set"]):
        p = g.set_index("direction_oriented")["padj_exp_bh"]
        calls[(eid, s)] = hs.call_from_padj(p.get("up", np.nan), p.get("down", np.nan))
    agg["experiment_call_oriented"] = [calls[(e, s)] for e, s in zip(agg.experiment_id, agg.set)]
    agg = agg[["experiment_id", "label", "group", "study", "stress_type", "set", "direction", "orientation",
               "direction_oriented", "n_timepoints", "n_testable", "n_sig_timepoints", "timepoint_count",
               "p_exp_bonferroni", "padj_exp_bh", "experiment_call_oriented"]]
    agg.to_csv(DATA / "control_experiment_calls.csv", index=False, encoding="utf-8")

    # random sets
    rand = rand.join(meta[["label", "group"]], on="experiment_id")
    rand = rand[["experiment_id", "label", "group", "timepoint", "direction", "set", "random_set_size",
                 "n_sig_total", "flags", "testable", "count", "pvalue"]].rename(columns={"set": "random_set"})
    rand.to_csv(DATA / "random_tests.csv", index=False, encoding="utf-8")
    fp = []
    for scope, r in (("testable_tests", rand[rand.testable]), ("all_run_tests", rand)):
        fp.append(dict(scope=scope, group="ALL", n_tests=len(r), n_p_lt_05=int((r.pvalue < 0.05).sum()),
                       frac_p_lt_05=float((r.pvalue < 0.05).mean())))
        for grp, g in r.groupby("group"):
            fp.append(dict(scope=scope, group=grp, n_tests=len(g), n_p_lt_05=int((g.pvalue < 0.05).sum()),
                           frac_p_lt_05=float((g.pvalue < 0.05).mean())))
    fp = pd.DataFrame(fp)
    fp.to_csv(DATA / "random_fp_rates.csv", index=False, encoding="utf-8")

    # flag counts per experiment x timepoint x direction (one set suffices; flags are per test)
    fl = tests[tests.set == "photosystem_II"][["group", "label", "experiment_id", "timepoint", "timepoint_order",
                                              "direction", "n_sig_total", "background_size", "genome_share_sig",
                                              "flags", "testable"]].copy()
    for f in ["too_few", "genome_wide_response", "not_testable", "descriptive", "approximate"]:
        fl[f] = fl["flags"].str.contains(f)
    fl.to_csv(DATA / "flag_counts.csv", index=False, encoding="utf-8")
    pd.DataFrame(qcs).to_csv(DATA / "de_qc.csv", index=False, encoding="utf-8")

    print(f"tests: {tests[['experiment_id','timepoint','direction']].drop_duplicates().shape[0]} "
          f"(rows incl. sets: {len(tests)}); testable: "
          f"{tests[tests.set=='photosystem_II'].testable.sum()}")
    print(fp.to_string())
    print(fl.groupby("group")[["too_few", "genome_wide_response", "not_testable", "descriptive"]].sum())


if __name__ == "__main__":
    main()
