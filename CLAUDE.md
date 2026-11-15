# CLAUDE.md

## What this repo is

Your working copy of **Spock**, the multiomics research template
([TheSherLab/spock](https://github.com/TheSherLab/spock)) — a clean starting
point for KG-backed research in Claude Code. It carries the research skills and
the MCP wiring; `uv sync` pulls the explorer tools into the local venv. Your
analyses live in `analyses/` in this clone.

This is the **consumer** side of the multiomics KG. The MCP tools themselves are
built in the sibling `multiomics_explorer` package (installed via `uv sync`, not
edited here).

## Layout

```
.claude/skills/research-methodology/   # Domain rules + the Plan→Run research arc (reference skill)
.claude/skills/recipes/                # On-demand analysis protocols land here as methods are formalized (none yet)
.claude/agents/                        # kg-coder (Run-phase coding subagent) + critic (read-only reviewer) + proposal-critic (Plan-phase reviewer, no access to results)
.mcp.json                              # Registers the multiomics-kg MCP server (uv run)
.env / .env.example                    # KG credentials (gitignored; copy the example)
hooks/                                 # Usage-logging hook (writes into usage/)
scripts/preflight.sh                   # DOA gate: version triple + KG contract + API smoke
scripts/build_report_index.py          # analyses/<slug>/index.html: every report + the paper
scripts/build_paper.py                 # analyses/<slug>/paper.html: paper.md with figures embedded
analyses/                              # YOUR research output (one dir per analysis)
usage/                                 # Usage logs (committed — ride along with your pushes)
VERSION / CHANGELOG.md                 # Template version + history
```

## Getting started

See [README.md](README.md): fork → clone → `uv sync` → set credentials →
`./scripts/preflight.sh` → start an analysis. Run preflight green before opening
a research chat.

## Research methodology

**Load the `research-methodology` skill BEFORE invoking
`superpowers:brainstorming` for the Plan phase of an analysis.** It contains the
KG usage rules, gene-identity rules, anti-hallucination patterns,
scripts-over-chat-reasoning, and the Plan→Run research arc. Loading after the
plan is committed means retrofitting.

### The research arc: Plan, then Run

Every analysis is two phases:

**Plan** — one grounded `superpowers:brainstorming` conversation, walked through
with the researcher in five steps, each ending with a "so far" summary they
confirm and recorded in `decisions_log.md`:
1. **Clarify and size the question** — what it is for, the mode (*exploratory*:
   scope and deliverables, no framing; or *control-validated*: the full framing),
   and whether to split a question that is too big into smaller analyses
2. **Show what the KG holds** — publications, experiments, organisms, data types,
   coverage, as tables or plots (a decision tree when many experiments must be sorted)
3. **Agree the general approach**
4. **Check that the approach can work** — throwaway tests in `spike/`, required when
   the method builds its own gene set or mixes platforms
5. **Set the framing** — hypothesis, approach, statistics plan (the specific test or a
   reasoned "none"), positive and negative controls (each with its expected result),
   a decision rule for every reading of the target, and design comparability (per
   experiment: what each arm is compared against and that reference's
   physiological state, shared samples or models, what it can confirm)

Then `proposal.md` is written as the record of what was agreed, reviewed by the
`proposal-critic`, its findings brought to the researcher with recommendations, a
delta critic pass over what changed, and an approval commit. Looking at data during
planning is free; the one exception is a plain-language question before showing the
data that answers the question, in control-validated mode.

**Run** — three milestones, each in its own folder; every iteration committed, each
milestone closed by an approval commit, and a push requested when the analysis is done:
- **methods** — ad-hoc Python module implementing the approach the proposal
  committed to; toy-tested (`superpowers:test-driven-development`)
- **analysis** — run the method; produce scored outputs, figures, tables
- **evaluation** — assess against the framing; harvest caveats; finalize paper

`proposal.md` is the plan (locked at the end of the Plan phase). The Run
milestones execute against it. The Plan phase collapses onto brainstorming; the
Run phase is the project's own iterate loop (it is not `executing-plans`, which
assumes a locked, pre-specified plan).

### Run-milestone rhythm: co-define → do → show → explore → decide

Each Run milestone advances through **co-define → do → show → explore → decide**,
with two researcher gates: agreement at **co-define** (before the work) and
approval at **decide** (after it). The **decide** phase produces a minimal
`notebook.md` checklist and pauses for explicit researcher approval before
committing. Execution (KG queries, scripts) is delegated to a coding subagent
(`superpowers:subagent-driven-development`) that returns artifacts, not
conclusions; the main thread owns `notebook.md` and all judgment. Use the
`kg-coder` agent for that role and continue it across the milestone. Figures use
the `dataviz` skill; each milestone produces HTML reports (`<milestone>/reports/`,
listed in the analysis's `index.html`); and `paper.md` is paper-ready prose for the
eventual paper's reader, rendered with its figures as `paper.html`. See
`.claude/skills/research-methodology/references/step-protocol.md` for commit
timing, the decide-gate checklist, hard gates, and the delegation rules.

### Just-in-time formalization, with enumeration

Terms, predictions, metrics, stability checks, decisions, and caveats enter the
analysis **only when the data demands them** — but within what the plan *does*
commit to, be concrete (a vague-but-approved plan forces redos). If you find
yourself listing things the analysis might need before the data has arrived, stop.

On-demand tools that remain available: `superpowers:verification-before-completion`,
`superpowers:systematic-debugging`, `superpowers:requesting-code-review`, and the
`critical-review` skill — a fresh-context critic that challenges a claim-bearing
artifact against its own files (automatic on the proposal before the Run phase,
interpretation-only; at the analysis milestone — and at a methods milestone that
emits a data file — with a data-integrity + interpretation lens; at the
evaluation milestone with interpretation only; as a delta pass whenever a
milestone's claims grow after its first pass; and on demand at any point).

## MCP server & credentials

The `multiomics-kg` MCP server runs via `uv run multiomics-kg-mcp` (see
`.mcp.json`) from the repo root, so the explorer reads KG credentials from the
gitignored `.env` at the repo root. The server requires the lab Neo4j KG to be
reachable (operator-provided URI + credentials). Run `./scripts/preflight.sh`
to confirm before starting.

## Usage logging

The hook in `hooks/log-mcp-usage.sh` appends one JSON line per MCP call to
`usage/multiomics-kg-usage.jsonl` **inside this repo** (un-ignored). Commit
`usage/` alongside your per-milestone analysis commits — the logs help improve the
tools. Forks are public; see the README before you start.
