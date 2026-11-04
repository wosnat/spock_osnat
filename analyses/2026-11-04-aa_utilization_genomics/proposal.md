# Proposal — Genomic capacity to release nitrogen from amino acids across Prochlorococcus

Researcher: Dikla Aharonovich · Drafted 2026-11-04 · Status: **draft, under design review**

> **Change log (Plan phase).**
> - v1 covered amino-acid transporters and full degradation routes.
> - Design review then narrowed it:
>   - focus on removing nitrogen from amino acids (motivated by amino acids as a nitrogen source; see the interpretation limits);
>   - Synechococcus added as a comparison group;
>   - Alteromonas removed;
>   - after the MED4 pilot, **transporters set aside** (deferred, not in this analysis).
>
> Earlier versions are in git history; the reasons are in `proposal_notebook.md`.

## 1. Question

**Which Prochlorococcus strains carry the enzymes that remove the nitrogen from the carbon skeleton of each of the 20 standard (L-) amino acids, so that it ends up as ammonium, or as the amino group of glutamate or another amino acid by transamination? How does this capacity differ across clades, and compared with marine Synechococcus?**

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
- **Comparison group: marine Synechococcus.** `list_organisms(["Synechococcus"])` returns 54 genome strains. The match also catches freshwater *S. elongatus* PCC 7942 and UTEX 2973, *Picosynechococcus* PCC 7002 and *Thermosynechococcus* BP-1. **Inclusion rule (recommended, pending researcher):** marine picocyanobacteria only, i.e. Synechococcus/Parasynechococcus subclusters 5.1–5.3. Freshwater, thermophilic and other-genus strains are excluded. The included list and its count are frozen in methods from `list_organisms`, using its clade/taxonomy fields.
- **Experiments:** none used. No KG experiment grows Prochlorococcus on amino acids.
- **Data used (genome annotations only):**
  - KEGG orthology (KO) assignments per gene (`genes_by_ontology`, ontology `kegg`).
  - The KG's KEGG reaction layer (`genes_by_metabolite`, evidence `metabolism`), as a cross-check for N-removing enzymes the catalogue missed.

## 3. Framing

### Hypothesis
None. The analysis is descriptive. Patterns across clades or between genera are reported as observations, not tested claims.

### Approach

**1. N-release catalogue.** For each of the 20 amino acids, list the enzymes that free its amino (or amide) nitrogen from the carbon skeleton. Each entry carries:
- **KO id(s)** and EC number. Alternatives that do the same step (isozymes, paralog KOs) are grouped as **one step**: the step is present if any of its KOs is present.
- **Mode** (what happens to the nitrogen):
  - **NH4+ release:** deaminases, ammonia-lyases, amino-acid dehydrogenases and oxidases, amidases (glutaminase, asparaginase).
  - **Transfer:** aminotransferases. The **acceptor is recorded**: 2-oxoglutarate gives glutamate; pyruvate gives alanine; glyoxylate gives glycine.
  - **Conversion to glutamate:** the skeleton itself becomes glutamate (e.g. Pro → P5C → Glu via proline dehydrogenase / PutA; His → Glu via the hut route). The N then sits in glutamate, the cell's main N donor.
  - **N kept in another amino acid (context only):** e.g. Thr → Gly (ltaE/tdh+kbl), decarboxylases (gadB, cadA), argF, speA, cysK. These do **not** free N from the skeleton, so they never make a call by themselves; they are shown as route context.
- **Shared flag:** the enzyme is also required for biosynthesis or central metabolism, or for using another N source. Examples: ilvE and hisC (biosynthesis); the glycine-cleavage system; **urease** (urea use). A shared hit is weaker evidence of a catabolic, N-releasing role. A short reason for each shared/not-shared flag is written in the catalogue. Enzymes whose flag is genuinely debatable are listed for the researcher to decide at catalogue approval (see "Open choices" below).
- **Multi-step routes:** the steps are listed and scored **k/n present**. The **N-releasing step of a route is the first step that frees N from the amino-acid backbone** (NH4+ release, transfer, or conversion to glutamate). Later N-releasing steps (e.g. hutG after hutH; urease after arginase or agmatinase) are context. A step whose product is urea (arginase, agmatinase speB) is mode "release as urea"; it counts as freeing N from the backbone.
- **Broad-specificity and "ALL" entries** (e.g. D-amino-acid dehydrogenase K00273; aminotransferases of broad or unknown substrate range) are reported in **their own column** and **never contribute to a per-amino-acid call**. D-amino-acid enzymes are outside the question (the 20 L-amino acids) and are shown only in that column.
- **Source:** drafted by Claude from standard biochemistry (KEGG reference pathways/modules). It is an `[interpretation]` input. The MED4 pilot draft (`spike/data/med4_n_release_catalogue.csv`, 75 KOs) is the starting point and will be revised to these rules.
- **KO validity** is checked against KEGG REST (`list/ko`), not the KG: the KG only holds KOs that some gene carries. A valid KO with no gene in the KG stays in the catalogue and scores absent.
- **The researcher approves the catalogue before any strain beyond MED4 is scored.** At that same review, the controls named below are fixed.

**2. Presence per strain.**
- A step is **present** if ≥1 gene in the strain is annotated to any of its KOs.
- Matching is by KO, **never by gene name**: the pilot found gene names that disagree with their KO and product (see `gaps_and_friction.md`).
- **KO/product disagreements are flagged, not silently trusted.** Example: MED4 PMM1468 sits on K00639 (kbl) but its product is "8-amino-7-oxononanoate synthase" (biotin synthesis). Every hit whose product does not match the KO's enzyme is flagged in the call table for researcher review, and a flagged hit does not make a call until reviewed.
- Locus tags are kept for every hit. Orthologs across strains are linked by KG ortholog groups, for display only.

**3. Per strain × amino acid call** (from N-releasing steps only, as defined above):
- **dedicated:** ≥1 non-shared N-releasing step present.
- **shared only:** only shared N-releasing steps present.
- **none found.**

The mode (NH4+ / transfer + acceptor / conversion to glutamate / via urea) is shown alongside, with the k/n route context. Example of the rule in use: in MED4, arginine's N-releasing step via agmatinase (speB, release as urea) is present, but speB is shared (polyamine synthesis), so Arg would be "shared only." Urease is a later step and shared (urea use), so it cannot make Arg "dedicated." The wording for such a cell is "N freed only via shared enzymes."

**4. Cross-check for gaps in the catalogue.**
- For each strain, list genes the KG's reaction layer links to an N-removing reaction on that amino acid that are not in the catalogue. These are candidates for the researcher to add or reject.
- Reaction direction is checked by hand for each candidate. The pilot showed that an EC-prefix filter also catches reactions where the amino acid is a *product* (e.g. carbamoyl-phosphate synthase for Glu).
- This list is reviewed with the catalogue, before scoring.

**5. Comparison.**
- A strain × amino-acid table and heatmap, rows grouped by clade, with marine Synechococcus as a separate block. Cell = dedicated / shared only / none found.
- Per-clade counts.
- Genome size (gene count) is shown beside each strain, because larger genomes may carry more enzymes simply by size.
- **Wording rule for genus differences:** "annotated in X of N marine Synechococcus vs Y of 45 Prochlorococcus." Never "Prochlorococcus lost …" or other evolutionary claims; this design cannot tell loss from gain.

**Methods milestone type: discovery.** The catalogue *is* the entity set. Verification layers:
1. real-serialization fixtures. These include the code invariants: "shared-only is never called dedicated"; "broad/ALL entries never make a call"; "context-only steps never make a call."
2. an independent MCP-only answer key for 5 amino acids in three strains, built without the module. MED4 is **not blind** (seen in the pilot); the two other strains (one HL, one LL, not MED4) are blind and carry the weight.
3. API-usage review of `genes_by_ontology` / `genes_by_metabolite` against the explorer docs;
4. a random sample of hits in each call bin, shown to the researcher.

Catalogue and rules are approved before any non-MED4 results are seen; later changes are logged with reason and date.

### Statistics plan
**No formal tests.** The analysis is descriptive with no hypothesis, and strains are not independent (shared ancestry). Results are counts and fractions per strain, per clade and per genus, with clade sizes stated; HLIII, HLIV and LLIII summaries are flagged as one- or two-strain observations.

### Validation set
Alteromonas was removed by the researcher, so all checks are within Prochlorococcus.

**Trade-off:** no check shows the method can detect a *dedicated* N-releasing enzyme where one surely exists. "None found" for dedicated enzymes is therefore reported as "not found with these annotations." These controls share the target's annotation pipeline: they test KO matching, not biology.

A "complete genome" below means NCBI assembly level "Complete Genome" (see the comparability table).

1. **Matching sanity:** glutamine synthetase (glnA, K01915) is found in every complete Prochlorococcus genome `[interpretation: universal in cyanobacteria]`. MED4 was seen in the pilot (PMM0920).
2. **N-transfer positive control (step level):** Prochlorococcus makes all 20 amino acids, so the transamination steps its biosynthesis needs must be present in every strain `[interpretation]`. At catalogue approval, name 2–3 such **steps**, each with all KOs that can carry it (paralog KOs included). Examples: the branched-chain aminotransferase step (ilvE K00826 and alternatives); the histidinol-phosphate aminotransferase step (hisC K00817 and alternatives). MED4 was seen for both, so they are not blind for MED4.
3. **Synechococcus is a comparison group, not a control** (researcher decision). A Synechococcus result similar to Prochlorococcus could be true biology.

### Falsifiability check
- **Method failure is judged only by the positive controls**, with an inspection step before any halt:
  - If glnA or a named control step is missing from a complete genome, inspect that strain first. Look for a sibling KO, a fragmented gene, or a KO assigned to the product under another ID.
  - If an annotation quirk explains it, record it and continue.
  - If it is missing without explanation in **more than 10% of complete genomes**, the matching is broken and strain results are not interpreted.
- **Findings, not failures:**
  - every strain has the same calls;
  - Prochlorococcus carries only shared enzymes;
  - most amino acids have none found;
  - a dedicated catabolic enzyme found in some strains (e.g. larger LL genomes).

  Each is reported as a result. A null is a valid, bounded outcome.
- **Pre-registered expected-negative (flag and inspect, not halt):**
  - At catalogue approval, before scoring, name one enzyme that should be absent from **cyanobacteria in general** `[interpretation]`, so that a hit would more likely mean a KO-matching artefact than biology.
  - A hit in any strain is **inspected and reported**: its locus tag, its product, and whether the KO assignment holds up. It does not halt the analysis.
  - Disclosure: the MED4 pilot already showed which dedicated enzymes MED4 lacks (`proposal_notebook.md`), so any MED4-based candidate is not blind.

### Open choices for the researcher (to settle before the plan is locked)
1. **Glutamate dehydrogenase (GDH): shared or dedicated?** It can deaminate glutamate (releasing NH4+), but in many bacteria it also assimilates NH4+ into glutamate. The pilot catalogue marked it shared; v2's text called it dedicated. The choice decides whether glutamate can ever be called "dedicated."
2. **Synechococcus inclusion rule:** marine subclusters 5.1–5.3 only (recommended), or all 54 KG "Synechococcus" genomes.
3. **Urease as shared** (recommended: it serves urea use, not specifically amino-acid catabolism).

### Design comparability
No experiments are used; the concern is whether **annotations are comparable across genomes**.

| Data source | Role | Comparable across strains? | Can confirm | Cannot confirm |
|---|---|---|---|---|
| KEGG KO per gene | N-release presence | The KG has no organism-level provenance (`reference_database` null for all 45). Methods tabulates the gene→KO edge `sources` / `evidence` per strain; any difference is reported, else comparability is stated as an assumption. | Enzyme-family presence | Activity, substrate range, direction, regulation |
| KEGG reaction layer | catalogue cross-check only | Same | Candidate enzymes the catalogue missed | Reaction direction (checked by hand) |
| Genome completeness | affects every "none found" | No KG field. **Source:** NCBI assembly level by `ncbi_taxon_id` (external input), plus researcher knowledge. **Action:** "none found" in a non-complete genome is reported as **none found (assembly incomplete)**. | — | — |
| Marine Synechococcus annotations | comparison group | Same pipeline check. Genome sizes overlap with Prochlorococcus (Synechococcus mostly 2,463–4,456 genes; Prochlorococcus 1,870–3,203), so gene count is shown | Differences in annotated capacity ("X of N vs Y of 45") | Loss vs gain; whether a shared absence is biology or annotation |

### Interpretation limits (stated up front)
- **Enzyme ≠ external N source.** These enzymes also act on amino acids made inside the cell, or freed by protein turnover. With transporters deferred, a strain that "can release N from amino acid X" cannot be said to *use external X as an N source*.
- **Annotation ≠ function.** KO presence shows an enzyme family, not activity or substrate specificity. Broad-specificity aminotransferases may act on several amino acids.

## 4. Deliverables
- An approved N-release catalogue (amino acid → enzymes/routes → KOs, with mode and shared flags).
- A strain × amino-acid call table with locus tags behind every call, for 45 Prochlorococcus strains + Synechococcus.
- A heatmap by clade, per-clade summary, HTML reports, and `paper.md`.
