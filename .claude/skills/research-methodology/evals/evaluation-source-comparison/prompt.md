---
tags: [spock-regression]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

This is a dry run of the research-methodology skill in this repo (.claude/skills/research-methodology/SKILL.md and its references/; related: .claude/skills/critical-review/SKILL.md, .claude/agents/). Do NOT call KG/MCP tools, run code, or write files. Read the skill the way you would if this were real — start at SKILL.md and follow what it tells you to read.

Scenario: You are at the evaluation milestone of an exploratory analysis of Prochlorococcus MED4 high-light-inducible (hli) genes. A main finding is that most hli genes are up after a shift to high light. One of the KG experiments used is from Steglich et al. 2006, whose paper states that 'three hli genes' respond strongly; the KG links that sentence to 18 genes, 4 of which were not up in the analysis. The researcher asks you to write the Discussion.

Report back, concise (under 450 words):
1. Which files you read, in order, and why.
2. What you agree with the researcher before writing, and the order of the Discussion's parts.
3. How you describe the comparison with Steglich 2006 (draft the sentence or table row).
4. Where citations for background claims about HLIP function come from.
5. Anything unclear, contradictory or missing in the skill (file and section).
