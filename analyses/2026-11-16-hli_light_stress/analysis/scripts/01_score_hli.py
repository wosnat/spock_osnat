"""Analysis part A, step 1: score hli (and all 12 reference sets) in the 29 MED4 experiments.

Uses the approved methods module unchanged (methods/hli_scoring.py, pipeline.py, kg_io.py; commit 78fb935).
BH is per gene set across testable tests, exactly as in methods/scripts/03_run_controls.py; adding hli as
its own family leaves every reference family unchanged (checked below against methods/data/control_tests.csv).
Random sets: same seed, same draw order as methods, so the same 200 size-matched sets per timepoint.

Writes (analysis/data/):
  hli_tests.csv           one row per test x set (hli + 12 references), control_tests format
                          + empirical_p_random (hli rows) + ortholog-group counts (hli rows)
  experiment_calls.csv    per experiment x set x direction aggregate (all sets)
  hli_gene_calls.csv      one row per hli gene x experiment x timepoint
  hli_random_baseline.csv per hli test: hli p, number of random sets, fraction with p <= hli p
  qc_hli_coverage.csv     hli genes measured per experiment x timepoint (main background and table rows)
  qc_bh_recompute.csv     BH recomputed per set vs padj_bh; reference padj vs methods
  qc_de_sign.csv          up/down/zero log2FC rows per full-table experiment x timepoint
  qc_de.csv               DE row checks (duplicates, truncation)

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/01_score_hli.py
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from multiomics_explorer import EnrichmentInputs, GraphConnection, fisher_ora
from statsmodels.stats.multitest import multipletests

ANALYSIS = Path(__file__).resolve().parents[1]
METHODS = ANALYSIS.parent / "methods"
sys.path.insert(0, str(METHODS))
import hli_scoring as hs  # noqa: E402
import kg_io  # noqa: E402
import pipeline  # noqa: E402

DATA = ANALYSIS / "data"
DATA.mkdir(parents=True, exist_ok=True)
SEED = 20261116          # same as methods/scripts/03_run_controls.py
N_RANDOM = 200


def main():
    sets = kg_io.load_gene_sets()
    hli = sets["hli"]
    targets = {"hli": hli, **{s: sets[s] for s in kg_io.COMPARISON_SETS}}
    gs = pd.read_csv(METHODS / "data" / "gene_sets.csv", encoding="utf-8")
    g2g = {r.locus_tag: r.set.split(":", 1)[1] for r in gs[gs.set.str.startswith("hli_group:")].itertuples()}
    gene_meta = gs[gs.set == "hli"].set_index("locus_tag")[["gene_name", "product"]]
    assert len(g2g) == 23 and set(g2g) == set(hli)
    ex = kg_io.load_experiments()
    rng = np.random.default_rng(SEED)

    with GraphConnection() as conn:
        genome = kg_io.fetch_genome(conn)
        de_all = {eid: kg_io.fetch_de(eid, conn) for eid in ex.experiment_id}   # asserts no truncation
    in_table = {}
    for grp, g in ex[ex.in_table_group.fillna("") != ""].groupby("in_table_group"):
        in_table[grp] = sorted(set().union(*[set(de_all[e].locus_tag) for e in g.experiment_id]))

    tests, rands, gene_rows, og_rows, cov_rows, sign_rows, qc_rows = [], [], [], [], [], [], []
    for exp in ex.to_dict("records"):
        eid = exp["experiment_id"]
        de = de_all[eid]
        qc = pipeline.de_qc(de)
        qc.update(experiment_id=eid, label=exp["label"], n_rows_returned=len(de))
        qc_rows.append(qc)
        grp = exp.get("in_table_group")
        t, r = pipeline.score_experiment(
            exp, de, genome, targets, fisher_ora, EnrichmentInputs,
            in_table_bg=in_table.get(grp) if isinstance(grp, str) and grp else None,
            random_size_set=hli, n_random=N_RANDOM, rng=rng)
        tests.append(t)
        rands.append(r)

        # gene calls and ortholog-group counts per experiment x timepoint (main background, as the pipeline)
        grid = hs.build_test_grid(de)
        d = de.copy()
        d["timepoint"] = d["timepoint"].fillna(hs.NULL_TIMEPOINT).astype(str)
        for tp, g in grid.groupby("timepoint", sort=False):
            gu = g.set_index("direction")
            ttype = pipeline.test_type_for(exp, tp)
            bg, bg_type = hs.main_background(exp["test_type"] if exp["test_type"] != "descriptive" else "sound",
                                             gu.at["up", "measured_genes"], genome)
            calls = hs.gene_calls_from_background(gu.at["up", "sig_genes"], gu.at["down", "sig_genes"], bg)
            oc = hs.ortholog_group_counts({k: v for k, v in calls.items() if k in g2g}, g2g)
            og_rows.append(dict(experiment_id=eid, timepoint=tp, **oc,
                                n_groups_down_reported=("n/a" if exp["up_only"] else oc["n_groups_down"])))
            rows_tp = d[d.timepoint == tp].set_index("locus_tag")
            in_rows = set(rows_tp.index)
            for lt in hli:
                call = calls.get(lt, "not_measured")
                if lt in in_rows:
                    src = "table_row"
                elif lt in bg:
                    src = "absent_from_significant_only_table"
                else:
                    src = "not_in_table"
                gene_rows.append(dict(
                    experiment_id=eid, label=exp["label"], label_detailed=exp["label_detailed"],
                    group=exp["group"], light_reading_group=exp["light_reading_group"],
                    more_light_arm=exp["more_light_arm"], stress_type=exp["stress_type"],
                    timepoint=tp, timepoint_order=g.timepoint_order.iloc[0], test_type=ttype,
                    up_only=exp["up_only"], locus_tag=lt, gene_name=gene_meta.at[lt, "gene_name"],
                    ck_group=g2g[lt], call=call, call_source=src,
                    expression_status=rows_tp.at[lt, "expression_status"] if lt in in_rows else "",
                    log2fc=rows_tp.at[lt, "log2fc"] if lt in in_rows else np.nan,
                    padj=rows_tp.at[lt, "padj"] if lt in in_rows else np.nan,
                    light_treatment_umol=exp["light_treatment_umol"],
                    light_control_umol=exp["light_control_umol"]))
            cov_rows.append(dict(experiment_id=eid, label=exp["label"], timepoint=tp, table_scope=exp["table_scope"],
                                 background_type=bg_type, hli_in_background=len(set(hli) & set(bg)),
                                 hli_with_table_row=len(set(hli) & in_rows),
                                 hli_groups_measured=oc["n_groups_measured"]))
            if exp["table_scope"] == "all_detected_genes":
                lf = rows_tp["log2fc"]
                sign_rows.append(dict(experiment_id=eid, label=exp["label"], timepoint=tp, n_rows=len(lf),
                                      n_log2fc_pos=int((lf > 0).sum()), n_log2fc_neg=int((lf < 0).sum()),
                                      n_log2fc_zero=int((lf == 0).sum()), n_log2fc_nan=int(lf.isna().sum())))

    tests = pd.concat(tests, ignore_index=True)
    rand = pd.concat(rands, ignore_index=True)
    meta = ex.set_index("experiment_id")[["label", "label_detailed", "group", "light_reading_group",
                                          "more_light_arm", "study", "stress_type", "omics", "up_only",
                                          "light_treatment_umol", "light_control_umol"]]
    tests = tests.join(meta, on="experiment_id")
    both = (tests.drop_duplicates(["experiment_id", "timepoint", "direction"])
            .groupby(["experiment_id", "timepoint"])["n_sig_total"].sum().rename("n_sig_both_directions"))
    tests = tests.join(both, on=["experiment_id", "timepoint"])
    tests["share_sig_both_directions"] = tests.n_sig_both_directions / tests.background_size
    tests["padj_bh"] = np.nan
    tests["padj_in_table_bh"] = np.nan
    for s in targets:
        m = (tests.set == s) & tests.testable
        tests.loc[m, "padj_bh"] = hs.bh(tests.loc[m, "pvalue"].values)
        m2 = m & tests.pvalue_in_table.notna()
        tests.loc[m2, "padj_in_table_bh"] = hs.bh(tests.loc[m2, "pvalue_in_table"].values)
    tests["set_role"] = tests["set"].map({**kg_io.SET_ROLE, "hli": "target"})

    # random baseline for hli tests: fraction of the 200 random sets with p <= hli p (same test)
    hp = tests[tests.set == "hli"].set_index("test_id")["pvalue"]
    rb = []
    for tid, g in rand.groupby("test_id"):
        p = hp.get(tid, np.nan)
        rb.append(dict(test_id=tid, hli_pvalue=p, n_random=len(g), random_set_size=int(g.random_set_size.iloc[0]),
                       n_random_p_le_hli=int((g.pvalue <= p).sum()) if not np.isnan(p) else np.nan,
                       empirical_p_random=float((g.pvalue <= p).mean()) if not np.isnan(p) else np.nan,
                       random_frac_p_lt_05=float((g.pvalue < 0.05).mean())))
    rb = pd.DataFrame(rb)
    tests = tests.merge(rb[["test_id", "empirical_p_random", "random_set_size"]].assign(set="hli"),
                        on=["test_id", "set"], how="left")

    # ortholog-group counts onto hli rows
    og = pd.DataFrame(og_rows)
    tests = tests.merge(og.assign(set="hli"), on=["experiment_id", "timepoint", "set"], how="left")

    cols = ["experiment_id", "label", "label_detailed", "group", "light_reading_group", "more_light_arm", "study",
            "stress_type", "omics", "timepoint", "timepoint_order", "direction", "set", "set_role", "test_type",
            "background_type", "background_size", "n_measured_in_background", "n_sig_in_set", "n_sig_total",
            "genome_share_sig", "share_sig_both_directions", "set_share_sig", "pvalue", "padj_bh", "flags",
            "testable", "in_table_background_size", "n_measured_in_table", "pvalue_in_table", "padj_in_table_bh",
            "empirical_p_random", "random_set_size", "n_groups", "n_groups_measured", "n_groups_up",
            "n_groups_down", "n_groups_down_reported", "up_only", "light_treatment_umol", "light_control_umol"]
    tests = tests[cols].sort_values(["group", "label", "timepoint_order", "direction", "set"])
    tests.to_csv(DATA / "hli_tests.csv", index=False, encoding="utf-8")

    agg = hs.experiment_aggregate(tests[["experiment_id", "set", "direction", "pvalue", "padj_bh", "testable"]])
    agg = agg.join(meta.drop(columns=["up_only"]), on="experiment_id")
    agg["set_role"] = agg["set"].map({**kg_io.SET_ROLE, "hli": "target"})
    calls = {}
    for (eid, s), g in agg.groupby(["experiment_id", "set"]):
        p = g.set_index("direction")["padj_exp_bh"]
        calls[(eid, s)] = hs.call_from_padj(p.get("up", np.nan), p.get("down", np.nan))
    agg["experiment_call"] = [calls[(e, s)] for e, s in zip(agg.experiment_id, agg.set)]
    agg = agg[["experiment_id", "label", "label_detailed", "group", "light_reading_group", "more_light_arm", "study",
               "stress_type", "set", "set_role", "direction", "n_timepoints", "n_testable", "n_sig_timepoints",
               "timepoint_count", "p_exp_bonferroni", "padj_exp_bh", "experiment_call"]]
    agg.to_csv(DATA / "experiment_calls.csv", index=False, encoding="utf-8")

    rb = rb.merge(tests[tests.set == "hli"][["experiment_id", "label", "timepoint", "direction", "flags",
                                              "testable"]].assign(
        test_id=lambda x: x.experiment_id + "|" + x.timepoint + "|" + x.direction), on="test_id", how="left")
    rb.to_csv(DATA / "hli_random_baseline.csv", index=False, encoding="utf-8")
    pd.DataFrame(gene_rows).to_csv(DATA / "hli_gene_calls.csv", index=False, encoding="utf-8")
    pd.DataFrame(cov_rows).to_csv(DATA / "qc_hli_coverage.csv", index=False, encoding="utf-8")
    pd.DataFrame(sign_rows).to_csv(DATA / "qc_de_sign.csv", index=False, encoding="utf-8")
    pd.DataFrame(qc_rows).to_csv(DATA / "qc_de.csv", index=False, encoding="utf-8")

    # ---- QC: BH recompute per set; reference rows identical to methods; random sets identical to methods
    qc = []
    for s in targets:
        m = (tests.set == s) & tests.testable
        re_ = multipletests(tests.loc[m, "pvalue"].values, method="fdr_bh")[1]   # independent implementation
        qc.append(dict(check=f"bh_recompute_statsmodels:{s}", n=int(m.sum()),
                       max_abs_diff=float(np.nanmax(np.abs(re_ - tests.loc[m, "padj_bh"].values))) if m.any() else 0.0))
    old = pd.read_csv(METHODS / "data" / "control_tests.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    k = ["experiment_id", "timepoint", "direction", "set"]
    new = pd.read_csv(DATA / "hli_tests.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    mm = old[k + ["pvalue", "padj_bh", "n_sig_in_set", "flags"]].merge(
        new[k + ["pvalue", "padj_bh", "n_sig_in_set", "flags"]], on=k, suffixes=("_m", "_a"))
    for c in ["pvalue", "padj_bh", "n_sig_in_set"]:
        dif = (mm[f"{c}_m"] - mm[f"{c}_a"]).abs()
        qc.append(dict(check=f"reference_vs_methods:{c}", n=len(mm), max_abs_diff=float(np.nanmax(dif.values))))
    qc.append(dict(check="reference_vs_methods:flags_equal", n=len(mm),
                   max_abs_diff=float((mm.flags_m.fillna("") != mm.flags_a.fillna("")).sum())))
    qc.append(dict(check="reference_rows_in_methods_vs_analysis", n=len(old), max_abs_diff=float(len(old) - len(mm))))
    mr = pd.read_csv(METHODS / "data" / "random_tests.csv", encoding="utf-8", keep_default_na=False, na_values=[""])
    rand_ids = rand.assign(timepoint=rand.test_id.str.split("|").str[1])
    m2 = mr[["experiment_id", "timepoint", "direction", "random_set", "pvalue"]].merge(
        rand_ids.rename(columns={"set": "random_set"})[["experiment_id", "timepoint", "direction", "random_set",
                                                        "pvalue"]],
        on=["experiment_id", "timepoint", "direction", "random_set"], suffixes=("_m", "_a"))
    qc.append(dict(check="random_sets_vs_methods:pvalue", n=len(m2),
                   max_abs_diff=float((m2.pvalue_m - m2.pvalue_a).abs().max())))
    qc.append(dict(check="random_rows_methods_vs_analysis", n=len(mr), max_abs_diff=float(len(mr) - len(m2))))
    qc = pd.DataFrame(qc)
    qc.to_csv(DATA / "qc_bh_recompute.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    print(qc.to_string(index=False))
    h = tests[tests.set == "hli"]
    print(f"hli tests: {len(h)}; testable {int(h.testable.sum())}; padj<0.05: {int((h.padj_bh < 0.05).sum())}")


if __name__ == "__main__":
    main()
