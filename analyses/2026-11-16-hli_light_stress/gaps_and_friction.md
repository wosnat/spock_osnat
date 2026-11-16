# Gaps and friction

- [pitfall] Gene-set counting during Plan step 1 went to `run_cypher` for convenience, although most of it was coverable by tools (`genes_by_function` per organism, `search_homolog_groups` + `genes_by_homolog_group`, `genes_by_ontology`). Counts should be cross-checked with the tools before the seed is frozen. (plan)
- [tool] No tool reports *which field* a text match hit (gene name vs product vs description) — `genes_by_function` searches them together, so "by name" vs "by product" counts need Cypher or post-filtering rows. (plan)
- [tool] `genes_by_ontology` is one organism per call; "which genes in which strains carry InterPro X" across 100 strains needs a loop or Cypher. (plan)
