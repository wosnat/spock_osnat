# Proposal — ntcA transcript response to growth on urea

*Quick exercise of the Plan→Run arc (~10 min budget). Scope deliberately small.*

## Question

**Does the ntcA transcript change when *Prochlorococcus* grows on urea as its sole
nitrogen source instead of ammonium?**

- Readout (researcher's choice): the **ntcA transcript only** — its log2 fold change and the
  source paper's significance call. NtcA *activity* (2-oxoglutarate binding, regulon output)
  is out of scope; a flat transcript will not be read as "NtcA does not respond".
- Purpose: training exercise of the research process; standalone, not part of a paper.

## KG entries [KG]

| Role | Item |
|---|---|
| Publication | Tolonen et al. 2006, *Mol Syst Biol*, doi 10.1038/msb4100087 |
| Experiment (MED4) | `10.1038/msb4100087_growth_medium_growth_on_urea_as_med4_microarray` — 1,696 genes; 14 sig. up, 5 sig. down |
| Experiment (MIT9313) | `10.1038/msb4100087_growth_medium_growth_on_urea_as_mit9313_microarray` — 2,241 genes; 28 sig. up, 41 sig. down |
| Organisms | *Prochlorococcus* MED4 (high-light), MIT9313 (low-light) |
| Data type | Microarray, `table_scope = all_detected_genes`, single time point |
| Target gene | ntcA — **PMM0246** (MED4), **PMT1831** (MIT9313) |

## Framing

**Hypothesis.** ntcA is itself NtcA-autoregulated and induced under nitrogen stress
[interpretation]; if growth on urea is perceived as mild N stress, ntcA should be up
(log2FC > 0) on urea vs ammonium. The null is no change.

**Approach.** Pull the differential-expression rows of the two experiments (all genes) from
the KG. Report for ntcA in each strain: log2FC, the paper's significance call, and its
percentile rank of |log2FC| in that experiment's genome-wide distribution. Do the same for
the validation and expected-negative sets below so the ntcA value can be read against
them. One table, one figure (ntcA plotted against the genome-wide log2FC distribution, with
the validation and negative genes marked).

**Statistics plan.** No new test. Significance is the source paper's own call as stored in
the KG (KG alpha.9 follows each paper's criterion). The percentile rank is descriptive.
Reason: n = 1 gene × 2 experiments; a formal test would add nothing beyond the paper's call.

**Validation set** (urea-utilization genes, expected **up on urea** if the data detect the
urea response at all):
- MED4: ureA–G PMM0963–PMM0969, urtA PMM0970, urtC–E PMM0972–PMM0974
- MIT9313: ureA–G PMT2230–PMT2236, urtA PMT2229, urtC–E PMT2225–PMT2227
- Also reported, no fixed expectation: amt1 (PMM0263 / PMT1853), glnA (PMM0920 / PMT0601),
  glnB (PMM1463 / PMT1481), pipX (PMM0393 / PMT0205).

**Falsifiability check.**
- *Nothing real*: if the ure/urt genes show no shift up in a strain (median log2FC ≤ 0 and
  none significant), that experiment can't detect the urea response, and a flat ntcA there
  is **uninterpretable**, not a negative.
- *Pre-registered expected-negative*: ribosomal-protein genes (rpl/rps, selected by the
  product name "ribosomal protein") should be flat (median |log2FC| near the genome median,
  none significant). If they move as much as ntcA, ntcA's change is not specific.
- A valid negative: ure/urt up, ribosomal genes flat, ntcA not significant and below the
  ~75th percentile of |log2FC| → "ntcA transcript not detectably changed on urea".

**Design comparability.**

| Experiment | Role | Treatment vs reference | Reference state | Shared samples | Can confirm / cannot |
|---|---|---|---|---|---|
| MED4 urea | primary | urea-acclimated log phase vs Pro99 ammonium log phase | exponential, N-replete; matched by growth state (same-day harvest not stated) [KG design_notes] | none with MIT9313 | can: steady-state ntcA transcript level; cannot: transient response, protein/activity |
| MIT9313 urea | replication in a second ecotype | same design | same | none | same; differs in strain, so agreement across strains is supportive, not required |

Fold changes are compared within experiment only (different arrays), never as magnitudes
across strains.

## Methods milestone

Not a discovery milestone — the gene sets are fixed above. Methods = one small extraction
function with a toy test.
