# Proposal — Amino-acid utilization pathways across Prochlorococcus genomes

Researcher: Dikla Aharonovich · Drafted 2026-11-04 · Status: **approved 2026-11-04 (Plan locked)**

> **Change log (Plan phase).**
> - v1 covered amino-acid transporters and full degradation routes.
> - Design review then narrowed it:
>   - focus on removing nitrogen from amino acids (motivated by amino acids as a nitrogen source; see the interpretation limits);
>   - Synechococcus added as a comparison group;
>   - Alteromonas removed;
>   - after the MED4 pilot, **transporters set aside** (deferred, not in this analysis);
>   - v4: **utilization pathways scored only on their breakdown-only (dedicated) steps.** The researcher judged that enzymes shared with biosynthesis are not informative about utilization, so the v3 "shared only" call was dropped.
>   - v5 (critic pass 3): status anchored on each pathway's N-freeing step; an operational dedicated/shared rule; precedence for the per-amino-acid cell.
>
> Earlier versions are in git history; the reasons are in `proposal_notebook.md`.

## 1. Question

**For each of the 20 standard (L-) amino acids, which Prochlorococcus strains carry a breakdown (utilization) pathway, judged by the pathway's breakdown-only enzymes, that frees the amino acid's nitrogen? How does this differ across clades, and compared with marine Synechococcus?**

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
- **Comparison group: marine Synechococcus.** `list_organisms(["Synechococcus"])` returns 54 genome strains. The match also catches freshwater *S. elongatus* PCC 7942 and UTEX 2973, *Picosynechococcus* PCC 7002 and *Thermosynechococcus* BP-1. **Inclusion rule (researcher decision):** marine picocyanobacteria only, i.e. Synechococcus/Parasynechococcus subclusters 5.1–5.3. Freshwater, thermophilic and other-genus strains are excluded. The included list and its count are frozen in methods from `list_organisms`, using its clade/taxonomy fields.
- **Experiments:** none used. No KG experiment grows Prochlorococcus on amino acids.
- **Data used (genome annotations only):**
  - KEGG orthology (KO) assignments per gene (`genes_by_ontology`, ontology `kegg`).
  - The KG's KEGG reaction layer (`genes_by_metabolite`, evidence `metabolism`), as a cross-check for N-removing enzymes the catalogue missed.

## 3. Framing

### Hypothesis
None. The analysis is descriptive. Patterns across clades or between genera are reported as observations, not tested claims.

### Approach

**1. Pathway catalogue.** For each of the 20 amino acids, list its known bacterial breakdown pathway(s) as ordered enzyme steps, up to and including the step(s) that free the nitrogen (as NH4+, by transamination, via urea, or by converting the skeleton into glutamate). Each step:
- has **one or more KO ids** (isozymes and paralog KOs grouped). The step is present if any of its KOs is present;
- has an **N-mode** where it frees N (NH4+ / transfer + acceptor / via urea / conversion to glutamate);
- is flagged **dedicated** or **shared** by one **operational rule**, applied uniformly. A step is **shared** if its reaction is needed in cyanobacterial metabolism for something other than breaking amino acids down: it makes a product the cell must build (an amino acid, a polyamine, a cofactor, a nucleotide); it belongs to central carbon or nitrogen metabolism; or it serves another N source (e.g. urease for urea). Otherwise it is **dedicated**. The judgement is against cyanobacterial metabolism, not bacteria in general `[interpretation]`. Consequence for the draft: both amino-acid decarboxylases making polyamines (speA for Arg, cadA for Lys) are **shared**. A short written reason is given for every flag, and the researcher approves them.
- **Where a pathway ends.** Each pathway is defined up to and including its **N-freeing step**: the first step that frees nitrogen from the amino acid, as NH4+, by transamination, as urea, or by converting the skeleton into glutamate. For amino acids with more than one N (Arg, Asn, Gln, His, Lys, Trp), the pathway ends at the first N-freeing step. Further N atoms freed later are listed as context and not scored. Example: His via the hut route ends at histidine ammonia-lyase (hutH), which frees NH4+ at step 1. A route in which the amino acid's N is only moved into another amino acid (e.g. Thr → Gly) is extended to the step that frees N from that product. Example: Thr → Gly → glycine cleavage.

**Source:** drafted by Claude from standard biochemistry (KEGG reference pathways/modules); an `[interpretation]` input. The MED4 pilot draft (`spike/data/med4_n_release_catalogue.csv`) is the starting point and will be rebuilt as pathways. KO validity is checked against KEGG REST (`list/ko`), not the KG. A valid KO with no gene in the KG stays in and scores absent. **The researcher approves the catalogue (steps, KOs, dedicated/shared flags) before any strain beyond MED4 is scored.** At that same review, the controls below are fixed.

**Broad-specificity and D-amino-acid enzymes** (e.g. K00273) are reported in their own column and never credited to an individual amino acid.

**2. Presence per strain.**
- A step is **present** if ≥1 gene in the strain is annotated to any of its KOs.
- Matching is by KO, **never by gene name** (the pilot found names that disagree with KO and product).
- **KO/product disagreements are flagged** (e.g. MED4 PMM1468: K00639 kbl, product "8-amino-7-oxononanoate synthase"). A flagged hit does not count until the researcher reviews it.
- Locus tags are kept for every hit; orthologs are linked by KG ortholog groups for display only.

**3. Pathway status per strain.** k/n counts the **dedicated** steps only. Shared steps never add to k or n. But the **N-freeing step is an anchor**: it must be present in the strain for the pathway to be complete, even when it is a shared step (then it is an uncounted precondition).
- **complete:** all dedicated steps present (k = n) **and** the N-freeing step present;
- **partial:** some but not all dedicated steps present, **or** all dedicated steps present but the N-freeing step missing. Shown as k of n, plus a separate field "N-freeing step: present / missing";
- **absent:** no dedicated step present;
- **can't be judged from the genome:** the pathway has no dedicated step (all steps shared). It is never counted as present. A secondary flag records whether all of its shared steps are present ("all-shared route fully present").
- n is always shown with k. k/n is **not comparable across pathways of different lengths**: single-step pathways can only be complete or absent.

**Per amino acid:** one cell, chosen by precedence **complete > partial > absent > can't be judged**. Within "partial", the highest k/n wins; ties go to the pathway with more steps. The cell also shows:
- the number of pathways catalogued for that amino acid;
- the "all-shared route fully present" flag, if any of its pathways has it.

**Utilization pathway found** means at least one pathway is complete.

Worked examples from the MED4 pilot (draft catalogue, for illustration):
- **Asn:** asparaginase route, 1 dedicated step that is also the N-freeing step (K01424/K13051), present (PMM0821 ansA) → **complete**.
- **Arg:** arginase and arginine-deiminase routes absent. The agmatine route has only shared steps (speA, speB; urease shared) but all of them are present in MED4 → arginine cell = **absent**, with the flag "all-shared route fully present".
- **His:** the hut pathway (all dedicated) has no MED4 gene → **absent**.

**4. Cross-check for gaps in the catalogue.**
- For each strain, list genes the KG's reaction layer links to an N-removing reaction on that amino acid that are not in the catalogue. These are candidates for the researcher to add or reject.
- Reaction direction is checked by hand for each candidate. The pilot showed that an EC-prefix filter also catches reactions where the amino acid is a *product* (e.g. carbamoyl-phosphate synthase for Glu).
- This list is reviewed with the catalogue, before scoring.

**5. Comparison.**
- A strain × amino-acid table and heatmap, rows grouped by clade, with marine Synechococcus as a separate block. Cell = complete / partial (k of n) / absent / can't be judged.
- Per-clade counts.
- Genome size (gene count) is shown beside each strain, because larger genomes may carry more enzymes simply by size.
- **Wording rule for genus differences:** "annotated in X of N marine Synechococcus vs Y of 45 Prochlorococcus." Never "Prochlorococcus lost …" or other evolutionary claims; this design cannot tell loss from gain.

**Methods milestone type: discovery.** The catalogue *is* the entity set. Verification layers:
1. real-serialization fixtures. These include the code invariants: "shared steps never count toward status"; "an all-shared pathway is 'can't be judged', never complete"; "broad/D-amino-acid entries never credit an amino acid."
2. an independent MCP-only answer key for 5 amino acids (their pathways) in three strains, built without the module. MED4 is **not blind** (seen in the pilot); the two other strains (one HL, one LL, not MED4) are blind and carry the weight.
3. API-usage review of `genes_by_ontology` / `genes_by_metabolite` against the explorer docs;
4. a random sample of hits in each call bin, shown to the researcher.

Catalogue and rules are approved before any non-MED4 results are seen; later changes are logged with reason and date.

### Statistics plan
**No formal tests.** The analysis is descriptive with no hypothesis, and strains are not independent (shared ancestry). Results are counts and fractions per strain, per clade and per genus, with clade sizes stated; HLIII, HLIV and LLIII summaries are flagged as one- or two-strain observations.

### Validation set
Alteromonas was removed by the researcher, so all checks are within Prochlorococcus.

**Trade-off:** no check shows the method can detect a complete *dedicated* pathway where one surely exists. "Absent" is therefore reported as "not found with these annotations." These controls share the target's annotation pipeline: they test KO matching, not biology. The MED4 pilot found one dedicated step present (asparaginase, PMM0821), which shows that dedicated enzymes *can* be detected in Prochlorococcus annotations. It is not blind, and it is not a control.

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
  - most amino acids have no utilization pathway in Prochlorococcus;
  - some amino acids "can't be judged" (all catalogued pathways are all-shared). Under the draft catalogue, Glu (if GDH is shared) and Gly (glycine cleavage and glycine oxidase are shared) are the likely cases;
  - complete pathways found in some strains only (e.g. larger LL genomes).

  Each is reported as a result. A null is a valid, bounded outcome.
- **Pre-registered expected-negative (flag and inspect, not halt):**
  - At catalogue approval, before scoring, name one **dedicated step within a catalogued pathway** that should be absent from **cyanobacteria in general** `[interpretation]`, so that a hit would more likely mean a KO-matching artefact than biology. It is inspected at step level.
  - A hit in any strain is **inspected and reported**: its locus tag, its product, and whether the KO assignment holds up. It does not halt the analysis.
  - Disclosure: the MED4 pilot already showed which dedicated enzymes MED4 lacks (`proposal_notebook.md`), so any MED4-based candidate is not blind.

### Researcher decisions (2026-11-04, design review close)
1. **Glutamate dehydrogenase is shared.** It also assimilates NH4+ (central N metabolism). Glutamate will likely be "can't be judged."
2. **Comparison group = marine Synechococcus only** (subclusters 5.1–5.3). Freshwater, thermophilic and other-genus strains are excluded; the list is frozen in methods.
3. **Urease is shared.** It serves urea use.

### Design comparability
No experiments are used; the concern is whether **annotations are comparable across genomes**.

| Data source | Role | Comparable across strains? | Can confirm | Cannot confirm |
|---|---|---|---|---|
| KEGG KO per gene | N-release presence | The KG has no organism-level provenance (`reference_database` null for all 45). Methods tabulates the gene→KO edge `sources` / `evidence` per strain; any difference is reported, else comparability is stated as an assumption. | Enzyme-family presence | Activity, substrate range, direction, regulation |
| KEGG reaction layer | catalogue cross-check only | Same | Candidate enzymes the catalogue missed | Reaction direction (checked by hand) |
| Genome completeness | affects every "absent" | No KG field. **Source:** NCBI assembly level by `ncbi_taxon_id` (external input), plus researcher knowledge. **Action:** "absent" in a non-complete genome is reported as **absent (assembly incomplete)**. | — | — |
| Marine Synechococcus annotations | comparison group | Same pipeline check. Genome sizes overlap with Prochlorococcus (Synechococcus mostly 2,463–4,456 genes; Prochlorococcus 1,870–3,203), so gene count is shown | Differences in annotated capacity ("X of N vs Y of 45") | Loss vs gain; whether a shared absence is biology or annotation |

### Interpretation limits (stated up front)
- **Enzyme ≠ external N source.** These enzymes also act on amino acids made inside the cell, or freed by protein turnover. With transporters deferred, a strain that "can release N from amino acid X" cannot be said to *use external X as an N source*.
- **Annotation ≠ function.** KO presence shows an enzyme family, not activity or substrate specificity. Broad-specificity aminotransferases may act on several amino acids.

## 4. Deliverables
- An approved pathway catalogue (amino acid → pathways → steps → KOs, with N-mode and dedicated/shared flags).
- A strain × pathway status table (k/n dedicated steps) and a strain × amino-acid summary, with locus tags behind every step, for 45 Prochlorococcus strains + marine Synechococcus.
- A heatmap by clade, per-clade summary, HTML reports, and `paper.md`.
