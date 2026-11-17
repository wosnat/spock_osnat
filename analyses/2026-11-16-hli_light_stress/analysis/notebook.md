# Analysis milestone — notebook

## Co-define (researcher, 2026-11-16)

- **Part A only for now (MED4).** Score hli in the 29 experiments with the approved methods pipeline:
  - tests, flags, both backgrounds;
  - ortholog-group (14 families) counts using `gene_calls_from_background`; `n_groups_down` is n/a for the up-only Lindell table;
  - random baseline.
- **Outputs:**
  - gene-level heatmap and set-level band (hli next to all reference sets), also ordered by light level;
  - per-experiment and per-stress summary with the fixed light reading rules;
  - which reference hli resembles.
- **HTML report**, plus a graphic of the aggregated results for hli and all control categories.
- **Then exploration** (directions to be agreed on seeing the results).
- **Part B (other strains):** later.
- **Mode:** all results exploratory.

## Run 1 (kg-coder): part A scored — run-manifest summary

- **Setup:** the approved methods module was imported unchanged.
- **QC:**
  - BH recompute (statsmodels) Δ = 0;
  - the reference rows are identical to the methods run;
  - random draws are identical;
  - no truncation, duplicates or both-direction genes;
  - every full DE table has both signs.
- **hli coverage:** 23 in significant-only tables (genome background; Steglich tables hold 11, so the other 12 count as ns); 15–22 in full tables.
- **Experiment calls for hli** (29 experiments; main thread recounted from `experiment_calls.csv`): up 13, down 4, neither 8, not tested 4.
  - **Up:**
    - light onset: blue, high white, red, white;
    - CO2 low ×2;
    - iron starvation;
    - N deprivation array, lowN axenic, lowN coculture;
    - phage infection array;
    - cyanate; urea.
  - **Down:** extended light, air vs time 0, coculture 2016, iron re-added.
  - **Neither:** extended darkness, constant dark ×2, salt, phage lysate in the light, phosphate (48 h), coculture 2025, phage lysate in the dark.
- **Light readings (mechanical):**
  - light onset: up with light in 4 of 4 testable (green untestable);
  - constant dark vs light: too few, or no set-level change;
  - schedule extension, reading pair (dark 2 h neither, light 14 h down): "unclear" by rule;
  - DCMU: 3 hli down, gene level only;
  - phage in the dark: 1 gene down.
- **Resemblance:** hli is significant in light onset, CO2, iron, nitrogen and phage (light), and in non-stress (2 up, 3 down). No reference set goes up at light onset; photosystem I goes down in 2 of 6 light-onset tests (`resemblance.csv`; corrected after the critical review). The specific sets respond only in their own stress.

## Explore (main thread) — first look, provisional

- **Light onset:** hli is the only set that goes up. 8–11 of the 11 hli genes in the Steglich table are up, at 5–8 CK groups.
- **Breadth:** hli is up in 4 of the 6 non-light stress types (CO2, Fe, N, phage), with no stress-type down call. It goes down in two relief or return contrasts (iron re-added; air vs time 0) and in coculture 2016. The coculture 2016 table is anomalous: 82% of log2FC values are negative, and hli goes down to −14. It is being re-checked (see Corrections). It is up in urea and cyanate, which are N-source changes, not starvation.
- **Not up:** salt, phosphate at 48 h, phage lysate in either light condition, constant dark vs light at set level.
- **Schedule extension at gene level** (`hli_gene_calls.csv`) splits by family:
  - **Six multi-copy genes** (PMM1118, PMM1399, PMM1384, PMM1385, PMM1398, PMM0818) are up in extended darkness (2 h/4 h) and down in extended light (14 h/16 h). They are higher in the *dark* arm in both experiments: a light-linked difference in the reverse direction to light onset. The pattern is not CK-group-wide: CK_00002025 members PMM1404 and PMM0690 go down in extended darkness, and the CK_00043616 genes are ns. (Corrected after the critical review; PMM1390 had been listed and is single-copy.)
  - **Single-copy genes PMM0064 and PMM0093** are up in extended darkness and in extended light 16 h, but ns at 14 h. The 4 h and 16 h contrasts are flagged genome-wide (>30% of genes significant), so "up in both arms" rests on a flagged time point.
  - **PMM1404, PMM0690 and PMM1482** are down in extended darkness.

  The set-level rule calls the reading pair "unclear" because the gene directions cancel.
- **Alternatives to keep in mind:**
  - Steglich significance is list-based on a filtered table;
  - near-identical paralogs may cross-hybridise;
  - "up in N/CO2/Fe" is consistent with relative excess light under limitation (see Known limits); it is not light-independent.

## Exploration chosen by the researcher (2026-11-16)

- **A. Gene families:** CK group and multi- vs single-copy, across all experiments.
- **B. Light level:** hli response vs background light intensity (cross-study; confounded by platform and design).
- **C. Timing:** in the time series, are hli responses mostly at the start of a stress?
- **Graphics for each;** a new page `reports/explore.html`.

## Run 2 (kg-coder): exploration A/B/C — facts

- **New outputs:** scripts 04–07; `data/explore_*.csv`; figures `explore_A1/A2/B1/C1/C2`; `reports/explore.html`. Existing data are unchanged.
- **Timing:** hli gene-level counts are asserted equal to `hli_gene_calls.csv`.

## Explore — what A/B/C show (main thread, provisional)

**C. Timing: not mostly at the start.** It depends on the stress.
- **Phage (with light):** early and short-lived.
  - Phage infection array: 39% of hli up at 1 h (set-level hit), 0% from 2 h to 8 h.
  - Phage lysate in the light: 22% up at 0.5 h, then 0 (untestable).
  - Constant dark with phage: 30% down at 0.5 h, then 0 (untestable).
- **Nutrient limitation:** builds up and is late.
  - N deprivation: 0% at 0–3 h, 12% at 6 h, 18% at 12 h, 24% at 24 h, 59% at 48 h. Set-level hits at 24 h and 48 h. Ribosomal-protein down peaks earlier (about 12 h), so the hli rise follows the growth shutdown.
  - Iron starvation: 0%, 4%, 26% at 12/24/48 h; hit at 48 h only.
  - N-depleted RNA-seq (descriptive): 5% at 3 h, 71% at 12 h, 73% at 24 h.
  - lowN coculture (vs day 11): 13% at day 18, 53% at day 31, 47% at day 60, 13% at day 89. It rises, then falls.
- **Light onset** is a single 45-min point, so its timing is not resolved.

**A. Families: the multi-copy cluster genes carry most of the response.** Share of measured gene × time observations, multi-copy vs single-copy:

| Scope | Multi-copy | Single-copy |
|---|---|---|
| Light onset up | 46% | 13% |
| CO2 up | 50% | 4% |
| Nitrogen up | 38% | 17% |
| Iron up | 17% | 0% |
| Phage (light) up | 8% | 0% |
| Schedule extension | 17% up / 50% down | 33% up / 14% down |
| Non-stress | 21% up / 33% down | 8% up / 10% down |

The single-copy genes respond less, and differently. [Table stale; superseded pending the twin-rule rerun with day 18 in its own scope: critic #1, #4]

**B. Light level (cross-study, confounded):**
- hli up strength rises with background light: Spearman ρ = 0.49 (p = 0.007; 29 tests, 15 experiments, 7 distinct light levels).
- hli down shows no relation.
- Ribosomal up tends the other way (ρ = −0.34, p = 0.07).
- Ribosomal **down** also rises with light: ρ = +0.52, p = 0.03 (`explore_light_level_spearman.csv`; added after the critical review).

The light levels are tied to study, platform and stress type. The p-values treat 29 tests as independent, but there are only 15 experiments at 7 levels. The ribosomal-down correlation suggests stronger responses overall in the higher-light studies. Reading: no hli-specific light-level signal. (Both arms are acclimated to the same background light, so light level is context, not treatment.)

## Run 3 (kg-coder): B2, continuous light only (researcher request)

- **Scope:** the 18 non-light-reading experiments, all asserted to be continuous light with equal light in both arms. They are ordered by light level: 10, 17.5, 20, 27, 30, 50, 55, 60 and 90 µmol.
- **New figures:** gene heatmap, set band and call grid (`explore_B2_*`), plus an interactive section B2 in `explore.html`.
- **Other changes:** the B1 subtitle overlap is fixed (data byte-identical). No values were recomputed.

## Run 4 (kg-coder): D, hli response groups (researcher request)

- **Value:** published call (+1 / 0 / −1; NaN = not measured / not testable). Fold change and rank were rejected: they are not comparable across platforms and are missing in significant-only tables. Gene distance = 1 − agreement over shared cells (≥10); average linkage; K = 4 (cut 0.205). 61 columns (Lindell 2–8 h all-NaN and pooled "days 60+89" dropped).
- **Clusters:**
  - C1: 5 single-copy genes (PMM0064, PMM0093, PMM0471, PMM1317, PMM1482). Up mainly at schedule extension (extended dark 2–4 h, extended light 16 h); not at light onset; otherwise quiet or down.
  - C2: 9 genes, mixed. Up in nitrogen limitation (47% of cells).
  - C3: 2 genes (PMM0689, PMM0690). Up in N and CO2.
  - C4: 7 multi-copy genes. Up at light onset, CO2 (71%), N (42%), iron (33%) and phage 1 h; down in extended light and in iron re-added / air vs time 0 / constant dark.
- **Robustness:** correlation distance agrees for 12/23 genes (it merges C2–C4); dropping the Steglich columns agrees for 18/23. C1 versus the rest is the stable split; C2/C3/C4 boundaries are soft.
- **Caveat:** all of C4 is multi-copy and 4 members share a CK group, so cross-hybridisation or multi-mapping may contribute.
- **D2/D3:** small multiples vs time (log h) and vs light level, coloured by stress type with hover. 8 timepoint labels are not times (CO2 "max across", steady state, acclimated, rescue), so carbon and salt are absent from D2.
- **Anomaly:** coculture 2016 20 h has hli log2FC down to −14 (median −5), including some genes called ns at padj 1. This dominates the y range.

## Run 5 (kg-coder): D rework (researcher feedback)

- **Column clusters:** agreement distance, average linkage, cut 0.491 → K1–K4 plus K0 (5 sparse columns: phosphate 0–24 h and phage array 1 h, each with <10 defined genes).
  - Adjacent leaf pairs share an experiment in 21.7% of cases, a category in 38.3% and a time label in 8.3%. So the column clusters mix experiments (no permutation baseline was run, so "grouped by response" is not shown).
  - K3 (14 columns) is the "hli up" block: light onset 45 min (red, white, blue, high white), N (6 columns), CO2 (2), urea and cyanate.
  - K4 (38 columns) is the quiet / mixed remainder.
- **Colours:** one scheme across section D, three hue families (light/dark violet, stress green, non-stress brown) with a shade and marker per type. Family anchors pass the validator. Within-family shades fail the normal-vision check, so markers are the secondary encoding. Clusters are shown in ink only.
- **D2 rebuilt:** % of each cluster's genes up/down per time-course experiment (10 experiments) on a fixed −100…+100 axis, plus per-experiment gene × time heatmaps.
- **D3 rebuilt** the same way, against light level. The log2FC spaghetti is removed.
- **Light theme** forced on all analysis reports.
- **Read-off from D2 (`explore_D_cluster_response.csv`):**
  - N deprivation: C3 up from 6 h (100% by 12 h), C2 from 6 h, C4 17% at 24 h and 83% at 48 h.
  - lowN coculture: C4 up from day 18, everything peaks day 31 and falls by day 89.
  - Iron: only C4, rising to 86% at 48 h. [Superseded pending the twin-rule rerun: critic #1]
  - Phage (array and lysate in light): C2/C4 up at the first time point only (1 h / 0.5 h).
  - Phosphate: no up.
  - C1 is rarely up in a time course: one gene at one time point in two experiments (PMM0093 at lowN day 60; PMM1317 at N-depleted 3 h).

## Run 6 (kg-coder): display decisions A.3–A.6

- **How it's applied:** `scripts/display_overrides.py` changes labels and categories at display time only. Part A CSVs are untouched, and no test was recomputed.
- **2025 coculture split:**
  - day 11 → non-stress "coculture, both exponential";
  - day 18 → stress "N stress, control side" (down = higher in the starving control).
- **lowN series labels** now say "vs the same culture in exponential growth (day 11), PRO99-lowN".
- **Day 18 per cluster:**
  - C2, C3 and C4 are 60%, 100% and 67% down, i.e. higher in the starving control.
  - C1 is 40% up (2 of 5: PMM0064 and PMM0471 higher in coculture). C2 is 3 of 5 down, C3 2 of 2, C4 2 of 3.
- **Day 11 per cluster:** C2 20% up, C4 33% up, nothing down.
- **Not updated:**
  - `06_explore_timing.py` was not rerun (the KG is down), so the C labels lack the lowN suffix.
  - `resemblance.csv` and the part A aggregate tables keep the original grouping, with an annotation.

## Run 7 (kg-coder): critic fixes #1–#2, coculture 2016 check, D4

- **Twin pairs:** exactly 4 detected, the ones the critic named: PMM0815/1396, PMM0816/1397, PMM0817/1398, PMM0818/1399. They are identical in the Lindell phage array (8/8) plus salt or coculture 2016, and differ in N-depleted and extended light/dark RNA-seq.
- **Twin rule:** in significant-only tables, the unlisted twin is NaN, not ns. 54 cells recoded (iron 12; Steglich ×6, CO2 ×2, iron re-added 4 each; others 2).
- **Clusters under the rule** (supersede Run 4/5 clusters):
  - C4 = 13 of the 14 multi-copy genes (the 14th, PMM0690, is in C3 with single-copy PMM0689).
  - C2 = 7 single-copy genes (PMM1390, TX50_RS09730, PMM1482, PMM0064, PMM0093, PMM0471, PMM1317).
  - C3 = PMM0689, PMM0690.
  - C1 = PMM1128.
  - **The old C2/C4 split was a twin artifact.**
  - Robustness: correlation distance 16/23 (was 12/23); no-Steglich 19/23 (was 18/23).
- **Per cluster:**
  - C4 is up in alternative N 13/16, light onset 28/45, CO2 19/31, N 50/112, iron 7/27 and phage 14/72. It is down in iron re-added 7/9, air vs t0 7/11 and day-18 control side 4/5 (= higher under stress). It is 0/39 in phage dark, 0/13 in P and 0/13 in salt.
  - C2 (single-copy) is up mainly in schedule extension 11/28; N only 10/88; light onset 1/35.
  - C3 is up at light onset 7/10, N 14/27 and CO2 3/6.
- **Collapsed ORA** (`twin_collapsed_comparison*.csv`): 21 → 19 significant tests.
  - Lost: extended light 16 h down; coculture 2016 down.
  - Coculture 2016 experiment call: down → neither.
  - Phage array 1 h survives (k 9 → 5, padj 1.1e-6). All light-onset, CO2, iron, iron re-added and air tests survive.
- **Coculture 2016 check** (`check_coculture2016_*.csv`; Aharonovich & Sher 2016, RNA-seq Rockhopper, coculture vs Pro99 axenic, 20 h, exponential):
  - 82% of genome log2FC values are negative; median −1.46; 515 genes have |log2FC| > 5.
  - 291 genes with |log2FC| > 5 are called ns at padj ≥ 0.99.
  - Many values repeat exactly (−10.345 and −8.234, ~30 genes each), the signature of zero or near-zero counts in one arm.
  - hli median −4.96 (29.8th genome percentile).
- **D4:** response vs time with all experiments (cluster % panels, point area = n defined; gene panels), deterministic dodge (≤1 point coincides). D3 now uses the same dodge and size encoding.
- **A families refreshed (critic #4).** Day 11 and day 18 of the 2025 coculture have their own scopes. Twin rule applied. Multi-copy has 14 genes in 5 CK groups; single-copy has 9 genes in 9 CK groups.

  | Scope | Multi up | Multi down | Single up | Single down |
  |---|---|---|---|---|
  | Light onset | 32/50 | 0/50 | 6/45 | 0/45 |
  | Schedule extension | 8/48 | 24/48 | 12/36 | 5/36 |
  | CO2 | 21/34 | 0/34 | 1/27 | 2/27 |
  | Nitrogen | 32/84 | 0/84 | 16/93 | 5/93 |
  | Iron | 7/30 | 0/30 | 0/27 | 0/27 |
  | Phage (light) | 14/180 | 0/180 | 0/117 | 0/117 |
  | Constant dark vs light | 0/124 | 7/124 | 0/81 | 0/81 |
  | DCMU | 0/10 | 3/10 | 0/9 | 0/9 |
  | Phage dark | 0/42 | 0/42 | 0/27 | 2/27 |
  | Phosphorus; salt | 0/14; 0/14 | 0; 0 | 0/9; 0/8 | 1/9; 0 |
  | Day 18 (down = higher under stress) | 0/6 | 5/6 | 2/9 | 2/9 |
  | Day 11 (both exponential) | 2/6 | 0/6 | 0/9 | 0/9 |
  | Other non-stress / relief | 13/54 | 19/54 | 3/42 | 4/42 |

  This supersedes the earlier A table and the earlier "Iron: only C4" line.
