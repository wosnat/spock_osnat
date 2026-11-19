---
name: critical-review
description: Use before the researcher sees a claim-bearing artifact of a research analysis — the proposal at the close of the Plan phase, and the methods (when it emits a data file), analysis and evaluation milestones at their decide phase — again as a delta pass whenever that artifact's claims grow, and on demand. Dispatches a fresh-context critic that re-checks the artifact's claims against its own files.
---

# Critical review

A fresh-context critic challenges an artifact **before** the researcher sees it.
It never sees your session; it reads the files cold, so it can't inherit the
story you anchored on. That is the point: the errors this methodology keeps
making — "all 5 are UP" over a data file that says otherwise; two
starvation-vs-own-baseline arms narrated as "coculture vs axenic" — survive
because the author believes the story. The review sharpens the researcher's
approval; it doesn't replace it. This skill owns when the critic runs and with
which lens; the research-methodology references point here.

**Keep it light:** match the lens to what the artifact produces; review only
its own files (earlier phases are trusted inputs, never re-audited); write a
file only when there are findings.

## When it runs, and with which lens

| Artifact | When | Lens | Agent |
|---|---|---|---|
| `proposal.md` | close of the Plan, and every delta pass before approval | interpretation | `proposal-critic` |
| methods milestone | automatic when it emits a data file later milestones read; otherwise on demand | data-integrity + interpretation | `critic` |
| analysis milestone | automatic — the heavy gate | data-integrity + interpretation | `critic` |
| evaluation milestone | automatic | interpretation (plus data-integrity on any new computation) | `critic` |
| any of the above | a **delta pass** when claims grew after the pass | as above, over the new work only | fresh agent |

**Proposal.** A framing flaw propagates through all three milestones, so it is
reviewed before the Run. The critic weighs testability, confounders, and
whether the statistics decision, controls and decision rule fit the question
(for an exploratory proposal: whether scope and deliverables match it) — most of
all where the framing rests on a judgment call: a non-obvious combining key
(disjoint strains mapped onto shared ortholog groups), a constructed comparison,
or controls whose validity isn't obvious (is the positive control independent?
is the negative control the contrast it's labelled as?). **It must not open the
result the plan will test** — in three analyses a Plan-phase critic did, and once
ran a script while read-only. So it is `proposal-critic`: no shell, no file
writes, experiment-level and annotation KG tools only. A check it can't run is
reported unverified, and you run it on non-target genes or experiment-level
counts. The Plan's close is in
[plan-phase.md — Closing the Plan](../research-methodology/references/plan-phase.md#closing-the-plan).

**Analysis.** Where computed results first appear, so the data-integrity half
pays off: it opens the CSVs and checks signs, counts, truncation and
conflation that the narrative glosses.

**Methods.** A toy-tested function alone can wait for the analysis pass. But a
method that *constructs the entity set* — a parts list, candidate set,
classification table — emits a file whose labels, flags and classes every later
milestone reads as a trusted input, so no later pass will catch its errors. It
gets the full lens. *(Alteromonas coculture: a soluble PTS phosphocarrier sat in
the candidate set as a confident sugar importer, and a carrier count 30% high had
already reached `paper.md`.)*

**Evaluation.** Conclusions, not new computation, so interpretation only: is
each conclusion earned by the analysis results? Caveats honest? Anything
over-claimed, causal from correlational, or compared across platforms? Is each
label right — nothing *tested as planned* that `decisions_log.md` lists as seen
before the plan was set, or that rests on a rule changed after the results? Does
each "agrees / disagrees" with other studies hold, given the designs? Does a
comparison with a source study claim replication or independence where it only
re-reads that study's data, or drop linked genes that disagree? New computation
here (typically testing an emerged finding) also gets data-integrity, scoped to
its own scripts and outputs.

**Emerged-finding check** (analysis or evaluation, whenever a finding no plan
asked for is tested): the prediction was logged in `decisions_log.md` before the
test data was opened, the test data was not used to find it, and the paper
states how independent that data is.

**Delta pass — expected, not exceptional.** Explore runs after the critic by
construction, and the Plan's design review changes the framing after its pass.
When claims materially grow, re-dispatch over the new work, listing the
already-reviewed files as trusted inputs. A milestone that grew after its pass
and closes without a delta pass closes unreviewed work. *(N-import: two Plan
delta passes found one Blocker and five Concerns in the additions; Alteromonas
coculture: a delta pass after a clean analysis review found a figure caveat
citing the wrong module's number, inverting its meaning.)*

**Not the critic's job:** routine compliance — locus tags present, computations
scripted, tables not paraphrase, checklist filled. That is the author's
decide-gate checklist.

## How to dispatch

1. **Identify** the analysis root and the folder under review (for the
   proposal, `proposal.md` at the root).
2. **Dispatch a fresh agent** — `proposal-critic` for the proposal, `critic`
   otherwise — filling the template in [critical-reviewer.md](critical-reviewer.md).
   Never continue an earlier critic; one that remembers the last pass isn't
   reading cold. If `proposal-critic` isn't available, use `critic` and add:
   "Do not open expression values or any other data that answers the question;
   do not run shell commands that write files." If `critic` isn't available,
   use a `general-purpose` agent.

   Placeholders: `{ANALYSIS_ROOT}`; `{REVIEW_FOLDER}` (the only files in scope);
   `{REVIEW_NAME}` ("the analysis milestone"); `{REVIEW_INTENT}` (one or two
   plain sentences: what it set out to do and its main judgment calls);
   `{REVIEW_LENS}` (from the table; for other on-demand runs, data files →
   include data-integrity); `{TRUSTED_INPUTS}` (earlier outputs it builds on —
   e.g. the analysis `data/` for an evaluation review; empty for the proposal).
3. **Record the result.** Findings → copy them verbatim into
   `critical_review.md` in the reviewed folder (`proposal_critical_review.md`
   for the proposal), each with your disposition: fixed (what changed),
   disputed (the file and number that show the critic is wrong), or deferred
   (why it can wait) — or *awaiting the researcher* when the fix is their
   design choice, updated once they decide; commit it. Clean → no file; one line in `notebook.md` (or
   `decisions_log.md`): `Critical review: clean (<lens>)`.
4. **Act before presenting.** A **Blocker** is resolved — fixed, or disputed with
   a file-and-number, never "I'm confident" — before the milestone closes or the
   Run begins; for a design Blocker, the researcher's decision, applied, resolves it. A **Concern** is addressed or deferred with a reason. A **Note** is
   recorded, fixed if cheap. A refutation without a file-and-number is itself
   something to dispute.
5. **Present** the dispositions with the decide-gate state. For the proposal,
   bring each finding as *"the reviewer noticed X; I suggest Y, because Z"*, with
   the choice it opens — never a silent fix followed by a question about one of
   its details.

## Never

- Skip a review because "the plan is obvious", "the result is obvious" or
  "methods is only code".
- Close a milestone that grew after its pass without a delta pass.
- Start the Run, or close a milestone, with an unresolved Blocker.
- Re-audit an earlier, already-reviewed phase as part of a later review.
