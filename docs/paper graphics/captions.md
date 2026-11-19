# Spock paper graphics — draft captions

Figures are sized for A4 text width: 170 mm wide, ~110–123 mm tall (Figure 1e, with seven rows, is ~146 mm),
with text ≥ 6.5 pt at that size.

Regenerate: `uv run python "docs/paper graphics/make_figures.py"` then
`bash "docs/paper graphics/render_figures.sh"` (headless Chrome → true-size vector PDF and a
~350 dpi PNG). Each figure ships as SVG (editable), PDF and PNG.

Quoted text is verbatim from `.claude/skills/research-methodology/` (SKILL.md,
references/step-protocol.md) and `.claude/agents/kg-coder.md`; "…" marks an elision and [square brackets] an editorial substitution. If the
skill text changes, update the quotes in `make_figures.py`.

## Figure 1e — fig1e_concepts (Figure 1c aligned with Figure 2h)

**How Spock counters threats to validity in AI-assisted research.** Left: seven ways an
AI-assisted analysis can go wrong, labelled with the stage of the process (Figure 2A) where
each arises. Right: the safeguard that counters it, quoted from the instructions Spock gives
the AI ([brackets] mark an editorial substitution), with how it is enforced. The safeguard
names and icons are the same as in Figure 2. Data come from a knowledge graph (KG); anything
the researcher adds from elsewhere is labelled, and gaps are flagged rather than filled from
memory. Before the success criteria are set,
a quick test checks what the data and annotations can actually tell apart. The criteria,
including positive and negative controls and a decision rule, are fixed in the plan before
the result is scored (Figure 2B): the controls must pass, then the method is frozen, then the
targets are scored once. Anything seen before the plan was set is reported as exploratory.
Success criteria apply to analyses that test something against controls; an exploratory
analysis agrees its scope instead and labels all its results exploratory. In the final
write-up, each finding is labelled as tested as planned or exploratory. Each method is first tested
on small hand-computed examples, and a method that builds its own gene set is also checked
against an independent answer key and random samples of its output. Running the code, judging its output and reviewing the
claims are done by separate AI agents, the reviewer starting with no knowledge of the work.
Claims are checked against the data before general words such as "all" are used, and
interpretation comes only after the numbers. All computation is in saved scripts, and every
version is kept. Throughout, the researcher approves every plan and every stage.
## Figure 2h — fig2h_process_framing (Figure 2g in plain language, plus the frozen plan)

**The Spock research process, and what the plan fixes in advance.** **(A)** The researcher
poses a question. The AI assistant shows what the knowledge graph (KG) holds and checks what
the data and annotations can actually show, then sets the success criteria with the
researcher (panel B). Looking at the data during planning is free; the one exception is the
result the plan will test, which the researcher may still choose to see, after which it is
reported as exploratory. A second AI, new to the work, reviews
the plan, and the researcher revises it until they approve it. The plan is then frozen. The
work runs in three stages: building and testing the method, the analysis, and the
evaluation. Each stage follows the same loop. The researcher agrees what the stage will do. A
coding AI runs the analysis code and returns output files, not conclusions. The main AI
reads the files and judges what they show, and a second AI, new to the work, re-checks the
claims against the files. Only then does the researcher see the stage and approve it, or ask
for a revision or a redo. If the results contradict the frozen plan, the plan is reopened and
the change is recorded, never made silently. Every version is saved and never overwritten.
Badges and line styles are explained in the legend below panel A. **(B)** The six things a
plan must fix before the result is scored, on a small worked example: does a gene that controls
nitrogen use switch on when marine bacteria (*Prochlorococcus*) are fed urea instead of
ammonium? The positive control (genes for using urea must switch on) shows the data can reveal
an effect at all; the negative control (growth genes must stay flat) shows what "no effect"
looks like. Without both, a null result cannot be told apart from an experiment that could not
detect anything. In this example the decision rule was committed and approved, and a further control was
added. While checking the revision, the AI reviewer looked up one result value; only the
controls changed after that, the change was disclosed, and the plan was re-approved. Every
version is kept.

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
