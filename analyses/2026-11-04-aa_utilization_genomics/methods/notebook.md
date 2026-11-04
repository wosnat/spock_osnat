# Methods milestone — notebook

## Context

Plan approved 2026-11-04 (commit 4ceb792). This is a **discovery milestone**: it builds the entity set (the pathway catalogue) that every later score inherits.

**Co-define (2026-11-04).** Claude proposed: draft the catalogue → check KOs against KEGG → cross-check for missed enzymes → name the controls → freeze the strain lists → write and test the scoring module → hand-built answer key on two blind strains. The researcher agreed and set the order: **finish the MED4 pilot at pathway level, then MIT9313 and MIT9312** (the answer-key strains, LL and HL).

Order of work:
1. Draft the pathway catalogue (MED4-only queries) → researcher review and approval of the catalogue, flags and controls.
2. Score MED4 at pathway level (not blind; seen in the pilot).
3. MIT9313 and MIT9312: independent MCP-only answer key vs the module, for 5 amino acids (blind until step 1 is approved).
4. Freeze the strain lists (45 Prochlorococcus with clades; marine Synechococcus 5.1–5.3; NCBI assembly level).

## Exploration during catalogue review (2026-11-04)

- The researcher stepped back to ask how amino-acid utilization works in other bacteria (E. coli etc.). Claude gave general background, tagged [interpretation]: heterotrophs typically carry specific transporters, dedicated breakdown operons (put, tna, sda, ast, hut) and Ntr-regulated induction.
- **MED4 neighbourhood check** (`gene_neighbors`, window 5):
  - asparaginase PMM0821, MED4's only credited dedicated hit, has no transporter or pathway step nearby (neighbours: hypotheticals, PMM0822 an uncharacterized membrane protein, rsfS, carB) → lone gene.
  - By contrast, urease ureC/B/A (PMM0963–0965) sits with ureD–G (PMM0966–0969) and urtA (PMM0970) → an uptake + breakdown package for urea.
- **Researcher request: run the same pilot on Alteromonas macleodii HOT1A3** (exploratory; Alteromonas is not in the approved analysis). It uses the current draft catalogue; it computes pathway-level status for HOT1A3 and MED4 and an operon/neighbourhood call for each credited dedicated hit. Prochlorococcus strains other than MED4 stay blind.
