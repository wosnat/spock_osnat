"""Spike discovery: verify signatures, term-id formats and peptide metabolite ids.
Run: uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s00_discover.py
"""
import inspect
import multiomics_explorer as me

for f in ["genes_by_function", "list_metabolites", "genes_by_ontology", "gene_neighbors",
          "gene_ontology_terms", "search_ontology", "genes_by_categorical_metric"]:
    print(f, inspect.signature(getattr(me, f)))

r = me.search_ontology(search_text="peptidase", ontology="ec", organism="MED4", limit=10, min_gene_count=1)
print("EC peptidase", r["total_matching"], [(x["id"], x["name"], x["level"], x.get("organism_gene_count")) for x in r["results"]])
r = me.search_ontology(ontology="ec", organism="MED4", level=1, limit=30, min_gene_count=1)
print("EC level1", [(x["id"], x["name"], x.get("organism_gene_count")) for x in r["results"]])
r = me.search_ontology(ontology="merops", organism="MED4", level=0, limit=30, min_gene_count=1)
print("MEROPS lvl0", [(x["id"], x["name"], x.get("organism_gene_count")) for x in r["results"]])
for q in ["peptide", "dipeptide", "oligopeptide", "tripeptide", "amino acid"]:
    try:
        r = me.list_metabolites(search=q, limit=8)
    except TypeError:
        r = me.list_metabolites(search_text=q, limit=8)
    print("MET", q, r.get("total_matching"), [(x.get("metabolite_id") or x.get("id"), x.get("name")) for x in r["results"]])
r = me.genes_by_function(search_text="amino acid transport OR peptide transport OR oligopeptide OR dipeptide", organism="MED4", limit=50)
print("GBF", r["total_matching"])
for x in r["results"]:
    print("  ", x.get("locus_tag"), x.get("gene_name"), x.get("product"))
print(r["results"][0].keys() if r["results"] else None)
