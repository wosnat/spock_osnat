# Proposal — Genomic capacity to release nitrogen from amino acids across Prochlorococcus

Researcher: Dikla Aharonovich · Drafted 2026-11-04 · Status: **draft, under design review**

> **Change log (Plan phase).**
> - v1 covered amino-acid transporters and full degradation routes.
> - Design review then narrowed it:
>   - focus on amino acids as a **nitrogen source**;
>   - Synechococcus added as a comparison group;
>   - Alteromonas removed;
>   - after the MED4 pilot, **transporters set aside** (deferred, not in this analysis).
>
> Earlier versions are in git history; the reasons are in `proposal_notebook.md`.

## 1. Question

**Which Prochlorococcus strains carry the enzymes that remove the nitrogen from each of the 20 standard amino acids, either releasing it as ammonium or transferring it to 2-oxoglutarate to make glutamate? How does this capacity differ across clades, and compared with Synechococcus?**

- **What it is for:** a standalone comparative-genomics result (researcher's choice).
- **Whose hypothesis:** none. A descriptive map. The researcher's own amino-acid growth experiments are out of scope (not in the KG, set aside by the researcher).
- **Non-goals:**
  - **Amino-acid uptake (transporters):** deferred by the researcher after the MED4 pilot.
  - Gene expression.
  - Amino-acid biosynthesis as a topic.
  - Peptide/protein degradation (peptidases).
  - Organisms other than Prochlorococcus and Synechococcus.

## 2. KG entries

Counts from live MCP queries on 2026-11-04, KG release 0.1.0-alpha.9 (see `proposal_notebook.md`).

- **Organisms:** 45 Prochlorococcus genome strains, clades:
  - HLI 4 · HLII 19 · HLIII 1 · HLIV 1
  - LLI 4 · LLII 8 · LLIII 2 · LLIV 6

  The strain → clade table is frozen in methods from `list_organisms`.
- **Comparison group:** all Synechococcus genomes in the KG. Same annotation layers; the list is frozen in methods from `list_organisms`.
- **Experiments:** none used. No KG experiment grows Prochlorococcus on amino acids.
- **Data used (genome annotations only):**
  - KEGG orthology (KO) assignments per gene (`genes_by_ontology`, ontology `kegg`).
  - The KG's KEGG reaction layer (`genes_by_metabolite`, evidence `metabolism`), as a cross-check for N-removing enzymes the catalogue missed.

## 3. Framing

### Hypothesis
None. The analysis is descriptive. Patterns across clades or between genera are reported as observations, not tested claims.

### Approach

**1. N-release catalogue.** For each of the 20 amino acids, list the enzymes that remove its amino (or amide) nitrogen. Each entry carries:
- **KO id(s)** and EC number. Alternatives such as isozymes are listed as separate KOs for the same step.
- **Mode:**
  - **NH4+ release:** deaminases, ammonia-lyases, amino-acid dehydrogenases and oxidases, amidases such as glutaminase/asparaginase, urease where the route goes through urea.
  - **Transfer:** aminotransferases that pass the amino group to 2-oxoglutarate, giving glutamate.
- **Shared flag:** the enzyme is also required for biosynthesis or central metabolism. Examples: ilvE, which builds branched-chain amino acids; hisC; the glycine-cleavage system. A shared hit is weaker evidence that the strain *uses* the amino acid as an N source. Dedicated catabolic enzymes are the stronger signal. Examples: glutamate dehydrogenase, alanine dehydrogenase, proline dehydrogenase, arginase, the hut enzymes.
- **Multi-step N routes:** where nitrogen is released only after earlier steps (e.g. Arg → agmatine → putrescine + urea → NH4+), list the steps and score the route as **k/n steps present**. The N-releasing step is marked.
- **Source:** drafted by Claude from standard biochemistry (KEGG reference pathways/modules). It is an `[interpretation]` input. The MED4 pilot draft (`spike/data/med4_n_release_catalogue.csv`, 75 KOs) is the starting point.
- **KO validity** is checked against KEGG REST (`list/ko`), not the KG: the KG only holds KOs that some gene carries. A valid KO with no gene in the KG stays in the catalogue and scores absent.
- **The researcher approves the catalogue before any strain beyond MED4 is scored.** At that same review, the controls named below are fixed.

**2. Presence per strain.**
- A catalogue entry is **present** if ≥1 gene in the strain is annotated to any of its KOs.
- Matching is by KO only, **never by gene name**: the pilot found gene names that disagree with their KO and product (see `gaps_and_friction.md`).
- Locus tags are kept for every hit. Orthologs across strains are linked by KG ortholog groups, for display only.

**3. Per strain × amino acid call:**
- **dedicated N release:** ≥1 non-shared N-releasing entry present.
- **shared only:** only shared entries present.
- **none found.**

The mode (NH4+ vs transfer) is shown alongside. Multi-step routes contribute only if their N-releasing step is present; the k/n route context is shown.

**4. Cross-check for gaps in the catalogue.**
- For each strain, list genes the KG's reaction layer links to an N-removing reaction on that amino acid that are not in the catalogue. These are candidates for the researcher to add or reject.
- Reaction direction is checked by hand for each candidate. The pilot showed that an EC-prefix filter also catches reactions where the amino acid is a *product* (e.g. carbamoyl-phosphate synthase for Glu).
- This list is reviewed with the catalogue, before scoring.

**5. Comparison.**
- A strain × amino-acid table and heatmap, rows grouped by clade, with Synechococcus as a separate block. Cell = dedicated / shared only / none found.
- Per-clade counts.
- Genome size (gene count) is shown beside each strain, because larger genomes may carry more enzymes simply by size.

**Methods milestone type: discovery.** The catalogue *is* the entity set. Verification layers:
1. real-serialization fixtures;
2. an independent MCP-only answer key for MED4 and two other strains (one HL, one LL), for 5 amino acids, built without the module;
3. API-usage review of `genes_by_ontology` / `genes_by_metabolite` against the explorer docs;
4. a random sample of hits in each call bin, shown to the researcher.

Catalogue and rules are approved before any non-MED4 results are seen; later changes are logged with reason and date.

### Statistics plan
**No formal tests.** The analysis is descriptive with no hypothesis, and strains are not independent (shared ancestry). Results are counts and fractions per strain, per clade and per genus, with clade sizes stated; HLIII, HLIV and LLIII summaries are flagged as one- or two-strain observations.

### Validation set
Alteromonas was removed by the researcher, so all checks are within Prochlorococcus.

**Trade-off:** no check shows the method can detect a *dedicated* N-releasing enzyme where one surely exists. "None found" for dedicated enzymes is therefore reported as "not found with these annotations."

1. **Matching sanity:** glutamine synthetase (glnA, K01915) is found in all 45 strains `[interpretation: universal in cyanobacteria]`. The pilot found it in MED4 (PMM0920).
2. **N-transfer positive control:** Prochlorococcus makes all 20 amino acids, so the aminotransferases its biosynthesis needs must be present in every strain `[interpretation]`.
   - At catalogue approval, name 2–3 such KOs, e.g. branched-chain aminotransferase ilvE (K00826) and histidinol-phosphate aminotransferase hisC (K00817).
   - Each must be found in every strain with a complete genome.
3. **Synechococcus is a comparison group, not a control** (researcher decision). A Synechococcus result similar to Prochlorococcus could be true biology.

### Falsifiability check
- **Method failure is judged only by the controls.** If a control fails, the strain results are not interpreted:
  - glnA or a named biosynthetic aminotransferase is missing from any complete genome;
  - an expected-negative fails.
- **Findings, not failures:**
  - every strain has the same calls;
  - Prochlorococcus carries only shared enzymes;
  - most amino acids have none found.

  Each is reported as a result. A null is a valid, bounded outcome.
- **Pre-registered expected-negatives:**
  - **Shared-only is never called dedicated.** A strain whose only hits for an amino acid are shared entries must be called "shared only."
  - **One dedicated catabolic enzyme expected absent:** at catalogue approval, before scoring, name one dedicated N-releasing enzyme expected absent across Prochlorococcus `[interpretation]`. It must be absent in all 45 strains. MED4 has already been seen, so the choice must be justified independently of the MED4 pilot.

### Design comparability
No experiments are used; the concern is whether **annotations are comparable across genomes**.

| Data source | Role | Comparable across strains? | Can confirm | Cannot confirm |
|---|---|---|---|---|
| KEGG KO per gene | N-release presence | The KG has no organism-level provenance (`reference_database` null for all 45). Methods tabulates the gene→KO edge `sources` / `evidence` per strain; any difference is reported, else comparability is stated as an assumption. | Enzyme-family presence | Activity, substrate range, direction, regulation |
| KEGG reaction layer | catalogue cross-check only | Same | Candidate enzymes the catalogue missed | Reaction direction (checked by hand) |
| Genome completeness | affects every "none found" | No KG field. **Source:** NCBI assembly level by `ncbi_taxon_id` (external input), plus researcher knowledge. **Action:** "none found" in a non-complete genome is reported as **none found (assembly incomplete)**. | — | — |
| Synechococcus annotations | comparison group | Same pipeline check; larger genomes, so gene count is shown | Differences in annotated capacity | Whether a shared absence is biology or annotation |

### Interpretation limits (stated up front)
- **Enzyme ≠ external N source.** These enzymes also act on amino acids made inside the cell, or freed by protein turnover. With transporters deferred, a strain that "can release N from amino acid X" cannot be said to *use external X as an N source*.
- **Annotation ≠ function.** KO presence shows an enzyme family, not activity or substrate specificity. Broad-specificity aminotransferases may act on several amino acids.

## 4. Deliverables
- An approved N-release catalogue (amino acid → enzymes/routes → KOs, with mode and shared flags).
- A strain × amino-acid call table with locus tags behind every call, for 45 Prochlorococcus strains + Synechococcus.
- A heatmap by clade, per-clade summary, HTML reports, and `paper.md`.
