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
