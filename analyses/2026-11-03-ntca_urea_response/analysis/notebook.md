# Analysis — notebook

## Context
Co-defined scope: apply the rules in proposal.md to ntcA on urea vs ammonium (MED4, MIT9313),
with N deprivation as the detectability control and cyanate / nitrite as descriptive context.
Produce one table, one figure per strain, and `reports/summary.html`.

## Run-manifest (coding agent, condensed)
- Scripts: `scripts/01_run_rules.py`, `scripts/02_figures.py`, `scripts/build_reports.py`;
  index rebuilt with `scripts/build_report_index.py`.
- Rows fetched = `total_matching` for all 6 experiments. No duplicate rows.
- Data: `readings.csv` (4), `controls.csv` (17), `ntca_rows.csv` (11), `gene_table.csv` (176),
  `qc_identity_gate.csv` (1), `genome_log2fc_used.csv` (21,381).
- Figures: `figures/ntca_med4.png|svg`, `figures/ntca_mit9313.png|svg`.

## Results (numbers first) [KG]

| Strain | Experiment | ntcA log2FC | Paper call | abs-rank pct | Control | Final reading |
|---|---|---|---|---|---|---|
| MED4 | urea | −2.27 | not_significant | 99.7 | ure/urt **failed** (0/11 sig up, median −0.12, 27% > 0) | **uninterpretable** (raw: suggestive_down) |
| MIT9313 | urea | +0.86 | not_significant | 91.6 | ure/urt passed (urtA +3.20, urtC +1.89, urtD +1.53 sig up; ureA–G ≤ +0.38) | **suggestive_up** |
| MED4 | cyanate (descriptive) | +0.03 | not_significant | 6.9 | ungated | not_changed |
| MIT9313 | nitrite (descriptive) | +1.43 | significant_up | 99.1 | ungated | up |

- Detectability passed in both strains. MED4 N-dep ntcA: +4.45 at 6h, +3.02 at 12h and +1.68 at
  24h (all significant), +1.23 at 48h (not significant, 79th percentile). MIT9313: +3.03 at 6h,
  +3.56 at 12h, +2.91 at 48h (all significant).
- Ribosomal growth-rate check: no flag in any experiment. Closest: MED4 cyanate, gap 0.283
  against the 0.3 limit.
- Identity gate did not fire: 0 of 1,696 log2FC identical; Pearson r 0.55; significant_up
  overlap 10/14, significant_down overlap 0/5. Why both have exactly 14 up / 5 down is
  **not explained** by the KG [gap]. It fits a fixed-length list in the paper, but that is unverified.

## Surprises
- The MED4 urea arm shows no urea signature (ure/urt flat), yet the same probes respond under
  N deprivation (urtA +5.37 at 6h). MED4 cyanate shows a mild N response (all 11 ure/urt > 0;
  glnA +1.40 sig up). [interpretation] Possible explanations: constitutive ure/urt expression on
  replete urea in MED4; a property of this arm in the source data (unverified). No biology is
  read into ntcA −2.27.
- The two strains point in opposite directions on urea (−2.27 vs +0.86). Fold changes are not
  compared across strains.
- MIT9313 glnB (PMT1481) is significant_down on both urea (−1.62) and nitrite (−1.40) [KG].
  It is a context gene with no rule attached.

## Decisions
- Cyanate / nitrite are **ungated and descriptive** (researcher, after the critic's finding 1):
  ure/urt is not a control for those N sources, and the proposal applies only the four-way table
  to them.
- Suggestive calls carry their direction (`suggestive_up` / `suggestive_down`).

## Critical review
Data-integrity + interpretation: data clean; 2 concerns fixed, 3 notes recorded. See
`critical_review.md`. The revision made only the two changes the critic recommended; no new
claims, so no delta pass.

## Decide-gate checklist
- [x] Every reading follows the pre-registered rule (critic recomputed from `data/`)
- [x] Main thread checked readings, ntcA rows and ure/urt values against `data/` CSVs
- [x] Time points match the proposal; no truncation
- [x] Critic pass done; findings dispositioned
- [x] Report built; index rebuilt
- [ ] Researcher approval
