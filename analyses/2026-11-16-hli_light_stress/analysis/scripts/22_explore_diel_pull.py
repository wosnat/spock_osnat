"""Exploration E, step 1: pull the diel KG sources for the 23 MED4 hli genes (no tests).

1. Zinser 2009 diel microarray experiment: experiment metadata (list_experiments, verbose) and all hli DE rows
   (differential_expression_by_gene, limit=None); genome-wide row count via summary=True.
2. Mfuzz diel clustering (list_clustering_analyses verbose; gene_clusters_by_gene for the hli genes;
   genes_in_cluster for each cluster hit, for cluster sizes).
3. Waldbauer 2012 derived metrics (list_derived_metrics for the publication; gene_derived_metrics for the hli genes).
Every call asserts total_matching == len(results) where rows are pulled.

Writes analysis/data/explore_E_kg_experiment.csv, explore_E_de_rows.csv, explore_E_cluster_analysis.csv,
explore_E_cluster_membership.csv, explore_E_clusters.csv, explore_E_derived_metric_defs.csv,
explore_E_derived_metrics.csv, explore_E_kg_calls.csv (call log: tool, arguments, total_matching, returned).
Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/22_explore_diel_pull.py
"""
import json
from pathlib import Path

import pandas as pd
from multiomics_explorer import (gene_clusters_by_gene, gene_derived_metrics, genes_in_cluster, list_clustering_analyses,
                                 list_derived_metrics, list_experiments, differential_expression_by_gene)

DATA = Path(__file__).resolve().parents[1] / "data"
EXP = "10.1371/journal.pone.0005135_diel_cycling_med4_microarray"
CLU = "clustering_analysis:journal.pone.0005135:med4_diel_clusters"
WALD_DOI = "10.1371/journal.pone.0043432"
LOG = []


def call(fn, rows=True, **kw):
    r = fn(**kw)
    tm, n = r.get("total_matching"), len(r.get("results", []))
    LOG.append(dict(tool=fn.__name__, args=json.dumps({k: v for k, v in kw.items()}, default=str)[:300],
                    total_matching=tm, returned=n))
    if rows and not kw.get("summary"):
        assert tm == n, (fn.__name__, tm, n)
    return r


def flat(df):
    for c in df.columns:
        if df[c].map(lambda v: isinstance(v, (list, dict))).any():
            df[c] = df[c].map(lambda v: json.dumps(v, default=str) if isinstance(v, (list, dict)) else v)
    return df


def main():
    hli = pd.read_csv(DATA / "explore_D_gene_clusters.csv", encoding="utf-8").locus_tag.tolist()
    assert len(hli) == 23
    e = call(list_experiments, experiment_ids=[EXP], verbose=True, limit=None)
    flat(pd.DataFrame(e["results"])).to_csv(DATA / "explore_E_kg_experiment.csv", index=False, encoding="utf-8")
    print("experiment keys:", list(e["results"][0].keys()))
    print(json.dumps(e["results"][0], indent=1, default=str)[:4000])
    s = call(differential_expression_by_gene, experiment_ids=[EXP], summary=True)
    print("DE summary (all genes):", json.dumps({k: v for k, v in s.items() if k != "results"}, default=str)[:2500])
    de = call(differential_expression_by_gene, experiment_ids=[EXP], locus_tags=hli, verbose=True, limit=None)
    d = flat(pd.DataFrame(de["results"]))
    d.to_csv(DATA / "explore_E_de_rows.csv", index=False, encoding="utf-8")
    print("DE hli rows:", len(d), "columns:", list(d.columns))

    ca = call(list_clustering_analyses, analysis_ids=[CLU], verbose=True, limit=None)
    flat(pd.DataFrame(ca["results"])).to_csv(DATA / "explore_E_cluster_analysis.csv", index=False, encoding="utf-8")
    print(json.dumps(ca["results"][0], indent=1, default=str)[:5000])
    gm = call(gene_clusters_by_gene, locus_tags=hli, analysis_ids=[CLU], verbose=True, limit=None)
    m = flat(pd.DataFrame(gm["results"]))
    m.to_csv(DATA / "explore_E_cluster_membership.csv", index=False, encoding="utf-8")
    print("membership rows:", len(m), "columns:", list(m.columns))
    print({k: v for k, v in gm.items() if k != "results"})
    cid_col = "cluster_id" if "cluster_id" in m.columns else [c for c in m.columns if "cluster" in c and "id" in c][0]
    cl = []
    for cid in sorted(m[cid_col].unique()):
        r = call(genes_in_cluster, cluster_ids=[cid], summary=True)
        cl.append(dict(cluster_id=cid, total_matching=r["total_matching"],
                       envelope=json.dumps({k: v for k, v in r.items() if k != "results"}, default=str)[:600]))
    pd.DataFrame(cl).to_csv(DATA / "explore_E_clusters.csv", index=False, encoding="utf-8")

    dm = call(list_derived_metrics, publication_dois=[WALD_DOI], verbose=True, limit=None)
    defs = flat(pd.DataFrame(dm["results"]))
    defs.to_csv(DATA / "explore_E_derived_metric_defs.csv", index=False, encoding="utf-8")
    print("derived metric defs:", len(defs), list(defs.columns))
    print(defs.drop(columns=[c for c in defs.columns if defs[c].astype(str).str.len().max() > 200]).to_string()[:4000])
    gd = call(gene_derived_metrics, locus_tags=hli, publication_dois=[WALD_DOI], verbose=True, limit=None)
    g = flat(pd.DataFrame(gd["results"]))
    g.to_csv(DATA / "explore_E_derived_metrics.csv", index=False, encoding="utf-8")
    print("gene derived metric rows:", len(g), list(g.columns))
    print({k: v for k, v in gd.items() if k != "results"})
    # coverage check: every gene carrying the Waldbauer transcript peak-time metric (expected 312), hli membership
    from multiomics_explorer import genes_by_numeric_metric
    pk = defs[defs.metric_type == "peak_time_transcript_h"].derived_metric_id.tolist()
    allg = call(genes_by_numeric_metric, derived_metric_ids=pk, limit=None)
    ag = flat(pd.DataFrame(allg["results"]))
    ag.to_csv(DATA / "explore_E_waldbauer_all_genes.csv", index=False, encoding="utf-8")
    print("Waldbauer peak_time_transcript_h genes:", len(ag), "| hli among them:", sorted(set(ag.locus_tag) & set(hli)),
          "| example locus tags:", ag.locus_tag.head(5).tolist())
    # any other MED4 diel derived metrics / experiments in the KG (for the record)
    od = call(list_derived_metrics, organism="MED4", treatment_type=["diel"], limit=None)
    flat(pd.DataFrame(od["results"])).to_csv(
        DATA / "explore_E_diel_metric_inventory.csv", index=False, encoding="utf-8")
    oe = call(list_experiments, organism="MED4", treatment_type=["diel"], limit=None)
    flat(pd.DataFrame(oe["results"])).to_csv(
        DATA / "explore_E_diel_experiment_inventory.csv", index=False, encoding="utf-8")
    x = pd.DataFrame(oe["results"])
    print(x[[c for c in ("experiment_id", "omics_type", "gene_count", "table_scope") if c in x.columns]].to_string())
    y = pd.DataFrame(od["results"])
    print(y[[c for c in ("derived_metric_id", "metric_type", "total_gene_count") if c in y.columns]].to_string())
    pd.DataFrame(LOG).to_csv(DATA / "explore_E_kg_calls.csv", index=False, encoding="utf-8")
    print(pd.DataFrame(LOG).to_string())


if __name__ == "__main__":
    main()
