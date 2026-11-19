---
tags: [spock-regression]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

This is a dry run of the research-methodology skill in this repo (.claude/skills/research-methodology/SKILL.md and its references/; related: .claude/skills/critical-review/SKILL.md, .claude/agents/). Do NOT call KG/MCP tools, run code, or write files. Read the skill the way you would if this were real — start at SKILL.md and follow what it tells you to read.

Scenario: You are the main thread of a control-validated analysis. The Plan and methods milestones are approved. kg-coder has just returned the analysis milestone's scored tables and figures. While reviewing them, the researcher noticed several genes cluster in a way no plan predicted and wants to pursue it. The researcher then says "looks good, let's wrap up this milestone".

Report back, concise (under 450 words):
1. Which files you read, in order, and why.
2. What you do about the unplanned cluster, step by step, and where each thing is recorded.
3. Your ordered actions from now to the approval commit.
4. Which critic lens applies, and what it checks about the cluster finding.
5. Anything unclear, contradictory or missing in the skill (file and section).
