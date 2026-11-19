# Notebook, paper, friction log, and method code

What goes *in* the analysis's written files, and how method code is verified.
When each is written is in [step-protocol.md](step-protocol.md); the Plan's
`decisions_log.md` is in [plan-phase.md](plan-phase.md#how-the-dialog-reads-decisions_logmd).

## Contents
1. [notebook.md](#notebookmd)
2. [paper.md](#papermd)
3. [gaps_and_friction.md](#gaps_and_frictionmd)
4. [Verifying the method](#verifying-the-method)

## notebook.md

One per Run milestone, written by the main thread (kg-coder's run-manifest is
pasted into the mechanical sections; every interpretive section is yours).
Freeform prose; use the sections that apply:

- **Context** — what this milestone is for; what the proposal or the previous
  milestone set up.
- **What I did** — scripts with command lines for non-trivial runs; KG queries.
- **Results** — summary tables as markdown (the real numbers, not paraphrase);
  links to full tables in `data/` and figures; publications resolved through
  `list_publications`, never from memory.
- **Surprises** — anomalies and oddities worth flagging.
- **Decisions** — forks taken this milestone, in prose with dates.

What to show, by milestone:
- **methods:** 2–3 genes worked through the formula step by step with real
  numbers; the output's distribution, range, NaNs; the positive controls ("glnA
  should score high — does it?").
- **analysis:** the full results table; best and worst; anything unexpected;
  comparison with what the framing expected.
- **evaluation:** the findings table with labels and numbered meanings; the
  comparison with other studies; predictions held or not, read through the
  decision rule (if a pre-set rule was deferred, report "not evaluated as
  planned", never a post-hoc substitute); stability checks; caveats.

### Decide-gate checklist

The notebook ends with exactly this — don't extend it:

- **Outputs produced** — files in `scripts/`, `data/`, `figures/`, with command
  lines for non-trivial scripts.
- **Results presented** — summary tables inline; links to full tables and
  figures.
- **QC gate** — what was checked → result, one line each.
- **Decisions** — prose + date; omit if none.
- **Advance rationale** — one line: why this milestone is ready to close.

**Labels** (P2, tier B) are allowed within one document only when paired with a
readable name in the same paragraph; never across files ("see D7 in
decisions.md"). **On redo the notebook is overwritten**, not appended — it
describes the attempt that worked; git keeps the rest.

## paper.md

One `paper.md` at the analysis root, **written for the reader of the eventual
paper**: each section drops into a manuscript as is. The skeleton exists from
the scaffold; each milestone writes its own section at decide, and earlier
sections are revised when a later milestone changes them — never left for a
final rewrite.

| Section | Written at |
|---|---|
| Abstract | evaluation, last — 150–200 words: question, approach, findings, meaning |
| Question, Background | Plan |
| Methods | Plan (framing) + methods; updated at analysis for anything added |
| Results | analysis, after its storyline is agreed |
| Discussion | evaluation, its storyline agreed the same way |
| References | every phase that cites |
| Supplementary information | any milestone |

**Journal prose; the process record lives elsewhere.**
- No internal vocabulary (milestones, gates, critic findings, module versions,
  undefined labels), no file paths or script names, no `[KG]` tags — make the
  same distinction in words ("the data show …" vs "this suggests …").
- Figures and tables by number with captions. A figure goes in as
  `![Fig. 2. Caption …](analysis/figures/fig2.png)`; a table is a markdown table
  under a "Table 1." line. `build_paper.py` renders `paper.html` with figures
  embedded and fails on a missing figure.
- Every number traces to a data file (the trace lives in the notebook).
- Statistics in journal form ("corrected p = 2 × 10⁻¹⁰", not "BH padj 2e-10");
  groups named for what they are ("responders"), not cluster numbers; one term
  per concept, defined at first use.

*(N-import: `paper.md` drifted into a process record and a separate manuscript
had to be written at the end.)*

**A paper tells a story, not what was done in order.** Before writing Results,
agree with the researcher: (1) the answer in three to five plain sentences;
(2) the Results as headings, each a one-sentence claim, in argument order —
usually the big picture first (does the set respond? to what?), then finer
structure (which genes, when); (3) one figure per claim. Several analyses that
point at one idea become one section. Each section opens with why it matters
and closes with what it adds to the answer; the headings and first sentences
alone should carry the argument. Method detail goes to Methods, long lists to a
figure or supplementary table, robustness checks one sentence each. More than
three numbers in a paragraph — would a figure carry them? Before presenting,
read it as a biologist who never saw the notebooks. Paper figures are their own
set ([figures-and-reports.md — Paper figures](figures-and-reports.md#paper-figures--a-separate-set-made-for-the-storyline)).
*(hli light stress: the first draft was the notebook in sentences; the
researcher rewrote it over a dozen rounds — "no narrative … too low-level".)*

### Discussion

1. **Findings table first** — one row per question or route, one column per
   reference or condition, a short verdict per cell, and a last column:
   **tested as planned** or **exploratory**.
2. **Numbered plain-language meanings**, one per pattern, each a sentence or two
   an outsider could restate.
3. **Comparison with other studies** — a short table: each finding against the
   other KG experiments or publications that bear on it (via
   `list_publications`): **agrees / disagrees / can't tell**, and why (design,
   platform, time point, strain, gene not measured). "Can't tell" is common and
   valid. KG data only; any reading of why studies differ is worded as
   interpretation. A comparison with the study that produced the data re-reads
   that study's own data: call it consistency, not replication. List every gene
   the KG links to the source's statement, including those that disagree, and
   give magnitudes where the source has them — publication links can spread one
   sentence over more genes than it names, and gene names may not follow the
   paper's numbering. *(hli light stress: a "three hli genes" sentence was
   linked to 18 genes.)*
4. **Caveats** in their own short section, each tied to the finding it limits.
   Don't fold them into the conclusion. *(N-import: the critic-hardened
   conclusion read as "a long paragraph that says we know nothing".)*

**The two labels.** *Tested as planned* only if the proposal's decision rule
produced it on data nobody looked at before the plan was set
(`decisions_log.md` lists what was seen early). Anything seen in planning, found
in exploration, or produced by a rule changed after the results were seen is
*exploratory*. Methods states once which analyses were specified in advance and
what was examined first. An exploratory analysis says once that it is
exploratory, with no per-row labels. **One exception:** a finding that emerged
stays exploratory, but a test of its prediction — logged before the test data
was opened, on data not used to find it — is *tested as planned*; the paper says
where the prediction came from and how independent the test data is
([step-protocol.md — explore](step-protocol.md#explore)).

### Citations and supplementary information

Background and Discussion cite what frames the question and the findings;
Methods cite every publication whose data is used, where its data is described,
and state once the KG release and explorer version. With more than a handful of
experiments, add Table S1 (experiment, publication, organism, platform, table
type, use). Two sources only:
- **KG publications** — resolved through `list_publications`, cited by DOI.
- **Literature outside the KG** — only through a web search the researcher
  authorised, for citations only, never data. Record the authorisation in
  `decisions_log.md`, check each record, and list these after the KG sources,
  marked as literature. Ask for the authorisation when the first such claim is
  written; no "[ref needed]" reaches the researcher.

Every citation is in References and every reference is cited; References give
the full reference with DOI. KG experiment IDs stay in the notebooks.

**Supplementary information** comes after References in the same file: Fig. S1,
Table S1 …, cited from the text. Long tables are not pasted — they are CSVs
listed as **Supplementary Data 1, 2 …** with a one-line description and file
name (the one place file names appear).

## gaps_and_friction.md

The learning record that feeds back into the methodology, the KG and the tools.
**Friction** — something that slowed the work, surprised you, or exposed a gap —
goes here; a **decision** goes to the notebook (or `decisions_log.md` in the
Plan). One event can be both; log both.

Record KG data issues, tool and API mismatches, methodology gaps, corrections of
claims made from memory, process friction — and **what worked**, so the log can
become best-known methods. Each entry: date, short name, one tag, what happened,
and the workaround or impact if any.

| Tag | Use for |
|---|---|
| `[pitfall]` | a mistake the method or Claude made, and how it was caught |
| `[bkm]` | something that worked and should be kept |
| `[kg]` | data the KG doesn't hold, or holds wrongly (older logs: `[kg-gap]`) |
| `[tool]` | an MCP, explorer, Claude Code or environment problem |
| `[api]` | explorer API behaviour (defaults, errors, missing parameters) |
| `[method-gap]` | something the methodology didn't anticipate |

Write each entry when it happens; the log goes quiet exactly when the late
milestones get heavy. Append-only; redo entries accumulate. It stays mandatory
while the methodology is settling; propose retiring it after two consecutive
analyses log no methodology gaps.

## Verifying the method

**Reusable logic in a module, specifics in scripts.** A new method's logic lives
in `methods/<module>.py` — the formula with a worked example, expected I/O, and
the minimum code — and later milestones' scripts import it. Plain extraction
and plotting scripts need no module.

**Toy data before real data** (`superpowers:test-driven-development`): small
synthetic input, expected output by hand, compare, log it in
`methods/notebook.md`. A green suite is not enough:
- **Fixtures in the real file format.** If the pipeline reads a CSV, the
  fixture's fields are the *strings* a CSV yields. *(Alteromonas coculture:
  `bool(row["in_candidate"])` on the string `"False"` is truthy; all 27 tests
  passed on Python booleans, and real data would have collapsed every class.)*
- **One small real example against an independent answer.** Run the module on a
  KG case whose answer is known (a control set, a case a source paper states)
  and compare with an answer built through MCP calls — not through the explorer
  API the module uses, and not by the module's author. Toy tests catch logic
  errors; only an independent path catches wrong calls, defaults, filters and
  paging. Log it as a QC-gate line. *(hli light stress: the spot checks re-used
  the same API, so a shared misuse would have passed.)*

**When the method builds the entity set, verify in four layers** before scaling
or handing it on, each logged as a QC-gate line. Layers 2 and 3 are done by
someone other than the module's author.

| Layer | What | What only it catches |
|---|---|---|
| 1. Real-format fixtures | toy inputs as the file actually arrives | parsing traps (`bool("False")`, `"n/a"` read as NaN) |
| 2. Pilot vs an independent answer key | for one organism or a few systems, build the answer through MCP calls alone and diff | wrong API defaults, rule gaps (57 vs 86 BRITE genes; `fadD` called a transporter) |
| 3. API-usage review | read how the module calls each explorer function against its source and `docs://` pages | paging, sorting and filter behaviour no count sees (offset paging swapped rows while every count passed) |
| 4. Bin sample | a random sample of each bin before its rule is approved | rules that read right but fill bins wrongly (a "Medium" tier of helicases) |

The researcher sees layer 4's samples at the decide gate: a rule is approved on
what it puts in the bin, not on how it reads.

**Productize later, not speculatively.** A utility rewritten in two or more
analyses is a candidate for the shared package — a separate design effort. One
analysis's one-off is not.
