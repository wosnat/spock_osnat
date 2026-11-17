# High-light-inducible (hli) genes in *Prochlorococcus*: light response or broad stress response?

## Question

*Prochlorococcus* MED4 carries 23 genes encoding small high-light-inducible proteins (HLIPs). We ask whether their transcripts respond to light, and whether they respond across stresses other than light. Where the available experiments allow it, we also ask whether that response is independent of light. The analysis is restricted to MED4 and is exploratory: it reuses published transcriptome experiments, several of which were inspected while the analysis was planned.

## Background

HLIPs are single-helix members of the chlorophyll a/b-binding protein superfamily. They are thought to protect the photosynthetic apparatus when absorbed light exceeds what photosynthesis can use. The *hli* gene family is greatly expanded in high-light-adapted *Prochlorococcus*; MED4 has 23 copies, many of them in clusters and near-identical in sequence. Several *Prochlorococcus* transcriptome studies report *hli* induction. Because a cell under nutrient or CO2 limitation uses less of the light it absorbs, induction under such stresses could reflect either a light-driven photoprotective response or a broader stress response. The experiments brought together here comprise 28 MED4 transcriptome comparisons from 11 publications, covering light onset and photoperiod, photosynthetic electron transport, nitrogen, phosphorus, iron, CO2, salt and phage infection, together with non-stress comparisons.

## Methods

**Data.** All data come from a multi-omics knowledge graph (KG) of published *Prochlorococcus* studies. We used 28 MED4 transcriptome experiments (microarray and RNA-seq), with the significance calls of each original study. A 29th, a 2016 coculture RNA-seq comparison, was excluded. In that table 82% of log2 fold changes were negative, 291 genes with |log2FC| > 5 were called not significant, and 18 distinct fold-change values each recurred in ten or more genes, which is consistent with near-zero counts in one arm. All proteomics data were excluded.

The *hli* set is the 23 MED4 members of the 14 Cyanorak *hli* ortholog groups. Experiments were grouped as:
- light onset (five 45-min light shifts after 5 h dark, one shared dark control);
- schedule extension (extended light past dusk; extended darkness past dawn);
- constant dark vs constant light;
- photosynthetic electron transport (DCMU);
- phage in the dark;
- non-light stress (nitrogen, CO2, iron, phosphorus, salt, phage);
- non-stress or possible relief.

A 2025 coculture-vs-axenic comparison was split by sampling day. On day 11 both arms were growing exponentially, so it is non-stress. On day 18 the axenic control was nitrogen-starved and declining, so "down in coculture" means "higher under nitrogen stress". The low-nitrogen starvation series is compared with the same culture in exponential growth (day 11).

**Set-level tests.** For each experiment × time point × direction, we asked whether *hli* genes were over-represented among significantly changed genes, using a one-sided Fisher test (`fisher_ora`).
- **Background:** the measured genes for full tables. For tables listing only significant genes, the genome was the background, and those tests are marked approximate.
- **Not tested:** direction-time points with fewer than 10 significant genes, and the down direction of an up-only table.
- **Flagged:** tests where more than 30% of genes were significant are reported with a genome-wide flag.
- **Multiple testing:** Benjamini–Hochberg (BH) correction was applied per gene set across tests. Per-experiment calls take the smallest time-point p-value, multiplied by the number of testable time points, then BH-correct across experiments.
- **Reference sets:** the same tests were run for ten Cyanorak reference sets (ribosomal proteins, protein folding and degradation, N, P and Fe adaptation, light adaptation without *hli*, photosystems I and II, CO2 fixation).
- **Random baseline:** 200 size-matched random sets per test.
- **Direction:** all contrasts are treatment vs control; light is read with rules per group.

**Near-identical paralogs.** Four pairs of multi-copy *hli* genes (PMM0815/PMM1396, PMM0816/PMM1397, PMM0817/PMM1398, PMM0818/PMM1399) had identical fold changes in every microarray table that listed both members. We read them as one shared probe signal. In significant-only microarray tables listing one member, the other was treated as undefined, not as unchanged. As a sensitivity analysis, the set tests were rerun with each pair counted once in microarray tables.

**Gene-level patterns (exploratory).** Each gene in each experiment × time point was coded +1 (up), −1 (down), 0 (not significant) or undefined. The 23 genes were clustered by average linkage on 1 − the fraction of shared defined cells with the same call. Robustness was checked with a correlation distance and with the light-onset arrays removed.

Ortholog-group breadth was taken from KG organism counts and organism clade (high-light or low-light *Prochlorococcus*, *Synechococcus*, *Cyanobium*). Background light level was compared across studies by Spearman correlation.

All computations are scripts in the analysis folder; figures and tables are generated from them.

## Results

**Light onset.** All four testable 45-min light shifts (blue, red and white at 13 µmol photons m⁻² s⁻¹; white at 55) induced *hli* (per-experiment BH padj 5e-8 to 2e-10). In each, 8–11 of the 11 *hli* genes in the table were up, spanning 5–8 ortholog groups. No reference set went up at light onset; photosystem I went down in 2 of 6 light-onset tests. The green-light shift had too few changed genes to test. DCMU was tested at gene level only: three *hli* genes went down.

**Other light contrasts.** Constant darkness vs constant light, with or without phage, gave no set-level *hli* change. The two schedule-extension experiments (extended light, extended darkness) are dominated by genome-wide responses (over 30% of genes significant at two of four time points).
- At gene level, six multi-copy genes were higher in the dark arm of both experiments.
- Two single-copy genes (PMM0064, PMM0093) went up in both.
- The set-level reading is therefore unclear.

**Non-light stresses.** *hli* was induced in 4 of 6 non-light stress types:
- **CO2 limitation:** two experiments; padj 2e-10 and 5e-10.
- **Iron starvation:** padj 6e-5.
- **Nitrogen:** three experiments; padj 5e-12 to 8e-3.
- **Phage infection:** microarray, padj 8e-12.

*hli* was not induced in phosphate starvation, salt acclimation or phage lysate in the light. It went down when iron was re-added after starvation (padj 9e-6) and when air was sparged compared with time 0 (padj 1e-6). It was also up when urea or cyanate replaced ammonium as nitrogen source (padj 8e-11 and 2e-12).
- **Robustness:** counting the paralog pairs once changed no test or experiment call (20 significant tests before and after). The phage call rested on 5 independent signals instead of 9 (padj 1e-6).

**Timing.** Within the time courses, the *hli* response was early and brief in phage infection: 9 of 23 *hli* genes (5 independent signals) were up at 1 h, and none from 2 h. Under nutrient limitation it built up slowly:
- **Nitrogen deprivation:** 0 of 17 measured genes up at 0–3 h, 10 of 17 at 48 h, after the drop in ribosomal-protein genes.
- **Iron starvation:** 0 of 19 up at 12 h, 6 of 19 at 48 h.
- **Long-term low-nitrogen coculture:** peaked at day 31 and declined by day 89.

**Two groups of *hli* genes (exploratory).** Clustering the per-gene calls separated 13 of the 14 multi-copy genes (cluster C4) from most single-copy genes (C2, 7 genes). Before the paralog correction, the multi-copy genes had split into two clusters; that split largely reflected which member of each pair a study listed.
- **C4 (multi-copy):** up at light onset (28 of 45 defined cells), under CO2 limitation (19/31), nitrogen stress (50/112), iron starvation (7/27) and phage infection (14/74). Down when stress was relieved (iron re-added 7/9; air vs time 0 7/11). Unchanged in phosphate, salt and phage-in-the-dark experiments.
- **C2 (single-copy):** responded mainly in schedule extension (11 of 28 cells up); rarely to stress (nitrogen 10/88) or light onset (1/35).
- **Robustness:** cluster membership held for 16 of 23 genes under a correlation distance and 19 of 23 without the light-onset arrays. C2's membership was the least stable.

**Conservation (exploratory).** The four *hli* genes whose ortholog groups span high- and low-light *Prochlorococcus*, *Synechococcus* and *Cyanobium* were the least responsive: median 2% of stress and light-onset calls up, 7% on RNA-seq alone. Genes in *Prochlorococcus*-wide groups (all multi-copy) had a median of 32% up, 37% on RNA-seq. Two *Prochlorococcus*-only single-copy genes (PMM1317, TX50_RS09730) were also quiet. Conservation here is confounded with copy number, and the pattern was noticed after clustering.

**Background light.** *hli* induction strength correlated with the background light of the study (Spearman ρ = 0.46, p = 0.015). Ribosomal-protein repression correlated similarly (ρ = 0.48, p = 0.05). The 28 tests come from 15 experiments at 7 light levels, so the p-values are pseudo-replicated. Cells were acclimated to that light, and each comparison is against a control at the same light. We therefore do not read light level as a driver of the *hli* response.

## Discussion

## References
