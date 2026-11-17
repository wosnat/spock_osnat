"""Size, taxonomic and clade (KG organism.clade) spread of the 14 Cyanorak hli ortholog groups (researcher curiosity question).

Writes analysis/data/og_conservation.csv: per group, MED4 members, total genes, organisms,
and the organism list; plus the D cluster of the MED4 members (twin-rule clusters).
Run from the repo root: uv run python analyses/2026-11-16-hli_light_stress/analysis/scripts/15_og_conservation.py
"""
from pathlib import Path
import pandas as pd
from multiomics_explorer import genes_by_homolog_group, list_organisms

HERE = Path(__file__).resolve().parents[1]
GROUPS = ["CK_00000050", "CK_00001414", "CK_00001058", "CK_00001313", "CK_00002026",
          "CK_00002025", "CK_00002168", "CK_00002332", "CK_00002661", "CK_00043616",
          "CK_00003573", "CK_00002103", "CK_00003421", "CK_00003510"]
r = genes_by_homolog_group(group_ids=GROUPS, limit=None)
assert r["total_matching"] == len(r["results"]), "truncated"
df = pd.DataFrame(r["results"])
gcol = "group_id"
ocol = "organism_name" if "organism_name" in df.columns else "organism"
ORGS = list_organisms(limit=None)["results"]
n_org_kg = len(ORGS)
CLADE = {o["organism_name"]: (o.get("clade") or "none") for o in ORGS}

def ecotype(org):
    c = CLADE.get(org, "none")
    if "Prochlorococcus" not in org:
        return "non-Prochlorococcus"
    return "HL" if c.startswith("HL") else "LL" if c.startswith("LL") else "Pro clade unknown"
clus = pd.read_csv(HERE / "data" / "explore_D_gene_clusters.csv")[["locus_tag", "cluster"]]
rows = []
for g, sub in df.groupby(gcol):
    med4 = sub[sub[ocol].str.contains("MED4")]
    orgs = sorted(sub[ocol].unique())
    m = med4.merge(clus, on="locus_tag", how="left")
    rows.append(dict(group=g, med4_genes=len(med4), med4_loci=";".join(sorted(med4.locus_tag)),
                     med4_clusters=";".join(sorted(set(m.cluster.dropna().astype(int).astype(str)))),
                     total_genes=len(sub), n_organisms=len(orgs),
                     n_prochlorococcus=sum("Prochlorococcus" in o for o in orgs),
                     n_synechococcus=sum("Synechococcus" in o for o in orgs),
                     n_other=sum(("Prochlorococcus" not in o and "Synechococcus" not in o) for o in orgs),
                     n_pro_HL=sum(ecotype(o) == "HL" for o in orgs),
                     n_pro_LL=sum(ecotype(o) == "LL" for o in orgs),
                     n_pro_clade_unknown=sum(ecotype(o) == "Pro clade unknown" for o in orgs),
                     pro_clades=";".join(sorted({CLADE.get(o, "none") for o in orgs if "Prochlorococcus" in o})),
                     organisms="; ".join(orgs)))
out = pd.DataFrame(rows).sort_values("n_organisms", ascending=False)
out.to_csv(HERE / "data" / "og_conservation.csv", index=False, encoding="utf-8")
print("organisms in KG:", n_org_kg)
print(out.drop(columns=["organisms"]).to_string(index=False))
