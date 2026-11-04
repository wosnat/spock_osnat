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

