# Proposal — Amino-acid uptake and degradation capacity across Prochlorococcus genomes

Researcher: Dikla Aharonovich · Drafted 2026-11-04 · Status: **draft, under design review**

## 1. Question

**Which amino-acid transporters and which amino-acid degradation routes does each Prochlorococcus strain carry in its genome, and how does this differ across clades?**

- **What it is for:** a standalone comparative-genomics result (researcher's choice). It does not test or support a specific paper.
- **Whose hypothesis:** none. The researcher has no prior hypothesis; this is a descriptive map. The researcher's own amino-acid growth experiments are explicitly **out of scope** (not in the KG, and set aside by the researcher).
- **Non-goals for now:** gene expression (e.g. whether these genes respond to nitrogen stress); amino-acid biosynthesis; peptide and protein uptake beyond what the transporter evidence names; Synechococcus and other cyanobacteria (except as noted under validation).

## 2. KG entries

All counts from live MCP queries on 2026-11-04, KG release 0.1.0-alpha.9 (see `proposal_notebook.md`).

- **Organisms:** 45 Prochlorococcus genome strains (`list_organisms`), spanning clades HLI (MED4, MIT9515, EQPAC1, RSP50), HLII (19 strains incl. MIT9312, MIT9301, AS9601), HLIII (HNLC2), HLIV (HNLC1), LLI (NATL1A, NATL2A, PAC1, MIT0801), LLII (SS120, SS2, SS35, SS51, SS52, LG, MIT0602, MIT0603), LLIII (MIT9211, MIT0601), LLIV (MIT9313, MIT9303, MIT0701, MIT0702, MIT0703, MIT1327). The full strain → clade table is produced in the methods milestone from `list_organisms`, not typed by hand.
- **Experiments:** none used. No KG experiment grows Prochlorococcus on amino acids (`list_experiments`, search "amino acid…": one hit, a MIT9313 viral-lysate addition, not used).
- **Data types used (all genome annotations):**
  - KEGG orthology (KO) assignments per gene → presence of degradation-route enzymes.
  - TCDB transporter-system calls with curated substrates (`genes_by_metabolite`, `transport` route) → amino-acid transporter evidence.
  - GO transport terms whose definition names an amino acid (`go_transport` route).
  - Predicted substrate-binding-protein substrates (DerivedMetric `sbp_predicted_substrate` / `sbp_nutrient_class`) from Ford et al. 2021 (DOI 10.1042/BST20200244), present for 42 of the 45 strains (absent: MIT1314, MIT1327, RSP50).
- **Comparator organisms for validation:** Alteromonas macleodii MIT1002, EZ55, HOT1A3 (heterotrophs, same annotation layers in the KG).

## 3. Framing

### Hypothesis
None. The analysis is descriptive: it produces a per-strain inventory and reports how it is distributed across clades. Patterns that emerge (e.g. differences between high-light and low-light clades) are reported as observations, not tested claims.

### Approach

Two inventories, built per strain, then compared.

**A. Amino-acid transporters.** For each strain and each of the 20 standard amino acids, collect the genes the KG links to transport of that amino acid, keeping three evidence lines separate:
1. **TCDB direct:** gene has a direct TCDB system call whose curated substrate is that amino acid (generic and L/D forms merged via `include_stereo_forms`).
2. **GO transport:** gene carries a molecular-function GO transport term whose definition names that amino acid (MF rows only, so storage/regulatory BP genes don't count).
3. **SBP prediction:** gene's predicted substrate-binding-protein substrate (Ford et al. 2021) names that amino acid or an amino-acid class.

Rules:
- Calls naming only a **class** ("amino acid", "polar amino acid", "branched-chain amino acid") are reported as a separate "class-level" column, not credited to individual amino acids. A class that unambiguously names a defined set (e.g. branched-chain = Leu/Ile/Val) is credited to that set but marked as class-derived.
- **TCDB family-walk rows** (`include_tcdb_family_substrates`) are excluded from calls. They are counted and reported as "candidates" only, because they say the family moves the compound somewhere, not that this gene does (docs://analysis/transport).
- Agreement between TCDB and GO is reported as one line of homology evidence, not two independent confirmations.
- Output per strain × amino acid: number of genes per evidence line, plus a summary call: **specific** (≥1 gene with TCDB-direct or GO-MF naming that amino acid), **class-only**, or **none found**.

**B. Amino-acid degradation routes.** Route-by-route, not whole KEGG maps (most KEGG amino-acid maps mix biosynthesis and degradation; see proposal_notebook).
1. **Route catalogue.** For each of the 20 amino acids, list its known bacterial degradation route(s) as ordered enzyme steps. Each step is one or more KEGG orthology IDs (alternatives = isozymes). Each step carries two flags:
   - **N-releasing:** the step removes the amino nitrogen (as ammonium or by transfer to an acceptor such as 2-oxoglutarate).
   - **Shared:** the enzyme is also used in biosynthesis or central metabolism, so its presence alone is weak evidence for degradation.

   The catalogue is drafted by Claude from standard biochemistry (KEGG reference pathways and modules). It is an `[interpretation]` input. Every KO is checked to exist in the KG, and **the researcher reviews and approves the catalogue before it is used**.
2. **Step presence per strain:** a step is present if ≥1 gene in the strain is annotated to any of its KOs. Gene identity is by locus tag; orthologs across strains are linked by KG ortholog groups for display only.
3. **Route status per strain:** **complete** (all steps present), **partial** (some), **absent** (none). Status is reported twice: counting all steps, and counting only non-shared steps (does the strain have the route's *dedicated* enzymes?).

**Comparison.** Strains × amino-acid tables for A and B, grouped by clade. The main figure is a heatmap (rows = strains ordered by clade; columns = amino acids; panels = transporter call and best degradation-route status). Per-clade counts summarise each column.

**Methods milestone type: discovery.** The method *builds* the entity set (transporter calls and the route catalogue). Plan for many decisions at its decide gate, and the four verification layers:
1. real-serialization fixtures;
2. an independent MCP-only answer key for one strain (MED4) and a few routes;
3. an API-usage review of `genes_by_metabolite` / `genes_by_ontology` / DerivedMetric calls against the explorer docs;
4. a random sample of genes in each call bin (specific, class-only, family candidate; complete/partial routes) shown to the researcher before the rules are approved.

### Statistics plan
**No formal statistical tests, because the analysis is descriptive and has no hypothesis.** Additionally, strains are not independent samples (they share ancestry within clades), so a test of e.g. high-light vs low-light gene counts would overstate confidence. Results are reported as counts and fractions per strain and per clade, with clade sizes stated (HLIII, HLIV each n = 1; LLIII n = 2; clade-level summaries for these are flagged as single-strain observations).

### Validation set
The method works only if the following come out as expected (each checked in the methods milestone):

1. **Alteromonas positive control (degradation).** The three Alteromonas strains, heterotrophs that grow on amino acids `[interpretation]`, are scored with the same catalogue. Expected: complete routes for clearly more amino acids than any Prochlorococcus strain. If Alteromonas scores no better than Prochlorococcus, the catalogue or the matching is broken.
2. **Matching sanity check.** Glutamine synthetase (glnA) is expected in all 45 Prochlorococcus genomes `[interpretation]`. The step-presence code must find it in all 45. This check tests the matching machinery; GS is not a degradation route.
3. **Transporter positive control.** Alteromonas strains are expected to show specific TCDB-direct amino-acid transporter calls for several amino acids `[interpretation]`. If none are found, the transporter extraction is broken.

### Falsifiability check
- **"Nothing real" looks like:** every degradation route has the same status in all 45 strains *and* Alteromonas looks like Prochlorococcus. Or every "complete" call depends on shared steps only (the non-shared-steps status is absent everywhere). Either means the method is detecting housekeeping enzymes, not degradation capacity.
- **Pre-registered expected-negatives:**
  - **Non-amino-acid transporters get no amino-acid credit.** The MED4 urea ABC transporter genes (urtA–E) and the phosphate Pst genes (pstS/A/B/C) must receive **no specific amino-acid call**. urtA's TCDB family (3.A.1.4) contains amino-acid systems, so this checks that family-walk rows are kept out of calls.
  - **Shared-only routes are not called "complete (dedicated)."** A route whose only present steps are flagged shared must not reach complete status in the non-shared count.
- **A null is a valid outcome.** If most Prochlorococcus strains carry no dedicated degradation route for most amino acids, that is reported as a bounded negative ("no route found with these annotations"), not a non-result. Absence of an annotation ≠ absence of function; this caveat travels with every "absent" call.

### Design comparability
No expression experiments are used, so the comparability concern is whether **annotations are comparable across genomes**.

| Data source | Role | Comparable across strains? | Can confirm | Cannot confirm |
|---|---|---|---|---|
| KEGG KO per gene | degradation-route steps | To check in methods: whether all 45 genomes went through the same annotation pipeline (KG `sources` / `evidence` fields). | Enzyme-family presence | Enzyme activity, direction, regulation |
| TCDB direct calls | transporter evidence (1) | Same check | A curated system with that substrate | Actual substrate in this strain; uptake vs export unless TCDB states it |
| GO MF transport terms | transporter evidence (2) | Same check; GO shares homology sources with TCDB | Term-level transport function | Independence from TCDB evidence |
| SBP predicted substrate (Ford et al. 2021) | transporter evidence (3) | 42 of 45 strains; absent for MIT1314, MIT1327, RSP50 (reported as "no data", not "none") | Predicted binding substrate | Transport activity |
| Genome completeness | affects all "absent" calls | **Ask researcher / check:** some genomes may be draft or incomplete assemblies, which would inflate absences | — | — |
| Alteromonas annotations | validation only | Same pipeline check | Method sanity | Anything about Prochlorococcus |

## 4. Deliverables
- Strain × amino-acid transporter table (per evidence line, plus summary call), with locus tags.
- Approved route catalogue (amino acid → routes → steps → KOs, with N-releasing / shared flags).
- Strain × route status table (all steps / non-shared steps), with the locus tags behind each step.
- Heatmap grouped by clade; per-clade summary; HTML reports per milestone; `paper.md`.
