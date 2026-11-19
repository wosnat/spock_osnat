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
`superpowers:brainstorming` for the Plan phase of an analysis** — loading it after
the plan is committed means retrofitting. It holds the KG and gene-identity rules
and the research arc: a **Plan** (a five-step dialog with the researcher, ending in
a reviewed `proposal.md`) and a **Run** of three milestones — `methods/` →
`analysis/` → `evaluation/` — each going co-define → do → show → explore → decide,
with execution delegated to the `kg-coder` agent and a fresh-context critic
(`critical-review` skill) before the researcher approves a milestone.

The process lives in the skill, not here — start at
`.claude/skills/research-methodology/SKILL.md`; the Plan is in
`references/plan-phase.md`, the Run in `references/step-protocol.md`.

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
