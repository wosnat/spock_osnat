# Methods milestone — notebook

## Co-define (agreed with the researcher, 2026-11-16)

1. Build the gene and experiment list. The 29 MED4 transcript experiments carry: group, table type, time points, the light orientation, and the background light level of each arm (parsed to a number).
2. Toy-test the scoring on hand-computed examples: Fisher p, backgrounds, light flip, flags, Bonferroni within experiment, BH per gene set.
3. Write the KG-based scripts using the API, and test them step by step on photosystem II:
   - check the direction of the extended light and extended darkness contrasts;
   - check one experiment against `pathway_enrichment`;
   - check whether the KG holds per-platform gene lists for backgrounds.
4. Run the comparison sets (chaperones, oxidative stress, photosystem II) and the size-matched random sets across all experiments. Check the flag counts against `proposal.md` Known limits.
5. Produce a report (summary + comparison-set checks), followed by the critic (data-integrity + interpretation) and the researcher's approval.

No hli results are produced or shown in this milestone.
