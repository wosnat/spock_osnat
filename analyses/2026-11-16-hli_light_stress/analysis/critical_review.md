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

## Researcher decisions on the first pass

- #1, #2: approved and fixed (Run 7).
- #10: coculture 2016 dropped (A.8).
- All other findings fixed as proposed.

## Delta pass (data-integrity + interpretation)

No Blocker. The pass confirmed against the files:
- twin pairs and the 54 recoded cells;
- that the rule code touches only the one-twin-listed case;
- new cluster membership and robustness;
- the Run 7 per-cluster counts;
- collapsed ORA 21 → 19;
- the summary.html headline counts;
- the coculture 2016 facts;
- conservation tiers vs the KG clade field.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| D1 | Concern | D5 read-off "15–45%" is wrong for PMM1317 (2%) and TX50_RS09730 (6%); the "Pattern" line overstates. | **Fixed wording.** |
| D2 | Concern | "Conserved = quiet" is confounded with copy number, with ns-by-absence in significant-only arrays, with twin-shrunk denominators, and with the clustering itself. | **Fixed.** Caveat added. RNA-seq-only and array-only % per gene added to D5; the tier ordering holds on RNA-seq. |
| D3 | Concern | The twin rule was applied to 2 RNA-seq tables (pone.0165375) where twins differ. | **Fixed:** rule restricted to microarray tables; 50 cells recoded; no cluster change. |
| D4 | Concern | Collapsed ORA merged pairs in RNA-seq tables where they differ, so "extended light 16 h lost" is not a fair twin result. | **Fixed:** collapse restricted to microarray tables; 20 → 20 significant, no call changes. |
| D5 | Concern | A-table non-stress row was pre-A.8. | **Fixed:** 13/40, 14/40 \| 3/34, 0/34. |
| D6 | Note | "C2/C4 split was a twin artifact" is too strong; C2 is not robust to correlation distance. | **Fixed wording.** |
| D7 | Note | Repeated-value counts misquoted. | **Fixed:** 18 values ≥10 times, 403 genes. |
| D8 | Note | "HL plus some LL" should be "patchy across HL and LL". | **Fixed.** |
| D9 | Note | padj not recomputed after A.8. | **Fixed:** footnote added; 0 flips (`qc_A8_bh_recompute.csv`). |

## Delta pass 2 (data-integrity + interpretation): commits 15e5e08..d955db2

Scope: A.10–A.13, explorations E and F, the restructured paper Results (groups, Figs 2–3), and the Background and Methods edits. No Blocker. The reviewer re-derived every paper number it checked, and all of them matched the files: condition counts, group and tier medians, robustness 16 and 21, light-level ρ, 27 comparisons from 10 publications, 55 rows, domain and arrangement counts, and the 25/45/101 genome totals. A.12 matches the KG design_notes; A.13 is applied consistently.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| E1 | Concern | The "quiet" group holds two responsive genes: PMM1128 (20% up, 40% on RNA-seq; N 6/14) and PMM1390 (17.5%). The groups overlap on % up (quiet 0–20, responders 16.7–45). | **Deferred to evaluation** (paper rewrite): name PMM1128 and PMM1390 as intermediate and drop "rarely / mostly do not" for the whole group. |
| E2 | Concern | The robustness failures cross the responder/quiet line. Correlation distance moves PMM1128, PMM1390 and TX50_RS09730 to responders; without Steglich, PMM1390 and TX50_RS09730 move. Two-group agreement is 20/23 and 21/23. | **Deferred to evaluation**: report the two-group agreement, name the movers, soften "divide the genes in almost the same way". |
| E3 | Concern | The "four views" are not independent. Twin pairs share array probes, tandem blocks are likely co-transcribed, and identical-copy status is a subset of multi-copy by definition. | **Deferred to evaluation**: recast as one genomic feature (multi-copy, often tandem, Pro-restricted) that correlates with the clustering, with the circularity stated. |
| E4 | Concern | Schedule extension does not split by group: 6/13 responders follow the pattern, PMM0690 and PMM1404 go the opposite way, and quiet PMM1390 follows it. Pooled up-calls mix opposite light meanings (Fig 3b). | **Deferred to evaluation**: reword "explain" as "help read" and give the exceptions; split or drop schedule extension in Fig 3b. |
| E5 | Concern | The 2025 coculture batch confound (separate axenic run) is not stated as a caveat; "ran out of nitrogen" is an inference. | **Deferred to evaluation** (caveats section and Methods wording). |
| E6 | Note | The dark-phage claim ignored PMM0689 (2/6 down). | **Fixed:** "rarely in the dark-phage experiment (2 of 45 calls down, both PMM0689)". |
| E7 | Note | "11 hli genes on the array" should be "listed in the study's table". | **Fixed.** |
| E8 | Note | `qc_A8_bh_recompute.csv` labels were stale; BH family includes dropped tables. | **Fixed:** script 18 rerun (0 flips). Methods sentence deferred to evaluation. |
| E9 | Note | Exploration F: the paper reports the null length result but not the nominal charged-fraction hit; the "Light" role is near-tautological. | **Deferred to evaluation** (report both as an uncorrected screen, or drop). |
| E10 | Note | The timing and light-level Results sections are not labelled exploratory, and the time-course method is missing from Methods. | **Deferred to evaluation.** |
| E11 | Note | The Exploration E diel "shared pattern" partly reflects shared probes. | Notebook only; not used in the paper. Qualify if promoted. |

Researcher approved the analysis milestone on 2026-11-18. The deferred items are the first tasks of the evaluation milestone.
