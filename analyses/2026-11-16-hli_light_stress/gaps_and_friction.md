# Gaps and friction

- [pitfall] Gene-set counting during Plan step 1 went to `run_cypher` for convenience, although most of it was coverable by tools (`genes_by_function` per organism, `search_homolog_groups` + `genes_by_homolog_group`, `genes_by_ontology`). Counts should be cross-checked with the tools before the seed is frozen. (plan)
- [tool] No tool reports *which field* a text match hit (gene name vs product vs description) — `genes_by_function` searches them together, so "by name" vs "by product" counts need Cypher or post-filtering rows. (plan)
- [tool] `genes_by_ontology` is one organism per call; "which genes in which strains carry InterPro X" across 100 strains needs a loop or Cypher. (plan)
- [kg] ~~Coculture vs axenic (2025): node does not record which arm the growth phase describes or that the axenic control is dying.~~ **Corrected (A.12):** `design_notes` do record it: matched by growth state, not sampling day; the axenic control is a separate repeat run sampled on days 7 and 14; day 11 coculture vs axenic day 7 (both exponential); day 18 coculture vs axenic day 14 (death; axenic MED4 lost viability around day 11). Remaining gap: the per-time-point `growth_phase` (day 18 nutrient_limited) describes the coculture arm only and has no field for the control arm's state, which sits in free text. (analysis)
- [kg] ~~PRO99-lowN series: node does not say the baseline is the same culture at day 11.~~ **Corrected (A.12):** `design_notes` say the coculture series is compared with itself on day 11 (exponential), and the axenic series (separate repeat run) with itself on day 7; the axenic RNA-seq node has experiment-level `growth_phases: death` and its time point (day 14) only in design_notes (`timepoints` null). The RNA-seq coculture design_notes mention the pooled 'days 60+89' sample. (analysis)
- [pitfall] I asked the researcher for culture states and wrote two KG-gap entries without reading `list_experiments(verbose=True)` `design_notes`, which already held them. Read design_notes before logging a design gap. (analysis)
- [pitfall] I labelled hli groups "HL-only" from strain names before checking `list_organisms`, which has a `clade` field (HLI–HLIV, LLI–LLIV). The researcher pointed it out. (analysis)
- [kg] The publication title for 10.1128/JB.01097-06 (Steglich et al. 2006) reads "...Light Sensing in Prochlorococcus/H17188" in the KG, which looks like an encoding error in the strain name. It is cited as stored. (analysis)
- [kg] Zinser 2009 diel microarray (10.1371/journal.pone.0005135) is listed as an experiment, but it has no expression rows (gene_count 0). Only its Mfuzz clusters are loaded, and their phase text mixes time origins ("h after onset of dark" vs day-part labels; cluster 1 uses "the paper's time scale"). Cluster sizes sum to 1697, while total_gene_count is 1756. (analysis)
- [kg] Pandhal 2007 HL vs LL iTRAQ: the table description says ~15 proteins are significant, but the KG holds 6. (analysis)
- [kg] Phosphate starvation (Martiny et al. 2006, the only MED4 P experiment): the KG holds a 34-gene filtered subset (q < 0.05 at 48 h, all time points reported). 22 of 23 hli genes are absent, so they are 'not significant' at 48 h only and undefined at 0–24 h; hli cannot be assessed for early P stress. Raised by the researcher from the heatmap. (analysis)
- [kg] hli annotation gaps (exploration F): PMM0815 and PMM1396 have no protein_id or seed ortholog; Pfam PF31213 has no descriptive name; TX50_RS09730 has no GO/Pfam/InterPro (annotation_quality 2, NCBI 'hypothetical protein'); PMM0816/PMM1397 (most hydrophobic, 86 aa) have 0 TM regions while 16/23 hli genes have one; function_description filled for 2/23. (analysis)
- [api] gene_ontology_terms rollup mode raises ValueError without `level`. (analysis)
- [kg] Publication 'discusses' edges spread one sentence over more genes than it names: Tolonen 2006 'three hli genes' sentence on 10 MED4 + 8 MIT9313 genes; Bagby 2015 'six hli genes' sentence on 13 MED4 genes; Thompson 2016 lists 7 hli numbers, 6 locus tags linked. Gene-level source comparison is approximate. (evaluation)
- [kg] hli gene names: most MED4 hli genes carry the bare name 'hli'; PMM1317 is 'hli6' and PMM1128 'hli15', which may not follow the numbering in Steglich 2006 (their hli6–9 operon), so paper-numbered hli genes cannot be mapped to locus tags from names. (evaluation)

## Assessment of the research skills (template 0.2.0-alpha.2)

This analysis was also a test of the recently changed skills: the five-step Plan dialog, exploratory vs control-validated modes, `decisions_log.md`, `proposal-critic`, and the evaluation comparison with other studies (fcdc825). It ran in exploratory mode, MED4 only, with part B dropped for time.

### What worked
- **`decisions_log.md`.** It was the backbone of the analysis. Fourteen analysis-phase decisions (A.1–A.14) record who decided what and why, including corrections (A.12 corrects A.5) and drops (A.8, A.13). Every late question could be traced back.
- **Critic passes, especially delta passes.** Every pass found something real:
  - the paralog-twin artifact that created a false cluster split;
  - wrong notebook generalisations ("C1 never up", "all 13 multi-copy");
  - the twin rule wrongly applied to RNA-seq;
  - "quiet" genes that respond (PMM1128, PMM1390);
  - "change in light rather than light level", which no contrast supports;
  - "independent" support that re-read the same arrays;
  - a 4-vs-7 gene miscount.

  Without the delta passes, the paper would have shipped with two Blocker-level over-claims.
- **kg-coder run manifests** with a "candidate anomalies" section. These surfaced the coculture-2016 table defects, statement spreading in the KG `discusses` edges, and missing protein IDs, without the main thread reading raw output.
- **Exploratory mode.** It fitted the question, and the labels held through to the paper.
- **The evaluation's source-study comparison** (new). It produced a useful table and exposed KG mapping limits. The critic's framing, "re-reading the source's own data, not replication", should become part of the method itself.

### What to update, and where

| # | Problem in this analysis | Evidence | Where to update |
|---|---|---|---|
| 1 | Culture states were asked of the researcher, then wrongly logged as KG gaps; the KG `design_notes` already held them. | A.3–A.5, then the A.12 correction | `SKILL.md` Rule 8, "Design comparability": replace "The KG doesn't hold every culture state — ask the researcher" with "read `list_experiments(verbose=True)` `design_notes` first; ask only for what is missing, and say what the notes already state". Also `kg-rules.md` "Scoping: what to verify". |
| 2 | HL/LL was inferred from strain names. | Researcher correction; pitfall above | `kg-rules.md` / `gene-identity.md` "Ortholog cluster rules": use the `list_organisms` `clade` field for ecotype; never parse names. |
| 3 | Unusable tables were found only in the analysis milestone: a 34-gene filtered phosphate table, and a coculture table with 82% negative log2FC and repeated values. | A.8, A.13 | `step-protocol.md` Plan step 4 / `anti-hallucination.md` 3.4: in the spike, per experiment, check (a) how many target genes are present in the table (a count, which is free to look at) and (b) table sanity: sign fraction, repeated identical values, large \|FC\| called ns. This extends 3.4 beyond "sign lost". |
| 4 | Identical paralogs share one microarray probe, and significant-only tables list one twin. Coding the other twin "ns" created false clusters; applying the fix to RNA-seq was wrong. | Critic #1, D3, D4 | `gene-identity.md` "Paralog handling": add a twin rule. Detect identical log2FC across a pair on arrays; mark the unlisted twin undefined in significant-only array tables; RNA-seq untouched; collapse pairs in a set-level sensitivity check. |
| 5 | Paper figures were first illegible and inconsistent; prose was too terse; Results followed the analysis chronology, not the argument; a dense table was hard to read; greys were too similar. | Researcher feedback, five rounds | `figures-and-reports.md` and `research-notebook.md` (paper.md): a dedicated page-width paper figure set (7.2 in, text ≥ 8 pt, one colour scheme shared with the reports); order Results by the question (set level → which genes → when), merging overlapping groupings into one section; prefer a figure or infographic over a multi-row table; run `validate_palette` on annotation-strip palettes (tiers, categories), not only up/down; light theme by default for reports. |
| 6 | The analysis milestone grew without bound. About ten explorations (A–F, conservation, diel, proteomics, annotations) and repeated "approve?" questions meant three critic passes over one milestone. | Notebook runs 4–10 | `step-protocol.md` "explore" / GATE E: after the first critic pass, offer to close the milestone and move further explorations to evaluation (or a follow-up analysis), each with a short delta pass, so approval is not held hostage by exploration. |
| 7 | The main thread repeatedly over-reached in interpretation: "therefore" from a contrast that cannot support it, "independent" support from the same data, "explains" for a partial split. | Critic V1, V2, E4 | `step-protocol.md` decide gate (author self-check before the critic): for each "therefore / explains / independent / all / none", name the contrast or file that supports it. The critic should not be the first line of defence. |
| 8 | Comparison with source studies: the KG `discusses` edges spread one sentence over more genes than it names, and gene names do not follow paper numbering. Agreement is consistency, not replication. | Evaluation V2, V4, V5; KG gaps above | `step-protocol.md` evaluation / `critical-review` evaluation lens: state that source comparisons re-read the source's own data; list every linked gene, including ones that disagree; report magnitudes when they exist. |
| 9 | Rule 1 forbids web search, but background citations (HLIP function, family expansion) cannot come from the KG. The researcher authorised a web search. | A.14 | `SKILL.md` Rule 1 / `kg-rules.md` "Separating KG from literature": allow researcher-authorised web search for background citations only; log it in `decisions_log.md`; list those references separately from KG data sources; never take data from them. |
| 10 | "All code in the repo": data and figure code was there, but figure edits were drafted in scratch files and spliced in; script 20 silently depends on script 24's output. | Researcher request | `artifacts.md`: figure and data code lives in `scripts/`, with run order stated in docstrings (or a `run_all` list); scratch is only for one-off text edits. |
| 11 | On Windows, inline bash heredocs with quotes and backslashes failed several times. | Session friction | `python-api-guide.md` / `kg-coder.md`: on Windows write scripts with the Write tool and run them; avoid inline heredoc Python for anything with quotes. |
| 12 | A hard-coded experiment count assertion in a script broke when an experiment was dropped. | Script 08 (17 → 16) | `kg-coder.md`: derive counts from data, or assert against a named list with the reason. |

### Not tested in this analysis
Control-validated mode; the plain-language "look now or wait" question; discovery milestones; the `proposal-critic` beyond one proposal pass; part B (cross-strain).

### Should recurring code become a shared library?

Yes, but in two places, and only for code that has proved itself. Rule 5 says not to re-wrap what the explorer package ships. Generic KG operations therefore belong upstream in `multiomics_explorer`. Template-level helpers (reports, paper, figure frame) belong in the template's `scripts/` or in a `recipes/` skill, which is still empty. Promote a function after it has been rewritten in two or more analyses, with its toy tests carried along. Do not promote something from one analysis's one-off.

| Candidate | Written here as | Generic problem it solves | Home |
|---|---|---|---|
| Table sanity and coverage check | `methods/02_sign_and_spot_check.py`, `analysis/11_check_coculture2016.py`, the phosphate coverage check | Per experiment: target-gene presence, sign fraction, repeated identical values, large \|FC\| called ns, `table_scope` semantics. Used in the Plan spike (assessment item 3). | **explorer** (a `de_table_qc` tool or utility); the template's step-protocol calls it |
| Gene × contrast call matrix with `table_scope` semantics | `methods/01_build_lists.py` (`gene_calls_from_background`), `analysis/09_explore_clusters.py` `code()` | up / ns / down / undefined per gene and time point; significant-only absence → ns; up-only tables → undefined for non-up; filtered subsets → undefined outside the filter | **explorer** utility (the semantics are KG knowledge) |
| Identical-paralog (shared-probe) detection and rule | `twin_rule.py`, `12_twin_pairs.py`, `13_twin_collapsed_ora.py` | Detect pairs with identical log2FC on arrays; mark the unlisted twin undefined in significant-only array tables; collapsed sensitivity check | **explorer** utility, plus a `gene-identity.md` rule |
| Gene-set ORA across all experiments × time points × directions | `analysis/01_score_hli.py` around `fisher_ora` | Per-experiment calls with flags (too few, genome-wide, approximate) and BH families | Check `pathway_enrichment` first; if a custom set is not covered, add a **recipe** (protocol + thin script), not a new library |
| Ortholog-group breadth by clade | `15_og_conservation.py`, `conservation.py` | Per homolog group: genomes by HL / LL / Syn / other from the `list_organisms` `clade` field, plus KG totals | **explorer** (`genes_by_homolog_group` could return clade counts) |
| References from KG publications | `21_references.py` | Reference list and in-text cite keys for paper.md | **template** `scripts/` (next to `build_paper.py`) |
| Paper figure frame | `20_paper_figures.py` helpers (`axin`, `save` with min-font and width asserts, `letter`) and `d_scheme.py` | Page-width figures, ≥ 8 pt check, one colour scheme shared with reports | **template** `scripts/` or the `figures-and-reports.md` reference, as a small module |
| Display overrides and dropped experiments | `display_overrides.py` | Researcher-supplied relabels and drops applied to every table without rewriting data | **recipe** (pattern doc); too analysis-specific for a library |

Not worth promoting: the exploration scripts (04–10, 14, 17, 22–25) and the report builders specific to this analysis.
