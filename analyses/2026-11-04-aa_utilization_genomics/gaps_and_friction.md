# Gaps and friction

Append-only. Each entry: date · [type] · short name — what happened, workaround, impact.

- 2026-11-04 · [kg-gap] · no KEGG modules — The KG carries KEGG subcategory → pathway → KO, but not KEGG modules. Most amino-acid pathway maps mix biosynthesis and degradation, so a degradation route must be defined as a curated KO step list instead of read from the KG. (plan)
- 2026-11-04 · [kg-gap] · no genome completeness / provenance on organisms — OrganismTaxon has no assembly-level or completeness field, and `reference_database` is null for all 45 Prochlorococcus taxa. Every "gene absent" comparison across genomes needs an external completeness source. (plan, critic)
- 2026-11-04 · [method-gap] · KO existence in KG ≠ KO validity — The KG stores only KO nodes that carry at least one gene, so "KO not in KG" conflates a typo with a real absence. Validate curated KO lists against KEGG itself. (plan, critic)
- 2026-11-04 · [method-gap] · descriptive falsifiability — For a descriptive survey, the first draft labelled plausible biology (uniform capacity across strains) as "method failure." Tie failure to the controls only. (plan, critic)
- 2026-11-04 · [kg-gap] · curated GO "branched-chain amino acid transporter" on urea transporter — MED4 urtC/urtE (PMM0972/PMM0974) carry go:0015658 (curated); their TCDB systems are urea porters in the HAAT subfamily 3.A.1.4. A GO class-level amino-acid call cannot be taken at face value for this family. (plan, MED4 pilot)
- 2026-11-04 · [pitfall] · gene names disagree with KO names — PMM0674 is named aspC but sits on K00812 (aspB); PMM1468 (bioF) sits on K00639 (kbl); PMM0222 is named aspA but its product is aspartoacylase; `resolve_gene("pstA")` also returns PMM0035, a phosphoserine transaminase. Catalogue matching must go by KO and product, never by gene name. (plan, MED4 pilot)
- 2026-11-04 · [kg-gap] · amino-acid uptake evidence is thin in MED4 — 0 TCDB-direct rows for any amino acid; 1 GO MF gene (gltS); 0 SBP predictions. Family-walk candidates are mostly non-transporters. (plan, MED4 pilot)
