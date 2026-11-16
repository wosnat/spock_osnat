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
