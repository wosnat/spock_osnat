---
tags: [spock-regression]
max_turns: 30
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
---

This is a dry run of the research-methodology skill in this repo (.claude/skills/research-methodology/SKILL.md and its references/; related: .claude/skills/critical-review/SKILL.md, .claude/agents/). Do NOT call KG/MCP tools, run code, or write files. Read the skill the way you would if this were real — start at SKILL.md and follow what it tells you to read.

Scenario: A researcher says: "Can you show me what the KG has on phosphate limitation in Prochlorococcus? No hypothesis, I just want an overview to see if there's something worth a real study."

Report back, concise (under 450 words):
1. Which files you read, in order, and why.
2. The mode you choose and what the Plan consists of in this mode.
3. What the proposal contains, and what it leaves out.
4. Whether and when you would ask before showing data.
5. How findings are labelled in the paper, and what happens if you notice a striking mechanism along the way.
6. Anything unclear, contradictory or missing in the skill (file and section).
