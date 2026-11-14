# Spock paper graphics — draft captions

Both figures are sized for half an A4 page: 170 mm wide (A4 text width), ~115–123 mm tall,
with text ≥ 6.5 pt at that size.

Regenerate: `uv run python "docs/paper graphics/make_figures.py"` then
`bash "docs/paper graphics/render_figures.sh"` (headless Chrome → true-size vector PDF and a
~350 dpi PNG). Each figure ships as SVG (editable), PDF and PNG.

Quoted text is verbatim from `.claude/skills/research-methodology/` (SKILL.md,
references/step-protocol.md) and `.claude/agents/kg-coder.md`; "…" marks an elision and [square brackets] an editorial substitution. If the
skill text changes, update the quotes in `make_figures.py`.

## Figure 1 — fig1_concepts

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

## Figure 1b — fig1b_concepts (alternative to Figure 1: problems framed explicitly)

**How Spock keeps AI-assisted research valid.** Left (red, dashed): six ways AI-assisted
analysis goes wrong. Right: the Spock safeguard that prevents each one, quoted from the
instructions Spock gives the AI, with a plain-language note on how it is enforced. Data come
only from the knowledge graph (KG), and every finding is tagged by source. Success and
failure criteria, including a statistics plan, genes of known expected behavior and an
expected-negative class, are fixed before any data are seen. A coding sub-agent returns
output files, not conclusions, so judgment is made from the data themselves. A separate
agent with a fresh context reviews each result before the researcher sees it. Generalizing
and evaluative language waits until the data support it. All computation lives in scripts,
and every iteration is committed. Throughout, the researcher agrees the scope of each step
and approves its outcome.

## Figure 1c — fig1c_concepts (six safeguards ordered by research stage)

**How Spock counters threats to validity in AI-assisted research.** Left (red, dashed): six
ways an AI-assisted analysis can go wrong, ordered by the research stage where they arise.
Right: the Spock safeguard that counters each one, quoted from the instructions Spock gives
the AI ("…" marks an elision, [brackets] an editorial insertion), with a plain-language note
on how it is enforced. Data come only from the knowledge graph (KG); every finding is tagged
by source and gaps are flagged, not filled. Before the analysis runs, the framing names the
genes that should score, a class that should not, and the statistics plan. It changes only by
a recorded reopening, and a null result is reported as a bounded negative. Each new method
is checked on hand-computed toy data, then against an independent answer key and on a random
sample of its output. A coding agent runs the scripts, the main agent judges from the output
files, and a critic agent with a fresh context reviews the plan and each claim-bearing
milestone. Generalizing words require a check against the data, and interpretive language
waits for the evaluation step. All computation is in scripts and every iteration is
committed. Throughout, the researcher agrees the scope of each step and approves its outcome.

## Figure 2f — fig2f_process_swimlanes (the research process as a swimlane flowchart)

**The Spock research process.** Each lane is one actor: the researcher, the main agent, a
coding agent and a critic agent. *Plan (left):* the researcher poses the question. The main
agent lists the relevant knowledge-graph (KG) entries by query and writes the framing: the
genes that should score, a class that should not, and the statistics plan. A critic agent
with a fresh context reviews the plan before the researcher's design review. Each change
from that review gets a new critic pass, until the researcher agrees and the proposal is
locked. *Run (right):* one milestone is shown; methods, analysis and evaluation each repeat
it. The researcher agrees the scope. The coding agent runs scripts and KG queries and returns
files and a factual manifest, never conclusions. The main agent reads the real files, judges
what they show, and sends follow-up questions back to the coding agent. The critic then
re-checks the milestone's claims against its files, with a lens matched to the milestone
(data integrity and interpretation at analysis, interpretation only at evaluation, and
methods only when it produces a data file). Each blocking issue is fixed, or rebutted with
data, before the researcher sees the work. The researcher then approves, asks for another
iteration, or asks for the milestone to be redone. If the data contradict the locked plan,
the plan is reopened on the record rather than silently changed. Every iteration and
approval is committed and never amended. Badges mark where each safeguard of Figure 1 acts.

## Figure 2g — fig2g_process_simple (Figure 2f simplified to two lanes)

**The Spock research process.** *Plan:* the researcher poses the question. The AI lists the
relevant knowledge-graph (KG) entries by query and writes the framing: the genes that should
score, a class that should not, and the statistics plan. A critic agent with a fresh context
reviews the plan, and the researcher reviews the design. Changes loop back until the
researcher agrees, and the proposal is then locked. *Run:* methods, analysis and evaluation
each follow the same loop. The researcher agrees the scope. A coding agent runs the scripts
and returns files, not conclusions. The main AI reads the files and judges what they show,
and a fresh critic checks the claims against the files, raising blocking issues that are
fixed or rebutted with data before the researcher sees the work. The researcher then
approves, or asks for another iteration or a redo. If the data contradict the locked plan,
the plan is reopened on the record rather than silently changed. Every iteration and
approval is committed and never amended. Badges mark where each safeguard of Figure 1 acts.

## Figure 2h — fig2h_process_framing (Figure 2g in plain language, plus the frozen plan)

**The Spock research process, and what the plan fixes in advance.** **(A)** The researcher
poses a question. The AI assistant finds the relevant data in the knowledge graph (KG) and
drafts a plan that sets the success criteria (panel B). A second AI, new to the work, reviews
the plan, and the researcher revises it until they approve it. The plan is then frozen. The
work runs in three stages: building and testing the method, the analysis, and the
evaluation. Each stage follows the same loop. The researcher agrees what the stage will do. A
coding AI runs the analysis code and returns output files, not conclusions. The main AI
reads the files and judges what they show, and a second AI, new to the work, re-checks the
claims against the files. Only then does the researcher see the stage and approve it, or ask
for a revision or a redo. If the results contradict the frozen plan, the plan is reopened and
the change is recorded, never made silently. Every version is saved and never overwritten.
Badges and line styles are explained in the legend below panel A. **(B)** The six things a
plan must fix before any results exist, on a small worked example: does a gene that controls
nitrogen use switch on when marine bacteria (*Prochlorococcus*) are fed urea instead of
ammonium? The positive control (genes for using urea must switch on) shows the data can reveal
an effect at all; the negative control (growth genes must stay flat) shows what "no effect"
looks like. Without both, a null result cannot be told apart from an experiment that could not
detect anything. In this example the plan was approved, then revised before any results to add a further
control, and re-approved; both versions are kept.

## Figure 1e — fig1e_concepts (Figure 1c aligned with Figure 2h)

**How Spock counters threats to validity in AI-assisted research.** Left: six ways an
AI-assisted analysis can go wrong, labelled with the stage of the process (Figure 2A) where
each arises. Right: the safeguard that counters it, quoted from the instructions Spock gives
the AI ([brackets] mark an editorial substitution), with how it is enforced. The safeguard
names and icons are the same as in Figure 2. All data come from a knowledge graph (KG), and
gaps in it are flagged rather than filled from memory. The success criteria, including a
positive and a negative control, are fixed in a frozen plan before any results exist
(Figure 2B), and a null result is reported rather than dropped. Each method is first tested
on small hand-computed examples. Running the code, judging its output and reviewing the
claims are done by separate AI agents, the reviewer starting with no knowledge of the work.
Claims are checked against the data before general words such as "all" are used, and
interpretation comes only after the numbers. All computation is in saved scripts, and every
version is kept. Throughout, the researcher approves every plan and every stage.
