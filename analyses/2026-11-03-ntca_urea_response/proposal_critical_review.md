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

# Delta pass (interpretation only) — controls added in design review round 2

No blockers. While spot-checking, the critic surfaced a primary result (MED4 urea ntcA log2FC −2.27,
rank 6, not significant). It is disclosed in proposal.md, and the ntcA decision table is left unchanged.

| # | Severity | Finding (summary) | Disposition |
|---|---|---|---|
| 1 | Concern | The detectability control relied only on the paper's significance call, which is binary (padj 0.01 or 1) and does not track fold-change size, so a real ntcA rise could miss it. A pass shows the probe responds, not that the array is sensitive enough to detect a urea-sized change. | **Fixed** — added a magnitude arm (log2FC > 0 and ≥ 75th percentile) and stated what a pass does and does not mean. |
| 2 | Concern | MIT9313 is matched at 6, 12 and 48h, not only 12h. The time-point subset had no stated reason. The MED4 "parallel sampling" [KG] tag was unsupported. | **Fixed** — use every matched time point from 6h on (MED4 6/12/24/48h; MIT9313 6/12/48h), with a stated reason for excluding 0h and 3h. MED4 sampling marked unverified. |
| 3 | Concern | The identity gate only catches a full duplicate; the identical counts would stay unexplained; and if the gate fired, urea would be just as suspect as cyanate. | **Fixed** — a firing quarantines both tables; on a pass, the notebook records why the counts match. |
| 4 | Note | "Shows whether specific to urea" was stronger than a possibly shared reference allows. | **Fixed** — softened to "reported as context; agreement may reflect a shared ammonium reference". |
