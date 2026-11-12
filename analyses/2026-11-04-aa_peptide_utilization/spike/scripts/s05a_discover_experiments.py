"""Spike discovery: MED4 N-stress experiments in three publications + reference N-response genes.
Run (repo root): PYTHONUTF8=1 uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s05a_discover_experiments.py
"""
import json
from pathlib import Path

import pandas as pd
import multiomics_explorer as me

DATA = Path(__file__).resolve().parents[1] / "data"
DOIS = ["10.1038/msb4100087", "10.1038/ismej.2017.88", "10.1101/2025.11.24.690089"]
r = me.list_experiments(organism="MED4", publication_dois=DOIS, verbose=True, limit=100)
print("list_experiments total_matching", r["total_matching"], "returned", r["returned"])
rows = []
for x in r["results"]:
    print(json.dumps({k: x.get(k) for k in ["experiment_id", "experiment_name", "omics_type", "treatment_type", "table_scope",
                                             "table_scope_detail", "control_timing", "is_time_course", "coculture_partner",
                                             "design_notes", "timepoints", "organism_name"]}, default=str)[:1500])
    rows.append(x)
pd.DataFrame(rows).to_csv(DATA / "med4_n_stress_experiments_raw.csv", index=False, encoding="utf-8")
print(sorted(rows[0].keys()))

for name in ["glnA", "glnB", "ntcA", "pipX", "amt1", "amt", "urtA", "ureC", "cynA", "cynS", "glsF", "nirA", "narB", "focA", "napA"]:
    g = me.resolve_gene(identifier=name, organism="MED4")
    print("resolve", name, g["total_matching"], [(x["locus_tag"], x.get("gene_name"), x.get("product")) for x in g["results"]])
for q in ["nitrogen regulat*", "nitrogen assimilation"]:
    g = me.genes_by_function(search_text=q, organism="MED4", limit=20)
    print("GBF", q, g["total_matching"], [(x["locus_tag"], x.get("gene_name"), x.get("product"), x.get("gene_category")) for x in g["results"]])
s = me.search_ontology(search_text="nitrogen", ontology=["cyanorak_role", "tigr_role"], organism="MED4", limit=10, min_gene_count=1)
for x in s["results"]:
    print("ROLE", x["id"], x["name"], x.get("organism_gene_count"))
