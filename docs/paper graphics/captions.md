# Spock paper graphics — draft captions

Both figures are sized for half an A4 page: 170 mm wide (A4 text width), ~115–123 mm tall,
with text ≥ 6.5 pt at that size.

Regenerate: `uv run python "docs/paper graphics/make_figures.py"` then
`bash "docs/paper graphics/render_figures.sh"` (headless Chrome → true-size vector PDF and a
~350 dpi PNG). Each figure ships as SVG (editable), PDF and PNG.

Quoted text is verbatim from `.claude/skills/research-methodology/` (SKILL.md,
references/step-protocol.md) and `.claude/agents/kg-coder.md`; "…" marks an elision. If the
skill text changes, update the quotes in `make_figures.py`.

## Figure 1 — fig1_concepts

(Concept boxes carry numbers 1–6, which are the rows of Figure 2b.)

**How Spock keeps AI-assisted research valid.** Each row pairs a threat to validity in
LLM-assisted analysis (left) with the Spock concept that counters it, quoted from the
research-methodology skill (right). Data come only from the knowledge graph (KG), and every
finding is tagged by source. The framing is fixed before any data are seen, including a
statistics plan, a named validation set and an expected-negative class. The coding subagent
returns artifacts, not conclusions, so the judgment is made from the data files themselves. A
critic with a fresh context reviews each claim-bearing artifact before the researcher sees
it. Claims must be checked against the data before any generalizing word is used. All
computation lives in scripts, and every iteration is committed. Together these measures stop
the assistant from amplifying the researcher's expectations or its own narrative. Throughout,
the researcher agrees the scope of each step and approves its outcome.

## Figure 2 — fig2_process

**The Spock research process.** *Plan:* one KG-grounded conversation locks the question,
enumerates the relevant KG entries, and states the framing concretely. The proposal is
self-reviewed, reviewed by a critic, and taken through design review with the researcher,
with a delta critic pass after each change. It is then locked by an approval commit. *Run:*
three milestones, each reviewed by a critic whose lens matches what the milestone produces.
Each milestone moves through co-define → do → show → explore → decide. The researcher gates
both ends, the middle is delegated to a coding subagent, and every round is committed. If
the data contradict the locked proposal, the proposal is reopened: the original plan, the
reveal and the revision are all recorded. A milestone can also be redone. Redoing adds a new
approval commit and never rewrites history.

## Figure 2b — fig2b_concepts_workflow (alternative to Figure 2)

**From concepts to workflow.** Each row is one of the validity concepts of Figure 1, with the
same numbers. Each column is a stage of the Spock workflow: Plan, Execute, Review, and
Decide & record. Each cell names the concrete mechanism that enforces the concept at that
stage. A dashed empty cell means the concept has no mechanism at that stage. The bottom row
shows the researcher's gates. Corrections (iterating within a milestone, redoing a
milestone, or reopening the locked plan) loop back to earlier stages. Each correction is
committed, so the record of what came before is kept.

## Figure 2c — fig2c_flow_concepts (simplified alternative to Figures 2 / 2b)

**The Spock research flow, and why each stage protects validity.** *Top:* in the Plan
phase, the research question is locked and the relevant knowledge-graph (KG) entries are
enumerated. The framing is then fixed: hypothesis, statistics plan, a validation set of
genes with known expected behavior, and an expected-negative class that should not score.
A fresh-context critic and then the researcher review the framing. The proposal is then
locked, and the Run phase proceeds through methods, analysis and evaluation milestones.
*Bottom:* what each stage contributes. The scope is grounded in what the KG holds rather
than recalled from memory. The success and failure criteria are set before any data are
seen, so a null result can be told apart from noise. Plan flaws are caught by a reader who
did not write the plan. The method is tested on toy data before it touches real data.
Results are re-counted by an independent reader before anyone sees them. Interpretive claims
wait until the evidence is complete. Each step is approved by the researcher and committed,
and corrections loop back openly instead of overwriting earlier work.

## Figure 2d — fig2d_concepts_in_flow (alternative: concepts as the workflow's labels)

**Validity concepts as reflected in the Spock workflow.** Each step of the workflow is
labelled with the concept it enforces (blue), followed by concrete examples of how it is
enforced. *Scope* is grounded in the knowledge graph (KG). Experiments and publications are
listed by query, genes are resolved to unambiguous locus tags, and gaps in the KG are flagged
rather than filled. *Framing* pre-registers the analysis: a hypothesis, a statistics plan, a
validation set of genes with known expected behavior, an expected-negative class that must
not score, and the design comparability of each experimental arm. *Review* is by a critic
with a fresh context and then the researcher, with a delta review after each change. The
proposal is then locked. In the Run phase, the method is tested first: on hand-computed toy
cases, against an independent answer key, and on random samples of every bin. The analysis
is checked by a cold critic, who re-checks every number against the data files. Claims come
last: results are judged by the pre-set hit and miss, a negative result is reported
with its limits rather than dropped, and interpretive language is allowed only at evaluation. Across all steps,
the researcher agrees each step's scope and approves it, and every step is scripted and
committed. Corrections loop back openly, and the locked framing changes only through a
recorded reopening.

## Figure 2e — fig2e_concepts_two_rows (Figure 2d content, laid out as Plan and Run rows)

Same content and caption as Figure 2d. The Plan row (scope, framing, review) and the Run row
(methods, analysis, evaluation) are separated by the proposal lock.

## Figure 3 — fig3_agents

**Multi-agent design.** The main Claude thread, loaded with the research-methodology skill,
owns all judgment. It reads the real data files, writes the notebook and paper, commits each
round, and is the only agent that talks to the researcher. Execution is delegated to a
kg-coder subagent. It is kept alive across a milestone, preloads the same domain rules, and
queries the knowledge graph and writes scripts, data and figures. It returns a factual
run-manifest and never interprets or commits. Claim-bearing artifacts are reviewed by a critic
subagent that starts from a fresh context on every pass. The critic is read-only, sees only
the current milestone's files, and applies a lens matched to the work. The main thread
records a disposition for each of its findings. Splitting doing from judging means no single
agent both produces a result and vouches for it.
