import json
from multiomics_explorer import genes_by_ontology
for lv in range(0,6):
    try:
        t = genes_by_ontology(ontology="tcdb", organism="MED4", level=lv, min_gene_set_size=0, max_gene_set_size=None, limit=None)
    except Exception as e:
        print(lv, "ERR", e); continue
    print("LEVEL", lv, t["total_matching"], [k for k in t.keys()])
    if lv in (2,4,5):
        for x in t["results"]: print(json.dumps(x, default=str))
