"""Spike: MED4 vs HOT1A3 counts (role x aa_class; subrole presence) + genome gene counts.
Run (repo root): PYTHONUTF8=1 uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s02_compare.py
"""
import json
from pathlib import Path

import pandas as pd
import multiomics_explorer as me

DATA = Path(__file__).resolve().parents[1] / "data"
ORGS = {"MED4": "med4", "HOT1A3": "hot1a3"}
ROLE_ORDER = ["uptake", "peptidase", "N-entry enzyme", "N-assimilation core", "regulation-if-found"]

frames = []
for org, tag in ORGS.items():
    d = pd.read_csv(DATA / f"{tag}_aa_peptide_gene_table.csv", encoding="utf-8", keep_default_na=False)
    frames.append(d)
df = pd.concat(frames, ignore_index=True)

# genome gene counts from the KG
genome = {}
for org in ORGS:
    r = me.list_organisms(search_text=org) if "search_text" in me.list_organisms.__code__.co_varnames else me.list_organisms()
    for x in r["results"]:
        name = x.get("organism_name") or x.get("preferred_name") or ""
        if org.lower() in name.lower().replace(" ", ""):
            genome[org] = {"organism_name": name, "gene_count": x.get("gene_count")}
            break
(DATA / "genome_gene_counts.json").write_text(json.dumps(genome, indent=1), encoding="utf-8")
print(genome)

def explode(d, col):
    e = d.assign(**{col: d[col].str.split(r" \| ")}).explode(col)
    e[col] = e[col].str.strip()
    return e

# role x aa_class (unique genes; a gene with two classes counts once in each)
e = explode(df, "aa_class")
strong = e[e.weak_evidence_only == "no"]
c_all = e.groupby(["role", "aa_class", "organism"]).locus_tag.nunique().unstack("organism", fill_value=0)
c_str = strong.groupby(["role", "aa_class", "organism"]).locus_tag.nunique().unstack("organism", fill_value=0)
c = c_all.join(c_str, rsuffix="_excl_weak", how="left").fillna(0).astype(int).reset_index()
for o in ORGS:
    for col in (o, f"{o}_excl_weak"):
        if col not in c:
            c[col] = 0
c["role"] = pd.Categorical(c["role"], ROLE_ORDER, ordered=True)
c = c.sort_values(["role", "aa_class"])[["role", "aa_class", "MED4", "HOT1A3", "MED4_excl_weak", "HOT1A3_excl_weak"]]
c.to_csv(DATA / "med4_vs_hot1a3_counts.csv", index=False, encoding="utf-8")

# role totals (unique genes)
t = df.groupby(["role", "organism"]).locus_tag.nunique().unstack("organism", fill_value=0)
ts = df[df.weak_evidence_only == "no"].groupby(["role", "organism"]).locus_tag.nunique().unstack("organism", fill_value=0)
t = t.join(ts, rsuffix="_excl_weak").fillna(0).astype(int).reset_index()
t["role"] = pd.Categorical(t["role"], ROLE_ORDER, ordered=True)
t = t[["role", "MED4", "HOT1A3", "MED4_excl_weak", "HOT1A3_excl_weak"]]
t.sort_values("role").to_csv(DATA / "med4_vs_hot1a3_role_totals.csv", index=False, encoding="utf-8")

# subrole presence
s = explode(df, "subrole")
sp = s.groupby(["role", "subrole", "organism"]).locus_tag.nunique().unstack("organism", fill_value=0).reset_index()
for o in ORGS:
    if o not in sp:
        sp[o] = 0
sp["present_in"] = sp.apply(lambda r: "both" if r.MED4 and r.HOT1A3 else ("MED4 only" if r.MED4 else "HOT1A3 only"), axis=1)
sp["role"] = pd.Categorical(sp["role"], ROLE_ORDER, ordered=True)
sp = sp.sort_values(["role", "present_in", "subrole"])[["role", "subrole", "MED4", "HOT1A3", "present_in"]]
sp.to_csv(DATA / "med4_vs_hot1a3_subroles.csv", index=False, encoding="utf-8")
print(t.to_string())
print(sp.present_in.value_counts().to_string())
