# Proposal critical review (interpretation only) — 2026-11-03

Critic spot-checks: both experiments, gene/sig counts, and locus tags PMM0246, PMT1831, PMM0963,
PMM0970, PMT2230, PMT2229, PMT2225 confirmed in KG. Light differs (MED4 50, MIT9313 10 µE) —
harmless since comparisons are within experiment. No blockers.

| # | Severity | Finding (verbatim summary) | Disposition |
|---|---|---|---|
| 1 | Concern | Only the negative outcome was defined; no rule for "ntcA up", "ntcA down", or the in-between case (not significant but ≥ 75th percentile). | **Fixed** — added a four-row ntcA decision table. |
| 2 | Concern | Positive-control gate left a gap (median > 0 but nothing significant); "ure/urt up" undefined. ure/urt may be expressed on ammonium, so a weak shift is plausible; PMT2225 has 0 significant calls in any experiment. | **Fixed** — explicit pass criterion (≥ 2 significant_up, or median ≥ 0.5 with ≥ 75% positive); anything weaker = uninterpretable. Threshold choice raised at the design review. |
| 3 | Concern | Ribosomal proteins track growth rate, so they're not an independent flat set, and "near genome median" had no tolerance. | **Fixed** — relabelled as a growth-rate check with tolerance ±0.3 of the genome median and ≤ 10% significant; failure read as a growth-rate caveat, not as ntcA non-specificity. |
| 4 | Note | "Urea = mild N stress" premise is uncertain; both arms are N-replete steady state. | **Fixed** — added a "Scope of the claim" paragraph. |
