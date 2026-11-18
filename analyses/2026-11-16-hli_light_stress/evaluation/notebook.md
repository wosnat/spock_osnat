# Evaluation milestone: notebook

## Co-define (agreed with the researcher, 2026-11-18)
1. **Discussion** in paper.md answering the two questions, built on the responder / quiet split (researcher: "refer to the hli subgroups" = responders vs quiet).
2. **Caveats in one place:** platforms; significant-only tables; paralog twins; exploratory labels; 2025 coculture separate axenic run (batch); dropped experiments (A.8, A.13); conservation confounded with copy number.
3. **Source-study comparison:** what each source publication says about hli in the KG vs our calls, as agrees / disagrees / can't tell.
4. **Smooth the paper:** prose pass, consistent terms, captions; the two "[ref needed]" claims go to the researcher.
5. **Carried over from the analysis delta review (critical_review.md E1–E5, E8–E10):** name the intermediate genes PMM1128 and PMM1390; give the two-group robustness (20/23, 21/23) and the genes that move; recast the "four views" as one correlated genomic feature with the probe and co-transcription circularity stated; schedule-extension exceptions, and drop schedule extension from Fig 3b; state the batch caveat; BH-family sentence; uncorrected-screen wording for exploration F; exploratory labels on timing and light level; time-course method in Methods.
6. Interpretation-only critic, then the decide gate, then approval; then ask about the push.

## Log
- Fig 3b: schedule-extension bar removed (review E4). Pooled up-calls mixed opposite light meanings.
- Paper rewrite part 1 (review E1–E5, E8–E10): grouping recast as one genomic feature with circularity stated; intermediate genes PMM1128 (N 6/14, LO 2/5) and PMM1390 (N 7/14) named — 13 of the quiet group's 16 N up-calls; two-group robustness 20/23 (corr.: PMM1128, PMM1390, TX50_RS09730 join responders; PMM1482 forms its own cluster) and 21/23 (no Steglich: PMM1390, TX50_RS09730); schedule-extension exceptions; batch caveat; BH-family sentence; uncorrected-screen wording; exploratory labels; time-course method in Methods.
- Source comparison (`evaluation/scripts/01_source_comparison.py`, `evaluation/data/source_comparison*.csv`): KG hli statements for 6 of 10 analysed studies (Steglich, Tolonen, Lindell [phage's own hli], Thompson 2011, Bagby, Thompson 2016); none for Read, He, Weissberg, Johnson. Main-thread readings: agree (Steglich induced genes, Steglich constitutive genes, Thompson 2011 PMM1404, Bagby air/CO2), partly agree (Steglich modest/minor; magnitude not in our calls), agree at set level (Tolonen; statement spread over 10 genes), agree at gene level (Thompson 2016: 4 responders higher in light at 0.5 h with phage), not comparable (Lindell). Independent support for the quiet group: Steglich's 'constitutively expressed' hli genes map in the KG to PMM0064, PMM0093, PMM0471 and PMM1390, all quiet.
- Discussion written: Q1 (yes, specific; change in light, not level; DCMU down hints redox signal [interpretation]); Q2 (broad, but every inducing stress was in the light; the only dark stress (phage lysate) lacks the 0.5 h point, so no test; light/sink-imbalance reading [interpretation]; follow-up = stress in darkness); two kinds of hli genes; comparison table; caveats; follow-ups.
- Background citations (A.14): He 2001 (Synechocystis hli mutants die in high light; Hli up in high light and N limitation, some in S deprivation and cold), Havaux 2003 (heat dissipation), Bhaya 2002 (MED4 >2x hli genes, recent duplications), Lindell 2004 (phage hli group with Pro multi-copy types). Venue of Havaux 2003 (BBA 1557:21–33) from bibliographic record; confirm if needed.
- Evaluation critic: 2 Blockers (V1 change-vs-level claim; V2 non-independent Steglich support) and 8 Concerns, all wording; all fixed in the Discussion rewrite (evaluation/critical_review.md). Delta pass next.

## Decide gate
- [x] Discussion answers both questions at the strength the data allow (Q1: responds to a shift into light, steady light level open; Q2: broad, not shown to be unrelated to light).
- [x] Responders vs quiet carried through (researcher request); boundary genes and circularity stated.
- [x] Source-study comparison in a table, re-reading not replication stated; script and data in evaluation/.
- [x] Caveats in one list; exploratory labels in Results and Discussion.
- [x] Background citations from web search (A.14), listed separately; no "[ref needed]" left.
- [x] Interpretation critic run, plus a delta pass: Blockers V1 and V2 fixed; delta W1–W6 fixed (critical_review.md).
- [x] paper.html and index.html rebuilt; all code in the repo.
- [x] **Researcher approval** (2026-11-18).
