# Proposal notebook — Plan-phase record

## Dialogue summary (2026-11-04, researcher: Dikla)

- Subject: amino-acid utilization in Prochlorococcus. Researcher has her own growth experiments of several strains on amino acids as the N source; those are **not in the KG** and the researcher asked to set them aside.
- Locked aim: a comparison of which amino-acid transporter and amino-acid breakdown genes each strain carries.
- Purpose: standalone result. Hypothesis: none; descriptive.
- "Breakdown" means **full degradation pathways** (not only the N-releasing enzymes).
- Approach for degradation: **route by route** (curated step lists reviewed by the researcher), chosen over whole-KEGG-map gene counts.
- Scope defaults accepted ("go for it"): all 45 strains grouped by clade; all 20 amino acids; three transporter evidence lines kept separate, class-level calls separate; expression data deferred.

## KG grounding queries (KG 0.1.0-alpha.9, explorer 0.1.0-alpha.6; preflight green)

| Query | Result |
|---|---|
| `list_experiments(organism="Prochlorococcus", search_text="amino acid OR … casamino")` | 1 of 340 experiments: MIT9313 viral DOM (vDOM) addition, RNA-seq (DOI 10.1111/1462-2920.14513). No amino-acid-as-N-source growth experiment. |
| `list_publications(organism="Prochlorococcus", search_text="amino acid OR organic nitrogen")` | 12 publications; N-related: Tolonen 2006 (10.1038/msb4100087), Read 2017 (10.1038/ismej.2017.88), Domínguez-Martín 2017 (10.1128/mSystems.00008-17), Weissberg/Aharonovich/Sher 2025 (10.1101/2025.11.24.690089); SBP survey Ford 2021 (10.1042/BST20200244). |
| `list_organisms(["Prochlorococcus"])` | 45 genome strains, clades HLI–HLIV, LLI–LLIV. Gene counts 1,870 (RSP50) – 3,203 (MIT0701). Transported-metabolite counts (TCDB) 32 (MIT0601) – 81 (MIT0701/0702). 42 strains carry `sbp_predicted_substrate`; MIT1314, MIT1327, RSP50 do not. Peptidase genes 32–73. |
| `list_metabolites(search amino acids, organisms MED4/MIT9313, evidence=transport)` | 8 metabolites incl. Glutamine, Glutamate, Alanine, Arginine, generic "Amino acid" (class). TCDB uses generic (non-stereo) names; KEGG reactions use L-/D- forms → need `include_stereo_forms`. GO transport for alanine reaches only LL strains + some others; for glutamate, all 45 Prochlorococcus. |
| `search_ontology(kegg, amino-acid / degradation maps, organism=MED4)` | KEGG levels in KG: subcategory → pathway → KO (no KEGG modules). MED4 genes: Amino acid metabolism 116; Gly/Ser/Thr 25; Cys/Met 23; Ala/Asp/Glu 15; Arg/Pro 13; His 12; D-amino acid 7; Val/Leu/Ile degradation 6; Tyr 5; Lys degradation 4; Phe 3; Trp 2. Only Val/Leu/Ile and Lys maps are degradation-only. |
| `docs://analysis/transport` | Three transport routes (KEGG metabolism / TCDB / GO) kept apart; TCDB family-walk rows are candidates, not calls; urtA's family 3.A.1.4 would add ~two dozen amino acids if walked; GO and TCDB agreement is not independent. |

## Rejected alternatives

- **Whole KEGG amino-acid maps, gene counts per strain.** Rejected: most maps mix biosynthesis and degradation, so counts would mostly measure biosynthesis (MED4 has 116 "amino acid metabolism" genes).
- **N-releasing enzymes only.** Researcher chose full routes; N-releasing steps are kept as a per-step flag instead.
- **Linking to the researcher's growth data.** Out of scope at the researcher's request.
- **Formal clade tests.** Rejected: descriptive aim, and strains are phylogenetically non-independent.

## Design-review round 1 (2026-11-04)

- **Focus narrowed to amino acids as a nitrogen source** (researcher). Degradation is now scored primarily by the N-releasing step per amino acid (release as NH4+ or transfer by transamination); the full carbon-skeleton route is secondary context. proposal.md to be updated after the pilot.
- **Synechococcus** proposed by researcher as positive control; Claude recommended comparison group + Alteromonas kept as method check. **Decided: Synechococcus = comparison group alongside Alteromonas (method check).**
- **Peek disclosure:** at the researcher's request, a throwaway proof-of-concept was run on MED4 alone (`spike/`) before the rules were locked. MED4 is also the planned answer-key strain, so its results have now been seen; the final call rules, catalogue and GO term list are still approved before scaling to all strains, and any rule shaped by the MED4 pilot is recorded as such.
- **Alteromonas removed** (researcher, 2026-11-04). Replaced as method check by in-genus controls: glnA in all 45; 2–3 biosynthetic aminotransferases (N-transfer, required for prototrophy) in all 45; urea transporter urtA–E returned by the TCDB extraction on urea. Stated trade-off: no check that a *dedicated* degradation route can be detected where one surely exists.

## MED4 pilot (throwaway, `spike/`, 2026-11-04)

Full manifest and tables in `spike/spike_summary.md`; data in `spike/data/`. Key counts (verified against `spike/data/med4_aa_summary.csv`, `med4_aa_uptake.csv`, `med4_validation_probes.csv`):

- **Uptake:** TCDB direct = 0 rows for all 20 amino acids and 7 amino-acid classes. GO MF specific = 1 gene (PMM0628 gltS, glutamate). SBP: 0 of 9 MED4 SBPs predicted for amino acids (PMM1049 dppA = peptide). TCDB family-walk candidates = 10 rows, mostly non-transporters by product (lipid exporters for Cys, sppA for Ala, murJ for Gln).
- **N release:** 11 of 20 amino acids have a catalogued N-releasing KO with a MED4 gene (Arg, Asn, Asp, Gln, Gly, His, Ile, Leu, Ser, Thr, Val); 9 have none (Ala, Cys, Glu, Lys, Met, Phe, Pro, Trp, Tyr). Most hits are enzymes also used in biosynthesis (e.g. ilvE PMM0878 for Ile/Leu/Val; hisC PMM0186; aspC-named PMM0674; ilvA PMM0908). No MED4 gene on glutamate dehydrogenase, glutaminase, alanine dehydrogenase, proline dehydrogenase, hut, arginase.
- **Probes:** glnA found (PMM0920). urtC (PMM0972) and urtE (PMM0974) carry a curated GO MF term "branched-chain amino acid transmembrane transporter activity" → class-level credit on the urea transporter (not a failure under the rules, but flagged). pst genes: no amino-acid rows.
- **Not done in pilot:** KO validity vs KEGG REST (15 of 75 KOs not in KG), approved GO list, subunit roles, reaction direction.

## Design-review round 2 (2026-11-04, after the MED4 pilot)

- Claude recommended a reviewed "candidate transporter family" line (example: gltS PMM0628 is family-only in TCDB 2.A.27; urtA–E in HAAT 3.A.1.4 but with direct urea systems → excluded). The line would add 1 gene in MED4.
- **Researcher decision: leave transporters aside.** The analysis is now N-release capacity only; transporters are deferred. proposal.md rewritten (v2). The urea-transporter positive control and all transporter evidence lines are removed. A new up-front limit: enzyme presence ≠ use of *external* amino acids as an N source.

## Design-review round 3 (2026-11-04)

- **Researcher: "only enzymes also used to build amino acids is not relevant" → focus on utilization pathways.** v4: whole breakdown pathways per amino acid, scored only on dedicated (breakdown-only) steps; shared steps shown as context, never counted; all-shared pathways = "can't be judged from the genome". The v3 dedicated / shared-only / none-found call is dropped.
- Worked MED4 examples shown to the researcher (draft catalogue): Asn complete (asparaginase PMM0821 ansA); Lys partial (cadA PMM1084); Arg no pathway (urease now shared; agmatine route all-shared); His absent (no hut genes); Thr hit PMM1468 flagged KO/product mismatch.
- The researcher asked for an updated infographic and a MED4 pilot summary figure (`spike/figures/`, throwaway).
