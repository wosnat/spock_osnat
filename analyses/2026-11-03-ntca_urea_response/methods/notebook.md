# Methods — notebook

## Context
Co-defined scope: a small module that applies the rules in `proposal.md`, with toy tests, plus
(researcher's addition) a check against the real KG that the API calls are correct. The KG
check asserts only values already known from the MCP tools, so no new primary results are
seen. The decision rules were not run on real ntcA data.

## Run-manifest (from the coding agent, condensed)
- Files: `ntca_urea.py` (fetch_de, add_abs_rank_pct, positive_control, growth_rate_check,
  detectability, classify_ntca, final_reading, identity_gate); `tests/test_ntca_urea.py` (21
  toy tests, written first); `tests/test_kg_api.py` (10 live-KG tests, marker `kg`);
  `tests/conftest.py`; `scripts/probe_api.py`, `scripts/probe_timepoints.py`;
  `data/qc_kg_api_checks.csv` (16 rows: counts and sign fractions only).
- Command: `uv run python -m pytest -q analyses/2026-11-03-ntca_urea_response/methods/tests`
  → **31 passed** (re-run by the main thread: 31 passed).
- Paging: rows fetched = `total_matching` for all 6 experiments (MED4 N-dep 10,176; MIT9313
  N-dep 13,446; others one row per gene). No duplicate (experiment, timepoint, locus_tag) rows.
- KG agreement: every gene count and up/down count per experiment and time point matches the
  `list_experiments` envelope. PMM0246 in MED4 urea = −2.2711, not_significant (already
  disclosed). ntcA, ure, urt locus tags resolve to the expected names.
- Fraction of genes with log2FC < 0: 0.445–0.639 in all rows except MED4 N-dep 0h (0.761). No
  zero or missing log2FC values, so the sign is present.
- Exposure beyond the disclosure: one validation-gene value, PMM0963 (ureC) in MED4 urea
  log2FC −0.12, not_significant, printed by the schema probe. No new ntcA value was seen.

## Surprises
- MED4 cyanate and MED4 urea have the same 14 up / 5 down, but different fractions of negative
  log2FC (0.445 vs 0.522) [KG]. So the two tables are not copies at the level of this summary.
  The row-level identity gate runs in the analysis step.
- MED4 N-dep 0h is 76% negative. That point is excluded from the plan anyway (it comes before
  the starvation response develops). Recorded as is.

## Not checked
- The locus tags for amt1, glnA, glnB and pipX (context genes only, with no decision rule
  attached).
- Exact urtC/D/E letter per locus tag (prefix `urt` checked).

## Decisions
- No critic pass: this milestone emits no data file that later steps consume (the QC CSV is a
  check, not an input).
- No `reports/summary.html` for this milestone, to keep the exercise short; reports start at
  the analysis step.

## Decide-gate checklist
- [x] Method implements the proposal's rules (main thread read `classify_ntca`,
      `final_reading`, `add_abs_rank_pct` against proposal.md)
- [x] Toy tests cover every outcome; tests written before code
- [x] Live-KG API check passes; paging verified against `total_matching`
- [x] No primary ntcA result seen beyond the disclosed MED4 urea value
- [ ] Researcher approval
