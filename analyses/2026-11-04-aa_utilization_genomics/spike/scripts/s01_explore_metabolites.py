import json
from multiomics_explorer import list_metabolites, list_organisms
o = list_organisms(organism_names=["MED4"], verbose=False)
print(json.dumps(o["results"][:3], default=str)[:800])
AAS=["alanine","arginine","asparagine","aspartate","cysteine","glutamate","glutamine","glycine","histidine","isoleucine","leucine","lysine","methionine","phenylalanine","proline","serine","threonine","tryptophan","tyrosine","valine","amino acid"]
for a in AAS:
    r = list_metabolites(search_text=a, limit=12)
    print("==",a,"total_matching",r["total_matching"])
    for x in r["results"]:
        print("  ", x.get("metabolite_id"), "|", x.get("name"), "|", x.get("formula"), "|", {k:v for k,v in x.items() if k in ("gene_count","transporter_count","organism_count","structure_kind")})
