import json
from multiomics_explorer import list_metabolites, genes_by_metabolite, list_derived_metrics
r = list_metabolites(search_text="amino acid", limit=None)
for x in r["results"]:
    if (x.get("transporter_count") or 0)>0 or (x.get("organism_count") or 0)>0 and x.get("structure_kind")=="generic":
        print("  ", x.get("metabolite_id"), "|", x.get("name"), "|", x.get("transporter_count"), x.get("organism_count"), x.get("structure_kind"))
for q in ["neutral amino","basic amino","acidic amino","hydrophobic amino","arginine","isoleucine","glycine"]:
    r = list_metabolites(search_text=q, limit=None)
    print("==",q,r["total_matching"]); 
    for x in r["results"][:8]: print("  ",x["metabolite_id"],x["name"],x.get("transporter_count"),x.get("structure_kind"))
g = genes_by_metabolite(metabolite_ids=["kegg.compound:C00302"], organism="MED4", evidence_sources=["transport"], include_stereo_forms=True, limit=3, verbose=True)
print({k:v for k,v in g.items() if k!="results"})
for row in g["results"]: print(json.dumps(row, default=str))
g = genes_by_metabolite(metabolite_ids=["kegg.compound:C00302"], organism="MED4", evidence_sources=["transport"], include_stereo_forms=True, include_tcdb_family_substrates=True, limit=3, verbose=True)
print({k:v for k,v in g.items() if k!="results"})
for row in g["results"]: print(json.dumps(row, default=str))
d = list_derived_metrics(search_text="sbp", organism="MED4", verbose=True)
print(json.dumps(d, default=str)[:3000])
