# Gaps and friction

Append-only. Each entry: date · [type] · short name — what happened, workaround, impact.

- 2026-11-04 · [kg-gap] · no KEGG modules — The KG carries KEGG subcategory → pathway → KO, but not KEGG modules. Most amino-acid pathway maps mix biosynthesis and degradation, so a degradation route must be defined as a curated KO step list instead of read from the KG. (plan)
- 2026-11-04 · [kg-gap] · no genome completeness / provenance on organisms — OrganismTaxon has no assembly-level or completeness field, and `reference_database` is null for all 45 Prochlorococcus taxa. Every "gene absent" comparison across genomes needs an external completeness source. (plan, critic)
- 2026-11-04 · [method-gap] · KO existence in KG ≠ KO validity — The KG stores only KO nodes that carry at least one gene, so "KO not in KG" conflates a typo with a real absence. Validate curated KO lists against KEGG itself. (plan, critic)
- 2026-11-04 · [method-gap] · descriptive falsifiability — For a descriptive survey, the first draft labelled plausible biology (uniform capacity across strains) as "method failure." Tie failure to the controls only. (plan, critic)
