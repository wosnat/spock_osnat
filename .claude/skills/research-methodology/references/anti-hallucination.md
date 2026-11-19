# Anti-hallucination patterns

The ways Claude has produced plausible but wrong claims from this KG, each
with the real case and the check that catches it. The rules themselves live in
their home files (gene-identity, statistical-rigor, SKILL.md Rule 9); this
file is the catalogue to read before presenting findings, and its last
section is the checklist.

## Contents
1. [Gene identity](#category-1-gene-identity-errors)
2. [Narrative beyond the data](#category-2-narrative-fabrication)
3. [Data handling](#category-3-data-handling-errors)
4. [Knowledge boundaries](#category-4-knowledge-boundary-violations)
5. [Claims from memory](#category-5-source-of-truth-verification-failures)
6. [Quick self-check](#quick-self-check)

## Category 1: Gene identity errors

The most dangerous: they yield plausible biology about the wrong gene.

### 1.1 Paralog conflation

Several locus tags share a name and their data are merged into one story.
*Case (catalase):* "katA is down under starvation (log2FC −7.8) then recovers
at day 89 (+1.8)" — the drop was ACZ81_02025, the "recovery" ACZ81_11985:
different genes, same name. Rule: [gene-identity.md — Paralog handling](gene-identity.md#paralog-handling).

### 1.2 Ortholog cluster conflation

A cluster-mate's data are reported for another gene. *Case:* MIT1002_02513
(katE) values were reported as katB (MIT1002_03530) because both sit in
cluster 4644E. Rule: [gene-identity.md — Ortholog cluster rules](gene-identity.md#ortholog-cluster-rules).

### 1.3 Gene functions from memory

"Gene X is in pathway Y" stated from training data; the KG may annotate it
differently or not at all. Rule: [gene-identity.md — Gene function claims](gene-identity.md#gene-function-claims).

## Category 2: Narrative fabrication

A coherent story that goes past what the data show.

### 2.1 Causal claims from correlational data

"X regulates Y", "A activates pathway B" from co-expression. Differential
expression shows association; the KG holds no ChIP-seq or knockouts. Write
"co-regulated", "respond together".

### 2.2 Cherry-picking from truncated results

A tool returns 50 rows of 800 and the summary reads "the top genes are…" — or
worse, "gene X is not differentially expressed" when it was simply not
returned. **Check:** read `truncated` and `total_matching`; never infer absence
from a truncated result; for an absence claim, query that gene.

### 2.3 Selective reporting of duplicate entries

The same gene and condition has two rows (two contrasts). *Case:* katG
(ACZ81_16125), coculture day 89: +1.26 (padj 3e-4) and −1.16 (padj 0.29); only
the first was reported. **Check:** report all rows; if you can't tell which
contrast applies, say so.

### 2.4 Strength of language vs strength of evidence

"Significantly down" at padj = 0.050; "consistent with ROS detoxification"
with no test. The scale of wording per padj is in
[statistical-rigor.md](statistical-rigor.md#strength-of-language-vs-strength-of-evidence).

### 2.5 Cross-experiment aggregation without caveats

Magnitudes or p-values compared across platforms and studies. *Case (N
stress):* Tolonen 2006 (microarray) and Read 2017 (RNA-seq) fold changes were
compared as if on one scale; "katA is more affected by starvation (padj
2e-11) than by coculture (padj 0.015)" compared p-values across studies.
Rule: [statistical-rigor.md — Cross-experiment comparison](statistical-rigor.md#cross-experiment-comparison-caveats).

### 2.6 Emotive vocabulary and speculative proposals

Language or fixes that run ahead of the data (rules: SKILL.md Rule 9).
- **Commitment words early.** *Case (discordance):* before any metric was
  computed, a 5-marker heatmap was "biologically explosive", a "massive
  finding" that "reframes the analysis".
- **Narrating the loud cells.** *Case (stress axis):* "all 5 N-stress positives
  are clearly UP" — the data file had coculture RNA at log2FC −1 to −2.6 at all
  four time points; the eye had anchored on the strongest cells. **Check:**
  every "all / none / primarily" against the data file.
- **Speculative proposals.** *Case:* seven process changes proposed after one
  analysis, several from a single nudge. One occurrence is a note; a change
  needs the same friction twice.

## Category 3: Data handling errors

### 3.1 Counting from truncated lists

"50 genes respond" when `total_matching` is 823. **Check:** counts come from
summary fields (`total_matching`, `total_entries`), never `len(results)`;
counts of sub-categories come from full extracts.

### 3.2 Fabricated summary statistics

A mean or percentage computed from whatever rows were in context and presented
as a finding ("catalase genes are down 6.2-fold on average"). **Check:**
summary statistics come from a script over complete data, and you cite it; a
quick chat estimate is labelled "rough, from the top N rows" and is never a
finding.

### 3.3 Direction claims from a table whose sign may be absent

Some tables hold one direction only, or lost the sign at ingestion, so every
gene reads "up" — and `table_scope = all_detected_genes` does not rule this
out. *Case (Alteromonas coculture):* four 2016 experiments had 0% negative
log2FC across 740–2,295 genes; a claimed "motility direction flips by partner"
partly rested on them. **Check:** before any direction claim, the sign
distribution over *all* rows, not the rollup counts. `significant_down = 0`
alone is not the tell (sparse proteomics can have none); a real all-gene table
is roughly 40–55% negative. A table far from that is reported, not used.

## Category 4: Knowledge boundary violations

### 4.1 Asserting absence

"Prochlorococcus lacks catalase" from a KG with no catalase annotated.
**Write** "no catalase genes are annotated in the KG for Prochlorococcus"; the
KG reflects what was annotated and loaded.

### 4.2 Assuming KG completeness

"MED4 has N nitrogen-responsive genes" when N came from one experiment.
**Write** "in experiment X, N genes were differentially expressed under
nitrogen limitation" — anchor every claim to its experiments and conditions.

### 4.3 Literature claims without KG support

"Gene X was shown to … (Smith et al. 2020)" from memory, about a paper not in
the KG. **Check:** keep KG findings and literature visibly apart; KG papers
are cited only via `list_publications`; outside literature only through a web
search the researcher authorised, for citations, never data
([research-notebook.md — Citations](research-notebook.md#citations-and-supplementary-information)).
Never cite a paper from memory.

### 4.4 Measurement failure vs biological absence

A layer, condition or time point has no data, and that is read as biology —
"mRNA is gone", "not expressed". *Case (discordance):* MED4 axenic days 31 and
89 had proteome but no RNA-seq; the RNA extraction had failed in dying cultures,
and "protein persists while mRNA is gone" would have been a false claim. Data
also go missing through detection limits, sample loss, depth, multi-mapper
filtering of identical paralogs, or platforms covering different genes.
**Check:** was it measured? Missing is no information, not zero. Write "no
protein detected", "no RNA-seq data", not "absent" or "not expressed".

## Category 5: Source-of-truth verification failures

Claims from memory of a schema, an API or a paper. They feel confident because
they are based on something real — but not this KG, this version or this field.

### 5.1 MCP tool capability from memory

*Case (N limitation):* "`pathway_enrichment` has no `term_ids` filter" — it
did, and the false claim blocked a line of analysis. **Check:** before saying
what a tool accepts or returns, read `docs://tools/{tool}` or load its schema
(`ToolSearch select:<tool>`); for cross-tool semantics (`not_found` vs
`not_matched`, truncation, tested-absent rows) read `docs://guide/conventions`.
A failed call is a reason to read the schema, not proof the capability is
missing.

### 5.2 Publication attribution from training knowledge

*Case (N limitation):* an experiment was attributed to "Hennon" because it
sounded like that group's work; it was Aharonovich & Sher 2016. **Check:** run
`list_publications` before naming any author, title or citation; cite by DOI.
Two experiments that "sound similar" is a reason to verify.

### 5.3 Field semantics from memory — cumulative vs per-timepoint counts

*Case:* Tolonen 2006 reported as "10,182 genes", about six times the MED4
ORFome — the top-level `gene_count` in `list_experiments` is summed over time
points. **Check:** per-time-point detection uses `timepoints[].gene_count`;
backgrounds and 2×2 tables use `distinct_gene_count`; never the cumulative
`gene_count`. For any count or total, check its unit and scope in the schema.

## Quick self-check

Before presenting a finding:

1. **Where did this number come from?** A named tool call or script output.
2. **Locus tag or gene name?** Locus tag.
3. **Complete or truncated?** Check `truncated` / `total_matching`.
4. **Across studies?** Direction and rank only; magnitude within one platform
   and study; never p-values.
5. **A direction (up / down)?** The all-row sign distribution is two-sided.
6. **Absence?** "In the KG" / "in this experiment"; and was it measured?
7. **KG or my own knowledge?** Labelled which.
8. **Would another paralog assignment change it?** Then verify the assignment.
9. **A tool capability, citation or field meaning from memory?** Check the
   schema, `list_publications` or the field description first.
