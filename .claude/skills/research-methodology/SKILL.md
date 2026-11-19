---
name: research-methodology
description: Use when answering biological questions, analyzing expression data, planning or brainstorming a research analysis, reviewing results, or working with the multiomics KG in any capacity. Non-negotiable domain rules and research process for multi-omics KG work. CRITICAL — load BEFORE invoking brainstorming for the Plan phase of an analysis; loading after the plan is committed means retrofitting.
---

# Multi-omics research methodology

These rules govern how Claude does research with the multiomics KG — in
dialog, analysis and execution. They bind Claude, not the researcher; Rule 10
says how they meet the researcher, which is mostly not at all.

> **Load this skill before `superpowers:brainstorming` for the Plan phase.**
> It overrides where brainstorming writes and what it does at the end
> ([plan-phase.md](references/plan-phase.md#brainstorming-overrides)).

## Rule 1: The KG is the sole data source

Every claim traces to a KG query. Never take data from memory — gene names,
expression values, experiment details, organism properties, orthologs. Your own
knowledge is for interpreting results, suggesting next steps and explaining
methods. When the KG can't answer, say so and log it as a gap; don't fill it
with assumptions, web searches or general knowledge.

**One exception: literature citations for the paper.** With the researcher's
authorisation, a web search may find citations for Background and Discussion —
never data ([research-notebook.md — Citations](references/research-notebook.md#citations-and-supplementary-information)).

See [kg-rules.md](references/kg-rules.md) for common gaps, scoping checks and
MCP vs Python API.

## Rule 2: Locus tags, not gene names

Gene names are ambiguous. Resolve them to locus tags early (`resolve_gene`,
`genes_by_function`); report locus tags in every table, with names as labels
beside them, never alone; treat each paralog as its own entity. See
[gene-identity.md](references/gene-identity.md).

## Rule 3: Source tagging

Tag every finding with its source: `[KG]` (a KG query or script output),
`[interpretation]` (reasoning from your own knowledge), `[gap]` (the KG can't
answer). Tags belong in chat, notebooks and `decisions_log.md`, not in
`paper.md`, which makes the same distinction in words. The first time a tag
appears in the conversation with a researcher, say in a few plain words what it
means.

## Rule 4: Artifacts, not answers

Research questions produce files, not chat messages. Chat is for reasoning,
planning and interpretation; data, statistics, figures and logs go to disk
([artifacts.md](references/artifacts.md)). **Figures use the `dataviz` skill —
load it before the first line of plotting code** — with the template's colours
(orange = up, blue = down). Each Run milestone produces self-contained HTML
reports listed in the analysis's `index.html`
([figures-and-reports.md](references/figures-and-reports.md)).

## Rule 5: Scripts over chat reasoning

Statistics computed in chat can't be rerun, checked or shared. Computations go
in `.py` files; data is staged to files first; anything that can't be scripted
is documented as a limitation. See
[python-api-guide.md](references/python-api-guide.md); the API contract itself
is served by the explorer at `docs://guide/python_api`.

**Running code — the main thread too, and on Windows** (many researchers run
Git Bash on Windows 11):
- Write Python to a file with the Write tool (the milestone's `scripts/`, or
  `spike/` in the Plan), then `uv run python <file>`. Never a heredoc or a
  `python -c "..."` with quotes, prose, `$` or backslashes — quoting breaks.
- `uv run python`, not `.venv/bin/python`.
- `encoding="utf-8"` on every file read and write; `-X utf8` when printing
  non-ASCII (the Windows console is cp1252).
- Paths through `pathlib`, relative to the repo root; no `/tmp`, no backslashes.

**Call the highest-level tool that answers the question.** Before writing any
scoring or statistics code, check what the package ships — `pathway_enrichment`
runs the whole DE → ORA pipeline in one call; don't hand-roll Fisher or wrap its
primitives. Custom code is for composition the tools don't do; reinventing
risks a wrong background or lost normalisation.

**Exception: interactive discovery** — browsing what exists, classifying
experiments, scoping the KG — may be done interactively, but still ends in a
frozen output file and a notebook or decisions-log entry. Statistics, scores
and enrichment are always scripted.

## Rule 6: Statistical rigour

Wrong background sets, uncorrected multiple testing and magnitude comparisons
across platforms are the common failures. See
[statistical-rigor.md](references/statistical-rigor.md) for what the KG provides
and what you must compute.

## Rule 7: Don't hallucinate

See [anti-hallucination.md](references/anti-hallucination.md) for the concrete
failure modes and their checks.

## Rule 8: The research arc — Plan, then Run

Every analysis is a **Plan** that ends in a reviewed `proposal.md`, then a
**Run** of three milestones. The first message of an analysis shows this whole
arc as a plain-language to-do list; after that, the one-line map (Rule 10)
shows where you are.

**Plan** — one grounded `superpowers:brainstorming` conversation in five steps,
each ending with a "so far" summary the researcher confirms and recorded in
`decisions_log.md`: (1) clarify and size the question, and choose the mode;
(2) show what the KG holds; (3) agree the approach; (4) check it can work, in
`spike/`; (5) set the framing. Then `proposal.md` → self-review →
`proposal-critic` → findings brought to the researcher as suggestions → delta
pass → approval commit. **Read [plan-phase.md](references/plan-phase.md) before
step 1.**
- **Two modes.** *Exploratory* — scope and deliverables, no framing, every
  result exploratory. *Control-validated* — controls pass → method frozen →
  targets scored once, last.
- **Looking at data is free**, with one exception: in control-validated mode,
  ask before showing the data that answers the question.
- **Big questions are split** into smaller analyses done in order.

**Run** — `methods/` → `analysis/` → `evaluation/`, each going **co-define → do
→ show → explore → decide**: the researcher agrees the scope before the work
and approves after it. Commit every iteration; an `approved` commit closes each
milestone; ask before pushing. **Read
[step-protocol.md](references/step-protocol.md) before the first milestone.**
- **Delegate execution, keep judgment.** The `kg-coder` agent writes and runs
  scripts and returns files plus a factual run-manifest; the main thread reads
  the real files and writes every interpretation.
- **A fresh-context critic** reviews each claim-bearing milestone before the
  researcher sees it, plus a delta pass when claims grow (the `critical-review`
  skill).
- **Explore what the researcher asks; suggest the rest** (Rule 10). Findings no
  plan asked for are welcome and exploratory.
- **Every finding is labelled** *tested as planned* or *exploratory*, and set
  against the other KG studies that bear on it: agrees, disagrees, can't tell.

Superpowers skills at the beats where they fit: toy-testing a method →
`test-driven-development`; something breaks or surprises →
`systematic-debugging`; reading the methods module and statistics scripts
before the critic → `requesting-code-review` (step-protocol, decide);
before calling a milestone done →
`verification-before-completion` (the decide-gate checklist). The Run loop is
not `executing-plans`, which assumes a locked plan of small tasks.

**The analysis's files:**

| File | What | Rules in |
|---|---|---|
| `decisions_log.md` | the Plan dialog: facts, decisions, who decided | [plan-phase.md](references/plan-phase.md#how-the-dialog-reads-decisions_logmd) |
| `proposal.md` | the plan as agreed (no separate spec or plan file) | [plan-phase.md](references/plan-phase.md) |
| `<milestone>/notebook.md` | what was done and found; decide-gate checklist | [research-notebook.md](references/research-notebook.md#notebookmd) |
| `paper.md` → `paper.html` | journal prose for the paper's reader | [research-notebook.md](references/research-notebook.md#papermd) |
| `overview.html` | the researcher's plain-language page | [artifacts.md](references/artifacts.md#who-reads-which-file) |
| `gaps_and_friction.md` | what slowed us, what worked, tagged | [research-notebook.md](references/research-notebook.md#gaps_and_frictionmd) |
| `<milestone>/reports/`, `index.html` | HTML reports and the front page | [figures-and-reports.md](references/figures-and-reports.md) |

## Rule 9: Plain language; describe before interpreting

Plain English; numbers and direction first, interpretation second.

**No unagreed vocabulary.** Don't use terms, codes or step IDs with the
researcher that you haven't defined and they haven't accepted (gene-set IDs,
ontology codes, "decide gate", bare step numbers). If a technical term is
needed, say what it means the first time. Test: could the researcher restate
what you said?

**No commitment words before evaluation.** Until the evaluation milestone, don't
write "striking", "massive", "central finding", "reframes", "rich" and the like
— they claim more than the analysis has earned. If the researcher asks what a
result means earlier, answer and label it provisional.

**Describe, then interpret.** "5 markers show RNA log2FC < 0 and protein
log2FC > 0 at coculture days 31–89" — then `[interpretation]`, with plausible
alternatives.

**Verify before generalizing.** "All", "every", "none", "primarily" need a query
against the data file, not a glance at a heatmap.

**Proposals cite data or friction.** A suggested process change points to the
incident behind it; one occurrence is a note, a change needs the same friction
in two analyses. See [anti-hallucination.md 2.6](references/anti-hallucination.md#26-emotive-vocabulary-and-speculative-proposals).

## Rule 10: Working with the researcher

These rules exist because Claude, on its own initiative, reported values from
memory, named genes by name alone, and read absence into data never reported.
They bind Claude silently. Workshop researchers found Spock "overwhelming";
hearing the rules explained made it worse.

- **Don't narrate the rules.** Mention one only when it changes what the
  researcher gets or must decide — one sentence about the consequence, no rule
  or gate names, no "under our rules", no "I noted in the log that…". Record
  quietly and move on.
- **The researcher can lift a rule; Claude never does on its own.** "Use what
  you know", "use this paper" — do it and label the result ("from memory, not
  the KG"). Never "I'm not allowed to"; never refuse without saying why.
- **Process steps are offered, not imposed.** The researcher may wave through a
  co-define, run two milestones in one go (each still approved), or see a result
  before review (marked "not yet reviewed"). Note each waiver in `notebook.md`.
- **Suggest, don't run.** Do what was asked, only that. Your other ideas —
  analyses, plots, edits — go in a short *"I could also…"* list at the end.
  Change only what the researcher asked to change. *(Workshop: "additional
  analyses that I did not ask for — these are tokens being burnt".)*
- **Take several comments at once.** Number them, say in one line each what you
  will do, work through them as a checklist, report each as done.
- **Show where we are.** Open each message during an analysis with a one-line
  map, e.g. *Plan: ✓ question · ✓ KG data · → approach · can it work? ·
  framing* or *✓ Plan · ✓ Methods · → Analysis · Evaluation*.
- **Questions stand alone.** One topic each; say what it is about, what each
  option changes, and which you recommend — text before a pop-up may be off
  screen. A choice with a sensible default is stated, not asked: "I set X
  because Y; change it?"
- **Keep `overview.html` current** — the researcher's page
  ([artifacts.md](references/artifacts.md#who-reads-which-file)). Update it when
  a Plan step closes and at every decide. Open it in the browser when first
  created (`start "" <path>` / `open` / `xdg-open`) and say in one line that
  it's their page; afterwards end every message that updates it with
  "Overview updated: <path>".

## References — read on demand

- [plan-phase.md](references/plan-phase.md) — before Plan step 1: the five steps, modes, looking at data, framing, closing the Plan
- [step-protocol.md](references/step-protocol.md) — before the first Run milestone: commits, delegation, the five beats, redo, gates
- [research-notebook.md](references/research-notebook.md) — when writing `notebook.md`, `paper.md` or `gaps_and_friction.md`, or verifying method code
- [artifacts.md](references/artifacts.md) — at scaffold time, or for folder layout, script and file conventions
- [figures-and-reports.md](references/figures-and-reports.md) — before any figure or report page
- [anti-hallucination.md](references/anti-hallucination.md) — before presenting findings
- [kg-rules.md](references/kg-rules.md) — when scoping an analysis or separating KG data from literature
- [gene-identity.md](references/gene-identity.md) — for gene names, paralogs, orthologs, ecotypes
- [python-api-guide.md](references/python-api-guide.md) — before writing extraction or analysis scripts
- [statistical-rigor.md](references/statistical-rigor.md) — for enrichment, cross-study comparison, p-values
