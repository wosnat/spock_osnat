# Research notebook

## Step protocol and enforcement

For per-milestone commit timing, hard gates, and the decide-gate checklist, see [Step protocol](step-protocol.md). This document owns the notebook **format and content**; step-protocol owns **when things happen and what gates enforce them**.

---

Every analysis is a **Plan phase** that converges on `proposal.md`, then a **Run phase** driven by **per-milestone interactive notebooks** — one `notebook.md` per Run milestone folder — plus a single `paper.md` at the analysis root that grows as a polished write-up. Execution is delegated to a coding subagent; quality control, exploration, and decision-making are always interactive and stay in the main thread (see [Code lifecycle](#code-lifecycle-analysis-first-productize-later)).

## Just-in-time formalization

Plans, framings, predictions, metrics, terms, decisions, and caveats enter the analysis **only when the data demands them**. Nothing is enumerated in advance "just in case." Its partner is **enumeration**: within what the plan *does* commit to, be concrete — a vague-but-approved plan is what forces redos.

Look at the data before drafting the plan. Pull what's in the KG — counts, fields, coverage — then propose the minimal framing that fits, stated concretely. Start simple; expand only when a specific finding forces it.

Concrete rules:
- **The Plan phase grounds the dialogue in MCP queries, not assumptions.** Before locking scope or framing, run `list_publications`, `list_experiments`, `list_organisms` filtered to the prompt's context. Surface counts and structural surprises (e.g. "axenic RNA-seq is single-contrast, not time-course") in the dialogue, shown as a table or plot. Capture the queries and key counts as facts in `decisions_log.md`, before the choices they inform.
- **Size the question before framing it.** If it has several parts that each need their own answer, or many stress types, strains and papers to sort before anything can be scored, propose splitting it into smaller analyses done one after another. A plan that keeps generating decisions without closing is the sign it was too big. *(General stress response: three parts, about 60 decisions in a week, plan still open.)*
- **Check that the approach can work before framing it** — in `spike/`, throwaway: annotation depth and recall, control coverage, a random sample per group, distribution shape per experiment. Required when the method builds its own gene set or mixes platforms. *(N-import: the transport-annotation limits surfaced only after the plan was locked.)*
- **The Plan phase locks the question and framing, not sub-questions.** Sub-narratives that form during dialogue (e.g., "protein persists while mRNA is gone") are for the Run phase to test. Defer; note them.
- **Ask what the result is for before locking the question.** Is this a standalone result, or part of a paper (or a rewrite of one)? Whose hypothesis is it — the researcher's own, possibly unpublished, or a published claim being tested? The answer changes what counts as a finding and who is anchored to it. *(N-import coculture: the anchor was the researcher's own preprint, which the analysis was rewriting; the Plan learned this only at approval.)*
- **Framing has a floor, not a template** (control-validated mode; an exploratory analysis agrees scope and deliverables instead). The floor — all seven, stated concretely: hypothesis in prose; approach (how and why); a deliberate statistics decision (the specific test and thresholds, *or* an explicit reasoned "none, because descriptive"); positive controls (named genes, pathways or experiments that must show the expected effect if the method works, each with its expected result, coverage checked); negative controls (a class that should *not* score if the signal is genuine, with its expected score stated, not assumed to be zero); a decision rule (every reading of the target named in advance, with thresholds); and design comparability (below). Nothing beyond the floor unless the data forces it.
- **Design comparability — one row per experiment used.** A metric can be comparable while the *designs* are not. For each experiment, state: its role in the analysis; what each arm is compared against (the reference sample, and that sample's physiological state — growth phase, nutrient status, sampling day); whether its contrasts share samples or one fitted model (if so they are not independent evidence); and what it can and cannot confirm. The KG does not hold everything here — reference-culture physiology often lives only with the researcher — so **ask the researcher** for the culture states the KG doesn't record, and mark those cells as researcher-supplied. A table is the natural form. *(Two analyses running: Alteromonas coculture hit an FDR-family-size trap across experiments; N-import coculture missed that late coculture vs early axenic confounds partner with starvation length, that the axenic "early" reference was a late-decline culture, that each arm's RNA reference was its own already-stressed exponential phase, and that the coculture-vs-axenic contrasts were algebraically one fitted model.)*
- **Predictions are named, not matrixed.** If confirmation bias is a real risk, name 1–3 predictions — not a 4×4 matrix of ordering and thresholds.
- **Stability checks are added when a specific result triggers them**, not planned up front.
- **Decisions are written when forced by data**, not anticipated. No "we may decide X" placeholders.
- **The methods milestone is minimal — unless it constructs the entity set.** A method that scores a set the proposal already defines is an ad-hoc Python module implementing exactly that approach. A method that *builds* the set — transport systems, a curated candidate list, tiers, classes, links between parts — is a **discovery milestone**: plan it as one. Expect many decisions at its decide gate (budget the researcher's time for them), several versions of the module, and the layered verification in [Phase 1 — Analysis code](#phase-1--analysis-code-methodology-first). *(Both analyses so far: Alteromonas coculture became a discovery milestone by accident; N-import coculture planned one and took 21 decisions across seven module versions.)*
- **Caveats are harvested at the evaluation milestone** from what actually happened; not pre-cataloged.

This principle governs the whole arc. If you find yourself listing or architecting things the analysis might need before the data has arrived, stop.

## The arc

**Plan phase** — one grounded `superpowers:brainstorming` conversation, walked through with the researcher in five steps, each closing on a "so far" summary they confirm (see [SKILL.md Rule 8 — Plan](../SKILL.md)):
1. **Clarify and size the question** — what it is for (standalone result or part of a paper; whose hypothesis), the mode (exploratory or control-validated), and whether to split it
2. **Show what the KG holds** — publications, experiments, organisms, data types, coverage, enumerated from the KG and shown as tables or plots
3. **Agree the general approach**
4. **Check that the approach can work** — throwaway tests in `spike/`, when the method builds its own gene set or mixes platforms
5. **Set the framing** — hypothesis, approach, statistics plan, positive and negative controls, decision rule, design comparability, all in KG terms (the enumerated floor above); control-validated mode only

`proposal.md` is written after the five steps, as the record of what was agreed, and locked at the end of the Plan phase. The Run phase executes against it.

**Run phase** — three milestones, each in its own folder:
- **methods** — implement the approach the proposal committed to as an ad-hoc Python module; toy-test it
- **analysis** — run the method; produce scored outputs, figures, tables
- **evaluation** — assess results against the framing; harvest caveats; finalize the paper

The Plan phase produces `proposal.md` + `decisions_log.md` (the step-by-step dialog: KG facts, decisions with who decided them, rejected alternatives, open questions), plus a throwaway `spike/` folder when step 4 ran. It is interactive, not scripted, but not assumption-driven — MCP queries ground the conversation. Run milestones add `scripts/`, `data/`, `figures/`, and QC alongside `notebook.md`.

## The Run-milestone rhythm: co-define → do → show → explore → decide

Every Run milestone advances through these phases (see [step-protocol.md](step-protocol.md) for commit timing, gates, and delegation):

- **co-define** — before doing the work, propose the milestone to the researcher in plain language (what it should produce, the judgment calls, why) and let them shape it; begin only once you've agreed
- **do** — the coding subagent does the agreed work; outputs land wherever they naturally belong
- **show** — the main thread populates `notebook.md` from the subagent's returned artifacts and run-manifest
- **explore** — investigate anomalies, surprises, or gaps; each question is a new request to the same coding subagent, returning the artifact that answers it; the main thread interprets
- **decide** — finalize notebook, update paper.md, run critical review (analysis + evaluation; methods when it emits a data artifact; a delta pass if claims grew after the first pass), present state to researcher, commit on approval

## notebook.md format

One `notebook.md` per Run-milestone folder. Freeform prose, not a rigid template — include what applies to the milestone. **The main thread owns and writes `notebook.md`** — it pastes the coding subagent's factual run-manifest verbatim into the mechanical sections (What I did, raw Results tables) and writes every interpretive section itself. The subagent never writes conclusions into the notebook (see [Code lifecycle](#code-lifecycle-analysis-first-productize-later)).

### Recommended sections

- **Context** — what this milestone is for; what the proposal or prior milestone set up
- **What I did** — work performed; scripts run with their command-line invocation for non-trivial cases; KG queries issued
- **Results** — summary tables shown inline (as markdown tables, not prose paraphrases); links to full tables in `data/` and figures in `figures/` produced this milestone; cited publications from the KG by DOI or experiment ID — resolved via `list_publications`, never from memory (see [anti-hallucination.md — Category 5](anti-hallucination.md#category-5-source-of-truth-verification-failures))
- **Surprises** — anomalies, data oddities, unexpected distributions worth flagging
- **Decisions** — in prose with dates, if any forks were taken this milestone; omit if none
- **Advance rationale** — one line at the end

### Decide-gate checklist (end of notebook.md)

At milestone close, the notebook ends with this checklist (see [step-protocol.md](step-protocol.md) for the approval gate):

- **Outputs produced** — filenames in `scripts/`, `data/`, `figures/`, with command lines for non-trivial scripts (for reproducibility)
- **Results presented** — summary tables shown inline in `notebook.md`; links to full tables and figures generated this milestone
- **QC gate** — what was checked → result (one line per check)
- **Decisions made this milestone** — prose + date, if any; omit the section if none
- **Advance rationale** — one line, why this milestone is ready to close

The checklist must stay this minimal. It is not a template to extend with optional fields. Inflation of this list reintroduces the premature-formalization failure that the per-milestone notebook is designed to prevent.

### Labels

Labels are permitted within a single document when each label is paired with a short readable name in the same paragraph on first mention. **No cross-file labels.**

- OK: "the coculture-stronger prediction (2) was not supported; (2) rests on the assumption that axenic cells shut down before fully engaging response"
- Not OK: "P2 failed" (no name) or "see D7 in decisions.md" (cross-file label)

If paired-label-plus-name still obscures content, drop to prose-only — labels are a convenience, not a requirement.

### Overwrite vs append

A milestone's `notebook.md` represents what-we-now-believe-happened in that milestone. On redo, the notebook is **overwritten**, not appended — the narrative reflects the successful attempt, not a log of past attempts. The prior attempt lives in git history (see [step-protocol.md — Redo path](step-protocol.md)).

`gaps_and_friction.md` is **append-only** (see below).

## paper.md growth pattern

Single `paper.md` at the analysis root. **It is written for the reader of the eventual paper, not for the team that ran the analysis**: each section must drop into a manuscript as is — its Methods into a Methods section, its Results into Results — with nothing to strip out first. Skeleton sections exist from day 1 (seeded by Claude during scaffolding at the start of the Plan phase) and fill in as the analysis advances — during the Plan phase and each Run milestone's **decide** phase, after the notebook is finalized but before the commit.

**`paper.md` is journal prose. The process record lives elsewhere.** The notebooks, `proposal.md`, critic files and `gaps_and_friction.md` carry the how-we-got-here; `paper.md` carries only what a reader of the paper needs:
- **No internal vocabulary** — no milestone names, decide gates, step labels, critic findings, version numbers of the module, or labels like "E7" or "tier B" unless defined in the text as they would be in a paper.
- **No file paths or script names** in the prose. Methods name the data sources (publications, experiments, KG release), the procedure and the statistics, as a Methods section would.
- **Figures and tables by number** ("Fig. 2", "Table 1"), each with a caption. Put a figure in with image syntax, the caption as the alt text and the path relative to `paper.md`: `![Fig. 2. Transport genes, log2FC coculture vs axenic …](analysis/figures/fig2_transport.png)`. Tables are markdown tables with a "Table 1." caption line above. `scripts/build_paper.py` renders this into `paper.html` with every figure embedded — one self-contained file to read, send, or print to PDF (see [figures-and-reports.md](figures-and-reports.md)).
- **Every number in the text traces to a data file.** The trace is recorded in the milestone's `notebook.md`, not in the paper.
- **Every citation is in References, and every reference is cited**, resolved through `list_publications` (below).
- **Tags stay out of the prose.** `[KG]` / `[interpretation]` / `[gap]` tags (Rule 3) belong to the notebooks; in `paper.md` the same distinction is made in words, as a paper would ("the data show …" vs "this suggests …").

*(N-import coculture: `paper.md` drifted into a process record — internal vocabulary, file paths, two cited papers missing from References and one listed but uncited — and a separate journal-style manuscript had to be written at the end.)*

**The conclusion leads with a findings table.** At the evaluation milestone, the Discussion opens with one table — one row per question or route, one column per reference or condition, a short verdict in each cell, and a last column saying whether the row was **tested as planned** or is **exploratory** — followed by **numbered plain-language meanings**, one per pattern in the table, each a sentence or two a biologist outside the project could restate. Caveats go in their own short section after the meanings, each tied to the finding it limits. Do not fold every caveat into the conclusion sentence: critic-hardened prose that carries all its caveats inline becomes unreadable. *(N-import coculture: the researcher rejected the critic-hardened conclusion as "a long paragraph that says we know nothing"; a findings table plus numbered meanings fixed it.)*

**Tested as planned, or exploratory.** A finding is *tested as planned* only if the proposal's decision rule produced it, on data nobody looked at before the plan was set (`decisions_log.md` lists what was seen early). Anything seen during planning, found during exploration, or produced by a rule changed after the results were seen is *exploratory*. Say this in the paper's own words: the findings table carries the label, and Methods states once, in a sentence or two, which analyses were specified in advance and what was examined before the plan was set ("Before the analysis was specified, we examined the expression of the control genes and of ntcA in MED4; results for MED4 are therefore exploratory"). An exploratory analysis says once, in Methods, that it is exploratory, and needs no per-row label. A finding that emerged from the results is exploratory; if its prediction was then written down and tested on KG data not used to find it, that test is *tested as planned*, and the paper says where the prediction came from and how independent the test data is (see [step-protocol.md — explore](step-protocol.md#explore-phase-run-milestones)).

**Put each finding in perspective.** After the numbered meanings, the Discussion compares each finding with the other KG experiments that bear on it, in a short table: the finding; each other experiment or publication (resolved through `list_publications`); whether it **agrees**, **disagrees**, or **can't tell**; and why, in a few words (different design, platform, timepoint, or strain; gene not measured). "Can't tell" is a valid and common answer. The comparison uses KG data only; any reading of why studies differ is interpretation and is worded as such. *(Workshop: "the grand overview it was able to generate across multiple papers" was the most-valued strength; it should be part of every evaluation, not an extra.)*

| paper.md section | Populated from |
|---|---|
| Question | Plan phase (proposal) |
| Background | Plan phase (KG entries and prior work) |
| Methods | Plan phase (framing) + methods milestone (implementation) |
| Results | analysis milestone |
| Discussion (findings table with labels → numbered meanings → comparison with other studies → caveats) | evaluation milestone |
| References | accumulates across every phase that cites publications |

References are populated as publications are cited. Every reference must be resolved through `list_publications` and cited by DOI — never drafted from intrinsic knowledge (see [anti-hallucination.md — Category 5.2](anti-hallucination.md#52-publication-attribution-from-training-knowledge)). Citation format inside prose can be short (author-year or numeric); the References section at the end carries a full reference with its DOI for each publication. KG experiment IDs are internal: they go in the notebooks, and `paper.md` names a dataset as a paper would (the publication, organism, condition, and the KG release used, stated once in Methods).

When the analysis ends, the paper ends. A recurring failure mode was deferring write-up to a final step that never happened — `paper.md`'s incremental growth prevents this. At the evaluation milestone's decide phase, read `paper.md` top to bottom once as a journal reviewer would, against the list above, before presenting it.

## gaps_and_friction.md (transitional)

A top-level file at `analyses/<slug>/gaps_and_friction.md` captures friction encountered during the analysis, distinct from decisions:

- **Decision** = a fork the analysis had to take, based on data → logged in the relevant milestone's `notebook.md` (or `decisions_log.md` if the fork was in the Plan phase)
- **Friction** = a problem that slowed us down, surprised us, or revealed a gap in methodology / KG / tooling → logged in `gaps_and_friction.md`

These can co-occur — a methodology gap can force both a decision and a friction entry. Log in both places when that happens.

**What goes in `gaps_and_friction.md`:**
- KG data issues and bugs encountered
- MCP tool schema or capability mismatches (see [anti-hallucination.md — Category 5.1](anti-hallucination.md#51-mcp-tool-capability-from-memory))
- Methodology gaps discovered during execution (nuances the framing didn't anticipate)
- Anti-hallucination corrections (claims from memory caught by verification)
- Process friction (things that slowed the work)
- **What worked** — a practice that caught an error or saved time and should be kept (a check, a prompt pattern, a way of splitting work). The log is the evidence base for writing up best-known methods, so it records wins as well as problems.

Each entry is prose with a date, a short name, a **type tag**, what happened, and — if relevant — the workaround and the downstream impact on methodology/KG/tooling. Type tags, one per entry, so logs from many analyses can be pooled:

| Tag | Use for |
|---|---|
| `[pitfall]` | a mistake the method or the agent made, and how it was caught |
| `[bkm]` | a best-known method: something that worked and should be kept |
| `[kg-gap]` | data the KG doesn't hold, or holds wrongly |
| `[tool]` | an MCP / explorer / Claude Code / environment problem |
| `[method-gap]` | something the methodology didn't anticipate |

Example: `2026-10-08 · [pitfall] · offset paging swapped rows` — then what happened, how it was caught, the workaround.

**Write the entry when it happens, not at the end.** The log decays late in a run, when the milestones are heaviest and the lessons most expensive. Two recurring leaks to watch: a `notebook.md` that points at an entry never written, and a **critic finding that exposed a gap the framing didn't anticipate** — that is friction (what the *next* analysis needs to know), not only a disposition (what you fixed in *this* one). The decide gate checks both — see [step-protocol.md — "decide" phase](step-protocol.md).

**Why this is transitional.** The methodology itself is under development. Every analysis teaches us something about what's missing or awkward. `gaps_and_friction.md` is the learning record that feeds back into methodology and KG/tooling improvements. Mandatory while the methodology is being stabilized — likely the first 3–5 analyses. Once the pattern settles, revisit: keep, make optional, or fold into `notebook.md`. Retirement criterion: when two consecutive analyses produce a near-empty `gaps_and_friction.md` (only incidental friction, no methodology gaps), propose retiring the requirement.

Append-only. Redo friction entries accumulate.

## Using `superpowers:brainstorming` for the Plan phase

The brainstorming skill's dialogue pattern (clarifying questions one at a time, exploring context, proposing approaches, then presenting the design section by section with a check-in after each) fits the whole Plan phase. Follow it literally: the five steps in [SKILL.md Rule 8 — Plan](../SKILL.md) are that pattern applied to a KG analysis. **Do not jump from a clarifying answer to writing `proposal.md`** — the walk-through is the point. **Three overrides apply:**

1. **Capture location.** The skill's default writes a design doc to `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`. Override: the design doc is `analyses/<slug>/proposal.md` (question + KG entries + framing), written *after* the five steps are agreed, and the dialog record lands in `analyses/<slug>/decisions_log.md`.
2. **KG grounding alongside the dialogue.** Brainstorming is pure conversation by default. The Plan phase adds MCP grounding (`list_publications`, `list_experiments`, `list_organisms` filtered to the prompt's context) before scope or framing decisions, and shows it — tables, plots, a decision tree when many experiments must be sorted. Record the facts in `decisions_log.md`. See the Just-in-time concrete rules above for the rationale.
3. **Terminal action.** The skill's terminal state is invoking `superpowers:writing-plans`. **Skip this.** The Plan phase's approval advances to the Run phase (methods milestone), not to implementation-plan writing. `proposal.md` *is* the plan — the enumerated framing replaces a separate implementation plan.

**How the dialog reads to the researcher.** One topic per message, in plain words. Show data rather than describing it. Ask open questions while exploring (steps 1–3); offer choices with a recommendation when deciding (step 5). Use a pop-up question only for a crisp choice, and make it stand alone: what it is about, what each option changes in the result, and the recommendation — text written before the pop-up may not be on screen. A choice with a sensible default is stated, not asked: "I set X because Y; change it?" A choice the researcher answers by picking "Recommended" without comment was probably not a real decision for them.

**`decisions_log.md` format.** It is the researcher's record, so it is written in plain language: no tool, field or file names in the decision text (a short `[KG]` tag on facts is fine). One section per step, each with a numbered table: `#`, decision, decided by (researcher / Claude proposed, researcher agreed / awaiting OK), reason. KG facts the step relies on are listed before its table, tagged `[KG]`. Open questions sit at the bottom until settled; caveats that emerge go in their own section and carry into `paper.md`. What the researcher chose to look at early (see [SKILL.md — Looking at the data](../SKILL.md)) is recorded here, without comment.

Brainstorming's own **spec self-review** and **user-reviews-the-spec** steps are kept — they become the Plan phase's close gate, plus one addition: the fresh-context critic runs on every proposal (interpretation-only) before the researcher approves. See [step-protocol.md — The Plan phase](step-protocol.md#the-plan-phase) for the ordered close.

**The close is a design review, not a sign-off.** Because the framing was agreed step by step, the review should bring few surprises. Present the critic's findings as *"the reviewer noticed X; I suggest Y, because Z"*, each with the choice it opens. Expect changes anyway, and after them run a scoped delta critic pass over what changed.

If the skill's preamble nudges toward writing a spec doc outside the analysis folder or invoking writing-plans at the end, treat those as defaults being overridden by this methodology skill (which has higher priority for research work in this repo).

## QC checkpoint types

What to show depends on the phase.

### KG entries + framing (Plan phase)
- Row counts per filter: experiments at each stage (started with → filter by organism → filter by assay → final)
- Sample rows of selected entries (experiment ID, publication, TPs, omics)
- Per-TP gene counts (`timepoints[].gene_count`) or the distinct-gene denominator (`distinct_gene_count`), **not** cumulative `gene_count` (see [anti-hallucination.md — Category 5.3](anti-hallucination.md#53-field-semantics-from-memory--cumulative-vs-per-timepoint-counts))
- Publication attributions resolved via `list_publications`
- Positive and negative controls selected from the KG: what distinguishes them; their coverage of TPs/conditions (checked in `spike/`); distributional QC
- Hypothesis in prose; statistics decision (named test or reasoned "none"); decision rule phrased in KG-operational terms (what table / metric / direction gives each reading of the target, and what would show nothing real)

### Computation / metric (methods milestone)
- Worked example: 2–3 genes or clusters through the formula with actual numbers, step by step
- Summary statistics of the output (distribution, range, NaNs)
- Sanity check against the positive controls ("glnA should score high — does it?")

### Scoring / comparison (analysis milestone)
- Full results table in markdown (the actual numbers, not prose summary)
- Best/worst scores, surprises, anything unexpected
- Cross-condition comparison with expectation check against the proposal's framing

### Evaluation (evaluation milestone)
- Findings table (question/route × reference/condition), each row labelled tested as planned or exploratory, and numbered meanings — see [paper.md growth pattern](#papermd-growth-pattern)
- Comparison with the other KG experiments that bear on each finding: agrees / disagrees / can't tell, and why
- Named predictions held / not held, read through the decision rule; if pre-registered labels were deferred, the rule is reported as "not evaluated as pre-registered", not replaced by a post-hoc criterion
- Sensitivity / LOO stability where applicable
- Harvested caveats

## Code lifecycle: analysis-first, productize later

Research code has two phases. Follow phase 1 during analysis; flag phase 2 candidates.

### Who writes what

Execution is delegated to a **coding subagent** (`superpowers:subagent-driven-development`); judgment stays in the main thread. The division is by artifact type:

- **The coding subagent authors** scripts (and their docstrings), data files, figures, logs, and a factual **run-manifest** (which scripts ran, command lines, KG queries, row counts, candidate anomalies). It executes and reports facts; it does not conclude.
- **The main thread authors** `notebook.md`, `paper.md`, `gaps_and_friction.md`, critical-review dispositions, and the decide-gate checklist — pasting the run-manifest verbatim into the mechanical notebook sections and writing every interpretive section itself.

Two rules keep delegation from breaking the skill's guarantees: the subagent loads `research-methodology` (or at least the KG / gene-identity / python-api / anti-hallucination references) so it doesn't re-hallucinate gene identities or miscount fields; and the *same* subagent stays alive across a milestone's invocations so those rules and the analysis context persist. Where no subagents are available, the same work runs inline — same rules, same artifacts, same ownership. See [SKILL.md Rule 8 — Run](../SKILL.md).

### Phase 1 — Analysis code (methodology-first)

Code lives in the analysis directory. Goal: correct methodology, not good software engineering.

**Separate reusable logic from scripts.** When the methods milestone introduces a new method, put the reusable logic in a utility module within the milestone folder (`methods/<module_name>.py`) and let scripts in later milestones import it. Scripts call utilities for specific data; utilities contain the methodology. This separation is what makes toy-testing possible and productization straightforward later.

**Methods modules describe methodology, not implementation scaffolding.** For novel utilities (scoring functions, metrics, gene-set operations), the module should be minimal — the formula with a worked example, expected I/O, and the minimum code to compute it. Regular extraction/plotting scripts are straightforward enough not to need a separate utility.

**Toy-data verification before real data** (`superpowers:test-driven-development`). When building a reusable utility, verify with hand-calculated toy examples first. Create small synthetic input, compute expected output by hand, run the utility, compare, log the verification in `methods/notebook.md`. Applies to anything in a shared utility; one-off scripts don't need it.

**A green suite is not evidence the code is correct on real input.** Two rules close the gap:

- **Fixtures use the real artifact's serialization form.** Build the toy input the way the data actually arrives — if the pipeline reads a CSV, the fixture's fields are the *strings* a CSV yields, not the Python objects you had in mind. A fixture whose input *type* differs from the real data hides every bug in the parsing layer while reporting all-green.
- **The main thread spot-runs the utility on one real row** before the milestone closes, and logs the result as a QC-gate line. Re-deriving one real case by hand is what catches what the suite structurally cannot.

*Why (Alteromonas coculture, 2026-07-23):* a reference-class assigner used `bool(row["in_candidate"])`; the real CSV stores that field as the string `"False"`, and `bool("False")` is truthy — on real data every system would have collapsed into one class, destroying the control structure the whole null comparison rested on. All 27 tests passed, because the fixture used Python booleans. A spot-run on one real CSV row caught it.

**When the method constructs the entity set, one spot-run is too thin — verify in four layers.** The pilot (layer 2) takes the spot-run's place, at a larger scale. Each layer catches an error class the others structurally cannot. Run them in this order, before the set is scaled to every organism or handed to the analysis milestone, and log each as a QC-gate line. **Layers 2 and 3 are done by someone other than the module's author** — the main thread, or a fresh agent that has not seen the module — or the answer key is not independent:

| Layer | What it is | What only it catches |
|---|---|---|
| 1. Real-serialization fixtures | toy inputs in the real file form (above) | parsing traps: `bool("False")`, pandas reading `"n/a"` as NaN |
| 2. Pilot against an independent answer key | for one organism or a handful of systems, build the expected answer step by step through MCP calls alone — not with the module — then diff the module's output against it | wrong API defaults and rule gaps (a gene-set size default that undercounted BRITE 57 vs 86; `fadD` called a transporter; a missing domain on `pstS`) |
| 3. API-usage review | before scaling, read how the module calls each explorer function against the explorer's source and `docs://` pages: defaults, sort order, paging, what a filter drops | tool-internal behaviour no count check sees (offset paging over a non-unique sort silently swapped rows while every count passed) |
| 4. Bin sample | before any tier or class rule is approved, look at a random sample of the members of each bin | rules that look right but fill bins wrongly (a "Medium" tier that was mostly helicases and proteases) |

The researcher sees layer 4's samples at the decide gate: a rule is approved on what it puts in the bin, not on how it reads. *(N-import coculture, 2026-10.)*

**Refine through the notebook QC cycle.** The co-define → do → show → explore → decide loop is how methodology gets validated. Formula corrections, edge cases, direction logic — all discovered through the researcher walking through concrete examples.

### Phase 2 — Productization (software-first)

After the analysis, if a utility proves reusable (used across multiple analyses), flag it for productization — a separate brainstorm with API design, tests, and documentation. It moves from the analysis directory to a shared package (e.g., `multiomics_explorer/analysis/`).

Don't productize speculatively. Wait for proven reuse — the analysis notebooks across multiple analyses are the evidence.
