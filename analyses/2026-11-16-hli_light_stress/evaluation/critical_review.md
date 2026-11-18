# Evaluation milestone: critical review (interpretation only)

Reviewer: `critic`, cold read of paper.md (Discussion) and evaluation/. Trusted inputs: proposal, decisions_log, methods/, analysis/, evaluation/data.

**Verdict:** the set-level results and the cautious answer to Q2 hold up. Two conclusions reached past the evidence.

| # | Severity | Finding | Disposition |
|---|---|---|---|
| V1 | Blocker | "Responds to a change in light rather than light level" is not supported. Constant dark vs light = light-to-dark transfer run on separate days, with tiny significant-only tables; at gene level 4 responders were lower in the dark (0.5 h, infected), which the paper's own table scores as agreeing with Thompson 2016. Fig 5 does not measure light level within a study. The KG has no steady light-level contrast with hli measured (A.11). | **Fixed:** conclusion dropped. Q1 now says hli respond to a shift into light; dependence on steady light level is open. Constant-dark and light-level evidence described as what it is. |
| V2 | Blocker | Steglich "constitutive" support for the quiet group is not independent: it is the same arrays, which also feed the clustering. PMM1390 is strongly N-induced (Tolonen) and sits on the group boundary. | **Fixed:** "independently" removed. The row now reads "Consistent (same data)"; the Discussion states the circularity and PMM1390. |
| V3 | Concern | Schedule-extension reversal (responders higher in the dark arm) is missing from Q1. | **Fixed:** added to Q1 with the genome-wide flag and [interpretation] explanations (time-of-day gating, dawn response passed). |
| V4 | Concern | Steglich operon row omits linked PMM1317 (quiet, KG name "hli6") and treats PMM0815 as ns. | **Fixed:** all linked genes listed; PMM0815 shares PMM1396's probe; reading now "Mostly agrees". Added to the source-comparison caveat. |
| V5 | Concern | "Our calls carry no magnitude" is wrong: PMM0689 log2FC 1.0–3.4. | **Fixed:** magnitudes given (checked in hli_gene_calls.csv: 2.04, 3.45, 1.00; PMM1128 1.26, 1.96); reading "Partly disagrees (PMM0689), or a gene-mapping problem". |
| V6 | Concern | Bagby: the air-vs-t0 drop is recovery from handling stress; low-CO2 "up" partly means failure to recover. | **Fixed:** stated in Q2, the table and the caveats; "air was supplied" removed from relief. |
| V7 | Concern | Time-course features are presented as "fitting" the sink reading but do not discriminate it from a general stress response; phage brevity argues against it; alternatives (oxidative, handling, phage transcription) unnamed. | **Fixed:** "consistent with … equally with a general stress response", one bullet per feature, alternatives named. |
| V8 | Concern | The conserved genes "hardly changed" is wrong: they carry the most down-calls (PMM1482 down under low CO2, N deprivation 6/12 h, extended darkness). | **Fixed:** "rarely induced, but carry the most down-calls" (checked in hli_gene_calls.csv). |
| V9 | Concern | "New readings" for studies without KG statements is a novelty claim the KG cannot support. | **Fixed:** "the knowledge graph records no statement … we have not checked the papers themselves". |
| V10 | Concern | Missing caveats: re-reading not replication; dark/light separate days; Bagby t0; light onset = dark-to-dim shift; no steady light-level contrast; urea/cyanate induce; Steglich statement spreading. | **Fixed:** all added. |
| V11 | Note | Light-onset and DCMU results were seen during planning. | **Fixed:** stated in Q1 and the caveats. |
| V12 | Note | Tolonen's "hli10" might be PMM1390 (unverified; the KG lacks the numbering). | Left as is; the row already says we cannot tell which three. Numbering gap logged earlier (gaps_and_friction.md). |
| V13 | Note | Q2 conclusion strength is right. | No change. |
| V14 | Note | Follow-up "stress in darkness" would not separate the readings, since darkness stops growth. | **Fixed:** follow-up 1 now crosses stress with two or more acclimated light intensities; follow-up 2 added for steady light level. |
