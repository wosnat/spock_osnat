# Run-phase protocol

The Run phase executes `proposal.md` across three milestones, each in its own
folder: `methods/` → `analysis/` → `evaluation/`. Each milestone goes
**co-define → do → show → explore → decide**: the researcher agrees the scope
at co-define and approves at decide. This file owns *when things happen*:
commits, the five beats, redo and reopen, and the gates. The Plan is in
[plan-phase.md](plan-phase.md); what goes *in* `notebook.md` and `paper.md` is in
[research-notebook.md](research-notebook.md).

## Contents
1. [Commits](#commits)
2. [Delegation](#delegation)
3. [co-define](#co-define) · [do](#do) · [show](#show) · [explore](#explore) · [decide](#decide)
4. [Redo and reopen](#redo-and-reopen)
5. [Gates](#gates)

## Commits

**Commit every iteration; approval gets its own commit.** Work changes many
times inside a phase — each design-review round, each do / explore round, each
critic pass, each report rebuild. Each is committed before the researcher looks,
so git keeps every version they saw (reports and notebooks are overwritten in
place).

| Commit | When | Message |
|---|---|---|
| Iteration | after every round that changed files, before presenting it | `<slug> <phase>: iteration — <what changed>` |
| Approval | only after the researcher's explicit approval | `<slug> <phase>: approved — <advance rationale>` |

`<phase>` is `plan`, `methods`, `analysis` or `evaluation`. The main thread
commits, never the coding subagent. Commit everything the round produced,
including `usage/`, rebuilt `reports/`, `index.html` and `paper.html`. Never
amend or squash — a wrong turn stays in history. Redo also makes new commits.

**What the approval commit must leave in the tree:**
- **Plan:** the scaffold ([artifacts.md](artifacts.md#scaffold)), `proposal.md`,
  `decisions_log.md`, `spike/` if step 4 ran, `proposal_critical_review.md` if
  the critic found something, `paper.md` Question + Background.
- **Run milestone:** `notebook.md` with its decide-gate checklist; `scripts/`,
  `data/`, `figures/`, `reports/`; the regenerated `index.html` and
  `paper.html`; this milestone's `paper.md` section; `gaps_and_friction.md`
  entries; `critical_review.md` if the critic found something.

**Before starting a Run milestone,** the previous phase's approval commit must
exist, with its notebook checklist and `paper.md` section written. If not, close
it first.

**Request a push when the analysis is done.** After the evaluation approval
commit, ask the researcher to push — forks are public, so never push unasked.
Show the branch, the commits not yet on the remote (`git log --oneline @{u}..`,
or the whole branch with no upstream), and that the analysis and its usage logs
become public. Push only on a yes; if they hold it back, note it in the
evaluation `notebook.md`. Same check if they ask to push earlier.

## Delegation

The KG queries and script iterations of *do*, *show* and *explore* run in the
**`kg-coder`** agent, so the researcher's thread keeps only artifacts and
decisions. It preloads this skill and `dataviz`, so the domain rules ride
along. **Continue the same agent** across the milestone (`SendMessage`) — it
keeps the rules and the analysis context; spawn a new one only if it has lost
the thread.

- **kg-coder writes** scripts, data, figures, reports and a factual
  run-manifest (what ran, KG calls, row counts, candidate anomalies). It does not
  conclude, and it does not commit.
- **The main thread writes** `notebook.md`, `paper.md`, `gaps_and_friction.md`,
  critic dispositions and the decide-gate checklist. It pastes the run-manifest
  into the notebook's mechanical sections and writes every interpretive section
  itself — reading the real files, not the summary. *(A heatmap narrated "all 5
  UP" while the data file showed them negative.)*

Without subagents, do the same work inline — same rules, same files, same
ownership.

## co-define

Before any work, propose the milestone in plain language: what it should
produce, the judgment calls you expect, and why. Let the researcher reshape it;
begin once agreed. No files are produced. The researcher may wave a routine
milestone through (note it in `notebook.md`), but a genuine judgment call — what
to compare, how to define a set, which controls — is always proposed.

## do

kg-coder does the agreed work. Scripts in `scripts/`, outputs in `data/` and
`figures/` (`qc_` prefix for checks), reports in `reports/`
([artifacts.md](artifacts.md), [figures-and-reports.md](figures-and-reports.md)).

- **methods:** implement the approach as an ad-hoc module and verify it as in
  [research-notebook.md — Verifying the method](research-notebook.md#verifying-the-method)
  (toy tests in the real file format, then one small real example checked
  against an answer built independently through MCP calls; four layers when the
  method builds the entity set). **Nothing in the Run phase restricts looking at
  data.** Settle method choices — thresholds, backgrounds, reading rules — on
  reference or control sets first so they don't bend toward the target; that is
  an order of work, not a blind, and a target value seen while debugging is not
  an incident. *(hli light stress: a console print of one hli row was logged as
  an incident and carried as a decide-gate item.)*
- **analysis:** run the method; produce scored outputs, figures, tables.
- **evaluation:** assess results against the framing; label each finding
  *tested as planned* or *exploratory* (checked against `decisions_log.md`);
  compare each finding with the other KG experiments that bear on it
  ([research-notebook.md — Discussion](research-notebook.md#discussion));
  sensitivity checks where a result triggers them.

## show

Populate `notebook.md` from what kg-coder returned
([format](research-notebook.md#notebookmd)). The summary tables shown in chat
are the same tables in the notebook: real numbers, copied, not paraphrased.

## explore

Investigate anomalies, surprises and gaps. Each question is a new request to the
same kg-coder, which returns the artifact that answers it; you and the
researcher interpret — `qc_` checks, sensitivity runs, cross-checks against the
controls; anomalies go under **Surprises** in the notebook. Before exploring, read `decisions_log.md` for facts
already established. *(hli light stress: a proteomics check was run as "missed"
though the Plan had logged 0 of 23 proteins quantified.)*

**Explore what the researcher asks; suggest the rest.** Asked-for exploration is
free and unplanned findings are welcome, provided they pass the decide gate.
Your own ideas go into an *"I could also…"* list (SKILL.md Rule 10).

**A finding that emerged** — a pattern no plan asked for — is exploratory; it
needs no reopening of the proposal. When the researcher wants to pursue it, log
three things in `decisions_log.md` (it holds what was seen when, and the
prediction must be dated before any test data); the check's results go under
**Surprises** in the milestone notebook:
1. **The moment** — what was found, after seeing which results.
2. **The check** — is it stable when the method changes (another distance, a
   dropped platform or study, collapsed duplicates)? Is it a restatement of its
   inputs (copy number, shared probes and gene layout can be one feature seen
   three ways)?
3. **The prediction** — what it predicts in data not used to find it (other
   strains, another data type), what would refute it, and whether the KG has
   that data. Revisit scope already cut: a dropped part may now be the test.
   *(hli light stress: part B, other strains, had been dropped before the
   multi-copy responder split appeared — and was its natural test.)*

The researcher decides whether the test runs here or becomes a follow-up;
either way the prediction is logged before the test data is opened. A test run
here is *tested as planned*, and the paper says where the prediction came from
and how independent the test data is. If the researcher asks to close the
milestone while such a finding is open, log the moment and the prediction first
and ask in one line: test it here, or a follow-up? A deferred one goes into
`paper.md` as a suggested follow-up, naming the data its test needs.

## decide

1. **Finalize `notebook.md`** and end it with the
   [decide-gate checklist](research-notebook.md#decide-gate-checklist).
2. **Update `overview.html`**: where we are, this milestone's decisions and
   findings, links to its reports.
3. **Update `paper.md`.** Agree the storyline of this milestone's section with
   the researcher first, then write it — at analysis the Results and paper
   figures; at evaluation the Discussion, then the Abstract, last
   ([research-notebook.md — paper.md](research-notebook.md#papermd)). Rebuild
   `reports/` (`scripts/build_reports.py`), then from the repo root
   `uv run python scripts/build_report_index.py analyses/<slug>` and
   `uv run python scripts/build_paper.py analyses/<slug>`. Check `summary.html`'s
   findings table against `notebook.md`.
4. **Log friction** in `gaps_and_friction.md`. Two cheap checks: every friction
   the notebook points to has an entry; and a critic finding that exposed
   something the framing didn't anticipate is friction too, not only a
   disposition.
5. **Check your own claims, then run the critic.** For each *therefore,
   explains, shows, independent, all, none, never, only* in `notebook.md` and
   `paper.md`, name the contrast, file and number behind it; weaken or cut the
   word where you can't. The critic is not the first line of defence. *(hli
   light stress: "therefore" from a contrast that couldn't support it,
   "independent" support that re-read the same arrays, and "explains" for a
   partial split all reached the critic.)* Then dispatch the critic via the
   `critical-review` skill, which says which milestones get which lens, and
   how to handle and record its findings.
6. **Present:** link `overview.html` and `index.html` first, then the notebook,
   the `paper.md` diff, new friction entries and any `critical_review.md` with
   your dispositions. Wait for explicit approval or a redirect.
7. **On approval, commit** `approved`. Changes after a redirect are iteration
   commits. At evaluation, request the push.
8. Begin the next milestone (create its folder then, not before).

## Redo and reopen

**Redo** ("redo the analysis milestone with X"): update the approach, rerun,
overwrite the milestone's outputs and `notebook.md` (it describes the attempt
that worked; git keeps the rest), write a new `paper.md` section and friction
entries, then iteration commits and a new approval commit. If downstream
milestones consumed the old outputs, list them in the notebook; the researcher
decides whether to cascade.

**Reopen** — the data contradicts an assumption in the locked `proposal.md`.
Don't paper over it: edit `proposal.md` to record the original lock, the data
that triggered the reopening, and the revised question or framing; re-lock,
log friction, and continue. *(Alteromonas coculture: "does motility go up or
down?" was reopened when every usable contrast turned out to run in a medium
with no added organic carbon.)*

## Gates

Each gate exists because its failure happened.

- **A — co-define before doing.** Don't start a milestone's work without the
  researcher's agreement on what it will do. *(The first analysis surfaced
  finished work; the researcher reacted instead of shaping.)*
- **B — one milestone at a time.** Don't start milestone N+1, or the Run phase,
  before the previous approval commit exists. If asked to run two in one go,
  do — but each gets its own decide and approval commit. *(Notebooks written
  afterwards lost the reasoning.)*
- **C — reviewed before shown.** Don't present a claim-bearing artifact until
  its critic pass has run and every Blocker is resolved; a milestone that grew
  after its pass gets a delta pass. If the researcher asks to see a result
  earlier, show it marked "not yet reviewed". Schedule and lenses:
  [critical-review](../../critical-review/SKILL.md).
- **D — tables, not paraphrase.** Don't close a milestone whose notebook
  Results are prose where a table belongs.
- **E — explicit approval.** Don't make an `approved` commit without it.
