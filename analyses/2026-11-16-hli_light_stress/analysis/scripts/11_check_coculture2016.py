"""Double check of 'Coculture HOT1A3 (2016)' (critic #10): metadata and the genome-wide log2FC distribution.

KG only (list_experiments verbose, list_publications, differential_expression_by_gene all genes). Facts only.
Writes analysis/data/check_coculture2016_rows.csv (all DE rows) and check_coculture2016_summary.csv.

Run from the repo root:
    PYTHONUTF8=1 uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/11_check_coculture2016.py
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from multiomics_explorer import differential_expression_by_gene, list_experiments, list_publications

DATA = Path(__file__).resolve().parents[1] / "data"
EID = "10.1038/ismej.2016.70_coculture_alteromonas_hot1a3_med4_rnaseq"


def main():
    e = list_experiments(experiment_ids=[EID], verbose=True)
    assert e["total_matching"] == 1
    m = e["results"][0]
    keys = ["experiment_id", "experiment_name", "publication_doi", "omics_type", "treatment_type", "treatment", "control",
            "table_scope", "table_scope_detail", "control_timing", "design_notes", "growth_phases", "statistical_test",
            "light_condition", "light_intensity", "medium", "temperature", "experimental_context", "timepoints",
            "genes_by_status", "distinct_gene_count", "gene_count", "coculture_partners", "background_factors"]
    print(json.dumps({k: m.get(k) for k in keys}, indent=1, default=str, ensure_ascii=False))
    pub = list_publications(publication_dois=[m["publication_doi"]], verbose=True)
    p = pub["results"][0]
    print(json.dumps({k: p.get(k) for k in ("doi", "title", "authors", "year", "journal")}, default=str, ensure_ascii=False)[:600])

    de = differential_expression_by_gene(experiment_ids=[EID], limit=None, verbose=True)
    assert de["total_matching"] == len(de["results"]), (de["total_matching"], len(de["results"]))
    df = pd.DataFrame(de["results"])
    print("total_matching", de["total_matching"], "| row keys:", list(df.columns))
    df.to_csv(DATA / "check_coculture2016_rows.csv", index=False, encoding="utf-8")
    lf = df.log2fc.astype(float)
    q = lf.quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99])
    s = dict(n=len(lf), n_nan=int(lf.isna().sum()), pct_negative=100 * float((lf < 0).mean()),
             pct_zero=100 * float((lf == 0).mean()), median=float(lf.median()), mean=float(lf.mean()),
             min=float(lf.min()), max=float(lf.max()), n_abs_gt5=int((lf.abs() > 5).sum()),
             n_abs_gt10=int((lf.abs() > 10).sum()), **{f"q{int(k * 100):02d}": float(v) for k, v in q.items()})
    calls = df.expression_status.value_counts().to_dict()
    s.update({f"status_{k}": v for k, v in calls.items()})
    big_ns = df[(df.expression_status == "not_significant") & (lf.abs() > 5)]
    s["n_ns_abs_gt5"] = len(big_ns)
    s["n_ns_abs_gt5_padj_ge_0.99"] = int((big_ns.padj.astype(float) >= 0.99).sum())
    # hli vs genome
    gs = pd.read_csv(DATA.parents[1] / "methods" / "data" / "gene_sets.csv", encoding="utf-8")
    hli = set(gs[gs.set == "hli"].locus_tag)
    hl = df[df.locus_tag.isin(hli)]
    s.update(hli_n=len(hl), hli_median_log2fc=float(hl.log2fc.median()), hli_pct_negative=100 * float((hl.log2fc < 0).mean()),
             genome_median_log2fc=float(lf.median()))
    # rank of hli in genome (percentile of each hli log2fc)
    ranks = lf.rank(pct=True)
    s["hli_median_genome_percentile"] = float(ranks[df.locus_tag.isin(hli)].median())
    pd.DataFrame([s]).to_csv(DATA / "check_coculture2016_summary.csv", index=False, encoding="utf-8")
    pd.set_option("display.width", 220)
    print(pd.Series(s).to_string())
    top = df.assign(a=lf.abs()).sort_values("a", ascending=False)
    print("\nTop 10 |log2fc| among not_significant rows:")
    print(top[top.expression_status == "not_significant"].head(10)[["locus_tag", "gene_name", "log2fc", "padj", "rank"]].to_string(index=False))
    print("\nTop 10 |log2fc| overall:")
    print(top.head(10)[["locus_tag", "gene_name", "log2fc", "padj", "expression_status"]].to_string(index=False))
    # other numeric columns that could be expression levels
    num = [c for c in df.columns if c not in ("log2fc", "padj") and pd.api.types.is_numeric_dtype(df[c])]
    print("\nother numeric columns:", num)
    for c in num:
        print(c, df[c].describe().to_dict())
    # padj vs |log2fc| relation
    print("\nspearman |log2fc| vs -log10 padj:", pd.Series(lf.abs()).corr(-np.log10(df.padj.astype(float).clip(lower=1e-300)), method="spearman"))
    print("padj distribution:", df.padj.astype(float).describe().to_dict())


if __name__ == "__main__":
    main()
