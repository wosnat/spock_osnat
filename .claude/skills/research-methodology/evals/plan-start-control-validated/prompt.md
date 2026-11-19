---
tags: [spock-regression]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

This is a dry run of the research-methodology skill in this repo (.claude/skills/research-methodology/SKILL.md and its references/; related: .claude/skills/critical-review/SKILL.md, .claude/agents/). Do NOT call KG/MCP tools, run code, or write files. Read the skill the way you would if this were real — start at SKILL.md and follow what it tells you to read.

Scenario: A researcher opens a chat and says: "I want to know whether the Prochlorococcus MED4 nitrogen-stress regulator ntcA targets respond in coculture with Alteromonas the same way they do under N starvation. Let's start an analysis."

Report back, concise (under 450 words):
1. Which files you read, in order, and why.
2. Your first message to the researcher, verbatim.
3. The Plan steps you will follow and the mode you propose, with the reason.
4. Exactly when you would stop and ask before showing data, with the wording — and whether the N-starvation data needs that question.
5. Anything unclear, contradictory or missing in the skill (file and section).
