# Methods milestone — notebook

## Context

Plan approved 2026-11-04 (commit 4ceb792). This is a **discovery milestone**: it builds the entity set (the pathway catalogue) that every later score inherits.

**Co-define (2026-11-04).** Claude proposed: draft the catalogue → check KOs against KEGG → cross-check for missed enzymes → name the controls → freeze the strain lists → write and test the scoring module → hand-built answer key on two blind strains. The researcher agreed and set the order: **finish the MED4 pilot at pathway level, then MIT9313 and MIT9312** (the answer-key strains, LL and HL).

Order of work:
1. Draft the pathway catalogue (MED4-only queries) → researcher review and approval of the catalogue, flags and controls.
2. Score MED4 at pathway level (not blind; seen in the pilot).
3. MIT9313 and MIT9312: independent MCP-only answer key vs the module, for 5 amino acids (blind until step 1 is approved).
4. Freeze the strain lists (45 Prochlorococcus with clades; marine Synechococcus 5.1–5.3; NCBI assembly level).
