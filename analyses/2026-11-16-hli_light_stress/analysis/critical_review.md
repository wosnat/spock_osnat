# Analysis milestone: critical review (data-integrity + interpretation)

Reviewer: `critic`, cold read of analysis/. Trusted inputs: proposal, decisions_log, methods/, spike/.

**Confirmed by the reviewer's recount:**
- experiment calls 13 up / 4 down / 8 neither / 4 not tested;
- light-onset gene counts;
- timing percentages;
- clustering robustness (12/23 and 18/23);
- column clusters;
- the 18 B2 experiments;
- the summary.html run facts;
- the Spearman values.

**Verdict:** the set-level breadth result stands. The problems are in the per-gene and cluster reading. Two Blockers.

| # | Severity | Finding | Main-thread check | Proposed disposition |
|---|---|---|---|---|
| 1 | Blocker | **Paralog twins.** Four multi-copy pairs (PMM0818/PMM1399, PMM1397/PMM0816, PMM1396/PMM0815, PMM0817/PMM1398) have identical log2FC wherever both are reported on some platforms, i.e. one signal under two loci. In significant-only array tables (Steglich, CO2, iron, iron re-added, DCMU) only one twin is listed; the other is coded `ns`. In each pair, one twin is in C4 and the other in C2. So the C2/C4 split, "iron: only C4" and "C4 up at light onset" partly reflect which twin the study annotated. | **Confirmed** (`hli_gene_calls.csv`). Each pair is identical in 9 of 13–18 shared cells: the Lindell phage array at every time point, plus salt or coculture 2016. They differ in the RNA-seq extended light/dark and N-depleted tables. When one twin is missing, it is `absent_from_significant_only_table` in 12–14 cells per pair. | **Fix.** Twin rule: in a significant-only array table where one twin is listed and the other is absent, code the absent twin NaN ("shared signal, reported under partner"), not `ns`. Rerun D (clusters, D2/D3) and A (families) under this rule. Re-read C2 vs C4. |
| 2 | Concern | The phage-array set-level hit counts 9 genes, but they are about 5 independent signals (the twins). | Follows from 1. | **Fix.** Sensitivity rerun of the hli set test on array tables with each twin pair counted once. Report whether each up call survives. Caveat it in the notebook. |
| 3 | Blocker | Notebook: "No reference set responds in light onset". Photosystem I goes down in 2 of 6 light-onset tests (`resemblance.csv`). | Accept | **Fix wording:** "no reference set goes up at light onset; PSI goes down in 2 of 6". |
| 4 | Concern | The notebook A table is stale since the Run-6 overrides. Day 18 "N stress, control side" (down = higher under stress) is pooled into the nitrogen scope, mixing opposite meanings. | Accept | **Fix.** Give day 18 its own scope in A. Refresh the table from the file. |
| 5 | Concern | Extended-darkness gene list is wrong. PMM1390 is single-copy. CK_00002025 members PMM1404 and PMM0690 go down, and CK_00043616 members are ns. | Accept | **Fix.** List the genes actually up (PMM1118, PMM1399, PMM1384, PMM1385, PMM1398, PMM0818). Say the pattern is not group-wide. |
| 6 | Concern | The C1 "schedule extension" claim rests mostly on extended light 16 h, which is flagged genome-wide. PMM0064 and PMM0093 are ns at 14 h. | Accept | **Fix.** Name the flag and soften the C1 wording. |
| 7 | Concern | "C1 never up in a time course" is wrong: PMM0093 at lowN day 60 and PMM1317 at N-depleted 3 h. Also, C4 is 17% up at N-deprivation 24 h. | Accept | **Fix wording.** |
| 8 | Concern | C3 is 70% up at light onset; the notebook omits it. | Accept | **Fix wording** (rechecked after rule 1). |
| 9 | Concern | Light-level ρ = 0.49 is pseudo-replicated (29 tests, 15 experiments, 7 levels). The omitted ribosomal-down ρ = +0.52 (p = 0.03) suggests stronger responses overall at the higher-light studies. | Accept | **Fix.** Report the ribosomal-down ρ. State n = 15 studies / 7 levels. Read B as no hli-specific light-level signal. |
| 10 | Note | Coculture 2016 down call is cited without its anomaly (82% of log2FC negative; hli down to −14). | Accept | **Fix.** Cross-reference the anomaly. |
| 11 | Note | "Columns group by response, not experiment" has no null baseline. | Accept | **Soften** to "columns mix experiments". |
| 12 | Note | Day 18 percentages rest on 2–5 defined genes. | Accept | **Fix.** Show counts next to percentages. |
