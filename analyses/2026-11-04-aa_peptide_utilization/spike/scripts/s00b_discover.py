"""Spike discovery 2: term-id formats and row fields.
Run: uv run python analyses/2026-11-04-aa_peptide_utilization/spike/scripts/s00b_discover.py
"""
import multiomics_explorer as me

def show(r, n=2):
    print("  total_matching", r["total_matching"], "returned", r["returned"], "not_found", r.get("not_found"),
          "wrong", r.get("wrong_ontology"), r.get("wrong_level"))
    for x in r["results"][:n]:
        print("   ", x)

for ont, ids in [("ec", ["ec:2.6.1.-"]), ("ec", ["ec:3.4.-.-"]), ("kegg", ["K00605"]), ("kegg", ["kegg.orthology:K01915"]),
                 ("go_mf", ["GO:0008233"]), ("go_mf", ["GO:0015171"]), ("go_mf", ["GO:1904680"]),
                 ("tcdb", ["tcdb:3.A.1.5"]), ("tcdb", ["tcdb:3.A.1.3"]), ("merops", ["merops.clan:MA"])]:
    print(ont, ids)
    try:
        show(me.genes_by_ontology(ontology=ont, organism="MED4", term_ids=ids, min_gene_set_size=0,
                                  max_gene_set_size=100000, limit=3))
    except Exception as e:
        print("  ERR", e)
r = me.gene_neighbors(locus_tags=["PMM1049"], window=3)
show(r, 6)
for q in ["GO:0008233", "GO:0015171", "GO:1904680", "GO:0042887"]:
    r = me.search_ontology(search_text=None, ontology=["go_mf"], limit=1)  # placeholder
r = me.search_ontology(search_text="peptidase activity OR \"amino acid transmembrane transporter\" OR \"peptide transmembrane transporter\"",
                       ontology=["go_mf"], organism="MED4", limit=15, min_gene_count=1)
for x in r["results"]:
    print("GO", x["id"], x["name"], x["level"], x.get("organism_gene_count"))
r = me.resolve_gene(identifier="ntcA", organism="MED4")
print(r)
