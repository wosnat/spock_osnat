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
- **lowN series labels** now say "vs the same culture in exponential growth (day 11), PRO99-lowN". *Superseded by A.12: the axenic series' reference is its own day 7 (separate repeat run), per the KG design_notes; the coculture-vs-axenic labels now name axenic day 7 / day 14.*
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
  - **The old C2/C4 split was largely a twin artifact.** All 4 pairs re-joined, and PMM1384 and PMM1385 moved with them. C2 membership is not robust to correlation distance: PMM1390, TX50_RS09730, PMM0689, PMM0690 and PMM1128 join C4 there.
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
  - 18 distinct values each repeat ≥10 times (403 genes; e.g. −8.234 ×31), the signature of zero or near-zero counts in one arm.
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
  | Other non-stress / relief (after A.8) | 13/40 | 14/40 | 3/34 | 0/34 |

  This supersedes the earlier A table and the earlier "Iron: only C4" line.

## Explore (researcher question): how conserved are the hli ortholog groups? (`scripts/15_og_conservation.py`, `data/og_conservation.csv`)

The KG holds 123 organisms. In these 14 groups the organism counts reach at most 43 *Prochlorococcus*, 50 *Synechococcus* and 3 *Cyanobium*.

- **Core picocyanobacterial (95–96 organisms):** CK_00000050 (PMM0093), CK_00001058 (PMM1482), CK_00001414 (PMM0471) and CK_00001313 (PMM0064). Each is present in 42–43 *Prochlorococcus*, 50 *Synechococcus* and 3 *Cyanobium*. All four are single-copy in MED4, and all sit in cluster C2 (the quiet / schedule group).
- CK_00002025 and CK_00002026 are multi-copy in MED4 (3 each), in clusters C4 and C3.
- **Prochlorococcus-wide (42–43 organisms, HL and LL clades):** CK_00002025 and CK_00002026.
- **Prochlorococcus, partial:** CK_00002661, CK_00002332, CK_00002168 and CK_00003573. These are patchy across both HL and LL (HL 12–23, LL 7–14).
- **HL Prochlorococcus only (21–23 organisms, `n_pro_LL` = 0):** CK_00002103, CK_00043616, CK_00003510 and CK_00003421. Clade comes from the KG `organism.clade` field. (Corrected: an earlier version of this entry inferred HL from strain names.)
- **Pattern:** the 4 picocyanobacteria-wide hli (all single-copy) respond little to stress, as do 2 of the *Prochlorococcus*-only single-copy genes (PMM1317, TX50_RS09730). The broad stress responders (C4) are in *Prochlorococcus*-specific, expanded multi-copy groups. Conservation is confounded with copy number and with array coding (see Run 8). [KG counts; the link to response is exploratory]

## Run 8 (kg-coder): A.8 drop coculture 2016; A.9 conservation strip and D5

- **A.8, how it is applied:** `display_overrides.DROPPED`. Part A CSVs are unchanged, and their rows are marked "dropped" in the tables.
- **Headline counts on summary.html:**
  - experiments 29 → 28;
  - tests 138 → 136 (testable 64 → 62);
  - significant tests up 16, down 5 → 4;
  - experiment calls 13 up / 4 down / 8 neither / 4 not tested → 13 / 3 / 8 / 4.
- **Clusters:** every gene keeps its cluster; robustness is unchanged (16/23, 19/23).
- **Light level:** hli up ρ = 0.455 (p = 0.015); ribosomal down ρ = 0.483 (p = 0.0496). Same reading as before: no hli-specific light-level signal.
- **Not updated:** the twin-collapsed ORA files (`hli_tests_twin_collapsed.csv`, `twin_collapsed_comparison*.csv`) still hold the 2016 rows. They are a sensitivity record and are not marked.
- **A.9:** a grey 4-tier ortholog-group breadth strip, using the KG `organism.clade` field, on D1, D2/D3 companions and D4. New figure D5 (`explore_D5_conservation.csv`).
- **D5 read-off** (% of defined stress + light-onset cells called up; `explore_D5_conservation.csv`):
  - the 4 picocyanobacteria-wide single-copy genes are at 0–2% up;
  - 17 of the 19 genes in *Prochlorococcus*-only groups are at 16–44% up. PMM1317 (2%) and TX50_RS09730 (6%) are as quiet as the core genes;
  - % down is at most 17%, and highest in the conserved genes.
  - Exploratory; seen after clustering. **Confounded:** tier 1 is all single-copy and tier 2 all multi-copy. Most of the core genes' quiet cells are ns-by-absence in significant-only arrays. The twin rule shrinks twin-gene denominators. The tiers are partly circular with the clustering. RNA-seq-only medians per tier (`explore_D5_tier_medians.csv`, % up): tier 1 6.7, tier 2 36.7, tiers 3–4 22.2. The ordering holds on RNA-seq, where absence is not coded ns.

## Run 9 (kg-coder): delta-critic fixes D3, D4, D9

- **Twin rule** restricted to microarray tables: 50 cells recoded. No gene changes cluster; robustness is unchanged (16/23, 19/23).
- **Collapsed ORA**, microarray only, coculture 2016 excluded: 20 → 20 significant tests. No test call and no experiment call changes. Phage array 1 h up stays significant (k 9 → 5, padj 1.0e-6). The earlier "extended light 16 h lost" came from collapsing distinct RNA-seq signals and is withdrawn.
- **BH without coculture 2016** (`qc_A8_bh_recompute.csv`): 0 call flips across 806 tests and 364 experiment calls. The footnote is on summary.html.
- **D5 per-tier medians** (% up): tier 1 is 2.4 pooled, 6.7 on RNA-seq and 0 on arrays; tier 2 is 32.0, 36.7 and 34.6. The quiet-conserved pattern holds on RNA-seq alone.

## Decide-gate checklist (analysis milestone)

- [x] Part A deliverables: enrichment table, hli heatmaps, set bands, per-experiment calls, light readings, aggregate by scope (`reports/summary.html`, `hli_heatmaps.html`, `aggregate.html`, `light_readings.html`).
- [x] Explorations the researcher asked for: A families, B and B2 light level, C timing, D clusters (D1–D4), D5 conservation (`reports/explore.html`). All are labelled exploratory.
- [x] Every number comes from a script in `scripts/`, its output in `data/` and its figure in `figures/`. KG calls go through the API with truncation asserted.
- [x] Locus tags are used in all tables.
- [x] Critical review: first pass had 2 Blockers and 8 Concerns, all fixed. Delta pass had 0 Blockers; 4 Concerns and 4 Notes were fixed, and 1 Note (padj after A.8) got a footnote and a no-flip check. See `critical_review.md`.
- [x] Researcher design facts and decisions A.3–A.9 are recorded in `decisions_log.md`.
- [x] `paper.md` Methods and Results are written; `paper.html` is rendered.
- [x] `gaps_and_friction.md` is updated (KG culture-state gaps; the clade pitfall).
- [x] **Researcher approval** (2026-11-18). Delta critic pass 2: no Blocker; Concerns E1–E5 and Notes E8–E10 deferred to the evaluation paper rewrite (critical_review.md).

## Run 10 (kg-coder): exploration E, diel cycle (A.10), and HL vs LL proteomics (A.11)

- **Zinser 2009 diel microarray:** the KG has no expression rows (gene_count 0), so no time series is available.
- **Waldbauer 2012 diel metrics:** cover 312 cycling genes, none of them hli.
- **Zinser Mfuzz diel clusters:** 18 of 23 hli genes are assigned (`explore_E_hli_diel.csv`).
  - The multi-copy C4 genes sit mostly in diel cluster 10 (6 genes; no phase stated in the KG) and cluster 8 (PMM1384, PMM1385; "21.0 h, night").
  - The single-copy C2 genes are spread over 6 diel clusters (stated phases 12.5–22.4 h).
  - In each twin pair exactly one member is clustered, consistent with one shared array signal.
  - The KG's phase origin ("h after onset of dark") contradicts the clusters' own day-part labels, so phases are not placed on a light/dark axis.
- **Reading (exploratory, weak):** the stress-responsive multi-copy genes share one diel pattern; the single-copy genes have diverse diel timing. The phase of the shared C4 pattern is not stated in the KG.
- **Pandhal 2007 iTRAQ** (HL 100 / ML 60 vs LL 20 µE; acclimated; ~179 proteins): no hli protein quantified. Fewer than 10 significant proteins per direction, so no test was run. This check cannot inform question 1.

- **Paper figures reorganised (researcher feedback).** Fig. 3 is now the full clustered call heatmap (all 60 experiment × time-point rows; was Fig. S1), because the per-time-point view shows the co-induced multi-copy block more clearly than the group-aggregated split cells. Fig. 4 is a per-gene bar chart of % up grouped by ortholog-group breadth (replaces the breadth scatter, which was hard to read); RNA-seq-only medians stay in the text. Light level moves to Fig. 5; S1 removed. Label and layout only; no number changed (`paper_fig_source_fig4.csv` tier medians: 2.4 / 32.0 / 20.3 / 19.5 % up).
- **Paper Results restructured (researcher feedback): one grouping, three views.** Order is now set level (light onset, stresses) → which genes (responders = C3+C4, quiet = C1+C2; cluster, copy number and ortholog breadth as views of one split; Table 1 from `24_paper_gene_groups.py`) → timing → light level. Figures renumbered: 2 = call heatmap, 3 = conservation bars, 4 = timing. Corrected the stale phage count (was "14 of 74"; the file gives 14 of 195 defined up-calls for the responders, 14 of 169 for C4).
- **Phosphate coverage (researcher question).** Martiny 2006 table = 34 genes with q < 0.05 at 48 h, reported at all 5 time points. hli: PMM1482 only (ns 0–24 h, down at 48 h, padj 0.049); the other 22 are ns at 48 h by the filter and NaN at 0–24 h (K0 in Fig. 2). Paper wording changed from "no response to phosphate" to the 48 h-only statement.
- **A.13: phosphate dropped.** Pipeline rerun with phosphate in `display_overrides.DROPPED`. Gene clusters: 0 changes. Columns 60 → 55 (K0: 5 → 1, phage array 1 h only). Robustness: correlation 16/23 (unchanged), without Steglich 21/23 (was 19). Table 1 medians: responders 29% (RNA-seq 27%), quiet 2.5% (7%); tier medians 2.5 / 33 / 21 / 20%. Light level: hli up ρ = 0.49, p = 0.010, 27 tests / 13 experiments / 6 levels; ribosomal down unchanged (0.48, 0.05). `18_check_A8_bh.py`: 0 flips. Script 08 count assertion 17 → 16.
- **Fig 2/3 redesign (researcher feedback).** Fig 2 rows now sorted by family → condition → experiment → time (not by column clustering); columns grouped responders | quiet with a header bracket; ortholog breadth shown as an organism-count bar per gene (replaces the 4 similar greys); copy number labelled beside its row. Table 1 replaced by Fig 3: (a) each gene on the ortholog-breadth axis by group, filled = multi-copy; (b) % of defined calls up (down for relief) per condition, responders vs quiet, from `paper_table1_condition_counts.csv`. The per-gene conservation bar chart is dropped (too detailed); tier medians stay in the text. All figure code is in `20_paper_figures.py` (run after `24_paper_gene_groups.py`).
- **Fig 2 refinements (researcher feedback).** Conservation bar stacked HL Pro / LL Pro / Synechococcus+Cyanobium (from explore_D5_conservation.csv; source `paper_fig_source_fig2_conservation.csv`), labelled "conserved in (no. of genomes)". Row labels split into experiment (named once) and time columns; experiment separators added; family labels beside the strips.
- **Fig 2 KG reference lines (researcher request).** `15_og_conservation.py` now also writes `kg_organism_categories.csv` (KG genome strains: 25 HL Pro, 20 LL Pro, 53 Synechococcus, 3 Cyanobium = 101 picocyanobacteria; og_conservation.csv unchanged). Fig 2 conservation bars carry dotted lines at 25 / 45 / 101. No hli group reaches all 25 HL genomes (max 23).
- **Exploration F: do KG annotations separate responders from quiet genes? (researcher question; `25_explore_annotations.py`, `explore_F_*.csv`).** Descriptive, n = 15 vs 8, no correction.
  - 17 ontologies registered; the 23 genes carry cyanorak_role and tigr_role (23/23), GO BP/CC (21), Pfam and COG (17), InterPro (6), localization (5); nothing in GO MF, EC, KEGG, etc.
  - **No annotation term separates the groups** (all p ≥ 0.11). Shared by all 23: Cyanorak D.1.2 Light, J Photosynthesis/respiration, "Stress response and adaptation". Pfam PF00504 (Chl a/b-binding) on 12/15 vs 5/8; HliA-D-like PF31213 on 3 vs 2; GO missing only on 2 quiet genes (PMM0471, TX50_RS09730).
  - Protein length: no difference (median 46 vs 58 aa; 48.5 vs 58 with identical copies collapsed, p = 0.42).
  - What differs is genomic layout, which restates copy number: 12/15 responders sit next to another hli gene (tandem blocks PMM0815–0818, PMM1396–1399; pairs PMM0689/0690, PMM1384/1385) vs 0/8 quiet; 10/15 responders have an identical-sequence copy vs 0/8.
  - Charged-residue (DEKR) fraction is lower in responders (median 0.14 vs 0.22, p = 0.006; with identical copies collapsed 0.15 vs 0.22, p = 0.037, 10 vs 8 proteins) — one of ~15 features tested, uncorrected: weak.
  - Expression-derived 'data coverage' rows (e.g. high-light-shock metrics on 11 responders, 0 quiet) are circular and not used.
- **Paper: neighbourhood and domains added (researcher request).** Results grouping now lists four views (pattern, copy number, ortholog breadth, genomic arrangement), plus one sentence that annotations do not separate the groups; Background describes the 23 genes from KG annotations (PF00504 on 17, PF31213 on 5 of those, 6 unannotated; 12 adjacent to another hli gene; 5 identical pairs); Methods says how these were collected. Background counts corrected to 27 comparisons / 10 publications after A.13.
