# Methods milestone — notebook

## Co-define (agreed with the researcher, 2026-11-16)

1. Build the gene and experiment list. The 29 MED4 transcript experiments carry: group, table type, time points, the light orientation, and the background light level of each arm (parsed to a number).
2. Toy-test the scoring on hand-computed examples: Fisher p, backgrounds, light flip, flags, Bonferroni within experiment, BH per gene set.
3. Write the KG-based scripts using the API, and test them step by step on photosystem II:
   - check the direction of the extended light and extended darkness contrasts;
   - check one experiment against `pathway_enrichment`;
   - check whether the KG holds per-platform gene lists for backgrounds.
4. Run the comparison sets (chaperones, oxidative stress, photosystem II) and the size-matched random sets across all experiments. Check the flag counts against `proposal.md` Known limits.
5. Produce a report (summary + comparison-set checks), followed by the critic (data-integrity + interpretation) and the researcher's approval.

No hli results are produced or shown in this milestone.

## Run 1 (kg-coder), 2026-11-16 — run-manifest summary

- **Tests:** 21 toy tests pass. `fisher_ora` matches `scipy` on a hand case (p = 0.162023). The pipeline matches `pathway_enrichment` on the N-deprivation microarray (20 tests, max |Δp| 8.2e-17).
- **Platform backgrounds:** the KG holds no per-platform gene lists. Significant-only tables use the MED4 genome (1973 genes), marked `genome_assumption`.
- **Test grid:** 138 experiment × timepoint × direction tests. 66 are testable; 57 too_few, 5 genome-wide (>30%), 8 not_testable (Lindell down), 14 descriptive (N-depleted top-50%; phosphate non-48h).
- **Flags vs proposal:** every too_few listed in Known limits matches. Seven more full-table tests are too_few (N-deprivation 0h/3h, coculture 2025 day 11 down, cyanate down, urea down).
- **Phosphate:** treated as descriptive at 0/4/12/24 h, because the table is filtered on q < 0.05 at 48 h. Known limits had implied 24 h up was testable; the kg-coder rule is the correct one (a gene significant only at 24 h would be missing).
- **Comparison sets (BH padj < 0.05, 66 testable tests each):**
  - chaperones 0 (raw p < 0.05 in 5; 3 of them up);
  - oxidative stress 0 (raw p < 0.05 in 3; 1 up);
  - photosystem II 5 (4 down: low CO2, N deprivation 48 h, lowN axenic day 14, lowN coculture day 60; 1 up: coculture vs axenic day 18).
- **Random size-matched sets:** raw p < 0.05 in 2.6% of testable tests. Fisher on discrete counts is conservative.
- **PSII direction check:**
  - consistent with light → PSII up for extended light 14 h (4 up / 0 down) and high white light (4 / 0);
  - extended darkness 2 h raw is 12 up / 6 down (darkness vs light), i.e. PSII lower with more light;
  - 16 h and 4 h are balanced.

  KG design notes say the stored log2FC reproduce the same-time-of-day contrast (r = 1.00), so the sign convention itself is documented.
- **Incident:** a probe script printed one hli DE row (extended light 14 h, PMM1404) to the coder's console. It was not saved, and this contrast was already seen during planning.
- **Gene sets:** PMM0211 (trxB) is in both chaperones and oxidative stress; neither overlaps hli.
- **Reports:** `reports/summary.html` and `reports/controls.html` render (checked by screenshot).

## Explore — what the controls show (main thread)

- **The general-stress references do not behave as general-stress references.** Chaperones and oxidative stress are never significant after correction, and their nominal hits go up and down. They cannot show "what a general stress gene looks like" in these data, so the planned contrast "hli vs general-stress references" is uninformative as designed. This needs a decision before the analysis.
- **Photosystem II behaves as expected for nutrient stress** (down in N and CO2 limitation). Its light response is mixed in the photoperiod contrasts.
- **The random-set rate (2.6%) is below 5%,** so the test is not anti-conservative.

## Decide-in-progress (researcher, 2026-11-16)

- **Reference sets replaced.** Nine Cyanorak categories are added as references:
  - broad stress: ribosomal proteins K.2, protein folding L.3, protein degradation L.4;
  - stress-specific: N D.1.3, P D.1.5, Fe D.1.1;
  - light-specific: D.1.2 minus hli;
  - photosynthesis: photosystem I J.7, CO2 fixation J.2, with photosystem II kept.

  Chaperones and oxidative stress are kept only as reported failed references.
- **Purpose:** hli is read by which reference pattern it resembles (broad, specific, light). References are kept or reported as failed by how they behave in the controls (no hli involved).

## Run 2 (kg-coder), 2026-11-16 — reference sets

- **12 sets.** Sizes: K.2 61, L.3 28, L.4 23, D.1.3 16, D.1.5 31, D.1.1 30, D.1.2 minus hli 12 (all 23 hli were inside D.1.2), J.7 17, J.2 22, J.8 31, D.4 13, D.1.4 25. Overlaps are listed in `data/gene_set_overlaps.csv`; none involves hli.
- **Outputs:** `data/reference_behaviour.csv` (130 rows). Random sets unchanged (2.6%). Flags unchanged. pytest: 21 pass.

## Explore — reference behaviour (main thread, checked against `control_tests.csv`)

Testable tests with BH padj < 0.05:

- **Specific sets work.**
  - Fe: up at 3 of 4 iron-starvation tests (12, 24, 48 h); 0 in other non-light stresses. It also moves in the iron re-added and extended-light 16 h (genome-wide) tests.
  - P: up at its only testable test (48 h, padj 4e-7); 0 elsewhere.
  - N: up at 2 of 20 nitrogen tests (N deprivation 6 h and 12 h); 0 in other stresses. It is also up in air vs time 0 and coculture day 11 (both non-stress). Weak but specific.
- **Ribosomal proteins (broad, growth).**
  - Down in 7 of 38 non-light stress tests: CO2 ×2, N deprivation 6/12/24 h, lowN axenic day 14, phage lysate in the light 8.5 h.
  - Up in 4: extended light 16 h, lowN coculture day 31, phage array 1 h, coculture 2025 day 18.
  - Tracks growth in both directions; the only broad reference that responds at all.
- **Failed (never padj < 0.05):** protein folding L.3, protein degradation L.4, chaperones D.4, oxidative stress D.1.4. Light-adaptation-minus-hli has 0 in the light group and 1 down in nitrogen.
- **Light group (16 testable tests):**
  - no reference responds consistently;
  - PSI: 2 up, 4 down;
  - CO2 fixation: 2 up, 2 down;
  - PSII and ribosomal proteins: 0 and 1.

  There is no clean "light pattern" to compare hli against. The light reading will rest on hli's own enrichment vs the random baseline.

## Researcher requests (2026-11-16): code review, spot checks, keep light-minus-hli

- **Light minus hli:** kept as the light-specific reference (researcher), even though it had no significant tests in the light group.
- **Independent spot checks (main thread):** `scripts/07_spot_checks_independent.py` → `data/spot_checks_independent.csv`. The script does not import the pipeline module. It uses the KG API and scipy only.
  - **Fisher tests (6):** Fe in iron starvation 12 h; ribosomal proteins in N deprivation 12 h and salt; P at 48 h; PSII in extended darkness 2 h, including the orientation flip; light-minus-hli in N deprivation 48 h. Every background size, set size, total-significant count, set-significant count and p-value matches.
  - **Flags (4):** too_few, genome_wide_response, no flag, descriptive. All computed from the thresholds, and all match.
  - **Per-experiment Bonferroni aggregate (1):** from independently computed time-point p-values. Matches (1.558e-30, testable at 4 time points).

  ALL MATCH. The genome size of 1973 is confirmed from the organism record.
- **Code review** (code-review skill, high, over methods/):
  - **Most findings were in the first version of 07:** checks that re-read the pipeline's own flags, results not saved, a hard-coded genome size, an incomplete match, dead code. All fixed in the version above.
  - **Pipeline findings, sent to kg-coder:**
    - the "NA" timepoint label is read back as NaN (latent);
    - the dark/range regexes in light parsing could misread arm text (latent; the current 29 are unaffected per the reviewer);
    - the set list is duplicated across scripts.
  - **The reviewer also flagged that 07 runs KG queries on the main thread.** Kept deliberately: an independent check has to be written outside the coder's code. The researcher asked for spot checks.

## Run 3 (kg-coder): code-review fixes

- **Fixes:**
  - null timepoints are labelled "single" (no row was affected);
  - `is_dark_arm()` replaces the "dark" regex, and a midpoint is taken only for true ranges;
  - the set list is derived from `kg_io.REFERENCE_SETS`.
- **Checks:** pytest 38 passed (21 before). All 14 data CSVs are byte-identical to run 2; `git status` shows no data file changed.

## Decisions after the methods review (researcher, 2026-11-16)

- **All critic dispositions accepted** (`critical_review.md`).
- **No light flip (changes proposal Approach 4).** Every result is reported as treatment vs control, as stored. Each experiment carries `more_light_arm` and a `light_reading_group`. Reason: the critic showed the extended light and extended darkness experiments move the references the same raw way, so a flip turns a consistent off-schedule signal into an apparent contradiction.
- **Light reading rules, fixed before hli is opened:**
  - **light onset** (Steglich, treatment lit): up = up with light;
  - **constant dark vs light** (control lit): down = up with light;
  - **schedule extension** (extended light: treatment lit; extended darkness: control lit): the same raw direction in both = schedule-extension response, not light; opposite raw directions = light response;
  - **DCMU:** electron-transport effect at constant light;
  - **phage in the dark:** up = phage response without light.
- **"days 60+89"** (pooled) becomes descriptive.
- **Wording of the references:**
  - Fe responds in iron (3 of 4, approximate);
  - P responds at its only testable test;
  - N responds weakly and not specifically (2/20 in nitrogen vs 2/11 in non-stress);
  - light-minus-hli is kept but did not respond in the light tests;
  - ribosomal proteins are down in N/CO2 limitation and up in some coculture/recovery contrasts.
- **Random-set baseline:** calibrates independent-gene sets only.

## Run 4 (kg-coder): review dispositions, no flip, detailed labels

- **Outputs:**
  - orientation removed;
  - `more_light_arm` and `light_reading_group` added (light onset 5, constant dark vs light 2, schedule extension 2, DCMU 1, phage dark 1, none 18);
  - `label_detailed` for the 11 light-reading experiments, built from KG arm text;
  - "days 60+89" made descriptive;
  - `share_sig_both_directions` added;
  - `gene_calls_from_background()` (absent genes in significant-only tables count as ns);
  - time-point labels filled;
  - `schedule_extension_concordance.csv` (48 rows).
- **Effects:** testable tests 66 → 64; test-level BH hits 61 → 60 (only the dropped pooled test); no experiment-level call changed. The random-set rate is 2.7% (the seeded stream shifted).
- **Checks (main thread re-run):** 07 independent spot checks ALL MATCH; pytest 40 passed.
- **Schedule-extension concordance confirms the critic's point (raw treatment vs control):**
  - **PSI** is up in both experiments: extended darkness 2 h 14/17 (padj 2.7e-5) and 4 h 15/17; extended light 14 h 4/17 and 16 h 13/17 (padj 7.8e-4).
  - **CO2 fixation** is down in both: extended darkness 14/21 and 15/21; extended light 5/21 and 13/21; all padj < 0.014.

  The lit arm is opposite in the two experiments, so these references respond to being off-schedule, not to light. The reading rule for hli in this group is fixed above.

## Corrections after the delta review (2026-11-16): these supersede earlier numbers in this notebook

The delta critic found no Blocker. It confirmed:
- `more_light_arm` is correct for all 29 experiments;
- the labels are faithful to the KG arm text;
- the pooled time point is out of both BH and Bonferroni;
- the concordance table matches `control_tests.csv` exactly.

Earlier sections of this notebook (Run 1/2 "Explore") were written with the light flip and with "days 60+89" included. The current, raw (treatment vs control) numbers are:
- **N set:** up at 2 of **18** testable nitrogen tests (not 20). It is also up in 2 of 11 non-stress tests, so it is weak and not specific.
- **Ribosomal proteins:** down in 7 of **36** non-light stress tests (not 38). Up in 4 contrasts: two coculture (lowN coculture day 31, coculture vs axenic day 18), extended light 16 h, and phage array 1 h. None is a recovery contrast; "recovery" is withdrawn.
- **The "light group" counts in Run 2** (PSI 2 up/4 down, CO2 fixation 2/2, PSII 0) were oriented. **Pooled light-group counts are not read for direction**, because the lit arm differs between experiments. References are read per light reading group (`reference_behaviour.csv` scope `light_reading_group`).
- **The PSII sign-check line "including the orientation flip"** refers to the earlier pipeline; no flip exists now.
- **The schedule-extension reading holds on the unflagged contrasts alone:**
  - extended darkness 2 h: PSI up padj 2.7e-5; CO2 fixation down padj 7.8e-4;
  - extended light 14 h: PSI up padj 0.017; CO2 fixation down padj 0.0026.

  Extended darkness 4 h and extended light 16 h are flagged genome-wide response (both-direction share 0.67 and 0.62).
- **Rule for hli in schedule extension (fixed now, before hli is opened):** the reading is made on the unflagged pair (extended darkness 2 h, extended light 14 h). The flagged pair (4 h, 16 h) is shown as supporting context only.
- **Background caveat:** the extended light and extended darkness KG tables hold 1876 genes, while the study reports about 1920 detected. The full-table background is the 1876 the KG holds.
- **Deferred to the analysis milestone:**
  - wire `gene_calls_from_background()` into the ortholog-group counts;
  - report `n_groups_down` as n/a for the up-only Lindell table.
