import json
from multiomics_explorer import search_ontology, ontology_term_details, genes_by_ontology
r = search_ontology(search_text="glutamine synthetase", ontology="kegg", limit=5)
print(json.dumps(r, default=str)[:1500])
