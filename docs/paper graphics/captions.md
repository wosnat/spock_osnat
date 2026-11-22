# Spock paper graphics — draft captions

Figures are sized for A4 text width: 170 mm wide, ~94–123 mm tall,
with text ≥ 6.5 pt at that size.

Regenerate: `uv run python "docs/paper graphics/make_figures.py"` then
`bash "docs/paper graphics/render_figures.sh"` (headless Chrome → true-size vector PDF and a
~350 dpi PNG). Each figure ships as SVG (editable), PDF and PNG.

Quoted text is verbatim from `.claude/skills/research-methodology/` (SKILL.md,
references/plan-phase.md, references/research-notebook.md) and `.claude/agents/kg-coder.md`;
"…" marks an elision and [square brackets] an editorial insertion. If the skill text changes,
`uv run python -X utf8 "docs/paper graphics/check_quotes.py"` names the card whose quote no
longer matches; update it in `CARDS` in `make_figures.py`.

## Figure 1 — fig1_concepts_cards (six safeguard cards)

**How Spock guards AI-assisted research against hallucination and bias.** Six safeguards, in
the order they act across the research process (Figure 2A): planning, building the method,
analysis and write-up. Each card names the safeguard, the danger it counters (red), a verbatim
quote from the instructions Spock gives the AI, and, below the line, what Spock does in
practice. **Look it up:** values, gene identities, the meaning of tools and fields, and the
absence of data all come from a knowledge graph (KG) query; gaps are flagged, not filled from
memory. **Scope first:** before any success criteria are set, a quick test checks what the
data, annotations and candidate controls can actually tell apart, and may send the approach
back; big questions are split into smaller analyses. **Pre-register the test:** genes that
must respond, genes that must not, and how every outcome will be read are fixed before the
answer is seen (Figure 2B), and the AI that reviews the plan cannot open the results. Anything
outside the plan is reported as exploratory; an unplanned pattern is tested only through a
prediction recorded first, on data not used to find it; and no confirmatory claim is made on
data that were already published. **Check the computation:** each method is tested on toy data
in the real file format, then on one real case against an answer built another way, by someone
other than its author, and its code is reviewed afresh. Statistics run in scripts, with the
package's own pipeline, the correct background gene set and multiple-testing correction, and
effect sizes are not compared across measurement platforms. **Separate the roles:** the coding
AI returns files, not conclusions; the main AI judges from those files; and a reviewer AI with
no prior context re-checks every claim. **Claims match evidence:** numbers come before
interpretation; words such as "therefore", "all" or "independent" each need a contrast, a file
and a number; and each finding is set against the other studies in the KG. The orange frame is
the researcher, who approves every step: the AI never moves on alone, and every version of the
work is kept. Quotes are verbatim from `.claude/skills/research-methodology/` (SKILL.md,
references/plan-phase.md, references/research-notebook.md) and `.claude/agents/kg-coder.md`.

## Figure 2 — fig2_process_safeguards (the process, with Figure 1's safeguards on it)

**Where each safeguard acts in the Spock research process.** **(A)** The researcher (orange,
as in Figure 1's frame) poses a question and approves every step; the AI assistant does the
work. Each AI step is drawn as the Figure 1 card it carries. In the plan: the AI shows what the
knowledge graph (KG) holds (*Look it up*); checks with a throwaway test that the approach can
work, which may send the approach back (*Scope first*); fixes the controls and decision rule
(*Pre-register the test*, panel B); and a second AI, new to the work and unable to open the
results, reviews the plan (*Separate the roles*). The researcher approves or asks for a
revision, and the plan is then frozen. In an overview, where nothing is being tested, there is
no framing and every result is reported as exploratory. The work then runs in three stages:
building and testing the method, the analysis, and the evaluation, each through the same loop.
The researcher agrees what the stage will do. A coding AI runs the code and returns files, not
conclusions; the method is tested on toy data and against an answer built another way
(*Check the computation*). The main AI reads the files and judges what they show, numbers
before interpretation (*Claims match evidence*). The researcher and the AI explore the results
together; a pattern nobody planned for is tested only through a prediction recorded first.
Before the researcher sees the stage, the method and statistics code is reviewed and a fresh AI re-checks every claim
against the files (*Separate the roles*); the researcher then approves, or asks for a revision
or a redo. If the results contradict the frozen plan, the plan is reopened and the change
recorded, never made silently. Every approval is saved and never overwritten (rings).
**(B)** What the plan fixes before the result is seen: the seven parts of a framing, each with
a few words quoted from the skill (`references/plan-phase.md`). Positive controls show the data
can reveal an effect at all; negative controls show what "no effect" looks like. Methods are
settled on the controls first; the targets are scored once, last.

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
