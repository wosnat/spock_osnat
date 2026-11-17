"""A.8 comparison: D outputs before (twin rule, with Coculture HOT1A3 (2016)) vs after dropping it.

Reads the *_pre_A8.csv snapshots (copied from the twin-rule outputs before the A.8 rerun) and the current files.
Writes analysis/data/explore_A8_cluster_comparison.csv (gene by gene), explore_A8_robustness_comparison.csv,
explore_A8_cluster_summary_comparison.csv, explore_A8_spearman_comparison.csv, explore_A8_column_clusters_comparison.csv.
Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/16_compare_A8.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"


def r(n):
    return pd.read_csv(DATA / n, encoding="utf-8", keep_default_na=False, na_values=[""])


old, new = r("explore_D_gene_clusters_pre_A8.csv"), r("explore_D_gene_clusters.csv")
cols = ["locus_tag", "ck_group", "copy_class", "cluster", "cluster_correlation", "agree_correlation",
        "cluster_no_steglich", "agree_no_steglich", "n_measured_cells", "leaf_order"]
c = old[cols].merge(new[cols], on=["locus_tag", "ck_group", "copy_class"], suffixes=("_twinrule", "_A8"))
c["cluster_changed"] = c.cluster_twinrule != c.cluster_A8
c = c.sort_values("leaf_order_A8")
c.to_csv(DATA / "explore_A8_cluster_comparison.csv", index=False, encoding="utf-8")
pd.set_option("display.width", 250)
print(c.to_string(index=False))

rob = pd.DataFrame([dict(version=v, agree_correlation=int(d.agree_correlation.sum()), agree_no_steglich=int(d.agree_no_steglich.sum()),
                         n_genes=len(d), cluster_sizes=" ".join(f"C{k}:{n}" for k, n in d.cluster.value_counts().sort_index().items()))
                    for v, d in (("twin rule", old), ("A.8", new))])
pa, pn = r("explore_D_parameters_pre_A8.csv").iloc[0], r("explore_D_parameters.csv").iloc[0]
for k in ("cut_height_agreement", "cut_height_correlation", "cut_height_no_steglich", "n_columns", "n_columns_no_steglich"):
    rob[k] = [pa[k], pn[k]]
rob.to_csv(DATA / "explore_A8_robustness_comparison.csv", index=False, encoding="utf-8")
print(rob.to_string(index=False))

so, sn = r("explore_D_cluster_summary_pre_A8.csv"), r("explore_D_cluster_summary.csv")
s = so.merge(sn, on=["cluster", "category"], how="outer", suffixes=("_twinrule", "_A8"))
num = ["n_genes", "n_measured_cells", "n_up", "n_down"]
s["changed"] = ~pd.concat([(s[f"{k}_twinrule"].fillna(-1).astype(float) == s[f"{k}_A8"].fillna(-1).astype(float)) for k in num], axis=1).all(axis=1)
s.to_csv(DATA / "explore_A8_cluster_summary_comparison.csv", index=False, encoding="utf-8")
print(s[s.changed].to_string(index=False))

po, pn_ = r("explore_light_level_spearman_pre_A8.csv"), r("explore_light_level_spearman.csv")
p = po.merge(pn_, on=["set", "direction", "y"], suffixes=("_before", "_A8"))
p = p[["set", "direction", "y", "n_tests_before", "n_tests_A8", "spearman_rho_before", "spearman_rho_A8", "p_value_before", "p_value_A8"]]
p.to_csv(DATA / "explore_A8_spearman_comparison.csv", index=False, encoding="utf-8")
print(p.to_string(index=False))

co, cn = r("explore_D_column_clusters_pre_A8.csv"), r("explore_D_column_clusters.csv")
cc = pd.concat([co.assign(version="twin rule"), cn.assign(version="A.8")])[
    ["version", "col_cluster", "n_columns", "n_experiments", "k_col", "cut_height_columns", "by_family"]]
cc.to_csv(DATA / "explore_A8_column_clusters_comparison.csv", index=False, encoding="utf-8")
print(cc.to_string(index=False))
