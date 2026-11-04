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

## Alteromonas HOT1A3 pilot (exploratory, `spike/alteromonas_hot1a3/`, 2026-11-04)

The draft catalogue was scored at pathway level (v5 rule) for HOT1A3 (4,028 genes) and MED4 (1,973). Verified against `aa_status_med4_vs_hot1a3.csv`:

| | complete | partial | absent | can't be judged |
|---|---|---|---|---|
| MED4 | 1 (Asn) | 0 | 16 | 3 |
| HOT1A3 | 8 (Ala, Arg, Asn, Gln, His, Pro, Ser, Thr) | 1 (Trp 2/3) | 8 | 3 |

- Dedicated steps found: MED4 1 / 53, HOT1A3 14 / 53 (34 of the 53 have a KG node).
- Operon calls (±3, same strand): packages = astB ACZ81_08435 (beside a dicarboxylate/amino acid:cation symporter), tdh + kbl ACZ81_00315/00310, kynA ACZ81_05520 (beside TonB receptors). Lone = ald, astA, ansA, iaaA, glsA, hutH, putA, sdaA, kynU, and MED4 PMM0821.
- **Method check restored informally:** the method does find complete dedicated pathways in a heterotroph genome (8 vs 1). [interpretation] Genome size differs ~2×.
- **Catalogue issues exposed (to fix before approval):**
  - product keywords miss synonyms. The glnA control is flagged in HOT1A3 (product "glutamate--ammonia ligase"); phhA "phenylalanine 4-monooxygenase" fails "hydroxylase"; gdhA ACZ81_20180 has product "hypothetical protein".
  - The GOGAT AND group fails because gltD has a generic product.
  - astB, the expected-negative for cyanobacteria, is detected in HOT1A3, so the KO is detectable in the KG (good for the control).

## MIT9313 pilot requested — blindness disclosure (2026-11-04)

The researcher asked for the same pilot on MIT9313 before catalogue approval. **MIT9313 was one of the two blind answer-key strains; it is now unblinded by researcher decision.** Consequence: the verification-layer-2 answer key needs a replacement blind LL strain (candidates: MIT9303, MIT0701, chosen before catalogue approval and not looked at). Any catalogue change made after seeing MIT9313 is logged as "shaped by MIT9313 pilot".

## MIT9313 pilot (exploratory, unblinded, `spike/mit9313/`, 2026-11-04)

Same code and draft catalogue as HOT1A3. Verified against `aa_status_med4_vs_mit9313_vs_hot1a3.csv`:

| | complete | partial | absent | can't be judged | dedicated steps found |
|---|---|---|---|---|---|
| MED4 (HLI, 1,973 genes) | 1 (Asn) | 0 | 16 | 3 | 1 |
| MIT9313 (LLIV, 2,906 genes) | 2 (Ala, Asn) | 0 | 15 | 3 | 3 (one on the excluded GABA shunt) |
| HOT1A3 (4,028 genes) | 8 | 1 | 8 | 3 | 14 |

- MIT9313 adds alanine dehydrogenase (PMT1462, lone gene) to asparaginase (PMT0825, lone). gadA PMT0474 is on the N-neutral, excluded GABA shunt.
- All Prochlorococcus dedicated hits are lone genes.
- Controls: glnA PMT0601, ilvE PMT0728 and hisC PMT2069 are found; astB is absent (as expected).
- Flagged hits are the same patterns as in MED4 (metB/metC on K01758; bioF on K00639). No synonym misses.
- Bookkeeping anomaly to fix before the real run: the per-amino-acid locus-tag list and the "dedicated steps found" count include steps on excluded routes.
