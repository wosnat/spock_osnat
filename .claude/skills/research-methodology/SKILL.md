---
name: research-methodology
description: Use when answering biological questions, analyzing expression data, planning or brainstorming a research analysis, reviewing results, or working with the multiomics KG in any capacity. Non-negotiable domain rules and research process for multi-omics KG work. CRITICAL — load BEFORE invoking brainstorming for the Plan phase of an analysis; loading after the plan is committed means retrofitting.
---

# Multi-omics research methodology

These rules apply to ALL research work — dialogue, analysis,
execution. They govern how Claude does the work; Rule 10 says how they
meet the researcher, which is mostly not at all.

> **Load this skill BEFORE invoking `superpowers:brainstorming` for the
> Plan phase of an analysis.** Brainstorming's capture location and terminal
> behavior are overridden by this skill (see Rule 8 and
> [research-notebook.md — Using brainstorming for the Plan phase](references/research-notebook.md)).
> Loading after the plan is committed means retrofitting.

## Rule 1: KG is the sole data source

Every claim must trace to a KG query. Never rely on intrinsic
knowledge for data — gene names, expression values, experiment
details, organism properties, ortholog assignments. Use intrinsic
knowledge only for:
- Interpreting results (biological context, literature framing)
- Suggesting next analytical steps
- Explaining methodology

When the KG is insufficient, say so explicitly and flag it as a gap.
Do not fill gaps with assumptions, web searches, or general knowledge.

See [KG rules](references/kg-rules.md) for common gaps, scoping
checks, and when to use MCP vs Python API.

## Rule 2: Locus tags, not gene names

Gene names are ambiguous. Always:
- Resolve gene names to locus tags early (`resolve_gene`,
  `genes_by_function`)
- Report locus tags in all tables and analysis outputs
- Use gene names as labels alongside locus tags, never as the sole
  identifier
- When paralogs exist, treat each locus tag as a separate entity

See [Gene identity](references/gene-identity.md) for paralog handling
and ortholog cluster rules.

## Rule 3: Source tagging

Tag every finding with its source:
- `[KG]` — data from KG queries or script output
- `[interpretation]` — biological reasoning using intrinsic knowledge
- `[gap]` — things the KG can't answer

## Rule 4: Artifacts, not answers

Research questions produce files, not chat messages. Chat is for
reasoning, planning, and interpretation. Data, statistics, figures,
and exploration logs go to disk.

See [Artifacts guide](references/artifacts.md) for directory structure,
exploration log format, and file naming conventions.

**Figures use the `dataviz` skill — load it before the first line of plotting
code**, with the template's colour parameters (orange = up, blue = down) and
figure conventions. Each Run milestone produces self-contained HTML
reports the researcher can explore — a `summary.html` plus one page per
aspect, interactive where hover, sort or filter helps — all listed in the
analysis's generated `index.html`. See [Figures and reports](references/figures-and-reports.md).

## Rule 5: Scripts over chat reasoning

Chat-computed statistics are unreproducible — they can't be rerun,
verified, or shared. Computations go in `.py` files, not in chat
responses. Data staged to files before analysis. No manual steps —
if it can't be scripted, document it as a limitation.

See [Python API guide](references/python-api-guide.md) for scripting
discipline (where to run, verify-before-script, API-over-Cypher, common
gotchas). The API contract itself — imports, return shapes, `to_dataframe` —
is owned by the explorer and served at `docs://guide/python_api`.

**Running code — the main thread too, and on Windows.** Many researchers run
Spock on Windows 11 (Git Bash), so these hold for every quick check, not only
for the coding subagent:
- Write Python to a file (the milestone's `scripts/`, or `spike/` in the
  Plan) with the Write tool, then `uv run python <file>`. Never a shell
  heredoc or a `python -c "..."` carrying quotes, prose, `$` or backslashes —
  quoting breaks in Git Bash.
- `uv run python`, not `.venv/bin/python` (on Windows it is
  `.venv\Scripts\python.exe`); `uv run` works everywhere.
- `encoding="utf-8"` on every file read and write; add `-X utf8` when a script
  prints non-ASCII (arrows, Greek letters, µ) — the Windows console is cp1252.
- Paths through `pathlib`, relative to the repo root; no hard-coded `/tmp` or
  backslashes in code.

**Call the highest-level tool that answers the question; don't reinvent or
re-wrap what the package ships.** Before building any scoring/statistics
utility, check the package's analysis surface (e.g. `pathway_enrichment` runs
the whole DE→ORA pipeline in one call — don't hand-roll Fisher, and don't wrap
its primitives either). Reserve custom code for composition the tool genuinely
doesn't do. Reinventing risks subtle errors (wrong background, lost
normalization) and wastes effort.

**Exception: interactive discovery steps.** Steps that are
inherently exploratory (browsing available data, classifying
experiments, scoping what the KG contains) may be done
interactively rather than scripted. These steps must still produce
a frozen output file (CSV) and a notebook entry documenting the
reasoning. Computations — statistics, scores, enrichment — always
go in scripts. See [Research notebook — Code lifecycle](references/research-notebook.md#code-lifecycle-analysis-first-productize-later) for the pattern.

## Rule 6: Statistical rigor

Expression data without proper statistical treatment produces
misleading claims — wrong background sets, uncorrected multiple
testing, and magnitude comparisons across platforms are common
failure modes.

See [Statistical rigor](references/statistical-rigor.md) for what
the KG provides, what you must compute in scripts, and what to flag.

## Rule 7: Don't hallucinate

See [Anti-hallucination](references/anti-hallucination.md) for
concrete failure modes and prevention patterns.

## Rule 8: The research arc — Plan, then Run

Every analysis is two phases: a **Plan** phase that converges on a
research proposal, and a **Run** phase that executes against it.
**Open the analysis by posting the arc as a plain-language to-do list**
so the researcher sees the whole path and where you are — ordinary
words, not internal codes.

The arc leans on the superpowers skills where they genuinely fit, and
keeps its own machinery only where research work needs something they
don't provide.

### Plan — a conversation built with the researcher

The Plan phase is one grounded `superpowers:brainstorming` conversation,
walked through with the researcher in five steps. Each step is a short
dialog, not a batch of questions, and ends with a plain-language **"so
far" summary** the researcher confirms before the next step. **Do not
write `proposal.md` until all five steps are agreed** — the proposal
records what was agreed and holds no surprises. *(ntcA/urea: the first
real question the researcher got was a pop-up about a fold-change
threshold, for a plan they had not been shown, fixing a critic finding
they had not seen. They answered "Recommended" twice, then asked "what is
the plan — present it to me".)*

1. **Clarify the question, and size it.** What the researcher wants to
   know; what the result is for (a standalone result or part of a paper;
   whose hypothesis); and the **mode** (below). If the question is too big
   for one analysis — several parts that each need their own answer, or
   many stress types, strains and papers to sort before anything can be
   scored — propose splitting it into smaller analyses, each with its own
   short plan and its own result, done one after another. *(General
   stress response: three parts in one plan; about 60 decisions over a
   week, and the plan never closed.)*
2. **Show what the KG holds.** Experiments, designs, coverage, and how
   each experiment's data look — as a table or a plot, not a description.
   When there are many experiments to sort, offer a decision tree showing
   where each one lands, and keep it current as decisions are made.
3. **Agree the general approach**, in plain words.
4. **Check that the approach can work.** A quick, throwaway test in
   `spike/` of what the data and annotations can actually tell apart:
   annotation depth and recall against a curated source, coverage of the
   candidate controls, a random sample of what lands in each group, and
   distribution shape per experiment when experiments come from different
   platforms. **Required** when the method builds its own gene set or
   combines experiments from different platforms; skip it otherwise. It
   may send you back to step 3. *(N-import: TCDB substrates inherited from
   the subfamily, a "Medium" tier full of helicases, and curated
   transporters missing from the gene universe all surfaced in the methods
   milestone, after the plan was locked; the module went through seven
   versions.)*
5. **Set the framing** — control-validated mode only (below). Offer a
   plain-language explainer for any statistics or method the researcher
   has not used before.

Then: write `proposal.md` → self-review → critic → bring the critic's
findings to the researcher as *"the reviewer noticed X; I suggest Y,
because Z"* — never fix them silently and then ask about a detail → delta
critic pass over whatever changed → approval commit. If the researcher
says "go fast", shorten the steps, but still show the summary before
writing anything. See
[step-protocol.md — The Plan phase](references/step-protocol.md#the-plan-phase).

**The dialog is recorded in `decisions_log.md`** at the analysis root:
one numbered table per step — the decision, who decided it (researcher;
Claude proposed and researcher agreed; awaiting OK), and why — with KG
facts listed before the choices they inform and open questions at the
bottom. Commit after each step. *(General stress response: this log,
kept by hand, worked better than the template's notebook.)*

Three overrides apply to brainstorming here (see
[research-notebook.md](references/research-notebook.md#using-superpowersbrainstorming-for-the-plan-phase)):
the design doc is `proposal.md` in the analysis folder, not
`docs/superpowers/specs/`; the dialog is grounded in live KG queries, not
assumptions; and the terminal action is **begin the Run phase**, not
`writing-plans`.

#### Two modes — chosen in step 1

- **Exploratory** — "show me what the KG has on X". Agree the scope and
  the deliverables (which overviews, which maps); there is no framing.
  Every result is labelled exploratory. A pattern that emerges from the
  results (a gene grouping, a link between pathways) may be pursued here
  when the researcher wants it — check it, write down what it predicts,
  and test it if the KG has the data (see Run, below). What is not done is building persuasion for a
  mechanism the data did not raise: that becomes a *suggested follow-up
  analysis*. *(Amino-acid pathways: an atlas request drifted into
  "evidence visuals" for a carbon–nitrogen mechanism, with no framing
  behind them. hli light stress: an unplanned responder / quiet gene split
  found in clustering became the paper's best finding.)*
- **Control-validated** — "does X happen under Y?". The method must give
  the expected result on positive and negative controls before it is
  applied to the target. The full framing below applies. Order in the
  Run phase: **controls pass → method frozen → targets scored once,
  last.** Thresholds and normalisation are tuned on the controls and
  reference experiments, never on the targets.

**Building a catalogue or classification** — transport systems, a
candidate list, tiers, classes — is **control-validated**, with the
classifier as the method, even when there is no hypothesis (state
"descriptive: the catalogue is the result"). Positive controls are known
members it must recover (curated genes, or a hand-built answer key for a
pilot strain); negative controls are what it must not include or must not
label (a random sample of each bin — e.g. helicases in a transporter
tier, a sulfate permease listed as an amino-acid importer); the decision
rule is the tier and class rules, fixed on the controls before the
catalogue is built across all strains. Step 4 is where most of the
annotation limits surface. If the catalogue feeds a further question
(cross-feeding, say), split it: the catalogue is its own analysis, and
the next one uses it as a trusted input. Its methods milestone is a
discovery milestone (below).

Almost all KG data is published and already analysed, so Spock does not
claim confirmatory hypothesis testing. Where a result needs confirming,
the output is a prediction for new experiments — or a test on KG data
nobody has looked at (another strain, paper or data type), where it
exists.

#### Looking at the data before the plan is set

Look at anything; nothing is refused or debated. **Exactly one thing
triggers a question:** in control-validated mode, just before showing
*the data that answers the question* — the target genes' values in the
target comparison, for an expression question; gene presence in the
target strains, for a genome comparison. What counts depends on the
question, not on the kind of data. Ask, in these words or close to them:

> "This will show the answer to our question. If we look now, before the
> plan is final, the result can no longer serve as a test of our
> prediction. It will be reported as exploratory. Look now, or wait until
> the plan is set?"

Everything else is free and needs no comment: what exists; coverage;
ontologies, annotations, orthologs, gene neighbourhoods and other genomic
features; annotation limits; distributions per experiment (comparing them
across experiments is encouraged — microarray, RNA-seq and proteomics
differ, and that difference must not be read as biology); and the control
genes (looking at controls and calibrating on them is what
control-validated means). Two habits keep the question rare: check
coverage and detection with counts (`summary=True`), not values; and
record in `decisions_log.md` any experiment kept or dropped because of
how the controls looked, since that shapes the result. If the researcher
chooses to look, record what was seen in `decisions_log.md`, without
further comment; it appears once, as a sentence in `paper.md` Methods.
Exploratory mode tracks nothing.

#### Framing (control-validated mode)

**Framing is enumerated, not sketched.** The recurring failure is a
vague plan that looks fine, gets approved, then falls apart in
execution and forces a redo. Concreteness surfaces a bad plan *at plan
time*. Every framing states, specifically:

- **Hypothesis** — in prose
- **Approach** — how you'll analyze and why it answers the question,
  concrete enough to poke holes in (not the code itself)
- **Statistics plan** — a deliberate decision every time: the specific
  statistical test(s) and thresholds, *or* an explicit "no formal
  stats, because descriptive," with the reasoning. Never left implicit.
- **Positive controls** — the named genes, pathways or experiments that
  must show the expected effect if the method works, each with its
  expected result stated, and their coverage checked in step 4. If a
  positive control fails, the target result is *uninterpretable*, not
  negative.
- **Negative controls** — a class that should *not* score if the signal
  is genuine, with its expected score stated rather than assumed to be
  zero (growth genes move with growth rate; an alternative nitrogen
  source can share part of the nitrogen response). Positive controls say
  what a hit looks like; negative controls say what "nothing real" looks
  like. Without both, a true null and a method that could not detect
  anything are indistinguishable. A null is a valid outcome; the
  evaluation milestone writes it up as a bounded negative.
- **Decision rule** — every reading of the target named in advance
  (e.g. up / down / suggestive only / not changed), each with its
  threshold, so no outcome is judged after the data are seen.
- **Design comparability** — per experiment used: its role; what each
  arm is compared against and that reference sample's physiological
  state (growth phase, nutrient status, sampling day); whether contrasts
  share samples or one fitted model; and what it can and cannot confirm.
  Read the KG first: `list_experiments(verbose=True)` `design_notes`
  often record how arms are matched, the reference culture's state and
  sampling day, and separate runs. **Ask the researcher only for what
  the notes do not hold**, saying what they already state; mark those
  cells researcher-supplied. *(hli light stress: culture states were
  asked for and logged as KG gaps, though `design_notes` held them.)* A
  comparable metric over incomparable designs is the recurring hole
  (an FDR family size, then a late-decline "early" reference and
  contrasts that were one fitted model).

**Say what the methods milestone is.** If the method *builds* the
entity set (transport systems, a candidate list, tiers, classes), the
methods milestone is a **discovery milestone**: plan for many decisions
at its decide gate and for four verification layers instead of one
spot-run — real-format fixtures, a pilot against an independent
MCP-only answer key, an API-usage review, and a random sample of every
bin before its rule is approved. See
[research-notebook.md — Phase 1](references/research-notebook.md#phase-1--analysis-code-methodology-first).

**Two principles, working together.** *Just-in-time* governs **what**
the plan commits to — only what the data so far supports; no
speculative padding for what the analysis might later need.
*Enumeration* governs **how** it states those commitments — concretely
and reviewably. Ground the conversation in KG counts before you frame;
start with the simplest framing that fits; add predictions or stability
checks only when a specific finding forces them.

See [Research notebook — Just-in-time formalization](references/research-notebook.md#just-in-time-formalization)
for the per-phase concrete rules.

### Run — the iterate loop

The Run phase executes the proposal across three milestones, each in
its own named folder: **`methods/` → `analysis/` → `evaluation/`**.
Each milestone advances through the loop **co-define → do → show →
explore → decide** — the researcher agrees the milestone's scope at
*co-define* (before the work) and approves at *decide* (after it).
**Commit every iteration** (`<slug> <phase>: iteration — …`), and close
each milestone with an approval commit (`… approved — …`) only after
explicit approval. When the evaluation milestone is approved, **ask the
researcher to push** — forks are public, so never push unasked. See
[step-protocol.md — Commit structure](references/step-protocol.md#commit-structure).

- **co-define** — before doing the work, say in plain words what you
  propose this milestone should do and why, and let the researcher
  shape it. Default to co-defining every milestone; the researcher may
  wave through a routine one, but never skip co-define for a genuine
  judgment call (what to compare, how to define a set, which controls).

Research execution is exploratory, so the Run loop is **ours, not
`superpowers:executing-plans`** — that skill assumes a locked,
pre-specified plan with bite-sized tasks, which fights how analysis
actually unfolds. But call the superpowers skills at the beats where
they do fit:

- verifying a new method against hand-computed toy data →
  `superpowers:test-driven-development`
- an analysis that breaks or returns something surprising →
  `superpowers:systematic-debugging`
- before claiming a milestone is done →
  `superpowers:verification-before-completion` (this *is* the
  decide-gate checklist)
- an adversarial second opinion before claims land → the
  `critical-review` skill, at the **analysis** milestone (data-integrity
  + interpretation) and the **evaluation** milestone (interpretation
  only) — and at the **methods** milestone too whenever it emits a data
  artifact that downstream milestones consume (a parts list, a
  classification table, a curated gene set): that file carries claims —
  labels, confidence flags, class assignments — so it gets the
  data-integrity lens, not a pass because "methods is only code."
  The critic reviews only that milestone's own files (the proposal and
  earlier milestones are trusted inputs), with a lens matched to the
  milestone, so the researcher reviews a vetted milestone, not a first
  draft. Kept light: matched lens, milestone-scoped, artifact only when
  it finds something. **A milestone that keeps producing after its
  critic pass earns a delta pass** over the new work before it closes.
  See [step-protocol.md GATE C](references/step-protocol.md).

**Explore what the researcher asks; suggest the rest.** Interactive
exploration — in the Plan, in evaluation, and in methods when the method
is complex or results are unexpected — is one of Spock's strengths, and
exploration the researcher asks for is free: findings you did not plan
for are discovery, not scope drift, provided they pass the decide gate
before being committed as findings. What Claude does **not** do is start
extra analyses, plots or reports on its own. Its own ideas become a short
*"I could also…"* list for the researcher to pick from (see Rule 10).
*(Workshop: "additional irrelevant plots", "additional analyses that I did
not ask for — these are tokens being burnt".)*

**Delegate execution to a coding subagent; keep judgment in the main
thread.** The KG queries and script iterations that make up *do* and
*show* generate a lot of noise. Run them in a coding subagent
(`superpowers:subagent-driven-development`) so the researcher-facing
thread keeps only the artifacts and the decisions. Use the template's
**`kg-coder`** agent, which preloads this skill and `dataviz`, and
continue it with `SendMessage` across the milestone. The subagent writes
and runs the scripts, queries the KG, and produces the tables and
figures; it is re-invoked for each exploration question as it arises.
Two rules keep this from quietly breaking the skill's guarantees:

- **The domain rules ride along.** The subagent loads
  `research-methodology` (or at least the KG / gene-identity /
  python-api / anti-hallucination references) into its own context — a
  fresh agent that doesn't know locus-tags-not-names or
  cumulative-vs-per-timepoint counts produces exactly the errors those
  rules prevent. Keep the *same* subagent alive across invocations so
  the rules and analysis context persist and it doesn't re-hallucinate
  on a later call.
- **Artifacts come back, not conclusions.** The subagent returns
  committed scripts, data, figures, logs, and a factual run-manifest
  (what ran, command lines, row counts, candidate anomalies). It does
  not get to *conclude*. The main thread reads the real files and owns
  what they mean — that is what preserves the anomaly-catch (a heatmap
  narrated "all 5 UP" while the data file shows them negative).

**Every finding carries a label, and is put in perspective.**
At the evaluation milestone, each finding in `paper.md` is marked
**tested as planned** (read through the proposal's decision rule, on data
not looked at before the plan was set) or **exploratory** (everything else:
seen during planning, found during exploration, or changed after the
results were seen). An exploratory analysis is exploratory throughout and
says so once. A finding that *emerged* from the results — a pattern no plan
asked for — is welcome and exploratory. Its prediction is written down; if
KG data not used to find it exists, the researcher decides whether it is
tested here or in a follow-up, and a test run here is *tested as planned*.
See [step-protocol.md — explore](references/step-protocol.md#explore-phase-run-milestones). And because bringing many papers together is one of Spock's
strengths, the evaluation also places each finding against the other KG
experiments that bear on it: agrees, disagrees, or can't tell, and why. See
[research-notebook.md — paper.md growth](references/research-notebook.md#papermd-growth-pattern).

**The main thread owns `notebook.md`.** The subagent authors code, data,
figures, and logs; the main thread authors the notebook — pasting the
subagent's factual run-manifest verbatim into the mechanical sections
and writing every interpretive section (Context, what the results mean,
Surprises, Decisions, Advance rationale) itself, with the researcher.
Single owner keeps the judgment record coherent and keeps conclusions
where the researcher is. See
[research-notebook.md — Code lifecycle](references/research-notebook.md#code-lifecycle-analysis-first-productize-later).

### What this replaces

- **No `spec.md` / `plan.md`** — `proposal.md` is the plan; the Run
  milestones execute it
- **One decisions file, for the Plan phase only** — `decisions_log.md`
  records the Plan dialog (it replaces `proposal_notebook.md`); Run-phase
  decisions live in the milestone's `notebook.md` where they were forced
- **No `hypotheses.md`** — the hypothesis lives in `proposal.md`
- **No cross-file labels** (H1/P3/D8/T4) — labels are document-scoped
  and must be paired with a short readable name in the same paragraph
- **`proposal.md` + per-milestone `notebook.md` + single `paper.md`**
  at the analysis root replace the single exploration notebook +
  methods.md + caveats.md. `paper.md` is written for the paper's
  reader — journal prose that drops into a manuscript, with no internal
  vocabulary, file paths or process history; its conclusion opens with
  a findings table and numbered meanings, caveats in their own section
- **`gaps_and_friction.md`** (transitional) captures methodology / KG /
  tooling friction — and what worked — each entry type-tagged
  (`[pitfall]`, `[bkm]`, `[kg-gap]`, `[tool]`, `[method-gap]`), distinct
  from decisions

See [Step protocol](references/step-protocol.md) for commit timing,
decide-gate checklist, hard gates, and redo path. See
[Research notebook](references/research-notebook.md) for notebook
format, `paper.md` growth, `gaps_and_friction.md`, and the
brainstorming override for the Plan phase. See
[Artifacts guide](references/artifacts.md) for directory structure and
scaffold creation.

## Rule 9: Plain language; describe before interpreting

Write in plain English. Numbers and direction first, interpretation
second. Don't reach for fancy vocabulary when ordinary words work.

**No unagreed vocabulary with the researcher.** Don't introduce terms,
codes, or step-IDs in conversation that you haven't defined and the
researcher hasn't accepted — internal labels (gene-set IDs, ontology
codes, "decide gate", bare step numbers used as names) read as opaque
shorthand and shut the researcher out. If a technical term is genuinely
needed, say what it means in plain words the first time. The test: could
the researcher restate what you just said back to you? If not, you've
leaned on jargon.

**Banned before the evaluation milestone** — i.e. throughout the Plan
phase and the methods and analysis milestones (these signal commitment
before the analysis has earned it): "striking", "massive", "central
finding", "biologically loaded", "biologically explosive", "reframes",
"rich", "hand-wavy" as praise. Reserve interpretive vocabulary for the
evaluation milestone. This restrains Claude's *own* wording; when the
researcher asks what a result means before evaluation, answer, and label
the answer provisional.

**Describe before interpreting.** Write the numbers and direction
first ("5 markers show RNA log2FC < 0 and protein log2FC > 0 at
coculture days 31–89"). Tag interpretation `[interpretation]` and
list plausible alternatives.

**Verify before generalizing.** Words like "all", "every",
"systematically", "primarily", "no genes" require a query against
the data file, not a heatmap glance. If you write "all 5 are UP",
check all 5 in the data first.

**Proposals must cite specific data or friction.** When suggesting
a fix, framework, or methodology change, point to the data or
incident that motivates it. One occurrence is a note; process
change needs the same friction in two analyses. Don't enumerate
speculative proposals.

See [Anti-hallucination — 2.6 Emotive vocabulary and speculative proposals](references/anti-hallucination.md#26-emotive-vocabulary-and-speculative-proposals).

## Rule 10: Working with the researcher

The rules in this skill are limits on **Claude's own behaviour**. They
were written because Claude, on its own initiative, reported values from
memory, identified genes by name alone, and read absence from data that was
never reported — not because researchers asked it to. They bind Claude
silently and are not for the researcher to manage. Workshop researchers
found Spock "overwhelming" and did not "fully follow its thought process";
hearing the rules explained made that worse.

**Don't narrate the rules.** Mention a rule only when it changes what the
researcher gets or has to decide, and then in one sentence about the
consequence, in plain words. No rule or gate names, no "under our rules",
no "peeking", no "I noted in the log that…". Record quietly in
`decisions_log.md` or `notebook.md` and move on. *(ntcA, amino-acid
genomics: "One caveat for the record: looking at results before the rules
are locked is the 'peeking' the plan guards against, so I'll note it…";
"Under our rules I can't use their claims as data…" — both unprompted.)*

**The researcher can lift a rule; Claude never lifts one on its own.** If
the researcher explicitly asks to step outside the KG — "use what you
know", "use this paper" — do it and label the result ("from memory, not
from the KG", "not from the KG"). Never answer with "I'm not allowed to",
and never refuse without saying why. The only refusal seen so far was to
look at results during planning, given without explanation; that case now
follows the one question in Rule 8.

**Process steps are offered, not imposed.** The researcher may wave
through a co-define, ask to run methods and analysis in one go, or ask to
see a result before the critic has run — show it marked "not yet
reviewed"; the review still runs before the milestone closes. Each
milestone still gets its own approval. Record each waiver in the
milestone's `notebook.md`.

**Suggest, don't run.** Do what was asked, and only that. Extra analyses,
plots, reports or edits Claude thinks of go into a short *"I could
also…"* list at the end of the message. Change only what the researcher
asked to change; any other change Claude thinks is needed is suggested,
not made. *(Workshop: "it changed things we didn't ask".)*

**Take several comments at once.** When the researcher sends several
comments in one message, number them, say in one line each what you will
do, work through them as a checklist, and report each as done.
*(Workshop: "it was hard to give it several comments at once, so we split
them into small points and ran each separately".)*

**Show where we are.** During an analysis, open each message with a
one-line map, e.g. *Plan: ✓ question · ✓ KG data · → approach · can it
work? · framing* or *✓ Plan · ✓ Methods · → Analysis · Evaluation*.

**Questions stand alone.** One topic per question. Each says what it is
about, what each option changes in the result, and which you recommend —
text before a pop-up may not be on screen. A choice with a sensible
default is stated, not asked: "I set X because Y; change it?"

**Keep the overview current.** `overview.html` at the analysis root is
the researcher's page: where we are, the question and mode, the plan in
small tables, decisions so far with who made them, open questions, and —
once results exist — the findings table with links to the reports. Update
it when a Plan step closes and at every milestone's decide phase. A page
the researcher doesn't know about is not an interface: **open it in the
browser when it is first created** (`start "" <path>` on Windows, `open` on
macOS, `xdg-open` on Linux) and tell the researcher in one line that this
is their page for following the analysis; after that, **end every message
that updates it with a one-line link** ("Overview updated: <path>"). The
page reloads itself, so a tab left open stays current. See
[artifacts.md — Who reads which file](references/artifacts.md#who-reads-which-file).
*(ntcA and amino-acid genomics: the researcher asked for a plain-language
overview page by hand in both.)*

## References — read on demand, not all at once

- [Step protocol](references/step-protocol.md) — read at the start of every analysis execution; owns commit timing, decide-gate checklist, hard gates, redo path
- [Research notebook](references/research-notebook.md) — read when starting or resuming an analysis; owns notebook format, paper.md growth, gaps_and_friction.md, brainstorming override for the Plan phase
- [Artifacts guide](references/artifacts.md) — read at scaffold time or when unsure about directory structure, per-milestone folders, QC naming
- [Figures and reports](references/figures-and-reports.md) — read before making any figure or report page; owns the colour parameters, figure conventions, and report contents
- [Anti-hallucination](references/anti-hallucination.md) — read before presenting findings; covers tool-schema claims, publication attribution, field semantics, and the other anti-hallucination patterns
- [KG rules](references/kg-rules.md) — read when scoping a new analysis or uncertain about data sourcing vs literature
- [Gene identity](references/gene-identity.md) — read when working with gene names, paralogs, or orthologs
- [Python API guide](references/python-api-guide.md) — read before writing extraction or analysis scripts
- [Statistical rigor](references/statistical-rigor.md) — read when computing enrichment, comparing across studies, or reporting p-values
