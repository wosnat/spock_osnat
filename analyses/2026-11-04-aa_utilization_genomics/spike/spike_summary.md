# Spike: MED4 amino acids as a nitrogen source (throwaway proof of concept)

Strain: Prochlorococcus MED4 only. KG 0.1.0-alpha.9, explorer 0.1.0-alpha.6 (kg_release_info verdict ok).
Factual record only; no biological conclusions. Columns `mode` and `shared_interpretation` in the KO catalogue are [interpretation] (drafted from standard biochemistry, not from the KG).

## What ran

All scripts run from the repo root as `uv run python analyses/2026-11-04-aa_utilization_genomics/spike/scripts/<script>` (with PYTHONUTF8=1).

| script | outputs |
|---|---|
| s01_explore_metabolites.py | stdout only (list_metabolites per amino-acid name) |
| s02_probe.py, s02b_probe.py, s02c_probe.py | schema probes (stdout only) |
| s03_uptake.py | data/med4_aa_uptake.csv (13 rows), data/med4_aa_uptake_envelopes.csv (83), data/med4_aa_metabolite_ids.csv (27), data/med4_sbp_all.csv (9) |
| s04_tcdb_context.py | data/med4_tcdb_all_levels.csv (646 gene x TCDB-term rows, levels 2-4) |
| s05_n_release.py | data/med4_n_release_catalogue.csv (75), data/med4_aa_n_release.csv (76), data/med4_aa_metabolism_crosscheck.csv (239) |
| s06_summary.py | data/med4_aa_summary.csv (20), data/med4_validation_probes.csv (11), data/_summary_tables.md |
| build_spike_summary.py | spike_summary.md (this file) |

Metabolite id mapping: data/med4_aa_metabolite_ids.csv. Each amino acid was queried with its generic + L- + D- ids where they exist, plus `include_stereo_forms=True`. Notes: no generic "Arginine" metabolite found (kegg.compound:C02385 "Amino acid(Arg-)" used as the arginine-like entry, 12 transporters KG-wide); Thr has only L-Threonine (C00188); generic isoleucine is chebi:24898; Gly is a single id. Class ids queried: C00045 + chebi:33709 (amino acid), C00151 (L-amino acid), C00405 (D-amino acid), chebi:22918 (branched-chain), chebi:26167 (polar), C01021 (aromatic), chebi:26834 (sulfur-containing).

Uptake lines: TCDB direct = `genes_by_metabolite(evidence_sources=['transport'], include_stereo_forms=True)`; TCDB family candidates = same + `include_tcdb_family_substrates=True`, family rows only; GO MF = `evidence_sources=['go_transport'], go_namespace=['molecular_function'], go_include_ancestors=True` (all 3 GO rows returned have go_term_depth 0); SBP = `genes_by_categorical_metric` on `derived_metric:BST20200244:med4_sbp:sbp_predicted_substrate` and `...:sbp_nutrient_class` (9 MED4 genes each). N-release: `ontology_term_details` on 75 KOs, `genes_by_ontology(ontology='kegg', organism='MED4', term_ids=..., min_gene_set_size=0)`, cross-check `genes_by_metabolite(evidence_sources=['metabolism'])` per amino acid.

## Uptake envelope facts
- TCDB direct: total_matching = 0 for all 20 amino acids and all 7 class targets.
- `tcdb_family_substrates_not_shown` (direct run) non-zero for: Ala {genes 1, rows 1}, Cys {genes 5, rows 5}, Glu {genes 1, metabolites 3, rows 3}, Gln {genes 1, rows 1}; all others 0.
- `tcdb_family_substrates_skipped` (identical on every query): tcdb:3.A.1 (ABC superfamily, 547 substrates) for PMM0449, PMM0450, PMM0913, PMM0977.
- GO MF: 1 specific row (Glu: PMM0628 gltS, go:0015501 glutamate:sodium symporter activity, curated); 2 class rows (branched-chain amino acid: PMM0972 urtC, PMM0974 urtE, go:0015658 branched-chain amino acid transmembrane transporter activity, curated).
- SBP: 9 MED4 SBP genes; none has predicted substrate `amino_acids` (values: not_stated, cyanate, manganese, phosphonate, phosphate, urea, manganese_zinc, peptide, iron). PMM1049 dppA = peptide (nitrogen class).
- MED4 TCDB context (data/med4_tcdb_all_levels.csv): urtA-E (PMM0970-0974) sit in subfamily tcdb:3.A.1.4 "Hydrophobic Amino Acid Uptake Transporter (HAAT) Family" with system calls tcdb:3.A.1.4.4 "high-affinity urea porter" and 3.A.1.4.5 "urea/thiourea/hydroxyurea porter". dppA/B/C, ddpD (PMM1049, PMM1048, PMM0421, PMM0192) are in tcdb:3.A.1.5 PepT family (gate = annotated, eggnog).

### Per-amino-acid summary (data/med4_aa_summary.csv)

| amino_acid   | tcdb_direct      | go_mf_specific   | sbp_specific     | class_level_calls                                                  | tcdb_family_candidates                                                    | n_release_present   | nh4_release_ko_genes                                                                   | transfer_ko_genes    | other_n_route_ko_genes                     | metabolism_arm_N_removing_genes_not_in_KO_catalogue                                                                                                                               |
|:-------------|:-----------------|:-----------------|:-----------------|:-------------------------------------------------------------------|:--------------------------------------------------------------------------|:--------------------|:---------------------------------------------------------------------------------------|:---------------------|:-------------------------------------------|:----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Ala          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | PMM1180(sppA)                                                             | no                  | none found in KG                                                                       | none found in KG     |                                            | PMM0070(sufS1); PMM0616(amiC); PMM0919(spt); PMM1472(bioA); PMM1527(alr)                                                                                                          |
| Arg          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | yes                 | K01428:PMM0963(ureC); K01429:PMM0964(ureB); K01430:PMM0965(ureA); K01480:PMM1686(speB) | none found in KG     | K00611:PMM1263(argF); K01585:PMM0045(speA) | PMM1703(-)                                                                                                                                                                        |
| Asn          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | yes                 | K01424:PMM0821(ansA)                                                                   | none found in KG     |                                            |                                                                                                                                                                                   |
| Asp          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | yes                 | K00278:PMM0100(nadB)                                                                   | K00812:PMM0674(aspC) |                                            | PMM0222(aspA); PMM0821(ansA)                                                                                                                                                      |
| Cys          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | PMM0065(mcyH); PMM0827(mdlB); PMM1239(hetA); PMM1295(sodX); PMM1323(glcH) | no                  | none found in KG                                                                       | none found in KG     | K01738:PMM0123(cysK); K01738:PMM0407(cysK) | PMM0409(metB); PMM0674(aspC); PMM1670(metC)                                                                                                                                       |
| Glu          | none found in KG | PMM0628(gltS)    | none found in KG | none found in KG                                                   | PMM0628(gltS)                                                             | no                  | none found in KG                                                                       | none found in KG     |                                            | PMM0184(pabC); PMM0186(hisC); PMM0674(aspC); PMM0825(carB); PMM0878(ilvE); PMM0919(spt); PMM0951(carA); PMM1301(argD); PMM1500(dapL); PMM1512(glsF); PMM1606(glmS); PMM1692(pabB) |
| Gln          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | PMM0261(murJ)                                                             | yes                 | none found in KG                                                                       | K00284:PMM1512(glsF) |                                            | PMM0184(pabC); PMM0825(carB); PMM0951(carA); PMM1606(glmS); PMM1692(pabB)                                                                                                         |
| Gly          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | yes                 | K00281:PMM1668(gcvP); K00605:PMM1687(gcvT); K02437:PMM1669(gcvH); K03153:PMM0047(thiO) | K00830:PMM0919(spt)  |                                            | PMM1298(lpdA); PMM1703(-)                                                                                                                                                         |
| His          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | yes                 | none found in KG                                                                       | K00817:PMM0186(hisC) |                                            |                                                                                                                                                                                   |
| Ile          | none found in KG | none found in KG | none found in KG | PMM0972[branched-chain_aa,go_mf]; PMM0974[branched-chain_aa,go_mf] | none                                                                      | yes                 | none found in KG                                                                       | K00826:PMM0878(ilvE) |                                            |                                                                                                                                                                                   |
| Leu          | none found in KG | none found in KG | none found in KG | PMM0972[branched-chain_aa,go_mf]; PMM0974[branched-chain_aa,go_mf] | none                                                                      | yes                 | none found in KG                                                                       | K00826:PMM0878(ilvE) |                                            |                                                                                                                                                                                   |
| Lys          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | no                  | none found in KG                                                                       | none found in KG     | K01582:PMM1084(cadA)                       |                                                                                                                                                                                   |
| Met          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | no                  | none found in KG                                                                       | none found in KG     |                                            | PMM1611(thiC)                                                                                                                                                                     |
| Phe          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | no                  | none found in KG                                                                       | none found in KG     |                                            | PMM0186(hisC); PMM0674(aspC)                                                                                                                                                      |
| Pro          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | no                  | none found in KG                                                                       | none found in KG     |                                            | PMM1703(-)                                                                                                                                                                        |
| Ser          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | yes                 | K01754:PMM0908(ilvA)                                                                   | none found in KG     |                                            | PMM0919(spt)                                                                                                                                                                      |
| Thr          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | yes                 | K01754:PMM0908(ilvA)                                                                   | none found in KG     | K00639:PMM1468(bioF)                       |                                                                                                                                                                                   |
| Trp          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | no                  | none found in KG                                                                       | none found in KG     |                                            |                                                                                                                                                                                   |
| Tyr          | none found in KG | none found in KG | none found in KG | none found in KG                                                   | none                                                                      | no                  | none found in KG                                                                       | none found in KG     |                                            | PMM0186(hisC); PMM0674(aspC)                                                                                                                                                      |
| Val          | none found in KG | none found in KG | none found in KG | PMM0972[branched-chain_aa,go_mf]; PMM0974[branched-chain_aa,go_mf] | none                                                                      | yes                 | none found in KG                                                                       | K00826:PMM0878(ilvE) |                                            |                                                                                                                                                                                   |

Broad-specificity KOs (amino_acid = ALL) with a MED4 gene: K00273:PMM1703(nan)

### KO catalogue (data/med4_n_release_catalogue.csv; mode and shared columns are [interpretation])

| amino_acid   | ko     | label     | ec                | mode                    | shared_interpretation   | ko_in_kg   | med4_locus_tags   |
|:-------------|:-------|:----------|:------------------|:------------------------|:------------------------|:-----------|:------------------|
| Ala          | K00259 | ald       | 1.4.1.1           | release_NH4             | no                      | True       |                   |
| Ala          | K00285 | dadA      | 1.4.5.1           | release_NH4             | no                      | True       |                   |
| Ala          | K14260 | alaA/alaC | 2.6.1.2           | transfer_transamination | yes                     | True       |                   |
| Ala          | K00814 | GPT       | 2.6.1.2           | transfer_transamination | yes                     | False      |                   |
| Ala          | K00835 | avtA      | 2.6.1.66          | transfer_transamination | yes                     | True       |                   |
| Arg          | K01476 | rocF      | 3.5.3.1           | release_NH4             | no                      | True       |                   |
| Arg          | K01478 | arcA      | 3.5.3.6           | release_NH4             | no                      | True       |                   |
| Arg          | K00611 | argF/arcB | 2.1.3.3           | other_N_route           | yes                     | True       | PMM1263           |
| Arg          | K00926 | arcC      | 2.7.2.2           | release_NH4             | no                      | True       |                   |
| Arg          | K01585 | speA      | 4.1.1.19          | other_N_route           | yes                     | True       | PMM0045           |
| Arg          | K01480 | speB      | 3.5.3.11          | release_NH4             | yes                     | True       | PMM1686           |
| Arg          | K12252 | aruH      | 2.6.1.84          | transfer_transamination | no                      | True       |                   |
| Arg          | K00819 | rocD      | 2.6.1.13          | transfer_transamination | no                      | True       |                   |
| Arg          | K01428 | ureC      | 3.5.1.5           | release_NH4             | no                      | True       | PMM0963           |
| Arg          | K01429 | ureB      | 3.5.1.5           | release_NH4             | no                      | True       | PMM0964           |
| Arg          | K01430 | ureA      | 3.5.1.5           | release_NH4             | no                      | True       | PMM0965           |
| Asn          | K01424 | ansA      | 3.5.1.1           | release_NH4             | no                      | True       | PMM0821           |
| Asn          | K13051 | iaaA/ansB | 3.5.1.1;3.4.19.5  | release_NH4             | no                      | True       |                   |
| Asp          | K01744 | aspA      | 4.3.1.1           | release_NH4             | no                      | True       |                   |
| Asp          | K00278 | nadB      | 1.4.3.16          | release_NH4             | yes                     | True       | PMM0100           |
| Asp          | K00812 | aspB      | 2.6.1.1           | transfer_transamination | yes                     | True       | PMM0674           |
| Asp          | K00813 | aspC      | 2.6.1.1           | transfer_transamination | yes                     | True       |                   |
| Asp          | K11358 | yhdR      | 2.6.1.1           | transfer_transamination | yes                     | False      |                   |
| Asp          | K14454 | GOT1      | 2.6.1.1           | transfer_transamination | yes                     | False      |                   |
| Asp          | K14455 | GOT2      | 2.6.1.1           | transfer_transamination | yes                     | False      |                   |
| Cys          | K01760 | metC      | 4.4.1.13          | release_NH4             | yes                     | True       |                   |
| Cys          | K05396 | dcyD      | 4.4.1.15          | release_NH4             | no                      | True       |                   |
| Cys          | K17217 | mccB      | 4.4.1.1           | release_NH4             | no                      | False      |                   |
| Cys          | K01738 | cysK      | 2.5.1.47          | other_N_route           | yes                     | True       | PMM0123;PMM0407   |
| Glu          | K00261 | GLUD1_2   | 1.4.1.3           | release_NH4             | yes                     | True       |                   |
| Glu          | K00262 | gdhA      | 1.4.1.4           | release_NH4             | yes                     | True       |                   |
| Glu          | K15371 | GDH2      | 1.4.1.2           | release_NH4             | yes                     | True       |                   |
| Glu          | K01580 | gadB      | 4.1.1.15          | other_N_route           | no                      | True       |                   |
| Gln          | K01425 | glsA      | 3.5.1.2           | release_NH4             | no                      | True       |                   |
| Gln          | K00265 | gltB      | 1.4.1.13          | transfer_transamination | yes                     | True       |                   |
| Gln          | K00266 | gltD      | 1.4.1.13          | transfer_transamination | yes                     | True       |                   |
| Gln          | K00284 | GLU/glsF  | 1.4.7.1           | transfer_transamination | yes                     | True       | PMM1512           |
| Gly          | K00281 | gcvP      | 1.4.4.2           | release_NH4             | yes                     | True       | PMM1668           |
| Gly          | K00605 | gcvT      | 2.1.2.10          | release_NH4             | yes                     | True       | PMM1687           |
| Gly          | K02437 | gcvH      | -                 | release_NH4             | yes                     | True       | PMM1669           |
| Gly          | K03153 | thiO      | 1.4.3.19          | release_NH4             | yes                     | True       | PMM0047           |
| Gly          | K00830 | AGXT      | 2.6.1.44;2.6.1.51 | transfer_transamination | yes                     | True       | PMM0919           |
| His          | K01745 | hutH      | 4.3.1.3           | release_NH4             | no                      | True       |                   |
| His          | K01712 | hutU      | 4.2.1.49          | other_N_route           | no                      | True       |                   |
| His          | K01468 | hutI      | 3.5.2.7           | other_N_route           | no                      | True       |                   |
| His          | K01479 | hutG      | 3.5.3.8           | release_NH4             | no                      | True       |                   |
| His          | K00817 | hisC      | 2.6.1.9           | transfer_transamination | yes                     | True       | PMM0186           |
| Ile;Leu;Val  | K00826 | ilvE      | 2.6.1.42          | transfer_transamination | yes                     | True       | PMM0878           |
| Ile;Leu;Val  | K00263 | ldh       | 1.4.1.9           | release_NH4             | no                      | True       |                   |
| Lys          | K03918 | lat       | 2.6.1.36          | transfer_transamination | no                      | False      |                   |
| Lys          | K01582 | cadA      | 4.1.1.18          | other_N_route           | no                      | True       | PMM1084           |
| Met          | K01761 | mdeA      | 4.4.1.11          | release_NH4             | no                      | True       |                   |
| Phe;Tyr      | K00832 | tyrB      | 2.6.1.57          | transfer_transamination | yes                     | True       |                   |
| Phe;Tyr      | K00838 | ARO8      | 2.6.1.57          | transfer_transamination | yes                     | False      |                   |
| Phe          | K10775 | PAL       | 4.3.1.24          | release_NH4             | no                      | False      |                   |
| Phe;Tyr      | K13064 | PTAL      | 4.3.1.25          | release_NH4             | no                      | False      |                   |
| Phe          | K00270 | pdh       | 1.4.1.20          | release_NH4             | no                      | False      |                   |
| Tyr          | K00815 | TAT       | 2.6.1.5           | transfer_transamination | no                      | False      |                   |
| Pro          | K00318 | PRODH     | 1.5.5.2           | other_N_route           | no                      | True       |                   |
| Pro          | K13821 | putA      | 1.5.5.2;1.2.1.88  | other_N_route           | no                      | True       |                   |
| Pro          | K00294 | rocA      | 1.2.1.88          | other_N_route           | no                      | True       |                   |
| Ser          | K01752 | sdaA      | 4.3.1.17          | release_NH4             | no                      | True       |                   |
| Ser          | K01753 | dsdA      | 4.3.1.18          | release_NH4             | no                      | False      |                   |
| Ser;Thr      | K01754 | ilvA      | 4.3.1.19          | release_NH4             | yes                     | True       | PMM0908           |
| Ser;Thr      | K17989 | SDS       | 4.3.1.17;4.3.1.19 | release_NH4             | no                      | True       |                   |
| Thr          | K01620 | ltaE      | 4.1.2.48          | other_N_route           | no                      | True       |                   |
| Thr          | K00060 | tdh       | 1.1.1.103         | other_N_route           | no                      | True       |                   |
| Thr          | K00639 | kbl       | 2.3.1.29          | other_N_route           | no                      | True       | PMM1468           |
| Trp          | K01667 | tnaA      | 4.1.99.1          | release_NH4             | no                      | False      |                   |
| ALL          | K03334 | LAAO      | 1.4.3.2           | release_NH4             | no                      | False      |                   |
| ALL          | K00273 | DAO       | 1.4.3.3           | release_NH4             | no                      | True       | PMM1703           |
| ALL          | K14267 | dapC      | 2.6.1.17          | transfer_transamination | yes                     | True       |                   |
| ALL          | K10907 | K10907    | 2.6.1.-           | transfer_transamination | yes                     | True       |                   |
| ALL          | K00837 | ALD1      | 2.6.1.-           | transfer_transamination | yes                     | False      |                   |
| REF          | K01915 | glnA      | 6.3.1.2           | NH4_assimilation        | yes                     | True       | PMM0920           |

### Validation probes (data/med4_validation_probes.csv)

| query   |   total_matching | locus_tag   | gene_name   | product                                                   | uptake_rows                   |
|:--------|-----------------:|:------------|:------------|:----------------------------------------------------------|:------------------------------|
| glnA    |                1 | PMM0920     | glnA        | glutamine synthetase, type I                              | none                          |
| urtA    |                1 | PMM0970     | urtA        | ABC-type urea transporter, substrate binding component    | none                          |
| urtB    |                1 | PMM0971     | urtB        | ABC-type urea transporter, permease component             | none                          |
| urtC    |                1 | PMM0972     | urtC        | ABC-type urea transporter, membrane component             | class:branched-chain_aa/go_mf |
| urtD    |                1 | PMM0973     | urtD        | ABC-type urea transporter, ATP-binding component UrtD     | none                          |
| urtE    |                1 | PMM0974     | urtE        | ABC-type urea transporter, ATPase component UrtE          | class:branched-chain_aa/go_mf |
| pstS    |                1 | PMM0710     | pstS        | phosphate ABC transporter, phosphate-binding protein PstS | none                          |
| pstA    |                2 | PMM0035     | PSTA        | 3-phosphoserine transaminase                              | none                          |
| pstA    |                2 | PMM0724     | pstA        | ABC-type phosphate transport system permease component    | none                          |
| pstB    |                1 | PMM0725     | pstB        | ABC-type phosphate transport system ATPase component      | none                          |
| pstC    |                1 | PMM0723     | pstC        | ABC-type phosphate transport system permease component    | none                          |

## Anomalies / surprises (facts only)
1. TCDB direct returns 0 genes for every amino acid and every amino-acid class in MED4 (data/med4_aa_uptake_envelopes.csv, line = tcdb_direct, total_matching = 0 in 27 of 27 targets).
2. The only specific uptake row on any line is PMM0628 gltS for Glu (GO MF, curated); the same gene is family-only on TCDB (tcdb:2.A.27, tcdb_calls = eggnog, tcdb_direction = unknown).
3. urtC (PMM0972) and urtE (PMM0974) carry GO MF go:0015658 branched-chain amino acid transmembrane transporter activity; urtA, urtB, urtD do not. Their TCDB system calls are urea porters (3.A.1.4.4 / 3.A.1.4.5).
4. TCDB family candidates: Cys = 4 genes in tcdb:3.A.1.106 "Lipid Exporter (LipidE) Family" (PMM0065 mcyH, PMM0827 mdlB, PMM1239 hetA, PMM1295 sodX) plus PMM1323 glcH (tcdb:2.A.2 GPH family); Ala = PMM1180 sppA (signal peptide peptidase, tcdb:8.A.21.2 Stomatin family); Gln = PMM0261 murJ (lipid II flippase, tcdb:2.A.66.4). All have tcdb_substrate_system_count = 1 except gltS (5-6); all tcdb_direction = unknown.
5. 15 of 75 catalogue KOs are not in the KG (ko_in_kg = False): K00270, K00814, K00815, K00837, K00838, K01667, K01753, K03334, K03918, K10775, K11358, K13064, K14454, K14455, K17217. Not-in-KG is not the same as invalid; not checked against KEGG REST.
6. KO K00639 (KG name "kbl, GCAT; glycine C-acetyltransferase") maps to PMM1468, gene_name bioF, product "8-amino-7-oxononanoate synthase".
7. KO K00812 (KG name "aspB; aspartate aminotransferase") maps to PMM0674 whose gene_name is aspC; K00813 (aspC) has no MED4 gene.
8. PMM0222 has gene_name aspA but product "aspartoacylase"; its metabolism reactions are N-acetyl/N-formyl-aspartate amidohydrolases (EC 3.5.1.14/3.5.1.15). No MED4 gene on K01744 (aspartate ammonia-lyase).
9. PMM1670 (gene_name metC, product "cystathionine beta-lyase family aluminum resistance") and PMM0409 (metB) carry cysteine/cystathionine lyase reactions in the metabolism arm (EC 4.4.1.x, including deaminating reactions), but no MED4 gene is on KO K01760 (metC).
10. PMM1703 (no gene name, "possible D-amino-acid dehydrogenase") is on K00273 (DAO) and in the metabolism arm carries deaminating reactions for D-Arg, Gly and D-Pro.
11. resolve_gene("pstA", MED4) returns 2 genes: PMM0724 pstA (phosphate ABC permease) and PMM0035 gene_name PSTA, product "3-phosphoserine transaminase". PMM0035 is not in the KO catalogue.
12. No MED4 gene on any catalogued glutamate dehydrogenase KO (K00261, K00262, K15371), glutaminase (K01425), NADPH-GOGAT (K00265/K00266), arginase (K01476), arginine deiminase pathway (K01478, K00926), His utilisation (K01745, K01712, K01468, K01479), proline dehydrogenase / P5C dehydrogenase (K00318, K13821, K00294), serine dehydratase (K01752, K17989), Met gamma-lyase (K01761), tryptophanase (K01667 not in KG), aromatic aminotransferase (K00832), alanine dehydrogenase (K00259) or alanine aminotransferase (K14260, K00835).
13. Amino acids with no catalogued NH4-release or transamination KO hit in MED4: Ala, Cys, Glu, Lys, Met, Phe, Pro, Trp, Tyr (n_release_present = no; 9 of 20). For Ala, Cys, Glu, Phe, Tyr, Pro, Met the metabolism arm lists genes with N-removing-class ECs outside the catalogue (column metabolism_arm_N_removing_genes_not_in_KO_catalogue). Trp and Lys have none on either.
14. The cross-check column filter is EC-prefix based (1.4., 2.6.1., 3.5.1., 3.5.3., 4.3.1., 4.4.1., 4.1.99.1); it includes reactions where the amino acid is a product rather than a substrate (e.g. glsF, carA/carB, pabB for Glu; sufS1, amiC for Ala) and an unrelated EC (PMM1611 thiC, 4.1.99.17, matched by prefix 4.1.99.1). Reaction direction was not checked.
15. Ile/Leu/Val uptake is credited via the branched-chain class only; no Ile/Leu/Val-specific row exists.
16. glnA PMM0920 found on K01915.
17. n_release_present counts NH4-release and transamination modes only; Arg is "yes" via urease (ureA/B/C) + agmatinase (speB), which requires speA (arginine decarboxylase, catalogued as other_N_route) as the first step.
