# Regression checks for the research skills

Run both before a release, or after any change to `research-methodology`,
`critical-review` or `CLAUDE.md`.

## 1. Behaviour — five dry-run cases

Each folder is one scenario (`prompt.md`), what a good answer looks like
(`case.yaml`), and one check per file in `graders/`. A run reads the skill and
reports what it would do; it calls no KG tools and writes no files.

| Case | Checks |
|---|---|
| `plan-start-control-validated` | reads plan-phase.md first; one plain-language question; slug as a default; "look now or wait?" only before the target values; a reference arm used as a positive control is free |
| `plan-close-critic-findings` | self-review → proposal-critic → findings as suggestions → delta pass → approval |
| `analysis-decide-emerged-finding` | emerged finding logged and asked about before closing; claim-word self-check; lens; explicit approval |
| `evaluation-source-comparison` | Discussion storyline and order; consistency not replication; all linked genes; authorised citations; Abstract last |
| `exploratory-atlas` | exploratory mode; no framing; no "look now?" question; follow-up instead of persuasion |

**Run them** by asking Claude Code: "run the evals in
.claude/skills/research-methodology/evals as dry runs and grade them" (one
subagent per case, Sonnet is enough), or with the CLI from the skill folder:
`claude plugin eval .` (real, billed runs).

Baseline 2026-11-19 (after the restructure): 29 of 30 checks. The miss ("Abstract
written last") was a dropped line in step-protocol.md, fixed but not re-run.
Each run also lists anything it found unclear — read those; they found most of
the gaps so far.

## 2. Triggering — real `claude -p` sessions

`_triggers/trigger_set.json` holds 14 prompts: when `research-methodology` and
`critical-review` should load, and near-misses (code review, editing a script,
README wording) where they shouldn't. From the repo root:

```
uv run python -X utf8 .claude/skills/research-methodology/evals/_triggers/trigger_check.py \
  .claude/skills/research-methodology/evals/_triggers/trigger_set.json trigger_results.json 120 4
```

It runs real sessions in this repo (KG tools, shell and file writes blocked, so
nothing is changed or logged), stops each once the expected skill loads, and
prints PASS / FAIL per prompt. Baseline 2026-11-19: 14 / 14.
