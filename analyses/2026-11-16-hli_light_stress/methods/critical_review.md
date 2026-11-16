# Methods milestone — critical review (data-integrity + interpretation)

Reviewer: `critic`, cold read of methods/. Blinding kept: no hli results computed.

**Verdict, summarised:**
- **Data artifacts sound.** Every count quoted in notebook.md and summary.html matches the CSVs, and BH reproduces to about 2e-15.
- **Pipeline correct.** Orientation, backgrounds, flags, the phosphate rule, the in-table unions and the random-set sizing are all correct.
- **Interpretive layer over-reaches** in places.
- **No Blocker.** The photoperiod point and "days 60+89" should be settled before the analysis.

Dispositions are proposed and await the researcher's choice.

| # | Severity | Finding | Proposed disposition |
|---|---|---|---|
| 1 | Concern | **Photoperiod experiments respond in the same *raw* direction in both extended light and extended darkness.** Main thread verified in `control_tests.csv`: PSI up 14/15 (dark 2/4 h) and 4/13 (light 14/16 h); CO2 fixation down 14/15 and 5/13. The −1 flip turns this into opposite oriented calls, so "no clean light pattern" hides a consistent "off-schedule" response, not a light response. hli in these two experiments would be read as "mixed" by construction. | **Accept.** Treat the two photoperiod experiments as a separate reading, "schedule extension", next to "light onset" (Steglich) and "constant dark vs light". Reading rule, fixed before hli is opened: hli moving the same raw way in both = schedule-extension response, not light; hli moving opposite raw ways (same oriented direction) = light response. Record the reference concordance in the notebook. |
| 2 | Concern | **"days 60+89" in the lowN coculture experiment is a pooled time point duplicating day 60 and day 89.** It enters the BH family and the per-experiment Bonferroni (n testable 5 instead of 4). | **Accept.** Drop "days 60+89" from testing (keep it descriptive) and rerun. |
| 3 | Concern | **"Specific sets work" is not earned for N.** N: 2/20 own-stress tests vs 2/11 non-stress. P rests on 1 test. Fe hits are all approximate, and Fe shares 3 genes with PSI and light-minus-hli. | **Accept.** Reword: "Fe responds in iron (3 of 4, approximate); P responds at its only testable test; N responds weakly and not specifically". |
| 4 | Concern | **Light-minus-hli** has 0 hits in the 16 light tests but is labelled light_specific. "Ribosomal tracks growth" is inferred, not measured. | **Accept** (keeping the set, per researcher). Label it "kept, non-responsive in light tests"; hli is never read as "resembling the light reference". Reword ribosomal as "down in N/CO2 limitation; up in some coculture/recovery contrasts". |
| 5 | Note | The random-set baseline uses independent genes, so it does not calibrate correlated sets (operons, hli paralogs). | **Accept.** Limit the statement; the ortholog-group count stays next to every hli test. |
| 6 | Note | The genome-wide flag is per direction, so contrasts with about 50–60% of genes significant across both directions go unflagged (extended darkness 2 h; coculture day 18; lowN axenic day 14 up). | **Accept.** Add the total share (both directions) as a column in the enrichment table. |
| 7 | Note | `ortholog_group_counts` treats genes absent from significant-only tables as "not measured"; the plan says "not significant". | **Accept.** Build gene calls from the main background before the hli run, and add a toy test. |
| 8 | Note | `experiments.csv` `timepoints` is blank for single-time-point experiments. The photoperiod KG tables hold 1876 genes, while the paper reports 1920 detected. | **Accept.** Fill the labels from the DE rows; mention 1876 vs 1920 in the background caveat. |
