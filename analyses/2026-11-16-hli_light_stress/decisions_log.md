# Decisions log — hli genes and light stress

Who decided: **R** = researcher; **C→R** = Claude proposed, researcher agreed; **pending** = awaiting OK.

## Step 1 — Clarify and size the question

KG facts known at this point (from a quick look before the analysis was opened):
- MED4 has 23 genes annotated "high light inducible protein" (gene category: Stress response and adaptation).
- 13 experiments in the KG have light as the treatment: 11 in MED4, 1 in MIT0604 (UV shock), 1 in Thermosynechococcus BP-1.

| # | Decision | Who | Why |
|---|---|---|---|
| 1.1 | Question: do cyanobacterial hli genes respond to light stress (excess light, UV), gene by gene? | C→R | Researcher's question, "are hli proteins related to light stress?" |
| 1.2 | Mode: tested answer (prediction, positive and negative controls, decision rule fixed before scoring) | R | Wants a defensible answer, not only a map |
| 1.3 | Scope: all cyanobacteria in the KG with relevant data, hli genes matched across strains by ortholog group | R | |
| 1.4 | Purpose: standalone result | R | |
| 1.5 | Folder name `2026-11-16-hli_light_stress` | C→R | |

What was looked at before the plan: hli values in MED4 for all 8 light-treatment experiments that measured them (the 10.1128/JB.01097-06 microarray set: high white, blue, white, red, green light, white light + DCMU; the dark-vs-light phage-infected RNA-seq; the extended-light RNA-seq). Most hli genes were up after 45 min of high light, blue, white and red light; none were up in green light or with DCMU; most were down in the extended-light contrast. These experiments can only give exploratory findings here.

Open questions:
- Is one analysis the right size, or should MED4 and the other strains be split?
