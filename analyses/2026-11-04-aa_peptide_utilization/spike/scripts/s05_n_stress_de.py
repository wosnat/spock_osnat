"""Spike: MED4 amino-acid/peptide genes + reference N-response genes in the KG's N-stress experiments.
Per-timepoint rows kept. Rows absent from a filtered_subset table are marked 'not in table';
absent from an all_detected_genes table are marked 'not measured'.
Run (repo root): PYTHONUTF8=1 uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s05_n_stress_de.py
"""
import json
from pathlib import Path

import pandas as pd
import multiomics_explorer as me

DATA = Path(__file__).resolve().parents[1] / "data"
DOIS = ["10.1038/msb4100087", "10.1038/ismej.2017.88", "10.1101/2025.11.24.690089"]
EXCL_SUB = ("housekeeping protease", "protein translocation", "GO-only peptidase call (check)")

# ---- gene set ----
t = pd.read_csv(DATA / "med4_aa_peptide_gene_table.csv", encoding="utf-8", keep_default_na=False)
t = t[(t.weak_evidence_only != "yes") & (t.weak_evidence_only.str[:3] != "yes")]
t = t[~t.subrole.apply(lambda s: any(x in s for x in EXCL_SUB))]
t = t[t.role != "regulation-if-found"]  # regulators enter via the reference set below
genes = (t.groupby("locus_tag")
         .agg(gene_name=("gene_name", "first"), role=("role", lambda s: " | ".join(dict.fromkeys(map(str, s)))),
              subrole=("subrole", lambda s: " | ".join(dict.fromkeys(s))),
              aa_class=("aa_class", lambda s: " | ".join(dict.fromkeys(s)))).reset_index())
genes["reference"] = ""

envs = []
ref = {}
for name in ["glnA", "glnB", "ntcA", "pipX", "amt1", "urtA", "ureC", "cynA", "cynS", "glsF"]:
    r = me.resolve_gene(identifier=name, organism="MED4")
    envs.append({"call": "resolve_gene", "args": name, "total_matching": r["total_matching"], "returned": r["returned"]})
    for x in r["results"]:
        ref[x["locus_tag"]] = (x.get("gene_name") or "", f"reference: N response (resolve_gene {name})")
r = me.genes_by_ontology(ontology="cyanorak_role", organism="MED4", term_ids=["cyanorak.role:D.1.3"],
                         min_gene_set_size=0, max_gene_set_size=100000, limit=None)
envs.append({"call": "genes_by_ontology cyanorak.role:D.1.3", "args": "", "total_matching": r["total_matching"],
             "returned": r["returned"]})
for x in r["results"]:
    ref.setdefault(x["locus_tag"], (x.get("gene_name") or "", "reference: N response (Cyanorak role D.1.3 Nitrogen)"))
for lt, (gn, lab) in ref.items():
    if lt in set(genes.locus_tag):
        genes.loc[genes.locus_tag == lt, "reference"] = lab
    else:
        genes = pd.concat([genes, pd.DataFrame([{"locus_tag": lt, "gene_name": gn, "role": "reference only",
                                                  "subrole": "", "aa_class": "", "reference": lab}])],
                          ignore_index=True)
print("genes:", len(genes), "reference:", (genes.reference != "").sum(), "reference-only:", (genes.role == "reference only").sum())

# ---- experiments ----
ex = me.list_experiments(organism="MED4", publication_dois=DOIS, verbose=True, limit=100)
envs.append({"call": "list_experiments", "args": json.dumps(DOIS), "total_matching": ex["total_matching"], "returned": ex["returned"]})
EXP = {x["experiment_id"]: x for x in ex["results"]}

def label(x):
    i = x["experiment_id"]
    if "msb4100087_nitrogen" in i: return (1, "Tolonen06 N-deprivation (array)")
    if "growth_on_urea" in i: return (2, "Tolonen06 urea vs NH4 (array)")
    if "growth_on_cyanate" in i: return (3, "Tolonen06 cyanate vs NH4 (array)")
    if "ismej" in i: return (4, "ismej17 N-depleted (RNA, top-50%)")
    if "rnaseq_axenic" in i: return (5, "2025 axenic lowN vs d7 (RNA)")
    if "proteomics_axenic" in i: return (6, "2025 axenic lowN vs d7 (prot)")
    if "rnaseq_coculture" in i: return (7, "2025 coculture lowN vs d11 (RNA)")
    if "proteomics_coculture" in i: return (8, "2025 coculture lowN vs d11 (prot)")
    if "coculture_alteromonas" in i: return (9, "2025 coculture vs axenic (RNA)")
    return (10, i)

# ---- DE pull ----
lts = sorted(genes.locus_tag)
r = me.differential_expression_by_gene(organism="MED4", locus_tags=lts, experiment_ids=list(EXP), limit=None, verbose=True)
envs.append({"call": "differential_expression_by_gene", "args": f"{len(lts)} genes x {len(EXP)} exps",
             "total_matching": r["total_matching"], "returned": r["returned"],
             "no_expression": ";".join(r.get("no_expression") or []), "not_found": json.dumps(r.get("not_found")),
             "by_table_scope": json.dumps(r.get("by_table_scope")), "warnings": " | ".join(r.get("warnings") or [])})
assert r["returned"] == r["total_matching"]
de = pd.DataFrame(r["results"])
print("DE rows", len(de), "cols", list(de.columns))

# timepoint grid per experiment from the DE rows themselves (all genes pulled)
tp = de.groupby(["experiment_id", "timepoint", "timepoint_order"], dropna=False).size().reset_index()[
    ["experiment_id", "timepoint", "timepoint_order"]]
grid = genes[["locus_tag"]].merge(tp, how="cross")
keep = ["locus_tag", "experiment_id", "timepoint", "timepoint_order", "timepoint_hours", "log2fc", "padj",
        "expression_status", "rank", "control_timing", "growth_phase", "omics_type", "table_scope"]
keep = [c for c in keep if c in de.columns]
long = grid.merge(de[keep], on=["locus_tag", "experiment_id", "timepoint", "timepoint_order"], how="left")
long = long.merge(genes, on="locus_tag", how="left")
long["experiment_label"] = long.experiment_id.map(lambda i: label(EXP[i])[1])
long["exp_order"] = long.experiment_id.map(lambda i: label(EXP[i])[0])
long["omics"] = long.experiment_id.map(lambda i: EXP[i].get("omics_type"))
long["exp_table_scope"] = long.experiment_id.map(lambda i: EXP[i].get("table_scope"))
long["in_table"] = long.log2fc.notna() | long.expression_status.notna()
def status(rw):
    if rw.in_table:
        return rw.expression_status
    return "not in table" if rw.exp_table_scope != "all_detected_genes" else "not measured"
long["status"] = long.apply(status, axis=1)
long["timepoint"] = long.timepoint.fillna("single")
cols = ["locus_tag", "gene_name", "reference", "role", "subrole", "aa_class", "experiment_id", "experiment_label",
        "omics", "exp_table_scope", "timepoint", "timepoint_order", "timepoint_hours", "log2fc", "padj",
        "expression_status", "status", "in_table", "control_timing", "growth_phase", "exp_order"]
cols = [c for c in cols if c in long.columns]
long = long[cols].sort_values(["exp_order", "timepoint_order", "locus_tag"], na_position="first")
long.to_csv(DATA / "med4_n_stress_de_long.csv", index=False, encoding="utf-8")

# ---- per-gene summary ----
rows = []
for lt, g in long.groupby("locus_tag"):
    m = g[g.in_table]
    best = m.loc[m.log2fc.abs().idxmax()] if m.log2fc.notna().any() else None
    rows.append({"locus_tag": lt, "gene_name": g.gene_name.iloc[0], "reference": g.reference.iloc[0],
                 "role": g.role.iloc[0], "subrole": g.subrole.iloc[0], "aa_class": g.aa_class.iloc[0],
                 "n_experiments_measured": m.experiment_id.nunique(), "n_timepoints_measured": len(m),
                 "n_sig_up": int((m.expression_status == "significant_up").sum()),
                 "n_sig_down": int((m.expression_status == "significant_down").sum()),
                 "n_not_in_table": int((g.status == "not in table").sum()),
                 "max_abs_log2fc": None if best is None else round(abs(best.log2fc), 3),
                 "max_log2fc_signed": None if best is None else best.log2fc,
                 "max_at": None if best is None else f"{best.experiment_label} / {best.timepoint}",
                 "max_status": None if best is None else best.expression_status})
summ = pd.DataFrame(rows)
summ.to_csv(DATA / "med4_n_stress_de_summary.csv", index=False, encoding="utf-8")
pd.DataFrame(envs).to_csv(DATA / "med4_n_stress_query_envelopes.csv", index=False, encoding="utf-8")

# ---- manifest prints ----
print("\nper experiment x timepoint: measured / sig_up / sig_down / not in table (table genes and reference)")
pe = long.groupby(["exp_order", "experiment_label", "timepoint_order", "timepoint"]).agg(
    measured=("in_table", "sum"), sig_up=("expression_status", lambda s: (s == "significant_up").sum()),
    sig_down=("expression_status", lambda s: (s == "significant_down").sum()),
    not_in_table=("status", lambda s: (s == "not in table").sum()),
    not_measured=("status", lambda s: (s == "not measured").sum())).reset_index()
pe.to_csv(DATA / "med4_n_stress_per_timepoint_counts.csv", index=False, encoding="utf-8")
print(pe.drop(columns=["exp_order", "timepoint_order"]).to_string())
tab_only = long[long.role != "reference only"]
pe2 = tab_only.groupby("experiment_label").agg(
    genes_measured=("locus_tag", lambda s: s[tab_only.loc[s.index, "in_table"]].nunique()),
    genes_sig_up_any_tp=("locus_tag", lambda s: s[tab_only.loc[s.index, "expression_status"] == "significant_up"].nunique()),
    genes_sig_down_any_tp=("locus_tag", lambda s: s[tab_only.loc[s.index, "expression_status"] == "significant_down"].nunique()))
print("\nTABLE genes (excl reference-only) per experiment:\n", pe2.to_string())
FOCUS = ["PMM1049", "PMM1048", "PMM0421", "PMM0192", "PMM0628", "PMM0821", "PMM0970", "PMM0963", "PMM0920",
         "PMM0186", "PMM0878", "PMM0674", "PMM0919"]
f = long[long.locus_tag.isin(FOCUS)].copy()
f["cell"] = f.apply(lambda r: (f"{r.log2fc:+.2f}" + ("*" if str(r.expression_status).startswith("significant") else ""))
                    if r.in_table else ("NIT" if r.status == "not in table" else "NM"), axis=1)
f["col"] = f.exp_order.astype(str) + " " + f.experiment_label.str.split(" ").str[0:2].str.join(" ") + " " + f.timepoint.astype(str)
piv = f.pivot_table(index=["locus_tag", "gene_name"], columns=["exp_order", "experiment_label", "timepoint_order", "timepoint"],
                    values="cell", aggfunc="first")
piv.to_csv(DATA / "med4_n_stress_focus_genes.csv", encoding="utf-8")
print("\nfocus written:", piv.shape)
