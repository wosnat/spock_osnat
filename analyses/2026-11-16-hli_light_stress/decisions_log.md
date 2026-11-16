# Decisions log — hli genes and light stress

Who decided: **R** = researcher; **C→R** = Claude proposed, researcher agreed; **pending** = awaiting OK.

## Step 1 — Clarify and size the question

KG facts known at this point (from a quick look before the analysis was opened):
- MED4 has 23 genes annotated "high light inducible protein" (gene category: Stress response and adaptation).
- 13 experiments in the KG have light as the treatment: 11 in MED4, 1 in MIT0604 (UV shock), 1 in Thermosynechococcus BP-1.

| # | Decision | Who | Why |
|---|---|---|---|
| 1.1 | Question: do cyanobacterial hli genes respond to light stress (excess light, UV), gene by gene? | C→R | Researcher's question, "are hli proteins related to light stress?" |
| 1.2 | Mode: tested answer (prediction, positive and negative controls, decision rule fixed before scoring) — **superseded by 3.1 (exploratory)** | R | Wants a defensible answer, not only a map |
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

### Which strains have light experiments (researcher's question)

KG facts (`list_experiments`, treatment = light, darkness or diel): 22 experiments; 20 are in cyanobacteria (the other 2 are Alteromonas).
- MED4: 14. These are 6 microarray light shifts, each vs darkness or vs white light with DCMU added; 2 proteomics (high 100 or medium 60 vs low 20 µE, about 180 proteins); 2 constant dark vs constant light (one with phage, one without; significant genes only); extended light and extended darkness (RNA-seq, same time-of-day control); and 2 diel series (microarray clusters; paired transcript-protein metrics).
- NATL2A: 3. Extended darkness vs diel cycle (axenic and in coculture); dark-tolerant vs parental in coculture.
- MIT0604: 1. UV shock vs untreated (all genes).
- Thermosynechococcus BP-1: 1. Light and oxygen levels in coculture; clusters only, no fold changes.
- Synechococcus WH8102: 1. Exoproteome after 10 h dark vs light.
- The 6 MED4 microarray "light stress" experiments compare light with *darkness* (dark-to-light shift). They are not high light vs normal light. The only true high-vs-low light contrast is the MED4 proteomics pair.

## Step 2 — What the KG holds (MED4)

Source: `spike/step2_med4_inventory.py` → `spike/step2_med4_inventory.csv`. It records coverage only (genes measured per experiment); no direction or significance was read.

KG facts:
- Gene sets in MED4: hli 23; chaperones 13; oxidative stress 25; photosystem II 31. None overlaps hli.
- 45 MED4 experiments. 8 are excluded because they have no stressed-vs-control fold changes (vesicles, transcription-start mapping, RNA decay, annotation survey, the two diel series, steady-state profiling).
- Proposed groups: light 12; non-light stress 15 (nitrogen 6, CO2 3, phage 3, iron 1, phosphorus 1, salt 1); non-stress 10 (all borderline).
- **hli coverage is incomplete even in full tables.** RNA-seq full tables hold 15–22 of 23 hli genes; the N-deprivation microarray holds 17. Likely cause: near-identical paralogs lose reads that map to several copies. Missing hli in a full table means "not measured", not "not changed".
- **Neither MED4 high-vs-low-light proteomics pair measured any hli protein** (0 of 23). The glucose proteomics also have 0. The N-starvation proteomics have 6.
- Reduced tables: the six light microarrays and the CO2 microarrays list genes significant in any condition of their study, so the approximate rule applies. The N-depleted RNA-seq table is the top 50% by expression level (no significance filter), so it is descriptive only. The phosphate table is filtered at 48 h only, so it is approximate at 48 h and descriptive at other times.
- Direction: the extended-darkness and constant-dark experiments have darkness as the treatment, so "more light" corresponds to their *down* arm.

- **What was seen early (2026-11-16):** the first version of the step 2 chart showed, for tables that list only significant genes, how many hli genes were in the table. In those tables, being in the table means being significant (direction not shown). So the researcher saw how many hli were significant, direction unknown, in: CO2 (12, 11, 1), iron starvation (7), phosphate (1 at 48 h), phage (9, 5, 1), air vs time 0 (8), iron rescue (7). The chart now shows "genome" for those rows. Full-table experiments were not affected.
- Comparison-set coverage in full tables (median measured / set size): light 10/23 hli, 8/13 chaperones, 14/25 oxidative, 18/31 photosystem II (low because the proteomics are included); non-light stress 15/23, 13/13, 25/25, 28/31; non-stress 17/23, 13/13, 25/25, 29/31.
- Publications used: 13 (list on the overview page).

### Reframing (researcher, 2026-11-16)

KG facts (experiment counts only, no hli values looked at): Prochlorococcus has experiments for carbon (19), nitrogen (12), phosphorus (9), iron (4), salt (3), temperature (1), plastic (4), phage (3), growth phase (6) and chemical (2). Synechococcus has carbon (15), phage (5), phosphorus (1), growth phase (1).

| # | Decision | Who | Why |
|---|---|---|---|
| 1.7 | Question becomes two parts: (1) do hli genes respond to light? (2) is their response a general stress response unrelated to light? | R | "a more interesting question to me" |
| 1.8 | hli values in non-light stress experiments are kept unseen until the plan is set — **partly broken (see "What was seen early"); moot after 3.1** | C | Keeps part 2 a tested answer |
| 1.9 | One analysis with two parts, not two analyses: part 1 is the light reference that part 2 is compared against | C→R | |
| 1.10 | Start with MED4 (45 experiments, most stress types); other strains as a quick same-method check | R | |

| # | Decision | Who | Why |
|---|---|---|---|
| 1.6 | Seed: the curated Cyanorak hli ortholog groups, plus hli-named genes (with eggNOG hli groups) in strains Cyanorak does not cover; exclude the radical SAM protein and hemH | C→R | Name, product and curated group agree completely in MED4; the domain route misses 18 of 23 |

### Agreed after step 2 (2026-11-16)

| # | Decision | Who | Why |
|---|---|---|---|
| 2.1 | Experiment groups as proposed; 4 glucose experiments dropped | C→R | No hli measured |
| 2.2 | Drop all proteomics (8 experiments) | R | Leaves 29 transcript experiments: light 10, non-light stress 13, non-stress 6 |
| 2.3 | Experiments whose significant-only tables were partly seen are labelled exploratory | C→R | See "What was seen early" |
| 2.4 | (Superseded by R.2: threshold 10) Add the reading "too few changed genes to tell" (fewer than 20 significant genes in that direction) | C→R | A non-enrichment there is uninformative |
| 2.5 | (Superseded by R.1: time-point counts, BH per gene set) Test per experiment × time point × direction, correcting across all tests; an experiment is "up" if enriched up at any time point; a stress type is read by study, not by assay | C→R | Stops one multi-assay study outvoting the others |

## Steps 3–5 — Approach, feasibility, framing

| # | Decision | Who | Why |
|---|---|---|---|
| 3.1 | Mode changed to **exploratory** (option B) | R | The tested part would rest on nitrogen and salt only; most of the stress range was seen or has only significant-only tables; one-day budget |
| 3.2 | Approach as written in `proposal.md` (per-test Fisher, background by table type, light orientation, "too few changes", comparison sets, combining by study) | C→R | Agreed step by step above |
| 4.1 | No separate feasibility spike: the comparison sets are run first in the methods milestone, and the test grid is spot-checked against `pathway_enrichment` | C | Exploratory mode, one-day budget; per-experiment tests avoid cross-platform comparison |
| 5.1 | No framing (exploratory mode); the descriptive label per stress type is a summary, not a decision rule | C | |

### Proposal review, first pass (2026-11-16)

The proposal critic returned 1 Blocker, 8 Concerns and 3 Notes (`proposal_critical_review.md`). The researcher accepted all of the proposed dispositions, and changed the "too few changes" threshold.

| # | Decision | Who | Why |
|---|---|---|---|
| R.1 | Apply all proposed dispositions; proposal revised | R | |
| R.2 | "Too few changed genes" threshold is **10** (not 20) | R | Fewer tests lost; Fisher can still reach significance with 10 changed genes |

### Proposal review, delta pass (2026-11-16)

The delta critic confirmed 9 of the 12 dispositions and found 2 Concerns and 5 Notes. All were fixed in wording (details in `proposal_critical_review.md`).

| # | Decision | Who | Why |
|---|---|---|---|
| R.3 | MIT0604 hli set includes EW14_RS05945 (16 genes) | C (default; researcher may change) | hli by product, in an eggNOG hli group |
| R.4 | Report time-point counts AND an aggregate per experiment: smallest time-point p × number of testable time points (Bonferroni within experiment), then BH across experiments per gene set | R asked for aggregation; C proposed the method | Avoids the many-time-points bias of "any time point" |
| R.5 | Keep the Fisher test where more than 30% of genes changed; show the hli and genome shares beside it as context | R | Fisher already accounts for the background rate; skipping it was over-cautious |

**Plan approved by the researcher, 2026-11-16.**
