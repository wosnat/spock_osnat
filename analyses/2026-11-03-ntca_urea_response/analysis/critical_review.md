# Analysis critical review (data-integrity + interpretation) — 2026-11-03

Data integrity: clean. The critic recomputed the ntcA percentiles, the ure/urt medians and the
significance counts from `data/`. Time points match the proposal, there are no duplicates or
truncation, and the figure cutoffs are at the computed values. No blockers.

| # | Severity | Finding (summary) | Disposition |
|---|---|---|---|
| 1 | Concern | The cyanate and nitrite readings were gated by ure/urt computed on those experiments. The proposal doesn't support this, and ure/urt is not a control for nitrite. It hid the only significant steady-state ntcA call (MIT9313 nitrite, +1.43). | **Fixed** — researcher decision: comparison rows are ungated and descriptive (`gating` column). Urea gating unchanged. |
| 2 | Concern | "Suggestive" was reported without its direction. Two "suggestive" urea results could be misread as agreement across strains, but MED4 is down (−2.27, and uninterpretable) and MIT9313 is up (+0.86). | **Fixed** — added `direction` and `suggestive_up/down`; summary.html now states that no agreement across strains can be claimed. |
| 3 | Note | The MED4 probes respond under N deprivation (urtA +5.37 at 6h), so the flat ure/urt on urea comes from this arm, not from the array. Cyanate looks more like an N response than urea does. | **Recorded** — MED4 stays uninterpretable; worded as "this arm shows no urea signature"; no biology read into −2.27. |
| 4 | Note | The MIT9313 control passes on the transporter genes only (urtA/C/D significant up; ureA–G ≤ +0.39). | **Recorded** — added to summary.html and the notebook. |
| 5 | Note | The identity-gate notebook entry (10/14 up shared, 0/5 down) is still owed; the MED4 cyanate ribosomal gap of 0.283 against a 0.3 limit is close; MED4 48h detectability passes on magnitude only (the overall pass doesn't depend on it). | **Recorded** in notebook.md. |
