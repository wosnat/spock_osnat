"""Spike: per-amino-acid summary + validation probes + spike_summary.md tables.
Run: uv run python analyses/2026-11-04-aa_utilization_genomics/spike/scripts/s06_summary.py
"""
import re
from pathlib import Path
import pandas as pd
from multiomics_explorer import resolve_gene

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
AAS = ["Ala", "Arg", "Asn", "Asp", "Cys", "Glu", "Gln", "Gly", "His", "Ile", "Leu", "Lys", "Met", "Phe",
       "Pro", "Ser", "Thr", "Trp", "Tyr", "Val"]
BCAA = {"Ile", "Leu", "Val"}
NPAT = r"(?:^|;)(?:1\.4\.|2\.6\.1\.|3\.5\.1\.|3\.5\.3\.|4\.3\.1\.|4\.4\.1\.|4\.1\.99\.1)"


def tag(df):
    if df.empty:
        return ""
    return "; ".join(sorted({f"{r.locus_tag}({r.gene_name if isinstance(r.gene_name, str) else '-'})"
                             for r in df.itertuples()}))


def main():
    up = pd.read_csv(DATA / "med4_aa_uptake.csv", encoding="utf-8")
    nr = pd.read_csv(DATA / "med4_aa_n_release.csv", encoding="utf-8")
    xc = pd.read_csv(DATA / "med4_aa_metabolism_crosscheck.csv", encoding="utf-8")
    xc["ec_numbers"] = xc.ec_numbers.fillna("")
    xcN = xc[xc.ec_numbers.str.contains(NPAT, regex=True)]
    hits = nr[nr.med4_gene_found]

    rows = []
    for aa in AAS:
        u = up[up.target == aa]
        cls = up[up.target.str.startswith("class:")]
        cls_aa = cls[(cls.target != "class:branched-chain_aa") | (aa in BCAA)]
        cat_rows = hits[hits.amino_acid.str.split(";").apply(lambda L: aa in L)]
        nh4 = cat_rows[cat_rows["mode"] == "release_NH4"]
        tr = cat_rows[cat_rows["mode"] == "transfer_transamination"]
        oth = cat_rows[cat_rows["mode"] == "other_N_route"]
        broad = hits[hits.amino_acid == "ALL"]
        x = xcN[xcN.amino_acid == aa]
        x_extra = x[~x.locus_tag.isin(cat_rows.locus_tag)]
        rows.append({
            "amino_acid": aa,
            "tcdb_direct": tag(u[u.evidence_line == "tcdb_direct"]) or "none found in KG",
            "go_mf_specific": tag(u[u.evidence_line == "go_mf"]) or "none found in KG",
            "sbp_specific": "none found in KG",
            "class_level_calls": "; ".join(sorted({f"{r.locus_tag}[{r.target.replace('class:', '')},{r.evidence_line}]"
                                                    for r in cls_aa.itertuples()})) or "none found in KG",
            "tcdb_family_candidates": tag(u[u.evidence_line == "tcdb_family_candidate"]) or "none",
            "n_release_present": "yes" if len(nh4) or len(tr) else "no",
            "nh4_release_ko_genes": "; ".join(sorted({f"{r.ko}:{r.locus_tag}({r.gene_name})" for r in nh4.itertuples()})) or "none found in KG",
            "transfer_ko_genes": "; ".join(sorted({f"{r.ko}:{r.locus_tag}({r.gene_name})" for r in tr.itertuples()})) or "none found in KG",
            "other_n_route_ko_genes": "; ".join(sorted({f"{r.ko}:{r.locus_tag}({r.gene_name})" for r in oth.itertuples()})) or "",
            "broad_specificity_ko_genes": "; ".join(sorted({f"{r.ko}:{r.locus_tag}({r.gene_name})" for r in broad.itertuples()})),
            "metabolism_arm_N_removing_genes_not_in_KO_catalogue": tag(x_extra),
        })
    s = pd.DataFrame(rows)
    s.to_csv(DATA / "med4_aa_summary.csv", index=False, encoding="utf-8")

    # validation probes
    probes = []
    for name in ["glnA", "urtA", "urtB", "urtC", "urtD", "urtE", "pstS", "pstA", "pstB", "pstC"]:
        r = resolve_gene(identifier=name, organism="MED4")
        for x in r["results"]:
            lt = x["locus_tag"]
            calls = up[up.locus_tag == lt]
            probes.append({"query": name, "total_matching": r["total_matching"], "locus_tag": lt,
                           "gene_name": x.get("gene_name"), "product": x.get("product"),
                           "uptake_rows": "; ".join(f"{c.target}/{c.evidence_line}" for c in calls.itertuples()) or "none"})
        if not r["results"]:
            probes.append({"query": name, "total_matching": r["total_matching"], "locus_tag": "", "uptake_rows": "not resolved"})
    p = pd.DataFrame(probes)
    p.to_csv(DATA / "med4_validation_probes.csv", index=False, encoding="utf-8")

    # markdown fragments
    md = []
    md.append("### Per-amino-acid summary (data/med4_aa_summary.csv)\n")
    md.append(s[["amino_acid", "tcdb_direct", "go_mf_specific", "sbp_specific", "class_level_calls",
                 "tcdb_family_candidates", "n_release_present", "nh4_release_ko_genes", "transfer_ko_genes",
                 "other_n_route_ko_genes", "metabolism_arm_N_removing_genes_not_in_KO_catalogue"]].to_markdown(index=False))
    md.append("\nBroad-specificity KOs (amino_acid = ALL) with a MED4 gene: "
              + (s.broad_specificity_ko_genes.iloc[0] or "none"))
    cat = pd.read_csv(DATA / "med4_n_release_catalogue.csv", encoding="utf-8")
    g = nr.groupby("ko").locus_tag.apply(lambda v: ";".join(sorted(v.dropna())))
    cat["med4_locus_tags"] = cat.ko.map(g).fillna("")
    md.append("\n### KO catalogue (data/med4_n_release_catalogue.csv; mode and shared columns are [interpretation])\n")
    md.append(cat[["amino_acid", "ko", "label", "ec", "mode", "shared_interpretation", "ko_in_kg", "med4_locus_tags"]].to_markdown(index=False))
    md.append("\n### Validation probes (data/med4_validation_probes.csv)\n")
    md.append(p.to_markdown(index=False))
    (DATA / "_summary_tables.md").write_text("\n".join(md), encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
