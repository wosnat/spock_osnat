# Proposal: hli genes — light response or general stress response?

**Mode:** exploratory. Every result is labelled exploratory. Ideas that emerge become suggested follow-up analyses.
**Purpose:** standalone result, for the researcher.
**Time budget:** about one day.
**Status:** agreed in the Plan dialog (see `decisions_log.md`); awaiting review and approval.

## Question

For the high-light-inducible (hli) genes of *Prochlorococcus* MED4:
1. Do they respond to light?
2. Or is their response a general stress response, unrelated to light?

A quick check in other cyanobacterial strains, using the same method, gives a broader picture.

## What the KG holds (MED4)

- **hli genes:** 23. They are the MED4 members of the 14 curated Cyanorak hli ortholog groups. Gene name, product and ortholog group all agree on the same 23.
- **Experiments:** 29 transcript experiments (14 microarray, 15 RNA-seq) from 13 studies. All proteomics are dropped.
  - **Light (10):** six 45-min light shifts vs dark (white, high white, blue, red, green, and white + DCMU vs white); constant dark vs constant light, with and without phage; extended light past dusk; extended darkness past dawn.
  - **Non-light stress (13):** nitrogen (4), CO2 (3), phage (3), iron (1), phosphorus (1), salt (1).
  - **Non-stress (6):** coculture with *Alteromonas* (2), urea or cyanate as sole nitrogen source (2), iron re-added after starvation (1), air-sparged vs time 0 (1).
- The light experiments compare light with *darkness*. No usable experiment compares high with normal light.
- Already looked at before this plan: hli results in the six light microarrays, constant dark (phage), and extended light. Also seen: how many hli genes were significant (direction not shown) in the significant-only tables for CO2, iron, phosphorus, phage, iron re-added and air vs time 0.

## Approach

1. **One test per experiment × time point × direction.** A Fisher over-representation test asks whether hli genes are over-represented among the genes that went up, and separately among those that went down. The package's `fisher_ora` is used with our own gene list; no test is hand-written. p-values are corrected (Benjamini–Hochberg) across all tests. The experiment's own significance calls are used as published. Fold changes are never compared across platforms.
2. **Background by table type:**
   - Full table: the genes measured in that experiment.
   - Significant-only table: run twice. Once with the whole genome as background (generous) and once with only the genes in the table (strict). Labelled approximate.
   - Top-N or expression-filtered table (the N-depleted RNA-seq): no test, description only.
3. **Light direction:** experiments where darkness is the treatment (extended darkness, constant dark) are read as "less light". In the summary they are turned around so that every light comparison reads as "more light vs less light".
4. **Too few changes:** if fewer than 20 genes in the genome are significant in a direction, that test is reported as "too few changed genes to tell", not as "not enriched".
5. **Comparison gene sets**, tested the same way in every experiment:
   - **Chaperones** (Cyanorak D.4, 13 genes): expected up in most stresses.
   - **Oxidative stress** (Cyanorak D.1.4, 25 genes): expected up in many stresses.
   - **Photosystem II** (Cyanorak J.8, 31 genes): expected to follow light; often down in nutrient stress.
   - **Random gene sets:** 200 sets of 23 genes drawn from each experiment's background. Expected enriched in about 5% of tests.
   - The Cyanorak "Adaptation > Light" category is not used: it contains the hli genes themselves.
6. **Combining:**
   - An experiment counts as "hli up" if hli is enriched up at any of its time points.
   - A stress type is read by study, not by assay: one study with several assays counts once, by majority.
   - A descriptive label per stress type and overall (light-linked / broad stress / changes in nearly everything / mixed) summarises the pattern. It is not a test.
7. **Gene level:** each hli gene's call (up / down / not changed / not measured) in each experiment × time point. Near-identical paralogs may cross-hybridise on arrays or lose multi-mapping RNA-seq reads, so gene-level calls are read with that caveat.

## Deliverables

1. **MED4 heatmap:** the 23 hli genes × experiment-time points, grouped light / non-light stress / non-stress. A top band shows the set-level enrichment for hli and each comparison set.
2. **MED4 enrichment table:** every test, with both backgrounds where they apply, plus the "too few changes" flag.
3. **MED4 summary:** per stress type, by study, with the descriptive label.
4. **Other strains (quick look):** the same method on strains with at least three stress types in the KG (candidates MIT9313, NATL2A, MIT9312, SS120, WH8102; confirmed at the methods milestone). It uses the same Cyanorak hli groups and comparison categories, and shows a set-level heatmap per strain.
5. HTML reports per milestone, `paper.md` and `overview.html`.

## Run phase

- **Methods:** a small module that builds the gene sets, the test grid, the backgrounds and the light orientation. It is toy-tested on hand-computed data, and the test grid is spot-checked against `pathway_enrichment` on one experiment. The comparison sets are run first, to confirm they behave as expected before hli is shown.
- **Analysis:** the MED4 deliverables, then the other strains.
- **Evaluation:** read the pattern; place each finding against the other KG experiments that bear on it; caveats; paper.

## Known limits

- No usable excess-light (high vs normal light) contrast in MED4. Light evidence is light vs dark.
- Most non-light stress types (CO2, phage, iron, phosphorus) have only significant-only tables, so their tests are approximate.
- hli coverage is incomplete in RNA-seq (15–22 of 23 measured), probably because reads that map to several near-identical copies are lost.
- Background light differs between experiments (10–60 µmol photons m⁻² s⁻¹), which may shift baseline hli levels.
