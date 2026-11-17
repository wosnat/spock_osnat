"""Delta critic: D outputs with the twin rule on all significant-only tables (snapshots *_pre_arrayonly.csv) vs
microarray tables only (current files). Writes analysis/data/explore_twin_arrayonly_cluster_comparison.csv,
explore_twin_arrayonly_summary_comparison.csv, explore_twin_arrayonly_robustness_comparison.csv,
explore_twin_arrayonly_D5_comparison.csv.
Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/19_compare_twin_arrayonly.py
"""
from pathlib import Path

import pandas as pd

DATA = Path(__file__).resolve().parents[1] / "data"
pd.set_option("display.width", 250)


def r(n):
    return pd.read_csv(DATA / n, encoding="utf-8", keep_default_na=False, na_values=[""])


old, new = r("explore_D_gene_clusters_pre_arrayonly.csv"), r("explore_D_gene_clusters.csv")
cols = ["locus_tag", "ck_group", "copy_class", "cluster", "cluster_correlation", "agree_correlation", "cluster_no_steglich",
        "agree_no_steglich", "n_measured_cells", "leaf_order"]
c = old[cols].merge(new[cols], on=["locus_tag", "ck_group", "copy_class"], suffixes=("_before", "_now")).sort_values("leaf_order_now")
c["cluster_changed"] = c.cluster_before != c.cluster_now
c.to_csv(DATA / "explore_twin_arrayonly_cluster_comparison.csv", index=False, encoding="utf-8")
print(c[["locus_tag", "cluster_before", "cluster_now", "cluster_correlation_before", "cluster_correlation_now",
         "cluster_no_steglich_before", "cluster_no_steglich_now", "n_measured_cells_before", "n_measured_cells_now",
         "leaf_order_before", "leaf_order_now"]].to_string(index=False))

pa, pn = r("explore_D_parameters_pre_arrayonly.csv").iloc[0], r("explore_D_parameters.csv").iloc[0]
rob = pd.DataFrame([dict(version=v, agree_correlation=int(d.agree_correlation.sum()), agree_no_steglich=int(d.agree_no_steglich.sum()),
                         cluster_sizes=" ".join(f"C{k}:{n}" for k, n in d.cluster.value_counts().sort_index().items()))
                    for v, d in (("all sig-only tables", old), ("microarray only", new))])
for k in ("cut_height_agreement", "cut_height_correlation", "cut_height_no_steglich", "n_columns"):
    rob[k] = [pa[k], pn[k]]
co, cn = r("explore_D_column_clusters_pre_arrayonly.csv"), r("explore_D_column_clusters.csv")
rob["k_col"] = [co.k_col.iloc[0], cn.k_col.iloc[0]]
rob["cut_height_columns"] = [co.cut_height_columns.iloc[0], cn.cut_height_columns.iloc[0]]
rob["column_cluster_sizes"] = [" ".join(f"K{a}:{b}" for a, b in zip(x.col_cluster, x.n_columns)) for x in (co, cn)]
rob.to_csv(DATA / "explore_twin_arrayonly_robustness_comparison.csv", index=False, encoding="utf-8")
print(rob.to_string(index=False))

so, sn = r("explore_D_cluster_summary_pre_arrayonly.csv"), r("explore_D_cluster_summary.csv")
s = so.merge(sn, on=["cluster", "category"], how="outer", suffixes=("_before", "_now"))
num = ["n_genes", "n_measured_cells", "n_up", "n_down"]
s["changed"] = ~pd.concat([(s[f"{k}_before"].fillna(-1).astype(float) == s[f"{k}_now"].fillna(-1).astype(float)) for k in num],
                          axis=1).all(axis=1)
s.to_csv(DATA / "explore_twin_arrayonly_summary_comparison.csv", index=False, encoding="utf-8")
print(s[s.changed].to_string(index=False))

do, dn = r("explore_D5_conservation_pre_arrayonly.csv"), r("explore_D5_conservation.csv")
k = ["locus_tag", "n_up", "n_up_defined", "pct_up", "n_down", "n_down_defined", "pct_down"]
d = do[k].merge(dn[k], on="locus_tag", suffixes=("_before", "_now"))
d = d[(d.n_up_defined_before != d.n_up_defined_now) | (d.n_down_defined_before != d.n_down_defined_now)
      | (d.n_up_before != d.n_up_now) | (d.n_down_before != d.n_down_now)]
d.to_csv(DATA / "explore_twin_arrayonly_D5_comparison.csv", index=False, encoding="utf-8")
print(d.to_string(index=False))

fo, fn = r("explore_families_scope_pre_arrayonly.csv"), r("explore_families_scope.csv")
f = fo.merge(fn, on=["family_type", "family", "scope_type", "scope"], suffixes=("_before", "_now"))
f = f[(f.n_gene_observations_before != f.n_gene_observations_now) | (f.n_up_before != f.n_up_now) | (f.n_down_before != f.n_down_now)]
print("families scope rows changed:", len(f))
print(f[["family_type", "family", "scope", "n_gene_observations_before", "n_gene_observations_now", "n_up_before", "n_up_now",
         "n_down_before", "n_down_now"]].to_string(index=False))
to, tn = r("explore_timing_pre_arrayonly.csv"), r("explore_timing.csv")
t = to.merge(tn, on=["experiment_id", "timepoint", "set"], suffixes=("_before", "_now"))
t = t[(t.n_measured_before != t.n_measured_now) | (t.n_up_before != t.n_up_now) | (t.n_down_before != t.n_down_now)]
print("timing rows changed:", len(t))
print(t[["label_before", "timepoint", "set", "n_measured_before", "n_measured_now", "n_up_before", "n_up_now", "n_down_before",
         "n_down_now"]].to_string(index=False))
