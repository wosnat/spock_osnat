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
- **Resemblance:** hli is significant in light onset, CO2, iron, nitrogen and phage (light), and in non-stress (2 up, 3 down). No reference set responds in light onset; the specific sets respond only in their own stress.

## Explore (main thread) — first look, provisional

- **Light onset:** hli is the only set that goes up. 8–11 of the 11 hli genes in the Steglich table are up, at 5–8 CK groups.
- **Breadth:** hli is up in 4 of the 6 non-light stress types (CO2, Fe, N, phage), with no stress-type down call. It goes down in two relief or return contrasts (iron re-added; air vs time 0) and in coculture 2016. It is up in urea and cyanate, which are N-source changes, not starvation.
- **Not up:** salt, phosphate at 48 h, phage lysate in either light condition, constant dark vs light at set level.
- **Schedule extension at gene level** (`hli_gene_calls.csv`) splits by family:
  - **Multi-copy cluster genes** (CK_00002168/2025/2026/43616, e.g. PMM1118, PMM1399, PMM1390, PMM1398, PMM1385, PMM0818) are up in extended darkness (2 h/4 h) and down in extended light (14 h/16 h). In both experiments they are higher in the *dark* arm: a light-linked difference in the reverse direction to light onset.
  - **Single-copy genes PMM0064 and PMM0093** are up in both arms: a schedule-type response.
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

The single-copy genes respond less, and differently.

**B. Light level (cross-study, confounded):**
- hli up strength rises with background light: Spearman ρ = 0.49 (p = 0.007; 29 tests, 15 experiments, 7 distinct light levels).
- hli down shows no relation.
- Ribosomal up tends the other way (ρ = −0.34, p = 0.07).

The light levels are tied to study, platform and stress type, so this is suggestive only.

## Run 3 (kg-coder): B2, continuous light only (researcher request)

- **Scope:** the 18 non-light-reading experiments, all asserted to be continuous light with equal light in both arms. They are ordered by light level: 10, 17.5, 20, 27, 30, 50, 55, 60 and 90 µmol.
- **New figures:** gene heatmap, set band and call grid (`explore_B2_*`), plus an interactive section B2 in `explore.html`.
- **Other changes:** the B1 subtitle overlap is fixed (data byte-identical). No values were recomputed.

## Run 4 (kg-coder): D, hli response groups (researcher request)

- **Value:** published call (+1 / 0 / −1; NaN = not measured / not testable). Fold change and rank were rejected: they are not comparable across platforms and are missing in significant-only tables. Gene distance = 1 − agreement over shared cells (≥10); average linkage; K = 4 (cut 0.205). 61 columns (Lindell 2–8 h all-NaN and pooled "days 60+89" dropped).
- **Clusters:**
  - C1: 5 single-copy genes (PMM0064, PMM0093, PMM0471, PMM1317, PMM1482). Up mainly at schedule extension and light onset, otherwise quiet or down.
  - C2: 9 genes, mixed. Up in nitrogen limitation (47% of cells).
  - C3: 2 genes (PMM0689, PMM0690). Up in N and CO2.
  - C4: 7 multi-copy genes. Up at light onset, CO2 (71%), N (42%), iron (33%) and phage 1 h; down in extended light and in iron re-added / air vs time 0 / constant dark.
- **Robustness:** correlation distance agrees for 12/23 genes (it merges C2–C4); dropping the Steglich columns agrees for 18/23. C1 versus the rest is the stable split; C2/C3/C4 boundaries are soft.
- **Caveat:** all of C4 is multi-copy and 4 members share a CK group, so cross-hybridisation or multi-mapping may contribute.
- **D2/D3:** small multiples vs time (log h) and vs light level, coloured by stress type with hover. 8 timepoint labels are not times (CO2 "max across", steady state, acclimated, rescue), so carbon and salt are absent from D2.
- **Anomaly:** coculture 2016 20 h has hli log2FC down to −14 (median −5), including some genes called ns at padj 1. This dominates the y range.
