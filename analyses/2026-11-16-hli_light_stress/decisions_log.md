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

### Counting the hli genes (researcher's question: how many, by name, by orthologs, what is the seed?)

KG facts (2026-11-16, interactive queries):
- Across the whole KG: 1,288 genes in 102 organisms match an hli name (gene name starting "hli") or an hli product description. 1,222 match by name, 1,266 by product, 1,203 sit in a curated Cyanorak hli ortholog group.
- There are 39 curated Cyanorak hli ortholog groups. Several hold more than one gene per strain: one group holds 4 MED4 genes (PMM0818, PMM1118, PMM1384, PMM1399), and two groups hold 3 each. Ortholog matching is therefore group to group, not gene to gene.
- Per strain with light-stress data (hli name / product / curated group / any route):
  - MED4: 23 / 23 / 23 / 23. All three routes agree on every gene.
  - MIT0604: 15 / 16 / 15 / 16. EW14_RS05945 has an hli product but no name and no curated group; it is in an eggNOG hli group.
  - Thermosynechococcus BP-1: hliA tsl2208, hli2 tsr1755, hli3 TLL_RS12660. This strain is not in Cyanorak, so none are in curated groups; each is in an eggNOG Cyanobacteria-level hli group.
- False hits to exclude: "photosystem II high light acclimation radical SAM protein" (tll1467, SYNPCC7002_A0894, H6G84_12355) matches "high light" but is not an hli; tsr0446 and SYNPCC7002_A0186 are ferrochelatase (hemH), which carries an hli-like domain.
- The domain annotation is not a usable seed: the InterPro family "High light-inducible protein HliA-D-like" covers only 5 of the 23 MED4 hli genes (PMM0064, PMM0817, PMM1135, PMM1398, PMM1482).

| # | Decision | Who | Why |
|---|---|---|---|
### Which strains have light experiments (researcher's question)

KG facts (`list_experiments`, treatment = light, darkness or diel): 22 experiments; 20 are in cyanobacteria (the other 2 are Alteromonas).
- MED4: 14. These are 6 microarray light shifts, each vs darkness or vs white light with DCMU added; 2 proteomics (high 100 or medium 60 vs low 20 µE, about 180 proteins); 2 constant dark vs constant light (one with phage, one without; significant genes only); extended light and extended darkness (RNA-seq, same time-of-day control); and 2 diel series (microarray clusters; paired transcript-protein metrics).
- NATL2A: 3. Extended darkness vs diel cycle (axenic and in coculture); dark-tolerant vs parental in coculture.
- MIT0604: 1. UV shock vs untreated (all genes).
- Thermosynechococcus BP-1: 1. Light and oxygen levels in coculture; clusters only, no fold changes.
- Synechococcus WH8102: 1. Exoproteome after 10 h dark vs light.
- The 6 MED4 microarray "light stress" experiments compare light with *darkness* (dark-to-light shift). They are not high light vs normal light. The only true high-vs-low light contrast is the MED4 proteomics pair.

| # | Decision | Who | Why |
|---|---|---|---|
| 1.6 | Seed: the curated Cyanorak hli ortholog groups, plus hli-named genes (with eggNOG hli groups) in strains Cyanorak does not cover; exclude the radical SAM protein and hemH | pending | Name, product and curated group agree completely in MED4; the domain route misses 18 of 23 |
