# Proposal — Amino-acid uptake and degradation capacity across Prochlorococcus genomes

Researcher: Dikla Aharonovich · Drafted 2026-11-04 · Status: **draft, under design review**

## 1. Question

**Which amino-acid transporters and which amino-acid degradation routes does each Prochlorococcus strain carry in its genome, and how does this differ across clades?**

- **What it is for:** a standalone comparative-genomics result (researcher's choice). It does not test or support a specific paper.
- **Whose hypothesis:** none. The researcher has no prior hypothesis; this is a descriptive map. The researcher's own amino-acid growth experiments are explicitly **out of scope** (not in the KG, and set aside by the researcher).
- **Non-goals for now:** gene expression (e.g. whether these genes respond to nitrogen stress); amino-acid biosynthesis; peptide and protein uptake beyond what the transporter evidence names; other cyanobacteria beyond Synechococcus (the comparison group).

## 2. KG entries

All counts from live MCP queries on 2026-11-04, KG release 0.1.0-alpha.9 (see `proposal_notebook.md`).

- **Organisms:** 45 Prochlorococcus genome strains (`list_organisms`), spanning clades HLI (MED4, MIT9515, EQPAC1, RSP50), HLII (19 strains incl. MIT9312, MIT9301, AS9601), HLIII (HNLC2), HLIV (HNLC1), LLI (NATL1A, NATL2A, PAC1, MIT0801), LLII (SS120, SS2, SS35, SS51, SS52, LG, MIT0602, MIT0603), LLIII (MIT9211, MIT0601), LLIV (MIT9313, MIT9303, MIT0701, MIT0702, MIT0703, MIT1327). The full strain → clade table is produced in the methods milestone from `list_organisms`, not typed by hand.
- **Experiments:** none used. No KG experiment grows Prochlorococcus on amino acids (`list_experiments`, search "amino acid…": one hit, a MIT9313 viral-lysate addition, not used).
- **Data types used (all genome annotations):**
  - KEGG orthology (KO) assignments per gene → presence of degradation-route enzymes.
  - TCDB transporter-system calls with curated substrates (`genes_by_metabolite`, `transport` route) → amino-acid transporter evidence.
  - GO transport terms whose definition names an amino acid (`go_transport` route).
  - Predicted substrate-binding-protein substrates (DerivedMetric `sbp_predicted_substrate` / `sbp_nutrient_class`) from Ford et al. 2021 (DOI 10.1042/BST20200244), present for 42 of the 45 strains (absent: MIT1314, MIT1327, RSP50).
- **Comparison group:** all Synechococcus genomes in the KG (same annotation layers). Alteromonas is not used (researcher decision).

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
- **GO matching uses an approved term list, not free text.** The methods milestone lists the GO MF transport terms whose curated transport target is an amino acid. The researcher approves this list (like the route catalogue) before it is used. Free-text matching on definitions is not used.
- **Calls are recorded at the system level.** For each TCDB-direct system, record which subunit roles the strain carries: substrate-binding protein, permease or ATPase, read from the TCDB system and gene annotations. A lone ATPase does not count as a whole system.
- **Direction.** Systems that TCDB marks as export (`tcdb_direction = export`), or that sit in known amino-acid efflux families (e.g. LysE/RhtB, TC 2.A.75 / 2.A.76), are flagged **export** and not counted as uptake capacity.
- Output per strain × amino acid: number of genes per evidence line, subunit roles present, plus a summary call:
  - **specific uptake:** ≥1 non-export system naming that amino acid, via TCDB-direct or the approved GO list;
  - **class-only;**
  - **SBP-only:** only the substrate-binding-protein prediction names it;
  - **export-only;**
  - **none found.**
  - For MIT1314, MIT1327 and RSP50, the SBP line reads **no data**.

**B. Amino-acid degradation routes.** Route-by-route, not whole KEGG maps (most KEGG amino-acid maps mix biosynthesis and degradation; see proposal_notebook).
1. **Route catalogue.** For each of the 20 amino acids, list its known bacterial degradation route(s) as ordered enzyme steps. Each step is one or more KEGG orthology IDs (alternatives = isozymes). Each step carries two flags:
   - **N-releasing:** the step removes the amino nitrogen (as ammonium or by transfer to an acceptor such as 2-oxoglutarate).
   - **Shared:** the enzyme is also used in biosynthesis or central metabolism, so its presence alone is weak evidence for degradation.

   The catalogue is drafted by Claude from standard biochemistry (KEGG reference pathways and modules). It is an `[interpretation]` input. **The researcher reviews and approves the catalogue before it is used.**

   **KO validity is checked against KEGG itself** (KEGG REST `list/ko`), not against the KG. The KG holds only KO nodes that at least one of its genes carries, so "not in the KG" cannot tell a mistyped KO from a valid KO that no organism has. A valid KO missing from the KG stays in the route and scores absent; these are listed separately.
2. **Step presence per strain:** a step is present if ≥1 gene in the strain is annotated to any of its KOs. Gene identity is by locus tag; orthologs across strains are linked by KG ortholog groups for display only.
3. **Route status per strain:** reported as the step fraction **k/n** (steps present / steps in route). The labels are shorthand: **complete** (n/n), **partial** (1 to n−1 of n), **absent** (0/n). Status is reported twice:
   - counting all steps;
   - counting only non-shared steps, i.e. does the strain have the route's *dedicated* enzymes? A route with zero non-shared steps (e.g. one-step transamination routes) gets the status **no dedicated step defined**. It is never vacuously complete.
4. **Per amino acid:** the number of catalogued routes is shown alongside the best route. "Best route" is the route with the highest all-steps fraction, with ties broken by the non-shared fraction. This makes visible that amino acids with more catalogued alternatives have more chances to score.

**Comparison.** Strains × amino-acid tables for A and B, grouped by clade. The main figure is a heatmap (rows = strains ordered by clade; columns = amino acids; panels = transporter call and best degradation-route status). Per-clade counts summarise each column.

**Methods milestone type: discovery.** The method *builds* the entity set (transporter calls and the route catalogue). Plan for many decisions at its decide gate, and the four verification layers:
1. real-serialization fixtures;
2. an independent MCP-only answer key for one strain (MED4) and a few routes;
3. an API-usage review of `genes_by_metabolite` / `genes_by_ontology` / DerivedMetric calls against the explorer docs;
4. a random sample of genes in each call bin (specific, class-only, SBP-only, export, family candidate; complete/partial routes) shown to the researcher.

The route catalogue, the GO term list and the call rules are approved **before** any strain-level results or bin samples are seen. Any rule changed after seeing the samples is recorded in the methods notebook, with its reason and the date.

### Statistics plan
**No formal statistical tests, because the analysis is descriptive and has no hypothesis.** Additionally, strains are not independent samples (they share ancestry within clades), so a test of e.g. high-light vs low-light gene counts would overstate confidence. Results are reported as counts and fractions per strain and per clade, with clade sizes stated (HLIII, HLIV each n = 1; LLIII n = 2; clade-level summaries for these are flagged as single-strain observations).

### Validation set
The method works only if the following come out as expected (each checked in the methods milestone):

The researcher removed Alteromonas from the analysis (2026-11-04). The checks below use only Prochlorococcus itself plus the transporter extraction on a known system. **Trade-off:** without a heterotroph there is no check that the catalogue can detect a *dedicated* degradation route where one surely exists. A dedicated-route absence in Prochlorococcus is therefore reported as "not found with these annotations," with that limit stated.

1. **Matching sanity check (enzymes).** Glutamine synthetase (glnA, K01915) is expected in all 45 Prochlorococcus genomes `[interpretation]`. The step-presence code must find it in all 45. This tests the matching machinery; GS is not a degradation route.
2. **N-transfer positive control.** Prochlorococcus makes all 20 amino acids, so the aminotransferases its biosynthesis requires must be present in every strain `[interpretation]`. They are also N-transfer (shared) enzymes in the catalogue. At catalogue approval, before scoring, name 2–3 such biosynthetic aminotransferase KOs (e.g. branched-chain aminotransferase ilvE, K00826). Each must be found in all 45 strains (or in all complete genomes, if assembly status explains a gap).
3. **Transporter extraction positive control.** The MED4 urea ABC transporter (urtA–E) is documented in the KG as having direct TCDB calls with urea as substrate (docs://analysis/transport). The extraction code, run with urea as the query compound, must return these genes as direct calls. This tests the TCDB extraction machinery on a known system. It is not an amino-acid result.
4. **Synechococcus: comparison group, not a control** (researcher decision, 2026-11-04). It is the closest relative of Prochlorococcus, with the same annotation layers. It is scored with the same method and shown beside Prochlorococcus as a comparison ("how does Prochlorococcus compare with its closest relative?"). It is not used to judge whether the method works: a Synechococcus result similar to Prochlorococcus could be true biology. The Synechococcus strain set is all Synechococcus genomes in the KG; the list is frozen in methods from `list_organisms`.

### Falsifiability check
- **Method failure is judged only by the controls:**
  - glnA (validation 1) or a named biosynthetic aminotransferase (validation 2) is not found in every complete genome;
  - the urea transporter positive control (validation 3) is not returned;
  - an expected-negative below fails.

  If any of these happen, the method is broken and the strain results are not interpreted.
- **These are findings, not failures:** every route having the same status in all 45 strains, or Prochlorococcus carrying only shared steps (no dedicated degradation enzymes). For a streamlined, closely related genus either may be true biology, and both would be reported as results.
- **Pre-registered expected-negatives:**
  - **Non-amino-acid transporters get no amino-acid credit.** The MED4 urea ABC transporter genes (urtA–E) and the phosphate Pst genes (pstS/A/B/C) must receive **no specific-uptake amino-acid call**. urtA's TCDB family (3.A.1.4) contains amino-acid systems, so this partly checks that family-walk rows are kept out of calls (a design rule). Class-only or SBP-only credit on these genes would not count as a failure, but it would be reported and reviewed.
  - **Shared-only routes are not called complete in the dedicated count.** A route whose only present steps are flagged shared must not reach complete status in the non-shared count.
  - **A degradation expected-negative:** at catalogue approval, before any scoring, name one route that is expected *absent* across Prochlorococcus `[interpretation]`. It must score absent in the dedicated count in all 45 strains.
- **A null is a valid outcome.** If most Prochlorococcus strains carry no dedicated degradation route for most amino acids, that is reported as a bounded negative ("no route found with these annotations"), not a non-result. Absence of an annotation ≠ absence of function; this caveat travels with every "absent" call.

### Design comparability
No expression experiments are used, so the comparability concern is whether **annotations are comparable across genomes**.

| Data source | Role | Comparable across strains? | Can confirm | Cannot confirm |
|---|---|---|---|---|
| KEGG KO per gene | degradation-route steps | The KG has no organism-level provenance (`reference_database` is null for all 45). The methods milestone tabulates the gene→KO edge `sources` / `evidence` per strain. If they differ across strains, that is reported; if the field is unusable, pipeline comparability is stated as an assumption. | Enzyme-family presence | Enzyme activity, direction, regulation |
| TCDB direct calls | transporter evidence (1) | Same check | A curated system with that substrate | Actual substrate in this strain; uptake vs export unless TCDB states it |
| GO MF transport terms | transporter evidence (2) | Same check; GO shares homology sources with TCDB | Term-level transport function | Independence from TCDB evidence |
| SBP predicted substrate (Ford et al. 2021) | transporter evidence (3) | 42 of 45 strains; absent for MIT1314, MIT1327, RSP50 (reported as "no data", not "none") | Predicted binding substrate | Transport activity |
| Genome completeness | affects all "absent" calls | The KG has no completeness field. **Source:** NCBI assembly level per strain (looked up by the KG's `ncbi_taxon_id`, outside the KG; recorded as an external input), plus any strains the researcher knows to be incomplete. **Action:** in a non-complete genome, an "absent" call is reported as **absent (assembly incomplete)**. Single-strain clades (HLIII, HLIV) and the smallest genome (RSP50) are named as the cases most exposed. | — | — |
| Synechococcus annotations | comparison group | Same pipeline check; genome sizes differ from Prochlorococcus, so counts are shown alongside genome gene count | Differences in annotated capacity | Whether a shared absence is real biology or an annotation limit |

## 4. Deliverables
- Strain × amino-acid transporter table (per evidence line, plus summary call), with locus tags.
- Approved route catalogue (amino acid → routes → steps → KOs, with N-releasing / shared flags).
- Strain × route status table (all steps / non-shared steps), with the locus tags behind each step.
- Heatmap grouped by clade; per-clade summary; HTML reports per milestone; `paper.md`.
