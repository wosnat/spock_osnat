# Proposal: hli genes — light response or broad stress response?

**Mode:** exploratory. Every result is labelled exploratory. Ideas that emerge become suggested follow-up analyses.
**Purpose:** standalone result, for the researcher.
**Time budget:** about one day.
**Status:** agreed in the Plan dialog (see `decisions_log.md`). Revised after the proposal review (`proposal_critical_review.md`); awaiting the delta review and approval.

## Question

For the high-light-inducible (hli) genes of *Prochlorococcus* MED4:
1. Do they respond to light? In this KG that means light onset and photoperiod, not excess light (see Known limits).
2. Do they respond across non-light stresses, or only to light? Where the KG allows, is that response independent of light?

A quick check in other cyanobacterial strains, using the same method, gives a broader picture across stresses.

**What the KG can and cannot show.** All but one of the non-light stress experiments were run in the light. Nutrient or CO2 limitation leaves the cell less able to use the light it absorbs, so the same light becomes relatively excessive. If hli goes up under those stresses, that is "induced across stresses", not "unrelated to light". In MED4, only two contrasts bear directly on light-independence:
- **Phage in the dark:** phage lysate vs spent medium, both arms in constant darkness (Thompson 2016). It sits beside the same comparison in the light. If hli goes up in the dark experiment, the phage-linked hli response does not need light; if it goes up only in the light experiment, it may.
- **DCMU:** DCMU + light vs light. DCMU blocks photosystem II electron transport, and both arms get the same light.

Both are small significant-only tables, and at the "too few changes" threshold almost all of their tests are flagged (see Known limits). In practice they will be read from the gene-level hli calls, not from set-level tests. Both get their own rows.

## What the KG holds (MED4)

- **hli genes:** 23. They are the MED4 members of the 14 curated Cyanorak hli ortholog groups. Gene name, product and ortholog group all agree on the same 23.
- **Experiments:** 29 transcript experiments (14 microarray, 15 RNA-seq) from 13 studies. All proteomics are dropped.
  - **Light onset / photoperiod (9):**
    - five 45-min light shifts vs one shared 5-h dark control (white 13, high white 55, blue, red, green; Steglich 2006, one table of genes significant in any of the six conditions);
    - constant dark vs constant light, with and without phage (arms run on separate days);
    - extended light past dusk; extended darkness past dawn (same time-of-day controls, cells on a 12:12 cycle).
  - **Photosynthetic electron transport (1):** DCMU + white light vs white light (Steglich 2006).
  - **Phage in the dark (1):** phage lysate vs spent medium in constant darkness (light-independence check, own row).
  - **Non-light stress (12):** nitrogen (4), CO2 (3), phage in the light (2), iron (1), phosphorus (1), salt (1).
    - The two phage experiments are Lindell 2007 (microarray; an up-only table with mixed control timing) and Thompson 2016 (lysate vs spent medium in the light).
    - All twelve were run in the light, at 10–60 µmol photons m⁻² s⁻¹.
  - **Non-stress / possible stress relief (6):** coculture with *Alteromonas* (2), urea or cyanate as sole nitrogen source (2), iron re-added after starvation (1), air-sparged vs time 0 (1). These show whether hli changes in nearly every comparison, including ones that are not stresses. They are not a clean negative control.
- Already looked at before this plan: hli results in the six Steglich microarrays, constant dark with phage, and extended light. Also seen: how many hli genes were significant (direction not shown) in the significant-only tables for CO2, iron, phosphorus, phage, iron re-added and air vs time 0.

## Approach

1. **One test per experiment × time point × direction.** A Fisher over-representation test asks whether hli genes are over-represented among the genes that went up, and separately among those that went down. The package's `fisher_ora` is used with our own gene list. The experiment's own significance calls are used as published. Fold changes are never compared across platforms.
2. **Correcting for many tests:** Benjamini–Hochberg separately for each gene set (hli, each comparison set). The random sets are outside every correction family.
3. **Background by table type:**
   - **Full table:** the genes measured in that experiment.
   - **Significant-only table:** a gene missing from the table counts as "not significant".
     - Main background: the genes on the platform (array features or genes detected by RNA-seq), if the KG holds them. Otherwise the whole genome, marked as an assumption.
     - For "significant in any condition" tables (Steglich, CO2), the platform background is near-exact. A second run with only the in-table genes is shown as a sensitivity check; it is biased against genes that respond in every condition.
     - All significant-only tests are labelled approximate.
   - **Up-only table:** the down tests are "not testable". The phage microarray table (Lindell 2007) is up-only according to the KG.
   - **Top-N or expression-filtered table** (the N-depleted RNA-seq): no test, description only.
4. **Light orientation:** where darkness is the treatment (extended darkness, constant dark), the contrast is turned around so that every light-onset/photoperiod comparison reads "more light vs less light". DCMU is not turned around; it has its own row. Before any hli result is read, the direction convention of the extended light/dark contrasts is checked on photosystem II genes.
5. **Too few changes:** if fewer than **10** genes in the genome are significant in a direction at a time point, that test is reported as "too few changed genes to tell", with the gene-level hli calls shown instead. Before running, the number of tests this flags in each group is counted from genome-wide counts. The stress types left with no testable contrast are listed in Known limits.
6. **Genome-wide response flag:** if more than **30%** of measured genes are significant in a direction at a time point, the Fisher test is still run and reported. Fisher already compares the hli share with the background share. The test is flagged "genome-wide response (>30%)", and the hli share is shown next to the genome-wide share, so the reader can see why a real but partial hli response may not reach significance there. This applies, for example, to extended light and extended darkness.
7. **Comparison gene sets**, tested the same way in every experiment:
   - **Chaperones** (Cyanorak D.4, 13 genes) and **oxidative stress** (Cyanorak D.1.4, 25 genes): general-stress references. They are themselves light/redox-responsive.
   - **Photosystem II** (Cyanorak J.8, 31 genes): expected to follow light; often down in nutrient stress.
   - **Random gene sets:** 200 per test, each the same size as the number of hli genes measured in that table and drawn from the same background. Expected enriched in about 5% of tests.
   - The Cyanorak "Adaptation > Light" category is not used: it contains the hli genes themselves.
   - **References uninformative** is a flag on the comparison column, not a label for the stress type. If the general-stress references are not enriched up in a non-light stress test, that test carries the flag, and the hli reading is kept beside it. The flag applies only to non-light stress tests that are not already flagged "too few changes".
8. **Paralog correlation:** hli copies are near-identical, so their calls are not independent and the Fisher p-values overstate the evidence. Next to every gene-level test, a count at the level of the 14 ortholog groups is shown (a group counts as changed if any member changes).
9. **Combining:**
   - Per experiment, both of these are reported:
     - significant time points out of the total, per direction (e.g. "up at 3 of 6, down at 0 of 6");
     - one aggregate call per direction. The smallest time-point p-value is multiplied by the number of testable time points (Bonferroni within the experiment), so experiments with many time points do not get extra chances. BH correction is then applied across experiments within each gene set, and the call is "up" / "down" / "both" / "neither".
   - The six Steglich conditions are shown side by side, not combined; the wavelength and DCMU pattern is the point.
   - Across studies within a stress type: by study, not by assay.
   - A descriptive label per stress type summarises the pattern; it is not a test. The labels are:
     - "light-onset responsive";
     - "induced across stresses (light-dependence not tested)";
     - "hli changes in nearly every comparison" (including the non-stress group);
     - "mixed";
     - "too few changes" (no testable contrast in that group; gene-level calls only).

     The flags ("references uninformative", "genome-wide response (>30%)", "approximate", "not testable") travel next to the label and never replace it.
10. **Gene level:** each hli gene's call (up / down / not changed / not measured) in each experiment × time point. Near-identical paralogs may cross-hybridise on arrays or lose multi-mapping RNA-seq reads, so gene-level calls are read with that caveat.

## Deliverables

1. **MED4 heatmap:** the 23 hli genes × experiment-time points, grouped by light onset / photoperiod, electron transport (DCMU), phage in the dark, non-light stress, and non-stress / possible relief. A top band shows the set-level result for hli and each comparison set.
2. **MED4 enrichment table:** every test, its background(s), the ortholog-group count, and its flags (too few / genome-wide response / not testable / approximate / references uninformative).
3. **MED4 summary:** per stress type, by study, with the descriptive label and time-point counts.
4. **Other strains (quick look, breadth across stresses only):** the same method, using the same Cyanorak hli groups and comparison categories, on:
   - strains with at least three stress types in the KG (candidates MIT9313, NATL2A, MIT9312, SS120, WH8102; confirmed in methods);
   - the NATL2A extended-darkness experiments;
   - **MIT0604 UV shock** (all genes measured), as a named check and the closest the KG has to an excess-light test. The MIT0604 hli set is its 15 curated-group members plus EW14_RS05945 (hli by product, in an eggNOG hli group, with no curated group), 16 genes in all.
5. HTML reports per milestone, `paper.md` and `overview.html`.

## Run phase

- **Methods:** a small module that builds:
  - the gene sets;
  - the test grid, with the backgrounds (platform gene lists checked);
  - the light orientation (sign checked on photosystem II);
  - the flags, the ortholog-group counts and the random sets.

  The module is toy-tested on hand-computed data, and the test grid is spot-checked against `pathway_enrichment` on one experiment. The flag counts and the comparison sets are run first, before any hli result is shown.
- **Analysis:** the MED4 deliverables, then the other strains.
- **Evaluation:** read the pattern; place each finding against the other KG experiments that bear on it; caveats; paper.

## Known limits

- **No excess light:** there is no usable high vs normal light contrast in MED4. The MED4 light data are light onset (45 min after 5 h dark) and photoperiod (extended light or darkness at the same time of day in 12:12-entrained cells). hli are known to follow the day–night cycle.
- **All non-light stresses but one were run in the light**, so a response across stresses cannot show independence from light. Only the phage-in-the-dark experiment and DCMU bear on that, and both are read at gene level only (next item).
- **Separate days:** the constant dark vs constant light arms were run on separate days from separate mother cultures, so day and culture effects are mixed into the light effect.
- **Timescales differ:** 45 min for light onset, versus hours to weeks for nutrient stress. A short-lived hli response may be missed in the long stress series.
- **Approximate tests:** most non-light stress types (CO2, phage, iron, phosphorus) have only significant-only tables.
- **"Too few changes" (fewer than 10 genes in the genome significant in that direction), from the KG's genome-wide counts:**
  - **Light onset:** green light, both directions (1 up / 1 down). Red light and white light 13, down only (3 down each).
  - **DCMU:** both directions (2 up / 7 down). Gene level only.
  - **Phage in the dark:** all tests except 4.5 h down (13 down). Gene level only.
  - **Phage in the light (lysate vs spent medium):** all tests except 8.5 h down (11 down).
  - **Constant dark vs light:** all tests except 8.5 h down (no phage 26; with phage 25).
  - **Phage microarray (up-only):** 6 h and 8 h up (7 and 6). Down is not testable.
  - **Iron starvation:** down at 12 h and 24 h (3 each).
  - **Phosphate:** up at 0, 4 and 12 h; down at every time point.
  - **CO2, ambient CO2 without O2:** both directions (4 up / 0 down).
  - **No stress type is left with no testable contrast at all,** but the light-independence checks rest on single tests or on gene-level calls.
- **Incomplete hli coverage in RNA-seq** (15–22 of 23 measured), probably because reads that map to several near-identical copies are lost.
- **Background light differs** between experiments (10–60 µmol photons m⁻² s⁻¹).
- **Inflated p-values:** paralog correlation inflates set-level Fisher p-values (see Approach 8).
