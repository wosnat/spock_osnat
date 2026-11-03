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
| Control (MED4) | `10.1038/msb4100087_nitrogen_nitrogen_deprivation_med4_med4_microarray` — N-deprivation time course; use 12h and 24h (matched controls) |
| Control (MIT9313) | `10.1038/msb4100087_nitrogen_nitrogen_deprivation_mit9313_mit9313_microarray` — use 12h only (matched); 24h excluded (−N 24h vs +NH4 12h) |
| Comparison (MED4) | `10.1038/msb4100087_growth_medium_growth_on_cyanate_as_med4_microarray` — 1,696 genes; 14 up, 5 down (**same counts as MED4 urea — identity check required**) |
| Comparison (MIT9313) | `10.1038/msb4100087_growth_medium_growth_on_nitrite_as_mit9313_microarray` — 2,241 genes; 9 up, 5 down |
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
- *Positive-control pass criterion (per strain)*: the ure/urt set (11 genes per strain)
  **passes** if ≥ 2 genes are `significant_up`, **or** its median log2FC ≥ 0.5 with ≥ 75% of
  the genes log2FC > 0. Anything weaker = **control failed** → that strain's ntcA result is
  **uninterpretable**, not a negative.
- *Pre-registered expected-negative / growth-rate check*: ribosomal-protein genes (product
  contains "ribosomal protein"). Expected: median log2FC within ±0.3 of the genome-wide
  median and ≤ 10% of them significant. Because ribosomal transcripts track growth rate, a
  failure here is read as a **possible growth-rate difference between arms** (a caveat on
  every gene, ntcA included), not as evidence that ntcA's change is non-specific.
- *Decision rule for ntcA (per strain, applied only if the control passed)*:

  | Outcome | Rule |
  |---|---|
  | ntcA up | paper call `significant_up` |
  | ntcA down (against hypothesis) | paper call `significant_down` |
  | suggestive only | not significant, but |log2FC| ≥ 75th percentile of the experiment; direction reported |
  | not detectably changed | not significant and |log2FC| < 75th percentile |

  Strains are read separately; agreement across strains is reported, disagreement is
  reported as such (no pooling).

- *ntcA detectability control (N deprivation, same paper, same platform per strain)*:
  passes if ntcA is `significant_up` at ≥ 1 of the used time points (MED4 12h, 24h;
  MIT9313 12h). If it fails, a "not detectably changed" urea result in that strain is
  downgraded to **uninterpretable** (ntcA not shown to move on this array), and the
  N-deprivation ntcA values are reported as-is. This also gives the reference magnitude:
  urea ntcA log2FC is reported next to the N-deprivation value from the same strain's array.
- *Alternative-N comparison (cyanate MED4, nitrite MIT9313)*: the same decision table is
  applied to ntcA in each, descriptive only (one experiment each). It shows whether any urea
  result is specific to urea or shared with another non-ammonium source.
  **Identity gate:** before use, compare MED4 cyanate and MED4 urea row by row; if log2FC and
  status are identical for all shared genes, drop cyanate and log a `[kg-gap]`.

**Scope of the claim.** Both arms are acclimated, log-phase, N-replete cultures (urea at a
replete concentration [interpretation]). The result answers "is the ntcA transcript level
different at steady state on urea vs ammonium", not "does ntcA respond to N stress".

**Design comparability.**

| Experiment | Role | Treatment vs reference | Reference state | Shared samples | Can confirm / cannot |
|---|---|---|---|---|---|
| MED4 urea | primary | urea-acclimated log phase vs Pro99 ammonium log phase | exponential, N-replete; matched by growth state (same-day harvest not stated) [KG design_notes] | none with MIT9313 | can: steady-state ntcA transcript level; cannot: transient response, protein/activity |
| MIT9313 urea | replication in a second ecotype | same design | same | none | same; differs in strain, so agreement across strains is supportive, not required |

| MED4 N deprivation | ntcA detectability control | −N vs +NH4, sampled in parallel after resuspension; 12h/24h | matched time points; 12h acute stress, 24h N-limited [KG] | same strain and platform as urea; urea and −N arms are **different cultures**, the +NH4 reference may or may not be shared (unknown) | can: ntcA moves under real N stress on this array; cannot: a transient vs steady-state comparison of equal footing |
| MIT9313 N deprivation | same | same; 12h only | 12h matched; 24h control is a 12h +NH4 sample → excluded [KG design_notes] | same | same |
| MED4 cyanate / MIT9313 nitrite | alternative-N comparison | acclimated log phase on cyanate / nitrite vs Pro99 ammonium | same as urea [KG design_notes] | possibly the same ammonium reference arrays as urea (not stated) → not independent of urea | can: whether ntcA differs on another non-ammonium source; cannot: a statistical urea-vs-cyanate contrast |

Fold-change magnitudes are never compared across strains (different arrays). Within a strain,
urea, N-deprivation and cyanate/nitrite values for ntcA are shown side by side as context
(same platform and lab), never tested against each other.

## Methods milestone

Not a discovery milestone — the gene sets are fixed above. Methods = one small extraction
function with a toy test.
